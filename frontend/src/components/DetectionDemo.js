import React, { useEffect, useState } from 'react';
import '../styles/DetectionDemo.css';

/*
  Full Detection Scenarios:
  1. Identity Verified (green) 
  2. Phone Detected (red) - scanning questions
  3. Looking Away (yellow) - not facing camera
  4. Tab Switch (red) - left interview window
  5. Multiple Faces (red) - shows TWO face silhouettes
  6. Audio Anomaly (red) - whispering / external voice
  7. Copy-Paste (red) - pasting code from outside
  8. No Face (yellow) - candidate left frame
  9. Suspicious Eye Movement (yellow) - reading from another screen
  10. Session Report (blue)
*/

const SCENES = [
  {
    id: 'verified',
    duration: 3500,
    dot: '#10B981',
    status: 'MONITORING',
    face1: true, face1Class: '', face1Tag: 'IDENTITY VERIFIED',
    face2: false,
    phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: { type: 'success', title: '✓ IDENTITY CONFIRMED', msg: 'Face matched with registered photo. Interview active.' },
    incidents: 0,
  },
  {
    id: 'phone',
    duration: 4500,
    dot: '#DC2626',
    status: 'ALERT',
    face1: true, face1Class: 'alert', face1Tag: 'VIOLATION',
    face2: false,
    phone: true, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: { type: 'danger', title: '⚠ PHONE DETECTED', msg: 'Mobile device in frame — candidate scanning questions. Flagged.' },
    incidents: 1,
  },
  {
    id: 'clear1',
    duration: 1800,
    dot: '#10B981', status: 'MONITORING',
    face1: true, face1Class: '', face1Tag: 'FACE VERIFIED',
    face2: false, phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: null, incidents: 1,
  },
  {
    id: 'lookaway',
    duration: 3500,
    dot: '#F59E0B',
    status: 'WARNING',
    face1: true, face1Class: 'warning', face1Tag: 'LOOKING AWAY',
    face2: false,
    phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    imgShift: 'shift-right',
    alert: { type: 'warning', title: '👁 NOT FACING CAMERA', msg: 'Candidate looking away. Please face the camera to continue.' },
    incidents: 1,
  },
  {
    id: 'clear2',
    duration: 1800,
    dot: '#10B981', status: 'MONITORING',
    face1: true, face1Class: '', face1Tag: 'FACE VERIFIED',
    face2: false, phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: null, incidents: 1,
  },
  {
    id: 'tabswitch',
    duration: 4000,
    dot: '#DC2626',
    status: 'ALERT',
    face1: false, face1Class: '', face1Tag: '',
    face2: false,
    phone: false, tabSwitch: true, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: { type: 'danger', title: '🖥 TAB SWITCH DETECTED', msg: 'Candidate left the interview window. Incident #2 logged.' },
    incidents: 2,
  },
  {
    id: 'clear3',
    duration: 1800,
    dot: '#10B981', status: 'MONITORING',
    face1: true, face1Class: '', face1Tag: 'FACE VERIFIED',
    face2: false, phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: null, incidents: 2,
  },
  {
    id: 'multiface',
    duration: 4500,
    dot: '#DC2626',
    status: 'ALERT',
    face1: true, face1Class: 'alert', face1Tag: 'PRIMARY',
    face2: true,
    phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: { type: 'danger', title: '👥 MULTIPLE FACES DETECTED', msg: 'Second person in frame. Proxy interview attempt suspected.' },
    incidents: 3,
  },
  {
    id: 'clear4',
    duration: 1800,
    dot: '#10B981', status: 'MONITORING',
    face1: true, face1Class: '', face1Tag: 'FACE VERIFIED',
    face2: false, phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: null, incidents: 3,
  },
  {
    id: 'eyemovement',
    duration: 3500,
    dot: '#F59E0B',
    status: 'WARNING',
    face1: true, face1Class: 'warning', face1Tag: 'SUSPICIOUS',
    face2: false,
    phone: false, tabSwitch: false, noFace: false,
    eyeTrack: true, audioWave: false, copyPaste: false,
    alert: { type: 'warning', title: '👀 SUSPICIOUS EYE MOVEMENT', msg: 'Rapid eye movement detected — possibly reading from another screen.' },
    incidents: 4,
  },
  {
    id: 'clear5',
    duration: 1800,
    dot: '#10B981', status: 'MONITORING',
    face1: true, face1Class: '', face1Tag: 'FACE VERIFIED',
    face2: false, phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: null, incidents: 4,
  },
  {
    id: 'audio',
    duration: 4000,
    dot: '#DC2626',
    status: 'ALERT',
    face1: true, face1Class: 'alert', face1Tag: 'AUDIO ALERT',
    face2: false,
    phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: true, copyPaste: false,
    alert: { type: 'danger', title: '🎤 AUDIO ANOMALY DETECTED', msg: 'External voice or whispering detected. Possible external help.' },
    incidents: 5,
  },
  {
    id: 'clear6',
    duration: 1800,
    dot: '#10B981', status: 'MONITORING',
    face1: true, face1Class: '', face1Tag: 'FACE VERIFIED',
    face2: false, phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: null, incidents: 5,
  },
  {
    id: 'copypaste',
    duration: 4000,
    dot: '#DC2626',
    status: 'ALERT',
    face1: true, face1Class: 'alert', face1Tag: 'VIOLATION',
    face2: false,
    phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: true,
    alert: { type: 'danger', title: '📋 COPY-PASTE DETECTED', msg: 'Code pasted from external source during coding assessment.' },
    incidents: 6,
  },
  {
    id: 'clear7',
    duration: 1800,
    dot: '#10B981', status: 'MONITORING',
    face1: true, face1Class: '', face1Tag: 'FACE VERIFIED',
    face2: false, phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: null, incidents: 6,
  },
  {
    id: 'noface',
    duration: 3500,
    dot: '#F59E0B',
    status: 'WARNING',
    face1: false, face1Class: '', face1Tag: '',
    face2: false,
    phone: false, tabSwitch: false, noFace: true,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: { type: 'warning', title: '🚫 NO FACE DETECTED', msg: 'Candidate has left the camera frame. Waiting for return...' },
    incidents: 7,
  },
  {
    id: 'report',
    duration: 4500,
    dot: '#2563EB',
    status: 'COMPLETE',
    face1: true, face1Class: '', face1Tag: 'FACE VERIFIED',
    face2: false,
    phone: false, tabSwitch: false, noFace: false,
    eyeTrack: false, audioWave: false, copyPaste: false,
    alert: { type: 'info', title: '📊 SESSION INTEGRITY REPORT', msg: '7 incidents detected & logged. Full report generated for recruiter.' },
    incidents: 7,
  },
];

