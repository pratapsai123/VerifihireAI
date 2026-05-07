import React from 'react';
import useNetworkStatus from '../hooks/useNetworkStatus';

/**
 * Full-screen overlay that appears when the browser loses internet connectivity.
 * 
 * Behaviour:
 *   • Shows immediately when `navigator.onLine` becomes false.
 *   • Displays a live "disconnected for X seconds" counter.
 *   • Auto-dismisses the instant the connection is restored.
 *   • Does NOT terminate the exam — the SecuritySessionGuard and backend
 *     heartbeat timeout (5 min) handle the real enforcement.
 */
export default function ConnectionLostOverlay() {
  const { isOnline, offlineDurationSec, refresh } = useNetworkStatus();

  if (isOnline) return null;

  const minutes = Math.floor(offlineDurationSec / 60);
  const seconds = offlineDurationSec % 60;
  const formattedTime = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  // Backend allows up to 600s (10 min) before termination
  const maxGraceSec = 600;
  const remaining = Math.max(0, maxGraceSec - offlineDurationSec);
  const remainMin = Math.floor(remaining / 60);
  const remainSec = remaining % 60;
  const remainFormatted = `${String(remainMin).padStart(2, '0')}:${String(remainSec).padStart(2, '0')}`;
  const urgencyPercent = Math.min(100, (offlineDurationSec / maxGraceSec) * 100);

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 999999,
      background: 'rgba(15, 23, 42, 0.97)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 24,
      padding: 32,
      textAlign: 'center',
      backdropFilter: 'blur(12px)',
    }}>
      {/* Animated wifi icon */}
      <div style={{
        width: 120,
        height: 120,
        borderRadius: '50%',
        background: `rgba(251, 191, 36, ${0.08 + urgencyPercent * 0.002})`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: `2px solid ${urgencyPercent > 80 ? '#ef4444' : '#fbbf24'}`,
        animation: 'connectionPulse 2s ease-in-out infinite',
      }}>
        <div style={{ fontSize: 56 }}>📡</div>
      </div>

      <div style={{ maxWidth: 520 }}>
        <h2 style={{
          color: '#fff',
          fontSize: '1.8rem',
          marginBottom: 8,
          fontWeight: 700,
        }}>
          Connection Lost
        </h2>
        <p style={{
          color: '#94a3b8',
          fontSize: '1.1rem',
          lineHeight: 1.6,
          margin: '0 0 8px',
        }}>
          Your internet connection has been interrupted. Please restore connectivity immediately to continue your assessment.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', justifyContent: 'center' }}>
        {/* Disconnected-for counter */}
        <div style={{
          background: 'rgba(251, 191, 36, 0.1)',
          border: '1px solid rgba(251, 191, 36, 0.3)',
          borderRadius: 16,
          padding: '20px 40px',
          minWidth: 260,
        }}>
          <p style={{
            color: '#fbbf24',
            fontSize: '0.85rem',
            textTransform: 'uppercase',
            letterSpacing: 1,
            marginBottom: 6,
            fontWeight: 600,
          }}>
            Disconnected for
          </p>
          <div style={{
            color: '#fff',
            fontSize: '3rem',
            fontWeight: 800,
            fontFamily: 'monospace',
            fontVariantNumeric: 'tabular-nums',
          }}>
            {formattedTime}
          </div>
        </div>

        {/* Grace period remaining */}
        <div style={{
          background: urgencyPercent > 80
            ? 'rgba(239, 68, 68, 0.15)'
            : 'rgba(100, 116, 139, 0.1)',
          border: `1px solid ${urgencyPercent > 80 ? 'rgba(239, 68, 68, 0.4)' : 'rgba(100, 116, 139, 0.25)'}`,
          borderRadius: 12,
          padding: '20px 40px',
          minWidth: 260,
        }}>
          <p style={{
            color: urgencyPercent > 80 ? '#f87171' : '#94a3b8',
            fontSize: '0.85rem',
            textTransform: 'uppercase',
            letterSpacing: 1,
            marginBottom: 4,
            fontWeight: 600,
          }}>
            Auto-terminate in
          </p>
          <div style={{
            color: urgencyPercent > 80 ? '#f87171' : '#cbd5e1',
            fontSize: '3rem',
            fontWeight: 700,
            fontFamily: 'monospace',
            fontVariantNumeric: 'tabular-nums',
          }}>
            {remainFormatted}
          </div>
        </div>
      </div>

      {/* Manual Retry Button */}
      <button 
        onClick={refresh}
        style={{
          background: '#fbbf24',
          color: '#0f172a',
          border: 'none',
          borderRadius: 12,
          padding: '12px 32px',
          fontSize: '1.1rem',
          fontWeight: 700,
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          boxShadow: '0 4px 12px rgba(251, 191, 36, 0.3)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(251, 191, 36, 0.4)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(251, 191, 36, 0.3)';
        }}
      >
        🔄 Retry Connection
      </button>

      {/* Progress bar */}
      <div style={{
        width: '100%',
        maxWidth: 540,
        height: 8,
        background: 'rgba(100, 116, 139, 0.2)',
        borderRadius: 4,
        overflow: 'hidden',
      }}>
        <div style={{
          width: `${urgencyPercent}%`,
          height: '100%',
          background: urgencyPercent > 80
            ? 'linear-gradient(90deg, #f87171, #ef4444)'
            : urgencyPercent > 50
              ? 'linear-gradient(90deg, #fbbf24, #f59e0b)'
              : 'linear-gradient(90deg, #34d399, #10b981)',
          borderRadius: 4,
          transition: 'width 1s linear',
        }} />
      </div>

      <p style={{
        color: '#64748b',
        fontSize: '0.95rem',
        maxWidth: 450,
        margin: 0,
        lineHeight: 1.5,
      }}>
        Please check your Wi-Fi or network cable. Note: The exam timer is still running in the background.
      </p>

      <style>{`
        @keyframes connectionPulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.06); opacity: 0.85; }
          100% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
