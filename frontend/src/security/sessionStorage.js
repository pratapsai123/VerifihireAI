export const SECURITY_STORAGE_PREFIX = 'vh_security_session_';
export const PRECHECK_STORAGE_PREFIX = 'vh_precheck_';

export const getSecuritySessionKey = (token) => `${SECURITY_STORAGE_PREFIX}${token}`;
export const getPrecheckKey = (token) => `${PRECHECK_STORAGE_PREFIX}${token}`;

export const readSessionRecord = (token) => {
  try {
    const raw = sessionStorage.getItem(getSecuritySessionKey(token));
    return raw ? JSON.parse(raw) : null;
  } catch (_err) {
    return null;
  }
};

export const writeSessionRecord = (token, value) => {
  sessionStorage.setItem(getSecuritySessionKey(token), JSON.stringify(value));
};

export const markPrecheckPassed = (token, type) => {
  sessionStorage.setItem(
    getPrecheckKey(token),
    JSON.stringify({ 
      passed: true, 
      type, 
      at: new Date().toISOString(),
      timestamp: Date.now() 
    })
  );
};

export const readPrecheckRecord = (token) => {
  try {
    const raw = sessionStorage.getItem(getPrecheckKey(token));
    return raw ? JSON.parse(raw) : null;
  } catch (_err) {
    return null;
  }
};

export const clearPrecheckRecord = (token) => {
  sessionStorage.removeItem(getPrecheckKey(token));
  sessionStorage.removeItem(getSecuritySessionKey(token));
  sessionStorage.removeItem(`vh_exam_active_${token}`);
};

export const markExamStarted = (token) => {
  sessionStorage.setItem(`vh_exam_active_${token}`, 'true');
};

export const isExamStarted = (token) => {
  return sessionStorage.getItem(`vh_exam_active_${token}`) === 'true';
};
