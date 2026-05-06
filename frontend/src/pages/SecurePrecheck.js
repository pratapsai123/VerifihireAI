import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import {
  fetchAgentStatus,
  runLocalScan,
  runLocalHardwareScan,
  startBackendSecuritySession,
  startLocalMonitor,
  checkViolationStatus,
  LOCAL_AGENT_BASE_URL,
} from '../security/securityApi';
import { markPrecheckPassed, writeSessionRecord } from '../security/sessionStorage';
import { logCandidateActivity } from '../utils/activityLogger';
import { API_BASE_URL } from '../apiConfig';

const TARGET_ROUTE_MAP = {
  assessment: (token) => `/take-assessment/${token}`,
  interview: (token) => `/interview-start/${token}`,
  ai_assessment: (token) => `/take-ai-assessment/${token}`,
  ai_interview: (token) => `/ai-interview-session/${token}`,
};

const WINDOWS_DOWNLOAD_URL = 'http://127.0.0.1:3000/VerifiHireSecureAgent.exe';
const MACOS_DOWNLOAD_URL = 'http://127.0.0.1:3000/VerifiHireSecureAgent.dmg';

// ── Version enforcement ─────────────────────────────────────────────────────
// Update this value whenever you release a new .exe that candidates MUST use.
// Any agent running a version below this will be rejected during precheck.
const MINIMUM_AGENT_VERSION = '2.0.0';

/**
 * Compare two semver version strings (e.g. "1.0.0" vs "2.0.0").
 * Returns: -1 if a < b, 0 if equal, 1 if a > b
 */
