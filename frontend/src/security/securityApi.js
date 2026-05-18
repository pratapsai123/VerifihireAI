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
  const res = await axios.post(
    `${API_BASE_URL}/security-session/start`,
    { token, type, user_id, agent_instance_id },
    { timeout: 8000 }
  );
  return res.data;
};

export const consumeAgentInstance = async ({ agent_instance_id, session_id, token }) => {
  const res = await axios.post(
    `${API_BASE_URL}/security-session/consume`,
    { agent_instance_id, session_id, token },
    { timeout: 8000 }
  );
  return res.data;
};

export const shutdownSecureAgent = async (delaySeconds = 0) => {
  await axios.post(
    `${LOCAL_AGENT_BASE_URL}/shutdown`,
    { delay: delaySeconds },
    { timeout: 5000 }
  );
};

/** Ask the local agent to run a process scan immediately (e.g. after closing a remote app). */
export const triggerMonitorScan = async () => {
  await axios.post(`${LOCAL_AGENT_BASE_URL}/monitor/scan-now`, {}, { timeout: 8000 });
};

export const startLocalMonitor = async ({ session_id, user_id, token }) => {
  const res = await axios.post(
    `${LOCAL_AGENT_BASE_URL}/monitor/start`,
    { session_id, user_id, token, backend_api_base: API_BASE_URL },
    { timeout: 15000 }
  );
  return res.data;
};

/**
 * End monitoring, mark agent consumed on server, and schedule local .exe removal.
 */
export const stopLocalMonitor = async ({
  session_id,
  user_id,
  token,
  agent_instance_id,
  destruct_delay = 90,
  immediate_shutdown = false,
  consume = true,
}) => {
  try {
    if (consume && (agent_instance_id || token || session_id)) {
      await consumeAgentInstance({ agent_instance_id, session_id, token });
    }
  } catch (_err) {
    // best effort — still stop local agent
  }

  const shouldDestruct = consume && (immediate_shutdown || destruct_delay >= 0);

  try {
    await axios.post(
      `${LOCAL_AGENT_BASE_URL}/monitor/stop`,
      {
        session_id,
        user_id,
        destruct_delay: !shouldDestruct ? -1 : (immediate_shutdown ? 0 : destruct_delay),
      },
      { timeout: 5000 }
    );
  } catch (_err) {
    // monitor may already be stopped
  }

  if (immediate_shutdown && consume) {
    try {
      await shutdownSecureAgent(0);
    } catch (_err) {
      // best effort
    }
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
