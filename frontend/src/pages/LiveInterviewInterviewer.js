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
        showNotification(data.message || 'Session expired or already completed.', 'error');
        setSessionExpired(true);
        localStorage.setItem(sessionKey, 'true');
        setTimeout(() => {
          navigate('/');
        }, 3000);
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
      newSkills[index] = { ...newSkills[index], score: parseInt(value) || 0 };
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
    const technicalSkill = skills.find(s => s.name === 'Problem Solving')?.score || 0;
    const communicationSkill = skills.find(s => s.name === 'Communication')?.score || 0;

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
        setTimeout(() => navigate('/dashboard'), 2000);
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
          <h3>Session Completed</h3>
          <p>This interview session has already been completed.</p>
          <button onClick={() => navigate('/live-interview-list')}>Close</button>
        </div>
      </div>
    );
  }

  if (showFeedbackSuccess) {
    return <div className="thank-you-screen"><h2>Feedback Submitted Successfully! Redirecting...</h2></div>;
  }

  if (showInterviewReport) {
    return (
      <div className="feedback-overlay">
        <div className="feedback-modal" style={{ width: '600px', textAlign: 'left' }}>
          <h2>Interview Report</h2>
          <p>Please provide your evaluation for {candidateName}</p>
          
          <div className="ratings-section">
            <h3 style={{ color: 'white', marginBottom: '10px' }}>Overall Rating</h3>
            {[1, 2, 3, 4, 5].map(star => (
              <i key={star} onClick={() => handleStarClick('overallRating', star)} className={`fas fa-star ${ratings.overallRating >= star ? 'active' : ''}`} style={{ cursor: 'pointer', color: ratings.overallRating >= star ? '#fbbf24' : '#475569', fontSize: '28px', marginRight: '8px' }}></i>
            ))}
          </div>
          
          <div className="skills-section" style={{ marginTop: '24px' }}>
            <h3 style={{ color: 'white', marginBottom: '12px' }}>Skills Assessment</h3>
            {skills.map((skill, idx) => (
              <div key={idx} style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <label style={{ color: '#94a3b8' }}>{skill.name}</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input type="number" min="0" max="10" value={skill.score} onChange={e => handleSkillScoreChange(idx, e.target.value)} style={{ width: '60px', padding: '6px', background: '#0f172a', border: '1px solid #334155', color: 'white', borderRadius: '4px' }} />
                  <span style={{ color: '#475569' }}>/ 10</span>
                </div>
              </div>
            ))}
          </div>

          <div className="feedback-section" style={{ marginTop: '24px' }}>
            <h3 style={{ color: 'white', marginBottom: '8px' }}>Detailed Feedback</h3>
            <textarea 
              value={feedback}
              onChange={e => setFeedback(e.target.value)}
              placeholder="Enter detailed feedback here..."
              style={{ minHeight: '100px' }}
            />
          </div>

          <div className="actions-section" style={{ marginTop: '30px', display: 'flex', gap: '12px' }}>
             <button className="btn-submit" onClick={() => confirmEndInterview('Qualified')} style={{ background: '#10b981', flex: 1, marginTop: 0 }}>Qualified</button>
             <button className="btn-submit" onClick={() => confirmEndInterview('Rejected')} style={{ background: '#ef4444', flex: 1, marginTop: 0 }}>Rejected</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
    <div className={`live-interview-interviewer ${chatPanelVisible ? 'chat-active' : ''}`}>
      <div className="notifications-container" style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 9999 }}>
        {notifications.map(n => (
          <div key={n.id} className={`session-popup ${n.severity}`} style={{ marginBottom: '10px', padding: '10px', background: '#333', color: '#fff', borderRadius: '5px' }}>
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
          <ConnectionOverlay status={connectionStatus} />

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

export default LiveInterviewInterviewer;