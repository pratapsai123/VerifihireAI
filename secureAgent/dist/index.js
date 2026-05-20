/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 124:
/***/ ((module, __unused_webpack_exports, __nccwpck_require__) => {

const axios = __nccwpck_require__(720);

async function getSecuritySignatures(apiBase) {
  const url = `${apiBase}/security-signatures`;
  const res = await axios.get(url, { timeout: 4000 });
  return res.data;
}

async function sendSecurityCheck(apiBase, payload) {
  const url = `${apiBase}/security-check`;
  const res = await axios.post(url, payload, { timeout: 4000 });
  return res.data;
}

async function sendHeartbeat(apiBase, payload) {
  const url = `${apiBase}/security-heartbeat`;
  const res = await axios.post(url, payload, { timeout: 4000 });
  return res.data;
}

async function logActivity(apiBase, token, action, details) {
  if (!token) return;
  const url = `${apiBase}/invitations/public/${token}/log/`;
  await axios.post(url, { action, details }, { timeout: 4000 });
}

module.exports = { getSecuritySignatures, sendSecurityCheck, sendHeartbeat, logActivity };


/***/ }),

/***/ 753:
/***/ ((module, __unused_webpack_exports, __nccwpck_require__) => {

const fs = __nccwpck_require__(896);
const path = __nccwpck_require__(928);

const bundledPath = __nccwpck_require__.ab + "blacklist.json";
let runtimeRules = [];

function loadBundledRules() {
  try {
    const raw = fs.readFileSync(__nccwpck_require__.ab + "blacklist.json", 'utf8');
    const parsed = JSON.parse(raw);
    runtimeRules = Array.isArray(parsed) ? parsed : (parsed.rules || []);
  } catch {
    runtimeRules = [];
  }
}

function setRules(rules) {
  runtimeRules = Array.isArray(rules) ? rules : [];
}

function getRules() {
  return runtimeRules;
}

function norm(v) {
  return String(v || '').toLowerCase();
}

function containsAny(hay, signatures) {
  const h = norm(hay);
  return (signatures || []).some((sig) => h.includes(norm(sig)));
}

function isServiceProcess(processName, rule) {
  const nameLower = norm(processName);
  const serviceProcs = rule.serviceProcesses || [];
  return serviceProcs.some((sp) => nameLower.includes(norm(sp)));
}

function pushDetection(detections, checkedPids, rule, pid, fields) {
  const key = `${rule.label}:${pid}`;
  if (checkedPids.has(key)) return;
  checkedPids.add(key);
  detections.push({
    app: rule.label,
    processName: fields.processName || '',
    processPath: fields.processPath || '',
    commandLine: fields.commandLine || '',
  });
}

/**
 * @param {object[]} processes
 * @param {Map<number, {title: string}>} windowTitles
 * @param {{ strict?: boolean }} options - strict=true for precheck: catch background/tray/session-0 UI processes
 */
async function detectBlocked(processes, windowTitles = new Map(), options = {}) {
  const strict = options.strict === true;
  const detections = [];
  const checkedPids = new Set();
  const matchedLabels = new Set();

  const titleSignaturesForRule = (rule) => [
    rule.label,
    ...(rule.signatures || []),
    ...((rule.activeIndicators && rule.activeIndicators.windowTitles) || []),
  ];

  for (const p of processes || []) {
    const name = p.processName || '';
    const fullPath = p.processPath || '';
    const cmd = p.commandLine || '';
    const desc = p.description || '';
    const comp = p.company || '';
    const pid = p.pid || 0;
    const sessionId = p.sessionId;

    for (const rule of runtimeRules) {
      const hitName = containsAny(name, rule.signatures);
      const hitPath = containsAny(fullPath, rule.pathSignatures);
      const hitCmd = containsAny(cmd, [
        ...(rule.signatures || []),
        ...(rule.pathSignatures || []),
      ]);
      const hitDesc = containsAny(desc, [rule.label, ...(rule.signatures || [])]);
      const hitComp = containsAny(comp, [rule.label, ...(rule.signatures || [])]);
      const windowInfo = windowTitles.get(pid);
      const hitWindow = windowInfo
        ? containsAny(windowInfo.title, titleSignaturesForRule(rule))
        : false;

      if (!(hitName || hitPath || hitCmd || hitDesc || hitComp || hitWindow)) {
        continue;
      }

      // Precheck (strict): flag background/tray helpers — only skip OS daemons like teamviewer_service
      if (!strict && isServiceProcess(name, rule)) {
        continue;
      }
      if (strict && isServiceProcess(name, rule)) {
        continue;
      }

      if (!strict && sessionId === 0 && !hitWindow) {
        continue;
      }
      if (strict && sessionId === 0 && !hitWindow && !hitName && !hitPath && !hitCmd) {
        continue;
      }

      pushDetection(detections, checkedPids, rule, pid, {
        processName: name,
        processPath: fullPath,
        commandLine: cmd,
      });
      matchedLabels.add(rule.label);
    }
  }

  // Window title pass — catches Chrome TeamViewer extension and tray-only UIs
  for (const [pid, windowInfo] of windowTitles) {
    for (const rule of runtimeRules) {
      if (matchedLabels.has(rule.label)) continue;
      if (!containsAny(windowInfo.title, titleSignaturesForRule(rule))) continue;
      const procName = windowInfo.processName || '';
      if (isServiceProcess(procName, rule)) continue;
      pushDetection(detections, checkedPids, rule, pid, {
        processName: procName,
        processPath: '',
        commandLine: '',
      });
      matchedLabels.add(rule.label);
    }
  }

  const blocked = [...new Set(detections.map((d) => d.app))];
  return {
    safe: blocked.length === 0,
    blocked,
    detections,
  };
}

loadBundledRules();

module.exports = { loadBundledRules, setRules, getRules, detectBlocked };


/***/ }),

