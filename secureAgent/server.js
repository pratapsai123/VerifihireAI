const express = require('express');
const cors = require('cors');
const { scanProcesses } = require('./processScanner');
const { detectBlocked, loadBundledRules } = require('./detector');
const { startMonitor, stopMonitor, getMonitorState } = require('./monitor');
const { scanHardwareDevices, initBaseline, compareToBaseline } = require('./hardwareScanner');

const app = express();
app.use(cors());
app.use(express.json());

loadBundledRules();
// Take hardware baseline at startup so built-in devices are whitelisted
initBaseline().catch(err => console.error('[server] hardware baseline init error:', err.message));

app.get('/status', (_req, res) => {
  const monitorState = getMonitorState();
  res.json({
    installed: true,
    running: true,
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
  return res.json({ stopped: true });
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
