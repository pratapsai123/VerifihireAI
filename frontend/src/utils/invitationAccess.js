import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import { getTabSessionId } from './tabSession';

/**
 * Lightweight invitation gate (check_only=1). Does not start the exam timer.
 * Passes X-Session-ID so the backend can identify whether the checking tab
 * is the same as the one that currently owns the session lock.
 */
export async function checkInvitationPublicAccess(token) {
  if (!token) {
    return { ok: false, submitted: false, error: 'Missing token' };
  }
  const sessionId = getTabSessionId();
  try {
    await axios.get(`${API_BASE_URL}/invitations/public/${token}/?check_only=1`, {
      timeout: 15000,
      headers: { 'X-Session-ID': sessionId },
    });
    return { ok: true, submitted: false };
  } catch (err) {
    const status = err?.response?.status;
    const errorMsg = String(err?.response?.data?.error || '');
    const schedule = err?.response?.data?.schedule || null;

    if (status === 409) {
      const sessionLocked = errorMsg.toLowerCase().includes('already in use');
      const submitted =
        !sessionLocked &&
        (errorMsg.toLowerCase().includes('completed') ||
          errorMsg.toLowerCase().includes('submitted'));
      return {
        ok: false,
        submitted,
        sessionLocked,
        status,
        error: errorMsg,
        schedule,
      };
    }

    return {
      ok: false,
      submitted: false,
      status,
      error: errorMsg || 'This assessment link is not accessible.',
      schedule,
    };
  }
}

export function isInvitationAlreadySubmitted(access) {
  return Boolean(access?.submitted);
}
