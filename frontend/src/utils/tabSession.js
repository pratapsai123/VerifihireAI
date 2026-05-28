/**
 * Tab Session Utility
 *
 * Provides a unique, per-browser-tab session ID that persists across page
 * refreshes (via sessionStorage) but is cleared when the tab is closed.
 *
 * This ID is used to enforce the "1 active tab at a time" rule while still
 * allowing candidates to close and reopen the exam in a new tab once the
 * old tab's heartbeat has expired (30 s timeout on the backend).
 */

const SESSION_STORAGE_KEY = 'vh_exam_tab_session_id';

/**
 * Returns the stable session ID for this tab.
 * A new UUID is generated on first call and cached in sessionStorage.
 */
export function getTabSessionId() {
  try {
    let sid = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!sid) {
      sid = generateUUID();
      sessionStorage.setItem(SESSION_STORAGE_KEY, sid);
    }
    return sid;
  } catch {
    // sessionStorage unavailable (private mode edge case) — use a runtime variable
    if (!getTabSessionId._fallback) {
      getTabSessionId._fallback = generateUUID();
    }
    return getTabSessionId._fallback;
  }
}

function generateUUID() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for older browsers
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
