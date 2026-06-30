export const TERMINAL_CLOSE_LIMIT = 3;

const getTerminalCloseWarningKey = (token) => `vh_terminal_close_warning_${token}`;

/** Cache warning for UX between precheck ↔ exam in the same tab (server is source of truth). */
export const setTerminalCloseWarning = (token, { closeCount, chancesLeft }) => {
  sessionStorage.setItem(
    getTerminalCloseWarningKey(token),
    JSON.stringify({ closeCount, chancesLeft, at: Date.now() })
  );
};

export const readTerminalCloseWarning = (token) => {
  try {
    const raw = sessionStorage.getItem(getTerminalCloseWarningKey(token));
    return raw ? JSON.parse(raw) : null;
  } catch (_err) {
    return null;
  }
};

export const clearTerminalCloseWarning = (token) => {
  sessionStorage.removeItem(getTerminalCloseWarningKey(token));
};

export const getTerminalCloseWarningMessage = (chancesLeft) => {
  if (chancesLeft === 1) {
    return 'You have 1 chance left. If you close the Secure Agent terminal again, your exam will be terminated.';
  }
  if (chancesLeft === 2) {
    return 'You closed the Secure Agent terminal. You have 2 chances remaining before your exam is permanently terminated. Keep the terminal window open during the exam.';
  }
  return '';
};

/** Build warning state from violation-status API response. */
export const warningFromViolationStatus = (status) => {
  const closeCount = Number(status?.terminal_close_count) || 0;
  const limit = Number(status?.terminal_close_limit) || TERMINAL_CLOSE_LIMIT;
  const chancesLeft =
    status?.chances_left != null
      ? Number(status.chances_left)
      : Math.max(0, limit - closeCount);
  if (closeCount <= 0 || chancesLeft <= 0) {
    return null;
  }
  return { closeCount, chancesLeft };
};
