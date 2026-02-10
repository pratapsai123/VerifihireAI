import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import '../styles/LiveInterview.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

function LiveInterview() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('token') || 'default-session';
  
  // State management
  const [interviewType, setInterviewType] = useState('Live');
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
  const [statusPanelVisible, setStatusPanelVisible] = useState(false);
  const [chatUnreadCount, setChatUnreadCount] = useState(0);
  const [showThankYou, setShowThankYou] = useState(false);
  const [showFinalThankYou, setShowFinalThankYou] = useState(false);
  const [feedback, setFeedback] = useState('');
  
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
  const thumbnailVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const remoteVideoBackupRef = useRef(null);
  const screenShareVideoRef = useRef(null);
  const chatMessagesRef = useRef(null);
  const chatInputRef = useRef(null);
  const startTimeRef = useRef(Date.now());
  const streamIntervalRef = useRef(null);
  const pauseTimeoutRef = useRef(null);
  const lastPersonDetectedTimeRef = useRef(Date.now());
  const noPersonPopupShownRef = useRef(false);
  const pendingScreenShareGrantResolverRef = useRef(null);
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
    const apiUrl = API_BASE_URL.replace('/api', '').replace('http://', '').replace('https://', '');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // Try backend URL first, then fallback to current host
    const hosts = [];
    if (apiUrl && apiUrl !== 'localhost:8001') {
      hosts.push(apiUrl);
    }
    hosts.push(window.location.host);
    hosts.push(window.location.hostname);
    const bare = window.location.hostname.replace(/^www\./, '');
    if (!hosts.includes(bare)) hosts.push(bare);
    if (!hosts.includes(`www.${bare}`)) hosts.push(`www.${bare}`);
    
    const paths = [
      `/ws/interview/${sessionId}/candidate/`,
      `/ws/interview/${sessionId}/candidate`,
    ];
    const candidates = [];
    for (const h of hosts) for (const p of paths) candidates.push(`${protocol}//${h}${p}`);
    
    let socket;
    let idx = 0;
    let heartbeatInterval;
    
    const tryNext = () => {
      if (idx >= candidates.length) {
        console.error('❌ All WS candidates failed');
        return;
      }
      const url = candidates[idx++];
      console.log('🔌 Connecting WS', url);
      
      try {
        socket = new WebSocket(url);
      } catch (e) {
        console.warn('WS ctor failed', e);
        return setTimeout(tryNext, 1500);
      }
      
      socket.addEventListener('error', () => setTimeout(tryNext, 1500));
      
      socket.addEventListener('open', () => {
        console.log('✅ WebSocket connected successfully!');
        socketRef.current = socket;
        setConnectionEstablished(true);
        setConnectionStatus('Connected');
        setConnectionStatusText('Ready for connection');
        
        // Heartbeat
        heartbeatInterval = setInterval(() => {
          try {
            socket.send(JSON.stringify({ type: 'client_ping', ts: Date.now() }));
          } catch {}
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
          if (data.sender !== candidateName && peerConnectionRef.current) {
            handleVideoOffer(data.offer);
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
            // Someone else is sharing
            if (data.active) {
              showSessionPopup(`${data.sender || 'Interviewer'} started screen sharing`);
            } else {
              showSessionPopup(`${data.sender || 'Interviewer'} stopped screen sharing`);
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
  
  // User joined handler
  const handleUserJoined = useCallback((data) => {
    const joinedUserName = data.user === 'Interviewer' ? interviewerName : data.user;
    showSessionPopup(`${joinedUserName} joined the session`);
    
    if (String(data.user).toLowerCase() === 'interviewer' && 
        String(candidateName).toLowerCase() === candidateName.toLowerCase() && 
        peerConnectionRef.current) {
      console.log('🎯 Interviewer joined, creating video offer...');
      createVideoOffer();
      setBothPartiesConnected(true);
      setSessionExpired(true);
      localStorage.setItem(sessionKey, 'true');
    }
  }, [candidateName, interviewerName, sessionKey]);
  
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
          showSessionPopup('Connection failed. Waiting for interviewer...');
          setTimeout(() => {
            if (peerConnectionRef.current && peerConnectionRef.current.connectionState === 'failed') {
              initializeWebRTC();
            }
          }, 3000);
        }
      };
      
      peerConnection.oniceconnectionstatechange = () => {
        console.log('🧊 ICE connection state:', peerConnection.iceConnectionState);
        if (peerConnection.iceConnectionState === 'connected') {
          setConnectionStatusText('Connected');
        } else if (peerConnection.iceConnectionState === 'failed') {
          setConnectionStatusText('Connection failed - retrying...');
          setTimeout(() => {
            if (peerConnectionRef.current && peerConnectionRef.current.iceConnectionState === 'failed') {
              initializeWebRTC();
            }
          }, 5000);
        } else if (peerConnection.iceConnectionState === 'checking') {
          setConnectionStatusText('Connecting...');
        } else if (peerConnection.iceConnectionState === 'disconnected') {
          setConnectionStatusText('Reconnecting...');
          setTimeout(() => {
            if (peerConnectionRef.current && peerConnectionRef.current.iceConnectionState === 'disconnected') {
              initializeWebRTC();
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
            if (remoteVideoBackupRef.current) {
              remoteVideoBackupRef.current.srcObject = remoteStream;
              remoteVideoBackupRef.current.style.display = 'block';
              remoteVideoBackupRef.current.muted = false;
              remoteVideoBackupRef.current.play();
            }
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
      
    } catch (error) {
      console.error('❌ Error initializing WebRTC:', error);
      showSessionPopup('Could not access camera/mic. Please check permissions.');
    }
  }, []);
  
  // Create video offer
  const createVideoOffer = useCallback(async () => {
    try {
      const offer = await peerConnectionRef.current.createOffer();
      await peerConnectionRef.current.setLocalDescription(offer);
      socketRef.current?.send(JSON.stringify({
        type: 'video_offer',
        offer: offer
      }));
    } catch (error) {
      console.error('Error creating video offer:', error);
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
      thumbnailVideoRef.current.style.visibility = newCameraOn ? 'visible' : 'hidden';
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
          const sender = peerConnectionRef.current.getSenders().find(s =>
            s.track && s.track.kind === 'video'
          );
          if (sender) {
            await sender.replaceTrack(videoTrack);
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
    if (candidateToken) {
      fetch('/submit-interview-feedback/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
          token: candidateToken,
          feedback: feedbackText
        })
      })
      .then(response => response.json())
      .then(data => {
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
          alert('Failed to submit feedback. Please try again.');
        }
      })
      .catch(error => {
        console.error('Error submitting feedback:', error);
        alert('Error submitting feedback. Please try again.');
      });
    }
  }, [feedback, sessionId, navigate]);
  
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
  
  const showSessionExpiredMessage = useCallback(() => {
    const popup = document.createElement('div');
    popup.className = 'session-expired-modal';
    popup.innerHTML = `
      <div class="session-expired-content">
        <div class="session-expired-icon">
          <i class="fas fa-clock" aria-hidden="true"></i>
        </div>
        <h3 class="session-expired-title">Session Completed</h3>
        <p class="session-expired-message">This interview session has already been completed. You cannot rejoin the interview.</p>
        <button onclick="window.close()" class="btn-close-window">Close</button>
      </div>
    `;
    document.body.appendChild(popup);
  }, []);
  
  const redirectToThankYou = useCallback(() => {
    const token = sessionId;
    navigate(`/thank-you?token=${encodeURIComponent(token)}`);
  }, [sessionId, navigate]);
  
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
          <button onClick={() => window.close()} className="btn-close-window">Close</button>
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
    <div id="meetingScreen" className="container-full">
      {/* Header */}
      <header className="header" role="banner">
        <div className="header-content">
          <div className="header-left">
            <div className="header-title">
              <span className="title-text">FDI Interview</span>
              <span className="subtitle-text">| {interviewType} Interview</span>
            </div>
            <div className="session-info">
              <span>Session: </span>
              <span className="session-id">{sessionId}</span>
            </div>
          </div>
          <div className="header-right">
            <div className="timer-container">
              <span id="timer" className="timer" role="timer">{timer}</span>
            </div>
            <button
              id="endInterviewButton"
              className="btn-end-interview"
              onClick={handleEndInterview}
              aria-label="End interview session"
            >
              <i className="fas fa-phone-slash" aria-hidden="true"></i>
              <span className="mr-1"></span>
              End Interview
            </button>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <div className="main-content" role="main">
        {/* Main Video Container */}
        <div id="videoMainContainer" className="video-stage" role="region" aria-label="Video conference area">
          <video
            ref={remoteVideoRef}
            id="remoteVideo"
            className="video-full"
            autoPlay
            playsInline
            muted={false}
            aria-label="Remote participant video"
          />
          <video
            ref={remoteVideoBackupRef}
            id="remoteVideoBackup"
            className="video-full"
            autoPlay
            playsInline
            muted={false}
            style={{ display: 'none' }}
            aria-label="Remote participant video backup"
          />
          
          <div id="connectionStatusOverlay" className="absolute top-4 left-4 bg-black bg-opacity-70 text-white px-3 py-2 rounded-lg text-sm">
            <span>{connectionStatusText}</span>
          </div>
          
          <video
            ref={screenShareVideoRef}
            id="screenShareVideo"
            className="video-full"
            autoPlay
            style={{ display: 'none', objectFit: 'contain' }}
            aria-label="Shared screen content"
          />
          
          <div id="thumbnailContainer" className="meeting-video-thumbnail">
            <video
              ref={thumbnailVideoRef}
              id="thumbnailVideo"
              className="w-full h-full object-cover"
              autoPlay
              muted
              aria-label="Your video"
            />
            <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-sm px-2 py-1 rounded">
              {candidateName}
            </div>
          </div>
          
          <div className="absolute top-4 right-4 bg-black bg-opacity-50 text-white text-sm px-3 py-1 rounded-lg">
            {interviewerName}
          </div>
        </div>
        
        {/* Chat Panel */}
        {chatPanelVisible && (
          <div id="chatPanel" className="chat-panel" role="complementary" aria-label="Chat panel">
            <div className="chat-header">
              <h3 className="chat-title">Interview Chat</h3>
            </div>
            <div className="chat-body">
              <div
                ref={chatMessagesRef}
                id="chatMessages"
                className="chat-messages"
                role="log"
                aria-live="polite"
              />
              <div className="chat-input-container">
                <div className="chat-input-wrapper">
                  <input
                    ref={chatInputRef}
                    type="text"
                    id="chatInput"
                    placeholder="Type your message..."
                    className="chat-input"
                    aria-label="Type chat message"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        sendMessage();
                      }
                    }}
                  />
                  <button
                    id="sendChatBtn"
                    className="btn-send-chat"
                    onClick={(e) => {
                      e.preventDefault();
                      sendMessage();
                    }}
                    aria-label="Send message"
                    type="button"
                  >
                    <i className="fas fa-paper-plane" aria-hidden="true"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Status Panel */}
        {statusPanelVisible && (
          <div id="statusPanel" className="status-panel" role="complementary" aria-label="Connection status panel">
            <h3 className="status-title">Status</h3>
            <div className="status-items">
              <div className="status-item">
                <span className="status-label">Your Mic:</span>
                <span className={`status-value ${isMuted ? 'red' : 'green'}`}>
                  {isMuted ? 'Off' : 'On'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Your Camera:</span>
                <span className={`status-value ${isCameraOn ? 'green' : 'red'}`}>
                  {isCameraOn ? 'On' : 'Off'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Connection:</span>
                <span className={`status-value ${connectionStatus === 'Connected' ? 'green' : 'red'}`}>
                  {connectionStatus}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Control Bar */}
      <div className="control-bar" role="toolbar" aria-label="Meeting controls">
        <button
          id="micButtonMeetingBottom"
          title="Toggle microphone"
          className="control-button"
          onClick={toggleMic}
          aria-label="Toggle microphone"
          aria-pressed={!isMuted}
        >
          <div className={`control-icon ${isMuted ? 'active' : ''}`}>
            <i className={`fas ${isMuted ? 'fa-microphone-slash' : 'fa-microphone'}`} aria-hidden="true"></i>
          </div>
          <span className="control-label">Mic</span>
        </button>
        <button
          id="cameraButtonMeetingBottom"
          title="Toggle camera"
          className="control-button"
          onClick={toggleCamera}
          aria-label="Toggle camera"
          aria-pressed={isCameraOn}
        >
          <div className={`control-icon ${!isCameraOn ? 'active' : ''}`}>
            <i className={`fas ${isCameraOn ? 'fa-video' : 'fa-video-slash'}`} aria-hidden="true"></i>
          </div>
          <span className="control-label">Video</span>
        </button>
        <button
          id="shareScreenButtonBottom"
          title="Share screen"
          className="control-button"
          onClick={toggleScreenShare}
          disabled={screenShareLocked && screenShareHolder !== MY_ROLE}
          aria-label="Share screen"
          aria-pressed={isScreenSharing}
        >
          <div className={`control-icon ${isScreenSharing ? 'active' : ''}`}>
            <i className={`fas ${isScreenSharing ? 'fa-stop-circle' : 'fa-desktop'}`} aria-hidden="true"></i>
          </div>
          <span className="control-label">Share</span>
        </button>
        <button
          id="statusPanelToggle"
          title="Status"
          className="control-button"
          onClick={() => setStatusPanelVisible(!statusPanelVisible)}
          aria-label="Toggle status panel"
        >
          <div className="control-icon">
            <i className="fas fa-signal" aria-hidden="true"></i>
          </div>
          <span className="control-label">Status</span>
        </button>
        <button
          id="chatPanelToggle"
          title="Chat"
          className="control-button"
          onClick={() => {
            setChatPanelVisible(!chatPanelVisible);
            if (chatPanelVisible) {
              setChatUnreadCount(0);
            }
          }}
          aria-label="Toggle chat panel"
          style={{ position: 'relative' }}
        >
          <div className="control-icon">
            <i className="fas fa-comments" aria-hidden="true"></i>
          </div>
          <span className="control-label">Chat</span>
          {chatUnreadCount > 0 && (
            <span className="unread-badge" aria-label="Unread messages">
              {chatUnreadCount}
            </span>
          )}
        </button>
      </div>
      
      {/* Floating Stop Sharing */}
      {isScreenSharing && (
        <div id="floatingStopShare" className="floating-stop-share">
          <button
            id="stopShareFloatingBtn"
            className="btn-stop-sharing"
            onClick={stopScreenSharing}
            aria-label="Stop sharing screen"
          >
            <i className="fas fa-stop-circle" aria-hidden="true"></i>
            <span className="mr-1"></span> Stop Sharing
          </button>
        </div>
      )}
      
      {/* Popup Container */}
      <div id="popupContainer" aria-live="assertive" aria-atomic="true"></div>
    </div>
  );
}

export default LiveInterview;
