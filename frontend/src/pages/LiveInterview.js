import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import '../styles/LiveInterview.css';

import { API_BASE_URL } from '../apiConfig';
import { useWebSocket } from '../hooks/useWebSocket';
import { useWebRTC } from '../hooks/useWebRTC';
import { useScreenShare } from '../hooks/useScreenShare';
import MalpracticeMonitor from '../components/LiveInterview/MalpracticeMonitor';

import VideoPanel from '../components/LiveInterview/VideoPanel';
import ChatPanel from '../components/LiveInterview/ChatPanel';
import ControlBar from '../components/LiveInterview/ControlBar';
import ConnectionOverlay from '../components/LiveInterview/ConnectionOverlay';
import ErrorBoundary from '../components/LiveInterview/ErrorBoundary';
import LiveInterviewLobby from '../components/LiveInterview/LiveInterviewLobby';

function LiveInterview() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const participantToken = searchParams.get('participant_token');
  const [sessionId, setSessionId] = useState(searchParams.get('token') || searchParams.get('session') || searchParams.get('sessionId') || 'default-session');

  const MY_ROLE = 'Candidate';
  const role = 'candidate';
  const sessionKey = `session_expired_${sessionId}`;

  const [candidateName, setCandidateName] = useState('Candidate');
  const [interviewerName, setInterviewerName] = useState('Interviewer');

  const [showLobby, setShowLobby] = useState(true);
  const [lobbyConfig, setLobbyConfig] = useState({
    cameraOn: true,
    micOn: true,
    videoDeviceId: null,
    audioDeviceId: null,
    speakerDeviceId: null
  });

  const handleLobbyJoin = (config) => {
    setLobbyConfig(config);
    setShowLobby(false);
  };

  // Load interview details
  useEffect(() => {
    const loadDetails = async () => {
      try {
        if (participantToken) {
          const axios = (await import('axios')).default;
          const resp = await axios.get(`${API_BASE_URL}/interviews/participants/validate/${participantToken}/`);
          if (resp.data) {
            setSessionId(resp.data.session_id);
            setCandidateName(resp.data.name || 'Candidate');
            setInterviewerName(resp.data.interviewer_name || 'Interviewer');
          }
        }
      } catch (error) {
        console.warn('Could not load interview details:', error);
      }
    };
    loadDetails();
  }, [participantToken]);

  const [sessionExpired, setSessionExpired] = useState(false);
  const [isWaiting, setIsWaiting] = useState(false);
  const [bothPartiesConnected, setBothPartiesConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isCameraOn, setIsCameraOn] = useState(true);
  const [isRemoteCameraOn, setIsRemoteCameraOn] = useState(true);
  const [isRemoteScreenSharing, setIsRemoteScreenSharing] = useState(false);

  const [chatPanelVisible, setChatPanelVisible] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatUnreadCount, setChatUnreadCount] = useState(0);

  const [showThankYou, setShowThankYou] = useState(false);
  const [showFinalThankYou, setShowFinalThankYou] = useState(false);
  const [feedback, setFeedback] = useState('');

  const [timer, setTimer] = useState('00:00:00');
  const startTimeRef = useRef(Date.now());
  const [cameraReady, setCameraReady] = useState(false);
  const candidateReadyRef = useRef(false);
  const interviewerReadyRef = useRef(false);
  const hasRequestedOfferRef = useRef(false);

  const [notifications, setNotifications] = useState([]);

  const [remoteParticipants, setRemoteParticipants] = useState({}); // { userId: { stream, role, name, isCameraOn, isScreenSharing } }
  const [myUserId, setMyUserId] = useState(null);
  // 🔥 FIX: Ref that is always synchronously up-to-date — safe to use inside handleMessage closures
  const myUserIdRef = useRef(null);
  // 🔥 FIX: Ref mirror of remoteParticipants so initializeMedia always reads fresh data
  const remoteParticipantsRef = useRef({});

  const closeCandidateTab = useCallback(() => {
    try {
      window.open('', '_self');
      window.close();
    } catch (e) {
      // ignore and use fallback below
    }
    setTimeout(() => {
      // Fallback for browsers that block window.close on non-script-opened tabs
      if (!window.closed) {
        window.location.replace('about:blank');
      }
    }, 120);
  }, []);

  // Check if session is expired
  useEffect(() => {
    if (localStorage.getItem(sessionKey) === 'true') {
      setSessionExpired(true);
    }
  }, [sessionKey]);

  useEffect(() => {
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTimeRef.current;
      const hours = Math.floor(elapsed / 3600000);
      const minutes = Math.floor((elapsed % 3600000) / 60000);
      const seconds = Math.floor((elapsed % 60000) / 1000);
      setTimer(`${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const showSessionPopup = useCallback((message, severity = 'info') => {
    const id = Date.now() + Math.random();
    setNotifications(prev => [...prev, { id, message, severity }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 4000);
  }, []);

  const sendMessageRef = useRef(null);
  const stableSendMessage = useCallback((data) => {
    if (sendMessageRef.current) sendMessageRef.current(data);
  }, []);

  const {
    peerConnectionsRef, localStreamRef, remoteStreamsRef,
    createPeerConnection, removePeerConnection, initLocalStream,
    createVideoOffer, handleVideoOffer, handleVideoAnswer, handleIceCandidate, stopWebRTC
  } = useWebRTC(stableSendMessage, myUserId);

  const {
    isScreenSharing, screenShareLocked, setScreenShareLocked, screenShareHolder, setScreenShareHolder,
    toggleScreenShare, stopScreenSharing, handleScreenShareGranted, handleScreenShareDenied, screenShareStreamRef
  } = useScreenShare(peerConnectionsRef, localStreamRef, stableSendMessage, showSessionPopup, MY_ROLE, createVideoOffer);

  const handleEndInterview = useCallback(() => {
    stableSendMessage({ type: 'end_interview' });
    setShowThankYou(true);
    stopWebRTC();
  }, [stableSendMessage, stopWebRTC]);

  // Message Handler
  const handleMessage = useCallback((data) => {
    console.log('Received message:', data);
    switch (data.type) {
      case 'session_info':
        if (data.start_time) startTimeRef.current = new Date(data.start_time).getTime();
        if (data.user_id) {
          // 🔥 FIX: Set BOTH the ref (synchronously) and the state (for renders)
          myUserIdRef.current = data.user_id;
          setMyUserId(data.user_id);
        }
        break;
      case 'existing_participants':
        console.log(`👥 ${data.participants.length} existing participants found`);
        data.participants.forEach(p => {
          if (p.user_id !== myUserIdRef.current) {
            const entry = {
              name: p.name || 'Participant',
              role: p.role,
              isCameraOn: p.is_camera_on !== false,
              isMuted: p.is_muted || false,
              stream: null,
              joinedAt: p.joined_at || Date.now()
            };
            remoteParticipantsRef.current = { ...remoteParticipantsRef.current, [p.user_id]: entry };
            setRemoteParticipants(prev => ({ ...prev, [p.user_id]: entry }));

            // 🔥 FIX: Only create peer+offer NOW if local stream is already ready
            if (localStreamRef.current) {
              console.log(`🚀 Local stream ready — connecting immediately to ${p.user_id}`);
              const screenStream = isScreenSharing ? screenShareStreamRef.current : null;
              createPeerConnection(p.user_id, (userId, stream) => {
                handleRemoteStream(userId, stream);
              }, [screenStream]);
              createVideoOffer(p.user_id);
            } else {
              console.log(`⏳ Local stream not ready yet — deferring connection to ${p.user_id}`);
            }
          }
        });
        break;
      case 'user_joined':
        showSessionPopup(`${data.user} joined the session`);
        setBothPartiesConnected(true);
        setRemoteParticipants(prev => {
          const entry = {
            ...(prev[data.user_id] || {}),
            name: data.user || 'Participant',
            role: data.role,
            isCameraOn: true,
            stream: prev[data.user_id]?.stream || null,
            joinedAt: Date.now()
          };
          remoteParticipantsRef.current = { ...remoteParticipantsRef.current, [data.user_id]: entry };
          return { ...prev, [data.user_id]: entry };
        });
        break;
      case 'user_left':
        showSessionPopup(`${data.user} left the session`, 'warning');
        setRemoteParticipants(prev => {
          const next = { ...prev };
          delete next[data.user_id];
          delete remoteParticipantsRef.current[data.user_id];
          return next;
        });
        removePeerConnection(data.user_id);
        break;
      case 'chat':
        if (data.sender_id !== myUserIdRef.current) {
          setChatMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            sender: data.sender || 'Participant',
            text: data.message,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            isMine: false
          }]);
          if (!chatPanelVisible) setChatUnreadCount(c => c + 1);
        }
        break;
      case 'ready_for_webrtc': {
        console.log(`✅ ready_for_webrtc from ${data.sender_id}`);
        const remoteUserId = data.sender_id;

        if (remoteUserId === myUserIdRef.current) break;

        // 🔥 FIX: Check both iceConnectionState AND live remote tracks
        const existingPc = peerConnectionsRef.current[remoteUserId];
        if (existingPc) {
          const hasRemoteTracks = existingPc.getReceivers().some(r => r.track && r.track.readyState === 'live');
          const isHealthy = ['connected', 'completed'].includes(existingPc.iceConnectionState) && hasRemoteTracks;
          if (isHealthy) {
            console.log(`⚠️ Healthy peer with live tracks for ${remoteUserId}, skipping.`);
            break;
          }
          console.log(`🧹 Stale/empty peer for ${remoteUserId} (ice=${existingPc.iceConnectionState}, hasTracks=${hasRemoteTracks}), recreating.`);
        }

        setRemoteParticipants(prev => {
          const entry = {
            ...(prev[remoteUserId] || {}),
            name: data.user || prev[remoteUserId]?.name || 'Participant',
            role: data.role || prev[remoteUserId]?.role,
            stream: null,
            joinedAt: prev[remoteUserId]?.joinedAt || Date.now()
          };
          remoteParticipantsRef.current = { ...remoteParticipantsRef.current, [remoteUserId]: entry };
          return { ...prev, [remoteUserId]: entry };
        });

        console.log(`🚀 Creating peer for ${remoteUserId}`);
        const currentScreenStream = isScreenSharing ? screenShareStreamRef.current : null;
        createPeerConnection(remoteUserId, (userId, stream) => {
          handleRemoteStream(userId, stream);
        }, [currentScreenStream]);
        createVideoOffer(remoteUserId);
        break;
      }
      case 'video_offer':
        if (data.target === myUserIdRef.current) {
          const currentScreenStream = isScreenSharing ? screenShareStreamRef.current : null;
          handleVideoOffer(data.sender_id, data.sdp, (userId, stream) => {
            handleRemoteStream(userId, stream);
          }, [currentScreenStream]);
        }
        break;
      case 'video_answer':
        if (data.target === myUserIdRef.current) {
          handleVideoAnswer(data.sender_id, data.sdp);
        }
        break;
      case 'ice_candidate':
        if (data.target === myUserIdRef.current) {
          handleIceCandidate(data.sender_id, data.candidate);
        }
        break;
      case 'media_state':
        // 🔥 Safety check: ensure sender_id exists and we already have this participant
        if (data.sender_id && data.sender_id !== myUserIdRef.current && remoteParticipantsRef.current[data.sender_id]) {
          setRemoteParticipants(prev => ({
            ...prev,
            [data.sender_id]: {
              ...prev[data.sender_id],
              isCameraOn: data.media === 'camera' ? data.enabled : prev[data.sender_id]?.isCameraOn,
              isMuted: data.media === 'mic' ? !data.enabled : prev[data.sender_id]?.isMuted
            }
          }));
        }
        break;
      case 'screen_share_state':
        if (data.sender_id !== myUserIdRef.current) {
          setRemoteParticipants(prev => {
            const p = prev[data.sender_id];
            const updated = {
              ...p,
              isScreenSharing: !!data.active,
              screenStreamId: data.active ? data.streamId : null
            };
            // If stopped, cleanup screen stream
            if (!data.active) updated.screenStream = null;

            remoteParticipantsRef.current = { ...remoteParticipantsRef.current, [data.sender_id]: updated };
            return { ...prev, [data.sender_id]: updated };
          });
        }
        break;
      case 'screen_share_lock':
        setScreenShareLocked(!!data.active);
        setScreenShareHolder(data.active ? data.holder : null);
        break;
      case 'screen_share_granted':
        handleScreenShareGranted();
        break;
      case 'screen_share_denied':
        handleScreenShareDenied();
        break;
      case 'screen_share_release':
        setScreenShareLocked(false);
        setScreenShareHolder(null);
        break;
      case 'end_interview':
        setShowThankYou(true);
        stopWebRTC();
        break;
      case 'interview_terminated_violations':
        navigate(`/interview-terminated?session_id=${sessionId}&reason=${data.reason || 'Multiple violations'}`);
        break;
      case 'session_expired':
        if (data.reason === 'not_started') {
          setIsWaiting(true);
        } else {
          showSessionPopup(data.message || 'Session expired or already completed.', 'error');
          setSessionExpired(true);
          localStorage.setItem(sessionKey, 'true');
        }
        break;
      default: break;
    }
  }, [myUserId, chatPanelVisible, sessionId, sessionKey, showSessionPopup, createPeerConnection, createVideoOffer, handleVideoOffer, handleVideoAnswer, handleIceCandidate, stopWebRTC, navigate, handleScreenShareGranted]);


  // 🔥 Centralized Stream Router
  const handleRemoteStream = useCallback((userId, stream) => {
    setRemoteParticipants(prev => {
      const p = prev[userId];
      if (!p) return prev;

      // Identification Logic:
      // 1. If ID matches signaled screenStreamId
      // 2. If track is video-only (screen share usually has no audio in this app)
      // 3. If we already have a primary stream and this is a new one
      const signaledIdMatch = p.screenStreamId === stream.id;
      const isVideoOnly = stream.getAudioTracks().length === 0 && stream.getVideoTracks().length > 0;

      // We prioritize the signaled ID, then fallback to video-only detection for screen
      const isScreen = signaledIdMatch || (p.stream && p.stream.id !== stream.id && isVideoOnly);

      console.log(`[Stream Router] User: ${userId}, StreamID: ${stream.id}, isScreen: ${isScreen} (SignalMatch: ${signaledIdMatch}, VideoOnly: ${isVideoOnly})`);

      const updated = {
        ...p,
        stream: isScreen ? p.stream : stream,
        screenStream: isScreen ? stream : p.screenStream
      };
      remoteParticipantsRef.current = { ...remoteParticipantsRef.current, [userId]: updated };
      return { ...prev, [userId]: updated };
    });
  }, []);

  const { socketRef, connectionStatus, sendMessage } = useWebSocket(sessionId, role, sessionExpired, handleMessage, participantToken);

  useEffect(() => {
    sendMessageRef.current = sendMessage;
  }, [sendMessage]);

  // Reconnect Cleanup
  useEffect(() => {
    if (connectionStatus === 'Disconnected') {
      console.log('🧹 Cleaning up WebRTC due to final disconnection');
      stopWebRTC();
      setBothPartiesConnected(false);
      setRemoteParticipants(prev => {
        const cleaned = {};
        Object.keys(prev).forEach(userId => {
          cleaned[userId] = {
            ...prev[userId],
            stream: null
          };
        });
        return cleaned;
      });
    }
  }, [connectionStatus, stopWebRTC]);

  const thumbnailVideoRef = useRef(null);



  const [mediaLoading, setMediaLoading] = useState(true);
  const [mediaError, setMediaError] = useState(false);
  const [showMediaHint, setShowMediaHint] = useState(false);

  useEffect(() => {
    if (!mediaLoading || mediaError) {
      setShowMediaHint(false);
      return;
    }
    const t = setTimeout(() => setShowMediaHint(true), 7000);
    return () => clearTimeout(t);
  }, [mediaLoading, mediaError]);

  const initializeMedia = useCallback(() => {
    setMediaLoading(true);
    setMediaError(false);

    const initialCameraOn = lobbyConfig.cameraOn;
    const initialMicOn = lobbyConfig.micOn;

    setIsCameraOn(initialCameraOn);
    setIsMuted(!initialMicOn);

    initLocalStream(true, true, lobbyConfig.videoDeviceId, lobbyConfig.audioDeviceId).then(stream => {
      setCameraReady(true);
      setMediaLoading(false);

      window.dispatchEvent(new Event('vh_exam_started'));

      // If camera was disabled in the lobby, disable the video tracks initially
      if (!initialCameraOn) {
        stream.getVideoTracks().forEach(track => track.enabled = false);
      }
      // If microphone was muted in the lobby, disable the audio tracks initially
      if (!initialMicOn) {
        stream.getAudioTracks().forEach(track => track.enabled = false);
      }

      if (thumbnailVideoRef.current) {
        thumbnailVideoRef.current.srcObject = stream;
      }

      console.log('🗣️ Broadcasting ready_for_webrtc');
      sendMessage({ type: 'ready_for_webrtc', user: candidateName, role: MY_ROLE });

    }).catch(err => {
      setMediaLoading(false);
      setMediaError(true);
      showSessionPopup('Could not access camera/mic. Please check permissions.', 'error');
    });
  }, [initLocalStream, sendMessage, showSessionPopup, stopWebRTC, candidateName, lobbyConfig]);

  // Initialize WebRTC
  useEffect(() => {
    if (!showLobby && connectionStatus === 'Connected' && !localStreamRef.current && !sessionExpired && mediaLoading) {
      initializeMedia();
    }
  }, [connectionStatus, sessionExpired, mediaLoading, initializeMedia, showLobby]);

  // Handle chat sending
  const handleChatSend = useCallback((msgText) => {
    sendMessage({ type: 'chat', sender: candidateName, message: msgText });
    setChatMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      sender: candidateName,
      text: msgText,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isMine: true
    }]);
  }, [sendMessage, candidateName]);

  const toggleMic = useCallback(() => {
    if (!localStreamRef.current) return;
    const newMuted = !isMuted;
    setIsMuted(newMuted);
    localStreamRef.current.getAudioTracks().forEach(track => track.enabled = !newMuted);
    sendMessage({ type: 'media_state', media: 'mic', enabled: !newMuted });
  }, [isMuted, localStreamRef, sendMessage]);

  const toggleCamera = useCallback(() => {
    if (!localStreamRef.current) return;
    const newCameraOn = !isCameraOn;
    setIsCameraOn(newCameraOn);

    // Explicitly toggle video tracks enabled property
    localStreamRef.current.getVideoTracks().forEach(track => {
      track.enabled = newCameraOn;
    });

    sendMessage({ type: 'media_state', media: 'camera', enabled: newCameraOn });
  }, [isCameraOn, localStreamRef, sendMessage]);



  const handleFeedbackSubmit = () => {
    fetch(`${API_BASE_URL}/submit-interview-feedback/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        token: sessionId, 
        participant_token: participantToken,
        feedback, 
        role: 'candidate' 
      })
    }).then(() => {
      setShowThankYou(false);
      setShowFinalThankYou(true);
    });
  };

  useEffect(() => {
    if (chatPanelVisible) setChatUnreadCount(0);
  }, [chatPanelVisible]);

  // Page level Security
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        showSessionPopup('⚠️ Tab switching detected. Please stay on this page.', 'error');
        // A proxy violation will be emitted if integrated directly, or rely on interval detection
      }
    };

    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && ['c', 'v', 'a', 'z', 'y', 'f', 'p'].includes(e.key.toLowerCase())) {
        e.preventDefault();
        showSessionPopup('⚠️ Keyboard shortcuts are disabled during interview.', 'error');
      }
      if (['F11', 'F10', 'F9'].includes(e.key)) {
        e.preventDefault();
        showSessionPopup('⚠️ Function keys are disabled during interview.', 'error');
      }
    };

    const handleContextMenu = (e) => {
      e.preventDefault();
      showSessionPopup('⚠️ Right-click is disabled during interview.', 'error');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('contextmenu', handleContextMenu);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('contextmenu', handleContextMenu);
    };
  }, [showSessionPopup]);


  if (sessionExpired && !showThankYou && !showFinalThankYou) {
    return (
      <div className="session-expired-modal">
        <div className="session-expired-content">
          <div className="session-expired-icon">✓</div>
          <h3 className="session-expired-title">Session Completed</h3>
          <p className="session-expired-message">This interview session has already been completed.</p>
          <button className="btn-close-window" onClick={closeCandidateTab}>Close</button>
        </div>
      </div>
    );
  }

  if (showLobby) {
    return (
      <LiveInterviewLobby
        token={sessionId === 'default-session' ? (searchParams.get('token') || searchParams.get('session') || searchParams.get('sessionId')) : sessionId}
        participantToken={participantToken}
        onJoin={handleLobbyJoin}
      />
    );
  }

  if (isWaiting) {
    return (
      <div className="li-waiting-screen">
        <div className="li-waiting-card">
          <div className="li-waiting-pulse">
            <div className="pulse-circle"></div>
            <i className="fas fa-clock waiting-icon"></i>
          </div>
          <h2 className="waiting-title">Waiting for Interview</h2>
          <p className="waiting-message">
            The interview session hasn't started yet. <br />
            Please stay on this page; the session will begin shortly.
          </p>
          <div className="waiting-status">
            <span className="status-dot"></span> Socket Connected
          </div>
          <button className="btn-refresh-waiting" onClick={() => window.location.reload()}>
            <i className="fas fa-sync-alt"></i> Check Again
          </button>
        </div>
      </div>
    );
  }

  if (showFinalThankYou) {
    return (
      <div className="li-final-thanks-screen">
        <div className="li-final-thanks-card">
          <div className="li-final-thanks-icon">✓</div>
          <h2>Feedback Submitted</h2>
          <p>Thank you for your response. You can now close this tab.</p>
          <button type="button" className="li-final-thanks-close" onClick={closeCandidateTab}>
            Close Tab
          </button>
        </div>
      </div>
    );
  }

  if (showThankYou) {
    return (
      <div className="feedback-overlay">
        <div className="feedback-modal">
          <h2>Interview Completed 🎉</h2>
          <p>We’d love your feedback</p>
          <textarea
            value={feedback}
            onChange={e => setFeedback(e.target.value)}
            placeholder="How was your experience?"
          />
          <button className="btn-submit" onClick={handleFeedbackSubmit}>
            Submit Feedback
          </button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className={`live-interview ${chatPanelVisible ? 'chat-active' : ''}`}>
        <div className="li-notifications-container">
          {notifications.map(n => (
            <div key={n.id} className={`li-notification ${n.severity}`}>
              {n.message}
            </div>
          ))}
        </div>

        <header className="live-interview-header">
          <div className="header-left"><h1>Live Interview</h1></div>
          <div className="header-controls"><div className="timer">{timer}</div></div>
        </header>

        <div className="main-wrapper">
          <div className="video-container">
            {!mediaLoading && !mediaError && <ConnectionOverlay status={connectionStatus} />}

            {mediaLoading && !mediaError && (
              <div className="connection-overlay media-loading-overlay" style={{ zIndex: 50 }}>
                <div className="media-loading-card" role="status" aria-live="polite" aria-atomic="true">
                  <i className="fas fa-circle-notch media-rotate-icon"></i>
                  <h3>Connecting...</h3>
                  <p>Please allow camera and microphone permissions in your browser prompt.</p>
                  {showMediaHint && (
                    <p className="media-loading-hint">Still connecting. If no popup appears, check browser permission icon near URL bar.</p>
                  )}
                </div>
              </div>
            )}

            {mediaError && (
              <div className="connection-overlay" style={{ background: 'rgba(15,23,42,0.95)', zIndex: 100 }}>
                <i className="fas fa-exclamation-circle" style={{ color: '#ef4444', fontSize: '48px', marginBottom: '20px' }}></i>
                <h3>Camera or Microphone Blocked</h3>
                <p style={{ maxWidth: '400px', marginBottom: '20px' }}>We couldn't access your camera or microphone. Please check your browser permissions and try again.</p>
                <button
                  onClick={initializeMedia}
                  style={{ padding: '10px 24px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '16px', fontWeight: 'bold' }}
                >
                  Retry Permissions
                </button>
              </div>
            )}

            <VideoPanel
              remoteParticipants={remoteParticipants}
              localVideoRef={thumbnailVideoRef}
              localStreamRef={localStreamRef}
              localScreenStream={screenShareStreamRef.current}
              isRemoteCameraOn={isRemoteCameraOn}
              isRemoteScreenSharing={isRemoteScreenSharing}
              bothPartiesConnected={bothPartiesConnected}
              isCameraOn={isCameraOn}
              isLocalScreenSharing={isScreenSharing}
              localName={candidateName}
              localRole={MY_ROLE}
              speakerDeviceId={lobbyConfig.speakerDeviceId}
            />
          </div>

          <ChatPanel
            chatPanelVisible={chatPanelVisible}
            setChatPanelVisible={setChatPanelVisible}
            chatMessages={chatMessages}
            setChatMessages={setChatMessages}
            onSendMessage={handleChatSend}
            sessionId={sessionId}
            localName={candidateName}
          />
        </div>

        <ControlBar
          isMuted={isMuted}
          isCameraOn={isCameraOn}
          isScreenSharing={isScreenSharing}
          chatPanelVisible={chatPanelVisible}
          chatUnreadCount={chatUnreadCount}
          MY_ROLE={MY_ROLE}
          screenShareLocked={screenShareLocked}
          screenShareHolder={screenShareHolder}
          toggleMic={toggleMic}
          toggleCamera={toggleCamera}
          toggleScreenShare={toggleScreenShare}
          setChatPanelVisible={setChatPanelVisible}
          handleEndInterview={handleEndInterview}
        />

        <MalpracticeMonitor
          sessionId={sessionId}
          participantToken={participantToken}
          videoRef={thumbnailVideoRef}
          cameraReady={cameraReady}
          isCameraOn={isCameraOn}
          sendMessage={sendMessage}
          showNotification={showSessionPopup}
        />
      </div>
    </ErrorBoundary>
  );
}

export default LiveInterview;