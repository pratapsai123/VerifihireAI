/** Minimum Secure Agent version candidates must run (packaged .exe). */
export const MINIMUM_AGENT_VERSION = '2.1.2';

export function compareVersions(a, b) {
  const pa = (a || '0.0.0').split('.').map(Number);
  const pb = (b || '0.0.0').split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    const va = pa[i] || 0;
    const vb = pb[i] || 0;
    if (va < vb) return -1;
    if (va > vb) return 1;
  }
  return 0;
}

/**
 * True only when the local service is the official packaged VerifiHire Secure Agent.
 * Rejects dev Node servers, stale processes, and unknown listeners on port 5001.
 */
export function isValidPackagedAgent(status) {
  if (!status?.running) return false;
  if (status.packaged !== true) return false;
  if (!status.version || compareVersions(status.version, MINIMUM_AGENT_VERSION) < 0) return false;
  const instanceId = (status.instance_id || '').trim();
  if (!instanceId || instanceId.startsWith('temp-')) return false;
  return true;
}

export function getAgentInvalidReason(status) {
  if (!status) {
    return 'VerifiHire Secure Agent is not running. Please download and run it.';
  }
  if (status.packaged !== true) {
    return 'An unsupported local process was detected. Please download and run VerifiHireSecureAgent.exe.';
  }
  if (!status.version || compareVersions(status.version, MINIMUM_AGENT_VERSION) < 0) {
    return `Your Secure Agent (v${status.version || 'unknown'}) is outdated. Download v${MINIMUM_AGENT_VERSION} or later.`;
  }
  const instanceId = (status.instance_id || '').trim();
  if (!instanceId || instanceId.startsWith('temp-')) {
    return 'Secure Agent could not verify its identity. Download and run a fresh copy.';
  }
  return 'VerifiHire Secure Agent is not ready. Please download and run it.';
}
