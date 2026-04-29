const axios = require('axios');

async function getSecuritySignatures(apiBase) {
  const url = `${apiBase}/security-signatures`;
  const res = await axios.get(url, { timeout: 4000 });
  return res.data;
}

async function sendSecurityCheck(apiBase, payload) {
  const url = `${apiBase}/security-check`;
  const res = await axios.post(url, payload, { timeout: 4000 });
  return res.data;
}

async function sendHeartbeat(apiBase, payload) {
  const url = `${apiBase}/security-heartbeat`;
  const res = await axios.post(url, payload, { timeout: 4000 });
  return res.data;
}

async function logActivity(apiBase, token, action, details) {
  if (!token) return;
  const url = `${apiBase}/invitations/public/${token}/log/`;
  await axios.post(url, { action, details }, { timeout: 4000 });
}

module.exports = { getSecuritySignatures, sendSecurityCheck, sendHeartbeat, logActivity };
