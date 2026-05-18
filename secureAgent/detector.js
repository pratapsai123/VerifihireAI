const fs = require('fs');
const path = require('path');

const bundledPath = path.join(__dirname, 'blacklist.json');
let runtimeRules = [];

// For exam proctoring: ANY remote desktop tool found running in the user's
// session (Session >= 1) is a policy violation — regardless of whether a
// remote session is currently active. Candidates must close these apps before
// starting an exam.

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
 * Check if a process is a known background service for a remote desktop app.
 * Service processes (like ad_svc.exe for AnyDesk) are always running even
 * when no remote session is active — they should NOT be flagged.
 */
function isServiceProcess(processName, rule) {
  const nameLower = norm(processName);
  const serviceProcs = rule.serviceProcesses || [];
  return serviceProcs.some((sp) => nameLower.includes(norm(sp)));
}

/**
 * Detect blocked remote desktop applications.
 *
 * Policy (Exam Proctoring):
 *   - ANY remote access tool found running in the USER session (Session >= 1)
 *     is a POLICY VIOLATION — even if no active remote session is in progress.
 *     Candidates must close these apps before starting an exam.
 *   - Known background SERVICES (e.g. UltraViewer_Service.exe) in Session 0
 *     are ignored — they are system daemons, not active cheating tools.
 *   - Detection is resilient to renaming via process metadata (Description/Company)
 *     and window title matching.
 */
async function detectBlocked(processes, windowTitles = new Map()) {
  const detections = [];
  const checkedPids = new Set();

  for (const p of processes || []) {
    const name = p.processName || '';
    const fullPath = p.processPath || '';
    const cmd = p.commandLine || '';
    const desc = p.description || '';
    const comp = p.company || '';
    const pid = p.pid || 0;
    const sessionId = p.sessionId;

    for (const rule of runtimeRules) {
      // ── Step 1: Identify the process by any available signal ────────────────
      const hitName = containsAny(name, rule.signatures);
      const hitPath = containsAny(fullPath, rule.pathSignatures);
      const hitCmd  = containsAny(cmd, [...(rule.signatures || []), ...(rule.pathSignatures || [])]);
      // Metadata survives binary renaming (e.g. anydesk.exe → 123456.exe)
      const hitDesc = containsAny(desc, [rule.label, ...(rule.signatures || [])]);
      const hitComp = containsAny(comp, [rule.label, ...(rule.signatures || [])]);
      // Window titles are reliable even when the exe is renamed
      const windowInfo = windowTitles.get(pid);
      const hitWindow = windowInfo
        ? containsAny(windowInfo.title, [rule.label, ...(rule.signatures || [])])
        : false;

      if (!(hitName || hitPath || hitCmd || hitDesc || hitComp || hitWindow)) {
        continue; // process doesn't match this rule at all
      }

      // ── Step 2: Skip known background service processes ──────────────────────
      // e.g. UltraViewer_Service.exe, teamviewer_service.exe — these are OS-level
      // daemons that run even when the app is not being used.
      if (isServiceProcess(name, rule)) {
        continue;
      }

      // ── Step 3: Skip Session 0 system processes (no UI/window) ──────────────
      // Session 0 is the Windows service session — processes there without a
      // window are OS services, not user-facing applications.
      if (sessionId === 0 && !hitWindow) {
        continue;
      }

      // ── Step 4: BLOCK — tool is running in user session ─────────────────────
      // At this point the process is:
      //   • Identified as a remote access tool (by name/path/metadata/window)
      //   • NOT a whitelisted background service
      //   • Running in the user session (Session >= 1) or has a visible window
      // Policy: presence alone is a violation. Close the app or the exam stops.
      const key = `${rule.label}:${pid}`;
      if (checkedPids.has(key)) continue;
      checkedPids.add(key);

      detections.push({
        app: rule.label,
        processName: name,
        processPath: fullPath,
        commandLine: cmd,
      });
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
