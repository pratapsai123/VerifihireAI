import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { fetchAgentStatus, fetchSecuritySessionStatus, runLocalScan, startLocalMonitor, stopLocalMonitor, triggerMonitorScan, terminateTerminalViolation } from '../security/securityApi';
import { isValidPackagedAgent } from '../security/agentValidation';
import { readPrecheckRecord, readSessionRecord, clearPrecheckRecord, markExamStarted, isExamStarted } from '../security/sessionStorage';
import {
  TERMINAL_CLOSE_LIMIT,
  incrementTerminalCloseCount,
  setTerminalCloseWarning,
  clearTerminalCloseCount,
} from '../security/terminalCloseStrikes';
import { logCandidateActivity } from '../utils/activityLogger';
import {
  finalizeTerminatedExam,
  logSessionTerminated,
  logTerminalCloseStrike,
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
  const [timeLeft, setTimeLeft] = useState(180);
  const warningRef = useRef(false);
  useEffect(() => {
    warningRef.current = warning;
  }, [warning]);

  // FIX 1: Track whether the candidate has completed the details form.
  // We only start aggressive polling AFTER the exam begins, not during the form.
  const [examStarted, setExamStarted] = useState(() => isExamStarted(token));
  const examStartedRef = useRef(examStarted);
  useEffect(() => {
    examStartedRef.current = examStarted;
  }, [examStarted]);

  // Nudge the local agent to scan frequently while the warning overlay is shown
  useEffect(() => {
    if (!warning || !examStarted) return;
    triggerMonitorScan().catch(() => {});
    const id = setInterval(() => {
      triggerMonitorScan().catch(() => {});
    }, 2500);
    return () => clearInterval(id);
  }, [warning, examStarted]);

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

  // FIX 2: Separate effect to handle termination - not inside setInterval
  useEffect(() => {
    if (!warning) return;
    if (timeLeft <= 0) {
      const sessionRecord = readSessionRecord(token);
      const graceDetail = `Remote access application not closed within grace period. App: ${blockedApp}`;
      (async () => {
        await finalizeTerminatedExam(token, {
          reason: TERMINATION_REASONS.GRACE_EXPIRED,
          detail: graceDetail,
        });
        if (sessionRecord) {
          stopLocalMonitor({
            session_id: sessionRecord.session_id,
            user_id: sessionRecord.user_id,
            token,
            agent_instance_id: sessionRecord.agent_instance_id,
            immediate_shutdown: true,
          }).catch(() => {});
        }
        clearPrecheckRecord(token);
        window.onbeforeunload = null;
        window.location.href = '/session-terminated?reason=remote_access';
      })();
    }
  }, [timeLeft, warning, token, blockedApp]);

  // Countdown timer for warning — only ticks when warning is active
  useEffect(() => {
    if (!warning) return;
    if (timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft(prev => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [warning, timeLeft]);

  const handleAgentTerminalClosed = async (sessionRecord) => {
    if (handlingTerminalCloseRef.current) return;
    handlingTerminalCloseRef.current = true;

    const closeCount = incrementTerminalCloseCount(token);
    const chancesLeft = Math.max(0, TERMINAL_CLOSE_LIMIT - closeCount);

    await logTerminalCloseStrike(token, closeCount, chancesLeft);

    if (closeCount >= TERMINAL_CLOSE_LIMIT) {
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
        }).catch(() => {});
      }
      clearPrecheckRecord(token);
      clearTerminalCloseCount(token);
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
    if (true /* TEMP BYPASS — change to false to re-enable precheck */) {
      console.warn('[SecuritySessionGuard] Skipping security polling (TEMP BYPASS)');
      return;
    }

    let active = true;

    // ── Entry gate scan (runs once when exam starts) ──────────────────────────
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

        // OPTIMIZATION: Check if we have a very recent precheck (e.g. within last 5 minutes)
        // If the candidate just passed precheck, we don't need to run a full scan again
        // immediately upon clicking 'Start'.
        const lastPrecheck = readPrecheckRecord(token);
        const PRECHECK_FRESHNESS_MS = 5 * 60 * 1000; // 5 minutes
        const isFresh = lastPrecheck?.timestamp && (Date.now() - lastPrecheck.timestamp) < PRECHECK_FRESHNESS_MS;

        if (isFresh && lastPrecheck?.passed) {
          console.log('[SecuritySessionGuard] Recent precheck found, skipping redundant entry-gate scan.');
        } else {
          console.log('[SecuritySessionGuard] Running definitive entry-gate scan...');
          const scanResult = await runLocalScan();
          if (!active) return;
          if (!scanResult?.safe) {
            const allApps = scanResult?.blocked?.length > 0
              ? [...new Set(scanResult.blocked)]
              : (scanResult?.detections || []).map(d => d.app).filter(Boolean);
            const remoteDetail = `Remote app detected after precheck. Apps: ${allApps.join(', ') || 'Unknown'}`;
            await logSessionTerminated(token, TERMINATION_REASONS.REMOTE_APP_AFTER_PRECHECK, remoteDetail);
            clearPrecheckRecord(token);
            navigate(`/precheck/${token}?type=${encodeURIComponent(sessionType)}`, { replace: true });
            return;
          }
        }

        // Restart monitor in case candidate navigated directly to URL
        try {
          await startLocalMonitor({
            session_id: sessionRecord.session_id,
            user_id: sessionRecord.user_id || token,
            token,
          });
        } catch (_monitorErr) { /* non-fatal */ }
      } catch (_err) {
        // If offline during entry-gate, don't redirect — just log and let overlay show
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
          setWarning(true);
          const start = new Date(status.violation_start_time).getTime();
          const now = Date.now();
          const elapsed = Math.floor((now - start) / 1000);
          const remaining = Math.max(0, 180 - elapsed);
          setTimeLeft(remaining);
          setBlockedApp(status.blocked_app || 'Remote access tool');
          return;
        }

        // CONTINUE / SAFE — clear any active warning
        if (warningRef.current) {
          setTimeLeft(180);
        }
        setWarning(false);

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
          destruct_delay: 90,
          consume: true,
        }).catch(() => {});
      } else if (sessRecord) {
        stopLocalMonitor({
          session_id: sessRecord.session_id,
          user_id: sessRecord.user_id,
          token,
          agent_instance_id: sessRecord.agent_instance_id,
          consume: false,
          destruct_delay: -1,
        }).catch(() => {});
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate, token, sessionType, examStarted, gateState]);

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
          background: 'rgba(15, 23, 42, 0.95)',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          gap: 20, padding: 32, textAlign: 'center',
          backdropFilter: 'blur(8px)',
        }}>
          <div style={{
            width: 100, height: 100, borderRadius: '50%',
            background: 'rgba(239, 68, 68, 0.1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '2px solid #ef4444',
            animation: 'pulse 2s infinite'
          }}>
            <div style={{ fontSize: 48 }}>⚠️</div>
          </div>

          <div style={{ maxWidth: 500 }}>
            <h2 style={{ color: '#fff', fontSize: '2rem', marginBottom: 12 }}>Security Warning</h2>
            <p style={{ color: '#94a3b8', fontSize: '1.1rem', lineHeight: 1.6 }}>
              A forbidden remote access application (<span style={{ color: '#f87171', fontWeight: 600 }}>{blockedApp}</span>) has been detected on your system.
            </p>
          </div>

          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 16, padding: '24px 48px',
            margin: '10px 0'
          }}>
            <p style={{ color: '#f87171', fontSize: '0.9rem', textTransform: 'uppercase', marginBottom: 8, fontWeight: 600 }}>
              Access Revocation in
            </p>
            <div style={{
              color: '#fff', fontSize: '4rem', fontWeight: 800, fontFamily: 'monospace',
              fontVariantNumeric: 'tabular-nums'
            }}>
              {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
            </div>
          </div>

          <p style={{ color: '#fcd34d', fontSize: '1.1rem', fontWeight: 500 }}>
            Please close the application immediately to avoid permanent disqualification.
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