function compareVersions(a, b) {
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
 * Attempt to launch the Secure Agent via the verifihire:// custom protocol.
 * Uses a hidden iframe so the current page is not navigated away.
 * The browser will show a one-time "Allow this site to open…?" prompt.
 */
function triggerProtocolLaunch() {
  try {
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = 'verifihire://start';
    document.body.appendChild(iframe);
    // Remove the iframe after the OS has had time to process the protocol
    setTimeout(() => {
      try { document.body.removeChild(iframe); } catch {}
    }, 3000);
  } catch {
    // Protocol launch is best-effort; if it fails the user can start manually
  }
}

/**
 * Tell the old agent to shut itself down so the new one can use port 5001.
 */
async function shutdownOldAgent() {
  try {
    await axios.post(`${LOCAL_AGENT_BASE_URL}/shutdown`, {}, { timeout: 3000 });
  } catch {
    // Best effort — old agent may not have /shutdown endpoint
  }
}

export default function SecurePrecheck() {
  const { token } = useParams();
  const [query] = useSearchParams();
  const type = (query.get('type') || 'assessment').toLowerCase();
  const navigate = useNavigate();
  const [phase, setPhase] = useState('checking');
  const [statusMessage, setStatusMessage] = useState('Checking system...');
  const [detectedApps, setDetectedApps] = useState([]);
  const [detectedHardware, setDetectedHardware] = useState([]);
  const [error, setError] = useState('');
  const [agentVersion, setAgentVersion] = useState('');
  const [showHelp, setShowHelp] = useState(false);

  // Track whether we've already attempted auto-launch via protocol
  const launchAttempted = useRef(false);

  const targetRoute = useMemo(() => {
    const builder = TARGET_ROUTE_MAP[type] || TARGET_ROUTE_MAP.assessment;
    const baseRoute = token ? builder(token) : '/';
    // Preserve query parameters (name, email) when navigating
    const queryParams = query.toString();
    return queryParams ? `${baseRoute}?${queryParams}` : baseRoute;
  }, [type, token, query]);

  const startSecureFlow = async () => {
    if (!token) return;

    try {
      setPhase('checking');
      setStatusMessage('Verifying exam policy status...');
      const { is_violated } = await checkViolationStatus(token);
      if (is_violated) {
        setPhase('permanently_blocked');
        setStatusMessage('Access Denied');
        setError('You have violated our exam policy. Access to this exam has been permanently revoked.');
        return;
      }
    } catch (err) {
      console.warn('Failed to check violation status:', err);
    }

    let status;
    try {
      setError('');
      setPhase('checking');
      setStatusMessage('Checking system...');
      status = await fetchAgentStatus();
      if (!status?.running) {
        setPhase('not_running');
        setStatusMessage('Please start VerifiHire Secure Agent to continue');
        return;
      }
    } catch (_err) {
      // Agent not reachable — attempt auto-launch via verifihire:// protocol
      if (!launchAttempted.current) {
        launchAttempted.current = true;
        setPhase('launching');
        setStatusMessage('Launching Secure Agent — please allow the prompt if your browser asks...');
        triggerProtocolLaunch();
        logCandidateActivity(token, 'Agent Auto-Launch', 'Attempting to launch Secure Agent via verifihire:// protocol.');
        // Wait for the agent to start up, then retry
        setTimeout(() => startSecureFlow(), 5000);
        return;
      }
      // Auto-launch was already attempted — show manual install/start UI
      setPhase('not_installed');
      setStatusMessage('To continue, please install and start VerifiHire Secure Agent');
      return;
    }

    // ── Version check: reject old/outdated agents ─────────────────────────────
    const runningVersion = status?.version || '0.0.0';
    setAgentVersion(runningVersion);
    if (compareVersions(runningVersion, MINIMUM_AGENT_VERSION) < 0) {
      setPhase('outdated');
      setStatusMessage('Your Secure Agent is outdated and needs to be updated');
      logCandidateActivity(token, 'Agent Outdated',
        `Running v${runningVersion}, minimum required v${MINIMUM_AGENT_VERSION}`);
      // Shut down the old agent so it frees port 5001 for the new one
      await shutdownOldAgent();
      return;
    }

    try {
      setStatusMessage('Running security scan...');
      const scanResult = await runLocalScan();
      if (!scanResult?.safe) {
        const allApps = scanResult?.blocked?.length > 0
          ? scanResult.blocked
          : (scanResult?.detections || []).map(d => d.app).filter(Boolean);
        const uniqueApps = [...new Set(allApps)];
        setPhase('blocked');
        setDetectedApps(uniqueApps);
        setStatusMessage('Please close remote access applications to continue');
        logCandidateActivity(token, 'Precheck Blocked', `Remote apps detected: ${uniqueApps.join(', ')}`);
        return;
      }
    } catch (scanErr) {
      setPhase('error');
      setError(scanErr?.message || 'Failed to run security scan');
      return;
    }

    // ── Step 2: Hardware scan (USB storage, extra monitors, cameras) ─────────
    try {
      setStatusMessage('Scanning for external devices...');
      const hwResult = await runLocalHardwareScan();
      if (!hwResult?.safe) {
        const hwNames = hwResult?.blocked || [];
        setPhase('blocked_hardware');
        setDetectedHardware(hwNames);
        setStatusMessage('Please disconnect external devices to continue');
        logCandidateActivity(token, 'Precheck Blocked', `External hardware detected: ${hwNames.join(', ')}`);
        return;
      }
    } catch (hwErr) {
      console.warn('[SecurePrecheck] hardware scan unavailable:', hwErr?.message);
    }

    try {
      setStatusMessage('Starting secure session...');
      const userId = token;
      const session = await startBackendSecuritySession({ token, type, user_id: userId });
      await startLocalMonitor({ session_id: session.session_id, user_id: userId, token });
      writeSessionRecord(token, {
        session_id: session.session_id,
        user_id: userId,
        type,
        started_at: new Date().toISOString(),
      });
      markPrecheckPassed(token, type);
      logCandidateActivity(token, 'Precheck Passed', 'Secure Agent verified and session started.');

      navigate(targetRoute, { replace: true });
    } catch (startErr) {
      if (startErr?.response?.data?.is_violated) {
        setPhase('permanently_blocked');
        setError(startErr.response.data.error || 'Access permanently revoked due to policy violation.');
      } else {
        setPhase('error');
        setError(startErr?.response?.data?.error || startErr?.message || 'Failed to start secure monitor');
      }
    }
  };

  useEffect(() => {
    logCandidateActivity(token, 'Precheck Started', `Verifying environment for ${type} assessment.`);
    startSecureFlow();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, type]);

  const renderAction = () => {
    if (phase === 'launching') {
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 20, height: 20, border: '3px solid #e2e8f0',
            borderTopColor: '#3b82f6', borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
          }} />
          <span style={{ color: '#64748b', fontSize: '0.9rem' }}>
            Waiting for Secure Agent to start...
          </span>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      );
    }
    if (phase === 'outdated') {
      return (
        <>
          <div style={{
            background: '#fef3c7', border: '1px solid #f59e0b', borderRadius: 8,
            padding: '12px 16px', marginBottom: 16,
          }}>
            <p style={{ color: '#92400e', fontWeight: 600, margin: '0 0 4px' }}>
              ⚠️ Update Required
            </p>
            <p style={{ color: '#92400e', margin: 0, fontSize: '0.9rem' }}>
              Your current version is <strong>v{agentVersion}</strong>, but <strong>v{MINIMUM_AGENT_VERSION}</strong> or later is required.
              Please download and run the latest version below.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <a href={WINDOWS_DOWNLOAD_URL} target="_blank" rel="noreferrer" className="btn btn-secondary">
              Download Latest for Windows (.exe)
            </a>
            <a href={MACOS_DOWNLOAD_URL} target="_blank" rel="noreferrer" className="btn btn-secondary">
              Download Latest for macOS (.dmg)
            </a>
          </div>
          <p style={{ color: '#64748b', fontSize: '0.85rem', marginTop: 10 }}>
            After downloading, close the old agent if still running, then double-click the new file and click Retry.
          </p>

          {/* SmartScreen bypass instructions for update flow */}
          <div style={{ marginTop: 8 }}>
            <button
              onClick={() => setShowHelp(!showHelp)}
              style={{
                background: 'none', border: 'none', color: '#3b82f6', cursor: 'pointer',
                fontSize: '0.85rem', padding: 0, textDecoration: 'underline',
              }}
            >
              {showHelp ? '▾ Hide help' : '▸ Having trouble opening the file?'}
            </button>
            {showHelp && (
              <div style={{
                marginTop: 8, background: '#f0f9ff', border: '1px solid #bae6fd',
                borderRadius: 8, padding: '12px 16px', fontSize: '0.85rem', color: '#334155',
              }}>
                <p style={{ margin: '0 0 6px', fontWeight: 600, color: '#0c4a6e' }}>🛡️ If Windows says "Windows protected your PC":</p>
                <ol style={{ margin: 0, paddingLeft: 18, lineHeight: 1.7 }}>
                  <li>Click <strong style={{ color: '#0369a1' }}>"More info"</strong></li>
                  <li>Click <strong style={{ color: '#0369a1' }}>"Run anyway"</strong></li>
                </ol>
              </div>
            )}
          </div>

          <button className="btn btn-primary" style={{ marginTop: 8 }} onClick={() => { launchAttempted.current = false; startSecureFlow(); }}>
            Retry
          </button>
        </>
      );
    }
    if (phase === 'not_installed') {
      return (
        <>
          <p style={{ color: '#64748b', fontSize: '0.9rem', margin: '0 0 12px' }}>
            If the agent didn't start automatically, please download and run it manually:
          </p>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <a href={WINDOWS_DOWNLOAD_URL} target="_blank" rel="noreferrer" className="btn btn-secondary">Download for Windows (.exe)</a>
            <a href={MACOS_DOWNLOAD_URL} target="_blank" rel="noreferrer" className="btn btn-secondary">Download for macOS (.dmg)</a>
          </div>

          {/* SmartScreen bypass instructions */}
          <div style={{ marginTop: 16 }}>
            <button
              onClick={() => setShowHelp(!showHelp)}
              style={{
                background: 'none', border: 'none', color: '#3b82f6', cursor: 'pointer',
                fontSize: '0.9rem', padding: 0, textDecoration: 'underline', fontWeight: 500,
              }}
            >
              {showHelp ? '▾ Hide help' : '▸ Having trouble opening the file? (Click here)'}
            </button>
            {showHelp && (
              <div style={{
                marginTop: 12, background: '#f0f9ff', border: '1px solid #bae6fd',
                borderRadius: 8, padding: '16px 20px',
              }}>
                <p style={{ color: '#0c4a6e', fontWeight: 700, margin: '0 0 12px', fontSize: '0.95rem' }}>
                  📋 How to run the Secure Agent after downloading:
                </p>

                {/* Windows SmartScreen */}
                <div style={{ marginBottom: 16 }}>
                  <p style={{ color: '#0369a1', fontWeight: 600, margin: '0 0 6px', fontSize: '0.9rem' }}>
                    🛡️ If you see "Windows protected your PC":
                  </p>
                  <ol style={{ margin: 0, paddingLeft: 20, color: '#334155', fontSize: '0.88rem', lineHeight: 1.8 }}>
                    <li>Click the <strong style={{ color: '#0369a1' }}>"More info"</strong> text (small blue link below the message)</li>
                    <li>Click the <strong style={{ color: '#0369a1' }}>"Run anyway"</strong> button that appears</li>
                    <li>The Secure Agent will start — a terminal window will open</li>
                  </ol>
                </div>

                {/* Chrome download warning */}
                <div style={{ marginBottom: 16 }}>
                  <p style={{ color: '#0369a1', fontWeight: 600, margin: '0 0 6px', fontSize: '0.9rem' }}>
                    🌐 If Chrome shows "file is not commonly downloaded":
                  </p>
                  <ol style={{ margin: 0, paddingLeft: 20, color: '#334155', fontSize: '0.88rem', lineHeight: 1.8 }}>
                    <li>Click the <strong>"⋮" (three dots)</strong> menu on the download bar</li>
                    <li>Select <strong style={{ color: '#0369a1' }}>"Keep"</strong> or <strong style={{ color: '#0369a1' }}>"Keep anyway"</strong></li>
                    <li>Then double-click the downloaded file to run it</li>
                  </ol>
                </div>

                {/* Antivirus */}
                <div>
                  <p style={{ color: '#0369a1', fontWeight: 600, margin: '0 0 6px', fontSize: '0.9rem' }}>
                    🔒 If your antivirus blocks it:
                  </p>
                  <ol style={{ margin: 0, paddingLeft: 20, color: '#334155', fontSize: '0.88rem', lineHeight: 1.8 }}>
                    <li>Temporarily allow/whitelist <strong>VerifiHireSecureAgent.exe</strong> in your antivirus</li>
                    <li>The agent is safe — it only monitors for remote desktop apps during exams</li>
                  </ol>
                </div>

                <div style={{
                  marginTop: 14, padding: '8px 12px', background: '#ecfdf5',
                  border: '1px solid #6ee7b7', borderRadius: 6,
                }}>
                  <p style={{ color: '#065f46', margin: 0, fontSize: '0.85rem' }}>
                    ✅ <strong>This is safe.</strong> The Secure Agent only scans for unauthorized remote desktop tools
                    (like AnyDesk, TeamViewer) and external monitors during your exam. It does not access your files or personal data.
                  </p>
                </div>
              </div>
            )}
          </div>

          <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={() => { launchAttempted.current = false; startSecureFlow(); }}>I have installed and started the agent</button>
        </>
      );
    }
    if (phase === 'not_running' || phase === 'blocked' || phase === 'blocked_hardware' || phase === 'error') {
      return <button className="btn btn-primary" onClick={startSecureFlow}>Retry</button>;
    }
    if (phase === 'permanently_blocked') {
      return null; // No retry for permanent violation
    }
    return null;
  };

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: '#f8fafc', padding: 16 }}>
      <div style={{ width: '100%', maxWidth: 680, background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 24 }}>
        <h2 style={{ marginTop: 0, color: '#0f172a' }}>Secure Precheck</h2>
        <p style={{ color: '#334155' }}>{statusMessage}</p>
        {detectedApps.length > 0 ? (
          <div style={{ marginTop: 8, marginBottom: 4 }}>
            <p style={{ color: '#dc2626', fontWeight: 600, margin: '0 0 6px' }}>Detected remote apps — please close all:</p>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {detectedApps.map((app, i) => (
                <li key={i} style={{ color: '#dc2626', fontWeight: 700, fontSize: '1rem' }}>{app}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {detectedHardware.length > 0 ? (
          <div style={{ marginTop: 8, marginBottom: 4 }}>
            <p style={{ color: '#b45309', fontWeight: 600, margin: '0 0 6px' }}>External devices detected — please disconnect:</p>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {detectedHardware.map((dev, i) => (
                <li key={i} style={{ color: '#b45309', fontWeight: 700, fontSize: '1rem' }}>{dev}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}
        {renderAction()}
      </div>
    </div>
  );
}
