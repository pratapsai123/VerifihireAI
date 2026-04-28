import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchAgentStatus, fetchSecuritySessionStatus, runLocalScan, startLocalMonitor, stopLocalMonitor } from '../security/securityApi';
import { readPrecheckRecord, readSessionRecord, clearPrecheckRecord } from '../security/sessionStorage';
import { logCandidateActivity } from '../utils/activityLogger';

export default function SecuritySessionGuard({ children, sessionType = 'assessment' }) {
  const { token } = useParams();
  const navigate = useNavigate();

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
      navigate(`/precheck/${token}?type=${encodeURIComponent(sessionType)}`, { replace: true });
      return;
    }

    let active = true;

    // ── On mount: run a fresh scan immediately ──────────────────────────────
    // This catches cases where a candidate passed precheck legitimately, then
    // opened a remote desktop app, then navigated directly to the exam URL.
    const runEntryGateScan = async () => {
      try {
        const agentStatus = await fetchAgentStatus();
        if (!agentStatus?.running) {
          // Agent not running — force back to precheck to re-establish monitoring
          if (active) {
            clearPrecheckRecord(token);
            navigate(`/precheck/${token}?type=${encodeURIComponent(sessionType)}`, { replace: true });
          }
          return;
        }

        const scanResult = await runLocalScan();
        if (!active) return;

        if (!scanResult?.safe) {
          // A blocked app is now running — log and kick them back to precheck
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

        // Scan is clean — ensure the local monitor is running for this session
        // (it may not be if they navigated directly to the URL)
        try {
          await startLocalMonitor({
            session_id: sessionRecord.session_id,
            user_id: sessionRecord.user_id || token,
            token,
          });
        } catch (_monitorErr) {
          // If monitor start fails, it's not fatal — backend polling will still catch violations
        }
      } catch (_err) {
        // If the agent is unreachable, force re-precheck so the agent is re-verified
        if (active) {
          clearPrecheckRecord(token);
          navigate(`/precheck/${token}?type=${encodeURIComponent(sessionType)}`, { replace: true });
        }
      }
    };

    runEntryGateScan();

    // ── Ongoing polling: check backend every 5s for STOP action ────────────
    const poll = async () => {
      try {
        const status = await fetchSecuritySessionStatus(sessionRecord.session_id);
        if (!active) return;
        if (status?.action === 'STOP') {
          const blockedApp = status.blocked_app || status.reason || 'Remote access tool';
          logCandidateActivity(
            token,
            'Session Terminated',
            `Exam session was terminated mid-exam. Reason: ${blockedApp}`
          );
          await stopLocalMonitor({ session_id: sessionRecord.session_id, user_id: sessionRecord.user_id });
          navigate('/session-terminated', { replace: true });
        }
      } catch (_err) {
        // If backend/local APIs are unreachable, force re-precheck instead of bypassing.
        if (!active) return;
        navigate(`/precheck/${token}?type=${encodeURIComponent(sessionType)}`, { replace: true });
      }
    };

    poll();
    const id = setInterval(poll, 5000);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [navigate, token, sessionType]);

  return children;
}
