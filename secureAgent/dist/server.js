const express = require('express');
const cors = require('cors');
const { scanProcesses } = require('./processScanner');
const { detectBlocked, loadBundledRules } = require('./detector');
const { startMonitor, stopMonitor, getMonitorState } = require('./monitor');
const { scanHardwareDevices, initBaseline, compareToBaseline } = require('./hardwareScanner');
const { registerProtocol } = require('./protocolRegister');
const { exec } = require('child_process');
const { getInstanceId, selfDestruct } = require('./instanceManager');

// Read version from package.json — used for frontend version checks
const AGENT_VERSION = require('./package.json').version;

/**
 * Minimizes the current terminal window to the taskbar.
 * Uses PowerShell to find the window associated with the current process ID.
 */
function minimizeTerminal() {
  if (process.platform !== 'win32') return;

  // We wait 1 second to ensure the window is fully rendered before minimizing
  setTimeout(() => {
    const script = `
      $powershell = [PowerShell]::Create()
      $powershell.AddScript('
        Add-Type -TypeDefinition "
          using System;
          using System.Runtime.InteropServices;
          public class WindowUtils {
            [DllImport(\\"user32.dll\\")]
            public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
            [DllImport(\\"user32.dll\\")]
            public static extern IntPtr GetConsoleWindow();
          }
        "
        $hwnd = [WindowUtils]::GetConsoleWindow()
        if ($hwnd -ne [IntPtr]::Zero) {
          [WindowUtils]::ShowWindow($hwnd, 6) # 6 = SW_MINIMIZE
        }
      ')
      $powershell.Invoke()
    `;
    
    // Simpler approach that usually works for console apps:
    const simpleScript = `powershell -Command "(Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class W { [DllImport(\\"user32.dll\\")] public static extern bool ShowWindow(IntPtr h, int n); }' -PassThru)::ShowWindow((Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class C { [DllImport(\\"kernel32.dll\\")] public static extern IntPtr GetConsoleWindow(); }' -PassThru)::GetConsoleWindow(), 6)"`;
    
    exec(simpleScript, (err) => {
      if (err) console.error('[server] Failed to minimize terminal:', err.message);
      else console.log('[server] Terminal minimized to taskbar');
    });
  }, 1000);
}

const app = express();
app.use(cors());
app.use(express.json());

loadBundledRules();
// Register verifihire:// custom protocol so browsers can auto-launch the agent
registerProtocol();
// Auto-minimize terminal window to taskbar
minimizeTerminal();
// Take hardware baseline at startup so built-in devices are whitelisted
initBaseline().catch(err => console.error('[server] hardware baseline init error:', err.message));

console.log(`[server] VerifiHire Secure Agent v${AGENT_VERSION} starting...`);

app.get('/status', (_req, res) => {
  const monitorState = getMonitorState();
  res.json({
    installed: true,
    running: true,
    version: AGENT_VERSION,
    instance_id: getInstanceId(),
    monitor: monitorState.running,
    monitorState: monitorState.current,
    platform: process.platform,
  });
});

app.post('/scan', async (_req, res) => {
  try {
    const { scanProcesses, getWindowTitles } = require('./processScanner');
    const processes = await scanProcesses();
    const windowTitles = await getWindowTitles();
    const result = await detectBlocked(processes, windowTitles);
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

app.post('/monitor/stop', (_req, res) => {
  stopMonitor();
  res.json({ stopped: true });
  // Auto-delete: trigger self-destruct sequence with 30-minute delay (1800s)
  console.log('[server] Monitor stopped — self-destruct scheduled in 30 minutes');
  setTimeout(() => {
    selfDestruct(1800);
  }, 2000);
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
  process.exit(1);
});

process.on('unhandledRejection', () => {});

process.on('uncaughtException', () => {
  process.exit(1);
});

const shutdown = () => {
  stopMonitor();
  server.close(() => process.exit(0));
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