/***/ 81:
/***/ ((module, __unused_webpack_exports, __nccwpck_require__) => {

const { exec } = __nccwpck_require__(317);

function run(cmd) {
  return new Promise((resolve, reject) => {
    exec(cmd, { windowsHide: true, maxBuffer: 15 * 1024 * 1024 }, (err, stdout) => {
      if (err) return reject(err);
      resolve(stdout || '');
    });
  });
}

function safeParseJson(raw) {
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : (parsed ? [parsed] : []);
  } catch {
    return [];
  }
}

// HIGH RISK: Pause exam if newly connected / block precheck
const BLOCK_CLASSES = ['DiskDrive', 'Camera', 'Net'];
// MEDIUM RISK: Log only
const LOG_CLASSES = ['HIDClass', 'Bluetooth'];

function isUSBConnected(instanceId) {
  const id = String(instanceId || '').toUpperCase();
  return id.startsWith('USB\\') || id.startsWith('USBSTOR\\');
}

// ── Startup Baseline ─────────────────────────────────────────────────────────
// Taken once when the Secure Agent server starts.
// Devices present at startup are considered "built-in" (laptop camera, bluetooth, etc.)
// Only devices that APPEAR AFTER startup are flagged as new.
let STARTUP_BASELINE = null;

async function initBaseline() {
  try {
    const scan = await scanHardwareDevices();
    STARTUP_BASELINE = {
      instanceIds: new Set([
        ...(scan.blocked || []).map(d => d.instanceId),
        ...(scan.logOnly || []).map(d => d.instanceId),
      ]),
      monitorCount: scan.monitorCount || 1,
    };
  } catch {
    STARTUP_BASELINE = { instanceIds: new Set(), monitorCount: 1 };
  }
}

function getStartupBaseline() {
  return STARTUP_BASELINE || { instanceIds: new Set(), monitorCount: 1 };
}

// ── Core Scanner ──────────────────────────────────────────────────────────────
async function scanHardwareDevices() {
  const blocked = [];
  const logOnly = [];

  // Pass 1: USB PnP devices — filtered in JS (avoids $_ PowerShell issue)
  try {
    const psCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-PnpDevice -PresentOnly | Select-Object Class, FriendlyName, InstanceId, Status | ConvertTo-Json -Compress"';
    const out = await run(psCmd);
    const arr = safeParseJson(out);

    for (const dev of arr) {
      if (!dev || !dev.Class) continue;
      const cls = String(dev.Class || '').trim();
      const name = String(dev.FriendlyName || '').trim() || cls;
      const instanceId = String(dev.InstanceId || '');

      if (!isUSBConnected(instanceId)) continue;
      if (String(dev.Status || '') === 'Unknown') continue;

      if (BLOCK_CLASSES.includes(cls)) {
        blocked.push({ class: cls, name, instanceId });
      } else if (LOG_CLASSES.includes(cls)) {
        logOnly.push({ class: cls, name, instanceId });
      }
    }
  } catch { /* non-fatal */ }

  // Pass 2: Active displays — use Get-PnpDevice -Class Monitor (Win32_DesktopMonitor is unreliable)
  let monitorCount = 1;
  let monitors = [];
  try {
    // Primary method: PnP monitor enumeration (correctly detects HDMI/DP connections)
    const psCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-PnpDevice -Class Monitor -PresentOnly | Select-Object InstanceId, FriendlyName, Status | ConvertTo-Json -Compress"';
    const out = await run(psCmd);
    const arr = safeParseJson(out);
    const active = arr.filter(m => m && m.Status === 'OK');
    monitorCount = active.length || 1;
    monitors = active.map(m => String(m.FriendlyName || m.InstanceId || 'Unknown Display'));
  } catch (err) {
    // Fallback: .NET Screen count
    try {
      const fallbackCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::AllScreens.Count"';
      const out = await run(fallbackCmd);
      monitorCount = parseInt(out.trim(), 10) || 1;
      monitors = [`${monitorCount} screen(s) detected`];
    } catch { /* non-fatal */ }
  }

  return { blocked, logOnly, monitorCount, monitors };
}

// ── Comparison against Startup Baseline ──────────────────────────────────────
/**
 * Compare a current scan result to the startup baseline.
 * Only NEW devices (not present at agent startup) are returned as violations.
 * Built-in devices (laptop camera, bluetooth, internal NIC) are ignored.
 */
function compareToBaseline(current) {
  const baseline = getStartupBaseline();

  const newBlocked = (current.blocked || []).filter(
    d => !baseline.instanceIds.has(d.instanceId)
  );
  
  // Strictly enforce 1 monitor maximum. If 2+ monitors are connected, it's a violation,
  // regardless of what the baseline was at startup.
  const extraMonitors = (current.monitorCount || 1) > 1;

  const hasNewViolation = newBlocked.length > 0 || extraMonitors;
  const violationNames = [
    ...newBlocked.map(d => `${d.name} (${d.class})`),
    ...(extraMonitors
      ? [`Multiple Displays Detected (${current.monitorCount} connected, only 1 allowed)`]
      : []),
  ];

  return {
    newBlocked,
    extraMonitors,
    hasNewViolation,
    violationNames,
    allClear: !hasNewViolation,
  };
}

module.exports = { scanHardwareDevices, initBaseline, getStartupBaseline, compareToBaseline };


/***/ }),