/* SVG Face Silhouette */
const FaceSVG = ({ color = '#3B82F6', size = 100, opacity = 0.5 }) => (
  <svg width={size} height={size} viewBox="0 0 120 150" fill="none" style={{ opacity }}>
    {/* Head outline */}
    <ellipse cx="60" cy="55" rx="38" ry="45" stroke={color} strokeWidth="2" fill="none" />
    {/* Eyes */}
    <ellipse cx="44" cy="50" rx="7" ry="4" stroke={color} strokeWidth="1.5" fill="none" />
    <ellipse cx="76" cy="50" rx="7" ry="4" stroke={color} strokeWidth="1.5" fill="none" />
    <circle cx="44" cy="50" r="2.5" fill={color} opacity="0.6" />
    <circle cx="76" cy="50" r="2.5" fill={color} opacity="0.6" />
    {/* Nose */}
    <path d="M60 55 L56 68 L64 68 Z" stroke={color} strokeWidth="1" fill="none" />
    {/* Mouth */}
    <path d="M48 78 Q60 88 72 78" stroke={color} strokeWidth="1.5" fill="none" />
    {/* Neck */}
    <line x1="50" y1="98" x2="50" y2="120" stroke={color} strokeWidth="1.5" />
    <line x1="70" y1="98" x2="70" y2="120" stroke={color} strokeWidth="1.5" />
    {/* Shoulders */}
    <path d="M20 148 Q35 120 50 120" stroke={color} strokeWidth="2" fill="none" />
    <path d="M100 148 Q85 120 70 120" stroke={color} strokeWidth="2" fill="none" />
    {/* Scan grid lines on face */}
    <line x1="30" y1="35" x2="90" y2="35" stroke={color} strokeWidth="0.3" opacity="0.3" />
    <line x1="28" y1="50" x2="92" y2="50" stroke={color} strokeWidth="0.3" opacity="0.3" />
    <line x1="30" y1="65" x2="90" y2="65" stroke={color} strokeWidth="0.3" opacity="0.3" />
    <line x1="35" y1="80" x2="85" y2="80" stroke={color} strokeWidth="0.3" opacity="0.3" />
    <line x1="45" y1="15" x2="45" y2="95" stroke={color} strokeWidth="0.3" opacity="0.3" />
    <line x1="60" y1="10" x2="60" y2="95" stroke={color} strokeWidth="0.3" opacity="0.3" />
    <line x1="75" y1="15" x2="75" y2="95" stroke={color} strokeWidth="0.3" opacity="0.3" />
  </svg>
);

