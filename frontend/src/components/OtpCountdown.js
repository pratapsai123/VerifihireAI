import { useEffect, useMemo, useRef, useState } from 'react';

function formatMmSs(totalSeconds) {
  const safe = Math.max(0, Number.isFinite(totalSeconds) ? totalSeconds : 0);
  const minutes = Math.floor(safe / 60);
  const seconds = safe % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

/**
 * Displays a decreasing countdown like 02:00 -> 00:00.
 *
 * Props:
 * - expiresAtMs: number | null
 * - onExpire?: () => void
 * - onRemainingSecondsChange?: (seconds: number) => void
 */
export default function OtpCountdown({ expiresAtMs, onExpire, onRemainingSecondsChange }) {
  const [now, setNow] = useState(Date.now());
  const didFireRef = useRef(false);
  const lastReportedSecondsRef = useRef(null);

  useEffect(() => {
    didFireRef.current = false;
    lastReportedSecondsRef.current = null;
  }, [expiresAtMs]);

  useEffect(() => {
    if (!expiresAtMs) return undefined;
    const id = setInterval(() => setNow(Date.now()), 250);
    return () => clearInterval(id);
  }, [expiresAtMs]);

  const remainingSeconds = useMemo(() => {
    if (!expiresAtMs) return null;
    const remainingMs = Math.max(0, expiresAtMs - now);
    return Math.ceil(remainingMs / 1000);
  }, [expiresAtMs, now]);

  useEffect(() => {
    if (remainingSeconds === null) return;
    if (typeof onRemainingSecondsChange !== 'function') return;
    if (lastReportedSecondsRef.current === remainingSeconds) return;
    lastReportedSecondsRef.current = remainingSeconds;
    onRemainingSecondsChange(remainingSeconds);
  }, [remainingSeconds, onRemainingSecondsChange]);

  useEffect(() => {
    if (remainingSeconds === null) return;
    if (remainingSeconds > 0) return;
    if (didFireRef.current) return;
    didFireRef.current = true;
    if (typeof onExpire === 'function') onExpire();
  }, [remainingSeconds, onExpire]);

  if (!expiresAtMs || remainingSeconds === null) return null;

  const isExpired = remainingSeconds <= 0;
  const isCritical = !isExpired && remainingSeconds <= 30;

  return (
    <div
      style={{
        marginTop: '0.35rem',
        fontSize: '12px',
        textAlign: 'center',
        color: isExpired ? '#dc2626' : isCritical ? '#b45309' : '#334155',
        fontWeight: 600,
      }}
    >
      {isExpired ? 'OTP expired' : `Time remaining: ${formatMmSs(remainingSeconds)}`}
    </div>
  );
}


