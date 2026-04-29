const { exec } = require('child_process');

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
      // Include BOTH blocked-class AND logOnly-class InstanceIds.
      // This ensures built-in devices (laptop mouse, keyboard, bluetooth adapter)
      // are whitelisted and never reported as "newly connected".
      instanceIds: new Set([
        ...(scan.blocked || []).map(d => d.instanceId),
        ...(scan.logOnly || []).map(d => d.instanceId),
      ]),
      monitorCount: scan.monitorCount || 1,
    };
    console.log(
      `[hardwareScanner] Startup baseline: ${STARTUP_BASELINE.instanceIds.size} device(s) whitelisted, ${STARTUP_BASELINE.monitorCount} monitor(s)`
    );
  } catch (err) {
    console.error('[hardwareScanner] initBaseline error:', err.message);
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
  } catch (err) {
    console.error('[hardwareScanner] PnP scan error:', err.message);
  }

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
    } catch {
      console.error('[hardwareScanner] Monitor scan error:', err.message);
    }
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
