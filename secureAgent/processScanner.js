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
  const primaryPids = new Set();

  // --- Pass 1: Get-Process (64-bit processes with full metadata) ---
  // Description and Company fields survive renaming — even if anydesk.exe → 123456.exe
  // BUT: Get-Process only sees 64-bit processes from a 64-bit shell.
  // 32-bit processes (like UltraViewer_Desktop.exe 32bit) have no Path → filtered out.
  try {
    const psCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Process | Where-Object Path | Select-Object Id,Name,Path,Description,Company,SessionId | ConvertTo-Json -Compress"';
    const out = await run(psCmd);
    const parsed = safeParseJson(out);
    const arr = Array.isArray(parsed) ? parsed : [parsed];
    for (const p of arr) {
      if (!p || !p.Id) continue;
      primaryPids.add(p.Id);
      allProcs.push({
        pid: p.Id || 0,
        processName: String(p.Name || '').trim(),
        processPath: String(p.Path || '').trim(),
        commandLine: '',
        description: String(p.Description || '').trim(),
        company: String(p.Company || '').trim(),
        sessionId: p.SessionId !== undefined ? p.SessionId : -1,
      });
    }
  } catch { /* non-fatal */ }

  // --- Pass 2: Get-CimInstance Win32_Process (catches ALL processes, including 32-bit) ---
  // Win32_Process is cross-bitness — it sees both 32-bit and 64-bit processes.
  // We only add processes NOT already captured in Pass 1 to avoid duplicates.
  try {
    const psCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | Select-Object ProcessId,Name,ExecutablePath,SessionId | ConvertTo-Json -Compress"';
    const out = await run(psCmd);
    const parsed = safeParseJson(out);
    const arr = Array.isArray(parsed) ? parsed : [parsed];
    for (const p of arr) {
      if (!p || !p.ProcessId) continue;
      if (primaryPids.has(p.ProcessId)) continue; // already captured with metadata in pass 1
      allProcs.push({
        pid: p.ProcessId || 0,
        processName: String(p.Name || '').trim(),
        processPath: String(p.ExecutablePath || '').trim(),
        commandLine: '',
        description: '', // no metadata without a resolvable path
        company: '',
        sessionId: p.SessionId !== undefined ? p.SessionId : -1,
      });
    }
  } catch {
    // Final fallback: tasklist (name-only, no session info)
    try {
      const out = await run('tasklist /fo csv /nh');
      for (const line of out.split(/\r?\n/).filter(Boolean)) {
        const cols = line.replace(/^"|"$/g, '').split('","');
        const pid = parseInt(cols[1], 10) || 0;
        if (primaryPids.has(pid)) continue;
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
  }

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
