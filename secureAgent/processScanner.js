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
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

async function scanWindows() {
  const allProcs = [];

  try {
    const combinedScript = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "$cim = Get-CimInstance Win32_Process | Select-Object ProcessId,Name,ExecutablePath,SessionId,CommandLine; $gps = Get-Process | Group-Object -Property Id -AsHashTable; $results = foreach ($c in $cim) { $id = $c.ProcessId; $p = $gps[$id][0]; [PSCustomObject]@{ Id = $id; Name = $c.Name; Path = if ($c.ExecutablePath) { $c.ExecutablePath } else { if ($p) { $p.Path } else { \'\' } }; CommandLine = $c.CommandLine; Description = if ($p) { $p.Description } else { \'\' }; Company = if ($p) { $p.Company } else { \'\' }; SessionId = if ($c.SessionId -ne $null) { $c.SessionId } else { if ($p) { $p.SessionId } else { -1 } }; } }; $results | ConvertTo-Json -Compress"';
    const out = await run(combinedScript);
    const parsed = safeParseJson(out);
    const arr = Array.isArray(parsed) ? parsed : [parsed];
    const seenPids = new Set();
    for (const p of arr) {
      if (!p || !p.Id) continue;
      seenPids.add(p.Id);
      allProcs.push({
        pid: p.Id,
        processName: String(p.Name || '').trim(),
        processPath: String(p.Path || '').trim(),
        commandLine: String(p.CommandLine || '').trim(),
        description: String(p.Description || '').trim(),
        company: String(p.Company || '').trim(),
        sessionId: p.SessionId !== undefined ? p.SessionId : -1,
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
        allProcs.push({
          pid,
          processName: String(cols[0] || '').trim(),
          processPath: '',
          commandLine: '',
          description: '',
          company: '',
          sessionId: -1,
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
