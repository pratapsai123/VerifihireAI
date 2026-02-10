import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/LiveInterviewInterviewer.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

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
  const remoteVideoRef = useRef(null);
  const remoteVideoBackupRef = useRef(null);
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
  }, []);

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
        <button onclick="window.close()" style="width: 100%; background: #6b7280; color: white; padding: 0.5rem 1rem; border-radius: 0.375rem; border: none; cursor: pointer;">
          Close
        </button>
      </div>
    `;
    document.body.appendChild(popup);
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

  // WebSocket connection
  const buildWsCandidates = useCallback((sessionId) => {
    // Get backend URL from API_BASE_URL
    const apiUrl = API_BASE_URL.replace('/api', '').replace('http://', '').replace('https://', '');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

    // Try backend URL first, then fallback to current host
    const hosts = [];
    if (apiUrl) {
      hosts.push(apiUrl);
    }
    hosts.push(window.location.host);
    hosts.push(window.location.hostname);
    const bare = window.location.hostname.replace(/^www\./, '');
    if (!hosts.includes(bare)) hosts.push(bare);
    if (!hosts.includes(`www.${bare}`)) hosts.push(`www.${bare}`);

    const paths = [`/ws/interview/${sessionId}/interviewer/`, `/ws/interview/${sessionId}/interviewer`];
    const urls = [];
    for (const h of hosts) {
      for (const p of paths) {
        urls.push(`${protocol}//${h}${p}`);
      }
    }
    return urls;
  }, []);

  const connectWebSocket = useCallback(() => {
    if (interviewEndedRef.current || sessionExpired) return;

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

        const fallbackTimer = setTimeout(() => {
          if (!socket || socket.readyState !== 1) {
            try { socket.close(); } catch { }
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
      console.log('📩 Received message:', data);

      switch (data.type) {
        case 'connection_error':
          console.error('❌ Server reported connection error:', data.error);
          showNotification(`Connection error: ${data.error}`, 'error');
          break;
        case 'user_joined':
          const joinedUserName = data.user === 'Candidate' ? candidateName : data.user;
          showNotification(`${joinedUserName} joined the session.`);
          if (data.user === 'Candidate' && peerConnectionRef.current) {
            console.log('🎯 Candidate joined, creating video offer...');
            candidateHasJoinedRef.current = true;
            setTimeout(() => {
              createVideoOffer();
            }, 1000);
            setBothPartiesConnected(true);
            setSessionExpired(true);
            localStorage.setItem(sessionKey, 'true');
            console.log('🔒 Session marked as expired - both parties have connected');
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
          if (peerConnectionRef.current) await handleVideoOffer(data.offer);
          break;
        case 'video_answer':
          if (peerConnectionRef.current) await handleVideoAnswer(data.answer);
          break;
        case 'media_state':
          if (String(data.sender).toLowerCase() !== 'candidate') break;
          const who = candidateName;
          const what = data.media === 'mic' ? (data.enabled ? 'unmuted mic' : 'muted mic') : (data.enabled ? 'turned on camera' : 'turned off camera');
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
            if (remoteVideoBackupRef.current) {
              remoteVideoBackupRef.current.style.objectFit = targetFit;
              remoteVideoBackupRef.current.style.objectPosition = 'center center';
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
              console.warn('Primary video play failed:', e);
              if (remoteVideoBackupRef.current) {
                remoteVideoBackupRef.current.srcObject = remoteStream;
                remoteVideoBackupRef.current.style.display = 'block';
                remoteVideoBackupRef.current.muted = false;
                remoteVideoBackupRef.current.play();
              }
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

      setTimeout(() => {
        if (peerConnection && peerConnection.connectionState !== 'connected') {
          console.log('🔄 Auto-triggering video connection...');
          createVideoOffer();
        }
      }, 3000);

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
    if (!peerConnectionRef.current) return;

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
    if (!sessionExpired) {
      connectWebSocket();
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
            onClick={() => window.close()}
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

  return (
    <div className="live-interview-interviewer">
      {/* Header */}
      <header className="header">
        <h1>FDI Live Interview</h1>
        <div className="header-controls">
          <span id="timer" className="timer">{timer}</span>
          <button
            id="endInterviewBtn"
            className="btn btn-red"
            onClick={() => setShowEndInterviewModal(true)}
          >
            <i className="fa-solid fa-phone-slash"></i>
            <span>End Interview</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="main-wrapper">
        {/* Video Container */}
        <div className="video-container">
          {/* Main Video Area */}
          <main id="mainVideoArea" className="main-video-area">
            {/* Primary remote video feed */}
            <video
              id="remoteVideo"
              ref={remoteVideoRef}
              className="remote-video"
              autoPlay
              playsInline
              muted={false}
            ></video>

            {/* Fallback video element */}
            <video
              id="remoteVideoBackup"
              ref={remoteVideoBackupRef}
              className="remote-video"
              autoPlay
              playsInline
              muted={false}
              style={{ display: 'none' }}
            ></video>

            {/* Self video */}
            <div
              id="selfVideoContainer"
              ref={selfVideoContainerRef}
              className="self-video-container"
              style={{ display: isCameraOn ? '' : 'none' }}
            >
              <video
                id="self-video"
                ref={selfVideoRef}
                className="self-video"
                autoPlay
                muted
                playsInline
              ></video>
              <div className="video-label">{interviewerName}</div>
            </div>

            {/* Connection status overlay */}
            <div
              id="connectionStatusOverlay"
              className={`connection-overlay ${connectionStatusClass}`}
              style={{ display: connectionStatusClass === 'connected' ? 'none' : 'block' }}
            >
              <span id="connectionStatusText">{connectionStatus}</span>
            </div>

            {/* Candidate name label */}
            <div className="candidate-label">
              {candidateName}
            </div>
          </main>

          {/* Bottom Controls */}
          <footer>
            <div>
              <button id="candidateScreenBtn" className="btn btn-gray">Candidate Screen</button>
            </div>
            <div className="footer-controls">
              <button
                id="muteBtn"
                className={`control-btn ${isMuted ? 'bg-red-600' : ''}`}
                onClick={handleMuteToggle}
              >
                <i className={`fas ${isMuted ? 'fa-microphone-slash' : 'fa-microphone'}`}></i>
              </button>
              <button
                id="cameraBtn"
                className={`control-btn ${!isCameraOn ? 'bg-red-600' : ''}`}
                onClick={handleCameraToggle}
              >
                <i className={`fas ${isCameraOn ? 'fa-video' : 'fa-video-slash'}`}></i>
              </button>
              <button
                id="screenShareBtn"
                className={`control-btn ${isScreenSharing ? 'bg-blue-600' : ''}`}
                onClick={handleScreenShareToggle}
                disabled={screenShareLocked && screenShareHolder && screenShareHolder !== MY_ROLE}
              >
                <i className={`fas ${isScreenSharing ? 'fa-stop-circle' : 'fa-desktop'}`}></i>
              </button>
              {/* Chat Button */}
              <button
                id="chatToggleBtn"
                className="control-btn"
                onClick={() => {
                  setChatPanelVisible(!chatPanelVisible);
                  if (chatPanelVisible) {
                    setChatUnreadCount(0);
                  }
                }}
                title="Open Chat"
                style={{ position: 'relative' }}
              >
                <i className="fas fa-comment-dots"></i>
                {chatUnreadCount > 0 && (
                  <span style={{
                    position: 'absolute',
                    top: '-6px',
                    right: '-6px',
                    backgroundColor: '#dc2626',
                    color: '#fff',
                    fontSize: '10px',
                    lineHeight: '10px',
                    width: '16px',
                    height: '16px',
                    borderRadius: '9999px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '2px'
                  }}>
                    {chatUnreadCount > 9 ? '9+' : chatUnreadCount}
                  </span>
                )}
              </button>
            </div>
            <div className="session-info">
              <span>Session: <span id="sessionDisplay">{sessionId}</span></span>
            </div>
          </footer>
        </div>

        {/* Chat Bar */}
        <div
          id="chatBar"
          className={chatPanelVisible ? '' : 'hidden'}
          style={{ display: chatPanelVisible ? 'block' : 'none' }}
        >
          <div className="chat-container">
            <div className="chat-header">
              <h3>CHAT</h3>
              <button
                id="closeChatBtn"
                className="chat-close-btn"
                onClick={() => setChatPanelVisible(false)}
              >
                &times;
              </button>
            </div>
            <div
              id="chatMessages"
              ref={chatMessagesRef}
              className="chat-messages hide-scrollbar"
            >
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`chat-message-container ${msg.isMyMessage ? 'text-right' : 'text-left'}`}
                >
                  <div className={`chat-message-bubble ${msg.isMyMessage ? 'own-message' : 'other-message'}`}>
                    <div className="chat-message-content">
                      <div className="chat-message-header">
                        <span className="chat-message-sender">{msg.sender}</span>
                        &nbsp;&nbsp;
                        <span className="chat-message-time">{msg.time}</span>
                      </div>
                      <div className="chat-message-text">{msg.message}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="chat-input-container">
              <input
                id="chatInput"
                ref={chatInputRef}
                type="text"
                placeholder="Type a message..."
                className="chat-input"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    sendChatMessage();
                  }
                }}
                autoComplete="off"
              />
              <button
                id="chatSendBtn"
                className="chat-send-btn"
                onClick={sendChatMessage}
              >
                <i className="fas fa-paper-plane"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Proxy Violation Notifications */}
      <div id="proxyNotificationContainer" className="proxy-notification-container">
        {proxyViolations.map((violation) => {
          let icon = '⚠️';
          if (violation.type.includes('Multiple people')) icon = '👥';
          else if (violation.type.includes('device')) icon = '📱';
          else if (violation.type.includes('Tab switching')) icon = '🔄';
          else if (violation.type.includes('No participant')) icon = '👻';
          else if (violation.type.includes('keyboard') || violation.type.includes('Right-click')) icon = '⌨️';

          return (
            <div key={violation.id} className="proxy-violation-notification">
              <div className="violation-header">
                <span>{icon}</span>
                <span>Proxy Violation Detected</span>
                <span className="violation-count">{violation.count}/{violation.limit}</span>
              </div>
              <div className="violation-details">
                <strong>{candidateName}</strong>: {violation.type}
              </div>
            </div>
          );
        })}
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div id="confirmModal" className="modal">
          <div className="modal-content">
            <p id="confirmMessage" className="modal-message">{confirmMessage}</p>
            <div className="modal-buttons">
              <button id="confirmYes" className="btn btn-red" onClick={handleConfirmYes}>Yes</button>
              <button id="confirmNo" className="btn btn-gray" onClick={handleConfirmNo}>No</button>
            </div>
          </div>
        </div>
      )}

      {/* Connection Failed Modal */}
      {showConnectionFailedModal && (
        <div id="connectionFailedModal" className="connection-failed-modal">
          <div className="connection-failed-content">
            <i className="fa-solid fa-tower-broadcast"></i>
            <h2>Connection Failed</h2>
            <p>The application could not connect to the required server.</p>

            <div className="troubleshooting">
              <h3>Troubleshooting Steps:</h3>
              <ul>
                <li>Ensure your local WebSocket server is running.</li>
                <li>Check that it is accessible at the address: <code>ws://www.facedinterview.com</code>.</li>
                <li>Look for any errors in your server's console output.</li>
                <li>Make sure no other service is blocking the connection.</li>
              </ul>
            </div>

            <button onClick={() => window.location.reload()} className="reload-page-btn">
              <i className="fa-solid fa-rotate-right"></i>
              Reload Page
            </button>
          </div>
        </div>
      )}

      {/* End Interview Confirmation Modal */}
      {showEndInterviewModal && (
        <div id="endInterviewConfirmModal" className="end-interview-modal">
          <div className="end-interview-content">
            <button
              id="dismissEndInterviewBtn"
              className="close-modal-btn"
              onClick={() => setShowEndInterviewModal(false)}
            >
              &times;
            </button>
            <h2>Do you want to join later or end it?</h2>
            <div className="end-interview-options">
              <div className="end-interview-option">
                <p>This will end the interview for you</p>
                <button id="joinLaterBtn" className="btn-blue" onClick={handleJoinLater}>
                  Join Later
                </button>
              </div>
              <div className="end-interview-option">
                <p>This will end the interview for all and mark it as completed.</p>
                <button
                  id="endInterviewWithFeedbackBtn"
                  className="btn-red"
                  onClick={handleEndWithFeedback}
                >
                  End Interview with Feedback
                </button>
              </div>
            </div>
            <div className="text-center">
              <button
                id="dismissEndInterviewBtn2"
                className="dismiss-btn"
                onClick={() => setShowEndInterviewModal(false)}
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LiveInterviewInterviewer;
