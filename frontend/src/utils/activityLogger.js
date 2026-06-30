import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

export const logCandidateActivity = async (token, action, details = '', extra = {}) => {
  if (!token) return;
  const payload = {
    action,
    details: typeof details === 'object' ? JSON.stringify(details) : details,
    ...extra,
  };

  // Standard assessments: invitation token first (AI endpoint returns 404 but order was wrong before).
  try {
    await axios.post(`${API_BASE_URL}/invitations/public/${token}/log/`, payload);
    return;
  } catch (stdErr) {
    if (stdErr.response?.status !== 404) {
      console.error('Failed to log activity (invitation):', stdErr.message);
      return;
    }
  }

  try {
    await axios.post(`${API_BASE_URL}/ai-candidates/public/${token}/log/`, payload);
  } catch (aiErr) {
    console.error('Failed to log activity (AI candidate):', aiErr.message);
  }
};
