import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom hook that monitors browser network connectivity.
 * 
 * Returns:
 *   - isOnline: boolean — current connection state
 *   - wasOffline: boolean — true if the user was offline at any point during the session
 *   - offlineSince: Date|null — timestamp when the connection was first lost
 *   - offlineDurationSec: number — how many seconds the user has been offline (live counter)
 * 
 * Also dispatches global custom events on window:
 *   - 'vh_network_offline' — fired when connection is lost
 *   - 'vh_network_online'  — fired when connection is restored
 */
export default function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(() => navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);
  const [offlineSince, setOfflineSince] = useState(null);
  const [offlineDurationSec, setOfflineDurationSec] = useState(0);
  const durationTimerRef = useRef(null);

  // Start a 1s counter while offline so the overlay can show elapsed time
  const startDurationCounter = useCallback((since) => {
    if (durationTimerRef.current) clearInterval(durationTimerRef.current);
    durationTimerRef.current = setInterval(() => {
      setOfflineDurationSec(Math.floor((Date.now() - since) / 1000));
    }, 1000);
  }, []);

  const stopDurationCounter = useCallback(() => {
    if (durationTimerRef.current) {
      clearInterval(durationTimerRef.current);
      durationTimerRef.current = null;
    }
    setOfflineDurationSec(0);
  }, []);

  const refresh = useCallback(() => {
    const status = navigator.onLine;
    setIsOnline(status);
    if (status) {
      setOfflineSince(null);
      stopDurationCounter();
      window.dispatchEvent(new CustomEvent('vh_network_online', { detail: { timestamp: new Date() } }));
    } else {
      const now = new Date();
      setWasOffline(true);
      setOfflineSince(now);
      startDurationCounter(now.getTime());
      window.dispatchEvent(new CustomEvent('vh_network_offline', { detail: { timestamp: now } }));
    }
  }, [startDurationCounter, stopDurationCounter]);

  useEffect(() => {
    const goOffline = () => {
      console.warn('[useNetworkStatus] Browser went OFFLINE');
      const now = new Date();
      setIsOnline(false);
      setWasOffline(true);
      setOfflineSince(now);
      startDurationCounter(now.getTime());
      window.dispatchEvent(new CustomEvent('vh_network_offline', { detail: { timestamp: now } }));
    };

    const goOnline = () => {
      console.log('[useNetworkStatus] Browser came back ONLINE');
      setIsOnline(true);
      setOfflineSince(null);
      stopDurationCounter();
      window.dispatchEvent(new CustomEvent('vh_network_online', { detail: { timestamp: new Date() } }));
    };

    window.addEventListener('offline', goOffline);
    window.addEventListener('online', goOnline);

    // If already offline on mount
    if (!navigator.onLine) {
      goOffline();
    }

    return () => {
      window.removeEventListener('offline', goOffline);
      window.removeEventListener('online', goOnline);
      stopDurationCounter();
    };
  }, [startDurationCounter, stopDurationCounter]);

  return { isOnline, wasOffline, offlineSince, offlineDurationSec, refresh };
}

