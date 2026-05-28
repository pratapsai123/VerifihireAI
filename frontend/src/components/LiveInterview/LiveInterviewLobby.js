import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../../apiConfig';

const LiveInterviewLobby = ({ token, participantToken, onJoin }) => {
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const videoRef = useRef(null);
  const localStreamRef = useRef(null);
  const [localStream, setLocalStream] = useState(null);
  const [micEnabled, setMicEnabled] = useState(false);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [devices, setDevices] = useState({ audioInputs: [], videoInputs: [], audioOutputs: [] });
  const [selectedMic, setSelectedMic] = useState('');
  const [selectedCamera, setSelectedCamera] = useState('');
  const [selectedSpeaker, setSelectedSpeaker] = useState('');
  const [devicesEnumerated, setDevicesEnumerated] = useState(false);

  // 1. Fetch Interview / Candidate Details
  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        let sessionToken = token;
        let cName = '';
        let roleName = 'candidate';

        if (participantToken) {
          const pResp = await axios.get(`${API_BASE_URL}/interviews/participants/validate/${participantToken}/`);
          if (pResp.data) {
            sessionToken = pResp.data.session_id;
            cName = pResp.data.name;
            roleName = pResp.data.role;
          }
        }

        if (sessionToken) {
          const invResp = await axios.get(`${API_BASE_URL}/interviews/invitations/${sessionToken}/`);
          if (invResp.data) {
            setCandidate({
              ...invResp.data,
              name: cName || invResp.data.name,
              role: roleName
            });
          }
        } else {
          setError('No interview token or participant token provided.');
        }
      } catch (err) {
        console.error('Error fetching interview details:', err);
        setError(err.response?.data?.error || err.message || 'Failed to load interview details.');
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [token, participantToken]);

  // 2. Request initial permissions and list media devices
  useEffect(() => {
    const initDevices = async () => {
      try {
        const initialStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
        // Stop tracks immediately so preview startPreviewStream takes over cleanly
        initialStream.getTracks().forEach(track => track.stop());

        const deviceList = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = deviceList.filter(d => d.kind === 'audioinput');
        const videoInputs = deviceList.filter(d => d.kind === 'videoinput');
        const audioOutputs = deviceList.filter(d => d.kind === 'audiooutput');

        setDevices({ audioInputs, videoInputs, audioOutputs });

        if (audioInputs.length > 0) setSelectedMic(audioInputs[0].deviceId);
        if (videoInputs.length > 0) setSelectedCamera(videoInputs[0].deviceId);
        if (audioOutputs.length > 0) setSelectedSpeaker(audioOutputs[0].deviceId);

        setMicEnabled(true);
        setCameraEnabled(true);
        setDevicesEnumerated(true);
      } catch (err) {
        console.error('Device access error:', err);
        setError('Permissions Required: Camera and microphone access is required for the interview. Please allow access in your browser and refresh the page.');
        setLoading(false);
      }
    };

    initDevices();
  }, []);

  // 3. Reactively update the media stream when mic/camera states or selected devices change
  const startPreviewStream = async () => {
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
    }

    if (!micEnabled && !cameraEnabled) {
      setLocalStream(null);
      return;
    }

    const constraints = {
      audio: micEnabled ? (selectedMic ? { deviceId: { exact: selectedMic } } : true) : false,
      video: cameraEnabled ? (selectedCamera ? { deviceId: { exact: selectedCamera } } : true) : false
    };

    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      localStreamRef.current = stream;
      setLocalStream(stream);
    } catch (err) {
      console.warn('Overconstrained or error with exact constraints, retrying with ideal constraints:', err);
      const fallbackConstraints = {
        audio: micEnabled ? (selectedMic ? { deviceId: { ideal: selectedMic } } : true) : false,
        video: cameraEnabled ? (selectedCamera ? { deviceId: { ideal: selectedCamera } } : true) : false
      };
      try {
        const stream = await navigator.mediaDevices.getUserMedia(fallbackConstraints);
        localStreamRef.current = stream;
        setLocalStream(stream);
      } catch (err2) {
        console.error('Error starting preview stream even with fallback constraints:', err2);
        if (err2.name === 'NotAllowedError' || err2.name === 'PermissionDeniedError') {
          setCameraEnabled(false);
          setMicEnabled(false);
        }
      }
    }
  };

  useEffect(() => {
    if (devicesEnumerated && (selectedMic || selectedCamera)) {
      startPreviewStream();
    }
    return () => {
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [micEnabled, cameraEnabled, selectedMic, selectedCamera, devicesEnumerated]);

  // 4. Safely sync the active media stream and speaker output to the video element whenever it is rendered
  useEffect(() => {
    const videoEl = videoRef.current;
    if (!videoEl) return;

    if (videoEl.srcObject !== localStream) {
      videoEl.srcObject = localStream;
      videoEl.muted = true;
    }

    if (selectedSpeaker && typeof videoEl.setSinkId === 'function') {
      videoEl.setSinkId(selectedSpeaker)
        .then(() => console.log(`Audio output device set to ${selectedSpeaker}`))
        .catch(err => console.error('Error setting audio output sink ID:', err));
    }
  }, [localStream, selectedSpeaker]);

  // 5. Play a pleasant synthesized tone to test the speaker output
  const playTestSound = () => {
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      
      const playBeep = () => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(440, audioCtx.currentTime); // A4 note
        
        gain.gain.setValueAtTime(0, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(0.2, audioCtx.currentTime + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.8);
        
        osc.start(audioCtx.currentTime);
        osc.stop(audioCtx.currentTime + 0.8);
      };

      if (selectedSpeaker && typeof audioCtx.setSinkId === 'function') {
        audioCtx.setSinkId(selectedSpeaker)
          .then(playBeep)
          .catch(err => {
            console.error('Error setting AudioContext sink ID:', err);
            playBeep();
          });
      } else {
        playBeep();
      }
    } catch (e) {
      console.error('Error playing test sound:', e);
    }
  };

  const handleJoin = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
    }
    onJoin({
      cameraOn: cameraEnabled,
      micOn: micEnabled,
      videoDeviceId: selectedCamera,
      audioDeviceId: selectedMic,
      speakerDeviceId: selectedSpeaker
    });
  };

  const duration = (start, end) => {
    if (!start || !end) return 45;
    const diffMs = new Date(end) - new Date(start);
    return Math.round(diffMs / 60000);
  };

  const formatDateTime = (isoString, timeZone) => {
    if (!isoString) return 'Not scheduled';
    try {
      const date = new Date(isoString);
      return date.toLocaleString('en-US', {
        timeZone: timeZone || undefined,
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    } catch (e) {
      return isoString;
    }
  };

  if (error && !candidate) {
    return (
      <div className="li-lobby-error">
        <div className="li-lobby-error-card">
          <i className="fas fa-exclamation-triangle li-lobby-error-icon"></i>
          <h2 className="li-lobby-error-title">Unable to Join</h2>
          <p className="li-lobby-error-msg">{error}</p>
          <button className="li-lobby-join-btn" onClick={() => window.location.reload()}>
            <i className="fas fa-redo"></i> Retry
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="li-lobby-loading">
        <div className="li-lobby-loading-spinner"></div>
        <p>Preparing interview lobby...</p>
      </div>
    );
  }

  const candidateInitials = candidate?.name ? candidate.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'C';

  return (
    <div className="li-lobby-wrapper">
      <div className="li-lobby-card">
        {/* Left Side: Video Preview & Controls */}
        <div className="li-lobby-video-section">
          <div className="li-lobby-video-wrapper">
            <video
              ref={videoRef}
              className="li-lobby-video-element"
              autoPlay
              playsInline
              muted
              style={{ display: cameraEnabled && localStream ? 'block' : 'none' }}
            />
            {(!cameraEnabled || !localStream) && (
              <div className="li-lobby-camera-placeholder">
                <i className="fas fa-video-slash"></i>
                <span>Camera is off</span>
              </div>
            )}
          </div>

          <div className="li-lobby-video-controls">
            <button
              onClick={() => setMicEnabled(!micEnabled)}
              title={micEnabled ? "Mute Microphone" : "Unmute Microphone"}
              className={`li-lobby-control-btn ${micEnabled ? 'on' : 'off'}`}
            >
              <i className={`fas ${micEnabled ? 'fa-microphone' : 'fa-microphone-slash'}`}></i>
            </button>
            <button
              onClick={() => setCameraEnabled(!cameraEnabled)}
              title={cameraEnabled ? "Turn Camera Off" : "Turn Camera On"}
              className={`li-lobby-control-btn ${cameraEnabled ? 'on' : 'off'}`}
            >
              <i className={`fas ${cameraEnabled ? 'fa-video' : 'fa-video-slash'}`}></i>
            </button>
          </div>

          <div className="li-lobby-device-selectors">
            <div className="li-lobby-select-container">
              <select
                value={selectedMic}
                onChange={(e) => setSelectedMic(e.target.value)}
                title="Select microphone"
                className="li-lobby-select"
              >
                {devices.audioInputs.map(d => (
                  <option key={d.deviceId} value={d.deviceId}>
                    {d.label || `Microphone ${devices.audioInputs.indexOf(d) + 1}`}
                  </option>
                ))}
              </select>
              <div className="li-lobby-select-arrow"><i className="fas fa-chevron-down"></i></div>
            </div>

            <div className="li-lobby-select-container" style={{ display: 'flex', gap: '8px' }}>
              <div style={{ flex: 1, position: 'relative' }}>
                <select
                  value={selectedSpeaker}
                  onChange={(e) => setSelectedSpeaker(e.target.value)}
                  title="Select speaker"
                  className="li-lobby-select"
                >
                  {devices.audioOutputs.length > 0 ? (
                    devices.audioOutputs.map(d => (
                      <option key={d.deviceId} value={d.deviceId}>
                        {d.label || `Speaker ${devices.audioOutputs.indexOf(d) + 1}`}
                      </option>
                    ))
                  ) : (
                    <option value="default">Speakers (Default)</option>
                  )}
                </select>
                <div className="li-lobby-select-arrow"><i className="fas fa-chevron-down"></i></div>
              </div>
              <button
                type="button"
                onClick={playTestSound}
                className="li-lobby-test-speaker-btn"
                title="Test Speaker Sound"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'rgba(59, 130, 246, 0.15)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: '12px',
                  color: '#60a5fa',
                  cursor: 'pointer',
                  padding: '0 14px',
                  fontSize: '0.825rem',
                  fontWeight: '600',
                  transition: 'all 0.2s ease',
                  whiteSpace: 'nowrap'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.25)';
                  e.currentTarget.style.color = '#93c5fd';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.15)';
                  e.currentTarget.style.color = '#60a5fa';
                }}
              >
                <i className="fas fa-volume-up" style={{ marginRight: '6px' }}></i> Test
              </button>
            </div>

            <div className="li-lobby-select-container">
              <select
                value={selectedCamera}
                onChange={(e) => setSelectedCamera(e.target.value)}
                title="Select camera"
                className="li-lobby-select"
              >
                {devices.videoInputs.map(d => (
                  <option key={d.deviceId} value={d.deviceId}>
                    {d.label || `Camera ${devices.videoInputs.indexOf(d) + 1}`}
                  </option>
                ))}
              </select>
              <div className="li-lobby-select-arrow"><i className="fas fa-chevron-down"></i></div>
            </div>
          </div>
        </div>

        {/* Right Side: Details & Join CTA */}
        <div className="li-lobby-info-section">
          <div className="li-lobby-header">
            <h2 className="li-lobby-title">Ready to join?</h2>
            <p className="li-lobby-subtitle">Confirm your details and settings before entering</p>
          </div>

          <div className="li-lobby-details-card">
            <h3 className="li-lobby-details-title">
              <i className="fas fa-calendar-alt"></i> Interview Details
            </h3>
            <div className="li-lobby-details-grid">
              <div className="li-lobby-detail-item">
                <i className="fas fa-user li-lobby-detail-icon"></i>
                <div>
                  <p className="li-lobby-detail-label">Candidate</p>
                  <p className="li-lobby-detail-value">{candidate?.name || 'N/A'}</p>
                </div>
              </div>
              <div className="li-lobby-detail-item">
                <i className="fas fa-briefcase li-lobby-detail-icon"></i>
                <div>
                  <p className="li-lobby-detail-label">Interview Type</p>
                  <p className="li-lobby-detail-value">{candidate?.interview?.name || 'Live Technical Interview'}</p>
                </div>
              </div>
              <div className="li-lobby-detail-item">
                <i className="fas fa-clock li-lobby-detail-icon"></i>
                <div>
                  <p className="li-lobby-detail-label">Start Time</p>
                  <p className="li-lobby-detail-value">{formatDateTime(candidate?.start_time, candidate?.time_zone)}</p>
                </div>
              </div>
              <div className="li-lobby-detail-item">
                <i className="fas fa-stopwatch li-lobby-detail-icon"></i>
                <div>
                  <p className="li-lobby-detail-label">Duration</p>
                  <p className="li-lobby-detail-value">{duration(candidate?.start_time, candidate?.end_time)} minutes</p>
                </div>
              </div>
            </div>
          </div>

          <div className="li-lobby-user-info">
            <div className="li-lobby-avatar">{candidateInitials}</div>
            <p className="li-lobby-user-name">{candidate?.name} is ready</p>
            {candidate?.token && (
              <p className="li-lobby-user-token">Token: {candidate.token.substring(0, 8)}...</p>
            )}
          </div>

          <div className="li-lobby-notes-card">
            <h4 className="li-lobby-notes-title">
              <i className="fas fa-exclamation-triangle"></i> Important Notes
            </h4>
            <ul className="li-lobby-notes-list">
              <li>• Ensure you have a stable internet connection</li>
              <li>• Use Chrome or Firefox browser for best compatibility</li>
              <li>• Test your camera and microphone before joining</li>
              <li>• Find a quiet environment for the interview</li>
            </ul>
          </div>

          <button className="li-lobby-join-btn" onClick={handleJoin}>
            <i className="fas fa-video"></i> Join Interview Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default LiveInterviewLobby;
