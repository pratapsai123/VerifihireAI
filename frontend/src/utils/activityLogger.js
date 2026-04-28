import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

export const logCandidateActivity = async (token, action, details = '') => {
  if (!token) return;
  try {
    await axios.post(`${API_BASE_URL}/invitations/public/${token}/log/`, {
      action,
      details: typeof details === 'object' ? JSON.stringify(details) : details
    });
  } catch (error) {
    console.error('Failed to log activity:', error);
  }
};