/***/ 357:
/***/ ((module, __unused_webpack_exports, __nccwpck_require__) => {

const fs = __nccwpck_require__(896);
const path = __nccwpck_require__(928);
const { spawn } = __nccwpck_require__(317);
const crypto = __nccwpck_require__(982);
const { unregisterProtocol } = __nccwpck_require__(654);

const APPDATA_DIR = path.join(process.env.APPDATA || '', 'VerifiHireSecureAgent');
const LEGACY_ID_FILE = path.join(APPDATA_DIR, 'instance.id');

/**
 * Packaged .exe: store instance id beside the binary so each download gets its own id.
 * Dev (node server.js): fall back to APPDATA.
 */
function getInstanceIdPath() {
  if (process.pkg) {
    return path.join(path.dirname(process.execPath), '.verifihire-instance');
  }
  if (!fs.existsSync(APPDATA_DIR)) {
    fs.mkdirSync(APPDATA_DIR, { recursive: true });
  }
  return LEGACY_ID_FILE;
}

function writeInstanceId(idPath, newId) {
  fs.writeFileSync(idPath, newId, 'utf8');
}

/**
 * Generates or retrieves a unique ID for this agent installation.
 * Each downloaded .exe gets its own id file — never reuse legacy APPDATA ids.
 */
function getInstanceId() {
  const newId = crypto.randomUUID();

  try {
    const idPath = getInstanceIdPath();

    if (fs.existsSync(idPath)) {
      const existing = fs.readFileSync(idPath, 'utf8').trim();
      if (existing && !existing.startsWith('temp-')) {
        return existing;
      }
    }

    try {
      writeInstanceId(idPath, newId);
      return newId;
    } catch (writeErr) {
      // Downloads folder may be read-only — fall back to APPDATA (fresh file per install attempt)
      if (!fs.existsSync(APPDATA_DIR)) {
        fs.mkdirSync(APPDATA_DIR, { recursive: true });
      }
      const fallbackPath = path.join(APPDATA_DIR, 'instance.id');
      if (fs.existsSync(fallbackPath)) {
        const existing = fs.readFileSync(fallbackPath, 'utf8').trim();
        if (existing && !existing.startsWith('temp-')) {
          return existing;
        }
      }
      writeInstanceId(fallbackPath, newId);
      return newId;
    }
  } catch (err) {
    console.error('[instance] Failed to manage instance ID:', err.message);
    return 'temp-' + Date.now();
  }
}

/**
 * Triggers the "Self-Destruct" sequence.
 * Creates a batch file that waits for a delay, deletes the .exe, instance file, and itself.
 * @param {number} delaySeconds - Delay before deletion (0 = immediate after process exit).
 */
function selfDestruct(delaySeconds = 0) {
  if (process.platform !== 'win32') {
    console.log('[instance] Self-destruct only supported on Windows');
    process.exit(0);
    return;
  }

  unregisterProtocol();

  const exePath = process.execPath;
  const exeDir = path.dirname(exePath);
  const batPath = path.join(exeDir, 'cleanup_verifihire.bat');
  const instancePath = getInstanceIdPath();

  const batContent = `@echo off
setlocal enabledelayedexpansion

if ${delaySeconds} GTR 0 (
  echo Waiting for cleanup period...
  timeout /t ${delaySeconds} /nobreak > nul
) else (
  timeout /t 2 /nobreak > nul
)

echo Stopping any other VerifiHire Secure Agent copies...
taskkill /F /IM VerifiHireSecureAgent.exe /T >nul 2>&1
timeout /t 2 /nobreak > nul

:retry
echo Attempting to remove Secure Agent...
del /f /q "${exePath}"
if exist "${exePath}" (
  echo File still locked, retrying in 5 seconds...
  timeout /t 5 /nobreak > nul
  goto retry
)

if exist "${instancePath}" del /f /q "${instancePath}"
if exist "${LEGACY_ID_FILE}" del /f /q "${LEGACY_ID_FILE}"
echo Cleaning up local data...
if exist "${APPDATA_DIR}" rmdir /s /q "${APPDATA_DIR}"

echo Cleanup complete.
del /f /q "%~f0"
`;

  try {
    fs.writeFileSync(batPath, batContent, 'utf8');

    spawn('cmd.exe', ['/c', 'start', '/min', 'cmd.exe', '/c', batPath], {
      detached: true,
      stdio: 'ignore',
    });

    console.log(`[instance] Agent scheduled for auto-deletion in ${delaySeconds}s. Goodbye!`);

    setTimeout(() => {
      process.exit(0);
    }, 1000);
  } catch (err) {
    console.error('[instance] Failed to initiate cleanup:', err.message);
    process.exit(0);
  }
}

module.exports = { getInstanceId, selfDestruct };


/***/ }),

