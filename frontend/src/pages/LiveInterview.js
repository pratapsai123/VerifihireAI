import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import '../styles/LiveInterview.css';

import { API_BASE_URL } from '../apiConfig';
import { useWebSocket } from '../hooks/useWebSocket';
import { useWebRTC } from '../hooks/useWebRTC';
import { useScreenShare } from '../hooks/useScreenShare';
import { useProxyDetection } from '../hooks/useProxyDetection';

import VideoPanel from '../components/LiveInterview/VideoPanel';
import ChatPanel from '../components/LiveInterview/ChatPanel';
import ControlBar from '../components/LiveInterview/ControlBar';
import ConnectionOverlay from '../components/LiveInterview/ConnectionOverlay';
import ErrorBoundary from '../components/LiveInterview/ErrorBoundary';

function LiveInterview() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('token') || searchParams.get('session') || searchParams.get('sessionId') || 'default-session';
  
  const MY_ROLE = 'Candidate';
  const role = 'candidate';
  const sessionKey = `session_expired_${sessionId}`;

  const [candidateName] = useState('Candidate');
  const [interviewerName] = useState('Interviewer');
  
  const [sessionExpired, setSessionExpired] = useState(false);
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

  const [notifications, setNotifications] = useState([]);

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

  // Message Handler
  const handleMessage = useCallback((data) => {
    console.log('Received message:', data);
    switch (data.type) {
      case 'session_info':
        if (data.start_time) startTimeRef.current = new Date(data.start_time).getTime();
        break;
      case 'user_joined':
        if (data.user === 'Interviewer' || data.user.toLowerCase() === 'interviewer') {
          showSessionPopup(`${interviewerName} joined the session`);
          setBothPartiesConnected(true);
        }
        break;
      case 'user_left':
        if (data.user === 'Interviewer' || data.user.toLowerCase() === 'interviewer') {
          showSessionPopup(`${interviewerName} left the session`, 'warning');
        }
        break;
      case 'chat':
        if (String(data.sender).toLowerCase() !== 'candidate') {
          setChatMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            sender: interviewerName,
            text: data.message,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            isMine: false
          }]);
          if (!chatPanelVisible) setChatUnreadCount(c => c + 1);
        }
        break;
      case 'video_offer':
        handleVideoOffer(data.offer);
        break;
      case 'video_answer':
        handleVideoAnswer(data.answer);
        break;
      case 'ice_candidate':
        handleIceCandidate(data.candidate);
        break;
      case 'request_offer':
        // Candidate is expected to answer normally, but if interviewer failed:
        createVideoOffer({ iceRestart: true });
        break;
      case 'media_state':
        if (String(data.sender).toLowerCase() === 'interviewer') {
          if (data.media === 'camera') setIsRemoteCameraOn(data.enabled);
          const what = data.media === 'mic' ? (data.enabled ? 'unmuted' : 'muted') : (data.enabled ? 'turned on camera' : 'turned off camera');
          showSessionPopup(`${interviewerName} ${what}`, !data.enabled && data.media === 'camera' ? 'error' : 'info');
        }
        break;
      case 'screen_share_state':
        if (String(data.sender).toLowerCase() !== 'candidate') {
          setIsRemoteScreenSharing(!!data.active);
          showSessionPopup(`${interviewerName} ${data.active ? 'started' : 'stopped'} screen sharing`);
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
        setSessionExpired(true);
        localStorage.setItem(sessionKey, 'true');
        break;
      default: break;
    }
  }, [interviewerName, chatPanelVisible, sessionId, sessionKey, navigate, showSessionPopup]);

  const { socketRef, connectionStatus, connectionStatusText, setConnectionStatusText, sendMessage } = useWebSocket(sessionId, role, sessionExpired, handleMessage);

  const {
    peerConnectionRef, localStreamRef, remoteStreamRef, 
    createPeerConnection, initLocalStream, addLocalTracksToPC,
    createVideoOffer, handleVideoOffer, handleVideoAnswer, handleIceCandidate, stopWebRTC
  } = useWebRTC(sendMessage);

  const {
    isScreenSharing, screenShareLocked, setScreenShareLocked, screenShareHolder, setScreenShareHolder,
    toggleScreenShare, stopScreenSharing, handleScreenShareGranted, handleScreenShareDenied
  } = useScreenShare(peerConnectionRef, localStreamRef, sendMessage, showSessionPopup, MY_ROLE);

  const { thumbnailVideoRef, startDetection, stopDetection, pauseDetection } = useProxyDetection(sessionId, cameraReady, isCameraOn, sendMessage);

  const remoteVideoRef = useRef(null);

  const [mediaLoading, setMediaLoading] = useState(true);
  const [mediaError, setMediaError] = useState(false);

  const initializeMedia = useCallback(() => {
    setMediaLoading(true);
    setMediaError(false);
    initLocalStream(true, true).then(stream => {
      setCameraReady(true);
      setMediaLoading(false);
      startDetection(showSessionPopup, () => {
        setShowThankYou(true);
        stopWebRTC();
      });

      const pc = createPeerConnection((remoteStream) => {
        if (remoteVideoRef.current) {
          remoteVideoRef.current.srcObject = remoteStream;
        }
      });
      
      pc.onconnectionstatechange = () => {
        if (pc.connectionState === 'connected') setConnectionStatusText('Connected');
        else if (pc.connectionState === 'failed') {
          setConnectionStatusText('Connection failed');
          setTimeout(() => {
              if (peerConnectionRef.current?.connectionState === 'failed') {
                  sendMessage({ type: 'request_offer' });
              }
          }, 2000);
        }
      };

      pc.oniceconnectionstatechange = () => {
        if (pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'disconnected') {
          setConnectionStatusText('Connection unstable - retrying...');
          setTimeout(() => {
              if (peerConnectionRef.current?.iceConnectionState === 'failed' || peerConnectionRef.current?.iceConnectionState === 'disconnected') {
                  sendMessage({ type: 'request_offer' });
              }
          }, 3000);
        }
      };

      addLocalTracksToPC(pc, stream);
    }).catch(err => {
      setMediaLoading(false);
      setMediaError(true);
      showSessionPopup('Could not access camera/mic. Please check permissions.', 'error');
    });
  }, [initLocalStream, startDetection, showSessionPopup, stopWebRTC, createPeerConnection, addLocalTracksToPC, sendMessage, setConnectionStatusText, peerConnectionRef]);

  // Initialize WebRTC
  useEffect(() => {
    if (connectionStatus === 'Connected' && !localStreamRef.current && !sessionExpired && mediaLoading) {
      initializeMedia();
    }
  }, [connectionStatus, sessionExpired, mediaLoading, initializeMedia]); 

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
    
    // Explicitly toggle video tracks
    localStreamRef.current.getVideoTracks().forEach(track => {
        track.enabled = newCameraOn;
    });

    if (newCameraOn) startDetection(showSessionPopup);
    else stopDetection();

    sendMessage({ type: 'media_state', media: 'camera', enabled: newCameraOn });
  }, [isCameraOn, localStreamRef, startDetection, stopDetection, sendMessage, showSessionPopup]);

  const handleEndInterview = useCallback(() => {
    sendMessage({ type: 'end_interview' });
    setShowThankYou(true);
    stopWebRTC();
  }, [sendMessage, stopWebRTC]);

  const handleFeedbackSubmit = () => {
    fetch(`${API_BASE_URL}/submit-interview-feedback/`, { 
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: sessionId, feedback, role: 'candidate' })
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
      if ((e.ctrlKey || e.metaKey) && ['c','v','a','z','y','f','p'].includes(e.key.toLowerCase())) {
        e.preventDefault();
        showSessionPopup('⚠️ Keyboard shortcuts are disabled during interview.', 'error');
      }
      if (['F12','F11','F10','F9'].includes(e.key)) {
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
          <h3>Session Completed</h3>
          <p>This interview session has already been completed.</p>
          <button onClick={() => navigate('/')}>Close</button>
        </div>
      </div>
    );
  }

  if (showFinalThankYou) {
    return <div className="thank-you-screen"><h2>Thank You!</h2></div>;
  }

  if (showThankYou) {
    return (
      <div className="thank-you-screen">
        <h2>Interview Completed!</h2>
        <div className="feedback-form" style={{ maxWidth: '400px', margin: '0 auto', textAlign: 'center' }}>
            <textarea 
                value={feedback} 
                onChange={e => setFeedback(e.target.value)} 
                placeholder="How was your experience?" 
                rows="4"
                style={{ width: '100%', padding: '10px', marginTop: '20px' }}
            />
            <button 
                onClick={handleFeedbackSubmit}
                style={{ padding: '10px 20px', marginTop: '10px', cursor: 'pointer' }}
            >
                Submit
            </button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
    <div className={`live-interview ${chatPanelVisible ? 'chat-active' : ''}`}>
      <div className="notifications-container" style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 9999 }}>
        {notifications.map(n => (
          <div key={n.id} className={`session-popup ${n.severity}`} style={{ marginBottom: '10px', padding: '10px', background: '#333', color: '#fff', borderRadius: '5px' }}>
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
          <ConnectionOverlay status={connectionStatus} statusText={connectionStatusText} />
          
          {mediaLoading && !mediaError && (
            <div className="connection-overlay" style={{ background: 'rgba(0,0,0,0.8)', zIndex: 50 }}>
              <i className="fas fa-video spinner"></i>
              <h3>Accessing Camera & Microphone...</h3>
              <p>Please allow permissions when prompted.</p>
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
            remoteVideoRef={remoteVideoRef}
            localVideoRef={thumbnailVideoRef}
            isRemoteCameraOn={isRemoteCameraOn}
            isRemoteScreenSharing={isRemoteScreenSharing}
            bothPartiesConnected={bothPartiesConnected}
            isCameraOn={isCameraOn}
            remoteName={interviewerName}
            localName={candidateName}
          />
        </div>

        <ChatPanel 
          chatPanelVisible={chatPanelVisible}
          setChatPanelVisible={setChatPanelVisible}
          chatMessages={chatMessages}
          onSendMessage={handleChatSend}
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
    </div>
    </ErrorBoundary>
  );
}

export default LiveInterview;