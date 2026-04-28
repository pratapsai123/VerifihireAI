const express = require('express');
const cors = require('cors');
const { scanProcesses } = require('./processScanner');
const { detectBlocked, loadBundledRules } = require('./detector');
const { startMonitor, stopMonitor, getMonitorState } = require('./monitor');

const app = express();
app.use(cors());
app.use(express.json());

loadBundledRules();

app.get('/status', (_req, res) => {
  res.json({
    installed: true,
    running: true,
    monitor: getMonitorState().running,
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
const server = app.listen(port, () => {
  console.log(`[secureAgent] listening on http://localhost:${port}`);
});

server.on('error', (err) => {
  console.error('[secureAgent] server error:', err?.message || err);
  process.exit(1);
});

process.on('unhandledRejection', (err) => {
  console.error('[secureAgent] unhandledRejection:', err);
});

process.on('uncaughtException', (err) => {
  console.error('[secureAgent] uncaughtException:', err);
  process.exit(1);
});

const shutdown = () => {
  console.log('[secureAgent] shutting down...');
  stopMonitor();
  server.close(() => process.exit(0));
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
