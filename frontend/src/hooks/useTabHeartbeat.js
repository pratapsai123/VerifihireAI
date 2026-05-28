/**
 * useTabHeartbeat
 *
 * Sends a POST to /api/invitations/public/<token>/tab-heartbeat/ every
 * HEARTBEAT_INTERVAL_MS milliseconds while the exam tab is open.
 *
 * This keeps the backend session lock "fresh" so that:
 *   - A second tab opening the same exam URL will get a 409 (blocked).
 *   - If this tab closes, heartbeats stop and the lock expires after 30 s,
 *     allowing the candidate to resume on a different browser / laptop.
 *
 * Returns { isLockedOut } — true if the server responded with 409.
 */
import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import { getTabSessionId } from '../utils/tabSession';


const HEARTBEAT_INTERVAL_MS = 15_000; // 15 seconds — well under the 30 s server timeout

export function useTabHeartbeat(token, { enabled = true } = {}) {
  const [isLockedOut, setIsLockedOut] = useState(false);
  const sessionId = getTabSessionId();
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!token || !enabled) return;

    const sendHeartbeat = async () => {
      try {
        await axios.post(
          `${API_BASE_URL}/invitations/public/${token}/tab-heartbeat/`,
          { session_id: sessionId },
          { timeout: 10_000 }
        );
        // If we previously got locked out and now succeed, unlock
        setIsLockedOut(false);
      } catch (err) {
        if (err?.response?.status === 409) {
          setIsLockedOut(true);
        }
        // Other errors (network) — don't lockout; heartbeat will retry
      }
    };

    // Send immediately, then on interval
    sendHeartbeat();
    intervalRef.current = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL_MS);

    return () => {
      clearInterval(intervalRef.current);
    };
  }, [token, enabled, sessionId]);

  return { isLockedOut, sessionId };
}
