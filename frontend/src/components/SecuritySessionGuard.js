import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { fetchAgentStatus, fetchSecuritySessionStatus, runLocalScan, startLocalMonitor, stopLocalMonitor } from '../security/securityApi';
import { readPrecheckRecord, readSessionRecord, clearPrecheckRecord } from '../security/sessionStorage';
import { logCandidateActivity } from '../utils/activityLogger';

export default function SecuritySessionGuard({ children, sessionType = 'assessment' }) {
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
  const [paused, setPaused] = useState(false);
  const [pauseDevice, setPauseDevice] = useState('');
  const [warning, setWarning] = useState(false);
  const [blockedApp, setBlockedApp] = useState('');
  const [timeLeft, setTimeLeft] = useState(180);

  // FIX 1: Track whether the candidate has completed the details form.
  // We only start aggressive polling AFTER the exam begins, not during the form.
  const [examStarted, setExamStarted] = useState(false);

  // FIX 2: Use a ref to reliably trigger navigation from inside setInterval.
  // This avoids the stale closure bug where navigate() is captured at mount time.
  const shouldTerminateRef = useRef(false);
  const navigateRef = useRef(navigate);
  useEffect(() => { navigateRef.current = navigate; }, [navigate]);

  // Listen for a custom event from TakeAssessment/children indicating exam has started
  useEffect(() => {
    const handler = () => setExamStarted(true);
    window.addEventListener('vh_exam_started', handler);
    return () => window.removeEventListener('vh_exam_started', handler);
  }, []);

  // FIX 2: Separate effect to handle termination - not inside setInterval
  useEffect(() => {
    if (!warning) return;
    if (timeLeft <= 0) {
      // Terminate session
      const sessionRecord = readSessionRecord(token);
      logCandidateActivity(
        token,
        'Session Terminated',
        `Grace period expired — auto-terminated. App: ${blockedApp}`
      );
      if (sessionRecord) {
        stopLocalMonitor({ session_id: sessionRecord.session_id, user_id: sessionRecord.user_id })
          .catch(() => {});
      }
      clearPrecheckRecord(token);
      window.onbeforeunload = null; // Prevent TakeAssessment from blocking the termination
      window.location.href = '/session-terminated';
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

  // Main security monitoring effect
  useEffect(() => {
    if (!token) {
      navigate('/', { replace: true });
      return;
    }

    const sessionRecord = readSessionRecord(token);
    const precheckRecord = readPrecheckRecord(token);
    const isPrecheckValid =
      precheckRecord?.passed === true &&
      precheckRecord?.type === sessionType &&
      sessionRecord?.session_id;

    if (!isPrecheckValid) {
      navigate(buildPrecheckUrl(token, sessionType), { replace: true });
      return;
    }

    // FIX 1: Only run the entry-gate scan and start polling AFTER exam has started.
    // While the candidate is filling in CandidateDetails, we do NOT poll,
    // so a temporary network hiccup won't send them back to precheck.
    if (!examStarted) return;

    let active = true;

    // ── Entry gate scan (runs once when exam starts) ──────────────────────────
    const runEntryGateScan = async () => {
      try {
        const agentStatus = await fetchAgentStatus();
        if (!agentStatus?.running) {
          if (active) {
            clearPrecheckRecord(token);
            navigate(buildPrecheckUrl(token, sessionType), { replace: true });
          }
          return;
        }

        const scanResult = await runLocalScan();
        if (!active) return;
        if (!scanResult?.safe) {
          const allApps = scanResult?.blocked?.length > 0
            ? [...new Set(scanResult.blocked)]
            : (scanResult?.detections || []).map(d => d.app).filter(Boolean);
          logCandidateActivity(
            token,
            'Session Terminated',
            `Remote app detected after precheck — session invalidated. Apps: ${allApps.join(', ') || 'Unknown'}`
          );
          clearPrecheckRecord(token);
          navigate(`/precheck/${token}?type=${encodeURIComponent(sessionType)}`, { replace: true });
          return;
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
        if (active) {
          clearPrecheckRecord(token);
          navigate(`/precheck/${token}?type=${encodeURIComponent(sessionType)}`, { replace: true });
        }
      }
    };

    runEntryGateScan();

    // ── Backend polling every 5s ─────────────────────────────────────────────
    const poll = async () => {
      try {
        const status = await fetchSecuritySessionStatus(sessionRecord.session_id);
        if (!active) return;

        if (status?.action === 'STOP') {
          const app = status.blocked_app || status.reason || 'Remote access tool';
          logCandidateActivity(
            token,
            'Session Terminated',
            `Exam session was terminated mid-exam. Reason: ${app}`
          );
          await stopLocalMonitor({ session_id: sessionRecord.session_id, user_id: sessionRecord.user_id });
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
        setWarning(false);

        if (status?.action === 'PAUSE') {
          const deviceName = status.blocked_hardware || 'External device';
          if (!paused) {
            logCandidateActivity(token, 'Exam Paused', `External device connected mid-exam: ${deviceName}`);
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
        // Silent fail during exam — don't redirect on transient errors
        console.warn('[SecuritySessionGuard] Poll error (non-fatal):', _err?.message);
      }
    };

    poll();
    const id = setInterval(poll, 5000);
    return () => {
      active = false;
      clearInterval(id);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate, token, sessionType, examStarted]);

  return (
    <>
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
