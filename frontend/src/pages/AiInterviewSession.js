import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import RecordRTC, { StereoAudioRecorder } from 'recordrtc';
import ReadyPlayerMeAvatar from '../components/ReadyPlayerMeAvatar';
import '../styles/Dashboard.css';
import '../styles/AiInterviewSession.css';
import { API_BASE_URL, DEEPFACE_BASE_URL, DEEPFACE_WS_URL } from '../apiConfig';
import { logCandidateActivity } from '../utils/activityLogger';

const AiInterviewSession = () => {
    const VIOLATION_COOLDOWN_MS = 10000;
    const { token } = useParams();
    const navigate = useNavigate();
    const [candidateName, setCandidateName] = useState('Candidate');
    const [candidateData, setCandidateData] = useState(null);
    const [maxQuestions, setMaxQuestions] = useState(13);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [questions, setQuestions] = useState([]);
    const [chatMessages, setChatMessages] = useState([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [userInputMode, setUserInputMode] = useState('audio'); // 'audio' or 'text'
    const [aiStatus, setAiStatus] = useState('Indu is Online');
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [progress, setProgress] = useState(0);
    const [showQuotaWarning, setShowQuotaWarning] = useState(false);
    const [responseInput, setResponseInput] = useState('');
    const [integrityBreach, setIntegrityBreach] = useState({ active: false, text: '' });
    const [aiToast, setAiToast] = useState({ active: false, text: '', urgent: false });
    const [isCompleted, setIsCompleted] = useState(false);
    const [timeLeft, setTimeLeft] = useState(null); // Timer in seconds
    const [sttReady, setSttReady] = useState(false); // New state for WS status
    const [silenceCountdown, setSilenceCountdown] = useState(0);
    const [isPermissionsGranted, setIsPermissionsGranted] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [isScreenSharing, setIsScreenSharing] = useState(false);
    const [isPaused, setIsPaused] = useState(false); // Pause timer during interruptions

    // ── Registration State ──
    const [isFaceRegistered, setIsFaceRegistered] = useState(false);
    const [wizardStep, setWizardStep] = useState(0); 
    const [capturedImage, setCapturedImage] = useState(null);
    const regVideoRef = useRef(null);

    // ── DeepFace Proctoring State ──
    const [dfSessionId, setDfSessionId] = useState(null);
    const [dfVerified, setDfVerified] = useState(null);
    const [dfEngagement, setDfEngagement] = useState(0);
    const [dfFaceCount, setDfFaceCount] = useState(0);
    const [dfFacePresent, setDfFacePresent] = useState(false);
    const [dfHeadDir, setDfHeadDir] = useState('FORWARD');

    const getDeepfacePersonId = useCallback(() => {
        // Stable identity for DeepFace across registration and session start.
        return String(token || '').trim().toLowerCase();
    }, [token]);

    // Refs
    const videoRef = useRef(null);
    const chatContainerRef = useRef(null);
    const recognitionRef = useRef(null);
    const synthRef = useRef(window.speechSynthesis);
    const voicesRef = useRef([]);
    const detectorRef = useRef(null);
    const lastDetectionTimeRef = useRef(0);
    const streamRef = useRef(null);
    const chatHistoryRef = useRef([]);
    const isInitializedRef = useRef(false);
    const isProcessingRef = useRef(false);
    const isSpeakingRef = useRef(false);
    const isRecordingRef = useRef(false);
    const isCompletedRef = useRef(false);
    const timeExpiredRef = useRef(false); // Flag to gracefully end after current answer if time runs out
    const silenceTimerRef = useRef(null);
    const globalSilenceTimerRef = useRef(null);
    const nudgeCountRef = useRef(0);
    const transcriptRef = useRef("");
    const interimTranscriptRef = useRef("");
    const submitHandlerRef = useRef(null);
    const assemblyAIRef = useRef(null);
    const startListeningRef = useRef(null);
    const canvasRef = useRef(null);
    const animationRef = useRef(null);
    const visualizerCtxRef = useRef(null);
    const lastSpokenTimeRef = useRef(Date.now());
    const lastTranscriptStrRef = useRef("");
    const micStreamRef = useRef(null); // Holds the active MediaStream to physically mute/unmute mic hardware
    const consecutiveSilenceRef = useRef(0); // Track consecutive [Silent] answers to auto-exit if candidate leaves
    const lastActivityTimeRef = useRef(Date.now()); // Track ANY candidate activity for grace period
    const screenStreamRef = useRef(null);
    const screenCanvasRef = useRef(null);
    const lastCaptureTimeRef = useRef({}); // Store timestamps per eventType for cooldowns
    const violationCooldownsRef = useRef({}); // Cooldown tracker for violations (10 sec)
    const isFullscreenRef = useRef(false);
    const currentAudioRef = useRef(null);
    const isStartingMicRef = useRef(false);
    const manualMuteRef = useRef(false); // Track if user manually muted mic to prevent auto-resume
    const isNoticePlayingRef = useRef(false);
    const faceEmbeddingHashRef = useRef(null); // Store face embedding hash for duplicate detection
    // DeepFace refs
    const dfWsRef = useRef(null);
    const dfCanvasRef = useRef(null);
    const dfSendIntervalRef = useRef(null);
    const dfSessionIdRef = useRef(null);
    const dfAwaitingRef = useRef(false);
    const dfLastUiUpdateRef = useRef(0); // Throttle HUD state updates to avoid re-render thrashing

    // 1. Load Voices
    useEffect(() => {
        const loadVoices = () => {
            const voices = synthRef.current.getVoices();
            voicesRef.current = voices;
        };
        loadVoices();
        if (synthRef.current.onvoiceschanged !== undefined) {
            synthRef.current.onvoiceschanged = loadVoices;
        }
    }, []);

    // 2. Camera and AI Monitoring
    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: "user" }
            });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                // Force play to ensure visibility across all browsers
                videoRef.current.play().catch(e => console.warn("Auto-play prevented:", e));
            }
            if (regVideoRef.current) {
                regVideoRef.current.srcObject = stream;
                regVideoRef.current.play().catch(e => console.warn("Auto-play prevented:", e));
            }
            streamRef.current = stream;
        } catch (err) {
            console.error("Camera access error:", err);
            setAiToast({ active: true, text: 'Camera Blocked', urgent: true });
        }
    };

    const startScreenShare = async () => {
        try {
            const stream = await navigator.mediaDevices.getDisplayMedia({
                video: { displaySurface: 'monitor' },
                audio: false
            });
            const track = stream.getVideoTracks()[0];

            // Validate entire screen sharing (some browsers may not support displaySurface)
            try {
                const settings = track.getSettings();
                if (settings.displaySurface && settings.displaySurface !== 'monitor') {
                    track.stop();
                    alert('Please share your "Entire Screen" to proceed. Tab/Window sharing is prohibited.');
                    return false;
                }
            } catch (settingsErr) {
                console.warn("Could not verify display surface (browser may not support it):", settingsErr);
                // Continue anyway — screen is shared, just can't verify type
            }

            screenStreamRef.current = stream;
            setIsScreenSharing(true);
            track.onended = () => {
                setIsScreenSharing(false);
                setIsPaused(true); // Pause timer and interview progression
                showAiEvent('SCREEN SHARING STOPPED', true, 'tab_switch');
            };
            return true;
        } catch (err) {
            console.error("Screen share error:", err);
            alert('Screen sharing (Entire Screen) is required to start the interview.');
            return false;
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        if (screenStreamRef.current) {
            screenStreamRef.current.getTracks().forEach(track => track.stop());
            screenStreamRef.current = null;
            setIsScreenSharing(false);
        }
    };

    const reportViolation = useCallback(async (eventType, screenshot = null, webcamScreenshot = null) => {
        const now = Date.now();
        const lastReported = violationCooldownsRef.current[eventType] || 0;
        
        // Check if this violation type is still in cooldown
        if (now - lastReported < VIOLATION_COOLDOWN_MS) {
            // Same violation type reported recently - skip this duplicate
            return;
        }
        
        // Update cooldown tracker
        violationCooldownsRef.current[eventType] = now;
        
        try {
            await axios.post(`${API_BASE_URL}/ai-candidates/public/${token}/integrity/`, {
                event_type: eventType,
                screenshot: screenshot,
                webcam_screenshot: webcamScreenshot
            });
        } catch (err) {
            console.error("Failed to report violation:", err);
        }
    }, [token]);

    const playAuditNotice = useCallback((text) => {
        if (!window.speechSynthesis) return;
        isNoticePlayingRef.current = true;

        // Cancel any existing notices to avoid overlapping alerts
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onend = () => { isNoticePlayingRef.current = false; };
        utterance.onerror = () => { isNoticePlayingRef.current = false; };

        // Optional: Custom voice/pitch for "System" feel
        utterance.rate = 1.0;
        utterance.pitch = 0.9;

        window.speechSynthesis.speak(utterance);
    }, []);

    const showAiEvent = useCallback(async (text, urgent = false, eventType = null) => {
        setAiToast({ active: true, text, urgent });
        if (urgent) {
            setIntegrityBreach({ active: true, text });
            // playAuditNotice(text); // AUDIBLE ALERT (Disabled - text alerts only)
            setTimeout(() => setIntegrityBreach({ active: false, text: '' }), 3000);
        }

        if (eventType) {
            // Throttling: 5-second cooldown per event type to prevent flooding the DB/UI
            const now = Date.now();
            const lastTime = lastCaptureTimeRef.current[eventType] || 0;
            if (now - lastTime < 5000) return;
            lastCaptureTimeRef.current[eventType] = now;

            let screenshot = null;
            let webcamScreenshot = null;

            // Capture Screen (if screen or environmental event)
            if (['tab_switch', 'window_blur', 'screen_stop', 'face_mismatch', 'looking_away', 'multi_person', 'no_face'].includes(eventType) && screenStreamRef.current) {
                try {
                    const video = document.createElement('video');
                    video.srcObject = screenStreamRef.current;
                    await video.play().catch(() => {});
                    
                    // Simple wait
                    if (video.readyState < 2) {
                        await new Promise(r => setTimeout(r, 400));
                    }

                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth || 1280;
                    canvas.height = video.videoHeight || 720;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0);
                    screenshot = canvas.toDataURL('image/jpeg', 0.6);
                    video.pause();
                    video.srcObject = null;
                } catch (e) { console.warn("Screen capture failed:", e); }
            }

            // Always capture Webcam for context
            if (videoRef.current && videoRef.current.readyState >= 2) {
                try {
                    const canvas = document.createElement('canvas');
                    canvas.width = videoRef.current.videoWidth;
                    canvas.height = videoRef.current.videoHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(videoRef.current, 0, 0);
                    webcamScreenshot = canvas.toDataURL('image/jpeg', 0.7);
                } catch (e) { console.warn("Webcam capture failed:", e); }
            }

            if (screenshot || webcamScreenshot) {
                reportViolation(eventType, screenshot, webcamScreenshot);
            }
        }

        setTimeout(() => setAiToast({ active: false, text: '', urgent: false }), 3000);
    }, [reportViolation]);

    useEffect(() => {
        // AI Monitoring: DeepFace handles ALL proctoring (face detection, verification,
        // multi-face, head pose). COCO-SSD/TensorFlow.js removed to eliminate GPU
        // contention that was causing laggy face tracking and poor recognition accuracy.
        setAiStatus('AI Monitoring Active');

        const handleVisibilityChange = () => {
            if (document.hidden || document.visibilityState === 'hidden') {
                setIsPaused(true); // Pause timer and interview progression
                showAiEvent("TAB SWITCHED", true, 'tab_switch');
            }
        };

        const handleBlur = () => {
            setIsPaused(true); // Pause timer and interview progression
            showAiEvent("WINDOW BLURRED", true, 'tab_switch');
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('blur', handleBlur);

        const handleFullscreenChange = () => {
            const isFS = !!document.fullscreenElement;
            setIsFullscreen(isFS);
            isFullscreenRef.current = isFS;

            if (isFS && isPermissionsGranted && isScreenSharing) {
                console.log("Integrity: Safe state restored. Resuming hardware...");
                // 1. Resume timer and interview progression
                setIsPaused(false);
                // 2. Unmute Hardware Tracks
                if (micStreamRef.current) {
                    micStreamRef.current.getAudioTracks().forEach(track => { track.enabled = true; });
                }
                if (streamRef.current) {
                    streamRef.current.getVideoTracks().forEach(track => { track.enabled = true; });
                }
                // 3. Ensure video element is playing
                if (videoRef.current) {
                    videoRef.current.play().catch(e => console.warn("Cam resume error:", e));
                }
                setAiStatus("Interview Resumed");
            }

            if (!isFS && isPermissionsGranted) {
                showAiEvent("FULLSCREEN EXITED", true, 'tab_switch');
                setIsPaused(true); // Pause timer and interview progression
                pauseHardware();
                setAiStatus("Interview Paused (Not in Full Screen)");
            }
        };

        const pauseHardware = () => {
            console.log("Integrity Violation: Pausing hardware...");
            // 1. Physically Mute Microphone Hardware
            if (micStreamRef.current) {
                micStreamRef.current.getAudioTracks().forEach(track => { track.enabled = false; });
            }
            // 2. Mute Camera Hardware
            if (streamRef.current) {
                streamRef.current.getVideoTracks().forEach(track => { track.enabled = false; });
            }

            // 3. Stop AssemblyAI STT
            if (assemblyAIRef.current) {
                try { assemblyAIRef.current.stop(); } catch (e) { }
            }

            // 3. Stop Speech (Browser TTS) - Respect proctoring notices
            if (window.speechSynthesis && !isNoticePlayingRef.current) {
                window.speechSynthesis.cancel();
            }
            setIsSpeaking(false);
            isSpeakingRef.current = false;

            // 4. Stop Speech (Coqui TTS)
            if (currentAudioRef.current) {
                try {
                    currentAudioRef.current.pause();
                    currentAudioRef.current.volume = 0; // Absolute silence
                    currentAudioRef.current = null;
                } catch (e) { }
            }
        };

        // NEW: Monitor Screen Sharing status for pausing
        if (!isScreenSharing && isPermissionsGranted && isInitializedRef.current && !isCompletedRef.current) {
            setIsPaused(true); // Pause timer and interview progression
            pauseHardware();
            setAiStatus("Interview Paused (Screen Share Stopped)");
        }

        document.addEventListener('fullscreenchange', handleFullscreenChange);

        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('fullscreenchange', handleFullscreenChange);
        };
    }, [token, showAiEvent, isScreenSharing]);

    // 3. CONTINUOUS PRIVACY HAMMER: Mutes everything 10 times a second if not in FS
    useEffect(() => {
        if (!isFullscreen && isPermissionsGranted && !isCompleted) {
            const hammer = setInterval(() => {
                // If a proctoring notice is playing, DO NOT cancel it
                if (window.speechSynthesis && !isNoticePlayingRef.current) {
                    window.speechSynthesis.cancel();
                }
                if (currentAudioRef.current) {
                    try {
                        currentAudioRef.current.pause();
                        currentAudioRef.current.volume = 0;
                    } catch (e) { }
                }
            }, 100);
            return () => clearInterval(hammer);
        }
    }, [isFullscreen, isPermissionsGranted, isCompleted]);

    // ══════════════════════════════════════
    // DEEPFACE PROCTORING
    // ══════════════════════════════════════
    const sendDeepfaceFrame = useCallback(() => {
        if (!dfWsRef.current || dfWsRef.current.readyState !== WebSocket.OPEN) {
            if (!dfWsRef.current) {
                // Silently skip if not connected yet (avoid log spam)
            } else if (dfWsRef.current.readyState !== WebSocket.OPEN) {
                // Log once per state change
                if (dfWsRef.current.readyState === WebSocket.CONNECTING) {
                    console.log('🟡 [DeepFace] WebSocket still connecting...');
                } else if (dfWsRef.current.readyState === WebSocket.CLOSED) {
                    console.error('🔴 [DeepFace] WebSocket is closed - monitoring stopped');
                }
            }
            return;
        }
        
        if (!videoRef.current || !videoRef.current.videoWidth) {
            console.warn('🟡 [DeepFace] Video not ready - dimensions:', videoRef.current?.videoWidth);
            return;
        }
        
        if (dfAwaitingRef.current) {
            return; // Skip frame if waiting for previous response
        }

        try {
            const canvas = document.createElement('canvas');
            canvas.width = 640;
            canvas.height = 480;
            const ctx = canvas.getContext('2d');
            // Apply brightness and contrast enhancement before sending to backend
            ctx.filter = 'brightness(1.15) contrast(1.2)';
            ctx.drawImage(videoRef.current, 0, 0, 640, 480);
            ctx.filter = 'none';

            // OPTIMIZATION: Reduced JPEG quality from 75% to 65% for faster encoding/decoding
            // Maintains sufficient quality for face recognition while reducing bandwidth overhead
            // Saves ~20-30ms per frame on base64 encoding/decoding operations
            const dataUrl = canvas.toDataURL('image/jpeg', 0.65);
            const b64 = dataUrl.split(',')[1];
            dfAwaitingRef.current = true;
            dfWsRef.current.send(JSON.stringify({ frame: b64 }));
        } catch (e) {
            console.error('🔴 [DeepFace] Frame send error:', e.message);
            dfAwaitingRef.current = false;
        }
    }, []);

    const drawDeepfaceOverlay = useCallback((result) => {
        const canvas = dfCanvasRef.current;
        if (!canvas || !videoRef.current) return;

        const vw = videoRef.current.clientWidth || 640;
        const vh = videoRef.current.clientHeight || 480;
        if (canvas.width !== vw || canvas.height !== vh) {
            canvas.width = vw;
            canvas.height = vh;
        }

        const ctx = canvas.getContext('2d');
        const sourceW = result.frame_width || 640;
        const sourceH = result.frame_height || 480;
        const scaleX = vw / sourceW;
        const scaleY = vh / sourceH;

        ctx.clearRect(0, 0, vw, vh);

        // Mirror the canvas drawing to match the scaleX(-1) on the video
        ctx.save();
        ctx.translate(vw, 0);
        ctx.scale(-1, 1);

        // Face bounding boxes
        if (Array.isArray(result.face_boxes)) {
            const isVerified = result.verification?.verified === true;
            const verSkipped = result.verification?.verified === 'skipped';

            result.face_boxes.forEach((box, idx) => {
                if (!box) return;
                let rawX = box.x ?? box.xmin;
                let rawY = box.y ?? box.ymin;
                let rawW = box.width;
                let rawH = box.height;
                if (rawX == null || rawY == null || rawW == null || rawH == null) return;

                rawX = Number(rawX); rawY = Number(rawY);
                rawW = Number(rawW); rawH = Number(rawH);
                if (!Number.isFinite(rawX) || !Number.isFinite(rawY)) return;

                const looksNormalized = rawW <= 1.2 && rawH <= 1.2;
                const xPx = looksNormalized ? (rawX * sourceW) : rawX;
                const yPx = looksNormalized ? (rawY * sourceH) : rawY;
                const wPx = looksNormalized ? (rawW * sourceW) : rawW;
                const hPx = looksNormalized ? (rawH * sourceH) : rawH;

                const x = Math.max(0, xPx * scaleX);
                const y = Math.max(0, yPx * scaleY);
                const w = Math.max(0, wPx * scaleX);
                const h = Math.max(0, hPx * scaleY);
                if (w < 6 || h < 6) return;

                let boxColor, label;
                if (result.face_count > 1) {
                    boxColor = '#f59e0b'; label = `FACE ${idx + 1}`;
                } else if (verSkipped) {
                    boxColor = '#f59e0b'; label = '';
                } else if (isVerified) {
                    boxColor = '#22c55e'; label = '✓ VERIFIED';
                } else {
                    boxColor = '#ef4444'; label = '✗ NOT MATCHED';
                }

                // Draw corner brackets
                ctx.strokeStyle = boxColor;
                ctx.lineWidth = 2.5;
                ctx.shadowColor = boxColor;
                ctx.shadowBlur = 6;
                const cornerLen = Math.min(w, h) * 0.25;
                ctx.beginPath(); ctx.moveTo(x, y + cornerLen); ctx.lineTo(x, y); ctx.lineTo(x + cornerLen, y); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(x + w - cornerLen, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + cornerLen); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(x, y + h - cornerLen); ctx.lineTo(x, y + h); ctx.lineTo(x + cornerLen, y + h); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(x + w - cornerLen, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - cornerLen); ctx.stroke();
                ctx.shadowBlur = 0;

                // Label above face — un-mirror so text reads correctly
                if (label) {
                    ctx.save();
                    // Flip back to normal for text rendering
                    const centerX = x + w / 2;
                    ctx.translate(centerX, 0);
                    ctx.scale(-1, 1);
                    ctx.translate(-centerX, 0);

                    ctx.font = '700 11px Inter, sans-serif';
                    ctx.textBaseline = 'top';
                    const tw = ctx.measureText(label).width + 12;
                    const th = 18;
                    const tx = x + (w - tw) / 2;
                    const ty = y > th + 6 ? y - th - 4 : y + h + 4;
                    ctx.fillStyle = boxColor;
                    ctx.beginPath();
                    if (ctx.roundRect) ctx.roundRect(tx, ty, tw, th, 3);
                    else ctx.fillRect(tx, ty, tw, th);
                    ctx.fill();
                    ctx.fillStyle = '#fff';
                    ctx.fillText(label, tx + 6, ty + 3);
                    ctx.restore();
                }
            });
        }

        // Restore from the mirror transform before drawing centered text
        ctx.restore();

        // No face / multi-face warning overlay (drawn in normal orientation)
        if (!result.face_present || result.face_count === 0) {
            ctx.fillStyle = 'rgba(239, 68, 68, 0.15)';
            ctx.fillRect(0, 0, vw, vh);
            ctx.font = '700 14px Inter, sans-serif';
            ctx.fillStyle = '#ef4444';
            ctx.textAlign = 'center';
            ctx.fillText('⚠ NO FACE DETECTED', vw / 2, vh - 16);
            ctx.textAlign = 'start';
        } else if (result.face_count > 1) {
            ctx.fillStyle = 'rgba(245, 158, 11, 0.15)';
            ctx.fillRect(0, 0, vw, vh);
            ctx.font = '700 14px Inter, sans-serif';
            ctx.fillStyle = '#f59e0b';
            ctx.textAlign = 'center';
            ctx.fillText(`⚠ ${result.face_count} FACES DETECTED`, vw / 2, vh - 16);
            ctx.textAlign = 'start';
        }
    }, []);

    const handleDeepfaceResult = useCallback((result) => {
        // PERFORMANCE: Draw overlay every frame for real-time feel (cheap canvas op)
        drawDeepfaceOverlay(result);

        // PERFORMANCE: Throttle React state updates to every 500ms
        // This prevents 25+ re-renders/sec which was causing jank and input lag
        const now = Date.now();
        if (now - dfLastUiUpdateRef.current > 500) {
            dfLastUiUpdateRef.current = now;
            setDfFacePresent(result.face_present ?? false);
            setDfFaceCount(result.face_count ?? 0);
            setDfEngagement(result.engagement_score ?? 0);
            if (result.verification) {
                setDfVerified(result.verification.verified);
            }
            if (result.head_pose) {
                const yaw = result.head_pose.yaw || 0;
                const pitch = result.head_pose.pitch || 0;
                let dir = 'FORWARD';
                if (Math.abs(yaw) > 15 || Math.abs(pitch) > 12) {
                    const parts = [];
                    if (pitch < -12) parts.push('UP');
                    else if (pitch > 12) parts.push('DOWN');
                    if (yaw < -15) parts.push('RIGHT');
                    else if (yaw > 15) parts.push('LEFT');
                    dir = parts.length > 0 ? parts.join('-') : 'FORWARD';
                }
                setDfHeadDir(dir);
            }
        }

        // Alerts are always processed immediately (they are rare events, not per-frame)
        if (result.alerts && result.alerts.length > 0) {
            result.alerts.forEach(a => {
                let eventType = a.type;
                let message = a.message.toUpperCase();
                
                if (a.type === 'verification_failed') eventType = 'face_mismatch';
                if (a.type === 'no_face') eventType = 'no_face_detection';
                if (a.type === 'multiple_faces') eventType = 'multiface_detection';
                if (a.type === 'head_yaw_exceeded' || a.type === 'head_pitch_exceeded') {
                    eventType = 'looking_away';
                    message = 'LOOKING AWAY DETECTED';
                }

                showAiEvent(message, a.severity === 'HIGH', eventType);
            });
        }
    }, [showAiEvent, drawDeepfaceOverlay]);

    const startDeepfaceMonitoring = useCallback(async (candidateId) => {
        try {
            const personId = String(candidateId || getDeepfacePersonId()).trim().toLowerCase();
            console.log('🔍 [DeepFace] Starting proctoring session for candidate:', personId);
            console.log('🔍 [DeepFace] DEEPFACE_BASE_URL:', DEEPFACE_BASE_URL);
            
            const res = await axios.post(`${DEEPFACE_BASE_URL}/session/start`, {
                person_id: personId
            });
            
            if (!res.data || !res.data.session_id) {
                console.error('🔴 [DeepFace] Invalid session response:', res.data);
                showAiEvent('DeepFace: Invalid session response', true, 'deepface_error');
                return;
            }
            
            const sessionId = res.data.session_id;
            console.log('✅ [DeepFace] Session created successfully:', sessionId);
            setDfSessionId(sessionId);
            dfSessionIdRef.current = sessionId;

            const wsUrl = `${DEEPFACE_WS_URL}/ws/monitor/${sessionId}`;
            console.log('🔍 [DeepFace] Connecting to WebSocket:', wsUrl);
            
            const ws = new WebSocket(wsUrl);
            dfWsRef.current = ws;

            ws.onopen = () => {
                console.log('✅ [DeepFace] WebSocket connected for session:', sessionId);
                console.log('✅ [DeepFace] Live monitoring is ACTIVE - frames being sent at 5 FPS');
                console.log('ℹ️ [DeepFace] Optimized for real-time face tracking responsiveness');
                dfAwaitingRef.current = false;
                // OPTIMIZATION: Reduced from 100ms (10 FPS) to 200ms (5 FPS)
                // Still provides real-time face tracking while reducing CPU load
                // Prevents laggy experience on lower-end devices
                dfSendIntervalRef.current = setInterval(() => {
                    sendDeepfaceFrame();
                }, 200); // 5 FPS for optimal performance/responsiveness balance
                showAiEvent('DeepFace Monitoring Started', false);
            };

            ws.onmessage = (event) => {
                try {
                    dfAwaitingRef.current = false;
                    const r = JSON.parse(event.data);
                    if (r.error) {
                        console.error('🔴 [DeepFace] Error in response:', r.error);
                        return;
                    }
                    handleDeepfaceResult(r);
                } catch (e) {
                    console.error('🔴 [DeepFace] Message parse error:', e.message);
                }
            };

            ws.onclose = () => {
                console.log('🟡 [DeepFace] WebSocket closed');
                if (dfSendIntervalRef.current) clearInterval(dfSendIntervalRef.current);
            };

            ws.onerror = (e) => {
                console.error('🔴 [DeepFace] WebSocket error:', e);
                console.error('🔴 [DeepFace] Connection failed - check if DeepFace service is running on port 8500');
                dfAwaitingRef.current = false;
                showAiEvent('DeepFace Connection Failed - Proctoring Unavailable', true, 'deepface_error');
            };

            console.log('✅ [DeepFace] Monitoring initialization complete');
        } catch (e) {
            console.error('🔴 [DeepFace] Critical error:', e.message);
            console.error('🔴 [DeepFace] Stack:', e.stack);
            if (e.code === 'ECONNREFUSED') {
                console.error('🔴 [DeepFace] Connection refused - DeepFace service NOT running on port 8500');
                console.error('🔴 [DeepFace] To start DeepFace: cd deepface && python run.py');
            }
            showAiEvent('DeepFace Service Unavailable', true, 'deepface_error');
        }
    }, [sendDeepfaceFrame, handleDeepfaceResult, showAiEvent, getDeepfacePersonId]);

    // Cleanup DeepFace on unmount
    useEffect(() => {
        return () => {
            if (dfSendIntervalRef.current) clearInterval(dfSendIntervalRef.current);
            if (dfWsRef.current) { dfWsRef.current.close(); dfWsRef.current = null; }
        };
    }, []);

    // 4. Speech and Interactions
    const unlockSpeech = useCallback(() => {
        if (!synthRef.current) return;
        // Playing a silent 0.01s utterance unlocks the browser's speech synthesis
        const silentU = new SpeechSynthesisUtterance(" ");
        silentU.volume = 0;
        synthRef.current.speak(silentU);
    }, []);

    const speak = useCallback((content) => {
        const text = typeof content === 'object' ? (content.question || JSON.stringify(content)) : content;

        // 0. STOP PREVIOUS AUDIO IMMEDIATELY to prevent overlaps
        if (currentAudioRef.current) {
            try {
                currentAudioRef.current.pause();
                currentAudioRef.current.currentTime = 0;
            } catch (e) {
                console.error("Error stopping current audio:", e);
            }
            currentAudioRef.current = null;
        }
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }

        if (!isFullscreenRef.current && isPermissionsGranted) {
            console.log("Speak blocked: Not in full screen.");
            return Promise.resolve();
        }

        // Immediate State Lock: Stop silence watchdog before promise starts
        setIsSpeaking(true);
        isSpeakingRef.current = true;
        setAiStatus("Speaking...");

        return new Promise(async (resolve) => {
            if (!text) {
                setIsSpeaking(false);
                isSpeakingRef.current = false;
                return resolve();
            }

            // Physically mute the mic hardware while Indu speaks
            if (micStreamRef.current) {
                micStreamRef.current.getAudioTracks().forEach(track => { track.enabled = false; });
            }

            // Safety Watchdog: resolve anyway after a generous timeout
            const timeoutMs = Math.max(15000, (text.length * 200) + 5000);
            const watchdog = setTimeout(() => {
                console.warn("📢 Speak Watchdog triggered (TTS timeout)");
                setIsSpeaking(false);
                isSpeakingRef.current = false;
                if (micStreamRef.current) {
                    micStreamRef.current.getAudioTracks().forEach(track => { track.enabled = true; });
                }
                resolve();
            }, timeoutMs);

            try {
                // --- COQUI TTS: POST text to backend and play the returned WAV ---
                const res = await axios.post(`${API_BASE_URL}/ai-candidates/tts/`, { text }, {
                    responseType: 'blob',
                    timeout: 30000 // 30s timeout for synthesis
                });

                const audioBlob = new Blob([res.data], { type: 'audio/mpeg' });
                const audioUrl = URL.createObjectURL(audioBlob);

                // SECONDARY GUARD: Ensure we didn't exit fullscreen while synthesis was occurring
                if (!isFullscreenRef.current && isPermissionsGranted) {
                    console.log("Speak aborted: Fullscreen exited during synthesis.");
                    URL.revokeObjectURL(audioUrl);
                    setIsSpeaking(false);
                    isSpeakingRef.current = false;
                    return resolve();
                }

                const audio = new Audio(audioUrl);
                currentAudioRef.current = audio;

                audio.onended = () => {
                    currentAudioRef.current = null;
                    clearTimeout(watchdog);
                    URL.revokeObjectURL(audioUrl);
                    // Delay unlock to allow speaker echo to fade
                    setTimeout(() => {
                        setIsSpeaking(false);
                        isSpeakingRef.current = false;
                        if (micStreamRef.current) {
                            micStreamRef.current.getAudioTracks().forEach(track => { track.enabled = true; });
                        }
                        if (isProcessingRef.current) {
                            setAiStatus("Processing answer...");
                        } else {
                            setAiStatus("Indu is Online");
                        }
                        resolve();
                    }, 500);
                };

                audio.onerror = (event) => {
                    console.error("Audio playback error (Edge TTS):", event);
                    clearTimeout(watchdog);
                    URL.revokeObjectURL(audioUrl);
                    // Fallback to browser speech
                    fallbackBrowserSpeak(text, watchdog, resolve);
                };

                audio.play().catch((err) => {
                    if (err.name === 'AbortError') {
                        console.log("Audio play interrupted by pause (intentional for fullscreen exit).");
                        return;
                    }
                    console.error("Audio play failed (Edge TTS - likely Autoplay blocked):", err);
                    // Autoplay blocked — fallback to browser TTS
                    currentAudioRef.current = null;
                    URL.revokeObjectURL(audioUrl);
                    fallbackBrowserSpeak(text, watchdog, resolve);
                });

            } catch (err) {
                console.error("Backend TTS Endpoint Error:", err.response?.data || err.message);
                fallbackBrowserSpeak(text, watchdog, resolve);
            }
        });
    }, []);

    // Fallback: Browser SpeechSynthesis (used if Coqui TTS endpoint is unavailable)
    const fallbackBrowserSpeak = useCallback((text, watchdog, resolve) => {
        synthRef.current.cancel();
        if (synthRef.current.paused) synthRef.current.resume();

        const utterance = new SpeechSynthesisUtterance(text);
        const voice =
            voicesRef.current.find(v => (v.name.includes('Siri') || v.name.includes('Samantha')) && v.name.toLowerCase().includes('female')) ||
            voicesRef.current.find(v => v.name.includes('Google US English') && v.name.toLowerCase().includes('female')) ||
            voicesRef.current.find(v => (v.name.includes('Jenny') || v.name.includes('Aria')) && v.name.toLowerCase().includes('female')) ||
            voicesRef.current.find(v => v.name.toLowerCase().includes('female')) ||
            voicesRef.current.find(v => v.name.includes('Siri') || v.name.includes('Samantha')) ||
            voicesRef.current.find(v => v.lang.startsWith('en')) ||
            voicesRef.current[0];

        if (voice) utterance.voice = voice;

        // SECONDARY GUARD: Prevent browser TTS if fullscreen was exited during setup
        if (!isFullscreenRef.current && isPermissionsGranted) {
            console.log("Browser Speak aborted: Not in full screen.");
            if (watchdog) clearTimeout(watchdog);
            setIsSpeaking(false);
            isSpeakingRef.current = false;
            return resolve();
        }

        utterance.onend = () => {
            if (watchdog) clearTimeout(watchdog);
            setTimeout(() => {
                setIsSpeaking(false);
                isSpeakingRef.current = false;
                if (micStreamRef.current) {
                    micStreamRef.current.getAudioTracks().forEach(track => { track.enabled = true; });
                }
                if (isProcessingRef.current) {
                    setAiStatus("Processing answer...");
                } else {
                    setAiStatus("Indu is Online");
                }
                resolve();
            }, 500);
        };

        utterance.onerror = (event) => {
            console.error("SpeechSynthesis error:", event);
            if (watchdog) clearTimeout(watchdog);
            setIsSpeaking(false);
            isSpeakingRef.current = false;
            setAiStatus("Indu is Online");
            if (micStreamRef.current) {
                micStreamRef.current.getAudioTracks().forEach(track => { track.enabled = true; });
            }
            resolve();
        };

        synthRef.current.speak(utterance);
    }, []);

    // Helper: Record ANY candidate activity to prevent false silence detection
    const recordActivity = useCallback(() => {
        lastActivityTimeRef.current = Date.now();
        if (consecutiveSilenceRef.current > 0) {
            consecutiveSilenceRef.current = 0;
            console.log("🎤 [Activity] Candidate activity detected, resetting silence counter");
        }
    }, []);

    // Helper: Wait for speech synthesis to fully complete before starting mic
    const waitForSpeechToFinish = useCallback(() => {
        return new Promise((resolve) => {
            // Check if browser TTS is still speaking
            const checkSpeaking = () => {
                if (!window.speechSynthesis.speaking && !currentAudioRef.current) {
                    resolve();
                } else {
                    setTimeout(checkSpeaking, 100);
                }
            };
            // Wait a bit first, then check
            setTimeout(checkSpeaking, 200);
        });
    }, []);

    // Helper: Validate answer before submission
    const validateAnswer = useCallback((text) => {
        if (text === "[Candidate remained silent/skipped]") {
            return { valid: true, isSilence: true };
        }
        if (!text || text.trim().length < 10) {
            return { valid: false, reason: "Answer too short (minimum 10 characters)" };
        }
        const words = text.trim().split(/\s+/).filter(w => w.length > 2);
        if (words.length < 3) {
            return { valid: false, reason: "Answer too brief (minimum 3 meaningful words)" };
        }
        // Check for repeated patterns (gibberish detection)
        const repeatedPattern = /(\b\w{1,3}\b)\s+\1\s+\1/;
        if (repeatedPattern.test(text)) {
            return { valid: false, reason: "Answer appears to be repetitive/gibberish" };
        }
        return { valid: true };
    }, []);

    // Helper: Submit answer with retry logic
    const submitAnswerWithRetry = useCallback(async (payload, retries = 3) => {
        for (let i = 0; i < retries; i++) {
            try {
                const response = await axios.post(`${API_BASE_URL}/ai-candidates/process-answer/`, payload, {
                    timeout: 60000
                });
                return { success: true, data: response.data };
            } catch (err) {
                console.warn(`API call attempt ${i + 1} failed:`, err.message);
                if (i === retries - 1) {
                    throw err; // All retries exhausted
                }
                // Exponential backoff: wait 1s, 2s, 4s
                await new Promise(r => setTimeout(r, 1000 * Math.pow(2, i)));
            }
        }
    }, [token]);

    // Helper: Check microphone quality before starting
    const checkMicrophoneQuality = useCallback(async (stream) => {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const analyser = audioContext.createAnalyser();
            const microphone = audioContext.createMediaStreamSource(stream);
            microphone.connect(analyser);
            analyser.fftSize = 256;

            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            let levels = [];

            const checkInterval = setInterval(() => {
                analyser.getByteFrequencyData(dataArray);
                const avg = dataArray.reduce((a, b) => a + b) / dataArray.length;
                levels.push(avg);
            }, 100);

            return new Promise((resolve) => {
                setTimeout(() => {
                    clearInterval(checkInterval);
                    const avgLevel = levels.reduce((a, b) => a + b) / levels.length;
                    console.log(`[Mic Quality] Average audio level: ${avgLevel.toFixed(2)}`);
                    resolve(avgLevel > 5); // At least some audio activity
                }, 2000);
            });
        } catch (e) {
            console.warn("[Mic Quality] Check failed:", e);
            return true; // Allow anyway if check fails
        }
    }, []);

    const addMessage = useCallback((sender, text) => {
        const displayText = typeof text === 'object' ? (text.question || JSON.stringify(text)) : text;
        const timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        setChatMessages(prev => {
            // Optional: De-duplicate consecutive identical AI messages
            if (prev.length > 0 && prev[prev.length - 1].sender === sender && prev[prev.length - 1].text === displayText) {
                return prev;
            }
            return [...prev, { sender, text: displayText, timestamp }];
        });
        chatHistoryRef.current.push({ role: sender === 'ai' ? 'assistant' : 'user', content: displayText });
    }, []);

    const completeInterview = useCallback(async (customMessage = null) => {
        if (isCompletedRef.current) return;
        isCompletedRef.current = true;
        setIsCompleted(true);
        logCandidateActivity(token, 'AI Interview Submitted', 'AI Interview completed and submitted.');
        stopCamera();
        // Stop DeepFace proctoring session
        if (dfSendIntervalRef.current) clearInterval(dfSendIntervalRef.current);
        if (dfWsRef.current) { dfWsRef.current.close(); dfWsRef.current = null; }
        if (dfSessionIdRef.current) {
            axios.post(`${DEEPFACE_BASE_URL}/session/${dfSessionIdRef.current}/end`).catch(() => {});
        }
        // Stop any ongoing AI speech to prevent overlap
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (currentAudioRef.current) {
            try {
                currentAudioRef.current.pause();
                currentAudioRef.current.currentTime = 0;
            } catch (e) {}
            currentAudioRef.current = null;
        }
        if (globalSilenceTimerRef.current) clearInterval(globalSilenceTimerRef.current);

        const finishMessage = customMessage || "The interview is now complete. Thank you for your time and we will get back to you soon. Goodbye!";
        addMessage('ai', finishMessage);
        await speak(finishMessage);
        axios.patch(`${API_BASE_URL}/ai-candidates/public/${token}/status/`, { status: 'Completed' }).catch(console.error);

        // Mark as completed locally to prevent re-opening link
        localStorage.setItem(`interview_completed_${token}`, 'true');
        
        // Clear saved progress to prevent stale data on re-interview
        localStorage.removeItem(`interview_progress_${token}`);
        console.log("✅ [Cleanup] Interview progress cleared from localStorage");

        setIsProcessing(true);
        setAiStatus("Session Finished");
    }, [token, speak, addMessage]);

    const startListening = useCallback(async () => {
        if (userInputMode !== 'audio' || isRecordingRef.current || isStartingMicRef.current) return;
        if (!isFullscreenRef.current) {
            console.log("Mic blocked: Not in full screen.");
            return;
        }
        isStartingMicRef.current = true;

        let attempts = 0;
        const maxAttempts = 10;

        const tryStart = async () => {
            if (!isFullscreenRef.current) return;

            if (isProcessingRef.current || isSpeakingRef.current) {
                if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(tryStart, 350);
                }
                return;
            }

            try {
                // Initialize AssemblyAI
                setIsRecording(true);
                isRecordingRef.current = true;
                setAiStatus("Connecting to AssemblyAI...");

                const token = process.env.REACT_APP_ASSEMBLYAI_API_KEY;

                if (!token) {
                    console.error("Missing REACT_APP_ASSEMBLYAI_API_KEY");
                    setAiStatus("Config Error - Missing Key");
                    return;
                }

                const wsUrl = `wss://streaming.assemblyai.com/v3/ws?sample_rate=16000&speech_model=u3-rt-pro&token=${token}`;
                const ws = new WebSocket(wsUrl);

                // Buffer to hold audio chunks while WebSocket is connecting
                const audioBufferQueue = [];

                ws.onopen = () => {
                    console.log("AssemblyAI Auto-mic active via Native WebSocket!");
                    setSttReady(true);
                    setAiStatus("Listening...");

                    // Flush queued audio buffers
                    while (audioBufferQueue.length > 0) {
                        ws.send(audioBufferQueue.shift());
                    }

                    transcriptRef.current = "";
                    interimTranscriptRef.current = "";
                    lastTranscriptStrRef.current = "";
                    lastSpokenTimeRef.current = Date.now();
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);

                    if (data.type === "SessionBegins") {
                        console.log("AssemblyAI Session Started:", data.session_id);
                        return;
                    }

                    // CRITICAL: Ignore all transcripts while Indu is speaking or processing to avoid feedback loops and buffer pollution
                    if (isSpeakingRef.current || isProcessingRef.current) return;

                    if (data.type !== "Turn") return;

                    const text = data.transcript;
                    if (!text) return;

                    // Compute the exact total text currently understood
                    const currentFullText = (transcriptRef.current + " " + text).trim();
                    // ONLY reset our strict timer if we actually hear NEW words!
                    if (currentFullText !== lastTranscriptStrRef.current) {
                        lastTranscriptStrRef.current = currentFullText;
                        lastSpokenTimeRef.current = Date.now(); // Activity Reset!
                    }

                    if (!data.turn_is_formatted) {
                        interimTranscriptRef.current = text;
                    } else {
                        transcriptRef.current += text + " ";
                        interimTranscriptRef.current = "";
                        // Notice: We don't trigger submit timers here anymore. 
                        // The strict interval above perfectly handles it the moment the text stops accumulating!
                    }

                    const currentTotal = (transcriptRef.current + interimTranscriptRef.current).trim();
                    if (currentTotal) {
                        const display = currentTotal.length > 35 ? '...' + currentTotal.slice(-35) : currentTotal;
                        setAiStatus(`Heard: "${display}"`);
                    }
                };

                ws.onerror = (error) => {
                    console.error("AssemblyAI Native WebSocket error:", error);
                    setSttReady(false);
                    setIsRecording(false);
                    isRecordingRef.current = false;
                    setAiStatus("Mic Error - Retrying...");
                };

                ws.onclose = (event) => {
                    console.log("AssemblyAI Native WebSocket closed:", event.code, event.reason);
                    setSttReady(false);
                    setIsRecording(false);
                    isRecordingRef.current = false;
                    if (silenceTimerRef.current) clearInterval(silenceTimerRef.current);
                    if (globalSilenceTimerRef.current) clearTimeout(globalSilenceTimerRef.current);

                    // Reconnect if closed unexpectedly (not by us calling stop())
                    if (event.code !== 1000 && !isProcessingRef.current && !isCompletedRef.current) {
                        console.log("Triggering auto-reconnect for AssemblyAI...");
                        setTimeout(() => startListening(), 2000);
                    }
                };

                // Remove sdk from connect queue
                // await rt.connect();

                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                micStreamRef.current = stream; // Store ref for physical mute/unmute

                // --- Audio Visualizer & Local VAD ---
                try {
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    visualizerCtxRef.current = audioCtx;
                    const analyser = audioCtx.createAnalyser();
                    const source = audioCtx.createMediaStreamSource(stream);
                    source.connect(analyser);
                    analyser.fftSize = 64;
                    const bufferLength = analyser.frequencyBinCount;
                    const dataArray = new Uint8Array(bufferLength);

                    const drawVisualizer = () => {
                        if (!canvasRef.current) return;
                        const canvas = canvasRef.current;
                        const ctx = canvas.getContext("2d");

                        // While Indu is speaking, show flat resting dots instead of live audio
                        if (isSpeakingRef.current) {
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                            const visualBins = 16;
                            const spacing = 3;
                            const bw = (canvas.width / (visualBins * 2)) - spacing;
                            const cx2 = canvas.width / 2;
                            const ry = (canvas.height / 2) - 2;
                            ctx.fillStyle = '#cbd5e1';
                            for (let i = 0; i < visualBins; i++) {
                                ctx.beginPath();
                                if (ctx.roundRect) ctx.roundRect(cx2 + (i * (bw + spacing)), ry, bw, 4, bw / 2);
                                else ctx.fillRect(cx2 + (i * (bw + spacing)), ry, bw, 4);
                                ctx.fill();
                                if (i !== 0) {
                                    ctx.beginPath();
                                    if (ctx.roundRect) ctx.roundRect(cx2 - (i * (bw + spacing)), ry, bw, 4, bw / 2);
                                    else ctx.fillRect(cx2 - (i * (bw + spacing)), ry, bw, 4);
                                    ctx.fill();
                                }
                            }
                            animationRef.current = requestAnimationFrame(drawVisualizer);
                            return;
                        }

                        analyser.getByteFrequencyData(dataArray);
                        ctx.clearRect(0, 0, canvas.width, canvas.height);

                        // Premium gradient across the whole canvas
                        const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
                        gradient.addColorStop(0, '#0ea5e9'); // Light blue
                        gradient.addColorStop(0.5, '#6366f1'); // Indigo
                        gradient.addColorStop(1, '#ec4899'); // Pink

                        const visualBins = 16; // Number of bars on *each half* of the axis
                        const spacing = 3;
                        const barWidth = (canvas.width / (visualBins * 2)) - spacing;
                        const centerX = canvas.width / 2;
                        let isSpeakingLocal = false;
                        let vocalVolume = 0;
                        for (let i = 2; i < 12; i++) {
                            vocalVolume += dataArray[i];
                        }
                        const averageVocal = vocalVolume / 10;
                        if (averageVocal > 160) isSpeakingLocal = true; // Increased threshold to 110 to ignore background noise/fans

                        for (let i = 0; i < visualBins; i++) {
                            const val = dataArray[i];

                            // Taper the outer bars slightly so it looks naturally curved like a voice
                            const positionScale = 1 - (i / visualBins) * 0.4;
                            let barHeight = (val / 255.0) * (canvas.height * 0.8) * positionScale;
                            if (barHeight < 4) barHeight = 4; // Glowing resting dot height

                            const y = (canvas.height / 2) - (barHeight / 2);

                            ctx.fillStyle = gradient;
                            ctx.shadowBlur = 8;
                            ctx.shadowColor = `rgba(99, 102, 241, ${barHeight / canvas.height})`; // Dynamic indigo glow

                            // Right side mirrored bar
                            ctx.beginPath();
                            if (ctx.roundRect) ctx.roundRect(centerX + (i * (barWidth + spacing)), y, barWidth, barHeight, barWidth / 2);
                            else ctx.fillRect(centerX + (i * (barWidth + spacing)), y, barWidth, barHeight);
                            ctx.fill();

                            // Left side mirrored bar
                            if (i !== 0) {
                                ctx.beginPath();
                                if (ctx.roundRect) ctx.roundRect(centerX - (i * (barWidth + spacing)), y, barWidth, barHeight, barWidth / 2);
                                else ctx.fillRect(centerX - (i * (barWidth + spacing)), y, barWidth, barHeight);
                                ctx.fill();
                            }
                        }

                        // Reset shadow
                        ctx.shadowBlur = 0;

                        // Local Mic Check: if we hear sound locally, update our master timestamp
                        if (isSpeakingLocal && isRecordingRef.current) {
                            if (Date.now() % 5000 < 100) console.log("VAD Active. Avg Volume:", averageVocal);
                            lastSpokenTimeRef.current = Date.now();
                        }

                        animationRef.current = requestAnimationFrame(drawVisualizer);
                    };
                    drawVisualizer();
                } catch (e) { console.error("Visualizer Error:", e); }

                const recorder = new RecordRTC(stream, {
                    type: 'audio',
                    mimeType: 'audio/webm;codecs=pcm',
                    recorderType: StereoAudioRecorder,
                    timeSlice: 250,
                    desiredSampRate: 16000,
                    numberOfAudioChannels: 1,
                    ondataavailable: async (blob) => {
                        try {
                            const buffer = await blob.arrayBuffer();
                            if (ws.readyState === WebSocket.OPEN) {
                                ws.send(buffer);
                            } else if (ws.readyState === WebSocket.CONNECTING) {
                                // Add to queue if ws is not fully ready yet to prevent audio loss
                                audioBufferQueue.push(buffer);
                            }
                        } catch (e) { } // In case connection closed
                    }
                });
                recorder.startRecording();
                isRecordingRef.current = true;
                setIsRecording(true);
                // CRITICAL: Reset the activity timer so the 5s watchdog starts fresh from NOW
                lastSpokenTimeRef.current = Date.now();

                assemblyAIRef.current = {
                    stop: () => {
                        try {
                            if (animationRef.current) cancelAnimationFrame(animationRef.current);
                            if (visualizerCtxRef.current) {
                                visualizerCtxRef.current.close().catch(e => { });
                                visualizerCtxRef.current = null;
                            }

                            // Flatline the canvas perfectly when mic turns off (resting dots)
                            if (canvasRef.current) {
                                const c = canvasRef.current;
                                const cx = c.getContext("2d");
                                cx.clearRect(0, 0, c.width, c.height);

                                const visualBins = 16;
                                const spacing = 3;
                                const barWidth = (c.width / (visualBins * 2)) - spacing;
                                const centerX = c.width / 2;
                                const y = (c.height / 2) - 2;
                                cx.fillStyle = '#cbd5e1'; // Dull offline gray

                                for (let i = 0; i < visualBins; i++) {
                                    cx.beginPath();
                                    if (cx.roundRect) cx.roundRect(centerX + (i * (barWidth + spacing)), y, barWidth, 4, barWidth / 2);
                                    else cx.fillRect(centerX + (i * (barWidth + spacing)), y, barWidth, 4);
                                    cx.fill();
                                    if (i !== 0) {
                                        cx.beginPath();
                                        if (cx.roundRect) cx.roundRect(centerX - (i * (barWidth + spacing)), y, barWidth, 4, barWidth / 2);
                                        else cx.fillRect(centerX - (i * (barWidth + spacing)), y, barWidth, 4);
                                        cx.fill();
                                    }
                                }
                            }

                            recorder.stopRecording(() => {
                                stream.getTracks().forEach(track => track.stop());
                                // Safely defer destruction to prevent corrupting the next question's AudioContext if started fast
                                setTimeout(() => {
                                    try { if (recorder && recorder.destroy) recorder.destroy(); } catch (e) { }
                                }, 1500);
                            });
                            ws.close(1000); // 1000 = Normal Closure, prevents auto-reconnect loops
                        } catch (e) { }
                    }
                };

                // Allow toggle functions to use this reference logic
                recognitionRef.current = assemblyAIRef.current;

            } catch (e) {
                console.error("AssemblyAI start error (startListening):", e);
                if (e instanceof TypeError) {
                    console.error("TypeError caught in startListening:", e.message, e.stack);
                }
                setIsRecording(false);
                isRecordingRef.current = false;
            }
        };

        tryStart().finally(() => {
            isStartingMicRef.current = false;
        });

        return () => {
            if (assemblyAIRef.current) {
                try { assemblyAIRef.current.stop(); } catch (e) { }
            }
        };
    }, [userInputMode]);

    const handleAnswerSubmission = useCallback(async (answer, retryCount = 0) => {
        if (!isFullscreenRef.current) {
            console.log("Submission blocked: Not in full screen.");
            return;
        }

        if (!answer || !answer.trim() || isProcessing) {
            console.log("Submission skipped: answer empty or already processing");
            return;
        }

        // NEW: Validate answer before processing
        const validation = validateAnswer(answer);
        if (!validation.valid) {
            console.log(`[Validation] Answer rejected: ${validation.reason}`);
            // Don't block silence answers, but warn for others
            if (!validation.isSilence) {
                setAiToast({ active: true, text: validation.reason + ". Please provide a more detailed answer.", urgent: true });
                setTimeout(() => setAiToast({ active: false, text: '', urgent: false }), 3000);
                // Allow submission anyway but log it
            }
        }

        // 1. Immediate UI Lock & Reset Nudge
        setIsProcessing(true);
        isProcessingRef.current = true;
        setAiStatus("AI is thinking...");
        nudgeCountRef.current = 0; // Reset nudge for the new question turn
        if (globalSilenceTimerRef.current) clearInterval(globalSilenceTimerRef.current);

        // 2. Force Microphone Stop
        if (recognitionRef.current) {
            try { recognitionRef.current.stop(); } catch (e) { }
        }
        if (silenceTimerRef.current) clearInterval(silenceTimerRef.current);
        setSilenceCountdown(0);

        // 3. Track Consecutive Silence (to end interview if candidate leaves)
        // NEW: Improved with grace period and activity tracking
        if (answer === "[Candidate remained silent/skipped]") {
            consecutiveSilenceRef.current += 1;
        } else {
            consecutiveSilenceRef.current = 0;
            recordActivity();
        }

        // NEW: Check grace period before ending interview
        if (consecutiveSilenceRef.current >= 3) {
            const timeSinceActivity = Date.now() - lastActivityTimeRef.current;
            const SILENCE_GRACE_PERIOD = 8000; // 8 seconds grace
            if (timeSinceActivity > SILENCE_GRACE_PERIOD) {
                console.log(`Consecutive silence limit reached (3). Time since activity: ${timeSinceActivity}ms. Ending interview.`);
                completeInterview("The interview has been ended due to lack of response. We will review the answers provided so far. Thank you.");
                return;
            } else {
                console.log(`Consecutive silence at 3, but grace period active (${timeSinceActivity}ms < ${SILENCE_GRACE_PERIOD}ms). Resetting counter.`);
                consecutiveSilenceRef.current = 0;
            }
        }

        addMessage('user', answer);
        setResponseInput('');

        // 3. Clear all speech buffers to prevent the "Repeated Input" bug
        transcriptRef.current = "";
        interimTranscriptRef.current = "";
        lastTranscriptStrRef.current = "";
        lastSpokenTimeRef.current = Date.now();
        recordActivity();

        console.log("Submitting answer turn...");

        try {
            const currentQ = questions[currentQuestionIndex] || "Introduction and Background";
            const payload = {
                candidate_token: token,
                question: typeof currentQ === 'object' ? currentQ.question : currentQ,
                answer: answer,
                turn_number: currentQuestionIndex + 1,
                remaining_questions: questions.slice(currentQuestionIndex + 1),
                chat_history: chatHistoryRef.current
            };
            // NEW: Use retry logic instead of single attempt
            const result = await submitAnswerWithRetry(payload, 3);
            const data = result.data;
            const isClarification = data.is_clarification === true;
            const isExit = data.is_exit === true;
            let fullFeedback = data.feedback || "";

            if (isExit) {
                // Scenario: Candidate wants to end the interview
                completeInterview(fullFeedback);
                return;
            }

            if (isClarification) {
                // Scenario A: Candidate asked for help/clarification
                // REPHRASE LOGIC: Combine acknowledgement and the actual rephrased question
                const rephrasedQ = data.refined_next_question || "";
                const combinedClarification = (fullFeedback.trim() === rephrasedQ.trim())
                    ? rephrasedQ
                    : (fullFeedback.trim() + " " + rephrasedQ).trim();

                addMessage('ai', combinedClarification);
                try {
                    await speak(combinedClarification);
                } catch (e) {
                    console.error("Clarification speak error:", e);
                }

                // NEW: Wait for speech to fully complete before starting mic
                await waitForSpeechToFinish();
                setIsProcessing(false);
                isProcessingRef.current = false;
                setAiStatus("Indu is Online");
                // Reset manual mute for new turn
                manualMuteRef.current = false;
                if (userInputMode === 'audio' && !showQuotaWarning) {
                    setTimeout(() => startListening(), 300);
                }
                return; // STOP HERE: Don't move to next question index
            }

            const nextIdx = currentQuestionIndex + 1;
            const totalAnswered = nextIdx; // questions answered so far

            // FIX: Better check - ensure we've answered enough questions AND haven't exceeded list
            // --- HARD STOP: end after maxQuestions ---
            if (totalAnswered >= maxQuestions || nextIdx >= questions.length || totalAnswered >= 13) {
                let finalWords = "That concludes our interview questions today. Thank you for your time, we will be in touch soon. Goodbye!";
                if (fullFeedback.trim()) {
                    finalWords = fullFeedback.trim() + ". " + finalWords;
                }
                completeInterview(finalWords);
                return;
            }
            // ------------------------------------------

            // --- GRACEFUL TIME EXPIRY: if time ran out while candidate was answering ---
            if (timeExpiredRef.current) {
                let finalWords = "Time has expired for this interview. Thank you for your time, we will review your responses and get back to you soon. Goodbye!";
                if (fullFeedback.trim()) {
                    finalWords = fullFeedback.trim() + ". " + finalWords;
                }
                completeInterview(finalWords);
                return;
            }
            // ------------------------------------------

            // Extract the question string from potential object or string
            const extractQ = (q) => {
                if (!q) return null;
                if (typeof q === 'object') return q.question || JSON.stringify(q);
                return q;
            };

            const followUpQ = extractQ(data.follow_up_question);
            const refinedNextQ = extractQ(data.refined_next_question);

            // --- MERGED CONVERSATIONAL FLOW ---
            // Combine feedback and next question into ONE bubble for a human feel
            let fullTurnText = "";
            if (fullFeedback.trim()) fullTurnText += fullFeedback.trim() + " ";

            if (followUpQ) {
                // De-duplicate if feedback and follow-up are identical
                const followUpText = (fullFeedback.trim() === followUpQ.trim())
                    ? followUpQ
                    : (fullFeedback.trim() + " " + followUpQ);

                addMessage('ai', followUpText);

                // Determine mode BEFORE speaking
                let effectiveMode = userInputMode;
                if (data.requires_code_input) {
                    effectiveMode = 'text';
                    setUserInputMode('text');
                    setAiStatus("Coding Mode (Keyboard)");
                    try { if (assemblyAIRef.current) assemblyAIRef.current.stop(); } catch (e) { }
                    setIsRecording(false);
                    isRecordingRef.current = false;
                } else {
                    effectiveMode = 'audio';
                    setUserInputMode('audio');
                    setAiStatus("Indu is Online");
                }

                await speak(followUpText);
                // NEW: Wait for speech to fully complete before starting mic
                await waitForSpeechToFinish();
                setIsProcessing(false);
                isProcessingRef.current = false;

                if (effectiveMode === 'audio' && !showQuotaWarning) {
                    // Reset manual mute for new turn
                    manualMuteRef.current = false;
                    // Additional small delay after speech fully completes
                    setTimeout(() => {
                        if (!isCompletedRef.current && !isProcessingRef.current) {
                            startListening();
                        }
                    }, 300);
                }
            } else if (refinedNextQ === null && nextIdx >= questions.length) {
                if (fullTurnText) addMessage('ai', fullTurnText);
                if (fullTurnText) await speak(fullTurnText);
                completeInterview();
            } else {
                const nextQ = refinedNextQ || questions[nextIdx] || "Could you tell me more about your experience?";
                setCurrentQuestionIndex(nextIdx);
                // Calculate progress against the actual total questions intended
                const totalQuestions = Math.max(1, Math.min(maxQuestions, questions.length || maxQuestions));
                setProgress((nextIdx / totalQuestions) * 100);

                setQuestions(prev => {
                    const newQs = [...prev];
                    if (nextIdx < newQs.length) newQs[nextIdx] = nextQ;
                    else newQs.push(nextQ);
                    return newQs;
                });

                // De-duplicate and filter out transition phrases if ending
                let finalTurnText = (fullFeedback.trim() === nextQ.trim())
                    ? nextQ
                    : (fullFeedback.trim() + " " + nextQ);

                // If this is the last question being answered (nextIdx >= MAX_QUESTIONS), 
                // we don't want "No worries, let's move
                if (nextIdx >= maxQuestions) {
                    finalTurnText = fullFeedback.trim();
                }

                // 1. DETERMINE MODE & STATUS (Instant UI Update)
                let effectiveMode = userInputMode;
                if (data.requires_code_input) {
                    effectiveMode = 'text';
                    setUserInputMode('text');
                    setAiStatus("Coding Mode (Keyboard)");
                    // Force Mic Stop
                    try { if (assemblyAIRef.current) assemblyAIRef.current.stop(); } catch (e) { }
                    setIsRecording(false);
                    isRecordingRef.current = false;
                } else {
                    effectiveMode = 'audio';
                    setUserInputMode('audio');
                    setAiStatus("Indu is Online");
                }

                // 2. LOG & SPEAK (Can be long-running)
                if (finalTurnText) {
                    addMessage('ai', finalTurnText);
                    await speak(finalTurnText);
                }

                // 3. FINAL STATE SYNC
                setIsProcessing(false);
                isProcessingRef.current = false;

                // Resume listening only if we are in audio mode AND not in a coding task
                // FIX: Add delay before mic starts to prevent feedback loop
                if (effectiveMode === 'audio' && !showQuotaWarning) {
                    // Reset manual mute for new turn
                    manualMuteRef.current = false;
                    setTimeout(() => {
                        if (!isCompletedRef.current && !isProcessingRef.current) {
                            startListening();
                        }
                    }, 600);
                }
            }
        } catch (err) {
            console.error("Submission error:", err.code === 'ECONNABORTED' ? "AI Timeout (60s)" : err.message);

            // ALWAYS reset processing state so the UI doesn't "stick"
            setIsProcessing(false);
            isProcessingRef.current = false;

            if (err.response?.status === 429 || err.response?.data?.retryable) {
                // Track retry count to prevent infinite loops
                const currentRetry = retryCount || 0;
                const maxRetries = 3;

                if (currentRetry < maxRetries) {
                    const backoffDelay = 8000 * Math.pow(2, currentRetry); // 8s, 16s, 32s
                    const retryMsg = `AI is busy... retrying in ${backoffDelay / 1000}s (attempt ${currentRetry + 1}/${maxRetries})`;
                    setAiStatus(retryMsg);
                    setShowQuotaWarning(true);

                    setTimeout(() => {
                        setShowQuotaWarning(false);
                        handleAnswerSubmission(answer, currentRetry + 1);
                    }, backoffDelay);
                } else {
                    // Max retries exceeded — give up gracefully and move on
                    setShowQuotaWarning(false);
                    const sorryMsg = "I apologize, there seems to be a temporary issue on my end. Let's move on to the next question.";
                    addMessage('ai', sorryMsg);
                    await speak(sorryMsg);
                    setIsProcessing(false);
                    isProcessingRef.current = false;
                    // FIX: Add delay before restarting mic
                    if (userInputMode === 'audio' && !showQuotaWarning) {
                        setTimeout(() => {
                            if (!isCompletedRef.current && !isProcessingRef.current) {
                                startListening();
                            }
                        }, 600);
                    }
                    setAiStatus("Indu is Online");
                }
                return;
            }

            // Show AI failure inline (NO blocking alert — keeps the session alive)
            const errorMessage = err.response?.data?.error || err.message || "Unknown error";
            console.error("AI submission error:", errorMessage);
            
            // FIX: Better error handling for timeouts
            if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
                setAiStatus("⏱️ Processing timeout - Please wait...");
            } else {
                setAiStatus("Connection Issue — Retrying...");
            }

            const recoveryMsg = "I apologize, I'm having a brief connectivity issue. Please try repeating your answer or click the microphone to continue.";
            addMessage('ai', recoveryMsg);
            await speak(recoveryMsg);

            setAiStatus("Indu is Online");

            // Automatically try to restart the mic to help the user
            if (userInputMode === 'audio') {
                // FIX: Add delay to ensure previous audio finishes
                setTimeout(() => {
                    if (!isCompletedRef.current && !isProcessingRef.current) {
                        startListening();
                    }
                }, 800);
            }
        }
    }, [token, questions, currentQuestionIndex, isProcessing, addMessage, speak, completeInterview, startListening, showQuotaWarning, userInputMode, submitAnswerWithRetry, recordActivity, validateAnswer, waitForSpeechToFinish]);

    // 4. Lifecycle
    useEffect(() => {
        if (isInitializedRef.current) return;
        isInitializedRef.current = true;

        const initSession = async () => {
            try {
                // Check localStorage first for instant blocking
                if (localStorage.getItem(`interview_completed_${token}`)) {
                    setAiStatus("Already Completed");
                    setIsCompleted(true);
                    return;
                }

                // Restore from auto-saved progress if available (within 30 minutes)
                try {
                    const saved = localStorage.getItem(`interview_progress_${token}`);
                    if (saved) {
                        const progress = JSON.parse(saved);
                        if (progress && (Date.now() - progress.timestamp) < 30 * 60 * 1000) {
                            console.log('Restoring interview progress from localStorage');
                            if (progress.candidateName) setCandidateName(progress.candidateName);
                            if (Array.isArray(progress.chatMessages)) setChatMessages(progress.chatMessages);
                            if (Array.isArray(progress.chatHistory)) chatHistoryRef.current = progress.chatHistory;
                            if (typeof progress.currentQuestionIndex === 'number') setCurrentQuestionIndex(progress.currentQuestionIndex);
                            if (Array.isArray(progress.questions)) setQuestions(progress.questions);
                        }
                    }
                } catch (e) {
                    console.warn('Failed to restore saved progress:', e);
                }

                const res = await axios.get(`${API_BASE_URL}/ai-candidates/public/${token}/?_t=${Date.now()}`);
                const candidate = res.data;
                setCandidateData(candidate);
                setCandidateName(candidate.full_name);

                if (candidate.status === 'Completed') {
                    setIsCompleted(true);
                    return;
                }

                if (candidate.link_opened_at) {
                    const startTime = new Date(candidate.link_opened_at).getTime();
                    const now = new Date().getTime();
                    const secondsElapsed = Math.floor((now - startTime) / 1000);
                    const initialTimeLeft = Math.max(0, (60 * 60) - secondsElapsed);
                    setTimeLeft(initialTimeLeft);
                }

                if (candidate.interview_summary && candidate.interview_summary.length > 0) {
                    setAiStatus("Ready to Resume");
                } else {
                    setAiStatus("Ready to Start");
                }
            } catch (err) {
                console.error("Session init error:", err);
            }
        };

        initSession();
        return () => stopCamera();
    }, [token]);

    // FIX: Auto-save interview progress to localStorage to prevent data loss
    useEffect(() => {
        if (!token || chatMessages.length === 0 || isCompleted) return;

        const autoSaveInterval = setInterval(() => {
            const progressData = {
                timestamp: Date.now(),
                token,
                currentQuestionIndex,
                chatMessages,
                chatHistory: chatHistoryRef.current,
                questions,
                candidateName
            };
            localStorage.setItem(`interview_progress_${token}`, JSON.stringify(progressData));
        }, 5000); // Auto-save every 5 seconds

        return () => clearInterval(autoSaveInterval);
    }, [token, chatMessages, currentQuestionIndex, questions, isCompleted, candidateName]);

    // FIX: Restore interview progress from localStorage on page load
    useEffect(() => {
        if (!token || isInitializedRef.current) return;
        
        const savedProgress = localStorage.getItem(`interview_progress_${token}`);
        if (savedProgress) {
            try {
                const progressData = JSON.parse(savedProgress);
                // Only restore if it's for the same candidate and interview not completed
                if (progressData.token === token && !isCompleted) {
                    console.log("🔄 [Restore] Found saved interview progress, restoring...");
                    
                    // Restore state
                    if (progressData.currentQuestionIndex > 0) {
                        setCurrentQuestionIndex(progressData.currentQuestionIndex);
                    }
                    if (progressData.questions && progressData.questions.length > 0) {
                        setQuestions(progressData.questions);
                        setMaxQuestions(Math.min(progressData.questions.length, 13));
                    }
                    if (progressData.chatMessages && progressData.chatMessages.length > 0) {
                        setChatMessages(progressData.chatMessages);
                    }
                    if (progressData.chatHistory && progressData.chatHistory.length > 0) {
                        chatHistoryRef.current = progressData.chatHistory;
                    }
                    if (progressData.candidateName) {
                        setCandidateName(progressData.candidateName);
                    }
                    
                    console.log("✅ [Restore] Interview progress restored successfully");
                    
                    // Clear saved progress after successful submission/completion
                    // This prevents stale data on re-interview
                }
            } catch (e) {
                console.error("[Restore] Failed to parse saved progress:", e);
            }
        }
    }, [token]); // Only run once on mount

    const handleStartInterview = async () => {
        // Step 1: Just request Camera for face registration
        console.log("Requesting Camera...");
        await startCamera();

        console.log("Basic permissions (Camera) granted.");
        setIsPermissionsGranted(true);
        setAiStatus("Starting Registration...");
        setWizardStep(0); 

        setTimeout(() => {
            if (regVideoRef.current && streamRef.current) {
                regVideoRef.current.srcObject = streamRef.current;
                regVideoRef.current.play().catch(e => console.warn("regVideo auto-play prevented:", e));
            }
        }, 500);
    };

    const handleRegisterFace = async () => {
        const videoElement = regVideoRef.current || videoRef.current;
        if (!videoElement || videoElement.readyState < 2) return;
        setWizardStep(1); // 'verifying'

        try {
            const canvas = document.createElement('canvas');
            canvas.width = 640;
            canvas.height = 480;
            const ctx = canvas.getContext('2d');
            ctx.filter = 'brightness(1.15) contrast(1.2)';
            ctx.drawImage(videoElement, 0, 0, 640, 480);
            ctx.filter = 'none';
            
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
            const b64 = dataUrl.split(',')[1];
            setCapturedImage(dataUrl); 
            
            const personId = getDeepfacePersonId();
            if (!personId) {
                throw new Error('Missing interview token for DeepFace registration.');
            }

            // Check if this is a PAN-recovery case (different person_id to verify against)
            const verifyAgainstPersonId = sessionStorage.getItem('verify_against_person_id');
            const pendingPan = sessionStorage.getItem('pending_pan');

            // Step 1: Ask DeepFace if this person already has a registered face
            // (Do NOT rely on candidateData - it may not be loaded yet due to race condition)
            let hasExistingFace = false;
            try {
                const checkRes = await axios.get(`${DEEPFACE_BASE_URL}/registration/registered/${personId}`);
                hasExistingFace = checkRes.data?.registered === true;
                console.log(`[Face] DeepFace reports person ${personId} has existing face: ${hasExistingFace}`);
            } catch (err) {
                console.warn('[Face] Could not check registration status, assuming new:', err.message);
                hasExistingFace = false;
            }

            let regRes = null;
            let verifyRes = null;
            let embeddingHash = null;

            // CASE A: Using a PAN that belongs to someone else (verify against original holder)
            if (verifyAgainstPersonId) {
                console.log(`[Face] PAN-recovery mode: verifying against original holder ${verifyAgainstPersonId}`);
                verifyRes = await axios.post(`${DEEPFACE_BASE_URL}/registration/verify`, {
                    person_id: verifyAgainstPersonId,
                    image_base64: b64
                });

                if (verifyRes.data?.verified) {
                    console.log('[Face] PAN-recovery: face matches original holder. Identity confirmed.');
                    // Re-register under current token to update embeddings
                    regRes = await axios.post(`${DEEPFACE_BASE_URL}/registration/register`, {
                        person_id: personId,
                        image_base64: b64
                    });
                    embeddingHash = regRes.data?.embedding_hash;
                } else {
                    const msg = verifyRes.data?.message || 'Face does not match the registered photo.';
                    console.error('[Face] PAN-recovery failed:', msg);
                    setWizardStep(3);
                    setCapturedImage(null);
                    alert(`Identity verification failed: ${msg}\n\nThis PAN is registered to another person. Please use your own PAN.`);
                    return;
                }
            }
            // CASE B: Returning candidate (same token) with existing face
            else if (hasExistingFace) {
                console.log(`[Face] Returning candidate: verifying new photo against stored embeddings for ${personId}`);
                verifyRes = await axios.post(`${DEEPFACE_BASE_URL}/registration/verify`, {
                    person_id: personId,
                    image_base64: b64
                });

                if (verifyRes.data?.verified) {
                    console.log('[Face] Returning candidate verified. Same person.');
                    // Re-register to update stored embeddings
                    regRes = await axios.post(`${DEEPFACE_BASE_URL}/registration/register`, {
                        person_id: personId,
                        image_base64: b64
                    });
                    embeddingHash = regRes.data?.embedding_hash;
                } else {
                    const msg = verifyRes.data?.message || 'Face does not match your previously registered photo.';
                    console.error('[Face] Returning candidate verification failed:', msg);
                    setWizardStep(3);
                    setCapturedImage(null);
                    alert(`Identity verification failed: ${msg}\n\nYou are using a different face than what was originally registered. If you believe this is an error, please ensure good lighting and face the camera directly.`);
                    return;
                }
            }
            // CASE C: Brand new candidate
            else {
                console.log(`[Face] New candidate: registering face for ${personId}`);
                regRes = await axios.post(`${DEEPFACE_BASE_URL}/registration/register`, {
                    person_id: personId,
                    image_base64: b64
                });
                embeddingHash = regRes.data?.embedding_hash;
            }

            // Validate registration result
            const success = regRes?.data?.success || (verifyRes?.data?.verified && embeddingHash);
            if (!success) {
                setWizardStep(3);
                setCapturedImage(null);
                alert(regRes?.data?.message || 'Face registration failed. Please ensure your face is clearly visible.');
                return;
            }

            // Send hash to backend
            if (embeddingHash) {
                faceEmbeddingHashRef.current = embeddingHash;
                console.log('[Face] Embedding hash captured:', embeddingHash.substring(0, 16) + '...');
                
                const payload = { face_embedding_hash: embeddingHash };
                if (verifyAgainstPersonId) {
                    payload.face_verified = true;
                }
                if (pendingPan) {
                    payload.pan_number = pendingPan;
                }
                
                try {
                    await axios.post(`${API_BASE_URL}/ai-candidates/public/${token}/register/`, payload);
                    console.log('[Face] Face hash sent to backend successfully');
                    sessionStorage.removeItem('verify_against_person_id');
                    sessionStorage.removeItem('pending_pan');
                } catch (hashErr) {
                    console.error('[Face] Failed to send face hash:', hashErr);
                    if (hashErr.response?.data?.duplicate_face) {
                        setWizardStep(3);
                        setCapturedImage(null);
                        alert(hashErr.response.data.error || 'This face is already registered to another candidate.');
                        return;
                    }
                }
            }

            setWizardStep(2); // 'success'
            logCandidateActivity(token, 'AI Interview Started', 'Candidate passed proctoring check and started the AI Interview.');
            setTimeout(() => {
                setWizardStep(4); // Environment Checks
            }, 1500);
        } catch (err) {
            console.error("Registration error:", err);
            setWizardStep(3); // 'error'
            setCapturedImage(null);
            alert('Failed to connect to DeepFace registration service. ' + (err.response?.data?.detail || err.response?.data?.message || err.message));
        }
    };

    const handleEnvironmentSetup = async () => {
        setAiStatus("Setting up environment...");
        // NEW: Pause timer during setup
        setIsPaused(true);

        // STEP 1: Request Screen Share FIRST (if not already active)
        if (!isScreenSharing) {
            console.log("Requesting Screen Share...");
            const screenSuccess = await startScreenShare();
            if (!screenSuccess) {
                console.warn("Screen share denied during setup.");
                setIsPaused(false);
                return;
            }
            // Screen share granted successfully - now automatically trigger fullscreen
            console.log("Screen share active. Auto-triggering fullscreen...");
        }

        // STEP 2: Auto-trigger Fullscreen after screen share is granted (if not already active)
        if (!isFullscreen) {
            try {
                const elem = document.documentElement;
                if (elem.requestFullscreen) {
                    await elem.requestFullscreen();
                } else if (elem.webkitRequestFullscreen) {
                    await elem.webkitRequestFullscreen();
                } else if (elem.msRequestFullscreen) {
                    await elem.msRequestFullscreen();
                }
                setIsFullscreen(true);
                isFullscreenRef.current = true;
                console.log("Fullscreen activated automatically after screen share.");
                // NEW: Resume timer after setup
                setIsPaused(false);
            } catch (err) {
                console.warn("Fullscreen request failed during setup:", err);
                setIsPaused(false);
                alert("Fullscreen mode is required for this interview. Please click 'Enable Fullscreen' to continue.");
                return;
            }
        }
    };

    const handleBeginInterview = async () => {
        if (!isFullscreen || !isScreenSharing) {
            alert("Please enable Fullscreen and Screen Sharing to begin.");
            return;
        }

        // NEW: Check microphone quality before starting
        try {
            const testStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const micOk = await checkMicrophoneQuality(testStream);
            testStream.getTracks().forEach(t => t.stop());
            if (!micOk) {
                console.warn("[Mic Check] Microphone quality check failed, but allowing interview to proceed.");
            }
        } catch (e) {
            console.warn("[Mic Check] Could not test microphone:", e);
        }
        
        try {
            const res = await axios.get(`${API_BASE_URL}/ai-candidates/public/${token}/?_t=${Date.now()}`);
            setIsFaceRegistered(true); // This hides the overlay
            finalizeInterviewStart(res.data);
        } catch (err) {
            console.error("Final start error:", err);
            alert("Error retrieving candidate data. Please refresh.");
        }
    };

    const finalizeInterviewStart = async (candidate) => {
        setAiStatus("Preparing Indu...");

        // Load questions NOW (after face registration is confirmed)
        const qList = candidate.interview_questions || [];
        setQuestions(qList);

        // Start DeepFace proctoring session (uses candidate.id as person_id)
        // Only start if not already running to prevent session leak
        if (!dfSessionIdRef.current) {
            await startDeepfaceMonitoring(getDeepfacePersonId());
        }

        if (candidate.interview_summary && candidate.interview_summary.length > 0) {
            console.log("Resuming session...");
            const summary = candidate.interview_summary;
            const restoredMessages = [];
            const restoredHistory = [];
            summary.forEach(turn => {
                restoredMessages.push({ sender: 'ai', text: turn.question }, { sender: 'user', text: turn.answer });
                restoredHistory.push({ role: 'assistant', content: turn.question }, { role: 'user', content: turn.answer });
            });
            setChatMessages(restoredMessages);
            chatHistoryRef.current = restoredHistory;
            const nextIdx = summary.length;
            setCurrentQuestionIndex(nextIdx);

            const resumeQ = qList[nextIdx] || "Let's continue. Please share more about your experience.";
            addMessage('ai', resumeQ);
            await speak(resumeQ);
            if (userInputMode === 'audio') startListening();
        } else {
            const firstName = candidate.full_name.split(' ')[0];
            const welcome = `Hi ${firstName}! This is Indu. Hope you're doing well, I'll be your interviewer today.`;
            const introQ = "To get started, please introduce yourself and your professional background.";

            // FIX: Strictly enforce 13 questions total to prevent count mismatch
            // Backend provides 13 questions, frontend should NOT add intro if already at limit
            let finalQs = [...qList];
            const TOTAL_QUESTIONS_LIMIT = 13;
            
            // Check if backend already has an intro-style question
            const backendHasIntro = finalQs.length > 0 && 
                (finalQs[0].toLowerCase().includes('introduce') || 
                 finalQs[0].toLowerCase().includes('background') ||
                 finalQs[0] === introQ);
            
            // Only add intro if:
            // 1. Backend doesn't already have an intro question AND
            // 2. Adding it won't exceed the 13 question limit
            if (!backendHasIntro && finalQs.length < TOTAL_QUESTIONS_LIMIT) {
                // Add intro but keep total at 13 by removing last question if needed
                finalQs = [introQ, ...finalQs];
                if (finalQs.length > TOTAL_QUESTIONS_LIMIT) {
                    finalQs = finalQs.slice(0, TOTAL_QUESTIONS_LIMIT);
                }
                setQuestions(finalQs);
                setMaxQuestions(finalQs.length);
                console.log(`[Question Fix] Added intro question. Total: ${finalQs.length}`);
            } else if (!backendHasIntro && finalQs.length >= TOTAL_QUESTIONS_LIMIT) {
                // Backend already has 13 questions, replace first with intro
                finalQs = [introQ, ...finalQs.slice(1)];
                setQuestions(finalQs);
                setMaxQuestions(TOTAL_QUESTIONS_LIMIT);
                console.log(`[Question Fix] Replaced first question with intro. Total: ${finalQs.length}`);
            } else {
                // Backend already has intro, use as-is but cap at 13
                if (finalQs.length > TOTAL_QUESTIONS_LIMIT) {
                    finalQs = finalQs.slice(0, TOTAL_QUESTIONS_LIMIT);
                }
                setQuestions(finalQs);
                setMaxQuestions(finalQs.length);
                console.log(`[Question Fix] Using backend questions. Total: ${finalQs.length}`);
            }

            const combinedStart = `${welcome} ${introQ}`;
            addMessage('ai', combinedStart);
            await speak(combinedStart);
            // FIX: Add delay before starting mic to prevent speech feedback loop
            if (userInputMode === 'audio') {
                setTimeout(() => {
                    if (!isCompletedRef.current && !isProcessingRef.current) {
                        startListening();
                    }
                }, 800);
            }
        }
    };

    useEffect(() => {
        startListeningRef.current = startListening;
    }, [startListening]);

    useEffect(() => {
        submitHandlerRef.current = handleAnswerSubmission;
    }, [handleAnswerSubmission]);

    // AUTO-RESUME MIC after Fullscreen restore
    // GUARD: Only auto-resume AFTER face registration is complete
    useEffect(() => {
        if (isFullscreen && isPermissionsGranted && !isCompleted && !isRecording && !isProcessing && isInitializedRef.current && isFaceRegistered) {
            // FIX: Respect manual mute — don't auto-resume if user explicitly turned mic off
            if (manualMuteRef.current) {
                console.log("Auto-resume skipped: User manually muted mic.");
                return;
            }
            const timer = setTimeout(() => {
                if (!isRecordingRef.current && !manualMuteRef.current) {
                    console.log("Auto-resuming mic via Effect...");
                    startListening();
                }
            }, 1000); // 1s buffer allowed for transition to settle
            return () => clearTimeout(timer);
        }
    }, [isFullscreen, isPermissionsGranted, isCompleted, isRecording, isProcessing, startListening, isFaceRegistered]);

    // (Native WebKit Speech Recognition removed in favor of AssemblyAI)
    useEffect(() => {
        // Initialize recognitionRef stub so toggleRecording doesn't fail immediately
        if (!recognitionRef.current) {
            recognitionRef.current = {
                start: startListening,
                stop: () => {
                    if (assemblyAIRef.current) assemblyAIRef.current.stop();
                }
            };
        }
    }, [startListening]);

    // --- UNIFIED ACTIVITY WATCHDOG ---
    // This single interval handles all microphone lifecycle timing
    useEffect(() => {
        if (!isRecording) {
            setSilenceCountdown(0);
            return;
        }

        let secondsRemaining = 5;
        const watchdog = setInterval(() => {
            // Safety Guard: If mic is physically off, this interval MUST not proceed
            if (!isRecordingRef.current || isCompletedRef.current) {
                clearInterval(watchdog);
                return;
            }
            if (isSpeakingRef.current || isProcessingRef.current) return;

            const timeSinceActivity = Date.now() - lastSpokenTimeRef.current;

            // If the user has spoken or transcript has updated within the last 2 seconds, 
            // keep the timer at 5. This prevents cutouts during natural speech pauses.
            if (timeSinceActivity < 2000) {
                secondsRemaining = 5;
                setSilenceCountdown("Listening...");
                // FIX: Reset consecutive silence counter if candidate speaks during countdown
                // This prevents false positives when AssemblyAI delivers delayed transcripts
                if (consecutiveSilenceRef.current > 0) {
                    consecutiveSilenceRef.current = 0;
                    recordActivity();
                    console.log("🎤 [Silence Fix] Candidate spoke during silence countdown, resetting silence counter");
                }
                return;
            }

            // Otherwise, proceed with the visible countdown (5-4-3-2-1)
            secondsRemaining = 5 - Math.floor((timeSinceActivity - 2000) / 1000);

            if (secondsRemaining > 0) {
                setSilenceCountdown(secondsRemaining + "s");
            } else if (secondsRemaining === 0 || secondsRemaining === -1) {
                // FIX: Add warning when countdown is critical
                setSilenceCountdown("⚠️ 0s");
            } else if (secondsRemaining <= -2) {
                // TRUE EXPIRATION
                console.log("Unified Watchdog: Maximum silence exceeded. Forcing submission.");
                clearInterval(watchdog);
                setSilenceCountdown(0);

                // FIX: Immediately turn off mic icon BEFORE stopping AssemblyAI
                setIsRecording(false);
                isRecordingRef.current = false;

                setIsProcessing(true);
                isProcessingRef.current = true;
                setAiStatus("Processing answer...");

                if (assemblyAIRef.current) {
                    try { assemblyAIRef.current.stop(); } catch (e) { }
                }

                const finalTranscript = (transcriptRef.current + interimTranscriptRef.current).trim();
                const submissionText = finalTranscript || "[Candidate remained silent/skipped]";

                if (submitHandlerRef.current) {
                    submitHandlerRef.current(submissionText);
                }
            }
        }, 1000);

        return () => clearInterval(watchdog);
    }, [isRecording]);



    const toggleRecording = () => {
        if (!isFullscreen) {
            alert("Please return to full-screen mode to resume the interview.");
            return;
        }

        // Unlock speech on first user click if not already
        unlockSpeech();

        if (isRecording) {
            // Capture any final speech before stopping
            const finalSubmission = (transcriptRef.current + interimTranscriptRef.current).trim();

            // FIX: Mark as manually muted so auto-resume doesn't override user's choice
            manualMuteRef.current = true;

            try { if (assemblyAIRef.current) assemblyAIRef.current.stop(); } catch (e) { }
            setIsRecording(false);
            isRecordingRef.current = false;

            // If the user actually said something, instantly submit it instead of discarding it!
            if (finalSubmission && finalSubmission.length > 3) {
                console.log("Manual Mic Stop: Auto-submitting speech!");
                if (submitHandlerRef.current) submitHandlerRef.current(finalSubmission);
            } else {
                setAiStatus("Mic Muted"); // Clear the "Listening..." label since nothing was submitted
            }
        } else {
            // Cancel any AI speech if user wants to speak
            if (synthRef.current.speaking) {
                synthRef.current.cancel();
                setIsSpeaking(false);
            }
            // FIX: Clear manual mute since user is explicitly turning mic back on
            manualMuteRef.current = false;
            startListening();
        }
    };

    useEffect(() => {
        if (chatContainerRef.current) chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }, [chatMessages]);

    // Timer Countdown Effect
    useEffect(() => {
        if (timeLeft === null || isCompleted) return;

        if (timeLeft <= 0) {
            // NEVER abruptly cut the interview. Set the flag, and the normal 
            // conversation loop will gracefully end the call after the current answer.
            if (!timeExpiredRef.current) {
                timeExpiredRef.current = true;
                console.log("Global timer expired. Deferring actual completion to end of current conversational turn...");
            }
            return;
        }

        // NEW: Pause timer during interruptions (fullscreen requests, dialogs, etc.)
        if (isPaused) {
            return;
        }

        const timer = setInterval(() => {
            setTimeLeft(prev => prev - 1);
        }, 1000);

        return () => clearInterval(timer);
    }, [timeLeft, isCompleted, isPaused, completeInterview]);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    useEffect(() => {
        return () => {
            if (animationRef.current) cancelAnimationFrame(animationRef.current);
            if (visualizerCtxRef.current) {
                try { visualizerCtxRef.current.close(); } catch (e) { }
            }
        };
    }, []);

    return (
        <div className="ai-session-page">
            {/* Fullscreen/Screen Share requirement overlay */}
            {isPermissionsGranted && (!isFullscreen || !isScreenSharing) && !isCompleted && (
                <div
                    onClick={() => {
                        if (!isFullscreen) {
                            const elem = document.documentElement;
                            if (elem.requestFullscreen) elem.requestFullscreen();
                            else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
                            else if (elem.msRequestFullscreen) elem.msRequestFullscreen();
                        }
                    }}
                    style={{
                        position: 'fixed',
                        inset: 0,
                        background: '#0a0a0a',
                        color: 'white',
                        zIndex: 30000,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textAlign: 'center',
                        padding: '2rem',
                        fontFamily: 'Inter, sans-serif'
                    }}
                >
                    <div style={{ maxWidth: '600px' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'center', gap: '1rem' }}>
                            <span style={{ filter: isFullscreen ? 'grayscale(0%)' : 'grayscale(100%)' }}>📺</span>
                            <span style={{ filter: isScreenSharing ? 'grayscale(0%)' : 'grayscale(100%)' }}>🖥️</span>
                        </div>
                        <h1 style={{ fontSize: '2.5rem', marginBottom: '1.5rem', fontWeight: '800', letterSpacing: '-0.02em' }}>
                            Resume Interview Requirements
                        </h1>
                        <div style={{ background: 'rgba(99, 102, 241, 0.1)', padding: '1.5rem', borderRadius: '12px', marginBottom: '2rem', textAlign: 'left' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1rem', fontSize: '1.1rem' }}>
                                <span style={{ fontSize: '1.3rem' }}>{isFullscreen ? '✅' : '❌'}</span>
                                <span>Fullscreen Mode: <strong>{isFullscreen ? 'Active' : 'Required'}</strong></span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '1.1rem' }}>
                                <span style={{ fontSize: '1.3rem' }}>{isScreenSharing ? '✅' : '❌'}</span>
                                <span>Screen Sharing: <strong>{isScreenSharing ? 'Active' : 'Required'}</strong></span>
                            </div>
                        </div>
                        <p style={{ fontSize: '1rem', color: '#94a3b8', marginBottom: '2rem', lineHeight: '1.6' }}>
                            {!isFullscreen && !isScreenSharing
                                ? 'Please enable both Fullscreen mode and Screen Sharing to continue.'
                                : !isFullscreen
                                ? 'Please enter Fullscreen mode to continue.'
                                : 'Please restart Screen Sharing (Entire Screen) to continue.'}
                        </p>
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                            {!isFullscreen && (
                                <button
                                    onClick={() => {
                                        const elem = document.documentElement;
                                        if (elem.requestFullscreen) elem.requestFullscreen();
                                        else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
                                        else if (elem.msRequestFullscreen) elem.msRequestFullscreen();
                                    }}
                                    className="resume-integrity-btn"
                                    style={{
                                        background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                                        color: 'white', border: 'none', padding: '0.8rem 2rem',
                                        borderRadius: '8px', fontSize: '1rem', fontWeight: 'bold',
                                        cursor: 'pointer', flex: 1, minWidth: '150px'
                                    }}
                                >
                                    📺 Enter Full Screen
                                </button>
                            )}
                            {!isScreenSharing && (
                                <button
                                    onClick={startScreenShare}
                                    className="resume-integrity-btn"
                                    style={{
                                        background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                                        color: 'white', border: 'none', padding: '0.8rem 2rem',
                                        borderRadius: '8px', fontSize: '1rem', fontWeight: 'bold',
                                        cursor: 'pointer', flex: 1, minWidth: '150px'
                                    }}
                                >
                                    🖥️ Share Screen
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Welcome Screen - shown after registration but before camera */}
            {
                !isPermissionsGranted && !isFaceRegistered && !isCompleted && (
                    <div style={{
                        position: 'fixed',
                        inset: 0,
                        background: 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(10px)',
                        zIndex: 20000,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textAlign: 'center',
                        padding: '2rem'
                    }}>
                        <div style={{ maxWidth: '600px', background: 'white', padding: '3rem', borderRadius: '30px', boxShadow: '0 20px 50px rgba(0,0,0,0.1)' }}>
                            <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>👋</div>
                            <h1 style={{ fontSize: '2rem', color: '#1a202c', marginBottom: '1rem', fontWeight: '800' }}>Ready to meet Indu?</h1>
                            <p style={{ color: '#4a5568', fontSize: '1.1rem', marginBottom: '2rem', lineHeight: '1.6' }}>
                                To ensure a fair and secure interview process, we require access to your <b>Camera</b> and <b>Entire Screen Share</b>.
                            </p>
                            <div style={{ background: '#f8fafc', padding: '1.5rem', borderRadius: '15px', marginBottom: '2.5rem', textAlign: 'left' }}>
                                <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                                    <i className="fa-solid fa-camera" style={{ color: '#6366f1', marginTop: '4px' }}></i>
                                    <span><b>Webcam:</b> Used for face and phone detection.</span>
                                </div>
                                <div style={{ display: 'flex', gap: '12px' }}>
                                    <i className="fa-solid fa-desktop" style={{ color: '#6366f1', marginTop: '4px' }}></i>
                                    <span><b>Screen:</b> Used for tab-switch monitoring. Please choose "Entire Screen".</span>
                                </div>
                            </div>
                            <button
                                onClick={handleStartInterview}
                                className="start-session-btn"
                                style={{
                                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                    color: 'white',
                                    border: 'none',
                                    padding: '1rem 3rem',
                                    borderRadius: '50px',
                                    fontSize: '1.2rem',
                                    fontWeight: '700',
                                    cursor: 'pointer',
                                    transition: 'transform 0.2s',
                                    boxShadow: '0 10px 20px rgba(102, 126, 234, 0.3)'
                                }}
                                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                            >
                                Start Interview
                            </button>
                        </div>
                    </div>
                )
            }

            {
                isPermissionsGranted && !isFaceRegistered && !isCompleted && (
                    <div style={{
                        position: 'fixed',
                        inset: 0,
                        background: 'rgba(255, 255, 255, 0.98)',
                        zIndex: 15000,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textAlign: 'center',
                        padding: '2rem'
                    }}>
                        <div style={{ maxWidth: '600px', width: '100%', background: 'white', padding: '2.5rem', borderRadius: '30px', boxShadow: '0 20px 50px rgba(0,0,0,0.1)' }}>
                            {wizardStep === 4 ? (
                                <>
                                    <h2 style={{ fontSize: '1.8rem', color: '#1a202c', marginBottom: '1rem', fontWeight: '800' }}>Environment Setup</h2>
                                    <p style={{ color: '#4a5568', fontSize: '1rem', marginBottom: '2.5rem' }}>
                                        Final check before we begin. Please ensure you are in the secure environment.
                                    </p>

                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '3rem', textAlign: 'left', background: '#f8fafc', padding: '2rem', borderRadius: '20px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: '#22c55e', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem' }}>✓</div>
                                                <span style={{ fontWeight: '600', color: '#2d3748' }}>Identity Verified</span>
                                            </div>
                                            <span style={{ color: '#22c55e', fontWeight: '700', fontSize: '0.9rem' }}>READY</span>
                                        </div>

                                        {/* STEP 1: Screen Share (User must click this first) */}
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: isScreenSharing ? '#22c55e' : '#6366f1', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: '700' }}>
                                                    {isScreenSharing ? '✓' : '1'}
                                                </div>
                                                <span style={{ fontWeight: '600', color: isScreenSharing ? '#2d3748' : '#1e293b' }}>Screen Sharing</span>
                                                {!isScreenSharing && <span style={{ fontSize: '0.7rem', color: '#6366f1', background: '#eef2ff', padding: '2px 8px', borderRadius: '4px' }}>Click below</span>}
                                            </div>
                                            {isScreenSharing ? (
                                                <span style={{ color: '#22c55e', fontWeight: '700', fontSize: '0.9rem' }}>ACTIVE</span>
                                            ) : (
                                                <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>Required</span>
                                            )}
                                        </div>

                                        {/* STEP 2: Fullscreen (Auto-triggered after screen share) */}
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', opacity: isScreenSharing ? 1 : 0.5 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: isFullscreen ? '#22c55e' : isScreenSharing ? '#f59e0b' : '#cbd5e1', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: '700' }}>
                                                    {isFullscreen ? '✓' : isScreenSharing ? '...' : '2'}
                                                </div>
                                                <span style={{ fontWeight: '600', color: isFullscreen ? '#2d3748' : isScreenSharing ? '#1e293b' : '#718096' }}>Full Screen Mode</span>
                                                {isScreenSharing && !isFullscreen && <span style={{ fontSize: '0.7rem', color: '#f59e0b', background: '#fffbeb', padding: '2px 8px', borderRadius: '4px' }}>Auto-starting...</span>}
                                            </div>
                                            {isFullscreen ? (
                                                <span style={{ color: '#22c55e', fontWeight: '700', fontSize: '0.9rem' }}>ACTIVE</span>
                                            ) : (
                                                <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{isScreenSharing ? 'Please allow...' : 'Waiting...'}</span>
                                            )}
                                        </div>

                                        {/* Progress indicator */}
                                        <div style={{ marginTop: '1rem', padding: '1rem', background: '#f8fafc', borderRadius: '12px', textAlign: 'center' }}>
                                            {!isScreenSharing ? (
                                                <p style={{ margin: 0, color: '#475569', fontSize: '0.9rem' }}>
                                                    <strong>Step 1 of 2:</strong> Click "Start Screen Share" below to begin
                                                </p>
                                            ) : !isFullscreen ? (
                                                <p style={{ margin: 0, color: '#f59e0b', fontSize: '0.9rem' }}>
                                                    <strong>Step 2 of 2:</strong> Please allow fullscreen mode when prompted...
                                                </p>
                                            ) : (
                                                <p style={{ margin: 0, color: '#22c55e', fontSize: '0.9rem' }}>
                                                    <strong>✓ All set!</strong> You can now begin the interview
                                                </p>
                                            )}
                                        </div>
                                    </div>

                                    {/* Show appropriate button based on state */}
                                    {!isScreenSharing ? (
                                        /* STEP 1: Start Screen Share */
                                        <button
                                            onClick={handleEnvironmentSetup}
                                            style={{
                                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                                color: 'white', border: 'none', padding: '1.2rem 3rem', borderRadius: '50px',
                                                fontSize: '1.1rem', fontWeight: '800', cursor: 'pointer',
                                                boxShadow: '0 10px 25px rgba(102, 126, 234, 0.3)'
                                            }}
                                        >
                                            Start Screen Share
                                        </button>
                                    ) : !isFullscreen ? (
                                        /* STEP 2: Waiting for fullscreen (user may need manual button if auto fails) */
                                        <button
                                            onClick={handleEnvironmentSetup}
                                            style={{
                                                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                                                color: 'white', border: 'none', padding: '1.2rem 3rem', borderRadius: '50px',
                                                fontSize: '1.1rem', fontWeight: '800', cursor: 'pointer',
                                                animation: 'pulse-amber 1.5s infinite'
                                            }}
                                        >
                                            Enable Fullscreen
                                        </button>
                                    ) : (
                                        /* Both ready - Begin Interview */
                                        <button
                                            onClick={handleBeginInterview}
                                            style={{
                                                background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                                                color: 'white', border: 'none', padding: '1.2rem 4rem', borderRadius: '50px',
                                                fontSize: '1.2rem', fontWeight: '800', cursor: 'pointer',
                                                boxShadow: '0 10px 25px rgba(34, 197, 94, 0.3)',
                                                animation: 'pulse-green 2s infinite'
                                            }}
                                        >
                                            Begin Interview
                                        </button>
                                    )}
                                    <style>{`
                                        @keyframes pulse-green {
                                            0% { transform: scale(1); box-shadow: 0 10px 25px rgba(34, 197, 94, 0.3); }
                                            50% { transform: scale(1.03); box-shadow: 0 15px 35px rgba(34, 197, 100, 0.4); }
                                            100% { transform: scale(1); box-shadow: 0 10px 25px rgba(34, 197, 94, 0.3); }
                                        }
                                        @keyframes pulse-amber {
                                            0% { transform: scale(1); box-shadow: 0 10px 25px rgba(245, 158, 11, 0.3); }
                                            50% { transform: scale(1.03); box-shadow: 0 15px 35px rgba(245, 158, 11, 0.4); }
                                            100% { transform: scale(1); box-shadow: 0 10px 25px rgba(245, 158, 11, 0.3); }
                                        }
                                    `}</style>
                                </>
                            ) : (
                                <>
                                    <h2 style={{ fontSize: '1.8rem', color: '#1a202c', marginBottom: '1rem', fontWeight: '800' }}>AI Face Registration</h2>
                                    <p style={{ color: '#4a5568', fontSize: '1rem', marginBottom: '2rem' }}>
                                        Please look directly at the camera. We need to register your face for our AI proctoring system.
                                    </p>
                                    
                                    <div style={{ width: '100%', maxWidth: '400px', margin: '0 auto 2rem', aspectRatio: '4/3', borderRadius: '20px', overflow: 'hidden', background: '#000', position: 'relative' }}>
                                        {capturedImage ? (
                                            <img src={capturedImage} alt="Captured face" style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                                        ) : (
                                            <video ref={regVideoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                                        )}
                                        
                                        {/* Overlay guides */}
                                        <div style={{ position: 'absolute', top: '10%', bottom: '15%', left: '25%', right: '25%', border: '2px dashed rgba(255,255,255,0.7)', borderRadius: '50%' }}></div>
                                        
                                        {wizardStep === 1 && (
                                            <>
                                                <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>
                                                    Analyzing face...
                                                </div>
                                                {/* CSS AI Scanning Animation Line */}
                                                <div style={{
                                                    position: 'absolute',
                                                    top: 0,
                                                    left: 0,
                                                    right: 0,
                                                    height: '4px',
                                                    background: '#6366f1',
                                                    boxShadow: '0 0 15px 4px rgba(99, 102, 241, 0.6)',
                                                    animation: 'ai-scan 1.5s ease-in-out infinite'
                                                }}></div>
                                                <style>{`
                                                    @keyframes ai-scan {
                                                        0% { top: 0%; }
                                                        50% { top: 100%; }
                                                        100% { top: 0%; }
                                                    }
                                                `}</style>
                                            </>
                                        )}
                                        {wizardStep === 2 && (
                                            <div style={{ position: 'absolute', inset: 0, background: 'rgba(34,197,94,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold', fontSize: '1.2rem' }}>
                                                ✓ Registered
                                            </div>
                                        )}
                                    </div>

                                    <button
                                        onClick={handleRegisterFace}
                                        disabled={wizardStep === 1 || wizardStep === 2}
                                        style={{
                                            background: wizardStep === 2 ? '#22c55e' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                            color: 'white', border: 'none', padding: '1rem 3rem', borderRadius: '50px',
                                            fontSize: '1.1rem', fontWeight: '700', cursor: (wizardStep === 1 || wizardStep === 2) ? 'not-allowed' : 'pointer',
                                            opacity: (wizardStep === 1) ? 0.7 : 1, transition: 'all 0.2s',
                                            boxShadow: '0 10px 20px rgba(102, 126, 234, 0.3)'
                                        }}
                                    >
                                        {wizardStep === 1 ? 'Please Wait...' : wizardStep === 2 ? 'Registration Complete!' : wizardStep === 3 ? 'Retry Capture' : 'Capture & Register'}
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                )
            }

            {
                showQuotaWarning && (
                    <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', padding: '15px', background: '#667eea', color: 'white', textAlign: 'center', zIndex: 10000, fontWeight: 'bold', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
                        ⏳ Indu is taking a moment to think (AI Busy). Please wait, your answer is being saved and will process automatically...
                    </div>
                )
            }

            <div className="ai-session-container">
                <div className="ai-sidebar">
                    <div className="camera-container" style={{ position: 'relative' }}>
                        <video ref={videoRef} autoPlay playsInline muted id="candidateVideo" style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                        <canvas ref={dfCanvasRef} style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }} />
                        <div className="ai-scan-bar"></div>
                        {integrityBreach.active && <div className="integrity-overlay"><span>{integrityBreach.text}</span></div>}
                        {aiToast.active && <div className={`ai-event-toast ${aiToast.urgent ? 'urgent' : ''}`}>{aiToast.text}</div>}
                        {/* DeepFace Proctoring HUD */}
                        {dfSessionId && (
                            <div style={{
                                position: 'absolute', bottom: '4px', left: '4px', right: '4px',
                                display: 'flex', gap: '4px', justifyContent: 'center',
                                pointerEvents: 'none', zIndex: 5
                            }}>
                                <span style={{
                                    background: dfVerified === true ? 'rgba(34,197,94,0.9)' : dfVerified === false ? 'rgba(239,68,68,0.9)' : 'rgba(245,158,11,0.9)',
                                    color: '#fff', fontSize: '0.55rem', fontWeight: 700, padding: '2px 5px', borderRadius: '4px',
                                    backdropFilter: 'blur(4px)'
                                }}>
                                    {dfVerified === true ? '✓ Verified' : dfVerified === false ? '✗ Mismatch' : '— Away'}
                                </span>
                                <span style={{
                                    background: dfEngagement >= 70 ? 'rgba(34,197,94,0.9)' : dfEngagement >= 40 ? 'rgba(245,158,11,0.9)' : 'rgba(239,68,68,0.9)',
                                    color: '#fff', fontSize: '0.55rem', fontWeight: 700, padding: '2px 5px', borderRadius: '4px',
                                    backdropFilter: 'blur(4px)'
                                }}>
                                    ⚡ {Math.round(dfEngagement)}%
                                </span>
                                <span style={{
                                    background: dfHeadDir === 'FORWARD' ? 'rgba(34,197,94,0.9)' : 'rgba(245,158,11,0.9)',
                                    color: '#fff', fontSize: '0.55rem', fontWeight: 700, padding: '2px 5px', borderRadius: '4px',
                                    backdropFilter: 'blur(4px)'
                                }}>
                                    🧭 {dfHeadDir}
                                </span>
                            </div>
                        )}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flex: 1, width: '100%', gap: '1rem' }}>
                        <ReadyPlayerMeAvatar isSpeaking={isSpeaking} />

                        {/* Local Mic Visualizer */}
                        <div style={{ width: '150px', height: '30px', background: '#f8fafc', borderRadius: '8px', overflow: 'hidden', border: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '-5px' }}>
                            <canvas ref={canvasRef} width="150" height="30" style={{ width: '100%', height: '100%' }}></canvas>
                        </div>

                        {/* Status Message moved to bottom as requested */}
                        <div className="ai-status-badge" style={{ marginTop: 'auto', marginBottom: '1rem' }}>
                            <span className="speaking-indicator"></span>{aiStatus}
                        </div>
                    </div>
                </div>

                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.75rem', height: '100%' }}>
                    <div style={{ background: 'white', padding: '0.75rem 1.5rem', borderRadius: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 4px 15px rgba(0,0,0,0.05)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <i className="fa-solid fa-user-tie" style={{ color: '#667eea', fontSize: '0.9rem' }}></i>
                                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{candidateName}</span>
                            </div>

                            {timeLeft !== null && (
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    background: timeLeft < 300 ? '#fff5f5' : '#f0f4ff',
                                    padding: '4px 10px',
                                    borderRadius: '8px',
                                    color: timeLeft < 300 ? '#e53e3e' : '#667eea',
                                    fontWeight: 'bold',
                                    fontSize: '0.8rem',
                                    border: `1px solid ${timeLeft < 300 ? '#feb2b2' : '#c3dafe'}`
                                }}>
                                    <i className="fa-solid fa-clock"></i>
                                    <span>{formatTime(timeLeft)}</span>
                                </div>
                            )}

                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                background: sttReady ? (silenceCountdown ? (silenceCountdown === 'Listening...' ? '#ebf8ff' : '#fffbec') : '#f0fff4') : '#fff5f5',
                                padding: '4px 10px',
                                borderRadius: '8px',
                                color: sttReady ? (silenceCountdown ? (silenceCountdown === 'Listening...' ? '#3182ce' : '#b7791f') : '#38a169') : '#e53e3e',
                                fontWeight: 'bold',
                                fontSize: '0.8rem',
                                border: `1px solid ${sttReady ? (silenceCountdown ? (silenceCountdown === 'Listening...' ? '#bee3f8' : '#f6e05e') : '#c6f6d5') : '#feb2b2'}`
                            }}>
                                <i className={`fa-solid ${sttReady ? (silenceCountdown ? (silenceCountdown === 'Listening...' ? 'fa-microphone-lines' : 'fa-hourglass-half') : 'fa-check-circle') : 'fa-microphone-slash'}`}></i>
                                <span>{sttReady ? (silenceCountdown ? `Indu Waiting (${silenceCountdown})` : 'AssemblyAI Live') : 'Mic Offline'}</span>
                            </div>
                        </div>
                        <div className="progress-bar"><div className="progress-fill" style={{ width: `${progress}%` }}></div></div>
                        <button onClick={() => completeInterview("You have chosen to end the interview early. Thank you for your time today.")} style={{ background: 'none', border: 'none', color: '#718096', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.85rem' }}><i className="fa-solid fa-xmark"></i> Exit</button>
                    </div>

                    <div className="question-card" style={{ padding: '0.5rem 1rem', borderLeftWidth: '4px' }}>
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.6rem', textTransform: 'uppercase', color: '#667eea', fontWeight: '900', letterSpacing: '0.5px' }}>Question:</span>
                            <div style={{ fontSize: '1rem', fontWeight: 600, color: '#1a202c', flex: 1 }}>
                                {questions[currentQuestionIndex] ? (
                                    typeof questions[currentQuestionIndex] === 'object'
                                        ? (questions[currentQuestionIndex].question || JSON.stringify(questions[currentQuestionIndex]))
                                        : questions[currentQuestionIndex]
                                ) : 'Initializing...'}
                            </div>
                        </div>
                    </div>

                    <div ref={chatContainerRef} className="chat-container">
                        {chatMessages.length === 0 && <div style={{ textAlign: 'center', color: '#a0aec0', marginTop: '1.5rem', fontStyle: 'italic', fontSize: '0.85rem' }}>History will appear here...</div>}
                        {chatMessages.map((msg, i) => (
                            <div key={i} className={`message ${msg.sender}`} title={msg.timestamp}>
                                {msg.text}
                                {msg.timestamp && <span style={{ fontSize: '0.7rem', opacity: 0.6, marginTop: '2px', display: 'block' }}>{msg.timestamp}</span>}
                            </div>
                        ))}
                    </div>

                    {/* Live Transcript Display - Restored below chat */}
                    {isRecording && aiStatus.startsWith('Heard:') && (
                        <div className="live-transcript-bubble">
                            <i className="fa-solid fa-ear-listen" style={{ color: '#667eea', marginRight: '8px' }}></i>
                            {aiStatus.replace('Heard: ', '').replace(/"/g, '')}
                        </div>
                    )}

                    <div style={{ background: 'white', padding: '0.6rem 1rem', borderRadius: '12px', boxShadow: '0 -2px 10px rgba(0,0,0,0.03)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        {userInputMode === 'audio' ? (
                            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <button
                                    onClick={toggleRecording}
                                    disabled={!isFullscreen}
                                    className={`mic-btn ${isRecording ? 'listening' : ''}`}
                                    style={{ width: '40px', height: '40px', fontSize: '1rem', cursor: !isFullscreen ? 'not-allowed' : 'pointer', opacity: !isFullscreen ? 0.6 : 1 }}
                                    title={!isFullscreen ? 'Please enter fullscreen to use mic' : isProcessing ? 'Processing...' : isRecording ? 'Click to stop' : 'Click to speak'}
                                >
                                    <i className={isRecording ? "fa-solid fa-stop" : "fa-solid fa-microphone"}></i>
                                </button>
                                <span style={{ color: '#4a5568', fontWeight: 600, fontSize: '0.8rem' }}>{!isFullscreen ? 'Fullscreen required' : isRecording ? "Listening..." : "Click to Speak"}</span>
                            </div>
                        ) : (
                            <div style={{ flex: 1, display: 'flex', gap: '0.5rem', alignItems: 'flex-end', background: '#f8fafc', padding: '8px', borderRadius: '8px' }}>
                                <textarea
                                    className="response-textarea"
                                    style={{
                                        flex: 1,
                                        border: '1px solid #cbd5e0',
                                        borderRadius: '8px',
                                        padding: '8px 12px',
                                        fontSize: '0.85rem',
                                        outline: 'none',
                                        minHeight: '40px',
                                        maxHeight: '150px',
                                        resize: 'vertical',
                                        fontFamily: 'monospace'
                                    }}
                                    value={responseInput}
                                    onChange={(e) => setResponseInput(e.target.value)}
                                    placeholder="Type answer or code here... (Enter for new line)"
                                />
                                <button
                                    onClick={() => handleAnswerSubmission(responseInput)}
                                    disabled={isProcessing || !responseInput.trim()}
                                    style={{
                                        background: '#667eea',
                                        color: 'white',
                                        border: 'none',
                                        width: '40px',
                                        height: '40px',
                                        borderRadius: '8px',
                                        fontSize: '1rem',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center'
                                    }}
                                    title="Send Answer"
                                >
                                    <i className="fa-solid fa-paper-plane"></i>
                                </button>
                            </div>
                        )}
                        <button
                            onClick={() => setUserInputMode(userInputMode === 'audio' ? 'text' : 'audio')}
                            style={{ background: '#edf2f7', border: 'none', color: '#4a5568', padding: '6px 10px', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                        >
                            <i className={userInputMode === 'audio' ? "fa-solid fa-keyboard" : "fa-solid fa-microphone"}></i>
                            {userInputMode === 'audio' ? "Keys" : "Voice"}
                        </button>
                    </div>
                </div>
            </div>

            {/* Success Completion Overlay */}
            {
                isCompleted && (
                    <div className="completion-overlay">
                        <div className="completion-card">
                            <div className="completion-icon-wrap">
                                <i className="fa-solid fa-circle-check"></i>
                            </div>
                            <h2 className="completion-title">Interview Completed!</h2>
                            <p className="completion-text">
                                Thank you, <strong>{candidateName}</strong>. Your interview session has been successfully recorded and submitted for review.
                            </p>
                            <div className="completion-next-steps">
                                <p>Moving forward, our recruitment team will analyze the session and get back to you with the next steps via email.</p>
                            </div>
                        </div>
                    </div>
                )
            }
        </div >
    );
};

export default AiInterviewSession;