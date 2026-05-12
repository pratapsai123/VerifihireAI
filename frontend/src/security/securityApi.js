import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

export const LOCAL_AGENT_BASE_URL = 'http://127.0.0.1:5001';

export const fetchAgentStatus = async () => {
  const res = await axios.get(`${LOCAL_AGENT_BASE_URL}/status`, { timeout: 4000 });
  return res.data;
};

export const runLocalScan = async () => {
  const res = await axios.post(`${LOCAL_AGENT_BASE_URL}/scan`, {}, { timeout: 45000 });
  return res.data;
};

export const runLocalHardwareScan = async () => {
  const res = await axios.post(`${LOCAL_AGENT_BASE_URL}/scan/hardware`, {}, { timeout: 30000 });
  return res.data;
};

export const startBackendSecuritySession = async ({ token, type, user_id, agent_instance_id }) => {
  const res = await axios.post(`${API_BASE_URL}/security-session/start`, { token, type, user_id, agent_instance_id }, { timeout: 8000 });
  return res.data;
};

export const startLocalMonitor = async ({ session_id, user_id, token }) => {
  const res = await axios.post(
    `${LOCAL_AGENT_BASE_URL}/monitor/start`,
    { session_id, user_id, token, backend_api_base: API_BASE_URL },
    { timeout: 15000 }
  );
  return res.data;
};

export const stopLocalMonitor = async ({ session_id, user_id }) => {
  try {
    await axios.post(`${LOCAL_AGENT_BASE_URL}/monitor/stop`, { session_id, user_id }, { timeout: 5000 });
  } catch (_err) {
    // best effort
  }
};

export const fetchSecuritySessionStatus = async (sessionId) => {
  const res = await axios.get(`${API_BASE_URL}/security-session/${sessionId}/status`, { timeout: 8000 });
  return res.data;
};

export const checkViolationStatus = async (token) => {
  const res = await axios.get(`${API_BASE_URL}/security-session/${token}/violation-status`, { timeout: 20000 });
  return res.data;
};
