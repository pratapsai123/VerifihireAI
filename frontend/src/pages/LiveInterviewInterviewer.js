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
  // 🔥 FIX: Ref that is always synchronously up-to-date — safe to use inside handleMessage closures
  const myUserIdRef = useRef(null);
  // 🔥 FIX: Ref mirror of remoteParticipants so initializeMedia always reads fresh data
  const remoteParticipantsRef = useRef({});
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
    createPeerConnection, removePeerConnection, initLocalStream,
    createVideoOffer, handleVideoOffer, handleVideoAnswer, handleIceCandidate, stopWebRTC
  } = useWebRTC(stableSendMessage, myUserId);

  const {
    isScreenSharing, screenShareLocked, setScreenShareLocked, screenShareHolder, setScreenShareHolder,
    toggleScreenShare, stopScreenSharing, handleScreenShareGranted, handleScreenShareDenied, screenShareStreamRef
  } = useScreenShare(peerConnectionsRef, localStreamRef, stableSendMessage, showNotification, MY_ROLE, createVideoOffer);

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
      }, { withCredentials: true }).catch(() => { });
    } catch (e) { console.warn('Failed to persist total time on end:', e); }

    // Redirect to the new dedicated Feedback Page
    navigate(`/feedback-page?session=${encodeURIComponent(sessionId)}&candidate=${encodeURIComponent(candidateName)}&interviewer=${encodeURIComponent(interviewerName)}&time=${encodeURIComponent(timer)}`);
  }, [sessionKey, timer, sessionId, stableSendMessage, stopWebRTC, navigate, candidateName, interviewerName]);

  // Message Handler
  const handleMessage = useCallback(async (data) => {
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
            // 🔥 FIX: Always update the ref synchronously
            remoteParticipantsRef.current = { ...remoteParticipantsRef.current, [p.user_id]: entry };
            setRemoteParticipants(prev => ({ ...prev, [p.user_id]: entry }));

            // 🔥 FIX: Only create peer+offer NOW if local stream is already ready.
            // If not ready, initializeMedia() will handle it after the stream is obtained.
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
        showNotification(`${data.user} joined the session`);
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
        showNotification(`${data.user} left the session`, 'warning');
        setRemoteParticipants(prev => {
          const next = { ...prev };
          delete next[data.user_id];
          delete remoteParticipantsRef.current[data.user_id];
          return next;
        });
        removePeerConnection(data.user_id);
        break;
      case 'ready_for_webrtc': {
        console.log(`✅ ready_for_webrtc from ${data.sender_id}`);
        const remoteUserId = data.sender_id;

        if (remoteUserId === myUserIdRef.current) break;

        // 🔥 FIX: Check peer health by iceConnectionState AND whether remote tracks exist
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

  // 🔥 Centralized Stream Router
  const handleRemoteStream = useCallback((userId, stream) => {
    setRemoteParticipants(prev => {
      const p = prev[userId];
      if (!p) return prev;

      const signaledIdMatch = p.screenStreamId === stream.id;
      const isVideoOnly = stream.getAudioTracks().length === 0 && stream.getVideoTracks().length > 0;
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

      // 🔥 FIX: Only broadcast ready_for_webrtc. Do NOT proactively send offers here.
      // Existing participants will receive ready_for_webrtc and respond with an offer.
      // This ensures exactly ONE offer per pair (no glare / double-offer).
      console.log('🗣️ Broadcasting ready_for_webrtc');
      sendMessage({ type: 'ready_for_webrtc', user: interviewerName, role: MY_ROLE });

    }).catch(err => {
      setMediaLoading(false);
      setMediaError(true);
      showNotification('Could not access camera/mic. Please check permissions.', 'error');
    });
  }, [initLocalStream, sendMessage, showNotification, interviewerName]);

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

    localStreamRef.current.getVideoTracks().forEach(track => {
      track.enabled = newCameraOn;
    });

    sendMessage({ type: 'media_state', media: 'camera', enabled: newCameraOn });
  }, [isCameraOn, localStreamRef, sendMessage]);


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
      participant_token: participantToken,
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
    if (inviteEmail.toLowerCase().endsWith('@gmail.com')) {
      showNotification('Gmail addresses are not allowed for panel members.', 'error');
      return;
    }
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
      showNotification(error.response?.data?.error || 'Failed to generate invite link', 'error');
    }
  };

  if (sessionExpired && !showInterviewReport && !showFeedbackSuccess) {
    return (
      <div className="session-expired-modal">
        <div className="session-expired-content">
          <div className="session-expired-icon">✓</div>
          <h3 className="session-expired-title">Session Completed</h3>
          <p className="session-expired-message">This interview session has already been completed.</p>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginTop: '20px' }}>
            <button className="btn-close-window" style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '4px', cursor: 'pointer' }} onClick={() => navigate(`/feedback-page?session=${encodeURIComponent(sessionId)}&candidate=${encodeURIComponent(candidateName)}&interviewer=${encodeURIComponent(interviewerName)}&time=${encodeURIComponent(timer)}`)}>Provide Feedback</button>
            <button className="btn-close-window" style={{ background: '#e2e8f0', color: '#1e293b', border: 'none', padding: '10px 20px', borderRadius: '4px', cursor: 'pointer' }} onClick={() => navigate('/live-interview-list')}>Back to Dashboard</button>
          </div>
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
              localStreamRef={localStreamRef}
              localScreenStream={screenShareStreamRef.current}
              isRemoteCameraOn={isRemoteCameraOn}
              isRemoteScreenSharing={isRemoteScreenSharing}
              bothPartiesConnected={bothPartiesConnected}
              isCameraOn={isCameraOn}
              isLocalScreenSharing={isScreenSharing}
              localName={interviewerName}
              localRole={MY_ROLE}
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