/* SVG Laptop — positioned in front of the person */
const LaptopSVG = () => (
  <svg width="220" height="90" viewBox="0 0 260 100" fill="none" className="dd-laptop-svg">
    {/* Screen */}
    <rect x="45" y="2" width="170" height="55" rx="5" stroke="#3B82F6" strokeWidth="1.5" fill="rgba(37,99,235,0.04)" />
    {/* Screen content lines */}
    <rect x="58" y="14" width="60" height="3" rx="1" fill="rgba(59,130,246,0.25)" />
    <rect x="58" y="21" width="90" height="3" rx="1" fill="rgba(59,130,246,0.15)" />
    <rect x="58" y="28" width="45" height="3" rx="1" fill="rgba(59,130,246,0.2)" />
    <rect x="58" y="35" width="75" height="3" rx="1" fill="rgba(59,130,246,0.12)" />
    <rect x="58" y="42" width="55" height="3" rx="1" fill="rgba(59,130,246,0.18)" />
    {/* Webcam dot */}
    <circle cx="130" cy="6" r="2" fill="#10B981" opacity="0.8" />
    {/* Hinge */}
    <rect x="40" y="57" width="180" height="4" rx="2" fill="rgba(59,130,246,0.15)" />
    {/* Keyboard base */}
    <path d="M25 61 L40 57 L220 57 L235 61 L240 95 L20 95 Z" fill="rgba(37,99,235,0.06)" stroke="#3B82F6" strokeWidth="1" opacity="0.5" />
    {/* Keyboard keys */}
    <rect x="50" y="65" width="160" height="5" rx="1" fill="rgba(59,130,246,0.08)" />
    <rect x="55" y="73" width="150" height="5" rx="1" fill="rgba(59,130,246,0.06)" />
    <rect x="60" y="81" width="140" height="5" rx="1" fill="rgba(59,130,246,0.05)" />
    {/* Trackpad */}
    <rect x="100" y="89" width="60" height="4" rx="2" fill="rgba(59,130,246,0.08)" />
  </svg>
);

