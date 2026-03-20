import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import '../styles/LiveInterview.css';
import VideoPlaceholder from '../components/VideoPlaceholder';
import { API_BASE_URL, WS_BASE_URL } from '../apiConfig';

function LiveInterview() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('token') || searchParams.get('session') || searchParams.get('sessionId') || 'default-session';

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
  const [isRemoteScreenSharing, setIsRemoteScreenSharing] = useState(false);
  const [screenShareLocked, setScreenShareLocked] = useState(false);
  const [screenShareHolder, setScreenShareHolder] = useState(null);

  // UI states
  const [chatPanelVisible, setChatPanelVisible] = useState(false);
  const [statusPanelVisible, setStatusPanelVisible] = useState(false);
  const [chatUnreadCount, setChatUnreadCount] = useState(0);
  const [showThankYou, setShowThankYou] = useState(false);
  const [showFinalThankYou, setShowFinalThankYou] = useState(false);
  const [feedback, setFeedback] = useState('');

  // Dragging state
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  // Connection states
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [connectionStatusText, setConnectionStatusText] = useState('Connecting...');
  const [timer, setTimer] = useState('00:00:00');

  // Proxy detection states
  const [cameraReady, setCameraReady] = useState(false);
  const [isDetectionPaused, setIsDetectionPaused] = useState(false);
  const [violationCount, setViolationCount] = useState(0);
  const violationLimit = 4;

  // Refs
  const socketRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const localStreamRef = useRef(null);
  const remoteStreamRef = useRef(null);
  const screenShareStreamRef = useRef(null);
  const remoteIceQueueRef = useRef([]);
  const pendingOfferRef = useRef(null);
  const thumbnailVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const screenShareVideoRef = useRef(null);
  const chatMessagesRef = useRef(null);
  const chatInputRef = useRef(null);
  const startTimeRef = useRef(Date.now());
  const streamIntervalRef = useRef(null);
  const pauseTimeoutRef = useRef(null);
  const lastPersonDetectedTimeRef = useRef(Date.now());
  const noPersonPopupShownRef = useRef(false);
  const pendingScreenShareGrantResolverRef = useRef(null);
  const selfVideoContainerRef = useRef(null);
  const videoConnectedNotifiedRef = useRef(false);
  const chatDedupRef = useRef(new Map());

  const sessionKey = `session_expired_${sessionId}`;
  const MY_ROLE = 'Candidate';

  // Check if session is expired
  useEffect(() => {
    if (localStorage.getItem(sessionKey) === 'true') {
      setSessionExpired(true);
      showSessionExpiredMessage();
    }
  }, [sessionKey]);

  // Timer effect
  useEffect(() => {
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTimeRef.current;
      const hours = Math.floor(elapsed / 3600000);
      const minutes = Math.floor((elapsed % 3600000) / 60000);
      const seconds = Math.floor((elapsed % 60000) / 1000);

      setTimer(
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      );
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // WebSocket connection
  useEffect(() => {
    if (sessionExpired) return;

    // Get backend URL from API_BASE_URL or use current host
    const apiUrl = API_BASE_URL.replace('/api', '').replace('http://', '').replace('https://', '').split(':')[0]; // Remove port if present to avoid :3000 issues
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const isProduction = window.location.hostname.includes('duckdns.org') || API_BASE_URL.includes('duckdns.org');

    const candidates = [];

    // 1. Explicit Production URL (Highest Priority for external access)
    if (isProduction) {
      candidates.push(`wss://verifihireai.com/ws/interview/${sessionId}/candidate/`);
    }

    // 2. API_BASE_URL derived
    if (apiUrl && apiUrl !== 'localhost' && !candidates.some(c => c.includes(apiUrl))) {
      candidates.push(`${protocol}//${apiUrl}/ws/interview/${sessionId}/candidate/`);
    }

    // 3. Current Host (Fallback)
    const currentHost = window.location.host;
    if (!candidates.some(c => c.includes(currentHost))) {
      candidates.push(`${protocol}//${currentHost}/ws/interview/${sessionId}/candidate/`);
    }

    // 4. Localhost Fallback (for mixed environments)
    if (window.location.hostname === 'localhost') {
      candidates.push(`${WS_BASE_URL}/interview/${sessionId}/candidate/`);
    }

    let socket;
    let idx = 0;
    let heartbeatInterval;
    let reconnectTimer;

    const tryNext = () => {
      if (idx >= candidates.length) {
        console.error('❌ All WS candidates failed to connect.');
        return;
      }
      const url = candidates[idx++];
      console.log(`🔌 Connecting WS to ${url} (Attempt ${idx}/${candidates.length})`);

      try {
        socket = new WebSocket(url);
      } catch (e) {
        console.warn('WS construction failed for', url, e);
        reconnectTimer = setTimeout(tryNext, 1000);
        return;
      }

      socket.addEventListener('error', (e) => {
        console.warn('WS error for', url, e);
        // Don't immediately tryNext here, wait for close or timeout
      });

      socket.addEventListener('open', () => {
        console.log('✅ WebSocket connected successfully to', url);
        socketRef.current = socket;
        setConnectionEstablished(true);
        setConnectionStatus('Connected');
        setConnectionStatusText('Ready for connection');

        // Heartbeat
        heartbeatInterval = setInterval(() => {
          try {
            socket.send(JSON.stringify({ type: 'client_ping', ts: Date.now() }));
          } catch { }
        }, 20000);

        initializeWebRTC();
      });

      socket.addEventListener('close', () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('Disconnected');
        if (heartbeatInterval) clearInterval(heartbeatInterval);
      });

      socket.addEventListener('error', (error) => {
        console.error('❌ WebSocket error:', error);
        setConnectionStatus('Error');
      });

      socket.addEventListener('message', handleWebSocketMessage);
    };

    tryNext();

    return () => {
      if (socket) socket.close();
      if (heartbeatInterval) clearInterval(heartbeatInterval);
    };
  }, [sessionId, sessionExpired]);

  // Utility functions
  const showSessionPopup = useCallback((message, severity = 'info') => {
    const popup = document.createElement('div');
    popup.className = `session-popup ${severity}`;
    popup.textContent = message;
    document.body.appendChild(popup);
    setTimeout(() => popup.remove(), 3000);
  }, []);

  const showPopup = useCallback((message) => {
    const popupContainer = document.getElementById('popupContainer');
    if (!popupContainer) return;

    const popup = document.createElement('div');
    popup.className = 'popup-message';
    popup.textContent = message;
    popupContainer.appendChild(popup);
    setTimeout(() => popup.remove(), 6000);
  }, []);

  const showNotification = useCallback((message, type) => {
    showSessionPopup(message, type);
  }, [showSessionPopup]);

  const redirectToThankYou = useCallback(() => {
    setShowThankYou(true);
    if (peerConnectionRef.current) peerConnectionRef.current.close();
  }, []);

  const redirectToTerminationPage = useCallback((vCount, vLimit, reason) => {
    const token = sessionId;
    const params = new URLSearchParams({
      session_id: token || 'N/A',
      interview_type: 'Live Interview',
      violation_count: String(vCount || ''),
      violation_limit: String(vLimit || ''),
      reason: reason || 'Policy violation'
    });
    navigate(`/interview-terminated?${params.toString()}`);
  }, [sessionId, navigate]);

  const showSessionExpiredMessage = useCallback(() => {
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

    const closeButton = popup.querySelector('#close-session-button');
    if (closeButton) {
      closeButton.onclick = () => {
        popup.remove();
        navigate('/thank-you');
      };
    }
  }, [navigate]);

  // WebSocket message handler
  const handleWebSocketMessage = useCallback((event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('Received message:', data);

      // Handle ping/pong
      if (data.type === 'server_ping' || data.type === 'pong') return;

      switch (data.type) {
        case 'connection_error':
          showNotification(`Connection error: ${data.error}`, 'error');
          break;

        case 'chat':
          console.log('📨 Received chat message:', data);
          handleChatMessage(data);
          break;

        case 'user_joined':
          handleUserJoined(data);
          break;

        case 'user_left':
          showSessionPopup(`${data.user === 'Interviewer' ? interviewerName : data.user} left the session`);
          break;

        case 'video_offer':
          if (data.sender !== candidateName) {
            if (peerConnectionRef.current) {
              handleVideoOffer(data.offer);
            } else {
              console.log('⏳ PC not ready (Candidate), queuing video offer');
              pendingOfferRef.current = data.offer;
            }
          }
          break;

        case 'video_answer':
          if (data.sender !== candidateName && peerConnectionRef.current) {
            handleVideoAnswer(data.answer);
          }
          break;

        case 'ice_candidate':
          if (data.sender !== candidateName && peerConnectionRef.current && data.candidate) {
            handleIceCandidate(data.candidate);
          }
          break;

        case 'media_state':
          if (String(data.sender).toLowerCase() !== 'interviewer') break;
          const who = interviewerName;
          const what = data.media === 'mic'
            ? (data.enabled ? 'unmuted mic' : 'muted mic')
            : (data.enabled ? 'turned on camera' : 'turned off camera');

          if (data.media === 'camera') {
            setIsRemoteCameraOn(data.enabled);
          }

          const severity = (data.media === 'camera' && !data.enabled) ? 'error' : 'info';
          showSessionPopup(`${who} ${what}`, severity);
          break;

        case 'screen_share_lock':
          setScreenShareLocked(!!data.active);
          setScreenShareHolder(data.active ? (data.holder || null) : null);
          break;

        case 'screen_share_state':
          // Handle when someone starts/stops screen sharing
          if (data.sender && String(data.sender).toLowerCase() !== 'candidate') {
            setIsRemoteScreenSharing(!!data.active);
            // Someone else is sharing
            if (data.active) {
              showSessionPopup(`${data.sender || 'Interviewer'} started screen sharing`);
            } else {
              showSessionPopup(`${data.sender || 'Interviewer'} stopped screen sharing`);
            }

            // Adjust video fit
            if (remoteVideoRef.current) {
              remoteVideoRef.current.style.objectFit = data.active ? 'contain' : 'cover';
            }
          }
          break;

        case 'screen_share_granted':
          if (pendingScreenShareGrantResolverRef.current) {
            const resolver = pendingScreenShareGrantResolverRef.current;
            pendingScreenShareGrantResolverRef.current = null;
            resolver(true);
          }
          break;

        case 'screen_share_denied':
          if (pendingScreenShareGrantResolverRef.current) {
            const resolver = pendingScreenShareGrantResolverRef.current;
            pendingScreenShareGrantResolverRef.current = null;
            resolver(false);
          }
          if (screenShareLocked && screenShareHolder) {
            showSessionPopup(`${screenShareHolder} is already sharing. Please wait.`);
          }
          break;

        case 'screen_share_release':
          // Screen share lock released
          setScreenShareLocked(false);
          setScreenShareHolder(null);
          break;

        case 'end_interview':
          redirectToThankYou();
          break;

        case 'interview_terminated_violations':
          redirectToTerminationPage(data.violation_count, data.violation_limit, data.reason);
          break;

        case 'session_expired':
          setSessionExpired(true);
          localStorage.setItem(sessionKey, 'true');
          showSessionExpiredMessage();
          break;
      }
    } catch (error) {
      console.error('Error processing message:', error);
    }
  }, [candidateName, interviewerName, screenShareLocked, screenShareHolder, sessionKey]);

  // Chat message handler
  const handleChatMessage = useCallback((data) => {
    console.log('💬 Processing chat message:', data);

    const normalizeSender = (s) => {
      if (s == null) return s;
      const lower = String(s).toLowerCase();
      if (lower === 'interviewer') return interviewerName;
      if (lower === 'candidate') return candidateName;
      return s;
    };

    const senderNormalized = normalizeSender(data.sender);
    const isSelf = (
      String(data.sender).toLowerCase() === 'candidate' ||
      String(senderNormalized).toLowerCase() === String(candidateName).toLowerCase()
    );

    // Don't filter out self messages - we want to see our own messages too
    // But avoid duplicates
    if (isSelf) {
      console.log('📝 Self message, skipping duplicate');
      return;
    }

    // De-duplication
    if (!chatDedupRef.current) chatDedupRef.current = new Map();
    const now = Date.now();
    const key = `${senderNormalized}|${data.message}`;
    const last = chatDedupRef.current.get(key);
    if (last && (now - last) < 2000) return;
    chatDedupRef.current.set(key, now);
    if (chatDedupRef.current.size > 100) {
      const firstKey = chatDedupRef.current.keys().next().value;
      chatDedupRef.current.delete(firstKey);
    }

    console.log('✅ Adding chat message:', senderNormalized, data.message);
    appendChatMessage(senderNormalized, data.message, false);

    if (chatPanelVisible === false) {
      setChatUnreadCount(prev => prev + 1);
    }
  }, [candidateName, interviewerName, chatPanelVisible]);

  // Create video offer
  const createVideoOffer = useCallback(async () => {
    try {
      const offer = await peerConnectionRef.current.createOffer({
        offerToReceiveAudio: true,
        offerToReceiveVideo: true
      });
      await peerConnectionRef.current.setLocalDescription(offer);
      socketRef.current?.send(JSON.stringify({
        type: 'video_offer',
        offer: offer
      }));
    } catch (error) {
      console.error('Error creating video offer:', error);
    }
  }, []);

  // User joined handler
  const handleUserJoined = useCallback((data) => {
    const joinedUserName = data.user === 'Interviewer' ? interviewerName : data.user;
    showSessionPopup(`${joinedUserName} joined the session`);

    if (String(data.user).toLowerCase() === 'interviewer' && peerConnectionRef.current) {
      console.log('🎯 Interviewer joined — waiting for their video offer...');
      setBothPartiesConnected(true);

      // Fallback: if interviewer doesn't send an offer within 5s, ask them to re-offer
      setTimeout(() => {
        if (
          peerConnectionRef.current &&
          peerConnectionRef.current.connectionState !== 'connected' &&
          peerConnectionRef.current.connectionState !== 'connecting' &&
          socketRef.current?.readyState === WebSocket.OPEN
        ) {
          console.log('⏱️ No offer received from interviewer, requesting one...');
          socketRef.current.send(JSON.stringify({ type: 'request_offer' }));
        }
      }, 5000);
    }
  }, [interviewerName, showSessionPopup]);

  // Initialize WebRTC
  const initializeWebRTC = useCallback(async () => {
    try {
      console.log('🎬 Starting WebRTC initialization (CANDIDATE)...');

      let localStream;
      try {
        localStream = await navigator.mediaDevices.getUserMedia({
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
      } catch (mediaError) {
        console.error('❌ Media access failed:', mediaError);
        let errorMessage = 'Could not access camera/mic. ';
        if (mediaError.name === 'NotAllowedError') {
          errorMessage += 'Please allow camera and microphone permissions and refresh the page.';
        } else if (mediaError.name === 'NotFoundError') {
          errorMessage += 'No camera or microphone found. Please connect your devices.';
        } else if (mediaError.name === 'NotReadableError') {
          errorMessage += 'Camera/microphone is in use by another application.';
        } else {
          errorMessage += 'Please check your device connections and browser permissions.';
        }
        showSessionPopup(errorMessage);
        return;
      }

      localStreamRef.current = localStream;

      if (thumbnailVideoRef.current) {
        thumbnailVideoRef.current.srcObject = localStream;
        thumbnailVideoRef.current.muted = true;
      }

      // Initialize proxy detection
      setCameraReady(true);
      startDetection();

      // Create peer connection
      const configuration = {
        iceServers: [
          // STUN servers
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' },
          { urls: 'stun:stun2.l.google.com:19302' },
          { urls: 'stun:stun3.l.google.com:19302' },
          { urls: 'stun:stun4.l.google.com:19302' },
          // TURN UDP (fast but blocked by some firewalls)
          {
            urls: 'turn:openrelay.metered.ca:80',
            username: 'openrelayproject',
            credential: 'openrelayproject'
          },
          {
            urls: 'turn:openrelay.metered.ca:443',
            username: 'openrelayproject',
            credential: 'openrelayproject'
          },
          // TURN TCP (penetrates most firewalls and strict NATs)
          {
            urls: 'turn:openrelay.metered.ca:443?transport=tcp',
            username: 'openrelayproject',
            credential: 'openrelayproject'
          },
          {
            urls: 'turn:openrelay.metered.ca:80?transport=tcp',
            username: 'openrelayproject',
            credential: 'openrelayproject'
          },
          // Additional public TURN fallbacks
          {
            urls: 'turn:relay1.expressturn.com:3478',
            username: 'efKBBHHGTBSOHDUE',
            credential: 'vMjLVPCetTbVQGTz'
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

      // Connection state handlers
      peerConnection.onconnectionstatechange = () => {
        console.log('🔗 Connection state:', peerConnection.connectionState);
        if (peerConnection.connectionState === 'connected') {
          if (!videoConnectedNotifiedRef.current) {
            showSessionPopup('Video connection established!');
            videoConnectedNotifiedRef.current = true;
          }
          setConnectionStatusText('Connected');
        } else if (peerConnection.connectionState === 'failed') {
          showSessionPopup('Connection failed. Reconnecting...', 'error');
          setConnectionStatusText('Connection failed');
          // Ask interviewer to resend offer — don't create a new PC (that breaks sync)
          setTimeout(() => {
            if (
              peerConnectionRef.current &&
              peerConnectionRef.current.connectionState === 'failed' &&
              socketRef.current?.readyState === WebSocket.OPEN
            ) {
              console.log('🔄 Requesting new offer from interviewer (connection failed)...');
              socketRef.current.send(JSON.stringify({ type: 'request_offer' }));
            }
          }, 2000);
        }
      };

      peerConnection.oniceconnectionstatechange = () => {
        console.log('🧊 ICE connection state:', peerConnection.iceConnectionState);
        if (peerConnection.iceConnectionState === 'connected') {
          setConnectionStatusText('Connected');
        } else if (peerConnection.iceConnectionState === 'failed') {
          setConnectionStatusText('Connection failed - retrying...');
          // Ask interviewer for ICE restart offer — keeps the same PCs in sync
          setTimeout(() => {
            if (
              peerConnectionRef.current &&
              peerConnectionRef.current.iceConnectionState === 'failed' &&
              socketRef.current?.readyState === WebSocket.OPEN
            ) {
              console.log('🔄 Requesting ICE restart from interviewer...');
              socketRef.current.send(JSON.stringify({ type: 'request_offer' }));
            }
          }, 2000);
        } else if (peerConnection.iceConnectionState === 'checking') {
          setConnectionStatusText('Connecting...');
        } else if (peerConnection.iceConnectionState === 'disconnected') {
          setConnectionStatusText('Reconnecting...');
          setTimeout(() => {
            if (
              peerConnectionRef.current &&
              peerConnectionRef.current.iceConnectionState === 'disconnected' &&
              socketRef.current?.readyState === WebSocket.OPEN
            ) {
              console.log('🔄 ICE disconnected — requesting new offer from interviewer...');
              socketRef.current.send(JSON.stringify({ type: 'request_offer' }));
            }
          }, 3000);
        }
      };

      // Add tracks
      localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
      });

      // Handle incoming tracks
      peerConnection.ontrack = (event) => {
        console.log('🎥 CANDIDATE: Received remote track!', event.track.kind);
        const remoteStream = event.streams[0];
        if (remoteStream && remoteVideoRef.current) {
          remoteVideoRef.current.srcObject = remoteStream;
          remoteVideoRef.current.style.display = 'block';
          remoteVideoRef.current.muted = false;
          remoteVideoRef.current.play().then(() => {
            console.log('✅ Remote video playing');
            setConnectionStatusText('Connected');
          }).catch(e => {
            console.warn('Primary video play failed:', e);
            // Retry play after a short delay
            setTimeout(() => {
              if (remoteVideoRef.current) remoteVideoRef.current.play().catch(err => console.error('Retry failed:', err));
            }, 1000);
          });
        }
      };

      // ICE candidate handler
      peerConnection.onicecandidate = (event) => {
        if (event.candidate && socketRef.current?.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({
            type: 'ice_candidate',
            candidate: event.candidate
          }));
        }
      };

      // Process pending offer if exists
      if (pendingOfferRef.current) {
        console.log('🔄 Processing queued video offer (Candidate side)...');
        await handleVideoOffer(pendingOfferRef.current);
        pendingOfferRef.current = null;
      }

    } catch (error) {
      console.error('❌ Error initializing WebRTC:', error);
      showSessionPopup('Could not access camera/mic. Please check permissions.');
    }
  }, []);


  // Handle video offer
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

  // Handle video answer
  const handleVideoAnswer = useCallback(async (answer) => {
    try {
      await peerConnectionRef.current.setRemoteDescription(new RTCSessionDescription(answer));
    } catch (error) {
      console.error('❌ Error handling video answer:', error);
    }
  }, []);

  // Handle ICE candidate
  const handleIceCandidate = useCallback(async (candidate) => {
    if (!peerConnectionRef.current) return;

    try {
      if (!peerConnectionRef.current.remoteDescription) {
        remoteIceQueueRef.current.push(candidate);
      } else {
        await peerConnectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
      }
    } catch (e) {
      console.warn('⚠️ ICE candidate error:', e);
    }
  }, []);

  // Proxy detection
  const startDetection = useCallback(() => {
    if (streamIntervalRef.current || isDetectionPaused || !cameraReady) return;

    streamIntervalRef.current = setInterval(() => {
      sendFrame();
    }, 1000);
  }, [isDetectionPaused, cameraReady]);

  const stopDetection = useCallback(() => {
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
    }
  }, []);

  const pauseDetection = useCallback(() => {
    if (isDetectionPaused) return;

    setIsDetectionPaused(true);
    stopDetection();

    if (pauseTimeoutRef.current) {
      clearTimeout(pauseTimeoutRef.current);
    }

    pauseTimeoutRef.current = setTimeout(() => {
      setIsDetectionPaused(false);
      if (isCameraOn && cameraReady) {
        startDetection();
      }
    }, 7000);
  }, [isDetectionPaused, isCameraOn, cameraReady, stopDetection, startDetection]);

  const sendFrame = useCallback(() => {
    if (!cameraReady || !isCameraOn || isDetectionPaused || !thumbnailVideoRef.current) return;

    const canvas = document.createElement('canvas');
    canvas.width = thumbnailVideoRef.current.videoWidth || 640;
    canvas.height = thumbnailVideoRef.current.videoHeight || 360;

    if (canvas.width === 0 || canvas.height === 0) return;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(thumbnailVideoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
      if (!blob) return;

      const formData = new FormData();
      formData.append('image', blob, 'frame.jpg');

      fetch('/video_stream/', {
        method: 'POST',
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            const persons = data.persons || 0;
            const gadgets = data.gadgets || [];
            const now = Date.now();

            if (persons > 0) {
              lastPersonDetectedTimeRef.current = now;
              noPersonPopupShownRef.current = false;
            }

            const timeSincePerson = now - lastPersonDetectedTimeRef.current;
            if (persons === 0 && timeSincePerson >= 10000 && !noPersonPopupShownRef.current) {
              registerViolation('No participant detected for 10 seconds. Please stay in frame.');
              noPersonPopupShownRef.current = true;
            }

            if (persons > 1) {
              registerViolation('Multiple people detected');
            }

            if (gadgets.length > 0) {
              registerViolation('Electronic device detected: ' + gadgets.join(', '));
            }
          }
        })
        .catch(err => console.error('Proxy detection error:', err));
    }, 'image/jpeg', 0.8);
  }, [cameraReady, isCameraOn, isDetectionPaused]);

  const registerViolation = useCallback((reason) => {
    const newCount = violationCount + 1;
    setViolationCount(newCount);

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'proxy_violation',
        violation_type: reason,
        violation_count: newCount,
        violation_limit: violationLimit
      }));
    }

    if (newCount >= violationLimit) {
      showPopup('❌ Maximum warnings reached. Interview is ending.');
      endInterviewDueToViolations();
    } else {
      showPopup(`⚠️ Warning ${newCount}/${violationLimit}: ${reason}`);
      pauseDetection();
    }
  }, [violationCount, violationLimit, pauseDetection]);

  const endInterviewDueToViolations = useCallback(() => {
    stopDetection();
    if (pauseTimeoutRef.current) {
      clearTimeout(pauseTimeoutRef.current);
    }

    showPopup('❌ Interview terminated due to violations.');

    // Update interview status
    const candidateToken = sessionId;
    if (candidateToken) {
      fetch('/update-interview-status/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
          token: candidateToken,
          status: 'Terminated',
          reason: `Maximum proxy violations reached (${violationCount}/${violationLimit})`
        })
      });
    }

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'interview_terminated_violations',
        violation_count: violationCount,
        violation_limit: violationLimit,
        reason: 'Maximum proxy violations reached'
      }));
    }

    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
    }

    if (screenShareStreamRef.current) {
      screenShareStreamRef.current.getTracks().forEach(track => track.stop());
      screenShareStreamRef.current = null;
    }

    setTimeout(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.close();
      }
    }, 800);

    setTimeout(() => {
      const thankYouParams = new URLSearchParams({
        token: candidateToken || sessionId || '',
        message: 'Interview has been terminated due to violations. Thank you for your participation.'
      });
      navigate(`/thank-you?${thankYouParams.toString()}`);
    }, 1200);
  }, [violationCount, violationLimit, sessionId, navigate, stopDetection]);

  // Control functions
  const toggleMic = useCallback(() => {
    if (!localStreamRef.current) return;
    const newMuted = !isMuted;
    setIsMuted(newMuted);
    localStreamRef.current.getAudioTracks().forEach(track => (track.enabled = !newMuted));

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'media_state',
        media: 'mic',
        enabled: !newMuted
      }));
    }
  }, [isMuted]);

  const toggleCamera = useCallback(() => {
    if (!localStreamRef.current) return;
    const newCameraOn = !isCameraOn;
    setIsCameraOn(newCameraOn);
    localStreamRef.current.getVideoTracks().forEach(track => (track.enabled = newCameraOn));

    if (thumbnailVideoRef.current) {
      // thumbnailVideoRef.current.style.visibility = newCameraOn ? 'visible' : 'hidden';
      // We control visibility via react state and conditional rendering now
    }

    if (newCameraOn && cameraReady) {
      if (!isDetectionPaused) {
        startDetection();
      }
    } else {
      stopDetection();
    }

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'media_state',
        media: 'camera',
        enabled: newCameraOn
      }));
    }
  }, [isCameraOn, cameraReady, isDetectionPaused, startDetection, stopDetection]);

  const toggleScreenShare = useCallback(async () => {
    if (!isScreenSharing) {
      if (screenShareLocked && screenShareHolder && screenShareHolder !== MY_ROLE) {
        showSessionPopup(`${screenShareHolder} is already sharing their screen.`);
        return;
      }

      const granted = await new Promise((resolve) => {
        pendingScreenShareGrantResolverRef.current = resolve;
        if (socketRef.current?.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ type: 'screen_share_request' }));
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
          showSessionPopup(`${screenShareHolder} is already sharing. Please wait.`);
        }
        return;
      }

      try {
        const screenShareStream = await navigator.mediaDevices.getDisplayMedia({
          video: { displaySurface: 'monitor', cursor: 'always' },
          audio: false
        });

        screenShareStreamRef.current = screenShareStream;
        setIsScreenSharing(true);

        if (peerConnectionRef.current) {
          const videoTrack = screenShareStream.getVideoTracks()[0];
          console.log('🖥️ Candidate replacing track with screen share...');

          const senders = peerConnectionRef.current.getSenders();
          const videoSender = senders.find(s => s.track && s.track.kind === 'video');

          if (videoSender) {
            await videoSender.replaceTrack(videoTrack).then(() => {
              console.log('✅ Candidate screen track successfully replaced');
            }).catch(e => {
              console.error('❌ replaceTrack failed:', e);
            });
          } else {
            console.warn('⚠️ No video sender found to replace track. Adding new track...');
            peerConnectionRef.current.addTrack(videoTrack, screenShareStream);
            // Re-negotiate
            const offer = await peerConnectionRef.current.createOffer();
            await peerConnectionRef.current.setLocalDescription(offer);
            socketRef.current?.send(JSON.stringify({ type: 'video_offer', offer }));
          }
        }

        if (socketRef.current?.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ type: 'screen_share_state', active: true }));
        }

        const videoTrack = screenShareStream.getVideoTracks()[0];
        if (videoTrack) {
          videoTrack.onended = () => stopScreenSharing();
        }
      } catch (error) {
        console.error('Error starting screen share:', error);
        if (socketRef.current?.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ type: 'screen_share_release' }));
        }
      }
    } else {
      stopScreenSharing();
    }
  }, [isScreenSharing, screenShareLocked, screenShareHolder]);

  const stopScreenSharing = useCallback(async () => {
    console.log('🛑 Stopping screen share...');

    if (screenShareStreamRef.current) {
      screenShareStreamRef.current.getTracks().forEach(track => {
        track.stop();
        console.log('✅ Stopped screen share track:', track.kind);
      });
      screenShareStreamRef.current = null;
    }
    setIsScreenSharing(false);

    // Notify backend
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'screen_share_state', active: false }));
      socketRef.current.send(JSON.stringify({ type: 'screen_share_release' }));
      console.log('✅ Notified backend of screen share stop');
    }

    // Restore camera
    try {
      let camTrack = null;
      if (!localStreamRef.current) {
        const camStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        camTrack = camStream.getVideoTracks()[0];
        localStreamRef.current = new MediaStream([camTrack]);
      } else {
        const tracks = localStreamRef.current.getVideoTracks();
        if (!tracks || tracks.length === 0 || tracks[0].readyState !== 'live') {
          const camStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
          camTrack = camStream.getVideoTracks()[0];
          localStreamRef.current.getVideoTracks().forEach(t => localStreamRef.current.removeTrack(t));
          localStreamRef.current.addTrack(camTrack);
        } else {
          camTrack = tracks[0];
        }
      }

      if (camTrack) camTrack.enabled = true;

      if (thumbnailVideoRef.current) {
        thumbnailVideoRef.current.srcObject = localStreamRef.current;
        thumbnailVideoRef.current.style.visibility = 'visible';
      }

      if (peerConnectionRef.current && camTrack) {
        const sender = peerConnectionRef.current.getSenders().find(s => s.track && s.track.kind === 'video');
        if (sender) {
          await sender.replaceTrack(camTrack);
        }
      }
    } catch (err) {
      console.error('Failed to restore camera after screen share:', err);
    }
  }, []);

  // Chat functions
  const sendMessage = useCallback(() => {
    const message = chatInputRef.current?.value.trim();
    if (!message) {
      console.warn('⚠️ Empty message, not sending');
      return;
    }

    if (socketRef.current?.readyState !== WebSocket.OPEN) {
      console.error('❌ WebSocket not open, cannot send message');
      showSessionPopup('Connection lost. Please refresh the page.', 'error');
      return;
    }

    console.log('📤 Sending chat message:', message);

    try {
      socketRef.current.send(JSON.stringify({
        type: 'chat',
        sender: candidateName,
        message: message
      }));

      // Add message to UI immediately
      appendChatMessage(candidateName, message, true);
      chatInputRef.current.value = '';

      console.log('✅ Chat message sent successfully');
    } catch (error) {
      console.error('❌ Error sending chat message:', error);
      showSessionPopup('Failed to send message. Please try again.', 'error');
    }
  }, [candidateName]);

  const appendChatMessage = useCallback((sender, message, isMine) => {
    if (!chatMessagesRef.current) return;

    const div = document.createElement('div');
    div.className = `chat-message ${isMine ? 'mine' : 'theirs'}`;

    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });

    div.innerHTML = `
      <div class="chat-message-header">
        <strong class="chat-message-sender">${sender}</strong>
        <span class="chat-message-time">${timeString}</span>
      </div>
      <div class="chat-message-text">${message}</div>
    `;
    chatMessagesRef.current.appendChild(div);
    chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
  }, []);

  // End interview
  const handleEndInterview = useCallback(() => {
    if (bothPartiesConnected) {
      setSessionExpired(true);
      localStorage.setItem(sessionKey, 'true');
    }

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'screen_share_state', active: false }));
      socketRef.current.send(JSON.stringify({ type: 'screen_share_release' }));
      socketRef.current.send(JSON.stringify({ type: 'end_interview' }));
    }

    setShowThankYou(true);
  }, [bothPartiesConnected, sessionKey]);

  // Submit feedback
  const handleSubmitFeedback = useCallback(() => {
    const feedbackText = feedback.trim();
    if (!feedbackText) {
      alert('Please enter your feedback before submitting.');
      return;
    }

    const candidateToken = sessionId;

    console.log('Submitting candidate feedback with token:', candidateToken);

    if (candidateToken) {
      fetch(`${API_BASE_URL}/submit-interview-feedback/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
          token: candidateToken,
          feedback: feedbackText,
          role: 'candidate'
        })
      })
        .then(response => response.json())
        .then(data => {
          console.log('Feedback submission response:', data);
          if (data.success) {
            setShowThankYou(false);
            setShowFinalThankYou(true);
            setTimeout(() => {
              const thankYouParams = new URLSearchParams({
                token: candidateToken,
                message: 'Thank you for your feedback. Your interview has been completed successfully.'
              });
              navigate(`/thank-you?${thankYouParams.toString()}`);
            }, 3000);
          } else {
            console.error('Failed to submit feedback:', data);
            alert(`Failed to submit feedback: ${data.error || 'Unknown error'}`);
          }
        })
        .catch(error => {
          console.error('Error submitting feedback:', error);
          alert('Error submitting feedback. Please check console for details.');
        });
    } else {
      alert('Session token is missing. Cannot submit feedback.');
    }
  }, [feedback, sessionId, navigate]);

  // Draggable Video Logic
  const handleDragStart = (e) => {
    if (selfVideoContainerRef.current) {
      const rect = selfVideoContainerRef.current.getBoundingClientRect();
      setDragOffset({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
      setIsDragging(true);
    }
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging && selfVideoContainerRef.current) {
        e.preventDefault();
        const container = selfVideoContainerRef.current;
        const parent = container.parentElement;
        if (!parent) return;

        const parentRect = parent.getBoundingClientRect();
        const newLeft = e.clientX - parentRect.left - dragOffset.x;
        const newTop = e.clientY - parentRect.top - dragOffset.y;

        // Constraints
        const maxLeft = parentRect.width - container.offsetWidth;
        const maxTop = parentRect.height - container.offsetHeight;

        container.style.left = `${Math.max(0, Math.min(newLeft, maxLeft))}px`;
        container.style.top = `${Math.max(0, Math.min(newTop, maxTop))}px`;
        container.style.bottom = 'auto';
        container.style.right = 'auto';
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);


  const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopDetection();
      if (pauseTimeoutRef.current) {
        clearTimeout(pauseTimeoutRef.current);
      }
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (screenShareStreamRef.current) {
        screenShareStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [stopDetection]);

  // Page visibility and security
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        showPopup('⚠️ Tab switching detected. Please stay on this page.');
        registerViolation('Tab switching detected');
      }
    };

    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && (
        e.key === 'c' || e.key === 'v' || e.key === 'a' || e.key === 'z' ||
        e.key === 'y' || e.key === 'f' || e.key === 'p' || e.key === 's' ||
        e.key === 'u' || e.key === 'i' || e.key === 'j' || e.key === 'k'
      )) {
        e.preventDefault();
        showPopup('⚠️ Keyboard shortcuts are disabled during interview.');
        registerViolation('Keyboard shortcut attempted');
      }

      if (e.key === 'F12' || e.key === 'F11' || e.key === 'F10' || e.key === 'F9') {
        e.preventDefault();
        showPopup('⚠️ Function keys are disabled during interview.');
        registerViolation('Function key attempted');
      }
    };

    const handleContextMenu = (e) => {
      e.preventDefault();
      showPopup('⚠️ Right-click is disabled during interview.');
      registerViolation('Right-click attempted');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('contextmenu', handleContextMenu);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('contextmenu', handleContextMenu);
    };
  }, [showPopup, registerViolation]);

  // Handle chat input enter key
  useEffect(() => {
    const chatInput = chatInputRef.current;
    if (!chatInput) return;

    const handleKeyPress = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
      }
    };

    chatInput.addEventListener('keypress', handleKeyPress);
    return () => chatInput.removeEventListener('keypress', handleKeyPress);
  }, [sendMessage]);

  if (sessionExpired && !showThankYou && !showFinalThankYou) {
    return (
      <div className="session-expired-modal">
        <div className="session-expired-content">
          <div className="session-expired-icon">
            <i className="fas fa-clock" aria-hidden="true"></i>
          </div>
          <h3 className="session-expired-title">Session Completed</h3>
          <p className="session-expired-message">
            This interview session has already been completed. You cannot rejoin the interview.
          </p>
          <button onClick={() => {
            navigate('/');
            window.location.reload();
          }} className="btn-close-window">Close</button>
        </div>
      </div>
    );
  }

  if (showFinalThankYou) {
    return (
      <div className="thank-you-screen">
        <div className="thank-you-content">
          <i className="fas fa-heart thank-you-icon heart" aria-hidden="true"></i>
          <h2 className="thank-you-title">Thank You!</h2>
          <p className="thank-you-subtitle">Your feedback has been submitted successfully.</p>
          <p className="thank-you-note">You may now close this window.</p>
        </div>
      </div>
    );
  }

  if (showThankYou) {
    return (
      <div className="thank-you-screen">
        <div className="thank-you-content">
          <i className="fas fa-check-circle thank-you-icon check" aria-hidden="true"></i>
          <h2 className="thank-you-title">Interview Completed!</h2>
          <p className="thank-you-subtitle">Thank you for participating in the interview.</p>
          <div className="feedback-form">
            <h3 className="feedback-form-title">Quick Feedback</h3>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="How was your interview experience?"
              className="feedback-textarea"
              rows="4"
            />
            <button onClick={handleSubmitFeedback} className="btn-submit-feedback">
              Submit Feedback
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`live-interview ${chatPanelVisible ? 'chat-active' : ''}`}>
      {/* Header */}
      <header className="live-interview-header">
        <div className="header-left">
          <h1>Live Interview</h1>
        </div>
        <div className="header-controls">
          <div className="timer">{timer}</div>
        </div>
      </header>

      {/* Main Content */}
      <div className="main-wrapper">
        <div className="video-container">

          {/* Main Remote Video (Interviewer) */}
          <video
            ref={remoteVideoRef}
            className="remote-video full"
            autoPlay
            playsInline
            muted={false}
            onContextMenu={e => e.preventDefault()}
            style={{ display: (isRemoteCameraOn || isRemoteScreenSharing) ? 'block' : 'none' }}
          />

          {!isRemoteCameraOn && bothPartiesConnected && (
            <div className="remote-video-placeholder" style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
              <VideoPlaceholder name={interviewerName} />
            </div>
          )}


          {/* Connection Status Overlay */}
          {connectionStatus !== 'Connected' && (
            <div className="connection-overlay">
              <i className="fas fa-spinner spinner"></i>
              <h3>{connectionStatusText}</h3>
            </div>
          )}

          {/* Name Label for Interviewer */}
          {bothPartiesConnected && (
            <div className="video-label" style={{ top: '20px', left: '20px', bottom: 'auto' }}>
              <span>{interviewerName}</span>
              <i className="fas fa-microphone" style={{ fontSize: '12px', marginLeft: '6px' }}></i>
            </div>
          )}

          {/* Local Video (Self View) - Draggable */}
          <div
            className="self-video-container floating"
            ref={selfVideoContainerRef}
            onMouseDown={handleDragStart}
          >
            <video
              ref={thumbnailVideoRef}
              className="self-video"
              autoPlay
              muted
              playsInline
              style={{ display: isCameraOn ? 'block' : 'none' }}
            />
            {!isCameraOn && (
              <div style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}>
                <VideoPlaceholder name="You" width="100%" height="100%" />
              </div>
            )}
            <div className="video-label">
              <span>{candidateName} (You)</span>
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

          <div
            className="chat-messages"
            ref={chatMessagesRef}
          >
            {/* Messages are appended via DOM manipulation in appendChatMessage, 
                 but keeping ref here is key. 
                 To fully support React rendering we'd map state, but 
                 we will keep existing DOM append logic for minimal refactor risk,
                 just ensuring container matches. 
             */}
          </div>

          <div className="chat-input-area">
            <input
              ref={chatInputRef}
              type="text"
              placeholder="Type a message..."
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            />
            <button className="btn-send" onClick={sendMessage}>
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
            onClick={toggleMic}
            title={isMuted ? "Unmute" : "Mute"}
          >
            <div className="icon-circle">
              <i className={`fas fa-microphone${isMuted ? '-slash' : ''}`}></i>
            </div>
            <span className="control-label">{isMuted ? "Unmute" : "Mute"}</span>
          </button>

          <button
            className={`control-btn ${isCameraOn ? 'active' : 'off'}`}
            onClick={toggleCamera}
            title={isCameraOn ? "Stop Video" : "Start Video"}
          >
            <div className="icon-circle">
              <i className={`fas fa-video${!isCameraOn ? '-slash' : ''}`}></i>
            </div>
            <span className="control-label">{isCameraOn ? "Stop Video" : "Start Video"}</span>
          </button>

          <button
            className={`control-btn screen-share ${isScreenSharing ? 'active' : ''}`}
            onClick={toggleScreenShare}
            title="Share Screen"
            disabled={screenShareLocked && screenShareHolder !== MY_ROLE}
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
            Leave
          </button>
        </div>
      </div>

      {/* Proxy Notifications */}
      <div className="proxy-notification-container" id="popupContainer">
        {/* Popups are appended here by showPopup logic */}
      </div>

    </div >
  );
}

export default LiveInterview;