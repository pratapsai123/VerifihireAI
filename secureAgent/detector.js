const fs = require('fs');
const path = require('path');

const bundledPath = path.join(__dirname, 'blacklist.json');
let runtimeRules = [];

function loadBundledRules() {
  try {
    const raw = fs.readFileSync(bundledPath, 'utf8');
    const parsed = JSON.parse(raw);
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

function isServiceProcess(processName, rule) {
  const nameLower = norm(processName);
  const serviceProcs = rule.serviceProcesses || [];
  return serviceProcs.some((sp) => nameLower.includes(norm(sp)));
}

function pushDetection(detections, checkedPids, rule, pid, fields) {
  const key = `${rule.label}:${pid}`;
  if (checkedPids.has(key)) return;
  checkedPids.add(key);
  detections.push({
    app: rule.label,
    processName: fields.processName || '',
    processPath: fields.processPath || '',
    commandLine: fields.commandLine || '',
  });
}

/**
 * @param {object[]} processes
 * @param {Map<number, {title: string}>} windowTitles
 * @param {{ strict?: boolean }} options - strict=true for precheck: catch background/tray/session-0 UI processes
 */
async function detectBlocked(processes, windowTitles = new Map(), options = {}) {
  const strict = options.strict === true;
  const detections = [];
  const checkedPids = new Set();
  const matchedLabels = new Set();

  const titleSignaturesForRule = (rule) => [
    rule.label,
    ...(rule.signatures || []),
    ...((rule.activeIndicators && rule.activeIndicators.windowTitles) || []),
  ];

  for (const p of processes || []) {
    const name = p.processName || '';
    const fullPath = p.processPath || '';
    const cmd = p.commandLine || '';
    const desc = p.description || '';
    const comp = p.company || '';
    const pid = p.pid || 0;
    const sessionId = p.sessionId;

    for (const rule of runtimeRules) {
      const hitName = containsAny(name, rule.signatures);
      const hitPath = containsAny(fullPath, rule.pathSignatures);
      const hitCmd = containsAny(cmd, [
        ...(rule.signatures || []),
        ...(rule.pathSignatures || []),
      ]);
      const hitDesc = containsAny(desc, [rule.label, ...(rule.signatures || [])]);
      const hitComp = containsAny(comp, [rule.label, ...(rule.signatures || [])]);
      const windowInfo = windowTitles.get(pid);
      const hitWindow = windowInfo
        ? containsAny(windowInfo.title, titleSignaturesForRule(rule))
        : false;

      if (!(hitName || hitPath || hitCmd || hitDesc || hitComp || hitWindow)) {
        continue;
      }

      // Mid-exam check: require active window title for tray-capable remote desktop apps
      // to prevent false positives when they are running idle in the background tray.
      const isTrayApp = ['AnyDesk', 'TeamViewer', 'UltraViewer', 'RustDesk', 'Supremo'].includes(rule.label);
      if (isTrayApp && !hitWindow) {
        continue;
      }

      // Precheck (strict): flag background/tray helpers — only skip OS daemons like teamviewer_service
      if (!strict && isServiceProcess(name, rule)) {
        continue;
      }
      if (strict && isServiceProcess(name, rule)) {
        continue;
      }

      if (!strict && sessionId === 0 && !hitWindow) {
        continue;
      }
      if (strict && sessionId === 0 && !hitWindow && !hitName && !hitPath && !hitCmd) {
        continue;
      }

      pushDetection(detections, checkedPids, rule, pid, {
        processName: name,
        processPath: fullPath,
        commandLine: cmd,
      });
      matchedLabels.add(rule.label);
    }
  }

  // Window title pass — catches Chrome TeamViewer extension and tray-only UIs
  for (const [pid, windowInfo] of windowTitles) {
    for (const rule of runtimeRules) {
      if (matchedLabels.has(rule.label)) continue;
      if (!containsAny(windowInfo.title, titleSignaturesForRule(rule))) continue;
      const procName = windowInfo.processName || '';
      if (isServiceProcess(procName, rule)) continue;
      pushDetection(detections, checkedPids, rule, pid, {
        processName: procName,
        processPath: '',
        commandLine: '',
      });
      matchedLabels.add(rule.label);
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
