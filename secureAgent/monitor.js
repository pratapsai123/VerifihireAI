const { scanProcesses, getWindowTitles } = require('./processScanner');
const { detectBlocked, loadBundledRules, setRules } = require('./detector');
const { getSecuritySignatures, sendSecurityCheck, sendHeartbeat, logActivity } = require('./apiClient');
const { scanHardwareDevices, compareToBaseline, getStartupBaseline } = require('./hardwareScanner');

let scanTimer = null;
let heartbeatTimer = null;
let signatureTimer = null;
let current = null;
let isScanning = false; // mutex — prevents overlapping PowerShell processes
// Map<instanceId, {name, class}> of logOnly devices seen in current session (not in startup baseline)
let knownLogOnlyMap = new Map();

async function refreshSignatures() {
  if (!current?.backendApiBase) return;
  try {
    const data = await getSecuritySignatures(current.backendApiBase);
    if (Array.isArray(data?.rules) && data.rules.length > 0) {
      setRules(data.rules);
      return;
    }
    loadBundledRules();
  } catch {
    loadBundledRules();
  }
}

async function scanAndReport() {
  if (!current) return;
  if (isScanning) {
    return;
  }
  isScanning = true;
  try { await _doScan(); } finally { isScanning = false; }
  // Schedule next scan only after this one completes
  if (current) scanTimer = setTimeout(scanAndReport, 10000);
}

async function _doScan() {
  if (!current) return;
  try {
    const { scanProcesses, getWindowTitles } = require('./processScanner');
    const processes = await scanProcesses();
    const windowTitles = await getWindowTitles();
    const verdict = await detectBlocked(processes, windowTitles);
    
    // Safety check: monitor might have been stopped while we were scanning
    if (!current) return;

    if (!verdict.safe) {
      console.log('[monitor] POLICY VIOLATION DETECTED:', verdict.blocked.join(', '));
      const allApps = [...new Set(verdict.blocked)];
      const response = await sendSecurityCheck(current.backendApiBase, {
        session_id: current.sessionId,
        user_id: current.userId,
        status: 'VIOLATION',
        app: allApps.join(', '),
        process_name: verdict.detections.map(d => d.processName).filter(Boolean).join(', '),
        app_path: verdict.detections[0]?.processPath || '',
      });
      if (response?.action === 'STOP') {
        stopMonitor();
        console.log('[monitor] STOP action received — agent will exit');
        setTimeout(() => process.exit(0), 2000);
      }
      return;
    }

    // Safety check again before sending SAFE report
    if (!current) return;
    
    await sendSecurityCheck(current.backendApiBase, {
      session_id: current.sessionId,
      user_id: current.userId,
      status: 'SAFE',
      app: '',
      process_name: '',
      app_path: '',
    });
  } catch (err) {
    if (current) {
        console.error('[monitor] Process scan error:', err.message);
    }
  }

  // ── Hardware scan (USB/HDMI/display check) ───────────────────────────────
  try {
    const hwScan = await scanHardwareDevices();
    const hwResult = compareToBaseline(hwScan);
    if (hwResult.hasNewViolation) {
      await sendSecurityCheck(current.backendApiBase, {
        session_id: current.sessionId,
        user_id: current.userId,
        status: 'HARDWARE_VIOLATION',
        app: hwResult.violationNames.join(', '),
        process_name: '',
        app_path: '',
      });
    } else {
      // All hardware clean — signal HARDWARE_SAFE so backend can un-pause if needed
      await sendSecurityCheck(current.backendApiBase, {
        session_id: current.sessionId,
        user_id: current.userId,
        status: 'HARDWARE_SAFE',
        app: '',
        process_name: '',
        app_path: '',
      });
    }

    // ── Log-only devices (mouse, keyboard, bluetooth) ─────────────────────
    // No exam pause — just write an audit trail entry when they connect/disconnect.
    const baseline = getStartupBaseline();
    const newLogOnly = (hwScan.logOnly || []).filter(
      d => !baseline.instanceIds.has(d.instanceId)
    );

    // Newly connected devices (not seen before in this session)
    for (const dev of newLogOnly) {
      if (!knownLogOnlyMap.has(dev.instanceId)) {
        knownLogOnlyMap.set(dev.instanceId, { name: dev.name, cls: dev.class });
        try {
          await logActivity(
            current.backendApiBase,
            current.token,
            'Device Connected',
            `${dev.name} (${dev.class}) connected during exam`
          );
        } catch { /* non-fatal */ }
      }
    }

    // Devices that were previously seen but are now disconnected
    const currentIds = new Set(newLogOnly.map(d => d.instanceId));
    for (const [prevId, devInfo] of knownLogOnlyMap) {
      if (!currentIds.has(prevId)) {
        knownLogOnlyMap.delete(prevId);
        try {
          await logActivity(
            current.backendApiBase,
            current.token,
            'Device Disconnected',
            `${devInfo.name} (${devInfo.cls}) disconnected during exam`
          );
        } catch { /* non-fatal */ }
      }
    }
  } catch {
    // Hardware scan errors are non-fatal
  }
}

async function sendAliveHeartbeat() {
  if (!current) return;
  try {
    const response = await sendHeartbeat(current.backendApiBase, {
      session_id: current.sessionId,
      user_id: current.userId,
      status: 'ALIVE',
    });
    if (response?.action === 'STOP') {
      stopMonitor();
      console.log('[monitor] STOP action from heartbeat — agent will exit');
      setTimeout(() => process.exit(0), 2000);
    }
  } catch {
    // Ignore transient network errors; backend timeout guard handles enforcement.
  }
}

async function startMonitor({ token, sessionId, userId, backendApiBase }) {
  stopMonitor();
  current = { token, sessionId, userId, backendApiBase };
  isScanning = false;
  await refreshSignatures();
  // Use self-scheduling setTimeout (not setInterval) so scans never overlap.
  // Each scan starts 10s after the PREVIOUS one finishes.
  // Fire first heartbeat immediately
  sendAliveHeartbeat();
  heartbeatTimer = setInterval(sendAliveHeartbeat, 10000);
  signatureTimer = setInterval(refreshSignatures, 60000);
  // Fire first scan non-blocking so /monitor/start responds immediately.
  scanTimer = setTimeout(scanAndReport, 3000);
}

function stopMonitor() {
  if (scanTimer) clearTimeout(scanTimer);
  if (heartbeatTimer) clearInterval(heartbeatTimer);
  if (signatureTimer) clearInterval(signatureTimer);
  scanTimer = null;
  heartbeatTimer = null;
  signatureTimer = null;
  current = null;
  isScanning = false;
  knownLogOnlyMap = new Map(); // reset on stop
}

function getMonitorState() {
  return { running: Boolean(scanTimer && heartbeatTimer), current };
}

module.exports = { startMonitor, stopMonitor, getMonitorState };
