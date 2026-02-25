import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/LiveInterviewInterviewer.css';
import VideoPlaceholder from '../components/VideoPlaceholder';
import { API_BASE_URL, WS_BASE_URL } from '../apiConfig';

function LiveInterviewInterviewer() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('token') || 'default-session';

  // State management
  const [candidateName, setCandidateName] = useState('Candidate');
  const [interviewerName, setInterviewerName] = useState('Interviewer');
  const [sessionExpired, setSessionExpired] = useState(false);
  const [bothPartiesConnected, setBothPartiesConnected] = useState(false);
  const [connectionEstablished, setConnectionEstablished] = useState(false);

  // Media states
  const [isMuted, setIsMuted] = useState(false);
  const [isCameraOn, setIsCameraOn] = useState(true);
  const [isRemoteCameraOn, setIsRemoteCameraOn] = useState(true);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [screenShareLocked, setScreenShareLocked] = useState(false);
  const [screenShareHolder, setScreenShareHolder] = useState(null);

  // UI states
  const [chatPanelVisible, setChatPanelVisible] = useState(false);
  const [chatUnreadCount, setChatUnreadCount] = useState(0);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');

  // Connection states
  const [connectionStatus, setConnectionStatus] = useState('Connecting...');
  const [connectionStatusClass, setConnectionStatusClass] = useState('');
  const [timer, setTimer] = useState('00:00:00');
  const [showEndInterviewModal, setShowEndInterviewModal] = useState(false);
  const [showConnectionFailedModal, setShowConnectionFailedModal] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmMessage, setConfirmMessage] = useState('');
  const [confirmCallback, setConfirmCallback] = useState(null);

  // Draggable interaction state
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  // Interview report states
  const [showInterviewReport, setShowInterviewReport] = useState(false);
  const [showFeedbackSuccess, setShowFeedbackSuccess] = useState(false);
  const [ratings, setRatings] = useState({
    solutionApproach: 0,
    codingLanguage: 0,
    codeCompleteness: 0,
    useCaseCoverage: 0,
    overallRating: 5,
    hireRecommendation: 'Qualified'
  });
  const [skills, setSkills] = useState([
    { name: 'Problem Solving', score: 0 },
    { name: 'Data Structures', score: 0 },
    { name: 'Algorithms', score: 0 },
    { name: 'Communication', score: 0 }
  ]);
  const [editingSkills, setEditingSkills] = useState(false);

  // Proxy violation notifications
  const [proxyViolations, setProxyViolations] = useState([]);

  // Refs
  const socketRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const localStreamRef = useRef(null);
  const remoteStreamRef = useRef(null);
  const screenShareStreamRef = useRef(null);
  const remoteIceQueueRef = useRef([]);
  const pendingOfferRef = useRef(null);
  const remoteVideoRef = useRef(null);

  const selfVideoRef = useRef(null);
  const selfVideoContainerRef = useRef(null);
  const chatMessagesRef = useRef(null);
  const chatInputRef = useRef(null);
  const startTimeRef = useRef(Date.now());
  const timerIntervalRef = useRef(null);
  const pendingScreenShareGrantResolverRef = useRef(null);
  const videoConnectedNotifiedRef = useRef(false);
  const chatDedupRef = useRef(new Map());
  const reconnectAttemptsRef = useRef(0);
  const wasEverConnectedRef = useRef(false);
  const interviewEndedRef = useRef(false);
  const candidateHasJoinedRef = useRef(false);
  const heartbeatIntervalRef = useRef(null);

  const sessionKey = `session_expired_${sessionId}`;
  const MY_ROLE = 'Interviewer';
  const MAX_RECONNECT_ATTEMPTS = 12;

  // Load interview details from API
  useEffect(() => {
    const loadInterviewDetails = async () => {
      try {
        // Try to fetch interview invitation details by token
        const resp = await axios.get(`${API_BASE_URL}/interviews/invitations/${sessionId}/`);
        if (resp.data) {
          setCandidateName(resp.data.name || 'Candidate');
          // You can also set interviewer name from user profile if available
        }
      } catch (error) {
        console.warn('Could not load interview details:', error);
        // Fallback: try to get from list
        try {
          const listResp = await axios.get(`${API_BASE_URL}/interviews/invitations/`);
          const invitation = listResp.data?.results?.find(inv => inv.token === sessionId);
          if (invitation) {
            setCandidateName(invitation.name || 'Candidate');
          }
        } catch (e) {
          console.warn('Could not load from list either:', e);
        }
      }
    };

    loadInterviewDetails();
  }, [sessionId]);

  // Check if session is expired
  useEffect(() => {
    if (localStorage.getItem(sessionKey) === 'true') {
      setSessionExpired(true);
      showSessionExpiredMessage();
    }
  }, [sessionKey]);

  // Timer effect
  useEffect(() => {
    timerIntervalRef.current = setInterval(() => {
      if (interviewEndedRef.current) return;
      const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
      const h = String(Math.floor(elapsed / 3600)).padStart(2, '0');
      const m = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
      const s = String(elapsed % 60).padStart(2, '0');
      setTimer(`${h}:${m}:${s}`);
    }, 1000);

    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, []);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, chatPanelVisible]);

  // Utility functions
  const showNotification = useCallback((message, type = 'info') => {
    // Create notification element
    const notification = document.createElement('div');
    const colors = {
      info: { bg: '#3b82f6', color: 'white' },
      success: { bg: '#10b981', color: 'white' },
      error: { bg: '#ef4444', color: 'white' },
      warning: { bg: '#f59e0b', color: 'white' }
    };
    const style = colors[type] || colors.info;

    notification.style.cssText = `
      background-color: ${style.bg};
      color: ${style.color};
      font-size: 0.875rem;
      font-weight: 600;
      padding: 0.5rem 1rem;
      border-radius: 0.375rem;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      transition: all 0.3s;
      transform: translateX(100%);
      margin-bottom: 0.75rem;
      position: fixed;
      top: 5rem;
      right: 1.5rem;
      z-index: 50;
      max-width: 350px;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => notification.style.transform = 'translateX(0)', 10);
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }, []);

  const showSessionExpiredMessage = () => {
    const popup = document.createElement('div');
    popup.style.cssText = 'position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 50;';
    popup.innerHTML = `
      <div style="background: white; padding: 1.5rem; border-radius: 0.5rem; max-width: 28rem; margin: 0 1rem; text-align: center;">
        <div style="margin-bottom: 1rem;">
          <i class="fas fa-clock" style="font-size: 3rem; color: #9ca3af;"></i>
        </div>
        <h3 style="font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; color: #1f2937;">Session Completed</h3>
        <p style="color: #6b7280; margin-bottom: 1.5rem;">This interview session has already been completed. You cannot rejoin the interview.</p>
        <button id="close-session-button" style="width: 100%; background: #6b7280; color: white; padding: 0.5rem 1rem; border-radius: 0.375rem; border: none; cursor: pointer;">
          Close
        </button>
      </div>
    `;
    document.body.appendChild(popup);

    // Attach event listener after the element is in the DOM
    const closeButton = document.getElementById('close-session-button');
    if (closeButton) {
      closeButton.onclick = () => {
        // Assuming 'navigate' is available in the component's scope
        // and this function is called within that component.
        // If not, 'navigate' would need to be passed as an argument.
        // For now, we'll use window.location for simplicity as navigate is not in scope here.
        window.location.href = '/live-interview-list';
        window.location.reload();
      };
    }
  };

  const showConfirmation = useCallback((message) => {
    return new Promise((resolve) => {
      setConfirmMessage(message);
      setConfirmCallback(() => resolve);
      setShowConfirmModal(true);
    });
  }, []);

  const handleConfirmYes = () => {
    setShowConfirmModal(false);
    if (confirmCallback) {
      confirmCallback(true);
      setConfirmCallback(null);
    }
  };

  const handleConfirmNo = () => {
    setShowConfirmModal(false);
    if (confirmCallback) {
      confirmCallback(false);
      setConfirmCallback(null);
    }
  };

  // Draggable Video Logic (Moved to top level)
  const handleDragStart = useCallback((e) => {
    if (!selfVideoContainerRef.current) return;
    const rect = selfVideoContainerRef.current.getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
    setIsDragging(true);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging || !selfVideoContainerRef.current) return;
      e.preventDefault();

      const x = e.clientX - dragOffset.x;
      const y = e.clientY - dragOffset.y;

      selfVideoContainerRef.current.style.left = `${x}px`;
      selfVideoContainerRef.current.style.top = `${y}px`;
      selfVideoContainerRef.current.style.bottom = 'auto';
      selfVideoContainerRef.current.style.right = 'auto';
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  // WebSocket connection
  const buildWsCandidates = useCallback((sessionId) => {
    // Get backend URL from API_BASE_URL
    const apiUrl = API_BASE_URL.replace('/api', '').replace('http://', '').replace('https://', '').split(':')[0];
    // Simplified WebSocket URL candidates using centralized WS_BASE_URL
    const candidates = [];
    candidates.push(`${WS_BASE_URL}/interview/${sessionId}/interviewer/`);

    // Fallback for local
    if (!candidates.includes(`ws://localhost:8001/ws/interview/${sessionId}/interviewer/`)) {
      candidates.push(`ws://localhost:8001/ws/interview/${sessionId}/interviewer/`);
    }

    return candidates;
  }, []);

  const connectWebSocket = useCallback(() => {
    if (interviewEndedRef.current || sessionExpired || localStorage.getItem(sessionKey) === 'true') {
      console.log('Session is expired, seemingly blocked connection attempt.');
      return;
    }

    const candidates = buildWsCandidates(sessionId);
    console.log('🔎 WebSocket URL candidates:', candidates);
    let attemptIndex = 0;

    const tryNext = () => {
      if (attemptIndex >= candidates.length) {
        console.error('❌ All WebSocket URL candidates failed');
        showNotification('Unable to connect to server (WS). Please check network or try again.', 'error');
        setShowConnectionFailedModal(true);
        return;
      }

      const url = candidates[attemptIndex++];
      console.log(`🔌 Attempting to connect to WebSocket at ${url}`);

      try {
        const socket = new WebSocket(url);
        socketRef.current = socket;
        window.interviewerSocket = socket;

        setupSocketListeners(socket);

        // If it closes immediately or errors, we proceed to next candidate via onclose/onerror
        socket.addEventListener('error', (e) => {
          console.warn(`WS Error on ${url}:`, e);
        });

        // Fallback timeout in case no events fire
        const fallbackTimer = setTimeout(() => {
          if (!socket || socket.readyState !== WebSocket.OPEN && socket.readyState !== WebSocket.CONNECTING) {
            console.warn(`WS detection timeout on ${url}, trying next...`);
            tryNext();
          }
        }, 3000);

        socket.addEventListener('open', () => clearTimeout(fallbackTimer));
        socket.addEventListener('error', (e) => {
          console.warn('WS error on', url, e);
        });
        socket.addEventListener('close', (e) => {
          if (e && e.code === 404) {
            console.warn('WS close 404 on', url);
            tryNext();
          }
        });
      } catch (error) {
        console.error('❌ Failed to create WebSocket:', error);
        tryNext();
      }
    };

    tryNext();
  }, [sessionId, sessionExpired, buildWsCandidates, showNotification]);

  const setupSocketListeners = useCallback((socket) => {
    socket.onopen = () => {
      wasEverConnectedRef.current = true;
      console.log('✅ WebSocket connected!');

      if (sessionExpired) {
        showSessionExpiredMessage();
        return;
      }

      document.title = 'FDI Live Interview';
      reconnectAttemptsRef.current = 0;
      setConnectionStatus('Connected');
      setConnectionStatusClass('connected');
      showNotification('Connection established!', 'success');
      setConnectionEstablished(true);
      initializeWebRTC();

      // Heartbeat
      heartbeatIntervalRef.current = setInterval(() => {
        try {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'client_ping', ts: Date.now() }));
          }
        } catch { }
      }, 20000);
    };

    socket.onclose = () => {
      if (interviewEndedRef.current) return;
      console.warn('🔌 WebSocket disconnected.');
      setConnectionStatus('Disconnected');
      setConnectionStatusClass('disconnected');

      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }

      if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = Math.pow(2, reconnectAttemptsRef.current) * 1000;
        reconnectAttemptsRef.current++;
        const message = wasEverConnectedRef.current
          ? `Connection lost. Retrying in ${delay / 1000}s...`
          : `Could not connect to server. Retrying in ${delay / 1000}s...`;
        showNotification(message, 'error');
        console.log(`Attempting to reconnect in ${delay / 1000} seconds (attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`);
        setTimeout(connectWebSocket, delay);
      } else {
        console.error('Max reconnection attempts reached.');
        document.title = 'Connection Failed | FDI Interview';
        setShowConnectionFailedModal(true);
      }
    };

    socket.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setConnectionStatus('Disconnected');
      setConnectionStatusClass('disconnected');
    };

    socket.onmessage = (event) => handleSocketMessage(event.data);
  }, [sessionExpired, showNotification, connectWebSocket]);

  const handleSocketMessage = useCallback(async (rawMessage) => {
    try {
      const data = JSON.parse(rawMessage);
      console.log(`📩 Received message type: ${data.type}`, data);

      switch (data.type) {
        case 'connection_error':
          console.error('❌ Server reported connection error:', data.error);
          showNotification(`Connection error: ${data.error}`, 'error');
          break;
        case 'server_pong':
          // Heartbeat response - ignore
          break;
        case 'user_joined':
          const joinedUserName = data.user === 'Candidate' ? candidateName : data.user;
          showNotification(`${joinedUserName} joined the session.`);
          if (data.user === 'Candidate' && peerConnectionRef.current) {
            console.log('🎯 Candidate joined, creating video offer...');
            candidateHasJoinedRef.current = true;
            // Initiate offer because Candidate joined AFTER us
            createVideoOffer();
            setBothPartiesConnected(true);
            // Session remains active until explicitly ended
            // localStorage.setItem(sessionKey, 'true');
            console.log('🔒 Session marked as expired in storage - both parties have connected');
          }
          break;
        case 'chat':
          const normalizeSender = (s) => {
            if (s == null) return s;
            const lower = String(s).toLowerCase();
            if (lower === 'interviewer') return interviewerName;
            if (lower === 'candidate') return candidateName;
            return s;
          };
          const senderNormalized = normalizeSender(data.sender);
          const isSelf = (
            String(data.sender).toLowerCase() === 'interviewer' ||
            String(senderNormalized).toLowerCase() === String(interviewerName).toLowerCase()
          );
          if (isSelf) break;

          // Deduplication
          if (!chatDedupRef.current) chatDedupRef.current = new Map();
          const now = Date.now();
          const key = `${senderNormalized}|${data.message}`;
          const last = chatDedupRef.current.get(key);
          if (last && (now - last) < 2000) break;
          chatDedupRef.current.set(key, now);
          if (chatDedupRef.current.size > 100) {
            const firstKey = chatDedupRef.current.keys().next().value;
            chatDedupRef.current.delete(firstKey);
          }

          appendChatMessage(data.message, senderNormalized);
          if (!chatPanelVisible) {
            setChatUnreadCount(prev => prev + 1);
          }
          break;
        case 'video_offer':
          if (peerConnectionRef.current) {
            await handleVideoOffer(data.offer);
          } else {
            console.log('⏳ PC not ready, queuing video offer');
            pendingOfferRef.current = data.offer;
          }
          break;
        case 'video_answer':
          if (peerConnectionRef.current) await handleVideoAnswer(data.answer);
          break;
        case 'media_state':
          if (String(data.sender).toLowerCase() !== 'candidate') break;
          const who = candidateName;
          const what = data.media === 'mic' ? (data.enabled ? 'unmuted mic' : 'muted mic') : (data.enabled ? 'turned on camera' : 'turned off camera');

          if (data.media === 'camera') {
            setIsRemoteCameraOn(data.enabled);
          }

          const variant = (data.media === 'camera' && !data.enabled) ? 'error' : 'info';
          showNotification(`${who} ${what}`, variant);
          break;
        case 'ice_candidate':
          if (peerConnectionRef.current && data.candidate) {
            try {
              if (!peerConnectionRef.current.remoteDescription) {
                remoteIceQueueRef.current.push(data.candidate);
                console.log('📦 Queued remote ICE candidate');
              } else {
                await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(data.candidate));
                console.log('✅ Added remote ICE candidate');
              }
            } catch (e) {
              console.error('❌ Error adding remote ICE candidate:', e);
            }
          }
          break;
        case 'user_left':
          if (data.user === 'Candidate') {
            console.log('👋 Candidate left the session');
            candidateHasJoinedRef.current = false;
            showNotification('Candidate left the session', 'warning');
          }
          break;
        case 'proxy_violation':
          if (String(data.sender).toLowerCase() === 'candidate') {
            showProxyViolationNotification(data.violation_type, data.violation_count, data.violation_limit);
            console.log(`🚨 Proxy violation detected: ${data.violation_type} (${data.violation_count}/${data.violation_limit})`);
          }
          break;
        case 'interview_terminated_violations':
          console.log('🚨 Interview terminated due to proxy violations');
          const reason = data.reason || 'Multiple people detected';
          showNotification(`Interview terminated: ${reason}`, 'error');
          setTimeout(() => {
            const params = new URLSearchParams({
              session_id: sessionId || '',
              candidate_name: candidateName,
              violation_count: String(data.violation_count || ''),
              violation_limit: String(data.violation_limit || ''),
              start_time: new Date().toISOString()
            });
            navigate(`/interview-terminated/?${params.toString()}`);
          }, 1200);
          break;
        case 'end_interview':
          handleEndInterview(false);
          break;
        case 'session_expired':
          console.log('Session expired - both parties have connected before');
          setSessionExpired(true);
          try { localStorage.setItem(sessionKey, 'true'); } catch (e) { }
          showSessionExpiredMessage();
          break;
        case 'screen_share_state':
          try {
            const isShare = !!data.active;
            const targetFit = isShare ? 'contain' : 'cover';
            if (remoteVideoRef.current) {
              remoteVideoRef.current.style.objectFit = targetFit;
              remoteVideoRef.current.style.objectPosition = 'center center';
            }

          } catch (e) { }
          break;
        case 'screen_share_lock':
          setScreenShareLocked(!!data.active);
          setScreenShareHolder(data.active ? (data.holder || null) : null);
          console.log(`🔒 Screen share lock: ${screenShareLocked}, holder: ${screenShareHolder}`);
          break;
        case 'screen_share_granted':
          if (pendingScreenShareGrantResolverRef.current) {
            const r = pendingScreenShareGrantResolverRef.current;
            pendingScreenShareGrantResolverRef.current = null;
            r(true);
          }
          break;
        case 'screen_share_denied':
          if (pendingScreenShareGrantResolverRef.current) {
            const r = pendingScreenShareGrantResolverRef.current;
            pendingScreenShareGrantResolverRef.current = null;
            r(false);
          }
          if (screenShareLocked && screenShareHolder) {
            showNotification(`${screenShareHolder} is already sharing. Please wait.`, 'warning');
          }
          break;
        default:
          console.warn('Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('Error processing message:', error);
    }
  }, [candidateName, interviewerName, chatPanelVisible, sessionId, sessionKey, navigate, showNotification]);

  // WebRTC functions
  const initializeWebRTC = useCallback(async () => {
    try {
      console.log('🎬 Starting WebRTC initialization (Interviewer)...');

      const localStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280, max: 1920 },
          height: { ideal: 720, max: 1080 },
          frameRate: { ideal: 30, max: 60 },
          facingMode: 'user'
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        }
      });

      console.log('✅ Got local media stream');
      localStreamRef.current = localStream;

      if (selfVideoRef.current) {
        selfVideoRef.current.srcObject = localStream;
        selfVideoRef.current.muted = true;
      }

      const configuration = {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' },
          { urls: 'stun:stun2.l.google.com:19302' },
          { urls: 'stun:stun.stunprotocol.org:3478' },
          { urls: 'stun:stun.voiparound.com' },
          { urls: 'stun:stun.voipbuster.com' },
          {
            urls: 'turn:openrelay.metered.ca:80',
            username: 'openrelayproject',
            credential: 'openrelayproject'
          },
          {
            urls: 'turn:openrelay.metered.ca:443',
            username: 'openrelayproject',
            credential: 'openrelayproject'
          }
        ],
        iceCandidatePoolSize: 10,
        iceTransportPolicy: 'all',
        bundlePolicy: 'max-bundle',
        rtcpMuxPolicy: 'require',
        sdpSemantics: 'unified-plan'
      };

      const peerConnection = new RTCPeerConnection(configuration);
      peerConnectionRef.current = peerConnection;
      console.log('✅ Created peer connection');

      peerConnection.onconnectionstatechange = () => {
        console.log('🔗 Connection state:', peerConnection.connectionState);
        if (peerConnection.connectionState === 'connected') {
          console.log('✅ WebRTC connection established');
          showNotification('Video connection established!', 'success');
          setConnectionStatus('Connected');
          setConnectionStatusClass('connected');
        } else if (peerConnection.connectionState === 'failed') {
          console.error('❌ WebRTC connection failed');
          showNotification('Video connection failed. Please check your network.', 'error');
          setConnectionStatus('Connection failed');
          setConnectionStatusClass('disconnected');
        }
      };

      peerConnection.oniceconnectionstatechange = () => {
        console.log('🧊 ICE connection state:', peerConnection.iceConnectionState);
        if (peerConnection.iceConnectionState === 'connected') {
          setConnectionStatus('Connected');
          setConnectionStatusClass('connected');
        } else if (peerConnection.iceConnectionState === 'failed') {
          setConnectionStatus('Connection failed - retrying...');
          setTimeout(() => {
            if (peerConnection.iceConnectionState === 'failed') {
              createVideoOffer({ iceRestart: true });
            }
          }, 1000);
        }
      };

      localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
        console.log('✅ Added', track.kind, 'track');
      });

      peerConnection.ontrack = (event) => {
        console.log('🎥 INTERVIEWER: Received remote track!', event.track.kind);
        const remoteStream = event.streams[0];

        if (remoteStream) {
          console.log('📺 Setting remote video stream...');
          if (remoteVideoRef.current) {
            remoteVideoRef.current.srcObject = remoteStream;
            remoteVideoRef.current.style.display = 'block';
            remoteVideoRef.current.muted = false;

            remoteVideoRef.current.play().then(() => {
              console.log('✅ Remote video playing');
              setConnectionStatus('Connected');
              setConnectionStatusClass('connected');
              if (!videoConnectedNotifiedRef.current) {
                showNotification('Video connection established!', 'success');
                videoConnectedNotifiedRef.current = true;
              }
            }).catch(e => {
              // Retry play after a short delay
              setTimeout(() => {
                if (remoteVideoRef.current) remoteVideoRef.current.play().catch(err => console.error('Retry failed:', err));
              }, 1000);
            });
          }
        }
      };

      peerConnection.onicecandidate = (event) => {
        if (event.candidate && socketRef.current?.readyState === WebSocket.OPEN) {
          console.log('📤 Sending ICE candidate');
          socketRef.current.send(JSON.stringify({
            type: 'ice_candidate',
            candidate: event.candidate
          }));
        } else if (!event.candidate) {
          console.log('🧊 ICE gathering complete');
        }
      };

      console.log('✅ WebRTC initialized successfully');

      // Process pending offer if exists
      if (pendingOfferRef.current) {
        console.log('🔄 Processing queued video offer...');
        await handleVideoOffer(pendingOfferRef.current);
        pendingOfferRef.current = null;
      }

      // Remove auto-trigger to avoid glare if Candidate is also offering
      // setTimeout(() => {
      //   if (peerConnection && peerConnection.connectionState !== 'connected') {
      //     console.log('🔄 Auto-triggering video connection...');
      //     createVideoOffer();
      //   }
      // }, 3000);

    } catch (error) {
      console.error('❌ Error initializing WebRTC:', error);
      let errorMessage = 'Could not access camera/mic. ';
      if (error.name === 'NotAllowedError') {
        errorMessage += 'Please allow camera and microphone permissions and refresh the page.';
      } else if (error.name === 'NotFoundError') {
        errorMessage += 'No camera or microphone found. Please connect your devices.';
      } else if (error.name === 'NotReadableError') {
        errorMessage += 'Camera/microphone is in use by another application.';
      } else {
        errorMessage += 'Please check your device connections and browser permissions.';
      }
      showNotification(errorMessage, 'error');
    }
  }, [showNotification]);

  const createVideoOffer = useCallback(async (options = {}) => {
    if (!peerConnectionRef.current || !socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.error('❌ Cannot create offer: peer connection or socket not ready');
      return;
    }

    try {
      console.log('🎬 INTERVIEWER: Creating video offer...');

      const offerOptions = {
        offerToReceiveAudio: true,
        offerToReceiveVideo: true
      };

      if (options.iceRestart) {
        offerOptions.iceRestart = true;
      }

      const offer = await peerConnectionRef.current.createOffer(offerOptions);
      await peerConnectionRef.current.setLocalDescription(offer);
      console.log('✅ Set local description');

      socketRef.current.send(JSON.stringify({
        type: 'video_offer',
        offer: offer
      }));
      console.log('✅ Video offer sent to candidate');
    } catch (error) {
      console.error('❌ Error creating video offer:', error);
      showNotification('Failed to create video offer', 'error');
    }
  }, [showNotification]);

  const handleVideoOffer = useCallback(async (offer) => {
    console.log('📼 Handling incoming VIDEO OFFER');
    if (!peerConnectionRef.current) {
      console.error('❌ PeerConnection not initialized when offer received');
      return;
    }

    try {
      await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(offer));
      const answer = await peerConnectionRef.current.createAnswer();
      await peerConnectionRef.current.setLocalDescription(answer);
      socketRef.current?.send(JSON.stringify({
        type: 'video_answer',
        answer: answer
      }));

      // Process queued ICE candidates
      if (remoteIceQueueRef.current.length > 0) {
        for (const candidate of remoteIceQueueRef.current) {
          try {
            await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
          } catch (e) {
            console.warn('Failed to add ICE candidate:', e);
          }
        }
        remoteIceQueueRef.current = [];
      }
    } catch (error) {
      console.error('❌ Error handling video offer:', error);
    }
  }, []);

  const handleVideoAnswer = useCallback(async (answer) => {
    if (!peerConnectionRef.current) {
      console.error('❌ No peer connection for video answer');
      return;
    }

    try {
      console.log('📥 INTERVIEWER: Received video answer');
      await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(answer));
      console.log('✅ Remote description set successfully');

      if (remoteIceQueueRef.current.length > 0) {
        console.log('📤 Processing', remoteIceQueueRef.current.length, 'queued ICE candidates');
        for (const candidate of remoteIceQueueRef.current) {
          try {
            await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
            console.log('✅ Added queued ICE candidate');
          } catch (e) {
            console.warn('⚠️ Failed to add ICE candidate:', e);
          }
        }
        remoteIceQueueRef.current = [];
      }
    } catch (error) {
      console.error('❌ Error handling video answer:', error);
    }
  }, []);

  // Chat functions
  const appendChatMessage = useCallback((msg, sender = 'You') => {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });

    const isMyMessage = sender === interviewerName;

    setChatMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      message: msg,
      sender: sender,
      time: timeString,
      isMyMessage: isMyMessage
    }]);

    // Scroll to bottom
    setTimeout(() => {
      if (chatMessagesRef.current) {
        chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
      }
    }, 100);
  }, [interviewerName]);

  const sendChatMessage = useCallback(() => {
    const msg = chatInput.trim();
    if (!msg) return;

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'chat',
        sender: interviewerName,
        message: msg
      }));
    }

    appendChatMessage(msg, interviewerName);
    setChatInput('');
  }, [chatInput, interviewerName, appendChatMessage]);

  // Media control functions
  const handleMuteToggle = useCallback(() => {
    if (!localStreamRef.current) return;
    const newMuted = !isMuted;
    setIsMuted(newMuted);
    localStreamRef.current.getAudioTracks().forEach(track => track.enabled = !newMuted);
    showNotification(newMuted ? 'Microphone muted' : 'Microphone unmuted');

    try {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({
          type: 'media_state',
          media: 'mic',
          enabled: !newMuted
        }));
      }
    } catch (e) {
      console.warn('media_state mic send failed', e);
    }
  }, [isMuted, showNotification]);

  const handleCameraToggle = useCallback(async () => {
    if (!localStreamRef.current) return;
    const newCameraOn = !isCameraOn;
    setIsCameraOn(newCameraOn);

    if (!newCameraOn) {
      localStreamRef.current.getVideoTracks().forEach(track => track.enabled = false);
      try {
        if (peerConnectionRef.current) {
          const sender = peerConnectionRef.current.getSenders().find(s => s.track && s.track.kind === 'video');
          if (sender) await sender.replaceTrack(null);
        }
      } catch (e) {
        console.warn('replaceTrack(null) failed', e);
      }
    } else {
      localStreamRef.current.getVideoTracks().forEach(track => track.enabled = true);
      try {
        if (peerConnectionRef.current) {
          const sender = peerConnectionRef.current.getSenders().find(s => !s.track || s.track.kind === 'video');
          if (sender && localStreamRef.current.getVideoTracks()[0]) {
            await sender.replaceTrack(localStreamRef.current.getVideoTracks()[0]);
          }
        }
      } catch (e) {
        console.warn('replaceTrack(videoTrack) failed', e);
      }
    }

    showNotification(newCameraOn ? 'Camera on' : 'Camera off');

    try {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({
          type: 'media_state',
          media: 'camera',
          enabled: newCameraOn
        }));
      }
    } catch (e) {
      console.warn('media_state camera send failed', e);
    }
  }, [isCameraOn, showNotification]);

  const handleScreenShareToggle = useCallback(async () => {
    if (!isScreenSharing) {
      try {
        if (screenShareLocked && screenShareHolder && screenShareHolder !== MY_ROLE) {
          showNotification(`${screenShareHolder} is already sharing their screen.`, 'warning');
          return;
        }

        const granted = await new Promise((resolve) => {
          pendingScreenShareGrantResolverRef.current = resolve;
          try {
            if (socketRef.current?.readyState === WebSocket.OPEN) {
              socketRef.current.send(JSON.stringify({ type: 'screen_share_request' }));
            }
          } catch (e) {
            resolve(false);
          }
          setTimeout(() => {
            if (pendingScreenShareGrantResolverRef.current) {
              const r = pendingScreenShareGrantResolverRef.current;
              pendingScreenShareGrantResolverRef.current = null;
              r(false);
            }
          }, 4000);
        });

        if (!granted) {
          if (screenShareLocked && screenShareHolder) {
            showNotification(`${screenShareHolder} is already sharing. Please wait.`, 'warning');
          }
          return;
        }

        const screenShareStream = await navigator.mediaDevices.getDisplayMedia({
          video: {
            displaySurface: 'monitor',
            cursor: 'always'
          },
          audio: false
        });

        setIsScreenSharing(true);
        screenShareStreamRef.current = screenShareStream;
        showNotification('Screen sharing started', 'success');

        if (peerConnectionRef.current) {
          const videoTrack = screenShareStream.getVideoTracks()[0];
          const sender = peerConnectionRef.current.getSenders().find(s =>
            s.track && s.track.kind === 'video'
          );
          if (sender) {
            await sender.replaceTrack(videoTrack);
            console.log('✅ Screen share track replaced in peer connection');
          }
        }

        try {
          if (socketRef.current?.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({ type: 'screen_share_state', active: true }));
          }
        } catch (e) { }

        const videoTrack = screenShareStream.getVideoTracks()[0];
        if (videoTrack) {
          videoTrack.onended = () => {
            console.log('Screen share ended by user');
            stopScreenSharing();
          };
        }
      } catch (error) {
        console.error('Error starting screen share:', error);
        showNotification('Failed to start screen share', 'error');
        try {
          if (socketRef.current?.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({ type: 'screen_share_release' }));
          }
        } catch (e) { }
      }
    } else {
      stopScreenSharing();
    }
  }, [isScreenSharing, screenShareLocked, screenShareHolder, showNotification]);

  const stopScreenSharing = useCallback(async () => {
    if (screenShareStreamRef.current) {
      screenShareStreamRef.current.getTracks().forEach(track => track.stop());
      screenShareStreamRef.current = null;
    }
    setIsScreenSharing(false);
    showNotification('Screen sharing stopped');

    try {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: 'screen_share_state', active: false }));
        socketRef.current.send(JSON.stringify({ type: 'screen_share_release' }));
      }
    } catch (e) { }

    // Restore camera
    if (localStreamRef.current && peerConnectionRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        try {
          const sender = peerConnectionRef.current.getSenders().find(s => s.track && s.track.kind === 'video');
          if (sender) {
            await sender.replaceTrack(videoTrack);
            console.log('✅ Camera track restored after screen share');
          }
        } catch (e) {
          console.warn('Failed to restore camera:', e);
        }
      }
    }
  }, [showNotification]);

  // Proxy violation notification
  const showProxyViolationNotification = useCallback((violationType, violationCount, violationLimit) => {
    const violation = {
      id: Date.now(),
      type: violationType,
      count: violationCount,
      limit: violationLimit
    };

    setProxyViolations(prev => [...prev, violation]);

    setTimeout(() => {
      setProxyViolations(prev => prev.filter(v => v.id !== violation.id));
    }, 8000);

    if (violationCount >= violationLimit) {
      setTimeout(() => {
        showNotification(`🚨 ${candidateName} exceeded violation limit - interview may be terminated`, 'error');
      }, 1000);
    }
  }, [candidateName, showNotification]);

  // End interview
  const handleEndInterview = useCallback(async (shouldSend = true) => {
    if (interviewEndedRef.current) return;

    if (shouldSend) {
      const confirmed = await showConfirmation('Are you sure you want to end the interview for everyone?');
      if (!confirmed) return;
    }

    if (bothPartiesConnected) {
      setSessionExpired(true);
      localStorage.setItem(sessionKey, 'true');
      console.log('✅ Session marked as expired - both parties connected once');
    }

    interviewEndedRef.current = true;
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);

    showNotification('Interview ended. Redirecting...', 'info');

    try {
      if (shouldSend && socketRef.current?.readyState === WebSocket.OPEN) {
        try {
          socketRef.current.send(JSON.stringify({ type: 'screen_share_state', active: false }));
          socketRef.current.send(JSON.stringify({ type: 'screen_share_release' }));
        } catch (e) { }
        socketRef.current.send(JSON.stringify({ type: 'end_interview' }));
      }
    } catch (e) {
      console.warn('end_interview send failed', e);
    }

    if (socketRef.current) socketRef.current.close();
    localStreamRef.current?.getTracks().forEach(track => track.stop());
    screenShareStreamRef.current?.getTracks().forEach(track => track.stop());

    try {
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
        peerConnectionRef.current = null;
      }
    } catch (e) { }

    // Persist interview duration
    try {
      const totalTime = timer;
      const payload = {
        token: sessionId,
        isInterviewer: true,
        totalTime: totalTime,
        sessionId: sessionId,
        isDraft: true
      };
      fetch('/submit-interview-feedback/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(payload)
      }).catch(() => { });
    } catch (e) {
      console.warn('Failed to persist total time on end:', e);
    }

    // Redirect to feedback page
    setTimeout(() => {
      const feedbackParams = new URLSearchParams({
        candidate: candidateName,
        interviewer: interviewerName,
        time: timer,
        status: candidateHasJoinedRef.current ? 'joined' : 'not_joined',
        session: sessionId
      });
      navigate(`/feedback-page/?${feedbackParams.toString()}`);
    }, 800);
  }, [bothPartiesConnected, sessionKey, showNotification, showConfirmation, timer, sessionId, candidateName, interviewerName, navigate]);

  // Initialize WebSocket on mount
  useEffect(() => {
    if (!sessionExpired && localStorage.getItem(sessionKey) !== 'true') {
      connectWebSocket();
    } else {
      setSessionExpired(true);
    }

    return () => {
      interviewEndedRef.current = true;
      if (socketRef.current) socketRef.current.close();
      if (peerConnectionRef.current) peerConnectionRef.current.close();
      localStreamRef.current?.getTracks().forEach(track => track.stop());
      screenShareStreamRef.current?.getTracks().forEach(track => track.stop());
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
    };
  }, [sessionExpired, connectWebSocket]);

  // Draggable camera
  useEffect(() => {
    const selfVideoContainer = selfVideoContainerRef.current;
    if (!selfVideoContainer) return;

    let isDragging = false;
    let startX, startY, initialX, initialY;

    const startDrag = (e) => {
      isDragging = true;
      startX = e.clientX || e.touches[0].clientX;
      startY = e.clientY || e.touches[0].clientY;

      const parent = selfVideoContainer.parentElement;
      const parentRect = parent.getBoundingClientRect();
      const selfRect = selfVideoContainer.getBoundingClientRect();

      initialX = selfRect.left - parentRect.left;
      initialY = selfRect.top - parentRect.top;

      selfVideoContainer.style.transition = 'none';
    };

    const drag = (e) => {
      if (!isDragging) return;
      e.preventDefault();

      const currentX = e.clientX || e.touches[0].clientX;
      const currentY = e.clientY || e.touches[0].clientY;

      const deltaX = currentX - startX;
      const deltaY = currentY - startY;

      let newX = initialX + deltaX;
      let newY = initialY + deltaY;

      const parent = selfVideoContainer.parentElement;
      const parentRect = parent.getBoundingClientRect();
      const footer = document.querySelector('footer');
      let availableHeight = parentRect.height;

      if (footer) {
        const footerRect = footer.getBoundingClientRect();
        const footerTopInParent = footerRect.top - parentRect.top;
        availableHeight = Math.max(0, footerTopInParent - 10);
      } else {
        availableHeight = parentRect.height - 60;
      }

      if (newX < 0) newX = 0;
      if (newY < 0) newY = 0;
      if (newX + selfVideoContainer.offsetWidth > parentRect.width) {
        newX = parentRect.width - selfVideoContainer.offsetWidth;
      }
      if (newY + selfVideoContainer.offsetHeight > availableHeight) {
        newY = availableHeight - selfVideoContainer.offsetHeight;
      }

      selfVideoContainer.style.left = newX + 'px';
      selfVideoContainer.style.top = newY + 'px';
      selfVideoContainer.style.right = 'auto';
      selfVideoContainer.style.bottom = 'auto';
    };

    const stopDrag = () => {
      isDragging = false;
      selfVideoContainer.style.transition = '';
    };

    selfVideoContainer.addEventListener('mousedown', startDrag);
    selfVideoContainer.addEventListener('touchstart', startDrag);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
    document.addEventListener('touchmove', drag);
    document.addEventListener('touchend', stopDrag);

    return () => {
      selfVideoContainer.removeEventListener('mousedown', startDrag);
      selfVideoContainer.removeEventListener('touchstart', startDrag);
      document.removeEventListener('mousemove', drag);
      document.removeEventListener('mouseup', stopDrag);
      document.removeEventListener('touchmove', drag);
      document.removeEventListener('touchend', stopDrag);
    };
  }, []);

  // Star rating handlers
  const setStarRating = useCallback((category, rating) => {
    setRatings(prev => ({
      ...prev,
      [category]: rating
    }));
  }, []);

  const handleStarClick = useCallback((category, rating) => {
    setStarRating(category, rating);
  }, [setStarRating]);

  const handleStarHover = useCallback((category, rating, container) => {
    // Visual feedback can be added here
  }, []);

  // Skills editing
  const handleEditSkills = useCallback(() => {
    setEditingSkills(true);
  }, []);

  const handleCancelSkills = useCallback(() => {
    setEditingSkills(false);
  }, []);

  const handleSaveSkills = useCallback(() => {
    setEditingSkills(false);
    // Save logic here
  }, []);

  const handleSkillScoreChange = useCallback((index, score) => {
    setSkills(prev => {
      const newSkills = [...prev];
      newSkills[index] = { ...newSkills[index], score: parseInt(score) || 0 };
      return newSkills;
    });
  }, []);

  // Submit feedback
  const handleSubmitFeedback = useCallback(async () => {
    if (ratings.overallRating === 0) {
      showNotification('Please provide an overall rating', 'error');
      return;
    }

    if (!ratings.hireRecommendation) {
      showNotification('Please select a hire recommendation', 'error');
      return;
    }

    try {
      const payload = {
        token: sessionId,
        candidate: candidateName,
        interviewer: interviewerName,
        time: timer,
        ratings: ratings,
        skills: skills,
        status: candidateHasJoinedRef.current ? 'joined' : 'not_joined'
      };

      // Submit feedback API call would go here
      console.log('Submitting feedback:', payload);

      setShowFeedbackSuccess(true);
      setTimeout(() => {
        setShowFeedbackSuccess(false);
        navigate('/dashboard');
      }, 2000);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      showNotification('Failed to submit feedback', 'error');
    }
  }, [ratings, skills, sessionId, candidateName, interviewerName, timer, showNotification, navigate]);

  // Handle end interview modal actions
  const handleJoinLater = useCallback(() => {
    setShowEndInterviewModal(false);
    showNotification('Functionality to join later would be implemented here.', 'info');
  }, [showNotification]);

  const handleEndWithFeedback = useCallback(() => {
    setShowEndInterviewModal(false);

    try {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: 'end_interview' }));
        console.log('Sent end_interview message to candidate');
      }
    } catch (error) {
      console.error('Error sending end_interview message:', error);
    }

    const feedbackParams = new URLSearchParams({
      candidate: candidateName,
      interviewer: interviewerName,
      time: timer,
      status: candidateHasJoinedRef.current ? 'joined' : 'not_joined',
      session: sessionId
    });

    navigate(`/feedback-page/?${feedbackParams.toString()}`);
  }, [candidateName, interviewerName, timer, sessionId, navigate]);

  const confirmEndInterview = useCallback((status) => {
    setShowEndInterviewModal(false);

    // Logic to handle qualification/rejection
    console.log(`Interview ended with status: ${status}`);
    setRatings(prev => ({ ...prev, hireRecommendation: status }));

    // Send end interview signal
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'end_interview',
        reason: status
      }));
    }

    // Navigate to feedback or dashboard
    setShowInterviewReport(true);
  }, []);

  if (sessionExpired && !showInterviewReport) {
    return (
      <div style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 50
      }}>
        <div style={{
          background: 'white',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          maxWidth: '28rem',
          margin: '0 1rem',
          textAlign: 'center'
        }}>
          <div style={{ marginBottom: '1rem' }}>
            <i className="fas fa-clock" style={{ fontSize: '3rem', color: '#9ca3af' }}></i>
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem', color: '#1f2937' }}>
            Session Completed
          </h3>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
            This interview session has already been completed. You cannot rejoin the interview.
          </p>
          <button
            onClick={() => {
              navigate('/live-interview-list');
              window.location.reload(); // Ensure a fresh state for sockets
            }}
            style={{
              width: '100%',
              background: '#6b7280',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            Close
          </button>
        </div>
      </div>
    );
  }
  // Render
  return (
    <div className={`live-interview-interviewer ${chatPanelVisible ? 'chat-active' : ''}`}>
      {/* Header */}


      {/* Main Content */}
      <div className="main-wrapper">
        <div className="video-container">

          {/* REMOTE VIDEO (Target Candidate) */}
          <video
            ref={remoteVideoRef}
            className="remote-video"
            autoPlay
            playsInline
            onContextMenu={e => e.preventDefault()}
            style={{ display: isRemoteCameraOn ? 'block' : 'none' }}
          />

          {!isRemoteCameraOn && bothPartiesConnected && (
            <div className="remote-video-placeholder" style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
              <VideoPlaceholder name={candidateName} />
            </div>
          )}


          {/* Connection Status Overlay */}
          {connectionStatus !== 'Connected' && (
            <div className="connection-overlay">
              <i className="fas fa-spinner spinner"></i>
              <h3>{connectionStatus}</h3>
              <p>Waiting for connection...</p>
            </div>
          )}

          {/* Name Label for Candidate */}
          {bothPartiesConnected && (
            <div className="video-label" style={{ top: '20px', left: '20px', bottom: 'auto' }}>
              <span>{candidateName}</span>
              <i className="fas fa-microphone" style={{ fontSize: '12px', marginLeft: '6px' }}></i>
            </div>
          )}

          {/* LOCAL VIDEO (Self View) - Draggable */}
          <div
            className="self-video-container"
            ref={selfVideoContainerRef}
            onMouseDown={handleDragStart}
          >
            <video
              ref={selfVideoRef}
              className="self-video"
              autoPlay
              muted
              style={{ display: isCameraOn ? 'block' : 'none' }}
            />
            {!isCameraOn && (
              <div style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}>
                <VideoPlaceholder name="You" width="100%" height="100%" />
              </div>
            )}
            <div className="video-label">
              <span>{interviewerName} (You)</span>
            </div>
          </div>

        </div>

        {/* Chat Sidebar */}
        <div className={`chat-sidebar ${!chatPanelVisible ? 'closed' : ''}`}>
          <div className="chat-header">
            <h3>Meeting Chat</h3>
            <button className="close-chat" onClick={() => setChatPanelVisible(false)}>
              <i className="fas fa-times"></i>
            </button>
          </div>

          <div className="chat-messages">
            {chatMessages.map((msg, index) => (
              <div
                key={index}
                className={`chat-msg ${msg.isMyMessage ? 'sent' : 'received'}`}
              >
                <span className="msg-meta">
                  {msg.sender} • {msg.time}
                </span>
                {msg.message}
              </div>
            ))}
            <div ref={chatMessagesRef} />
          </div>

          <div className="chat-input-area">
            <input
              type="text"
              placeholder="Type a message..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendChatMessage()}
            />
            <button className="btn-send" onClick={sendChatMessage}>
              <i className="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>

      </div>

      {/* Control Bar (Bottom Floating) */}
      <div className="control-bar-wrapper">
        <div className="control-bar">
          <button
            className={`control-btn ${!isMuted ? 'active' : 'off'}`}
            onClick={handleMuteToggle}
            title={isMuted ? "Unmute" : "Mute"}
          >
            <div className="icon-circle">
              <i className={`fas fa-microphone${isMuted ? '-slash' : ''}`}></i>
            </div>
            <span className="control-label">{isMuted ? "Unmute" : "Mute"}</span>
          </button>

          <button
            className={`control-btn ${isCameraOn ? 'active' : 'off'}`}
            onClick={handleCameraToggle}
            title={isCameraOn ? "Stop Video" : "Start Video"}
          >
            <div className="icon-circle">
              <i className={`fas fa-video${!isCameraOn ? '-slash' : ''}`}></i>
            </div>
            <span className="control-label">{isCameraOn ? "Stop Video" : "Start Video"}</span>
          </button>

          <button
            className={`control-btn screen-share ${isScreenSharing ? 'active' : ''}`}
            onClick={handleScreenShareToggle}
            title="Share Screen"
          >
            <div className="icon-circle">
              <i className="fas fa-desktop"></i>
            </div>
            <span className="control-label">Share</span>
          </button>

          <button
            className={`control-btn ${chatPanelVisible ? 'active' : ''}`}
            onClick={() => {
              setChatPanelVisible(!chatPanelVisible);
              setChatUnreadCount(0);
            }}
            title="Chat"
            style={{ position: 'relative' }}
          >
            <div className="icon-circle">
              <i className="fas fa-comment-alt"></i>
              {chatUnreadCount > 0 && <span className="unread-badge">{chatUnreadCount}</span>}
            </div>
            <span className="control-label">Chat</span>
          </button>

          <button className="btn-end" onClick={handleEndInterview} style={{ marginLeft: '10px' }}>
            End Call
          </button>
        </div>
      </div>

      {/* Proxy Notifications */}
      <div className="proxy-notification-container">
        {proxyViolations.map((v) => (
          <div key={v.id} className="proxy-violation-notification">
            <div className="violation-header">
              <i className="fas fa-exclamation-triangle"></i>
              <span>Proxy Warning</span>
              <span className="violation-count">{v.count}/{v.limit}</span>
            </div>
            <p className="violation-details">
              <strong>{v.type}</strong>
              <br />
              Detected at {v.time}
            </p>
          </div>
        ))}
      </div>

      {/* Report Modal */}
      {
        showInterviewReport && (
          <div className="modal">
            <div className="modal-content" style={{ maxWidth: '600px', textAlign: 'left' }}>
              <h2>Interview Feedback Report</h2>
              <p className="mb-4">Rate the candidate's performance ({candidateName})</p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <label className="block mb-2 text-sm font-medium">Coding Skills</label>
                  <input
                    type="range" min="1" max="10"
                    className="w-full"
                    value={ratings.codingLanguage}
                    onChange={e => setRatings({ ...ratings, codingLanguage: parseInt(e.target.value) })}
                  />
                  <div className="text-right text-sm">{ratings.codingLanguage}/10</div>
                </div>
                <div>
                  <label className="block mb-2 text-sm font-medium">Problem Solving</label>
                  <input
                    type="range" min="1" max="10"
                    className="w-full"
                    value={ratings.solutionApproach}
                    onChange={e => setRatings({ ...ratings, solutionApproach: parseInt(e.target.value) })}
                  />
                  <div className="text-right text-sm">{ratings.solutionApproach}/10</div>
                </div>
                {/* Add more fields as needed */}
              </div>

              <div className="text-right mt-6">
                <button className="btn-secondary mr-2" onClick={() => setShowInterviewReport(false)}>Cancel</button>
                <button className="btn-blue" onClick={() => {
                  setShowInterviewReport(false);
                  setShowFeedbackSuccess(true);
                  setTimeout(() => setShowFeedbackSuccess(false), 3000);
                }}>Submit Report</button>
              </div>
            </div>
          </div>
        )
      }

      {/* Confirmation Modal */}
      {
        showConfirmModal && (
          <div className="modal-overlay">
            <div className="modal-card">
              <h2>Confirm Action</h2>
              <p className="mb-4">{confirmMessage}</p>
              <div className="modal-buttons">
                <button className="btn-secondary" onClick={handleConfirmNo}>Cancel</button>
                <button className="btn-danger" onClick={handleConfirmYes}>Confirm</button>
              </div>
            </div>
          </div>
        )
      }

      {/* End Interview Modal */}
      {
        showEndInterviewModal && (
          <div className="end-interview-modal">
            <div className="end-interview-content">
              <button className="close-modal-btn" onClick={() => setShowEndInterviewModal(false)}>
                <i className="fas fa-times"></i>
              </button>

              <h2>End Interview Session?</h2>

              <div className="end-interview-options">
                <div className="end-interview-option">
                  <div style={{ fontSize: '2rem', color: '#10b981', marginBottom: '0.5rem' }}>
                    <i className="fas fa-check-circle"></i>
                  </div>
                  <p>Complete & Qualify</p>
                  <span className="text-sm text-gray-500 mb-4">Candidate passed requirements</span>
                  <button
                    style={{ backgroundColor: '#10b981', color: 'white' }}
                    onClick={() => confirmEndInterview('Qualified')}
                  >
                    Qualify Candidate
                  </button>
                </div>

                <div className="end-interview-option">
                  <div style={{ fontSize: '2rem', color: '#ef4444', marginBottom: '0.5rem' }}>
                    <i className="fas fa-times-circle"></i>
                  </div>
                  <p>Reject</p>
                  <span className="text-sm text-gray-500 mb-4">Did not meet requirements</span>
                  <button
                    style={{ backgroundColor: '#ef4444', color: 'white' }}
                    onClick={() => confirmEndInterview('Rejected')}
                  >
                    Reject Candidate
                  </button>
                </div>
              </div>
            </div>
          </div>
        )
      }

    </div >
  );
}

export default LiveInterviewInterviewer;