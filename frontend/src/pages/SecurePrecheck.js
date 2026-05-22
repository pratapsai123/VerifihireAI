import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import {
  fetchAgentStatus,
  runLocalScan,
  runLocalHardwareScan,
  startBackendSecuritySession,
  startLocalMonitor,
  checkViolationStatus,
  shutdownSecureAgent,
  forceCleanupSecureAgent,
} from '../security/securityApi';
import {
  markPrecheckPassed,
  writeSessionRecord,
  clearPrecheckRecord,
  readRemoteBlockRecord,
  clearRemoteBlockRecord,
} from '../security/sessionStorage';
import {
  readTerminalCloseWarning,
  getTerminalCloseWarningMessage,
  TERMINAL_CLOSE_LIMIT,
  setTerminalCloseWarning as cacheTerminalCloseWarning,
  warningFromViolationStatus,
} from '../security/terminalCloseStrikes';
import {
  isValidPackagedAgent,
  getAgentInvalidReason,
  MINIMUM_AGENT_VERSION,
} from '../security/agentValidation';
import { logCandidateActivity } from '../utils/activityLogger';
import { checkInvitationPublicAccess, isInvitationAlreadySubmitted } from '../utils/invitationAccess';
import '../styles/SecurePrecheck.css';

const COPY = {
  scanningRemote: 'Checking for unauthorized remote access software…',
  scanningHardware: 'Checking connected devices…',
  scanningAgent: 'Verifying Secure Agent…',
  startingSession: 'Preparing your secure session…',
  blockedTitle: 'Action required before you continue',
  blockedBody: (n) =>
    n > 1
      ? `We detected ${n} prohibited programs that are not allowed during the exam. Close them completely, then scan again.`
      : 'We detected a prohibited program that is not allowed during the exam. Close it completely, then scan again.',
  blockedSteps: 'End any related background tasks in Task Manager if needed, then click Retry.',
  blockedStatus: (n) =>
    n > 1
      ? `${n} unauthorized applications are still running.`
      : 'An unauthorized application is still running.',
};

const TARGET_ROUTE_MAP = {
  assessment: (token) => `/take-assessment/${token}`,
  interview: (token) => `/interview-start/${token}`,
  ai_assessment: (token) => `/take-ai-assessment/${token}`,
  ai_interview: (token) => `/ai-interview-session/${token}`,
};

const WINDOWS_DOWNLOAD_URL = 'https://verifihireai.com/VerifiHireSecureAgent.exe';

/** Collect every blocked app label from a scan result (all tools, not just one). */
function collectBlockedApps(scanResult) {
  const labels = new Set();
  for (const app of scanResult?.blocked || []) {
    if (app) labels.add(app);
  }
  for (const d of scanResult?.detections || []) {
    if (d?.app) labels.add(d.app);
  }
  return [...labels];
}

/** Group running process names under each blocked app label for display. */
function groupProcessesByApp(scanResult) {
  const map = {};
  for (const d of scanResult?.detections || []) {
    if (!d?.app) continue;
    if (!map[d.app]) map[d.app] = new Set();
    const proc = (d.processName || '').trim();
    if (proc) map[d.app].add(proc);
  }
  return map;
}

/**
 * Tell the old agent to shut itself down so the new one can use port 5001.
 */