/***/ 857:
/***/ ((module, __unused_webpack_exports, __nccwpck_require__) => {

const { scanProcesses, getWindowTitles } = __nccwpck_require__(798);
const { detectBlocked, loadBundledRules, setRules } = __nccwpck_require__(753);
const { getSecuritySignatures, sendSecurityCheck, sendHeartbeat, logActivity } = __nccwpck_require__(124);
const { selfDestruct } = __nccwpck_require__(357);
const { scanHardwareDevices, compareToBaseline, getStartupBaseline, initBaseline } = __nccwpck_require__(81);

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
    const { scanProcesses, getWindowTitles } = __nccwpck_require__(798);
    const processes = await scanProcesses();
    const windowTitles = await getWindowTitles();
    const verdict = await detectBlocked(processes, windowTitles, { strict: true });
    
    // Safety check: monitor might have been stopped while we were scanning
    if (!current) return;

    if (!verdict.safe) {
      lastScanWasViolation = true;
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
  knownLogOnlyMap = new Map();
  knownBlockedUsbMap = new Map();
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
}

function getMonitorState() {
  return { running: Boolean(scanTimer && heartbeatTimer), current };
}

module.exports = { startMonitor, stopMonitor, getMonitorState, triggerScanNow };


/***/ }),

/***/ 798:
/***/ ((module, __unused_webpack_exports, __nccwpck_require__) => {

const { exec } = __nccwpck_require__(317);

function run(cmd) {
  return new Promise((resolve, reject) => {
    exec(cmd, { windowsHide: true, maxBuffer: 15 * 1024 * 1024 }, (err, stdout) => {
      if (err) return reject(err);
      resolve(stdout || '');
    });
  });
}

function safeParseJson(raw) {
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

async function scanWindows() {
  const metaByPid = new Map();
  const allProcs = [];

  // Enrich with Description / Company / Path from Get-Process (all processes, not only those with Path)
  try {
    const psCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Process | Select-Object Id,Name,Path,Description,Company,SessionId | ConvertTo-Json -Compress"';
    const out = await run(psCmd);
    const parsed = safeParseJson(out);
    const arr = Array.isArray(parsed) ? parsed : [parsed];
    for (const p of arr) {
      if (!p || !p.Id) continue;
      metaByPid.set(p.Id, {
        processName: String(p.Name || '').trim(),
        processPath: String(p.Path || '').trim(),
        description: String(p.Description || '').trim(),
        company: String(p.Company || '').trim(),
        sessionId: p.SessionId !== undefined ? p.SessionId : -1,
      });
    }
  } catch { /* non-fatal */ }

  // Primary pass: Win32_Process sees 32-bit and 64-bit processes + command lines (Chrome extensions, etc.)
  try {
    const psCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | Select-Object ProcessId,Name,ExecutablePath,SessionId,CommandLine | ConvertTo-Json -Compress"';
    const out = await run(psCmd);
    const parsed = safeParseJson(out);
    const arr = Array.isArray(parsed) ? parsed : [parsed];
    const seenPids = new Set();
    for (const p of arr) {
      if (!p || !p.ProcessId) continue;
      seenPids.add(p.ProcessId);
      const meta = metaByPid.get(p.ProcessId) || {};
      allProcs.push({
        pid: p.ProcessId || 0,
        processName: String(p.Name || meta.processName || '').trim(),
        processPath: String(p.ExecutablePath || meta.processPath || '').trim(),
        commandLine: String(p.CommandLine || '').trim(),
        description: meta.description || '',
        company: meta.company || '',
        sessionId: p.SessionId !== undefined ? p.SessionId : (meta.sessionId !== undefined ? meta.sessionId : -1),
      });
    }

    // Always merge tasklist — catches tray/background processes WMI may omit
    try {
      const out = await run('tasklist /fo csv /nh');
      for (const line of out.split(/\r?\n/).filter(Boolean)) {
        const cols = line.replace(/^"|"$/g, '').split('","');
        const pid = parseInt(cols[1], 10) || 0;
        if (seenPids.has(pid)) continue;
        seenPids.add(pid);
        const meta = metaByPid.get(pid) || {};
        allProcs.push({
          pid,
          processName: String(cols[0] || meta.processName || '').trim(),
          processPath: meta.processPath || '',
          commandLine: '',
          description: meta.description || '',
          company: meta.company || '',
          sessionId: meta.sessionId !== undefined ? meta.sessionId : -1,
        });
      }
    } catch { /* ignore */ }

    if (allProcs.length > 0) return allProcs;
  } catch { /* fall through */ }

  // Fallback: tasklist only
  try {
    const out = await run('tasklist /fo csv /nh');
    for (const line of out.split(/\r?\n/).filter(Boolean)) {
      const cols = line.replace(/^"|"$/g, '').split('","');
      const pid = parseInt(cols[1], 10) || 0;
      const meta = metaByPid.get(pid) || {};
      allProcs.push({
        pid,
        processName: String(cols[0] || meta.processName || '').trim(),
        processPath: meta.processPath || '',
        commandLine: '',
        description: meta.description || '',
        company: meta.company || '',
        sessionId: meta.sessionId !== undefined ? meta.sessionId : -1,
      });
    }
  } catch { /* ignore */ }

  return allProcs;
}

/**
 * Get TCP connections grouped by PID on Windows using PowerShell Get-NetTCPConnection.
 * Returns a Map<pid, { established: number, connections: Array }>
 */
async function getConnectionsByPidWindows() {
  const map = new Map();
  try {
    const psCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue | Select-Object OwningProcess,LocalAddress,LocalPort,RemoteAddress,RemotePort,State | ConvertTo-Json -Compress"';
    const out = await run(psCmd);
    const parsed = safeParseJson(out);
    const arr = Array.isArray(parsed) ? parsed : [parsed];

    for (const c of arr) {
      const pid = c.OwningProcess || 0;
      const remoteAddr = String(c.RemoteAddress || '');
      const localAddr = String(c.LocalAddress || '');

      if (remoteAddr === '127.0.0.1' || remoteAddr === '::1' || remoteAddr === '0.0.0.0') continue;
      if (localAddr === '127.0.0.1' || localAddr === '::1') continue;

      if (!map.has(pid)) {
        map.set(pid, { established: 0, connections: [] });
      }
      const entry = map.get(pid);
      entry.established++;
      entry.connections.push({
        localAddr,
        localPort: c.LocalPort || 0,
        remoteAddr,
        remotePort: c.RemotePort || 0,
      });
    }
  } catch { /* non-fatal */ }
  return map;
}

/**
 * Get window titles for processes on Windows.
 * Returns Map<pid, { processName, title }>
 */
async function getWindowTitlesWindows() {
  const map = new Map();
  try {
    const psCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Process | Where-Object MainWindowTitle | Select-Object Id,ProcessName,MainWindowTitle | ConvertTo-Json -Compress"';
    const out = await run(psCmd);
    const parsed = safeParseJson(out);
    const arr = Array.isArray(parsed) ? parsed : [parsed];
    for (const p of arr) {
      if (p.Id && p.MainWindowTitle) {
        map.set(p.Id, {
          processName: String(p.ProcessName || '').toLowerCase(),
          title: String(p.MainWindowTitle || ''),
        });
      }
    }
  } catch { /* non-fatal */ }
  return map;
}

async function scanProcesses() {
  if (process.platform === 'win32') return scanWindows();
  return [];
}

async function getConnectionsByPid() {
  if (process.platform === 'win32') return getConnectionsByPidWindows();
  return new Map();
}

async function getWindowTitles() {
  if (process.platform === 'win32') return getWindowTitlesWindows();
  return new Map();
}

module.exports = { scanProcesses, getConnectionsByPid, getWindowTitles };


/***/ }),

/***/ 654:
/***/ ((module, __unused_webpack_exports, __nccwpck_require__) => {

/**
 * Register / unregister the verifihire:// custom URL protocol on Windows.
 * Only the packaged .exe should register — never Node dev mode.
 */
const { execSync } = __nccwpck_require__(317);
const path = __nccwpck_require__(928);

const REG_BASE = 'HKCU\\Software\\Classes\\verifihire';

function isPackagedAgent() {
  return Boolean(process.pkg);
}

function registerProtocol() {
  if (process.platform !== 'win32') {
    console.log('[protocol] Skipping protocol registration (non-Windows platform)');
    return;
  }

  if (!isPackagedAgent()) {
    console.log('[protocol] Skipping registration (not a packaged .exe)');
    return;
  }

  try {
    const launchCommand = `\\"${process.execPath}\\"`;

    execSync(`reg add "${REG_BASE}" /ve /d "URL:VerifiHire Secure Agent Protocol" /f`, { stdio: 'ignore' });
    execSync(`reg add "${REG_BASE}" /v "URL Protocol" /d "" /f`, { stdio: 'ignore' });
    execSync(`reg add "${REG_BASE}\\shell\\open\\command" /ve /d "${launchCommand}" /f`, { stdio: 'ignore' });

    console.log('[protocol] verifihire:// protocol registered');
    console.log('[protocol] Launch command:', launchCommand.replace(/\\"/g, '"'));
  } catch (err) {
    console.error('[protocol] Registration failed:', err.message);
  }
}

function unregisterProtocol() {
  if (process.platform !== 'win32') {
    return;
  }

  try {
    execSync(`reg delete "${REG_BASE}" /f`, { stdio: 'ignore' });
    console.log('[protocol] verifihire:// protocol unregistered');
  } catch (err) {
    // Key may already be absent
    if (!String(err.message || '').includes('unable to find')) {
      console.warn('[protocol] Unregister failed:', err.message);
    }
  }
}

module.exports = { registerProtocol, unregisterProtocol };


/***/ }),

/***/ 720:
/***/ ((module) => {

module.exports = eval("require")("axios");


/***/ }),

/***/ 409:
/***/ ((module) => {

module.exports = eval("require")("cors");


/***/ }),

/***/ 546:
/***/ ((module) => {

module.exports = eval("require")("express");


/***/ }),

/***/ 317:
/***/ ((module) => {

"use strict";
module.exports = require("child_process");

/***/ }),

/***/ 982:
/***/ ((module) => {

"use strict";
module.exports = require("crypto");

/***/ }),

/***/ 896:
/***/ ((module) => {

"use strict";
module.exports = require("fs");

/***/ }),

/***/ 928:
/***/ ((module) => {

"use strict";
module.exports = require("path");

/***/ }),

/***/ 330:
/***/ ((module) => {

"use strict";
module.exports = {"rE":"2.1.3"};

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __nccwpck_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		var threw = true;
/******/ 		try {
/******/ 			__webpack_modules__[moduleId](module, module.exports, __nccwpck_require__);
/******/ 			threw = false;
/******/ 		} finally {
/******/ 			if(threw) delete __webpack_module_cache__[moduleId];
/******/ 		}
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat */
/******/ 	
/******/ 	if (typeof __nccwpck_require__ !== 'undefined') __nccwpck_require__.ab = __dirname + "/";
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
const express = __nccwpck_require__(546);
const cors = __nccwpck_require__(409);
const { detectBlocked, loadBundledRules, setRules } = __nccwpck_require__(753);
const { getSecuritySignatures } = __nccwpck_require__(124);
const { startMonitor, stopMonitor, getMonitorState, triggerScanNow } = __nccwpck_require__(857);
const { scanHardwareDevices, initBaseline, compareToBaseline } = __nccwpck_require__(81);
const { registerProtocol } = __nccwpck_require__(654);
const { exec } = __nccwpck_require__(317);
const { getInstanceId, selfDestruct } = __nccwpck_require__(357);

// Read version from package.json — used for frontend version checks
const AGENT_VERSION = (__nccwpck_require__(330)/* .version */ .rE);

/**
 * Minimizes the current terminal window to the taskbar.
 * Uses PowerShell to find the window associated with the current process ID.
 */
function minimizeTerminal() {
  if (process.platform !== 'win32') return;

  // We wait 1 second to ensure the window is fully rendered before minimizing
  setTimeout(() => {
    const minimizeScript = `powershell -Command "(Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class W { [DllImport(\\"user32.dll\\")] public static extern bool ShowWindow(IntPtr h, int n); }' -PassThru)::ShowWindow((Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class C { [DllImport(\\"kernel32.dll\\")] public static extern IntPtr GetConsoleWindow(); }' -PassThru)::GetConsoleWindow(), 6)"`;

    exec(minimizeScript, (err) => {
      if (err) console.error('[server] Failed to minimize terminal:', err.message);
      else console.log('[server] Terminal minimized to taskbar');
    });
  }, 1000);
}

const app = express();
app.use(cors());
app.use(express.json());

loadBundledRules();
// Register verifihire:// only for the packaged .exe (not Node dev mode)
if (process.pkg) {
  registerProtocol();
}
// Auto-minimize terminal window to taskbar
minimizeTerminal();
// Take hardware baseline at startup so built-in devices are whitelisted
initBaseline().catch(err => console.error('[server] hardware baseline init error:', err.message));

console.log(`[server] VerifiHire Secure Agent v${AGENT_VERSION} starting...`);

app.get('/status', (_req, res) => {
  const monitorState = getMonitorState();
  const packaged = Boolean(process.pkg);
  res.json({
    installed: packaged,
    running: true,
    packaged,
    version: AGENT_VERSION,
    instance_id: getInstanceId(),
    exe_path: packaged ? process.execPath : null,
    monitor: monitorState.running,
    monitorState: monitorState.current,
    platform: process.platform,
  });
});

app.post('/scan', async (req, res) => {
  try {
    const apiBase = (req.body && req.body.backend_api_base) || process.env.SECURE_AGENT_API_BASE || '';
    if (apiBase) {
      try {
        const data = await getSecuritySignatures(apiBase);
        if (Array.isArray(data?.rules) && data.rules.length > 0) {
          setRules(data.rules);
        } else {
          loadBundledRules();
        }
      } catch {
        loadBundledRules();
      }
    } else {
      loadBundledRules();
    }

    const { scanProcesses, getWindowTitles } = __nccwpck_require__(798);
    const processes = await scanProcesses();
    const windowTitles = await getWindowTitles();
    const result = await detectBlocked(processes, windowTitles, { strict: true });
    return res.json(result);
  } catch (e) {
    return res.status(500).json({
      safe: false,
      blocked: [],
      detections: [],
      error: e.message || 'scan failed',
    });
  }
});

app.post('/scan/hardware', async (_req, res) => {
  try {
    const current = await scanHardwareDevices();
    const comparison = compareToBaseline(current);
    return res.json({
      safe: !comparison.hasNewViolation,
      blocked: comparison.violationNames,
      newDevices: comparison.newBlocked,
      extraMonitors: comparison.extraMonitors,
      monitorCount: current.monitorCount,
      logOnly: current.logOnly,
    });
  } catch (e) {
    return res.status(500).json({ safe: true, blocked: [], error: e.message || 'hardware scan failed' });
  }
});

app.post('/monitor/start', async (req, res) => {
  const body = req.body || {};
  if (!body.session_id || !body.backend_api_base) {
    return res.status(400).json({ error: 'session_id and backend_api_base are required' });
  }
  try {
    await startMonitor({
      token: body.token || '',
      sessionId: body.session_id,
      userId: body.user_id || body.token || '',
      backendApiBase: body.backend_api_base,
    });
    return res.json({ started: true });
  } catch (e) {
    return res.status(500).json({ started: false, error: e.message || 'monitor start failed' });
  }
});

app.post('/monitor/scan-now', (_req, res) => {
  const monitorState = getMonitorState();
  if (!monitorState.running) {
    return res.status(400).json({ error: 'monitor not running' });
  }
  triggerScanNow();
  return res.json({ triggered: true });
});

app.post('/monitor/stop', (req, res) => {
  stopMonitor();
  const body = req.body || {};
  const rawDelay = Number(body.destruct_delay);
  res.json({ stopped: true, destruct_delay: rawDelay });
  // destruct_delay < 0 means stop monitoring only — keep agent running for precheck retry
  if (Number.isFinite(rawDelay) && rawDelay < 0) {
    console.log('[server] Monitor stopped — agent stays running (no self-destruct)');
    return;
  }
  const destructDelay = Number.isFinite(rawDelay)
    ? Math.max(0, Math.min(rawDelay, 300))
    : 90;
  console.log(`[server] Monitor stopped — self-destruct scheduled in ${destructDelay}s`);
  setTimeout(() => {
    selfDestruct(destructDelay);
  }, 1500);
});

// Explicit shutdown endpoint (browser can call this as a fallback)
app.post('/shutdown', (req, res) => {
  const delay = req.body?.delay || 0;
  stopMonitor();
  res.json({ shutdown: true });
  console.log(`[server] Shutdown requested — self-destruct in ${delay}s`);
  setTimeout(() => {
    selfDestruct(delay);
  }, 1000);
});

const port = process.env.SECURE_AGENT_PORT || 5001;
const server = app.listen(port);

server.on('error', (err) => {
  if (err && err.code === 'EADDRINUSE') {
    console.log('');
    console.log('============================================================');
    console.log('  VerifiHire Secure Agent is ALREADY RUNNING.');
    console.log('  Check your taskbar for a minimized terminal window.');
    console.log('  Do not start a second copy — close the other one first.');
    console.log('============================================================');
    console.log('');
    // Keep the window open so the user can read the message
    setInterval(() => {}, 60000);
    return;
  }
  console.error('[server] Failed to start:', err.message);
  console.log('Press any key to close...');
  process.stdin.resume();
  process.stdin.on('data', () => process.exit(1));
});

process.on('unhandledRejection', (reason) => {
  console.error('[server] Unhandled rejection:', reason);
});

process.on('uncaughtException', (err) => {
  console.error('[server] Uncaught exception:', err.message);
  console.log('Press any key to close...');
  process.stdin.resume();
  process.stdin.on('data', () => process.exit(1));
});

let shuttingDown = false;

/** When the candidate closes the terminal window, still schedule .exe cleanup. */
const shutdown = (scheduleDestruct = false) => {
  if (shuttingDown) return;
  shuttingDown = true;
  stopMonitor();
  server.close(() => {
    if (scheduleDestruct && process.pkg) {
      console.log('[server] Terminal closing — scheduling Secure Agent removal...');
      selfDestruct(5);
      return;
    }
    process.exit(0);
  });
};

process.on('SIGINT', () => shutdown(true));
process.on('SIGTERM', () => shutdown(true));

module.exports = __webpack_exports__;
/******/ })()
;