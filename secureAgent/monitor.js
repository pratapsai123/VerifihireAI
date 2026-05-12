const { scanProcesses, getWindowTitles } = require('./processScanner');
const { detectBlocked, loadBundledRules, setRules } = require('./detector');
const { getSecuritySignatures, sendSecurityCheck, sendHeartbeat, logActivity } = require('./apiClient');
const { selfDestruct } = require('./instanceManager');
const { scanHardwareDevices, compareToBaseline, getStartupBaseline } = require('./hardwareScanner');

let scanTimer = null;
let heartbeatTimer = null;
let signatureTimer = null;
let current = null;
let isScanning = false; // mutex — prevents overlapping PowerShell processes
let pendingViolation = null; // Buffers violations detected while offline
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

/**
 * Retries any violation that occurred while the network was down.
 */
async function flushPendingViolation() {
  if (!pendingViolation || !current) return;
  
  try {
    console.log('[monitor] Attempting to flush pending offline violation...');
    const response = await sendSecurityCheck(current.backendApiBase, {
      ...pendingViolation,
      session_id: current.sessionId,
      user_id: current.userId,
    });
    
    if (response) {
      console.log('[monitor] Pending violation flushed successfully.');
      pendingViolation = null;
      
      if (response.action === 'STOP') {
        stopMonitor();
        setTimeout(() => selfDestruct(0), 2000);
      }
    }
  } catch (err) {
    console.warn('[monitor] Could not flush violation yet (still offline):', err.message);
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
      const violationData = {
        status: 'VIOLATION',
        app: allApps.join(', '),
        process_name: verdict.detections.map(d => d.processName).filter(Boolean).join(', '),
        app_path: verdict.detections[0]?.processPath || '',
      };

      try {
        const response = await sendSecurityCheck(current.backendApiBase, {
          ...violationData,
          session_id: current.sessionId,
          user_id: current.userId,
        });
        pendingViolation = null; // Success, clear buffer
        if (response?.action === 'STOP') {
          stopMonitor();
          console.log('[monitor] STOP action received — agent will self-destruct');
          setTimeout(() => selfDestruct(0), 2000);
        }
      } catch (err) {
        console.warn('[monitor] Network down — buffering process violation for later reporting');
        pendingViolation = violationData;
      }
      return;
    }

    // If we have a pending violation, try to flush it before reporting SAFE
    if (pendingViolation) {
      await flushPendingViolation();
      if (pendingViolation) return; // Still offline, don't report SAFE yet
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
      const hwViolation = {
        status: 'HARDWARE_VIOLATION',
        app: hwResult.violationNames.join(', '),
        process_name: '',
        app_path: '',
      };
      
      try {
        await sendSecurityCheck(current.backendApiBase, {
          ...hwViolation,
          session_id: current.sessionId,
          user_id: current.userId,
        });
        pendingViolation = null;
      } catch (err) {
        console.warn('[monitor] Network down — buffering hardware violation');
        pendingViolation = hwViolation;
      }
    } else {
      // All hardware clean — signal HARDWARE_SAFE so backend can un-pause if needed
      // But only if we don't have a pending violation
      if (!pendingViolation) {
        await sendSecurityCheck(current.backendApiBase, {
          session_id: current.sessionId,
          user_id: current.userId,
          status: 'HARDWARE_SAFE',
          app: '',
          process_name: '',
          app_path: '',
        }).catch(() => {});
      }
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

let failedHeartbeats = 0;

async function sendAliveHeartbeat() {
  if (!current) return;

  // Prioritize flushing pending violations over sending a normal heartbeat
  if (pendingViolation) {
    await flushPendingViolation();
  }

  try {
    const response = await sendHeartbeat(current.backendApiBase, {
      session_id: current.sessionId,
      user_id: current.userId,
      status: 'ALIVE',
    });
    if (failedHeartbeats > 0) {
      console.log(`[monitor] Heartbeat recovered after ${failedHeartbeats} failed attempts`);
    }
    failedHeartbeats = 0;
    if (response?.action === 'STOP') {
      stopMonitor();
      console.log('[monitor] STOP action from heartbeat — agent will self-destruct');
      setTimeout(() => selfDestruct(0), 2000);
    }
  } catch {
    failedHeartbeats++;
    // When heartbeats fail (network down), retry faster (every 3s instead of 10s)
    // so we refresh the backend timeout clock ASAP when connectivity returns.
    if (failedHeartbeats === 1) {
      console.warn('[monitor] Heartbeat failed — network may be down. Retrying faster...');
    }
    if (failedHeartbeats <= 3) {
      // Schedule an extra retry in 3 seconds (in addition to the normal 10s interval)
      setTimeout(sendAliveHeartbeat, 3000);
    }
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
  failedHeartbeats = 0;
  knownLogOnlyMap = new Map(); // reset on stop
}

function getMonitorState() {
  return { running: Boolean(scanTimer && heartbeatTimer), current };
}

module.exports = { startMonitor, stopMonitor, getMonitorState };
