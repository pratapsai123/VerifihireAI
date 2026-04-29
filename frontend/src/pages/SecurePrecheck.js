import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import {
  fetchAgentStatus,
  runLocalScan,
  runLocalHardwareScan,
  startBackendSecuritySession,
  startLocalMonitor,
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

const WINDOWS_DOWNLOAD_URL = 'https://downloads.verifihireai.com/VerifiHireSecureAgent.exe';
const MACOS_DOWNLOAD_URL = 'https://downloads.verifihireai.com/VerifiHireSecureAgent.dmg';

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

  const targetRoute = useMemo(() => {
    const builder = TARGET_ROUTE_MAP[type] || TARGET_ROUTE_MAP.assessment;
    return token ? builder(token) : '/';
  }, [type, token]);

  const startSecureFlow = async () => {
    if (!token) return;
    try {
      setError('');
      setPhase('checking');
      setStatusMessage('Checking system...');
      const status = await fetchAgentStatus();
      if (!status?.running) {
        setPhase('not_running');
        setStatusMessage('Please start VerifiHire Secure Agent to continue');
        return;
      }
    } catch (_err) {
      setPhase('not_installed');
      setStatusMessage('To continue, please install VerifiHire Secure Agent');
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
      setPhase('error');
      setError(startErr?.response?.data?.error || startErr?.message || 'Failed to start secure monitor');
    }
  };

  useEffect(() => {
    logCandidateActivity(token, 'Precheck Started', `Verifying environment for ${type} assessment.`);
    startSecureFlow();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, type]);

  const renderAction = () => {
    if (phase === 'not_installed') {
      return (
        <>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <a href={WINDOWS_DOWNLOAD_URL} target="_blank" rel="noreferrer" className="btn btn-secondary">Download for Windows (.exe)</a>
            <a href={MACOS_DOWNLOAD_URL} target="_blank" rel="noreferrer" className="btn btn-secondary">Download for macOS (.dmg)</a>
          </div>
          <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={startSecureFlow}>I have installed and started the agent</button>
        </>
      );
    }
    if (phase === 'not_running' || phase === 'blocked' || phase === 'blocked_hardware' || phase === 'error') {
      return <button className="btn btn-primary" onClick={startSecureFlow}>Retry</button>;
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
