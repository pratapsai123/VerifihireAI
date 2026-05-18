export const TERMINAL_CLOSE_LIMIT = 3;

const getTerminalCloseKey = (token) => `vh_terminal_close_${token}`;
const getTerminalCloseWarningKey = (token) => `vh_terminal_close_warning_${token}`;

export const incrementTerminalCloseCount = (token) => {
  const key = getTerminalCloseKey(token);
  const prev = parseInt(sessionStorage.getItem(key) || '0', 10);
  const next = Math.min(prev + 1, TERMINAL_CLOSE_LIMIT);
  sessionStorage.setItem(key, String(next));
  return next;
};

export const getTerminalCloseCount = (token) => {
  return parseInt(sessionStorage.getItem(getTerminalCloseKey(token)) || '0', 10);
};

export const clearTerminalCloseCount = (token) => {
  sessionStorage.removeItem(getTerminalCloseKey(token));
  sessionStorage.removeItem(getTerminalCloseWarningKey(token));
};

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
