import { useEffect, useRef, useState, useCallback } from 'react';
import { WS_BASE_URL } from '../apiConfig';

export const useWebSocket = (sessionId, role, sessionExpired, onMessage) => {
  const socketRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [connectionStatusText, setConnectionStatusText] = useState('Connecting...');
  const [connectionEstablished, setConnectionEstablished] = useState(false);
  
  const heartbeatIntervalRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 12;

  const buildWsCandidates = useCallback((sessionId, role) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const hostname = window.location.hostname;
    const candidates = [];

    // 1. Primary: Use the centralized WS_BASE_URL
    let base = WS_BASE_URL.endsWith('/') ? WS_BASE_URL.slice(0, -1) : WS_BASE_URL;
    if ((hostname.includes('verifihireai.com') || hostname.includes('duckdns.org')) && base.includes(':3000')) {
      base = base.replace(':3000', '');
    }
    candidates.push(`${base}/interview/${sessionId}/${role}/`);

    // 2. Production Domain (Explicit)
    if (hostname.includes('verifihireai.com') || hostname.includes('duckdns.org')) {
      candidates.push(`wss://${hostname}/ws/interview/${sessionId}/${role}/`);
    }

    // 3. Fallback: Host but NO PORT 3000
    const currentHost = window.location.host;
    if (!currentHost.includes(':3000')) {
      const hostCandidate = `${protocol}//${currentHost}/ws/interview/${sessionId}/${role}/`;
      if (!candidates.includes(hostCandidate)) {
        candidates.push(hostCandidate);
      }
    }

    // 4. Localhost Fallback
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      candidates.push(`ws://${hostname}:8001/ws/interview/${sessionId}/${role}/`);
    }

    return candidates;
  }, []);

  const connectWebSocket = useCallback(() => {
    if (sessionExpired) return;

    const candidates = buildWsCandidates(sessionId, role);
    let attemptIndex = 0;

    const tryNext = () => {
      if (attemptIndex >= candidates.length) {
        console.error('❌ All WebSocket URL candidates failed');
        setConnectionStatus('Error');
        setConnectionStatusText('Connection failed');
        return;
      }

      const url = candidates[attemptIndex++];
      console.log(`🔌 Attempting WS connection to ${url}`);

      try {
        const socket = new WebSocket(url);
        socketRef.current = socket;

        const fallbackTimer = setTimeout(() => {
          if (!socket || (socket.readyState !== WebSocket.OPEN && socket.readyState !== WebSocket.CONNECTING)) {
            console.warn(`WS timeout on ${url}`);
            tryNext();
          }
        }, 3000);

        socket.addEventListener('open', () => {
          clearTimeout(fallbackTimer);
          console.log('✅ WebSocket connected successfully to', url);
          setConnectionEstablished(true);
          setConnectionStatus('Connected');
          setConnectionStatusText('Ready for connection');
          reconnectAttemptsRef.current = 0;

          heartbeatIntervalRef.current = setInterval(() => {
            try {
              if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ type: 'client_ping', ts: Date.now() }));
              }
            } catch (e) { }
          }, 20000);
        });

        socket.addEventListener('message', (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'server_ping' || data.type === 'pong' || data.type === 'server_pong') return;
            if (onMessage) onMessage(data);
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
          }
        });

        socket.addEventListener('close', (e) => {
          console.warn('WebSocket disconnected', e.code);
          setConnectionStatus('Disconnected');
          if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);

          if (!sessionExpired && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
            const delay = Math.pow(2, reconnectAttemptsRef.current) * 1000;
            reconnectAttemptsRef.current++;
            setConnectionStatusText(`Reconnecting in ${delay / 1000}s...`);
            setTimeout(connectWebSocket, delay);
          } else if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
            setConnectionStatus('Error');
            setConnectionStatusText('Connection failed');
          }
        });

        socket.addEventListener('error', (e) => {
          console.warn('WS error on', url, e);
          // tryNext will handle failover on close event
        });
      } catch (e) {
        console.warn('WS construction failed for', url, e);
        tryNext();
      }
    };

    tryNext();
  }, [sessionId, role, sessionExpired, buildWsCandidates, onMessage]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socketRef.current) socketRef.current.close();
      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
    };
  }, [connectWebSocket]);

  const sendMessage = useCallback((msgObj) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(msgObj));
    }
  }, []);

  return {
    socketRef,
    connectionStatus,
    setConnectionStatus,
    connectionStatusText,
    setConnectionStatusText,
    connectionEstablished,
    sendMessage
  };
};

export default useWebSocket;
