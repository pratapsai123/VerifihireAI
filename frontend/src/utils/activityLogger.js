import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

export const logCandidateActivity = async (token, action, details = '') => {
  if (!token) return;
  const payload = {
    action,
    details: typeof details === 'object' ? JSON.stringify(details) : details
  };

  try {
    // 1. Try AI Interview Candidate endpoint (primary for AI Interviews)
    await axios.post(`${API_BASE_URL}/ai-candidates/public/${token}/log/`, payload);
  } catch (aiErr) {
    // 2. If 404, fallback to standard Assessment Invitation endpoint
    if (aiErr.response?.status === 404) {
      try {
        await axios.post(`${API_BASE_URL}/invitations/public/${token}/log/`, payload);
      } catch (stdErr) {
        console.error('Failed to log activity (Standard Invitation fallback failed):', stdErr.message);
      }
    } else {
      console.error('Failed to log activity (AI Candidate endpoint error):', aiErr.message);
    }
  }
};
