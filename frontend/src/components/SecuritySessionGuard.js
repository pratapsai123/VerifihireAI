import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { fetchAgentStatus, fetchSecuritySessionStatus, runLocalScan, startLocalMonitor, stopLocalMonitor, triggerMonitorScan, terminateTerminalViolation, recordTerminalCloseStrike } from '../security/securityApi';
import { isValidPackagedAgent } from '../security/agentValidation';
import {
  readPrecheckRecord,
  readSessionRecord,
  clearPrecheckRecord,
  markExamStarted,
  isExamStarted,
  writeRemoteBlockRecord,
} from '../security/sessionStorage';
import {
  setTerminalCloseWarning,
  clearTerminalCloseWarning,
} from '../security/terminalCloseStrikes';
import { logCandidateActivity } from '../utils/activityLogger';
import {
  finalizeTerminatedExam,
  logSessionTerminated,
  TERMINATION_REASONS,
} from '../utils/examTermination';
import ConnectionLostOverlay from './ConnectionLostOverlay';
import useNetworkStatus from '../hooks/useNetworkStatus';
import { checkInvitationPublicAccess, isInvitationAlreadySubmitted } from '../utils/invitationAccess';

export default function SecuritySessionGuard({ children, sessionType = 'assessment' }) {
  const { isOnline } = useNetworkStatus();
  const params = useParams();
  const [searchParams] = useSearchParams();
  const token = params.token || searchParams.get('token');
  const navigate = useNavigate();

  // Helper to build precheck URL with preserved query params (name, email)
  const sendBackToPrecheckForRemoteApps = (apps, processesByApp = {}) => {
    const list = [...new Set((apps || []).filter(Boolean))];
    writeRemoteBlockRecord(token, { apps: list, processesByApp });
    clearPrecheckRecord(token);
    setWarning(false);
    navigate(buildPrecheckUrl(token, sessionType), { replace: true });
  };

  const buildPrecheckUrl = (token, sessionType) => {
    const name = searchParams.get('name');
    const email = searchParams.get('email');
    let url = `/precheck/${token}?type=${encodeURIComponent(sessionType)}`;
    if (name) url += `&name=${encodeURIComponent(name)}`;
    if (email) url += `&email=${encodeURIComponent(email)}`;
    console.log('SecuritySessionGuard - Redirecting to precheck:', url);
    return url;
  };
  const [gateState, setGateState] = useState('pending'); // pending | submitted | redirecting | ready
  const [paused, setPaused] = useState(false);
  const [pauseDevice, setPauseDevice] = useState('');
  const [warning, setWarning] = useState(false);
  const [blockedApp, setBlockedApp] = useState('');
  const warningRef = useRef(false);
  useEffect(() => {
    warningRef.current = warning;
  }, [warning]);

  // Formal exam start (questions running). Remote-access polling runs from precheck onward.
  const [examStarted, setExamStarted] = useState(() => isExamStarted(token));
  const examStartedRef = useRef(examStarted);
  useEffect(() => {
    examStartedRef.current = examStarted;
  }, [examStarted]);

  // Nudge the local agent to scan frequently while the warning overlay is shown
  useEffect(() => {
    if (!warning) return;
    triggerMonitorScan().catch(() => { });
    const id = setInterval(() => {
      triggerMonitorScan().catch(() => { });
    }, 2500);
    return () => clearInterval(id);
  }, [warning]);

  // Sync isOnline with a ref for use in setInterval
  const isOnlineRef = useRef(isOnline);
  useEffect(() => {
    isOnlineRef.current = isOnline;
  }, [isOnline]);

  // FIX 2: Use a ref to reliably trigger navigation from inside setInterval.
  // This avoids the stale closure bug where navigate() is captured at mount time.
  const shouldTerminateRef = useRef(false);
  const navigateRef = useRef(navigate);
  useEffect(() => { navigateRef.current = navigate; }, [navigate]);

  const terminalAbsentRef = useRef(false);
  const handlingTerminalCloseRef = useRef(false);

  // Listen for a custom event from TakeAssessment/children indicating exam has started
  useEffect(() => {
    const handler = () => {
      markExamStarted(token);
      setExamStarted(true);
    };
    window.addEventListener('vh_exam_started', handler);
    return () => window.removeEventListener('vh_exam_started', handler);
  }, [token]);

  // No grace-period timer — the warning overlay simply blocks the exam until
  // the candidate closes the remote app. Polling will clear it automatically.

  const handleAgentTerminalClosed = async (sessionRecord) => {
    if (handlingTerminalCloseRef.current) return;
    handlingTerminalCloseRef.current = true;

    let closeCount = 0;
    let chancesLeft = 0;
    let shouldTerminate = false;

    try {
      const strike = await recordTerminalCloseStrike(token);
      closeCount = strike?.close_count ?? 0;
      chancesLeft = strike?.chances_left ?? 0;
      shouldTerminate = Boolean(strike?.should_terminate);
    } catch (err) {
      console.error('[SecuritySessionGuard] Failed to record terminal close strike:', err?.message);
      handlingTerminalCloseRef.current = false;
      return;
    }

    if (shouldTerminate) {
      const terminalDetail = 'Secure Agent terminal was closed 3 times during the exam.';
      try {
        await terminateTerminalViolation({
          session_id: sessionRecord?.session_id,
          token,
          user_id: sessionRecord?.user_id,
        });
      } catch (_err) { /* best effort */ }

      await finalizeTerminatedExam(token, {
        reason: TERMINATION_REASONS.TERMINAL_CLOSE,
        detail: terminalDetail,
      });

      if (sessionRecord) {
        await stopLocalMonitor({
          session_id: sessionRecord.session_id,
          user_id: sessionRecord.user_id,
          token,
          agent_instance_id: sessionRecord.agent_instance_id,
          immediate_shutdown: true,
        }).catch(() => { });
      }
      clearPrecheckRecord(token);
      clearTerminalCloseWarning(token);
      window.onbeforeunload = null;
      window.location.href = '/session-terminated?reason=terminal';
      return;
    }

    setTerminalCloseWarning(token, { closeCount, chancesLeft });
    clearPrecheckRecord(token);
    navigateRef.current(buildPrecheckUrl(token, sessionType), { replace: true });
  };

  // Entry gate: submitted exams skip precheck; active exams require valid precheck session.
  useEffect(() => {
    if (!token) {
      navigate('/', { replace: true });
      return;
    }

    let cancelled = false;

    const resolveGate = async () => {
      const access = await checkInvitationPublicAccess(token);
      if (cancelled) return;

      if (isInvitationAlreadySubmitted(access)) {
        setGateState('submitted');
        return;
      }

      const sessionRecord = readSessionRecord(token);
      const precheckRecord = readPrecheckRecord(token);
      const isPrecheckValid =
        precheckRecord?.passed === true &&
        precheckRecord?.type === sessionType &&
        sessionRecord?.session_id;

      // ── DEV BYPASS ────────────────────────────────────────────────
      // When REACT_APP_SKIP_PRECHECK=true, treat the entry gate as passed
      // and skip the live security polling below. Re-enable by flipping
      // the env var off.
      if (true /* TEMP BYPASS — change to false to re-enable precheck */) {
        console.warn('[SecuritySessionGuard] Skipping precheck gate (TEMP BYPASS)');
        setGateState('ready');
        return;
      }

      if (!isPrecheckValid) {
        setGateState('redirecting');
        navigate(buildPrecheckUrl(token, sessionType), { replace: true });
        return;
      }

      markExamStarted(token);
      setExamStarted(true);
      setGateState('ready');
    };

    setGateState('pending');
    resolveGate();

    return () => {
      cancelled = true;
    };
  }, [token, sessionType, navigate, searchParams]);

  // Main security monitoring effect
  useEffect(() => {
    if (!token || gateState !== 'ready') {
      return;
    }

    const sessionRecord = readSessionRecord(token);
    if (!sessionRecord?.session_id) {
      return;
    }

    // FIX 1: Only run the entry-gate scan and start polling AFTER exam has started.
    // While the candidate is filling in CandidateDetails, we do NOT poll,
    // so a temporary network hiccup won't send them back to precheck.
    if (!examStarted) return;

    // ── DEV BYPASS ────────────────────────────────────────────────
    // When REACT_APP_SKIP_PRECHECK=true, do not run the post-start
    // security polling either; otherwise it will redirect the user
    // back to /precheck the moment the agent isn't found.
    if (process.env.REACT_APP_SKIP_SECURITY_POLLING === 'true') {
      console.warn('[SecuritySessionGuard] Skipping security polling (ENV BYPASS)');
      return;
    }

    let active = true;

    const runEntryGateScan = async () => {
      try {
        const agentStatus = await fetchAgentStatus();
        if (!isValidPackagedAgent(agentStatus)) {
          if (active) {
            await handleAgentTerminalClosed(sessionRecord);
          }
          return;
        }
        terminalAbsentRef.current = false;

        triggerMonitorScan().catch(() => { });
        const scanResult = await runLocalScan();
        if (!active) return;
        if (!scanResult?.safe) {
          const allApps = scanResult?.blocked?.length > 0
            ? [...new Set(scanResult.blocked)]
            : [...new Set((scanResult?.detections || []).map((d) => d.app).filter(Boolean))];
          if (!examStartedRef.current) {
            sendBackToPrecheckForRemoteApps(allApps);
            return;
          }
          const appLabel = allApps.join(', ') || 'Remote access tool';
          const remoteDetail = `Remote app detected after precheck. Apps: ${appLabel}`;
          await logSessionTerminated(token, TERMINATION_REASONS.REMOTE_APP_AFTER_PRECHECK, remoteDetail);
          sendBackToPrecheckForRemoteApps(allApps);
          return;
        }

        try {
          await startLocalMonitor({
            session_id: sessionRecord.session_id,
            user_id: sessionRecord.user_id || token,
            token,
          });
        } catch (_monitorErr) { /* non-fatal */ }
      } catch (_err) {
        if (!navigator.onLine) {
          console.warn('[SecuritySessionGuard] Entry-gate scan failed (offline). Will retry when online.');
          return;
        }
        if (active && navigator.onLine) {
          await handleAgentTerminalClosed(sessionRecord);
        }
      }
    };

    runEntryGateScan();

    // ── Backend & Local Agent polling every 5s ─────────────────────────────
    const poll = async () => {
      // ── NETWORK CHECK: Skip polling entirely when offline ──────────────
      if (!isOnlineRef.current) {
        console.log('[SecuritySessionGuard] Offline — skipping security poll');
        return;
      }

      // ── LOCAL AGENT CHECK: Ensure the terminal is still open ──────────
      let localViolationActive = false;
      try {
        const agentStatus = await fetchAgentStatus();
        if (!isValidPackagedAgent(agentStatus)) {
          console.warn('[SecuritySessionGuard] Valid packaged Secure Agent not running mid-exam.');
          if (active && !terminalAbsentRef.current) {
            terminalAbsentRef.current = true;
            await handleAgentTerminalClosed(sessionRecord);
          }
          return;
        }
        terminalAbsentRef.current = false;

        localViolationActive = !!agentStatus.monitorState?.lastScanWasViolation;

        // ── INSTANT LOCAL VIOLATION DETECTION ────────────────────────────
        if (localViolationActive) {
          const pending = agentStatus.monitorState.pendingViolation;
          const appLabel = pending?.app || 'Remote access tool';
          // Always update the displayed app list — even while warning is already showing.
          // This ensures a second app (e.g. AnyDesk opened after Chrome Remote Desktop)
          // appears immediately without needing a page refresh.
          if (!warningRef.current) {
            setWarning(true);
          }
          setBlockedApp(appLabel);
        }
      } catch (err) {
        // If we can't reach the local agent while online, it means the terminal was closed.
        console.error('[SecuritySessionGuard] Cannot reach Secure Agent (ECONNREFUSED).');
        if (active && !terminalAbsentRef.current) {
          terminalAbsentRef.current = true;
          await handleAgentTerminalClosed(sessionRecord);
        }
        return;
      }

      try {
        const status = await fetchSecuritySessionStatus(sessionRecord.session_id);
        if (!active) return;

        if (status?.action === 'STOP') {
          const app = status.blocked_app || status.reason || 'Remote access tool';
          const remoteDetail = `Remote access application detected during exam: ${app}`;
          await finalizeTerminatedExam(token, {
            reason: TERMINATION_REASONS.REMOTE_ACCESS,
            detail: remoteDetail,
          });
          await stopLocalMonitor({
            session_id: sessionRecord.session_id,
            user_id: sessionRecord.user_id,
            token,
            agent_instance_id: sessionRecord.agent_instance_id,
            immediate_shutdown: true,
          });
          window.onbeforeunload = null;
          window.location.href = '/session-terminated';
          return;
        }

        if (status?.action === 'WARN') {
          // 3-minute grace timer is mid-exam only — before exam, hard-block on precheck page
          if (!examStartedRef.current) {
            const apps = String(status.blocked_app || '')
              .split(',')
              .map((s) => s.trim())
              .filter(Boolean);
            sendBackToPrecheckForRemoteApps(
              apps.length ? apps : ['Remote access tool']
            );
            return;
          }
          // Always update the displayed app list while WARN is active so the
          // overlay reflects the latest set of blocked apps without a refresh.
          if (!warningRef.current) {
            setWarning(true);
          }
          setBlockedApp(status.blocked_app || 'Remote access tool');
          return;
        }

        // CONTINUE / SAFE — clear any active warning
        if (!localViolationActive) {
          setWarning(false);
        }

        if (status?.action === 'PAUSE') {
          const deviceName = status.blocked_hardware || 'External device';
          if (!paused) {
            const isUsb = /usb|diskdrive|storage/i.test(deviceName);
            logCandidateActivity(
              token,
              isUsb ? 'USB Device Connected' : 'External Device Connected',
              `${deviceName} connected during exam (exam paused until removed).`,
              { category: 'hardware' }
            );
          }
          setPauseDevice(deviceName);
          setPaused(true);
          return;
        }

        if (paused) {
          logCandidateActivity(token, 'Exam Resumed', 'External device removed — exam resumed automatically');
        }
        setPaused(false);
        setPauseDevice('');
      } catch (_err) {
        // ── NETWORK-AWARE ERROR HANDLING ──────────────────────────────────
        // If we're offline, this is expected — just log and wait for reconnect.
        // If we're online but the request failed, it's a transient server error — also non-fatal.
        if (!navigator.onLine) {
          console.log('[SecuritySessionGuard] Poll failed (offline) — overlay is active, will retry when online');
        } else {
          console.warn('[SecuritySessionGuard] Poll error (non-fatal):', _err?.message);
        }
      }
    };

    let pollTimer = null;
    const schedulePoll = () => {
      poll().finally(() => {
        if (!active) return;
        const intervalMs = warningRef.current ? 1500 : 5000;
        pollTimer = setTimeout(schedulePoll, intervalMs);
      });
    };
    schedulePoll();
    return () => {
      active = false;
      if (pollTimer) clearTimeout(pollTimer);
      // Ensure the local agent stops and the terminal auto-closes when the exam ends
      // or the candidate navigates away from the guarded session.
      const sessRecord = readSessionRecord(token);
      if (sessRecord && examStartedRef.current) {
        stopLocalMonitor({
          session_id: sessRecord.session_id,
          user_id: sessRecord.user_id,
          token,
          agent_instance_id: sessRecord.agent_instance_id,
          destruct_delay: 5,
          consume: true,
        }).catch(() => { });
      } else if (sessRecord) {
        stopLocalMonitor({
          session_id: sessRecord.session_id,
          user_id: sessRecord.user_id,
          token,
          agent_instance_id: sessRecord.agent_instance_id,
          consume: false,
          destruct_delay: -1,
        }).catch(() => { });
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate, token, sessionType, gateState]);

  if (gateState === 'pending' || gateState === 'redirecting') {
    return (
      <div
        style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', color: '#64748b', fontSize: 16 }}
      >
        Checking assessment status...
      </div>
    );
  }

  return (
    <>
      {/* ── Connection Lost Overlay (highest priority) ──────────────────── */}
      {gateState === 'ready' && !isOnline && <ConnectionLostOverlay />}

      {paused && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 99999,
          background: 'rgba(0,0,0,0.92)',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          gap: 16, padding: 24, textAlign: 'center',
        }}>
          <div style={{ fontSize: 48 }}>⛔</div>
          <h2 style={{ color: '#fff', margin: 0, fontSize: '1.6rem' }}>Exam Paused</h2>
          <p style={{ color: '#fcd34d', fontSize: '1.1rem', maxWidth: 480, margin: 0 }}>
            An external device was detected:
          </p>
          <p style={{
            color: '#f87171', fontWeight: 700, fontSize: '1.2rem',
            background: 'rgba(239,68,68,0.15)', borderRadius: 8,
            padding: '10px 20px', margin: 0,
          }}>
            {pauseDevice}
          </p>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem', maxWidth: 420, margin: 0 }}>
            Please disconnect the device. The exam will resume automatically once the device is removed.
          </p>
        </div>
      )}
      {warning && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 99999,
          background: 'rgba(15, 23, 42, 0.97)',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          gap: 24, padding: 32, textAlign: 'center',
          backdropFilter: 'blur(8px)',
        }}>
          <div style={{
            width: 100, height: 100, borderRadius: '50%',
            background: 'rgba(239, 68, 68, 0.12)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '2px solid #ef4444',
            animation: 'pulse 2s infinite',
          }}>
            <div style={{ fontSize: 48 }}>⚠️</div>
          </div>

          <div style={{ maxWidth: 520 }}>
            <h2 style={{ color: '#fff', fontSize: '2rem', marginBottom: 12, margin: '0 0 12px' }}>Exam Access Blocked</h2>
            <p style={{ color: '#94a3b8', fontSize: '1.1rem', lineHeight: 1.6, margin: 0 }}>
              Unauthorized remote access software is running on your system.
              Your exam is <strong style={{ color: '#f87171' }}>paused</strong> until you close it.
            </p>
          </div>

          <div style={{
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: 14, padding: '18px 36px',
          }}>
            <p style={{ color: '#f87171', fontSize: '0.85rem', textTransform: 'uppercase', marginBottom: 6, fontWeight: 700, letterSpacing: '0.08em' }}>
              Detected application
            </p>
            <div style={{ color: '#fff', fontSize: '1.4rem', fontWeight: 700 }}>
              {blockedApp || 'Remote Access Tool'}
            </div>
          </div>

          <div style={{
            background: 'rgba(250, 204, 21, 0.08)',
            border: '1px solid rgba(250, 204, 21, 0.3)',
            borderRadius: 12, padding: '16px 28px', maxWidth: 480,
          }}>
            <p style={{ color: '#fbbf24', fontSize: '1rem', fontWeight: 600, margin: '0 0 8px' }}>
              ✅ How to resume your exam
            </p>
            <ol style={{ color: '#94a3b8', fontSize: '0.95rem', lineHeight: 1.8, margin: 0, paddingLeft: 20, textAlign: 'left' }}>
              <li>Close <strong style={{ color: '#fff' }}>{blockedApp || 'the remote access application'}</strong> completely.</li>
              <li>Open <strong style={{ color: '#fff' }}>Task Manager</strong> and end any related background processes.</li>
              <li>Your exam will <strong style={{ color: '#fff' }}>resume automatically</strong> once the app is gone.</li>
            </ol>
          </div>

          <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0 }}>
            This session is being monitored. Repeated violations may result in permanent disqualification.
          </p>

          <style>{`
            @keyframes pulse {
              0% { transform: scale(1); opacity: 1; }
              50% { transform: scale(1.05); opacity: 0.8; }
              100% { transform: scale(1); opacity: 1; }
            }
          `}</style>
        </div>
      )}
      {children}
    </>
  );
}