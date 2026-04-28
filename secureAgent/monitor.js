const { scanProcesses } = require('./processScanner');
const { detectBlocked, loadBundledRules, setRules } = require('./detector');
const { getSecuritySignatures, sendSecurityCheck, sendHeartbeat } = require('./apiClient');

let scanTimer = null;
let heartbeatTimer = null;
let signatureTimer = null;
let current = null;

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
  try {
    const { scanProcesses, getWindowTitles } = require('./processScanner');
    const processes = await scanProcesses();
    const windowTitles = await getWindowTitles();
    const verdict = await detectBlocked(processes, windowTitles);
    if (!verdict.safe) {
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
      }
      return;
    }
    await sendSecurityCheck(current.backendApiBase, {
      session_id: current.sessionId,
      user_id: current.userId,
      status: 'SAFE',
      app: '',
      process_name: '',
      app_path: '',
    });
  } catch {
    // Do not silently bypass; heartbeat/status will force stop from backend timeout.
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
    }
  } catch {
    // Ignore transient network errors; backend timeout guard handles enforcement.
  }
}

async function startMonitor({ token, sessionId, userId, backendApiBase }) {
  stopMonitor();
  current = { token, sessionId, userId, backendApiBase };
  await refreshSignatures();
  scanTimer = setInterval(scanAndReport, 3000);
  heartbeatTimer = setInterval(sendAliveHeartbeat, 5000);
  signatureTimer = setInterval(refreshSignatures, 60000);
  await scanAndReport();
}

function stopMonitor() {
  if (scanTimer) clearInterval(scanTimer);
  if (heartbeatTimer) clearInterval(heartbeatTimer);
  if (signatureTimer) clearInterval(signatureTimer);
  scanTimer = null;
  heartbeatTimer = null;
  signatureTimer = null;
  current = null;
}

function getMonitorState() {
  return { running: Boolean(scanTimer && heartbeatTimer), current };
}

module.exports = { startMonitor, stopMonitor, getMonitorState };
