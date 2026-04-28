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

module.exports = { getSecuritySignatures, sendSecurityCheck, sendHeartbeat };
