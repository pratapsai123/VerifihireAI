import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import { logCandidateActivity } from './activityLogger';

export const TERMINATION_REASONS = {
  TERMINAL_CLOSE: 'terminal_close',
  REMOTE_ACCESS: 'remote_access',
  GRACE_EXPIRED: 'grace_expired',
  REMOTE_APP_AFTER_PRECHECK: 'remote_app_after_precheck',
};

export const TERMINATION_REASON_LABELS = {
  [TERMINATION_REASONS.TERMINAL_CLOSE]: 'Secure Agent terminal closed (3 strikes)',
  [TERMINATION_REASONS.REMOTE_ACCESS]: 'Remote access application detected',
  [TERMINATION_REASONS.GRACE_EXPIRED]: 'Remote access app not closed within grace period',
  [TERMINATION_REASONS.REMOTE_APP_AFTER_PRECHECK]: 'Remote app detected after precheck',
};

function buildCodeMapFromProgress(progress) {
  const codeMap = {};
  const codeById = progress?.codeById || {};
  Object.keys(codeById).forEach((key) => {
    codeMap[key] = {
      code: codeById[key] || '',
      language: progress?.languageById?.[key] || 'python3',
    };
  });
  return codeMap;
}

/**
 * Save partial answers and mark invitation as terminated (for results + PDF).
 */
export async function finalizeTerminatedExam(token, { reason, detail }) {
  if (!token) return null;

  const reasonLabel = TERMINATION_REASON_LABELS[reason] || reason || 'Policy violation';
  const terminationDetail = detail || reasonLabel;

  let answers = {};
  let code_map = {};
  try {
    const raw = localStorage.getItem(`take_assessment_progress_${token}`);
    if (raw) {
      const progress = JSON.parse(raw);
      answers = progress.answersById || {};
      code_map = buildCodeMapFromProgress(progress);
    }
  } catch (_err) {
    // continue with empty payload
  }

  try {
    const res = await axios.post(
      `${API_BASE_URL}/invitations/public/${token}/terminate/`,
      {
        answers,
        code_map,
        termination_reason: reason,
        termination_detail: terminationDetail,
      },
      { timeout: 30000 }
    );
    localStorage.removeItem(`take_assessment_progress_${token}`);
    return res.data;
  } catch (err) {
    console.error('finalizeTerminatedExam failed:', err?.message);
    return null;
  }
}

export async function logSessionTerminated(token, reason, detail) {
  const label = TERMINATION_REASON_LABELS[reason] || reason;
  await logCandidateActivity(token, 'Session Terminated', detail || label, {
    category: 'termination',
    termination_reason: reason,
    termination_label: label,
  });
}

export async function logTerminalCloseStrike(token, closeCount, chancesLeft) {
  const detail = chancesLeft > 0
    ? `Secure Agent terminal closed (${closeCount}/3). ${chancesLeft} chance(s) remaining before permanent termination.`
    : `Secure Agent terminal closed (${closeCount}/3). Exam terminated.`;
  await logCandidateActivity(token, 'Terminal Closed', detail, {
    category: 'security',
    termination_reason: 'terminal_close',
  });
}
