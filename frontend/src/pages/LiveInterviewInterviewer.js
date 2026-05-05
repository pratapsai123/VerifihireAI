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
  const participantToken = searchParams.get('participant_token');
  const [sessionId, setSessionId] = useState(searchParams.get('token') || searchParams.get('session') || searchParams.get('sessionId') || 'default-session');
  
  const MY_ROLE = 'Interviewer';
  const role = 'interviewer';
  const sessionKey = `session_expired_${sessionId}`;

  const [candidateName, setCandidateName] = useState('Candidate');
  const [interviewerName, setInterviewerName] = useState('Interviewer');
  
  // New state for invite flow
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [generatedInviteLink, setGeneratedInviteLink] = useState('');

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

  const [remoteParticipants, setRemoteParticipants] = useState({}); // { userId: { stream, role, name, isCameraOn, isScreenSharing } }
  const [myUserId, setMyUserId] = useState(null);
  const [notifications, setNotifications] = useState([]);

  // Load interview details
  useEffect(() => {
    const loadInterviewDetails = async () => {
      try {
        if (participantToken) {
          const resp = await axios.get(`${API_BASE_URL}/interviews/participants/validate/${participantToken}/`);
          if (resp.data) {
            setSessionId(resp.data.session_id);
            setCandidateName(resp.data.candidate_name || 'Candidate');
            setInterviewerName(resp.data.name || 'Interviewer');
          }
        } else {
          const resp = await axios.get(`${API_BASE_URL}/interviews/invitations/${sessionId}/`);
          if (resp.data) setCandidateName(resp.data.name || 'Candidate');
        }
      } catch (error) {
        console.warn('Could not load interview details:', error);
      }
    };
    loadInterviewDetails();
  }, [sessionId, participantToken]);

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

  const sendMessageRef = useRef(null);
  const stableSendMessage = useCallback((data) => {
    if (sendMessageRef.current) sendMessageRef.current(data);
  }, []);

  const {
    peerConnectionsRef, localStreamRef, remoteStreamsRef, 
    createPeerConnection, initLocalStream,
    createVideoOffer, handleVideoOffer, handleVideoAnswer, handleIceCandidate, stopWebRTC
  } = useWebRTC(stableSendMessage);

  const {
    isScreenSharing, screenShareLocked, setScreenShareLocked, screenShareHolder, setScreenShareHolder,
    toggleScreenShare, stopScreenSharing, handleScreenShareGranted, handleScreenShareDenied
  } = useScreenShare(peerConnectionsRef, localStreamRef, stableSendMessage, showNotification, MY_ROLE);

  const handleEndInterview = useCallback((shouldSend = true) => {
    if (shouldSend) {
      if (!window.confirm('Are you sure you want to end the interview for everyone?')) return;
    }

    if (shouldSend) {
      stableSendMessage({ type: 'end_interview' });
    }
    
    stopWebRTC();
    setSessionExpired(true);
    localStorage.setItem(sessionKey, 'true');

    try {
      const axios = require('axios');
      axios.post(`${API_BASE_URL}/interviews/submit-feedback/`, {
        token: sessionId,
        isInterviewer: true,
        totalTime: timer,
        isDraft: true
      }, { withCredentials: true }).catch(() => {});
    } catch (e) { console.warn('Failed to persist total time on end:', e); }

    setShowInterviewReport(true);
  }, [sessionKey, timer, sessionId, stableSendMessage, stopWebRTC]);

  // Message Handler
  const handleMessage = useCallback(async (data) => {
    console.log('Received message:', data);
    switch (data.type) {
      case 'session_info':
        if (data.start_time) startTimeRef.current = new Date(data.start_time).getTime();
        if (data.user_id) setMyUserId(data.user_id);
        break;
      case 'user_joined':
        showNotification(`${data.user} joined the session`);
        setBothPartiesConnected(true);
        break;
      case 'user_left':
        showNotification(`${data.user} left the session`, 'warning');
        setRemoteParticipants(prev => {
          const next = { ...prev };
          delete next[data.user_id];
          return next;
        });
        if (peerConnectionsRef.current[data.user_id]) {
            peerConnectionsRef.current[data.user_id].close();
            delete peerConnectionsRef.current[data.user_id];
        }
        break;
      case 'ready_for_webrtc':
        console.log(`✅ Received ready_for_webrtc from ${data.sender_id} (${data.role})`);
        if (myUserId && myUserId < data.sender_id) {
            console.log(`🚀 Initiating offer to ${data.sender_id}`);
            createPeerConnection(data.sender_id, (userId, stream) => {
                setRemoteParticipants(prev => ({
                    ...prev,
                    [userId]: { ...prev[userId], stream, name: data.user || 'Participant' }
                }));
            });
            createVideoOffer(data.sender_id);
        }
        break;
      case 'chat':
        if (data.sender_id !== myUserId) {
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
      case 'video_offer':
        if (data.target === myUserId) {
          handleVideoOffer(data.sender_id, data.sdp, (userId, stream) => {
              setRemoteParticipants(prev => ({
                  ...prev,
                  [userId]: { ...prev[userId], stream, name: data.user || 'Participant' }
              }));
          });
        }
        break;
      case 'video_answer':
        if (data.target === myUserId) {
          handleVideoAnswer(data.sender_id, data.sdp);
        }
        break;
      case 'ice_candidate':
        if (data.target === myUserId) {
          handleIceCandidate(data.sender_id, data.candidate);
        }
        break;
      case 'media_state':
        if (data.sender_id !== myUserId) {
          setRemoteParticipants(prev => ({
              ...prev,
              [data.sender_id]: { 
                  ...prev[data.sender_id], 
                  isCameraOn: data.media === 'camera' ? data.enabled : prev[data.sender_id]?.isCameraOn 
              }
          }));
        }
        break;
      case 'screen_share_state':
        if (data.sender_id !== myUserId) {
          setRemoteParticipants(prev => ({
              ...prev,
              [data.sender_id]: { ...prev[data.sender_id], isScreenSharing: !!data.active }
          }));
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
      case 'session_expired':
        if (data.reason === 'not_started') {
          setIsWaiting(true);
        } else {
          showNotification(data.message || 'Session expired or already completed.', 'error');
          setSessionExpired(true);
          localStorage.setItem(sessionKey, 'true');
        }
        break;
      default: break;
    }
  }, [myUserId, chatPanelVisible, sessionId, sessionKey, navigate, showNotification, createPeerConnection, createVideoOffer, handleVideoOffer, handleVideoAnswer, handleIceCandidate, stopWebRTC, handleScreenShareGranted]);

  const { socketRef, connectionStatus, sendMessage } = useWebSocket(sessionId, role, sessionExpired, handleMessage, participantToken);

  useEffect(() => {
    sendMessageRef.current = sendMessage;
  }, [sendMessage]);

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
      
      if (selfVideoRef.current) {
        selfVideoRef.current.srcObject = stream;
      }

      console.log('🗣️ Broadcasting ready_for_webrtc');
      sendMessage({ type: 'ready_for_webrtc' });
    }).catch(err => {
      setMediaLoading(false);
      setMediaError(true);
      showNotification('Could not access camera/mic. Please check permissions.', 'error');
    });
  }, [initLocalStream, sendMessage, showNotification]);

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
        Object.values(peerConnectionsRef.current).forEach(pc => {
          const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
          if (sender) sender.replaceTrack(null);
        });
      } catch (e) {
        console.warn('replaceTrack(null) failed', e);
      }
    } else {
      localStreamRef.current.getVideoTracks().forEach(track => track.enabled = true);
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      try {
        Object.values(peerConnectionsRef.current).forEach(pc => {
          const sender = pc.getSenders().find(s => !s.track || s.track.kind === 'video');
          if (sender && videoTrack) {
            sender.replaceTrack(videoTrack);
          }
        });
      } catch (e) {
        console.warn('replaceTrack(videoTrack) failed', e);
      }
    }
    sendMessage({ type: 'media_state', media: 'camera', enabled: newCameraOn });
  }, [isCameraOn, localStreamRef, sendMessage, peerConnectionsRef]);


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

  const handleInviteInterviewer = async (e) => {
    e.preventDefault();
    if (!inviteEmail) return;
    try {
      const resp = await axios.post(`${API_BASE_URL}/interviews/add-participant/`, {
        session_id: sessionId,
        email: inviteEmail,
        name: inviteName || 'Interviewer',
        role: 'interviewer'
      });
      if (resp.data.invite_link) {
        setGeneratedInviteLink(resp.data.invite_link);
        showNotification('Invite link generated!', 'success');
      }
    } catch (error) {
      console.error('Invite failed:', error);
      showNotification('Failed to generate invite link', 'error');
    }
  };

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
        <div className="header-controls">
          <button className="btn-invite-panelist" onClick={() => setShowInviteModal(true)}>
            <i className="fas fa-user-plus"></i> Invite Panelist
          </button>
          <div className="timer">{timer}</div>
        </div>
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
            localVideoRef={selfVideoRef}
            isRemoteCameraOn={isRemoteCameraOn}
            isRemoteScreenSharing={isRemoteScreenSharing}
            bothPartiesConnected={bothPartiesConnected}
            isCameraOn={isCameraOn}
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