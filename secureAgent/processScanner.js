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

async function scanMac() {
  const out = await run('ps -axo pid=,user=,comm=,command=');
  return out.split(/\r?\n/).filter(Boolean).map((line) => {
    const trimmed = line.trim();
    const parts = trimmed.split(/\s+/);
    const pidStr = parts[0];
    const user = parts[1];
    const first = parts[2];
    const rest = parts.slice(3);
    return {
      pid: parseInt(pidStr, 10) || 0,
      processName: first || '',
      processPath: first || '',
      commandLine: rest.length ? `${first} ${rest.join(' ')}` : first || '',
      description: '',
      company: '',
      sessionId: user === 'root' ? 0 : 1,
    };
  });
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

/**
 * Get TCP connections grouped by PID on macOS.
 */
async function getConnectionsByPidMac() {
  const map = new Map();
  try {
    const out = await run('lsof -i TCP -sTCP:ESTABLISHED -nP 2>/dev/null');
    const lines = out.split(/\r?\n/).filter(Boolean);
    for (const line of lines) {
      const cols = line.trim().split(/\s+/);
      if (cols.length >= 2) {
        const pid = parseInt(cols[1], 10) || 0;
        if (!map.has(pid)) {
          map.set(pid, { established: 0, connections: [], processName: cols[0] || '' });
        }
        map.get(pid).established++;
      }
    }
  } catch {
    // ignore
  }
  return map;
}

async function scanProcesses() {
  if (process.platform === 'win32') return scanWindows();
  if (process.platform === 'darwin') return scanMac();
  return [];
}

async function getConnectionsByPid() {
  if (process.platform === 'win32') return getConnectionsByPidWindows();
  if (process.platform === 'darwin') return getConnectionsByPidMac();
  return new Map();
}

async function getWindowTitles() {
  if (process.platform === 'win32') return getWindowTitlesWindows();
  return new Map();
}

module.exports = { scanProcesses, getConnectionsByPid, getWindowTitles };
