import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/LiveInterviewInterviewer.css';

import { API_BASE_URL } from '../apiConfig';
import { useWebSocket } from '../hooks/useWebSocket';
import { useWebRTC } from '../hooks/useWebRTC';
import { useScreenShare } from '../hooks/useScreenShare';

import VideoPanel from '../components/LiveInterview/VideoPanel';
import ChatPanel from '../components/LiveInterview/ChatPanel';
import ControlBar from '../components/LiveInterview/ControlBar';
import ConnectionOverlay from '../components/LiveInterview/ConnectionOverlay';
import ErrorBoundary from '../components/LiveInterview/ErrorBoundary';

function LiveInterviewInterviewer() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('token') || searchParams.get('session') || searchParams.get('sessionId') || 'default-session';
  
  const MY_ROLE = 'Interviewer';
  const role = 'interviewer';
  const sessionKey = `session_expired_${sessionId}`;

  const [candidateName, setCandidateName] = useState('Candidate');
  const [interviewerName] = useState('Interviewer');
  
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
  const [feedback, setFeedback] = useState('');

  const [timer, setTimer] = useState('00:00:00');
  const startTimeRef = useRef(Date.now());
  const candidateHasJoinedRef = useRef(false);
  const candidateReadyRef = useRef(false);
  const interviewerReadyRef = useRef(false);

  const [notifications, setNotifications] = useState([]);

  // Load interview details
  useEffect(() => {
    const loadInterviewDetails = async () => {
      try {
        const resp = await axios.get(`${API_BASE_URL}/interviews/invitations/${sessionId}/`);
        if (resp.data) setCandidateName(resp.data.name || 'Candidate');
      } catch (error) {
        try {
          const listResp = await axios.get(`${API_BASE_URL}/interviews/invitations/`);
          const invitation = listResp.data?.results?.find(inv => inv.token === sessionId);
          if (invitation) setCandidateName(invitation.name || 'Candidate');
        } catch (e) {
          console.warn('Could not load interview details:', e);
        }
      }
    };
    loadInterviewDetails();
  }, [sessionId]);

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

  const showNotification = useCallback((message, severity = 'info') => {
    const id = Date.now() + Math.random();
    setNotifications(prev => [...prev, { id, message, severity }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 4000);
  }, []);

  // Message Handler
  const handleMessage = useCallback(async (data) => {
    console.log('Received message:', data);
    switch (data.type) {
      case 'session_info':
        if (data.start_time) startTimeRef.current = new Date(data.start_time).getTime();
        break;
      case 'user_joined':
        if (data.user === 'Candidate' || data.user.toLowerCase() === 'candidate') {
          showNotification(`${candidateName} joined the session`);
          setBothPartiesConnected(true);
          candidateHasJoinedRef.current = true;
          // We wait for ready_for_webrtc signal before sending offer
        }
        break;
      case 'user_left':
        if (data.user === 'Candidate' || data.user.toLowerCase() === 'candidate') {
          candidateHasJoinedRef.current = false;
          showNotification(`${candidateName} left the session`, 'warning');
        }
        break;
      case 'ready_for_webrtc':
        console.log('✅ Received ready_for_webrtc from', data.sender);
        if (data.sender === 'candidate') {
          candidateReadyRef.current = true;
        }
        if (data.sender === 'interviewer') {
          interviewerReadyRef.current = true;
        }

        if (
          MY_ROLE === 'Interviewer' &&
          candidateReadyRef.current &&
          interviewerReadyRef.current
        ) {
          setTimeout(() => {
            if (
              peerConnectionRef.current &&
              localStreamRef.current &&
              localStreamRef.current.getTracks().length > 0 &&
              peerConnectionRef.current.signalingState === 'stable'
            ) {
              console.log('🚀 Both ready. Sending video offer...');
              createVideoOffer();
            }
          }, 500);
        }
        break;
      case 'chat':
        if (String(data.sender).toLowerCase() !== 'interviewer') {
          setChatMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            sender: candidateName,
            text: data.message,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            isMine: false
          }]);
          if (!chatPanelVisible) setChatUnreadCount(c => c + 1);
        }
        break;
      case 'video_offer':
        await handleVideoOffer(data.sdp);
        break;
      case 'video_answer':
        await handleVideoAnswer(data.sdp);
        break;
      case 'ice_candidate':
        await handleIceCandidate(data.candidate);
        break;
      case 'request_offer':
        console.log('🔄 Candidate requested a new offer (ICE restart), creating...');
        if (peerConnectionRef.current) {
          createVideoOffer({ iceRestart: true });
        }
        break;
      case 'media_state':
        if (String(data.sender).toLowerCase() === 'candidate') {
          if (data.media === 'camera') setIsRemoteCameraOn(data.enabled);
          const what = data.media === 'mic' ? (data.enabled ? 'unmuted' : 'muted') : (data.enabled ? 'turned on camera' : 'turned off camera');
          showNotification(`${candidateName} ${what}`, !data.enabled && data.media === 'camera' ? 'error' : 'info');
        }
        break;
      case 'screen_share_state':
        if (String(data.sender).toLowerCase() === 'candidate') {
          setIsRemoteScreenSharing(!!data.active);
          showNotification(`${candidateName} ${data.active ? 'started' : 'stopped'} screen sharing`);
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
        handleEndInterview(false);
        break;
      case 'proxy_violation':
        if (String(data.sender).toLowerCase() === 'candidate') {
          showNotification(`🚨 ${candidateName} proxy violation: ${data.violation_type} (${data.violation_count}/${data.violation_limit})`, 'warning');
        }
        break;
      case 'interview_terminated_violations':
        showNotification(`Interview terminated: ${data.reason || 'Multiple violations'}`, 'error');
        setTimeout(() => {
            navigate(`/interview-terminated/?session_id=${sessionId}&candidate_name=${candidateName}&violation_count=${data.violation_count}`);
        }, 1200);
        break;
      case 'session_expired':
        if (data.reason === 'not_started') {
          setIsWaiting(true);
        } else {
          showNotification(data.message || 'Session expired or already completed.', 'error');
          setSessionExpired(true);
          localStorage.setItem(sessionKey, 'true');
          setTimeout(() => {
            navigate('/live-interview-list');
          }, 3000);
        }
        break;
      default: break;
    }
  }, [candidateName, chatPanelVisible, sessionId, sessionKey, navigate, showNotification]);

  const { socketRef, connectionStatus, sendMessage } = useWebSocket(sessionId, role, sessionExpired, handleMessage);

  const {
    peerConnectionRef, localStreamRef, remoteStreamRef, 
    createPeerConnection, initLocalStream, addLocalTracksToPC,
    createVideoOffer, handleVideoOffer, handleVideoAnswer, handleIceCandidate, stopWebRTC
  } = useWebRTC(sendMessage);

  const {
    isScreenSharing, screenShareLocked, setScreenShareLocked, screenShareHolder, setScreenShareHolder,
    toggleScreenShare, stopScreenSharing, handleScreenShareGranted, handleScreenShareDenied
  } = useScreenShare(peerConnectionRef, localStreamRef, sendMessage, showNotification, MY_ROLE);

  const remoteVideoRef = useRef(null);
  const selfVideoRef = useRef(null); // Local interviewer view

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
    
    initLocalStream(true, true).then(stream => {
      setMediaLoading(false);
      
      // ✅ Fix: Assign local stream to video element
      if (selfVideoRef.current) {
        console.log('🖼️ Setting local video srcObject');
        selfVideoRef.current.srcObject = stream;
      }

      const pc = createPeerConnection((remoteStream) => {
        if (remoteVideoRef.current) {
          console.log('🖼️ Setting remote video srcObject');
          remoteVideoRef.current.srcObject = remoteStream;
        }
      });
      
      pc.onconnectionstatechange = () => {
        // Handled by ConnectionOverlay
      };

      pc.oniceconnectionstatechange = () => {
        if (pc.iceConnectionState === 'failed') {
          setTimeout(() => {
            if (peerConnectionRef.current?.iceConnectionState === 'failed') {
              console.log('🔄 ICE failed, restarting...');
              createVideoOffer({ iceRestart: true });
            }
          }, 1000);
        }
      };

      addLocalTracksToPC(pc, stream);
      
      console.log('🗣️ Sending ready_for_webrtc to candidate');
      interviewerReadyRef.current = true;
      sendMessage({ type: 'ready_for_webrtc' });
    }).catch(err => {
      setMediaLoading(false);
      setMediaError(true);
      showNotification('Could not access camera/mic. Please check permissions.', 'error');
    });
  }, [initLocalStream, createPeerConnection, createVideoOffer, addLocalTracksToPC, showNotification, peerConnectionRef]);

  // Initialize WebRTC
  useEffect(() => {
    if (connectionStatus === 'Connected' && !localStreamRef.current && !sessionExpired && mediaLoading) {
      initializeMedia();
    }
  }, [connectionStatus, sessionExpired, mediaLoading, initializeMedia]); 

  const handleChatSend = useCallback((msgText) => {
    sendMessage({ type: 'chat', sender: interviewerName, message: msgText });
    setChatMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      sender: interviewerName,
      text: msgText,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isMine: true
    }]);
  }, [sendMessage, interviewerName]);

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

    if (!newCameraOn) {
      localStreamRef.current.getVideoTracks().forEach(track => track.enabled = false);
      try {
        if (peerConnectionRef.current) {
          const sender = peerConnectionRef.current.getSenders().find(s => s.track && s.track.kind === 'video');
          if (sender) sender.replaceTrack(null);
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
            sender.replaceTrack(localStreamRef.current.getVideoTracks()[0]);
          }
        }
      } catch (e) {
        console.warn('replaceTrack(videoTrack) failed', e);
      }
    }
    sendMessage({ type: 'media_state', media: 'camera', enabled: newCameraOn });
  }, [isCameraOn, localStreamRef, sendMessage, peerConnectionRef]);

  const handleEndInterview = useCallback((shouldSend = true) => {
    if (shouldSend) {
      if (!window.confirm('Are you sure you want to end the interview for everyone?')) return;
    }

    if (bothPartiesConnected) {
      setSessionExpired(true);
      localStorage.setItem(sessionKey, 'true');
    }

    try {
      if (shouldSend && socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: 'screen_share_state', active: false }));
        socketRef.current.send(JSON.stringify({ type: 'screen_share_release' }));
        socketRef.current.send(JSON.stringify({ type: 'end_interview' }));
      }
    } catch (e) { console.warn('end_interview send failed', e); }

    stopWebRTC();

    try {
      axios.post(`${API_BASE_URL}/submit-interview-feedback/`, {
        token: sessionId,
        isInterviewer: true,
        totalTime: timer,
        sessionId: sessionId,
        isDraft: true
      }, { withCredentials: true }).catch(() => {});
    } catch (e) { console.warn('Failed to persist total time on end:', e); }

    setShowInterviewReport(true);
  }, [bothPartiesConnected, sessionKey, timer, sessionId, socketRef, stopWebRTC]);

  const handleStarClick = (category, value) => {
    setRatings(prev => ({ ...prev, [category]: value }));
  };

  const handleSkillScoreChange = (index, value) => {
    setSkills(prev => {
      const newSkills = [...prev];
      const parsed = parseInt(value, 10);
      const safeScore = Number.isNaN(parsed) ? 0 : Math.min(10, Math.max(0, parsed));
      newSkills[index] = { ...newSkills[index], score: safeScore };
      return newSkills;
    });
  };

  const confirmEndInterview = useCallback((status) => {
    if (ratings.overallRating === 0) {
      showNotification('Please provide an overall rating', 'error');
      return;
    }
    setRatings(prev => ({ ...prev, hireRecommendation: status }));
    
    // Map frontend ratings/skills to backend expected fields
    const normalizeScore = (n) => {
      const val = parseInt(n, 10);
      if (Number.isNaN(val)) return 0;
      return Math.min(10, Math.max(0, val));
    };

    const technicalSkill = normalizeScore(skills.find(s => s.name === 'Problem Solving')?.score || 0);
    const communicationSkill = normalizeScore(skills.find(s => s.name === 'Communication')?.score || 0);

    axios.post(`${API_BASE_URL}/submit-interview-feedback/`, {
        token: sessionId,
        feedback: feedback,
        rating: ratings.overallRating,
        technical_rating: technicalSkill,
        communication_rating: communicationSkill,
        team_fit_rating: 5, // Default or derived if possible
        role: 'interviewer',
        candidate: candidateName,
        interviewer: interviewerName,
        time: timer,
        status: candidateHasJoinedRef.current ? 'joined' : 'not_joined'
    }).then(() => {
        setShowInterviewReport(false);
        setShowFeedbackSuccess(true);
    }).catch(err => {
        console.error('Submit feedback failed:', err);
        showNotification('Failed to submit feedback. Retrying...', 'error');
    });
  }, [ratings, skills, candidateName, interviewerName, timer, sessionId, navigate, showNotification]);

  useEffect(() => {
    if (chatPanelVisible) setChatUnreadCount(0);
  }, [chatPanelVisible]);

  if (sessionExpired && !showInterviewReport && !showFeedbackSuccess) {
    return (
      <div className="session-expired-modal">
        <div className="session-expired-content">
          <div className="session-expired-icon">✓</div>
          <h3 className="session-expired-title">Session Completed</h3>
          <p className="session-expired-message">This interview session has already been completed.</p>
          <button className="btn-close-window" onClick={() => navigate('/live-interview-list')}>Close</button>
        </div>
      </div>
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
            As the interviewer, you can wait here or come back at the scheduled time.
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

  if (showFeedbackSuccess) {
    return (
      <div className="thank-you-screen">
        <div className="thank-you-card">
          <div className="thank-you-card-icon">✓</div>
          <h2>Feedback Submitted Successfully</h2>
          <p>Thank you. You can close this tab when ready.</p>
        </div>
      </div>
    );
  }

  if (showInterviewReport) {
    return (
      <div className="feedback-overlay">
        <div className="feedback-modal interview-report-modal">
          <h2>Interview Report</h2>
          <p>Please provide your evaluation for {candidateName}</p>
          
          <div className="ratings-section report-section">
            <h3 className="report-section-title">Overall Rating</h3>
            {[1, 2, 3, 4, 5].map(star => (
              <i
                key={star}
                onClick={() => handleStarClick('overallRating', star)}
                className={`fas fa-star ${ratings.overallRating >= star ? 'active' : ''}`}
                style={{ cursor: 'pointer', color: ratings.overallRating >= star ? '#fbbf24' : '#475569', fontSize: '28px', marginRight: '8px' }}
              ></i>
            ))}
          </div>
          
          <div className="skills-section report-section">
            <h3 className="report-section-title">Skills Assessment</h3>
            {skills.map((skill, idx) => (
              <div key={idx} className="report-skill-row">
                <label className="report-skill-label">{skill.name}</label>
                <div className="report-skill-input-wrap">
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={skill.score}
                    onChange={e => handleSkillScoreChange(idx, e.target.value)}
                    onBlur={e => handleSkillScoreChange(idx, e.target.value)}
                    className="report-skill-input"
                  />
                  <span className="report-skill-max">/ 10</span>
                </div>
              </div>
            ))}
          </div>

          <div className="feedback-section report-section">
            <h3 className="report-section-title">Detailed Feedback</h3>
            <textarea 
              value={feedback}
              onChange={e => setFeedback(e.target.value)}
              placeholder="Enter detailed feedback here..."
              className="report-feedback-textarea"
            />
          </div>

          <div className="actions-section report-actions">
             <button className="btn-submit report-btn-qualified" onClick={() => confirmEndInterview('Qualified')}>Qualified</button>
             <button className="btn-submit report-btn-rejected" onClick={() => confirmEndInterview('Rejected')}>Rejected</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
    <div className={`live-interview-interviewer ${chatPanelVisible ? 'chat-active' : ''}`}>
      <div className="li-notifications-container">
        {notifications.map(n => (
          <div key={n.id} className={`li-notification ${n.severity}`}>
            {n.message}
          </div>
        ))}
      </div>

      <header className="live-interview-header">
        <div className="header-left"><h1>Live Interview (Interviewer View)</h1></div>
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
            remoteVideoRef={remoteVideoRef}
            localVideoRef={selfVideoRef}
            isRemoteCameraOn={isRemoteCameraOn}
            isRemoteScreenSharing={isRemoteScreenSharing}
            bothPartiesConnected={bothPartiesConnected}
            isCameraOn={isCameraOn}
            remoteName={candidateName}
            localName={interviewerName}
          />
        </div>

        <ChatPanel 
          chatPanelVisible={chatPanelVisible}
          setChatPanelVisible={setChatPanelVisible}
          chatMessages={chatMessages}
          setChatMessages={setChatMessages}
          onSendMessage={handleChatSend}
          sessionId={sessionId}
          localName={interviewerName}
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

export default LiveInterviewInterviewer;