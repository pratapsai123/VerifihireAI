const { scanProcesses, getWindowTitles } = require('./processScanner');
const { detectBlocked, loadBundledRules, setRules } = require('./detector');
const { getSecuritySignatures, sendSecurityCheck, sendHeartbeat, logActivity } = require('./apiClient');
const { selfDestruct } = require('./instanceManager');
const { scanHardwareDevices, compareToBaseline, getStartupBaseline, initBaseline } = require('./hardwareScanner');

/** Returns current local time as HH:MM:SS for terminal log clarity. */
function ts() {
  const d = new Date();
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const ss = String(d.getSeconds()).padStart(2, '0');
  return `[${hh}:${mm}:${ss}]`;
}

let scanTimer = null;
let heartbeatTimer = null;
let signatureTimer = null;
let current = null;
let isScanning = false; // mutex — prevents overlapping PowerShell processes
let scanRequested = false; // queue an immediate follow-up scan
let lastScanWasViolation = false;
let pendingViolation = null; // Buffers violations detected while offline

const SCAN_INTERVAL_SAFE_MS = 8000;
const SCAN_INTERVAL_AFTER_VIOLATION_MS = 2500;
// Map<instanceId, {name, class}> of logOnly devices seen in current session (not in exam baseline)
let knownLogOnlyMap = new Map();
// Map<instanceId, {name, class}> of blocked USB/high-risk devices logged during this exam
let knownBlockedUsbMap = new Map();
// Set of blocked app labels already logged this session (prevents duplicate entries per app)
let knownViolationAppsSet = new Set();

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
    console.log(ts(), '[monitor] Attempting to flush pending offline violation...');
    const response = await sendSecurityCheck(current.backendApiBase, {
      ...pendingViolation,
      session_id: current.sessionId,
      user_id: current.userId,
    });
    
    if (response) {
      console.log(ts(), '[monitor] Pending violation flushed successfully.');
      pendingViolation = null;
      
      if (response.action === 'STOP') {
        stopMonitor();
        setTimeout(() => selfDestruct(0), 2000);
      }
    }
  } catch (err) {
    console.warn(ts(), '[monitor] Could not flush violation yet (still offline):', err.message);
  }
}


function scheduleNextScan(delayMs) {
  if (!current) return;
  if (scanTimer) clearTimeout(scanTimer);
  scanTimer = setTimeout(scanAndReport, delayMs);
}

async function scanAndReport() {
  if (!current) return;
  if (isScanning) {
    scanRequested = true;
    return;
  }
  isScanning = true;
  try {
    await _doScan();
  } finally {
    isScanning = false;
    if (!current) return;
    if (scanRequested) {
      scanRequested = false;
      scheduleNextScan(400);
      return;
    }
    const delay = lastScanWasViolation ? SCAN_INTERVAL_AFTER_VIOLATION_MS : SCAN_INTERVAL_SAFE_MS;
    scheduleNextScan(delay);
  }
}

function triggerScanNow() {
  if (!current) return;
  if (isScanning) {
    scanRequested = true;
    return;
  }
  if (scanTimer) clearTimeout(scanTimer);
  scanTimer = null;
  scanAndReport();
}

async function _doScan() {
  if (!current) return;
  try {
    const { scanProcesses, getWindowTitles } = require('./processScanner');
    const processes = await scanProcesses();
    const windowTitles = await getWindowTitles();
    const verdict = await detectBlocked(processes, windowTitles, { strict: true });
    
    // Safety check: monitor might have been stopped while we were scanning
    if (!current) return;

    if (!verdict.safe) {
      lastScanWasViolation = true;
      console.log(ts(), '[monitor] POLICY VIOLATION DETECTED:', verdict.blocked.join(', '));
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

        // Log the app-open event so recruiters can see which apps were opened and when.
        // Only log each distinct blocked app once per exam session (de-duplicate).
        if (current.token) {
          const newApps = allApps.filter(a => !knownViolationAppsSet.has(a));
          if (newApps.length > 0) {
            newApps.forEach(a => knownViolationAppsSet.add(a));
            try {
              await logActivity(
                current.backendApiBase,
                current.token,
                'App Opened (Blocked)',
                `Blocked app detected: ${newApps.join(', ')}${
                  violationData.process_name ? ` (process: ${violationData.process_name})` : ''
                }`,
              );
            } catch { /* non-fatal */ }
          }
        }

        if (response?.action === 'STOP') {
          stopMonitor();
          console.log(ts(), '[monitor] STOP action received — agent will self-destruct');
          setTimeout(() => selfDestruct(0), 2000);
        }
      } catch (err) {
        console.warn(ts(), '[monitor] Network down — buffering process violation for later reporting');
        pendingViolation = violationData;
      }
      return;
    }

    lastScanWasViolation = false;

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
        console.error(ts(), '[monitor] Process scan error:', err.message);
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
        console.warn(ts(), '[monitor] Network down — buffering hardware violation');
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

    // ── Mid-exam USB / external device audit (only devices NEW since exam monitor started) ──
    const baseline = getStartupBaseline();
    const newBlocked = (hwScan.blocked || []).filter(
      d => !baseline.instanceIds.has(d.instanceId)
    );
    for (const dev of newBlocked) {
      if (!knownBlockedUsbMap.has(dev.instanceId)) {
        knownBlockedUsbMap.set(dev.instanceId, { name: dev.name, cls: dev.class });
        try {
          await logActivity(
            current.backendApiBase,
            current.token,
            'USB Device Connected',
            `${dev.name} (${dev.class}) connected during exam`
          );
        } catch { /* non-fatal */ }
      }
    }

    const newLogOnly = (hwScan.logOnly || []).filter(
      d => !baseline.instanceIds.has(d.instanceId)
    );

    for (const dev of newLogOnly) {
      if (!knownLogOnlyMap.has(dev.instanceId)) {
        knownLogOnlyMap.set(dev.instanceId, { name: dev.name, cls: dev.class });
        try {
          await logActivity(
            current.backendApiBase,
            current.token,
            'USB Device Connected',
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
      console.log(ts(), `[monitor] Heartbeat recovered after ${failedHeartbeats} failed attempts`);
    }
    failedHeartbeats = 0;
    if (response?.action === 'STOP') {
      stopMonitor();
      console.log(ts(), '[monitor] STOP action from heartbeat — agent will self-destruct');
      setTimeout(() => selfDestruct(0), 2000);
    }
  } catch {
    failedHeartbeats++;
    // When heartbeats fail (network down), retry faster (every 3s instead of 10s)
    // so we refresh the backend timeout clock ASAP when connectivity returns.
    if (failedHeartbeats === 1) {
      console.warn(ts(), '[monitor] Heartbeat failed — network may be down. Retrying faster...');
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
  knownLogOnlyMap = new Map();
  knownBlockedUsbMap = new Map();
  knownViolationAppsSet = new Set();
  // Baseline at exam start — devices already connected before the exam are not logged.
  await initBaseline();
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
  scanRequested = false;
  lastScanWasViolation = false;
  failedHeartbeats = 0;
  knownLogOnlyMap = new Map();
  knownBlockedUsbMap = new Map();
  knownViolationAppsSet = new Set();
}

function getMonitorState() {
  return {
    running: Boolean(scanTimer && heartbeatTimer),
    current,
    lastScanWasViolation,
    pendingViolation,
  };
}

module.exports = { startMonitor, stopMonitor, getMonitorState, triggerScanNow };
