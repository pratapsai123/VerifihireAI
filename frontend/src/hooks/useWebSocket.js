import { useEffect, useRef, useState, useCallback } from "react";
import { WS_BASE_URL } from "../apiConfig";

export const useWebSocket = (sessionId, role, sessionExpired, onMessage) => {
  const socketRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState("Connecting");
  const retryDelayRef = useRef(3000);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const shouldReconnectRef = useRef(true);

  // 🔥 CACHE: Store onMessage in a ref so connect() doesn't depend on it
  const onMessageRef = useRef(onMessage);
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    if (!sessionId || !role || sessionExpired || !shouldReconnectRef.current) return;

    // 🔥 GUARD: Prevent redundant connections
    if (socketRef.current) {
      if (socketRef.current.readyState === WebSocket.OPEN || socketRef.current.readyState === WebSocket.CONNECTING) {
        console.log("ℹ️ WebSocket already connected or connecting. Skipping.");
        return;
      }
    }

    const wsUrl = `${WS_BASE_URL}/${sessionId}/${role}/`;
    console.log("🔌 Connecting to:", wsUrl);

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("✅ WebSocket connected");
      setConnectionStatus("Connected");
      retryDelayRef.current = 3000;

      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "ping" }));
        }
      }, 20000);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // 🔥 TERMINATION GUARD: Stop reconnect if interview ends
        if (data.type === "end_interview" || data.type === "session_expired") {
          console.log("🛑 Termination message received. Stopping reconnect.");
          shouldReconnectRef.current = false;
        }

        if (onMessageRef.current) onMessageRef.current(data);
      } catch (e) {
        console.error("Parse error:", e);
      }
    };

    socket.onerror = (err) => {
      console.error("❌ WebSocket error:", err);
    };

    socket.onclose = (event) => {
      console.warn(`⚠️ WebSocket closed: ${event.code} ${event.reason}`);

      // ❌ DO NOT reconnect for these cases
      if (
        event.code === 1000 ||   // normal close
        event.code === 1008 ||   // policy violation (auth fail)
        event.code === 4001 ||   // custom close (session expired)
        event.code === 4003      // unauthorized / invalid
      ) {
        console.log("🛑 Not reconnecting due to server rejection");
        shouldReconnectRef.current = false;
        setConnectionStatus("Disconnected");
        return;
      }

      setConnectionStatus("Reconnecting");

      reconnectTimeoutRef.current = setTimeout(() => {
        console.log(`🔄 Attempting reconnect in ${retryDelayRef.current}ms`);
        retryDelayRef.current = Math.min(retryDelayRef.current * 2, 15000);
        connect();
      }, retryDelayRef.current);
    };
  }, [sessionId, role, sessionExpired]); // onMessage removed from deps

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.close(1000, "Normal closure");
      }
    };
  }, [connect]);

  const sendMessage = useCallback((msg) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(msg));
    }
  }, []);

  return {
    socketRef,
    connectionStatus,
    sendMessage
  };
};

export default useWebSocket;