function DetectionDemo() {
  const [sceneIdx, setSceneIdx] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const scene = SCENES[sceneIdx];
    const timer = setTimeout(() => {
      setFade(false);
      setTimeout(() => {
        setSceneIdx((prev) => (prev + 1) % SCENES.length);
        setFade(true);
      }, 350);
    }, scene.duration);
    return () => clearTimeout(timer);
  }, [sceneIdx]);

  const s = SCENES[sceneIdx];

  return (
    <div className="dd-card">
      {/* Top bar */}
      <div className="dd-topbar">
        <div className="dd-topbar-left">
          <span className="dd-dot" style={{ background: s.dot, boxShadow: `0 0 10px ${s.dot}` }} />
          <span className="dd-status" style={{ color: s.dot }}>{s.status}</span>
        </div>
        <span className="dd-topbar-brand">VERIFIHIREAI</span>
      </div>

      {/* Main area */}
      <div className={`dd-main ${fade ? 'dd-in' : 'dd-out'}`}>
        {/* Scanning line */}
        <div className="dd-scan" />

        {/* Primary face */}
        {!s.tabSwitch && !s.noFace && (
          <div className={`dd-cam ${s.imgShift || ''}`}>
            <FaceSVG color="#3B82F6" size={140} opacity={0.5} />
          </div>
        )}

        {/* Laptop in front of person */}
        {!s.tabSwitch && !s.noFace && (
          <div className="dd-laptop-wrap">
            <LaptopSVG />
          </div>
        )}

        {/* No face - empty frame */}
        {s.noFace && (
          <div className="dd-noface">
            <div className="dd-noface-circle" />
            <span className="dd-noface-label">NO FACE IN FRAME</span>
          </div>
        )}

        {/* Face bounding box - primary */}
        {s.face1 && (
          <div className={`dd-face ${s.face1Class}`}>
            <span className="dd-face-tag">{s.face1Tag}</span>
          </div>
        )}

        {/* Second face + bounding box for multi-face detection */}
        {s.face2 && (
          <div className="dd-face2-container">
            <FaceSVG color="#DC2626" size={70} opacity={0.45} />
            <div className="dd-face2-box">
              <span className="dd-face2-tag">UNKNOWN FACE</span>
            </div>
          </div>
        )}

        {/* Phone indicator */}
        {s.phone && (
          <div className="dd-phone">
            <div className="dd-phone-box">
              <span className="dd-phone-icon">📱</span>
            </div>
            <span className="dd-phone-tag">PHONE DETECTED</span>
          </div>
        )}

        {/* Tab switch overlay */}
        {s.tabSwitch && (
          <div className="dd-tabswitch">
            <div className="dd-tab-icon">🖥️</div>
            <div className="dd-tab-title">Tab Switch Detected</div>
            <div className="dd-tab-sub">Candidate left the interview window</div>
          </div>
        )}

        {/* Eye tracking indicator */}
        {s.eyeTrack && (
          <div className="dd-eyetrack">
            <div className="dd-eye-arrow dd-eye-left">◀</div>
            <div className="dd-eye-arrow dd-eye-right">▶</div>
            <span className="dd-eye-tag">RAPID EYE MOVEMENT</span>
          </div>
        )}

        {/* Audio anomaly indicator */}
        {s.audioWave && (
          <div className="dd-audio">
            <div className="dd-audio-bars">
              <span className="dd-bar dd-bar1" />
              <span className="dd-bar dd-bar2" />
              <span className="dd-bar dd-bar3" />
              <span className="dd-bar dd-bar4" />
              <span className="dd-bar dd-bar5" />
              <span className="dd-bar dd-bar6" />
              <span className="dd-bar dd-bar7" />
            </div>
            <span className="dd-audio-tag">🎤 EXTERNAL VOICE</span>
          </div>
        )}

        {/* Copy-paste indicator */}
        {s.copyPaste && (
          <div className="dd-copypaste">
            <div className="dd-cp-icon">📋</div>
            <div className="dd-cp-code">
              <span className="dd-cp-line">{'>'} Ctrl+V detected</span>
              <span className="dd-cp-line dd-cp-red">{'>'} External code pasted</span>
              <span className="dd-cp-line dd-cp-blink">{'>'} Flagging incident...</span>
            </div>
          </div>
        )}

        {/* Alert banner */}
        {s.alert && (
          <div className={`dd-alert dd-alert-${s.alert.type}`}>
            <span className="dd-alert-title">{s.alert.title}</span>
            <p className="dd-alert-msg">{s.alert.msg}</p>
          </div>
        )}
      </div>

      {/* Bottom metrics */}
      <div className="dd-bottom">
        <div className="dd-metric">
          <span className="dd-metric-val">98.7%</span>
          <span className="dd-metric-lbl">Accuracy</span>
        </div>
        <div className="dd-metric">
          <span className="dd-metric-val">0.3s</span>
          <span className="dd-metric-lbl">Response</span>
        </div>
        <div className="dd-metric">
          <span className={`dd-metric-val ${s.incidents > 0 ? 'dd-red' : ''}`}>{s.incidents}</span>
          <span className="dd-metric-lbl">Incidents</span>
        </div>
      </div>
    </div>
  );
}

export default DetectionDemo;
