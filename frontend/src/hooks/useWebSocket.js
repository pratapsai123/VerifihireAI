import { useEffect, useRef, useState, useCallback } from "react";
import { WS_BASE_URL } from "../apiConfig";

export const useWebSocket = (sessionId, role, sessionExpired, onMessage) => {
  const socketRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState("Connecting");

  const retryDelayRef = useRef(3000);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const shouldReconnectRef = useRef(true);
  const messageQueueRef = useRef([]);

  // ✅ Keep latest onMessage without re-triggering connect
  const onMessageRef = useRef(onMessage);
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    if (!sessionId || !role || sessionExpired) return;
    if (!shouldReconnectRef.current) return;

    // 🔥 Prevent duplicate connections
    if (
      socketRef.current &&
      (socketRef.current.readyState === WebSocket.OPEN ||
        socketRef.current.readyState === WebSocket.CONNECTING)
    ) {
      console.log("ℹ️ WebSocket already active. Skipping.");
      return;
    }

    // 🔥 Close previous socket (safety)
    if (socketRef.current) {
      socketRef.current.close();
    }

    const wsUrl = `${WS_BASE_URL}/${sessionId}/${role}/`;
    console.log("🔌 Connecting to:", wsUrl);

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("✅ WebSocket connected");
      setConnectionStatus("Connected");
      retryDelayRef.current = 3000;

      if (messageQueueRef.current.length > 0) {
        console.log(`🚀 Flushing ${messageQueueRef.current.length} queued messages`);
        messageQueueRef.current.forEach(msg => socket.send(JSON.stringify(msg)));
        messageQueueRef.current = [];
      }

      // 🔥 Heartbeat (keep connection alive)
      if (heartbeatIntervalRef.current)
        clearInterval(heartbeatIntervalRef.current);

      heartbeatIntervalRef.current = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "ping" }));
        }
      }, 20000);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // 🔥 Stop reconnect only on terminal states
        if (
          data.type === "end_interview" ||
          (data.type === "session_expired" && (data.reason === "completed" || data.reason === "expired"))
        ) {
          console.log("🛑 Final session state reached. Stopping reconnect.");
          shouldReconnectRef.current = false;
        }

        if (onMessageRef.current) {
          onMessageRef.current(data);
        }
      } catch (e) {
        console.error("❌ Message parse error:", e);
      }
    };

    socket.onerror = (err) => {
      console.error("❌ WebSocket error:", err);
    };

    socket.onclose = (event) => {
      console.warn(`⚠️ WebSocket closed: ${event.code} ${event.reason}`);

      // ❌ Do not reconnect for these cases
      if (
        event.code === 1000 || // normal
        event.code === 1008 || // policy
        event.code === 4001 || // session expired
        event.code === 4003 // unauthorized
      ) {
        console.log("🛑 Not reconnecting (expected close)");
        shouldReconnectRef.current = false;
        setConnectionStatus("Disconnected");
        return;
      }

      // 🔁 Reconnect with backoff
      setConnectionStatus("Reconnecting");

      reconnectTimeoutRef.current = setTimeout(() => {
        console.log(`🔄 Reconnecting in ${retryDelayRef.current}ms`);
        retryDelayRef.current = Math.min(
          retryDelayRef.current * 2,
          15000
        );
        connect();
      }, retryDelayRef.current);
    };
  }, [sessionId, role, sessionExpired]);

  // ✅ CLEAN + STABLE EFFECT
  useEffect(() => {
    if (!sessionId || !role) return;

    shouldReconnectRef.current = true;
    connect();

    return () => {
      console.log("🧹 Cleaning WebSocket");

      shouldReconnectRef.current = false;

      if (reconnectTimeoutRef.current)
        clearTimeout(reconnectTimeoutRef.current);

      if (heartbeatIntervalRef.current)
        clearInterval(heartbeatIntervalRef.current);

      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [sessionId, role]); // 🔥 ONLY these deps

  const sendMessage = useCallback((msg) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(msg));
    } else {
      console.warn("⚠️ Cannot send message, socket not open. Queueing message.");
      messageQueueRef.current.push(msg);
    }
  }, []);

  return {
    socketRef,
    connectionStatus,
    sendMessage,
  };
};

export default useWebSocket;