const fs = require('fs');
const path = require('path');
const { getConnectionsByPid, getWindowTitles } = require('./processScanner');

const bundledPath = path.join(__dirname, 'blacklist.json');
let runtimeRules = [];

// How many ESTABLISHED external TCP connections an app can have before
// we consider it as running an active remote session.
// Idle remote-desktop apps typically maintain 1-2 keepalive connections
// to relay servers. Active sessions create additional data-stream connections.
const ACTIVE_CONNECTION_THRESHOLD = 3;

function loadBundledRules() {
  try {
    const raw = fs.readFileSync(bundledPath, 'utf8');
    const parsed = JSON.parse(raw);
    // Support both { rules: [...] } and plain array formats
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

/**
 * Check if a process is just a background service for a remote desktop app.
 * Service processes (like ad_svc.exe for AnyDesk) are always running even
 * when no remote session is active — they should NOT be flagged.
 */
function isServiceProcess(processName, rule) {
  const nameLower = norm(processName);
  const serviceProcs = rule.serviceProcesses || [];
  return serviceProcs.some((sp) => nameLower.includes(norm(sp)));
}

/**
 * Determines if the detected remote desktop app has an ACTIVE remote session.
 * Uses THREE detection methods:
 *
 *   1. LISTEN PORT CHECK: If there's an ESTABLISHED connection where the
 *      local port matches the app's known listen port (direct connections).
 *
 *   2. CONNECTION COUNT: If the app's PID(s) have more than ACTIVE_CONNECTION_THRESHOLD
 *      established external TCP connections, it's likely in an active session.
 *      (Idle apps have 1-2 keepalive connections; active sessions create more.)
 *
 *   3. WINDOW TITLE: If the app has a visible window with a title matching
 *      known session-related patterns.
 */
async function isActiveSession(processName, processPid, rule, connectionsByPid, windowTitles) {
  const indicators = rule.activeIndicators || {};
  const listenPorts = indicators.listenPorts || [];
  const windowTitleKeywords = indicators.windowTitles || [];

  // Collect all PIDs belonging to this app (from the process list)
  // We'll check the specific PID passed in
  const connInfo = connectionsByPid.get(processPid);

  // ---- METHOD 1: Listen port check (direct incoming connections) ----
  if (connInfo && listenPorts.length > 0) {
    for (const conn of connInfo.connections || []) {
      if (listenPorts.includes(conn.localPort)) {
        console.log(`[detector] ACTIVE (listen port): ${rule.label} PID=${processPid} incoming on port ${conn.localPort} from ${conn.remoteAddr}`);
        return true;
      }
    }
  }

  // ---- METHOD 2: Connection count threshold (relay-based sessions) ----
  if (connInfo && connInfo.established >= ACTIVE_CONNECTION_THRESHOLD) {
    console.log(`[detector] ACTIVE (conn count): ${rule.label} PID=${processPid} has ${connInfo.established} established connections (threshold=${ACTIVE_CONNECTION_THRESHOLD})`);
    return true;
  }

  // ---- METHOD 3: Window title check ----
  // When remote desktop apps have an active session, they show session-related windows
  if (windowTitleKeywords.length > 0) {
    for (const [wPid, wInfo] of windowTitles.entries()) {
      // Check if this window belongs to the app
      if (containsAny(wInfo.processName, rule.signatures)) {
        const titleLower = norm(wInfo.title);
        // Check for session-related window titles
        // AnyDesk shows desk IDs, TeamViewer shows "TeamViewer" with session info
        // A visible main window with a title often means active use
        for (const kw of windowTitleKeywords) {
          if (titleLower.includes(norm(kw))) {
            // Check if the window title suggests an active session
            // (not just the main idle window)
            // Session windows often contain numbers (remote IDs), "session", "connected"
            const hasSessionIndicators =
              /\d{6,}/.test(wInfo.title) ||           // AnyDesk remote IDs are 9+ digits
              /session/i.test(wInfo.title) ||
              /connected/i.test(wInfo.title) ||
              /remote/i.test(wInfo.title) ||
              /controlling/i.test(wInfo.title) ||
              /\s-\s/.test(wInfo.title);               // "AnyDesk - 123456789" pattern

            if (hasSessionIndicators) {
              console.log(`[detector] ACTIVE (window title): ${rule.label} window="${wInfo.title}"`);
              return true;
            }
          }
        }
      }
    }
  }

  return false;
}

/**
 * Detect blocked remote desktop applications.
 *
 * Logic:
 *   - Apps that are installed but idle (running as SYSTEM/root services in Session 0) are IGNORED.
 *   - Apps running in the USER session (Session > 0) are BLOCKED.
 *   - Even if the file is renamed (e.g. 123456.exe), we detect it via:
 *     1. Metadata (File Description / Company Name)
 *     2. Window Titles (AnyDesk windows almost always say "AnyDesk")
 */
async function detectBlocked(processes, windowTitles = new Map()) {
  const detections = [];
  const checkedPids = new Set(); 

  // Fetch TCP connections once for active-session checks
  const { getConnectionsByPid } = require('./processScanner');
  let connectionsByPid = new Map();
  try {
    connectionsByPid = await getConnectionsByPid();
  } catch { /* non-fatal */ }

  for (const p of processes || []) {
    const name = p.processName || '';
    const fullPath = p.processPath || '';
    const cmd = p.commandLine || '';
    const desc = p.description || '';
    const comp = p.company || '';
    const pid = p.pid || 0;
    const sessionId = p.sessionId;

    for (const rule of runtimeRules) {
      // 1. Identification by Name/Path/Cmd
      const hitName = containsAny(name, rule.signatures);
      const hitPath = containsAny(fullPath, rule.pathSignatures);
      const hitCmd = containsAny(cmd, [...(rule.signatures || []), ...(rule.pathSignatures || [])]);
      
      // 2. Identification by Metadata (Handles Renaming)
      // AnyDesk usually has Description="AnyDesk" and Company="AnyDesk Software GmbH"
      const hitDesc = containsAny(desc, [rule.label, ...(rule.signatures || [])]);
      const hitComp = containsAny(comp, [rule.label, ...(rule.signatures || [])]);

      // 3. Identification by Window Title (Handles Renaming + Hidden processes)
      const windowInfo = windowTitles.get(pid);
      const hitWindow = windowInfo ? containsAny(windowInfo.title, [rule.label, ...(rule.signatures || [])]) : false;

      if (hitName || hitPath || hitCmd || hitDesc || hitComp || hitWindow) {
        // Explicitly skip known background services by name
        if (isServiceProcess(name, rule)) {
          continue;
        }

        // CRITICAL CHECK: Ignore System Services
        if (sessionId === 0) {
          // If we have a window title, it's definitely NOT a background service (services can't have UI windows in Session 0 easily)
          if (!hitWindow) {
            console.log(`[detector] Ignored background service: ${name} (PID: ${pid}, Session: ${sessionId})`);
            continue;
          }
        }

        const key = `${rule.label}:${pid}`;
        if (checkedPids.has(key)) continue;
        checkedPids.add(key);

        // CRITICAL: Only block if the app has an ACTIVE remote session.
        // Apps like AnyDesk can be installed and running idle — that is NOT cheating.
        const active = await isActiveSession(name, pid, rule, connectionsByPid, windowTitles);
        if (!active) {
          console.log(`[detector] IDLE (no active session): ${rule.label} (PID: ${pid}, Session: ${sessionId}) — skipping`);
          continue;
        }

        console.log(`[detector] BLOCKED: ${rule.label} ACTIVE session detected (Method: ${hitWindow ? 'WINDOW' : 'PROCESS'}) (PID: ${pid}, Session: ${sessionId})`);
        
        detections.push({
          app: rule.label,
          processName: name,
          processPath: fullPath,
          commandLine: cmd,
        });
      }
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