async function shutdownOldAgent(delaySeconds = 0) {
  try {
    await shutdownSecureAgent(delaySeconds);
  } catch {
    // Best effort — old agent may not be running
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
  const [detectedProcessesByApp, setDetectedProcessesByApp] = useState({});
  const [detectedHardware, setDetectedHardware] = useState([]);
  const [error, setError] = useState('');
  const [agentVersion, setAgentVersion] = useState('');
  const [showHelp, setShowHelp] = useState(false);
  const [terminalCloseWarning, setTerminalCloseWarning] = useState(() =>
    token ? readTerminalCloseWarning(token) : null
  );

  useEffect(() => {
    if (!token) return;

    const cached = readTerminalCloseWarning(token);
    if (cached?.chancesLeft > 0) {
      setTerminalCloseWarning(cached);
    }

    checkViolationStatus(token)
      .then((status) => {
        const fromServer = warningFromViolationStatus(status);
        if (fromServer) {
          setTerminalCloseWarning(fromServer);
          cacheTerminalCloseWarning(token, fromServer);
        } else if (!cached) {
          setTerminalCloseWarning(null);
        }
      })
      .catch(() => {});
  }, [token]);

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
      const violationStatus = await checkViolationStatus(token);
      if (violationStatus?.is_violated) {
        setPhase('permanently_blocked');
        setStatusMessage('Access Denied');
        setError('You have violated our exam policy. Access to this exam has been permanently revoked.');
        return;
      }
      const serverWarning = warningFromViolationStatus(violationStatus);
      if (serverWarning) {
        setTerminalCloseWarning(serverWarning);
        cacheTerminalCloseWarning(token, serverWarning);
      }
    } catch (err) {
      console.warn('Failed to check violation status:', err);
    }

    let status = null;
    try {
      setError('');
      setDetectedApps([]);
      setDetectedProcessesByApp({});
      setPhase('checking');
      setStatusMessage(COPY.scanningAgent);
      status = await fetchAgentStatus();
    } catch (_err) {
      setPhase('not_installed');
      setStatusMessage('Download and run VerifiHire Secure Agent to continue');
      setError('Secure Agent is not running on this computer.');
      return;
    }

    setAgentVersion(status?.version || '');

    if (!isValidPackagedAgent(status)) {
      const reason = getAgentInvalidReason(status);
      if (status?.running && status.packaged !== true) {
        await shutdownOldAgent(0);
      }
      if (status?.version && status.packaged === true) {
        setPhase('outdated');
        setStatusMessage('Your Secure Agent is outdated');
        logCandidateActivity(
          token,
          'Agent Outdated',
          `Running v${status.version}, minimum required v${MINIMUM_AGENT_VERSION}`
        );
      } else {
        setPhase('not_installed');
        setStatusMessage('Download and run VerifiHire Secure Agent to continue');
      }
      setError(reason);
      return;
    }

    try {
      setStatusMessage(COPY.scanningRemote);
      let scanResult = await runLocalScan();
      if (scanResult?.safe) {
        await new Promise((r) => setTimeout(r, 600));
        scanResult = await runLocalScan();
      }
      if (!scanResult?.safe) {
        const uniqueApps = collectBlockedApps(scanResult);
        setPhase('blocked');
        setDetectedApps(uniqueApps);
        setDetectedProcessesByApp(groupProcessesByApp(scanResult));
        setStatusMessage(COPY.blockedStatus(uniqueApps.length));
        setError(COPY.blockedSteps);
        logCandidateActivity(token, 'Precheck Blocked', `Remote apps detected: ${uniqueApps.join(', ')}`);
        clearRemoteBlockRecord(token);
        return;
      }
      clearRemoteBlockRecord(token);
      setDetectedProcessesByApp({});
    } catch (scanErr) {
      setPhase('error');
      setError(scanErr?.message || 'Failed to run security scan');
      return;
    }

    // ── Step 2: Hardware scan (USB storage, extra monitors, cameras) ─────────
    try {
      setStatusMessage(COPY.scanningHardware);
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
      setStatusMessage(COPY.startingSession);
      const userId = token;
      const session = await startBackendSecuritySession({ 
        token, 
        type, 
        user_id: userId,
        agent_instance_id: status.instance_id,
      });
      await startLocalMonitor({ session_id: session.session_id, user_id: userId, token });
      writeSessionRecord(token, {
        session_id: session.session_id,
        user_id: userId,
        type,
        agent_instance_id: status.instance_id,
        started_at: new Date().toISOString(),
      });
      markPrecheckPassed(token, type);
      clearRemoteBlockRecord(token);
      logCandidateActivity(token, 'Precheck Passed', 'Secure Agent verified and session started.');

      navigate(targetRoute, { replace: true });
    } catch (startErr) {
      if (startErr?.response?.data?.agent_expired) {
        clearPrecheckRecord(token);
        await forceCleanupSecureAgent();
        setPhase('agent_expired');
        setStatusMessage('Action Required: Download a Fresh Security Agent');
        setError(
          'This Secure Agent was already used for a previous attempt (for example after the exam was terminated). '
          + 'Any old agent window must be closed and removed before a new download will work. '
          + 'Use Task Manager to end every VerifiHireSecureAgent.exe, then download a new copy, run it once, and click Retry.'
        );
      } else if (startErr?.response?.data?.is_violated) {
        setPhase('permanently_blocked');
        setError(startErr.response.data.error || 'Access permanently revoked due to policy violation.');
      } else {
        setPhase('error');
        setError(startErr?.response?.data?.error || startErr?.message || 'Failed to start secure monitor');
      }
    }
  };

  useEffect(() => {
    if (!token) return;

    let cancelled = false;

    const run = async () => {
      setPhase('checking');
      setStatusMessage('Checking assessment status...');

      const access = await checkInvitationPublicAccess(token);
      if (cancelled) return;

      if (isInvitationAlreadySubmitted(access)) {
        navigate(targetRoute, { replace: true });
        return;
      }

      const remoteBlock = readRemoteBlockRecord(token);
      if (remoteBlock?.apps?.length) {
        setPhase('blocked');
        setDetectedApps([...new Set(remoteBlock.apps)]);
        setDetectedProcessesByApp(remoteBlock.processesByApp || {});
        setStatusMessage(COPY.blockedStatus(remoteBlock.apps.length));
        setError(COPY.blockedSteps);
        return;
      }

      logCandidateActivity(token, 'Precheck Started', `Verifying environment for ${type} assessment.`);
      startSecureFlow();
    };

    run();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, type, targetRoute, navigate]);

  const renderAction = () => {
    if (phase === 'outdated' || phase === 'agent_expired') {
      return (
        <>
          <div style={{
            background: phase === 'agent_expired' ? '#fee2e2' : '#fef3c7', 
            border: `1px solid ${phase === 'agent_expired' ? '#ef4444' : '#f59e0b'}`, 
            borderRadius: 8,
            padding: '12px 16px', marginBottom: 16,
          }}>
            <p style={{ color: phase === 'agent_expired' ? '#991b1b' : '#92400e', fontWeight: 600, margin: '0 0 4px' }}>
              {phase === 'agent_expired' ? 'Security Agent Expired' : '⚠️ Update Required'}
            </p>
            <p style={{ color: phase === 'agent_expired' ? '#991b1b' : '#92400e', margin: 0, fontSize: '0.9rem' }}>
              {phase === 'agent_expired'
                ? 'Each exam attempt needs a brand-new Secure Agent. An old copy may still be running in the background and blocking the new one.'
                : `Your current version is v${agentVersion}, but v${MINIMUM_AGENT_VERSION} or later is required.`}
            </p>
          </div>
          {phase === 'agent_expired' ? (
            <ol style={{ color: '#475569', fontSize: '0.88rem', lineHeight: 1.8, margin: '0 0 14px', paddingLeft: 20 }}>
              <li>Open <strong>Task Manager</strong> and end every <strong>VerifiHireSecureAgent.exe</strong></li>
              <li>Click <strong>Stop old Secure Agent</strong> below if an old window is still open</li>
              <li>Download a <strong>new</strong> copy and run it once (do not reuse an old .exe)</li>
              <li>Click <strong>Retry</strong></li>
            </ol>
          ) : null}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {phase === 'agent_expired' ? (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={async () => {
                  await forceCleanupSecureAgent();
                  setStatusMessage('Stopping old Secure Agent. Wait a few seconds, then download a fresh copy.');
                }}
              >
                Stop old Secure Agent
              </button>
            ) : null}
            <button
              type="button"
              className="btn btn-secondary"
              onClick={async () => {
                await shutdownOldAgent(0);
                if (phase === 'agent_expired') {
                  await forceCleanupSecureAgent();
                }
                window.open(WINDOWS_DOWNLOAD_URL, '_blank', 'noreferrer');
              }}
            >
              Download Security Agent
            </button>
          </div>
          <p style={{ color: '#64748b', fontSize: '0.85rem', marginTop: 10 }}>
            {phase === 'agent_expired'
              ? 'Only one Secure Agent may run at a time. If you see already running, end all copies in Task Manager first.'
              : 'After downloading, close the old agent, run the new file, and click Retry.'}
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

          <button className="btn btn-primary" style={{ marginTop: 8 }} onClick={() => startSecureFlow()}>
            Retry
          </button>
        </>
      );
    }
    if (phase === 'not_installed') {
      return (
        <>
          <p style={{ color: '#64748b', fontSize: '0.9rem', margin: '0 0 12px' }}>
            Download <strong>VerifiHireSecureAgent.exe</strong> (Windows only), run it once, then click Retry.
            The exam cannot start without the official Secure Agent.
          </p>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <a href={WINDOWS_DOWNLOAD_URL} download className="btn btn-secondary">Download Secure Agent (.exe)</a>
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
                    ✅ <strong>This is safe.</strong> The Secure Agent only checks for unauthorized remote access software
                    and unapproved external devices during your exam. It does not access your files or personal data.
                  </p>
                </div>
              </div>
            )}
          </div>

          <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={() => startSecureFlow()}>
            I have installed and started the agent
          </button>
        </>
      );
    }
    if (phase === 'blocked' || phase === 'blocked_hardware' || phase === 'error') {
      return <button className="btn btn-primary" onClick={startSecureFlow}>Retry</button>;
    }
    if (phase === 'permanently_blocked') {
      return null; // No retry for permanent violation
    }
    return null;
  };

  const remoteBlockCount = detectedApps.length;
  const isScanning = phase === 'checking';
  const showBlockedRemote = phase === 'blocked' && remoteBlockCount > 0;

  return (
    <div className="secure-precheck-page">
      <div className="secure-precheck-card">
        <h2>Secure Precheck</h2>
        <p className="secure-precheck-subtitle">
          We verify your device meets exam security requirements before you begin.
        </p>
        {terminalCloseWarning?.chancesLeft > 0 ? (
          <div
            style={{
              marginBottom: 16,
              padding: '14px 16px',
              borderRadius: 10,
              background: terminalCloseWarning.chancesLeft === 1 ? '#fef2f2' : '#fffbeb',
              border: `1px solid ${terminalCloseWarning.chancesLeft === 1 ? '#fecaca' : '#fde68a'}`,
            }}
          >
            <p style={{
              margin: '0 0 6px',
              fontWeight: 700,
              color: terminalCloseWarning.chancesLeft === 1 ? '#b91c1c' : '#b45309',
              fontSize: '0.95rem',
            }}>
              Secure Agent terminal was closed
              {terminalCloseWarning.closeCount > 0
                ? ` (${terminalCloseWarning.closeCount}/${TERMINAL_CLOSE_LIMIT})`
                : ''}
            </p>
            <p style={{
              margin: 0,
              color: terminalCloseWarning.chancesLeft === 1 ? '#991b1b' : '#92400e',
              lineHeight: 1.5,
              fontSize: '0.92rem',
            }}>
              {getTerminalCloseWarningMessage(terminalCloseWarning.chancesLeft)}
            </p>
          </div>
        ) : null}
        {isScanning && statusMessage ? (
          <div className="secure-precheck-status secure-precheck-status--scanning">
            <div className="secure-precheck-status-icon">
              <div className="secure-precheck-spinner" aria-hidden />
            </div>
            <p className="secure-precheck-status-text">{statusMessage}</p>
          </div>
        ) : null}

        {showBlockedRemote ? (
          <div className="secure-precheck-alert secure-precheck-alert--blocked">
            <p className="secure-precheck-alert-title">{COPY.blockedTitle}</p>
            <p className="secure-precheck-alert-body">{COPY.blockedBody(remoteBlockCount)}</p>
            <div className="secure-precheck-count-badge" role="status">
              <span aria-hidden>⚠</span>
              {remoteBlockCount} prohibited {remoteBlockCount === 1 ? 'program' : 'programs'} detected
            </div>
            <ol className="secure-precheck-steps">
              <li>Close the application completely (not minimized).</li>
              <li>If it still appears in Task Manager, end the task there.</li>
              <li>Click <strong>Retry</strong> to scan again.</li>
            </ol>
          </div>
        ) : null}

        {!isScanning && !showBlockedRemote && statusMessage ? (
          <div className="secure-precheck-status">
            <div className="secure-precheck-status-icon">ℹ️</div>
            <p className="secure-precheck-status-text">{statusMessage}</p>
          </div>
        ) : null}

        {detectedHardware.length > 0 ? (
          <div className="secure-precheck-alert secure-precheck-alert--hardware">
            <p className="secure-precheck-alert-title">External device detected</p>
            <p className="secure-precheck-alert-body">
              Please disconnect unapproved external devices before continuing.
            </p>
            <div className="secure-precheck-count-badge" style={{ borderColor: '#fde68a', color: '#b45309' }}>
              {detectedHardware.length} device{detectedHardware.length === 1 ? '' : 's'} need attention
            </div>
          </div>
        ) : null}

        {error && !showBlockedRemote ? <p className="secure-precheck-error">{error}</p> : null}
        {error && showBlockedRemote ? (
          <p className="secure-precheck-error" style={{ background: 'transparent', padding: 0, marginTop: 0 }}>
            {error}
          </p>
        ) : null}
        <div className="secure-precheck-actions">{renderAction()}</div>
      </div>
    </div>
  );
}
