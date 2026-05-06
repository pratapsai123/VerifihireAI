import React, { useEffect, useRef, useState, useCallback } from 'react';

import { useParams, useNavigate, useSearchParams } from 'react-router-dom';

import axios from 'axios';

import Editor from "@monaco-editor/react";

import '../styles/Dashboard.css';

import { API_BASE_URL, DEEPFACE_BASE_URL, DEEPFACE_WS_URL } from '../apiConfig';
import { logCandidateActivity } from '../utils/activityLogger';



const AiTakeAssessment = () => {

    const { token } = useParams();

    const navigate = useNavigate();

    const [assessment, setAssessment] = useState(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState('');

    const [submitted, setSubmitted] = useState(false);

    const [isRegistered, setIsRegistered] = useState(false);

    const [registrationSnapshot, setRegistrationSnapshot] = useState(null);

    const [isRegistering, setIsRegistering] = useState(false);

    const [isSubmitting, setIsSubmitting] = useState(false);

    const [isCheckingRegistration, setIsCheckingRegistration] = useState(true);

    const [answers, setAnswers] = useState({});







    // Intake

    const [candidateName, setCandidateName] = useState('');

    const [candidateEmail, setCandidateEmail] = useState('');

    const [isAutoFilled, setIsAutoFilled] = useState(false);

    const [submissionId, setSubmissionId] = useState(null);

    // PAN Authentication fields
    const [phone, setPhone] = useState('');
    const [panNumber, setPanNumber] = useState('');
    const [panPhoto, setPanPhoto] = useState(null);
    const [panPhotoPreview, setPanPhotoPreview] = useState(null);
    const [panValidating, setPanValidating] = useState(false);
    const [panVerified, setPanVerified] = useState(false);
    const [panError, setPanError] = useState('');
    const [formError, setFormError] = useState('');

    const [timeLeft, setTimeLeft] = useState(null);

    const [isStarted, setIsStarted] = useState(false);



    // Navigator state

    const [answeredQs, setAnsweredQs] = useState(new Set());

    const [markedQs, setMarkedQs] = useState(new Set());

    const [visitedQs, setVisitedQs] = useState(new Set([0]));

    const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);



    // Monitoring

    const [aiToast, setAiToast] = useState({ active: false, text: '', urgent: false });

    const [isFullscreen, setIsFullscreen] = useState(false);



    // IDE

    const [codeOutput, setCodeOutput] = useState([]);

    const [isExecuting, setIsExecuting] = useState(false);

    const [selectedLanguage, _setSelectedLanguage] = useState('python');

    const [codeDrafts, setCodeDrafts] = useState({});



    const DEFAULT_BOILERPLATES = {

        python: 'import sys\n\ndef main():\n    # Write your code here\n    pass\n\nif __name__ == "__main__":\n    main()\n',

        java: 'import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Write your code here\n    }\n}\n',

        cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your code here\n    return 0;\n}\n',

        javascript: 'const fs = require("fs");\n\nfunction main() {\n    // Read input from stdin\n    // const input = fs.readFileSync(0, "utf8");\n    \n    // Write your code here\n}\n\nmain();\n',

        sql: '-- SQLite\n-- Create tables and insert data if needed\n-- SELECT * FROM ...\n',

        csharp: 'using System;\n\nclass Program {\n    static void Main() {\n        // Write your code here\n    }\n}\n',

        kotlin: 'import java.util.Scanner\n\nfun main() {\n    val sc = Scanner(System.`in`)\n    // Write your code here\n}\n',

        swift: 'import Foundation\n\nfunc main() {\n    // Write your code here\n}\n\nmain()\n'

    };



    const formatCode = (codeStr) => {

        if (!codeStr || typeof codeStr !== 'string') return codeStr;

        // AI models often escape newlines when generating JSON, producing literal "\\n" and "\\t". 

        // We need to convert them to actual newlines for the code editor.

        return codeStr.replace(/\\n/g, '\n')

            .replace(/\\t/g, '\t')

            .replace(/\\"/g, '"')

            .replace(/\\\\n/g, '\n') // Handle double escaped

            .replace(/\\\\"/g, '"');

    };



    const setSelectedLanguage = (lang) => {

        const currentLang = selectedLanguage;

        const qKey = currentAnswerKey;



        if (qKey && qKey.startsWith('coding_')) {

            const currentCode = answers[qKey] || '';

            const draftKeyForOldLang = `${qKey}_${currentLang}`;

            const nextDraftKey = `${qKey}_${lang}`;

            let nextCode = codeDrafts[nextDraftKey];



            if (nextCode === undefined) {

                const qIdx = parseInt(qKey.replace('coding_', ''), 10);

                const q = assessment?.generated_content?.coding_challenges?.[qIdx];

                if (q) {

                    if (q.starter_code && typeof q.starter_code === 'object') {

                        // Case-insensitive lookup

                        const foundKey = Object.keys(q.starter_code).find(k => k.toLowerCase() === lang.toLowerCase());

                        if (foundKey) nextCode = formatCode(q.starter_code[foundKey]);

                    }



                    if (nextCode === undefined && q[`starter_code_${lang}`]) {

                        nextCode = formatCode(q[`starter_code_${lang}`]);

                    }

                }



                if (nextCode === undefined) {

                    nextCode = DEFAULT_BOILERPLATES[lang] || '# Write logic here\n';

                }

            }



            setAnswers(prev => ({ ...prev, [qKey]: nextCode }));

            setCodeDrafts(prev => ({

                ...prev,

                [draftKeyForOldLang]: currentCode,

                [nextDraftKey]: nextCode

            }));

        }



        _setSelectedLanguage(lang);

    };

    const [customInput, setCustomInput] = useState('');

    const [executionResult, setExecutionResult] = useState(null);

    const [coding_results, setCodingResults] = useState({}); // { qId: { passed, total } }



    const supportedLanguages = [

        { id: 'javascript', name: 'JavaScript', version: '18.15.0' },

        { id: 'python', name: 'Python', version: '3.10.0' },

        { id: 'cpp', name: 'C++', version: '10.2.0' },

        { id: 'java', name: 'Java', version: '15.0.2' },

        { id: 'sql', name: 'SQL (SQLite)', version: '3.42.0' },

        { id: 'csharp', name: 'C#', version: '8.0' },

        { id: 'kotlin', name: 'Kotlin', version: '1.9.23' },

        { id: 'swift', name: 'Swift', version: '5.10' }

    ];



    const formatText = (text) => {

        if (!text) return '';

        // If it looks like HTML (contains tags), return it raw to let dangerouslySetInnerHTML handle it

        if (/<[a-z][\s\S]*>/i.test(text)) {

            return text;

        }

        return text.replace(/\n/g, '<br />');

    };



    const videoRef = useRef(null);

    const streamRef = useRef(null);

    const lastCaptureTimeRef = useRef(0); // For throttling tab_switch/window_blur

    const screenStreamRef = useRef(null);

    const screenCanvasRef = useRef(null);

    const timerRef = useRef(null);

    const handleSubmitRef = useRef(null); // always points to latest handleSubmit



    // ══════════════════════════════════════

    // DEEPFACE STATE & REFS

    // ══════════════════════════════════════

    const [dfSessionId, setDfSessionId] = useState(null);



    const [dfFacePresent, setDfFacePresent] = useState(false);

    const [dfFaceCount, setDfFaceCount] = useState(0);

    const [dfEngagement, setDfEngagement] = useState(0);

    const [dfVerified, setDfVerified] = useState(null);

    const [dfHeadDir, setDfHeadDir] = useState('FORWARD');

    const [dfFps, setDfFps] = useState(0);

    const [isDeepfaceActive, setIsDeepfaceActive] = useState(false);



    const getDeepfacePersonId = useCallback(() => {

        return String((candidateEmail || token || '')).trim().toLowerCase();

    }, [candidateEmail, token]);



    const checkDeepfaceRegistration = useCallback(async () => {

        const personId = getDeepfacePersonId();

        if (!personId) return false;

        try {

            const res = await axios.get(`${DEEPFACE_BASE_URL}/registration/registered/${encodeURIComponent(personId)}`);

            return res?.data?.registered === true;

        } catch (e) {

            return false;

        }

    }, [DEEPFACE_BASE_URL, getDeepfacePersonId]);



    const dfWsRef = useRef(null);

    const dfSessionIdRef = useRef(null);

    const dfCanvasRef = useRef(null);

    const dfAwaitingRef = useRef(false);

    const dfSendIntervalRef = useRef(null);

    const dfLastUiUpdateRef = useRef(0);

    const dfFpsRef = useRef({ count: 0, last: Date.now() });



    // ══════════════════════════════════════

    // INTEGRITY & VIOLATION LOGGING

    // ══════════════════════════════════════

    const reportViolation = useCallback(async (eventType, screenshot = null, webcamScreenshot = null) => {

        if (!submissionId) return;

        try {

            await axios.post(`${API_BASE_URL}/ai/submission/${submissionId}/integrity/`, {

                event_type: eventType,

                screenshot: screenshot,

                webcam_screenshot: webcamScreenshot

            });

        } catch { }

    }, [submissionId]);



    const showAiEvent = useCallback(async (text, urgent = false, eventType = null) => {

        setAiToast({ active: true, text, urgent });



        let screenshot = null;

        let webcamScreenshot = null;



        if (eventType) {

            const isScreenEvent = ['tab_switch', 'window_blur', 'window_switch'].includes(eventType);

            if (isScreenEvent) {

                const now = Date.now();

                if (now - lastCaptureTimeRef.current < 2000) return;

                lastCaptureTimeRef.current = now;

            }



            if (isScreenEvent && screenStreamRef.current && screenCanvasRef.current) {

                try {

                    const video = document.createElement('video');

                    video.srcObject = screenStreamRef.current;

                    video.muted = true;

                    video.playsInline = true;



                    await new Promise((resolve) => {

                        let resolved = false;

                        const fallback = setTimeout(() => { if (!resolved) { resolved = true; resolve(); } }, 300);

                        video.onloadedmetadata = () => {

                            video.play().then(() => {

                                if (!resolved) { resolved = true; clearTimeout(fallback); setTimeout(resolve, 50); }

                            }).catch(() => { if (!resolved) { resolved = true; clearTimeout(fallback); resolve(); } });

                        };

                        video.onerror = () => { if (!resolved) { resolved = true; clearTimeout(fallback); resolve(); } };

                    });



                    const canvas = screenCanvasRef.current;

                    const ctx = canvas.getContext('2d');

                    canvas.width = video.videoWidth || window.innerWidth || 1280;

                    canvas.height = video.videoHeight || window.innerHeight || 720;

                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);



                    // Burn label into snapshot

                    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';

                    ctx.fillRect(0, canvas.height - 40, canvas.width, 40);

                    ctx.fillStyle = urgent ? '#ef4444' : '#f59e0b';

                    ctx.font = 'bold 16px Poppins, Arial';

                    ctx.textAlign = 'center';

                    ctx.fillText(`AI ALERT: ${text}`, canvas.width / 2, canvas.height - 15);



                    screenshot = canvas.toDataURL('image/jpeg', 0.5);

                    video.pause();

                    video.srcObject = null;

                } catch (e) {

                    console.error('Failed to capture AI integrity snapshot', e);

                }

            }



            if (['multiface_detection', 'phone_detection', 'no_face_detection', 'face_detection_lost', 'face_detection_lost_rechecked', 'face_mismatch', 'looking_away'].includes(eventType) && videoRef.current && videoRef.current.readyState >= 2) {

                try {

                    const camCanvas = document.createElement('canvas');

                    camCanvas.width = videoRef.current.videoWidth || 640;

                    camCanvas.height = videoRef.current.videoHeight || 480;

                    const ctx = camCanvas.getContext('2d');

                    ctx.drawImage(videoRef.current, 0, 0, camCanvas.width, camCanvas.height);



                    // Burn label into webcam snapshot

                    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';

                    ctx.fillRect(0, camCanvas.height - 30, camCanvas.width, 30);

                    ctx.fillStyle = urgent ? '#ef4444' : '#f59e0b';

                    ctx.font = 'bold 14px Poppins, Arial';

                    ctx.textAlign = 'center';

                    ctx.fillText(`${text}`, camCanvas.width / 2, camCanvas.height - 10);



                    webcamScreenshot = camCanvas.toDataURL('image/jpeg', 0.5);

                } catch (e) {

                    console.error('Failed to capture AI webcam snapshot', e);

                }

            }



            reportViolation(eventType, screenshot, webcamScreenshot);

        }



        setTimeout(() => setAiToast({ active: false, text: '', urgent: false }), 3000);

    }, [reportViolation]);



    // ══════════════════════════════════════

    // DEEPFACE PROCTORING LOGIC

    // ══════════════════════════════════════

    const sendDeepfaceFrame = useCallback(() => {

        if (!dfWsRef.current || dfWsRef.current.readyState !== WebSocket.OPEN) return;

        if (!videoRef.current || !videoRef.current.videoWidth) return;

        if (dfAwaitingRef.current) return;



        const canvas = document.createElement('canvas');

        canvas.width = 640;

        canvas.height = 480;

        const ctx = canvas.getContext('2d');

        // Apply brightness and contrast enhancement before sending to backend (matches app.js:466)

        ctx.filter = 'brightness(1.15) contrast(1.2)';

        ctx.drawImage(videoRef.current, 0, 0, 640, 480);

        ctx.filter = 'none';



        const dataUrl = canvas.toDataURL('image/jpeg', 0.75);

        const b64 = dataUrl.split(',')[1];

        dfAwaitingRef.current = true;

        dfWsRef.current.send(JSON.stringify({ frame: b64 }));



        // FPS Tracking

        const f = dfFpsRef.current;

        f.count++;

        const now = Date.now();

        if (now - f.last > 1000) {

            setDfFps(f.count);

            f.count = 0;

            f.last = now;

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



        // Mirror for HUD

        ctx.save();

        ctx.translate(vw, 0);

        ctx.scale(-1, 1);



        if (Array.isArray(result.face_boxes)) {

            const isVerified = result.verification?.verified === true;

            result.face_boxes.forEach((box, idx) => {

                if (!box) return;

                const x = (box.x || box.xmin || 0) * scaleX;

                const y = (box.y || box.ymin || 0) * scaleY;

                const w = (box.width || 0) * scaleX;

                const h = (box.height || 0) * scaleY;

                if (w < 5 || h < 5) return; // Adjusted for tiny feed



                let color = idx === 0 ? (isVerified ? '#22c55e' : '#ef4444') : '#f59e0b';

                let label = idx === 0 ? (isVerified ? 'VERIFIED' : 'UNAUTHORIZED') : 'SUSPECT';



                ctx.strokeStyle = color;

                ctx.lineWidth = 2.5; // Slightly thicker for small feed visibility

                ctx.strokeRect(x, y, w, h);



                // Brackets

                const bLen = Math.min(w, h) * 0.25;

                ctx.beginPath(); ctx.moveTo(x, y + bLen); ctx.lineTo(x, y); ctx.lineTo(x + bLen, y); ctx.stroke();

                ctx.beginPath(); ctx.moveTo(x + w - bLen, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + bLen); ctx.stroke();

                ctx.beginPath(); ctx.moveTo(x, y + h - bLen); ctx.lineTo(x, y + h); ctx.lineTo(x + bLen, y + h); ctx.stroke();

                ctx.beginPath(); ctx.moveTo(x + w - bLen, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - bLen); ctx.stroke();



            });

        }

        ctx.restore();

    }, []);



    const handleDeepfaceResult = useCallback((result) => {

        drawDeepfaceOverlay(result);

        const now = Date.now();

        if (now - dfLastUiUpdateRef.current > 500) {

            dfLastUiUpdateRef.current = now;

            setDfFacePresent(result.face_present ?? false);

            setDfFaceCount(result.face_count ?? 0);

            setDfEngagement(result.engagement_score ?? 0);

            if (result.verification) setDfVerified(result.verification.verified);

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



        if (result.alerts && result.alerts.length > 0) {

            result.alerts.forEach(a => {

                let eventType = a.type;

                if (a.type === 'verification_failed' || a.type === 'verification_failed_not_matched') eventType = 'face_mismatch';

                if (a.type === 'no_face') eventType = 'no_face_detection';

                if (a.type === 'multiple_faces') eventType = 'multiface_detection';

                if (a.type === 'head_yaw_exceeded' || a.type === 'head_pitch_exceeded' || a.type === 'looking_away_detected') eventType = 'looking_away';



                // Alert throttling: don't spam the same event type every frame

                showAiEvent(a.message.toUpperCase(), a.severity === 'HIGH' || a.severity === 'CRITICAL', eventType);

            });

        }

        dfAwaitingRef.current = false;

    }, [drawDeepfaceOverlay, showAiEvent]);



    const startDeepfaceMonitoring = useCallback(async (candidateId) => {

        const normalizedEmail = String(candidateId).trim().toLowerCase();

        try {

            const res = await axios.post(`${DEEPFACE_BASE_URL}/session/start`, {

                person_id: normalizedEmail

            });

            const sessionId = res.data.session_id;

            setDfSessionId(sessionId);

            dfSessionIdRef.current = sessionId;



            const wsUrl = `${DEEPFACE_WS_URL}/ws/monitor/${sessionId}`;

            const wsReady = await new Promise((resolve) => {

                const ws = new WebSocket(wsUrl);

                dfWsRef.current = ws;



                const openTimeout = setTimeout(() => {

                    try { ws.close(); } catch (e) { }

                    resolve(false);

                }, 7000);



                ws.onopen = () => {

                    clearTimeout(openTimeout);

                    console.log('DeepFace WS connected for assessment:', sessionId);

                    dfAwaitingRef.current = false;

                    setIsDeepfaceActive(true);

                    // Production-safe cadence (~5 FPS). This matches DeepFace guidance and prevents CPU/network overload.

                    dfSendIntervalRef.current = setInterval(sendDeepfaceFrame, 200);

                    resolve(true);

                };

                ws.onmessage = (e) => handleDeepfaceResult(JSON.parse(e.data));

                ws.onclose = () => {

                    clearTimeout(openTimeout);

                    clearInterval(dfSendIntervalRef.current);

                    setIsDeepfaceActive(false);

                };

                ws.onerror = () => {

                    clearTimeout(openTimeout);

                    resolve(false);

                };

            });

            return wsReady;

        } catch (e) {

            console.error('DeepFace Init Failed:', e);

            if (e?.response?.status === 403) {

                // DeepFace backend says not registered.

                setIsRegistered(false);

            }

            setIsDeepfaceActive(false);

            return false;

        }

    }, [sendDeepfaceFrame, handleDeepfaceResult]);



    const stopDeepfaceMonitoring = useCallback(async () => {

        if (dfWsRef.current) dfWsRef.current.close();

        if (dfSendIntervalRef.current) clearInterval(dfSendIntervalRef.current);

        setIsDeepfaceActive(false);



        // Finalize session on backend

        if (dfSessionIdRef.current) {

            try {

                await axios.post(`${DEEPFACE_BASE_URL}/session/${dfSessionIdRef.current}/end`);

            } catch (e) {

                console.error("Failed to end DeepFace session:", e);

            }

        }

    }, []);

    const mcqSection = React.useMemo(() => {

        const raw = assessment?.generated_content?.mcqs;

        return Array.isArray(raw) ? raw : [];

    }, [assessment]);

    const codingSection = React.useMemo(() => {

        const raw = assessment?.generated_content?.coding_challenges;

        return Array.isArray(raw) ? raw : [];

    }, [assessment]);

    const allQs = React.useMemo(() => [

        ...mcqSection.map((q, i) => ({ ...q, type: 'mcq', id: i })),

        ...codingSection.map((c, i) => ({ ...c, type: 'coding', id: i }))

    ], [mcqSection, codingSection]);



    const currentQ = allQs[currentQuestionIdx] || allQs[0];

    const currentAnswerKey = currentQ?.type === 'mcq' ? `mcq_${currentQ?.id}` : `coding_${currentQ?.id}`;

    const isLastQ = currentQuestionIdx === allQs.length - 1;



    const [searchParams] = useSearchParams();

    useEffect(() => {
        const nameParam = searchParams.get('name');
        const emailParam = searchParams.get('email');

        console.log('URL Params from useSearchParams:', { nameParam, emailParam });

        const isNameValid = nameParam && nameParam !== 'Extraction Failed' && nameParam.trim() !== '';
        const isEmailValid = emailParam && emailParam !== 'Extraction Failed' && emailParam.trim() !== '';

        console.log('Validation:', { isNameValid, isEmailValid });

        if (isNameValid || isEmailValid) {
            if (isNameValid) setCandidateName(decodeURIComponent(nameParam));
            if (isEmailValid) setCandidateEmail(decodeURIComponent(emailParam));
            // Only lock inputs if we have a valid email to track them with
            if (isEmailValid) setIsAutoFilled(true);
        }
    }, [searchParams]);



    useEffect(() => {

        const fetchAssessment = async () => {

            try {

                // Check if already completed via local storage first for instant blocking

                if (localStorage.getItem(`assessment_completed_${token}`)) {

                    setError('You have already completed this assessment and cannot retake it.');

                    setLoading(false);

                    return;

                }



                const params = new URLSearchParams(window.location.search);

                const emailParam = params.get('email');

                // Cache-busting nonce _t ensures we never get a "stale" in-progress response

                const url = emailParam

                    ? `${API_BASE_URL}/ai/public/${token}/?email=${encodeURIComponent(emailParam)}&_t=${Date.now()}`

                    : `${API_BASE_URL}/ai/public/${token}/?_t=${Date.now()}`;

                const response = await axios.get(url);

                const data = response.data;

                setAssessment(data);



                // Availability Window Check

                const now = new Date();

                const from = data.available_from ? new Date(data.available_from) : null;

                const until = data.available_until ? new Date(data.available_until) : null;



                if (data.already_completed) {

                    setError('You have already completed this assessment and cannot retake it.');

                } else if (from && now < from) {

                    setError(`This assessment will be available starting ${from.toLocaleString()}.`);

                } else if (until && now > until) {

                    setError(`This assessment link has expired. It was available until ${until.toLocaleString()}.`);

                }



                setLoading(false);

            } catch (err) {

                setError('Invalid or expired assessment link.');

                setLoading(false);

            }

        };

        fetchAssessment();

    }, [token, candidateEmail]);



    useEffect(() => {

        // Always require fresh face registration - do not check if already registered

        if (candidateEmail && DEEPFACE_BASE_URL) {

            setIsCheckingRegistration(false);

        }

    }, [candidateEmail, DEEPFACE_BASE_URL]);



    const handleAnswerChange = (key, val) => {

        setAnswers(prev => ({ ...prev, [key]: val }));



        // Also update draft if this is a coding question

        if (key.startsWith('coding_')) {

            setCodeDrafts(prev => ({ ...prev, [`${key}_${selectedLanguage}`]: val }));

        }



        setAnsweredQs(prev => new Set([...prev, currentQuestionIdx]));

    };

    // PAN Authentication handlers
    const validatePanFormat = (pan) => {
        const panPattern = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
        return panPattern.test(pan.toUpperCase().trim());
    };

    const handlePanPhotoChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Check file size (2.5MB limit)
            if (file.size > 2.5 * 1024 * 1024) {
                setPanError('File size exceeds 2.5MB limit');
                return;
            }
            
            // Check file type
            const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
            const validExtensions = ['.jpg', '.jpeg', '.png', '.pdf'];
            const isValidType = validTypes.includes(file.type) || 
                               validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
            
            if (!isValidType) {
                setPanError('Please upload a valid image (JPG, PNG) or PDF file');
                return;
            }
            
            setPanPhoto(file);
            // For PDFs, don't create preview
            if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
                setPanPhotoPreview(null);
            } else {
                setPanPhotoPreview(URL.createObjectURL(file));
            }
            setPanVerified(false);
            setPanError('');
        }
    };

    const handleValidatePan = async () => {
        const pan = panNumber.toUpperCase().trim();

        if (!validatePanFormat(pan)) {
            setPanError('Invalid PAN format. Expected: ABCDE1234F (5 letters + 4 digits + 1 letter)');
            return;
        }
        if (!panPhoto) {
            setPanError('Please upload your PAN card photo first');
            return;
        }

        setPanValidating(true);
        setPanError('');

        try {
            const formPayload = new FormData();
            formPayload.append('pan_photo', panPhoto);
            formPayload.append('pan_number', pan);
            // Send email for identity fraud detection
            if (candidateEmail) {
                formPayload.append('email', candidateEmail);
            }

            const res = await axios.post(`${API_BASE_URL}/ai-candidates/validate-pan/`, formPayload, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (res.data.is_verified) {
                setPanVerified(true);
                setPanError('');
            } else {
                setPanVerified(false);
                setPanError(res.data.message || 'PAN mismatch. The PAN number on your card does not match the entered number.');
            }
        } catch (err) {
            const msg = err.response?.data?.error || err.response?.data?.message || 'Validation failed. Please try again.';
            setPanError(msg);
            setPanVerified(false);
        } finally {
            setPanValidating(false);
        }
    };



    const startAssessment = async (bypassReg = false) => {

        if (!candidateName || !candidateEmail) { alert('Please provide your name and email.'); return; }

        // PAN Authentication validation
        if (!phone.trim()) {
            setFormError('Phone number is required');
            return;
        }
        if (!panNumber.trim()) {
            setFormError('PAN card number is required');
            return;
        }
        if (!validatePanFormat(panNumber)) {
            setFormError('Invalid PAN format. Expected: ABCDE1234F');
            return;
        }
        if (!panPhoto) {
            setFormError('Please upload your PAN card photo');
            return;
        }
        if (!panVerified) {
            setFormError('Please verify your PAN card before proceeding');
            return;
        }

        const personId = getDeepfacePersonId();

        if (!personId) { alert('Invalid candidate identity for DeepFace registration.'); return; }



        // DeepFace Requirement: Ensure face is registered first

        if (!bypassReg && !isRegistered) {

            setIsRegistering(true);

            return;

        }



        try {

            const formPayload = new FormData();
            formPayload.append('share_token', token);
            formPayload.append('candidate_name', candidateName);
            formPayload.append('candidate_email', candidateEmail);
            formPayload.append('phone', phone);
            formPayload.append('pan_number', panNumber);
            formPayload.append('pan_verified', panVerified);
            if (panPhoto) {
                formPayload.append('pan_photo', panPhoto);
            }
            if (registrationSnapshot) {
                formPayload.append('snapshot', registrationSnapshot);
            }

            const res = await axios.post(`${API_BASE_URL}/ai/submit/create/`, formPayload, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const { submission_id, time_left, answers: savedAnswers, current_question_index, coding_results: savedResults, codeDrafts: savedDrafts, candidate_questions } = res.data;



            setSubmissionId(submission_id);

            if (savedResults) setCodingResults(savedResults);

            if (savedDrafts) setCodeDrafts(savedDrafts);



            if (candidate_questions) {

                setAssessment(prev => ({ ...prev, generated_content: candidate_questions }));

            }



            setTimeLeft(time_left !== undefined ? time_left : assessment.duration_minutes * 60);



            // Restore session

            if (savedAnswers && Object.keys(savedAnswers).length > 0) {

                setAnswers(savedAnswers);

                const mcqsArr = assessment?.generated_content?.mcqs || [];

                const totalMcqs = mcqsArr.length;

                const restoredAnswered = new Set();

                const restoredVisited = new Set();

                Object.keys(savedAnswers).forEach(key => {

                    const val = savedAnswers[key];

                    if (!val) return;

                    let globalIdx = null;

                    if (key.startsWith('mcq_')) {

                        const i = parseInt(key.replace('mcq_', ''), 10);

                        if (!isNaN(i)) globalIdx = i;

                    } else if (key.startsWith('coding_')) {

                        const i = parseInt(key.replace('coding_', ''), 10);

                        if (!isNaN(i)) globalIdx = totalMcqs + i;

                    }

                    if (globalIdx !== null) {

                        restoredAnswered.add(globalIdx);

                        restoredVisited.add(globalIdx);

                    }

                });

                if (restoredAnswered.size > 0) {

                    setAnsweredQs(restoredAnswered);

                    setVisitedQs(prev => new Set([...prev, ...restoredVisited]));

                }

            }



            if (current_question_index !== undefined) {

                setCurrentQuestionIdx(current_question_index);

                setVisitedQs(prev => new Set([...prev, current_question_index]));

            }



            // Start Proctoring (Replacement for old monitor)

            await startScreenShare();



            try {

                if (document.documentElement.requestFullscreen) {

                    await document.documentElement.requestFullscreen();

                    setIsFullscreen(true);

                }

            } catch (err) { }



            // Set started state - camera and DeepFace will be initialized in useEffect

            // after the video element is rendered

            setIsStarted(true);
            logCandidateActivity(token, 'AI Assessment Started', 'Candidate started the AI-proctored assessment.');



        } catch (err) {

            const msg = err.response?.data?.error || 'Failed to start assessment.';

            alert(msg);

            if (msg.includes('already completed')) {

                navigate('/');

            }

        }

    };



    const startScreenShare = async () => {

        try {

            const stream = await navigator.mediaDevices.getDisplayMedia({

                video: { displaySurface: 'monitor' },

                audio: false

            });

            const track = stream.getVideoTracks()[0];

            if (track.getSettings().displaySurface !== 'monitor') {

                track.stop();

                alert('Please share your "Entire Screen" to proceed. Tab/Window sharing is prohibited.');

                return false;

            }

            screenStreamRef.current = stream;

            track.onended = () => {

                showAiEvent('SCREEN SHARING STOPPED', true, 'tab_switch');

                setIsStarted(false); // End session or force re-auth

                setIsRegistered(false); // Require fresh face registration before restarting

            };

            return true;

        } catch (err) {

            // alert('Screen sharing (Entire Screen) is required to start the test.');

            return false;

        }

    };



    const runCode = async (qId, isTestRun = false) => {

        setIsExecuting(true);

        setExecutionResult(null);

        const code = answers[`coding_${qId}`];

        if (!code) { alert('Please write some code first!'); setIsExecuting(false); return; }

        // qId is the per-type index (0,1,...) — AI generated challenges have no .id field, use index directly

        const currentQ = assessment?.generated_content?.coding_challenges?.[qId];

        const langData = supportedLanguages.find(l => l.id === selectedLanguage);



        if (isTestRun && currentQ?.test_cases?.length > 0) {

            try {

                const results = await Promise.all((currentQ.test_cases || []).map(async (tc, index) => {

                    const rawInput = tc.input || tc.input_data || tc.stdin || '';

                    // Coerce to string — AI test cases may have input as a JSON object

                    const tcInput = (typeof rawInput === 'string') ? rawInput : JSON.stringify(rawInput);

                    const tcOutput = tc.output || tc.expected_output || tc.stdout || '';

                    const isHidden = index >= 2;



                    try {

                        const r = await axios.post(`${API_BASE_URL}/ai/execute/`, {

                            language: selectedLanguage,

                            version: langData.version,

                            files: [{ content: code }],

                            stdin: tcInput

                        });

                        const out = String(r.data.run.stdout || r.data.run.stderr || '').trim();

                        const exp = String(tcOutput).trim();



                        // Robust comparison: check for exact match OR normalized match

                        const normalize = (s) => s.replace(/\s+/g, '').replace(/'/g, '"').toLowerCase();

                        let passed = out === exp || normalize(out) === normalize(exp);



                        // Further fallback: if it looks like a JSON wrap issue (e.g. expected {'result': ...} but got ...)

                        if (!passed && normalize(exp).includes(normalize(out))) {

                            passed = true; // Partial match if the core data is present

                        }



                        return {

                            input: tcInput,

                            expected: exp,

                            actual: out,

                            passed,

                            isHidden

                        };

                    } catch (err) {

                        return {

                            input: tcInput,

                            expected: tcOutput,

                            actual: 'Error: ' + (err.message || 'Unknown'),

                            passed: false,

                            isHidden

                        };

                    }

                }));



                const passedCount = results.filter(r => r.passed).length;

                setExecutionResult({

                    type: 'test_cases',

                    results,

                    score: passedCount,

                    total: results.length

                });

                setCodingResults(prev => ({

                    ...prev,

                    [qId]: { passed: passedCount, total: results.length }

                }));

            } catch (err) {

                console.error("Test execution failed", err);

                setCodeOutput(prev => [...prev, { type: 'error', content: 'Internal test execution error.' }]);

            }

            setIsExecuting(false);

            return;

        }



        // If Submit Code but NO test cases available — show message and fall through to plain run

        if (isTestRun && (!currentQ?.test_cases || currentQ.test_cases.length === 0)) {

            setCodeOutput([{ type: 'info', content: '⚠️ No hidden test cases found for this question. Running your code with custom input instead...' }]);

        }



        setCodeOutput([{ type: 'info', content: `Running ${selectedLanguage}...` }]);

        try {

            const r = await axios.post(`${API_BASE_URL}/ai/execute/`, {

                language: selectedLanguage, version: langData.version,

                files: [{ content: code }], stdin: customInput

            });

            const { run } = r.data;

            const logs = [];

            if (run.stdout) logs.push({ type: 'log', content: run.stdout });

            if (run.stderr) logs.push({ type: 'error', content: run.stderr });

            const isSuccess = run.code === 0 && !run.stderr;

            logs.push({

                type: isSuccess ? 'success' : 'error',

                content: isSuccess ? '✅ Execution Successful' : `❌ Execution Failed (Exit code: ${run.code})`

            });

            setCodeOutput(logs);

        } catch { setCodeOutput([{ type: 'error', content: 'Connection error.' }]); }

        finally { setIsExecuting(false); }

    };



    const handleRestoreCode = () => {

        if (!currentAnswerKey || !currentAnswerKey.startsWith('coding_')) return;

        const qIdx = parseInt(currentAnswerKey.replace('coding_', ''), 10);

        const q = assessment?.generated_content?.coding_challenges?.[qIdx];



        let restoredCode = '';

        if (q?.starter_code && typeof q.starter_code === 'object') {

            const foundKey = Object.keys(q.starter_code).find(k => k.toLowerCase() === selectedLanguage.toLowerCase());

            if (foundKey) restoredCode = formatCode(q.starter_code[foundKey]);

        }



        if (!restoredCode && q && q[`starter_code_${selectedLanguage}`]) {

            restoredCode = formatCode(q[`starter_code_${selectedLanguage}`]);

        }



        if (!restoredCode) {

            restoredCode = DEFAULT_BOILERPLATES[selectedLanguage] || '# Write logic here\n';

        }



        if (window.confirm("Restore predefined code? This will clear your current progress for this language.")) {

            handleAnswerChange(currentAnswerKey, restoredCode);

        }

    };



    const startCamera = async () => {

        try {

            const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });

            if (videoRef.current) { videoRef.current.srcObject = stream; videoRef.current.play().catch(() => { }); }

            streamRef.current = stream;

        } catch { setAiToast({ active: true, text: 'Camera Denied', urgent: true }); }

    };



    const stopCamera = () => {

        if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }

    };







    // Initialize camera and DeepFace when assessment starts

    useEffect(() => {

        if (!isStarted || !submissionId) return;



        const initMonitoring = async () => {

            const personId = getDeepfacePersonId();

            if (!personId) return;

            

            // Start camera first (gives video element time to mount)

            await startCamera();

            

            // Small delay to ensure video element is ready

            await new Promise(r => setTimeout(r, 500));

            

            // Start DeepFace monitoring

            const deepfaceOk = await startDeepfaceMonitoring(personId);

            if (!deepfaceOk) {

                // DeepFace failed - show registration wizard

                stopCamera();

                if (screenStreamRef.current) {

                    screenStreamRef.current.getTracks().forEach(t => t.stop());

                    screenStreamRef.current = null;

                }

                setIsRegistering(true);

                setIsStarted(false); // Reset started state

            }

        };

        

        initMonitoring();



        const onHide = () => { if (document.hidden) showAiEvent('TAB SWITCHED', true, 'tab_switch'); };

        const onBlur = () => showAiEvent('WINDOW BLURRED', true, 'window_switch');

        const onFullscreenChange = () => {

            const isNowFullscreen = !!document.fullscreenElement;

            setIsFullscreen(isNowFullscreen);

            if (!isNowFullscreen && isStarted && !submitted) {

                showAiEvent('FULLSCREEN EXITED', true, 'fullscreen_exit');

            }

        };



        document.addEventListener('visibilitychange', onHide);

        window.addEventListener('blur', onBlur);

        document.addEventListener('fullscreenchange', onFullscreenChange);



        return () => {

            document.removeEventListener('visibilitychange', onHide);

            window.removeEventListener('blur', onBlur);

            document.removeEventListener('fullscreenchange', onFullscreenChange);

            stopDeepfaceMonitoring();

            stopCamera();

        };

    }, [isStarted, submissionId, showAiEvent, submitted, stopDeepfaceMonitoring, getDeepfacePersonId, startDeepfaceMonitoring]);



    // Continuous background tracking for "Tab 1 -> Tab 2" and "Window 1 -> Window 2" switches

    useEffect(() => {

        if (!isStarted || !submissionId || submitted) return;



        const bgInterval = setInterval(() => {

            // If candidate is actively looking at our tab, do nothing

            if (!document.hidden && document.hasFocus()) return;



            // If they are hidden (different tab) or blurred (different window), capture every 5s

            const eventType = document.hidden ? 'tab_switch' : 'window_switch';

            showAiEvent('BACKGROUND ACTIVITY DETECTED', true, eventType);

        }, 5000);



        return () => clearInterval(bgInterval);

    }, [showAiEvent, isStarted, submissionId, submitted]);



    // Save progress periodically (debounced)

    // Also exposes saveProgress via ref so beforeunload can call it synchronously

    const saveProgressRef = useRef(null);

    useEffect(() => {

        if (!isStarted || !submissionId || submitted) return;



        const saveProgress = async () => {

            try {

                await axios.post(`${API_BASE_URL}/ai/submission/${submissionId}/progress/`, {

                    answers,

                    current_question_index: currentQuestionIdx,

                    coding_results,

                    codeDrafts: codeDrafts

                });

            } catch (err) {

                console.error("Failed to save progress", err);

            }

        };



        // Store reference so unload handler can call it

        saveProgressRef.current = { answers, currentQuestionIdx, submissionId, coding_results };



        const timer = setTimeout(saveProgress, 1000); // 1-second debounce (reduced from 3s)

        return () => clearTimeout(timer);

    }, [answers, currentQuestionIdx, isStarted, submissionId, submitted]);



    // Save progress immediately when user leaves the page (close tab, navigate away)

    useEffect(() => {

        if (!isStarted || !submissionId) return;



        const handleBeforeUnload = () => {

            const ctx = saveProgressRef.current;

            if (!ctx) return;

            // navigator.sendBeacon works even when the page is unloading

            const payload = JSON.stringify({

                answers: ctx.answers,

                current_question_index: ctx.currentQuestionIdx,

                coding_results: ctx.coding_results,

                codeDrafts: ctx.codeDrafts

            });

            navigator.sendBeacon(

                `${API_BASE_URL}/ai/submission/${ctx.submissionId}/progress/`,

                new Blob([payload], { type: 'application/json' })

            );

        };



        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => window.removeEventListener('beforeunload', handleBeforeUnload);

    }, [isStarted, submissionId]);



    useEffect(() => {

        if (isStarted && timeLeft > 0) {

            timerRef.current = setInterval(() => setTimeLeft(p => p - 1), 1000);

        } else if (timeLeft === 0 && isStarted) {

            clearInterval(timerRef.current);

            // Use ref to avoid stale closure — always submits with current answers

            if (handleSubmitRef.current) handleSubmitRef.current();

        }

        return () => clearInterval(timerRef.current);

    }, [isStarted, timeLeft]);



    useEffect(() => {

        setCodeOutput([]);

        setExecutionResult(null);



        // Auto-populate custom input with sample case for coding challenges

        const cQ = allQs[currentQuestionIdx];



        if (cQ?.type === 'coding') {

            let sampleInput = cQ.example_input || cQ.examples?.[0]?.input || '';

            if (typeof sampleInput === 'object') sampleInput = JSON.stringify(sampleInput);

            setCustomInput(String(sampleInput).trim());

        } else {

            setCustomInput('');

        }

    }, [currentQuestionIdx, assessment]);



    // Bootstrap code drafts from starter code for all languages

    useEffect(() => {

        if (!isStarted || !assessment?.generated_content?.coding_challenges) return;



        setCodeDrafts(prev => {

            const nextDrafts = { ...prev };

            let changed = false;



            assessment.generated_content.coding_challenges.forEach((q, idx) => {

                const qKey = `coding_${idx}`;



                // Use supported languages to bootstrap all possible defaults

                supportedLanguages.forEach(sl => {

                    const dKey = `${qKey}_${sl.id}`;

                    if (nextDrafts[dKey] !== undefined) return;



                    let starter = undefined;

                    if (q.starter_code && typeof q.starter_code === 'object') {

                        const foundKey = Object.keys(q.starter_code).find(k => k.toLowerCase() === sl.id.toLowerCase());

                        if (foundKey) starter = formatCode(q.starter_code[foundKey]);

                    }



                    if (starter === undefined && q[`starter_code_${sl.id}`]) {

                        starter = formatCode(q[`starter_code_${sl.id}`]);

                    }



                    if (starter === undefined) {

                        starter = DEFAULT_BOILERPLATES[sl.id] || '# Write logic here\n';

                    }



                    nextDrafts[dKey] = starter;

                    changed = true;

                });

            });



            return changed ? nextDrafts : prev;

        });

    }, [isStarted, assessment]);



    // Track question switch to ensure answers sync with selected language draft

    useEffect(() => {

        if (!isStarted || !currentAnswerKey || !currentAnswerKey.startsWith('coding_')) return;



        const draftKey = `${currentAnswerKey}_${selectedLanguage}`;

        const draft = codeDrafts[draftKey];



        // If a draft exists and we don't have an answer for this coding question yet, load it.

        // But DON'T force sync if we already have an answer, to avoid fighting with setSelectedLanguage.

        if (draft !== undefined && !answers[currentAnswerKey]) {

            setAnswers(prev => ({ ...prev, [currentAnswerKey]: draft }));

        }

    }, [currentQuestionIdx, isStarted, codeDrafts]);

    // Lock page scroll while assessment is running

    useEffect(() => {

        document.body.style.margin = '0';

        document.body.style.overflow = 'hidden';

        document.documentElement.style.overflow = 'hidden';

        return () => {

            document.body.style.overflow = '';

            document.documentElement.style.overflow = '';

        };

    }, []);



    const goToQuestion = (idx) => {

        // Save progress immediately before navigating away from current question

        if (isStarted && submissionId && !submitted) {

            axios.post(`${API_BASE_URL}/ai/submission/${submissionId}/progress/`, {

                answers,

                current_question_index: idx,

                coding_results,

                codeDrafts: codeDrafts

            }).catch(() => { });

        }

        setCurrentQuestionIdx(idx);

        setVisitedQs(prev => new Set([...prev, idx]));

    };



    const handleSaveAndNext = () => {

        const total = (assessment?.generated_content?.mcqs?.length || 0) + (assessment?.generated_content?.coding_challenges?.length || 0);

        if (currentQuestionIdx < total - 1) goToQuestion(currentQuestionIdx + 1);

    };



    const handleMarkForReview = () => {

        setMarkedQs(prev => {

            const next = new Set(prev);

            if (next.has(currentQuestionIdx)) next.delete(currentQuestionIdx);

            else next.add(currentQuestionIdx);

            return next;

        });

        handleSaveAndNext();

    };



    const handleClearResponse = () => {

        const mcqs = assessment?.generated_content?.mcqs || [];

        const coding = assessment?.generated_content?.coding_challenges || [];

        const allQs = [...mcqs.map((q, i) => ({ ...q, type: 'mcq', id: i })), ...coding.map((c, i) => ({ ...c, type: 'coding', id: i }))];

        const cQ = allQs[currentQuestionIdx];

        const key = cQ.type === 'mcq' ? `mcq_${cQ.id}` : `coding_${cQ.id}`;

        setAnswers(prev => { const n = { ...prev }; delete n[key]; return n; });

        setAnsweredQs(prev => { const n = new Set(prev); n.delete(currentQuestionIdx); return n; });

    };



    const handleSubmit = async (e) => {

        if (e) e.preventDefault();

        setIsSubmitting(true);

        try {

            const formPayload = new FormData();
            formPayload.append('token', token);
            formPayload.append('name', candidateName);
            formPayload.append('email', candidateEmail);
            formPayload.append('phone', phone);
            formPayload.append('pan_number', panNumber);
            formPayload.append('pan_verified', panVerified);
            if (panPhoto) {
                formPayload.append('pan_photo', panPhoto);
            }
            formPayload.append('answers', JSON.stringify(answers));
            formPayload.append('coding_results', JSON.stringify(coding_results));

            await axios.post(`${API_BASE_URL}/ai/submit/`, formPayload, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            logCandidateActivity(token, 'AI Assessment Submitted', 'AI Assessment completed and submitted successfully.');

            // Mark as completed locally to prevent re-opening link later

            localStorage.setItem(`assessment_completed_${token}`, 'true');

            setSubmitted(true);

            await stopDeepfaceMonitoring();

            stopCamera();

            setIsRegistered(false);

            if (screenStreamRef.current) {

                screenStreamRef.current.getTracks().forEach(t => t.stop());

                screenStreamRef.current = null;

            }

        } catch { alert('Failed to submit.'); }

        finally { setIsSubmitting(false); }

    };



    // Keep ref in sync so timer always calls the latest version

    handleSubmitRef.current = handleSubmit;



    const formatTime = (seconds) => {

        if (!seconds && seconds !== 0) return '--:--';

        const m = Math.floor(seconds / 60);

        const s = seconds % 60;

        return `${m}:${s < 10 ? '0' : ''}${s}`;

    };



    // ══════════════════════════════════════

    // INTERNAL COMPONENTS

    // ══════════════════════════════════════

    const RegistrationWizard = ({ onComplete, onCancel }) => {

        const localVideoRef = useRef(null);

        const [capturedImg, setCapturedImg] = useState(null);

        const [wizardStep, setWizardStep] = useState(0); // 0: Capture, 1: Analyzing, 2: Success

        const [regError, setRegError] = useState('');



        useEffect(() => {

            const startRegCamera = async () => {

                try {

                    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });

                    if (localVideoRef.current) localVideoRef.current.srcObject = stream;

                } catch (e) { setRegError("Camera access denied. Biometric verification is required for this assessment."); }

            };

            startRegCamera();

            return () => {

                if (localVideoRef.current?.srcObject) localVideoRef.current.srcObject.getTracks().forEach(t => t.stop());

            };

        }, []);



        const handleRegisterFace = async () => {

            if (!localVideoRef.current && !capturedImg) return;



            let finalImage = capturedImg;

            if (!finalImage) {

                const canvas = document.createElement('canvas');

                canvas.width = 640; canvas.height = 480;

                const ctx = canvas.getContext('2d');

                ctx.drawImage(localVideoRef.current, 0, 0, 640, 480);

                finalImage = canvas.toDataURL('image/jpeg', 0.9);

                setCapturedImg(finalImage);

            }



            setWizardStep(1); // Analyzing

            setRegError('');



            try {

                const normalizedEmail = (candidateEmail || '').trim().toLowerCase();

                const personId = normalizedEmail || `temp_${Date.now()}`;

                const res = await axios.post(`${DEEPFACE_BASE_URL}/registration/register`, {

                    person_id: personId,

                    image_base64: finalImage.split(',')[1]

                });



                if (!res.data.success) {

                    setRegError(res.data.message || "Registration failed. Please ensure your face is clearly visible.");

                    setWizardStep(0);

                    setCapturedImg(null);

                    return;

                }



                setWizardStep(2); // Success

                logCandidateActivity(token, 'AI Interview Started', 'Candidate passed proctoring check and started the AI Interview.');

                setTimeout(() => {

                    setIsRegistered(true);

                    onComplete(finalImage.split(',')[1]);

                }, 1500);

            } catch (e) {

                setRegError("Registration failed. Please ensure your face is clearly visible.");

                setWizardStep(0);

                setCapturedImg(null);

            }

        };



        return (

            <div style={{

                position: 'fixed',

                inset: 0,

                background: 'rgba(255, 255, 255, 0.98)',

                zIndex: 100000,

                display: 'flex',

                flexDirection: 'column',

                alignItems: 'center',

                justifyContent: 'center',

                textAlign: 'center',

                padding: '2rem',

                fontFamily: 'Poppins'

            }}>

                <div style={{ maxWidth: '600px', width: '100%', background: 'white', padding: '2.5rem', borderRadius: '30px', boxShadow: '0 20px 50px rgba(0,0,0,0.1)' }}>

                    <h2 style={{ fontSize: '1.8rem', color: '#1a202c', marginBottom: '1rem', fontWeight: '800' }}>AI Face Registration</h2>

                    <p style={{ color: '#4a5568', fontSize: '1rem', marginBottom: '2rem' }}>

                        Please look directly at the camera. We need to register your face for our AI proctoring system.

                    </p>



                    <div style={{ width: '100%', maxWidth: '400px', margin: '0 auto 2rem', aspectRatio: '4/3', borderRadius: '20px', overflow: 'hidden', background: '#000', position: 'relative' }}>

                        {capturedImg ? (

                            <img src={capturedImg} alt="Captured face" style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />

                        ) : (

                            <video ref={localVideoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />

                        )}



                        {/* Overlay guides */}

                        <div style={{ position: 'absolute', top: '10%', bottom: '15%', left: '25%', right: '25%', border: '2px dashed rgba(255,255,255,0.7)', borderRadius: '50%' }}></div>



                        {wizardStep === 1 && (

                            <>

                                <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>

                                    Analyzing face...

                                </div>

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



                    {regError && <div style={{ color: '#ef4444', marginBottom: '1.5rem', fontWeight: 600 }}>{regError}</div>}



                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>

                        <button

                            onClick={onCancel}

                            style={{ background: 'white', color: '#4a5568', border: '1px solid #e2e8f0', padding: '1rem 2rem', borderRadius: '50px', fontSize: '1rem', fontWeight: '600', cursor: 'pointer' }}

                        >

                            Cancel

                        </button>

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

                            {wizardStep === 1 ? 'Please Wait...' : wizardStep === 2 ? 'Registration Complete!' : 'Capture & Register'}

                        </button>

                    </div>

                </div>

            </div>

        );

    };



    if (isRegistering) {

        return <RegistrationWizard onComplete={(img) => { 

            setRegistrationSnapshot(img);

            setIsRegistering(false); 

            setIsRegistered(true); 

            startAssessment(true); 

        }} onCancel={() => setIsRegistering(false)} />;

    }



    if (loading) return (



        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins', background: '#F4F7FE' }}>

            <div style={{ textAlign: 'center' }}>

                <p style={{ color: '#4318FF', fontWeight: 600 }}>Loading assessment...</p>

            </div>

        </div>

    );



    if (error) return (

        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins', background: '#F4F7FE' }}>

            <div style={{ textAlign: 'center', padding: '3rem', background: 'white', borderRadius: '20px', boxShadow: '0 4px 20px rgba(0,0,0,0.06)' }}>

                <h2 style={{ color: '#1B254B' }}>Link Error</h2>

                <p style={{ color: '#A3AED0' }}>{error}</p>

            </div>

        </div>

    );



    if (submitted) return (

        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins', background: '#F4F7FE' }}>

            <div style={{ textAlign: 'center', padding: '3rem', background: 'white', borderRadius: '24px', maxWidth: 480, boxShadow: '0 4px 20px rgba(0,0,0,0.06)' }}>

                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>

                <h1 style={{ color: '#1B254B', marginBottom: '1rem' }}>Assessment Submitted!</h1>

                <p style={{ color: '#A3AED0' }}>Thank you, {candidateName}. The recruiter has been notified.</p>

            </div>

        </div>

    );



    if (!isStarted) return (

        <div style={{ background: '#F4F7FE', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', fontFamily: 'Poppins', padding: 20 }}>

            <div style={{ maxWidth: 580, width: '100%', background: 'white', borderRadius: 24, boxShadow: '0 4px 20px rgba(67,24,255,0.08)', overflow: 'hidden', border: '1px solid #f1f5f9' }}>

                <div style={{ background: '#4318FF', padding: '1.5rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>

                    <div>

                        <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.75rem', fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase' }}>AI Technical Assessment</div>

                        <div style={{ color: 'white', fontSize: '1.4rem', fontWeight: 800, marginTop: 2 }}>{assessment?.title || 'Technical Test'}</div>

                    </div>

                    <div style={{ textAlign: 'right', color: 'rgba(255,255,255,0.7)', fontSize: '0.82rem' }}>

                        <div>Duration</div>

                        <div style={{ color: 'white', fontWeight: 800, fontSize: '1.1rem' }}>{assessment?.duration_minutes} min</div>

                    </div>

                </div>

                <div style={{ padding: '0.8rem 2rem', background: '#F8F9FF', borderBottom: '1px solid #E0E5F2', display: 'flex', gap: '1.5rem', fontSize: '0.78rem', color: '#707EAE' }}>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>

                        <i className="fa-regular fa-calendar-check" style={{ color: '#4318FF' }}></i>

                        <span>Starts: <strong style={{ color: '#1B254B' }}>{assessment.available_from ? new Date(assessment.available_from).toLocaleString() : 'Now'}</strong></span>

                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>

                        <i className="fa-regular fa-calendar-xmark" style={{ color: '#EE5D50' }}></i>

                        <span>Ends: <strong style={{ color: '#1B254B' }}>{assessment.available_until ? new Date(assessment.available_until).toLocaleString() : 'No Limit'}</strong></span>

                    </div>

                </div>

                <div style={{ padding: '2rem' }}>

                    <p style={{ color: '#A3AED0', marginBottom: '1.5rem', lineHeight: 1.6 }}>Please enter your details to start. The exam will begin immediately after you click <strong style={{ color: '#1B254B' }}>Start Test</strong>.</p>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>

                        <div>

                            <label style={{ display: 'block', fontWeight: 700, color: '#1B254B', marginBottom: 6, fontSize: '0.85rem' }}>Full Name *</label>

                            <input type="text" value={candidateName} onChange={e => setCandidateName(e.target.value)} placeholder="Enter your full name"

                                disabled={isAutoFilled}

                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: 12, border: '1px solid #E0E5F2', outline: 'none', fontSize: '0.95rem', fontFamily: 'Poppins', boxSizing: 'border-box', color: '#1B254B', background: isAutoFilled ? '#f8f9ff' : 'white', cursor: isAutoFilled ? 'not-allowed' : 'text' }} />

                        </div>

                        <div>

                            <label style={{ display: 'block', fontWeight: 700, color: '#1B254B', marginBottom: 6, fontSize: '0.85rem' }}>Email Address *</label>

                            <input type="email" value={candidateEmail} onChange={e => setCandidateEmail(e.target.value)} placeholder="Enter your email"

                                disabled={isAutoFilled}

                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: 12, border: '1px solid #E0E5F2', outline: 'none', fontSize: '0.95rem', fontFamily: 'Poppins', boxSizing: 'border-box', color: '#1B254B', background: isAutoFilled ? '#f8f9ff' : 'white', cursor: isAutoFilled ? 'not-allowed' : 'text' }} />

                        </div>

                        {/* Phone Number */}
                        <div>

                            <label style={{ display: 'block', fontWeight: 700, color: '#1B254B', marginBottom: 6, fontSize: '0.85rem' }}>Phone Number *</label>

                            <input

                                type="tel"

                                value={phone}

                                onChange={(e) => {

                                    const value = e.target.value.replace(/\D/g, '');

                                    if (value.length <= 10) setPhone(value);

                                }}

                                placeholder="Enter your phone number"

                                maxLength={10}

                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: 12, border: '1px solid #E0E5F2', outline: 'none', fontSize: '0.95rem', fontFamily: 'Poppins', boxSizing: 'border-box', color: '#1B254B' }}

                            />

                        </div>

                        {/* PAN Card Number */}
                        <div>

                            <label style={{ display: 'block', fontWeight: 700, color: '#1B254B', marginBottom: 6, fontSize: '0.85rem' }}>PAN Card Number *</label>

                            <div style={{ display: 'flex', gap: '0.5rem' }}>

                                <input

                                    type="text"

                                    value={panNumber}

                                    onChange={(e) => {

                                        const value = e.target.value.toUpperCase();

                                        const position = value.length - 1;

                                        const lastChar = value[position];



                                        if (position >= 0 && position < 5) {

                                            if (!/^[A-Z]$/.test(lastChar)) return;

                                        } else if (position >= 5 && position < 9) {

                                            if (!/^[0-9]$/.test(lastChar)) return;

                                        } else if (position === 9) {

                                            if (!/^[A-Z]$/.test(lastChar)) return;

                                        }



                                        setPanNumber(value);

                                        setPanVerified(false);

                                        setPanError('');

                                    }}

                                    placeholder="e.g. ABCDE1234F"

                                    maxLength={10}

                                    style={{

                                        flex: 1, padding: '0.75rem 1rem', borderRadius: 12, border: '1px solid #E0E5F2',

                                        outline: 'none', fontSize: '0.95rem', fontFamily: 'Poppins', boxSizing: 'border-box',

                                        textTransform: 'uppercase', letterSpacing: '0.05em', color: '#1B254B',

                                        borderColor: panVerified ? '#22c55e' : panError ? '#ef4444' : '#E0E5F2'

                                    }}

                                />

                                {panVerified && (

                                    <span style={{ display: 'flex', alignItems: 'center', color: '#22c55e', fontWeight: '700', fontSize: '0.85rem', whiteSpace: 'nowrap' }}>

                                        <i className="fa-solid fa-circle-check" style={{ marginRight: '4px' }}></i>Verified

                                    </span>

                                )}

                            </div>

                            <p style={{ margin: '0.25rem 0 0', fontSize: '0.75rem', color: '#707EAE' }}>Format: 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F)</p>

                        </div>

                        {/* PAN Card Photo Upload */}

                        <div>

                            <label style={{ display: 'block', fontWeight: 700, color: '#1B254B', marginBottom: 6, fontSize: '0.85rem' }}>
                                PAN Card Photo * <span style={{ fontWeight: 400, fontSize: '0.75rem', color: '#707EAE' }}>(JPG, PNG, PDF, Max 2.5MB)</span>
                            </label>

                            <div

                                onClick={() => document.getElementById('panPhotoInput').click()}

                                style={{

                                    border: '2px dashed #cbd5e0', borderRadius: 12, padding: '1rem', cursor: 'pointer',

                                    transition: 'all 0.2s', background: panPhotoPreview ? '#f0fdf4' : 'transparent',

                                    borderColor: panVerified ? '#22c55e' : panPhotoPreview ? '#38b2ac' : '#cbd5e0',

                                    display: 'flex', alignItems: 'center', gap: '1rem'

                                }}

                            >

                                <input type="file" id="panPhotoInput" accept=".jpg,.jpeg,.png,.pdf,image/*,application/pdf" hidden onChange={handlePanPhotoChange} />

                                {panPhotoPreview ? (
                                    <img src={panPhotoPreview} alt="PAN card" style={{ width: '80px', height: '60px', objectFit: 'cover', borderRadius: '8px' }} />
                                ) : panPhoto && (panPhoto.type === 'application/pdf' || panPhoto.name?.toLowerCase().endsWith('.pdf')) ? (
                                    <i className="fa-solid fa-file-pdf" style={{ fontSize: '2rem', color: '#ef4444' }}></i>
                                ) : (
                                    <i className="fa-solid fa-cloud-arrow-up" style={{ fontSize: '1.5rem', color: '#4318FF' }}></i>
                                )}

                                <div>

                                    <p style={{ margin: '0 0 0.25rem', fontWeight: '600', color: '#1B254B', fontSize: '0.9rem' }}>

                                        {panPhoto ? panPhoto.name : 'Upload PAN Card Photo'}

                                    </p>

                                    <p style={{ margin: 0, fontSize: '0.75rem', color: '#707EAE' }}>Click to browse</p>

                                </div>

                            </div>

                        </div>

                        {/* Verify PAN Button */}

                        {panNumber && panPhoto && !panVerified && (

                            <button

                                onClick={handleValidatePan}

                                disabled={panValidating || !validatePanFormat(panNumber)}

                                style={{

                                    width: '100%', padding: '0.75rem', marginBottom: '1.5rem',

                                    background: panValidating || !validatePanFormat(panNumber) ? '#cbd5e0' : 'linear-gradient(135deg, #4318FF 0%, #764ba2 100%)',

                                    color: 'white', border: 'none', borderRadius: 12,

                                    fontSize: '0.95rem', fontWeight: '600', cursor: panValidating || !validatePanFormat(panNumber) ? 'not-allowed' : 'pointer',

                                    opacity: panValidating || !validatePanFormat(panNumber) ? 0.7 : 1

                                }}

                            >

                                {panValidating ? <><i className="fa-solid fa-spinner fa-spin"></i> Verifying PAN...</> : 'Verify PAN Card'}

                            </button>

                        )}

                        {/* PAN Error */}

                        {panError && (

                            <div style={{

                                background: '#FEF2F2', border: '1px solid #FCA5A5', borderRadius: 12,

                                padding: '0.75rem 1rem', marginBottom: '1.5rem', color: '#991B1B',

                                fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem'

                            }}>

                                <i className="fa-solid fa-circle-exclamation"></i>

                                <span>{panError}</span>

                            </div>

                        )}

                        {/* Form Error */}

                        {formError && (

                            <div style={{

                                background: '#FEF2F2', border: '1px solid #FCA5A5', borderRadius: '14px',

                                padding: '0.8rem 1.2rem', marginBottom: '1.5rem', color: '#991B1B',

                                fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.75rem',

                                boxShadow: '0 2px 4px rgba(153, 27, 27, 0.05)'

                            }}>

                                <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '1.1rem' }}></i>

                                <span style={{ fontWeight: '500' }}>{formError}</span>

                            </div>

                        )}

                    </div>

                    <div style={{ background: '#FFF8E6', border: '1px solid #FFA800', borderRadius: 12, padding: '0.9rem 1rem', marginBottom: '1.5rem', fontSize: '0.82rem', color: '#1B254B' }}>

                        <strong>⚠️ Warning:</strong> This test uses AI video monitoring. Switching tabs or leaving the window will be flagged as malpractice.

                    </div>

                    <button onClick={startAssessment}

                        disabled={isCheckingRegistration}

                        style={{ width: '100%', padding: '0.9rem', background: isCheckingRegistration ? '#94a3b8' : '#4318FF', color: 'white', border: 'none', borderRadius: 12, fontSize: '1rem', fontWeight: 700, cursor: isCheckingRegistration ? 'not-allowed' : 'pointer', fontFamily: 'Poppins', boxShadow: '0 10px 20px rgba(67,24,255,0.2)', transition: 'all 0.2s' }}>

                        {isCheckingRegistration ? 'Checking Registration...' : 'Start Test'}

                    </button>

                </div>

            </div>

        </div>

    );



    if (allQs.length === 0) {

        return (

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#f8f9ff', fontFamily: 'Poppins' }}>

                <div style={{ background: 'white', padding: '2rem', borderRadius: 16, boxShadow: '0 10px 25px rgba(0,0,0,0.05)', textAlign: 'center', maxWidth: 400 }}>

                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>

                    <h2 style={{ color: '#1B254B', margin: '0 0 1rem 0' }}>Assessment Content Empty</h2>

                    <p style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.5 }}>

                        The AI was unable to generate any questions for your assessment, or the content format was malformed. Please contact the recruiter or attempt to regenerate the link.

                    </p>

                </div>

            </div>

        );

    }



    const isLastQ_old = currentQuestionIdx === allQs.length - 1;

    // const currentAnswerKey = currentQ?.type === 'mcq' ? `mcq_${currentQ?.id}` : `coding_${currentQ?.id}`;



    // const mcqSection = allQs.filter(q => q.type === 'mcq');

    // const codingSection = allQs.filter(q => q.type === 'coding');



    const getQStatus = (idx) => {

        if (idx === currentQuestionIdx) return 'current';

        if (markedQs.has(idx) && answeredQs.has(idx)) return 'answered-marked';

        if (markedQs.has(idx)) return 'marked';

        if (answeredQs.has(idx)) return 'answered';

        if (visitedQs.has(idx)) return 'not-answered';

        return 'not-visited';

    };



    const statusStyle = (status) => {

        switch (status) {

            case 'current': return { background: '#3b82f6', color: 'white', border: '2px solid #1d4ed8' };

            case 'answered': return { background: '#22c55e', color: 'white', border: '2px solid #16a34a' };

            case 'not-answered': return { background: '#ef4444', color: 'white', border: '2px solid #dc2626' };

            case 'marked': return { background: '#a855f7', color: 'white', border: '2px solid #7c3aed' };

            case 'answered-marked': return { background: '#a855f7', color: 'white', border: '2px solid #7c3aed' };

            default: return { background: 'white', color: '#374151', border: '2px solid #d1d5db' };

        }

    };



    return (

        <div style={{

            position: 'fixed',

            top: 0,

            left: 0,

            right: 0,

            bottom: 0,

            background: '#f0fdf4',

            display: 'flex',

            flexDirection: 'column',

            overflow: 'hidden',

            fontFamily: 'Poppins'

        }}>





            {aiToast.active && (

                <div style={{ position: 'fixed', top: 100, left: '50%', transform: 'translateX(-50%)', zIndex: 99999, background: aiToast.urgent ? '#dc2626' : '#1d4ed8', color: 'white', padding: '10px 24px', borderRadius: 25, fontWeight: 700, fontSize: '0.82rem', boxShadow: '0 6px 24px rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', gap: 8, letterSpacing: 0.5 }}>

                    <span style={{ fontSize: '1rem' }}>{aiToast.urgent ? '' : ''}</span>

                    {aiToast.text}

                </div>

            )}

            <canvas ref={screenCanvasRef} style={{ display: 'none' }} width="1280" height="720" />



            {/* TOP HEADER */}

            <div style={{ flexShrink: 0, background: 'white', borderBottom: '1px solid #e5e7eb', padding: '0 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 52 }}>

                <div style={{ fontWeight: 800, fontSize: '1.1rem', color: '#1a5276' }}>{assessment?.title || 'Technical Assessment'}</div>

                <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>

                    <button style={{ background: 'none', border: 'none', color: '#374151', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}>

                        Question Paper

                    </button>

                    <button style={{ background: 'none', border: 'none', color: '#374151', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}>

                        Instructions

                    </button>

                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>

                    <div style={{ textAlign: 'right' }}>

                        <div style={{ fontSize: '0.65rem', color: '#6b7280', fontWeight: 700, textTransform: 'uppercase' }}>Time Left</div>

                        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: timeLeft < 300 ? '#dc2626' : '#1a5276' }}>{formatTime(timeLeft)}</div>

                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'rgba(255,255,255,0.8)', border: '1px solid #e0e7ff', borderRadius: 40, padding: '4px 14px 4px 6px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', backdropFilter: 'blur(8px)' }}>

                        <div style={{

                            position: 'relative',

                            width: 52,

                            height: 52,

                            borderRadius: '50%',

                            overflow: 'hidden',

                            border: `2.5px solid ${dfVerified === null ? '#6366f1' :

                                    dfVerified === false ? '#ef4444' :

                                        dfHeadDir !== 'FORWARD' ? '#f59e0b' : '#22c55e'

                                }`,

                            boxShadow: `0 0 12px ${dfVerified === null ? 'rgba(99,102,241,0.3)' :

                                    dfVerified === false ? 'rgba(239,68,68,0.5)' :

                                        dfHeadDir !== 'FORWARD' ? 'rgba(245,158,11,0.4)' : 'rgba(34,197,94,0.3)'

                                }`,

                            transition: 'all 0.3s ease',

                            animation: dfVerified === false ? 'pulse-error 1s infinite' : 'none'

                        }}>

                            <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />

                            <canvas ref={dfCanvasRef} style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 10, pointerEvents: 'none' }} />



                            {/* Scanning Animation */}

                            <div style={{

                                position: 'absolute', top: 0, left: 0, right: 0, height: '2px', background: '#6366f1',

                                boxShadow: '0 0 8px 2px rgba(99, 102, 241, 0.6)', animation: 'ai-scan 2s ease-in-out infinite', zIndex: 11

                            }}></div>

                        </div>



                        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>

                            <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#1B254B', lineHeight: 1.1 }}>{candidateName}</span>

                            <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>

                                {dfSessionId ? (

                                    <>

                                        <div style={{

                                            background: dfVerified === true ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)',

                                            color: dfVerified === true ? '#16a34a' : '#dc2626',

                                            padding: '2px 8px', borderRadius: 6, fontSize: '0.62rem', fontWeight: 800,

                                            border: `1px solid ${dfVerified === true ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,

                                            display: 'flex', alignItems: 'center', gap: 4, backdropFilter: 'blur(4px)'

                                        }}>

                                            <i className={`fa-solid ${dfVerified === true ? 'fa-check-circle' : 'fa-circle-xmark'}`}></i>

                                            {dfVerified === true ? 'VERIFIED' : 'MISMATCH'}

                                        </div>

                                        <div style={{

                                            background: 'rgba(99, 102, 241, 0.15)', color: '#4f46e5',

                                            padding: '2px 8px', borderRadius: 6, fontSize: '0.62rem', fontWeight: 800,

                                            border: '1px solid rgba(99, 102, 241, 0.3)',

                                            display: 'flex', alignItems: 'center', gap: 4, backdropFilter: 'blur(4px)'

                                        }}>

                                            <i className="fa-solid fa-bolt"></i>

                                            {Math.round(dfEngagement)}%

                                        </div>

                                        <div style={{

                                            background: 'rgba(75, 85, 99, 0.1)', color: '#4b5563',

                                            padding: '2px 8px', borderRadius: 6, fontSize: '0.62rem', fontWeight: 800,

                                            border: '1px solid rgba(75, 85, 99, 0.2)',

                                            display: 'flex', alignItems: 'center', gap: 4, backdropFilter: 'blur(4px)'

                                        }}>

                                            <i className="fa-solid fa-compass"></i>

                                            {dfHeadDir}

                                        </div>

                                        <div style={{

                                            background: isDeepfaceActive ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)',

                                            color: isDeepfaceActive ? '#16a34a' : '#dc2626',

                                            padding: '2px 8px',

                                            borderRadius: 6,

                                            fontSize: '0.62rem',

                                            fontWeight: 800,

                                            border: `1px solid ${isDeepfaceActive ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,

                                            display: 'flex',

                                            alignItems: 'center',

                                            gap: 4,

                                            backdropFilter: 'blur(4px)'

                                        }}>

                                            <i className={`fa-solid ${isDeepfaceActive ? 'fa-shield-halved' : 'fa-triangle-exclamation'}`}></i>

                                            {isDeepfaceActive ? 'MONITORING ON' : 'MONITORING OFF'}

                                        </div>

                                    </>

                                ) : (

                                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>

                                        <div className="pulse-dot" style={{ width: 6, height: 6, borderRadius: '50%', background: '#6366f1' }}></div>

                                        <span style={{ fontSize: '0.62rem', color: '#6366f1', fontWeight: 800, letterSpacing: 0.5 }}>SECURE FEED INITIALIZING...</span>

                                    </div>

                                )}

                            </div>

                        </div>

                    </div>

                </div>



                <style>{`

                    @keyframes ai-scan {

                        0% { top: 0%; opacity: 0.2; }

                        50% { top: 100%; opacity: 1; }

                        100% { top: 0%; opacity: 0.2; }

                    }

                    .pulse-dot {

                        animation: pulse-ai 1.5s infinite;

                    }

                    @keyframes pulse-ai {

                        0% { transform: scale(1); opacity: 1; }

                        50% { transform: scale(1.5); opacity: 0.5; }

                        100% { transform: scale(1); opacity: 1; }

                    }

                    @keyframes pulse-error {

                        0% { border-color: #ef4444; box-shadow: 0 0 0px rgba(239,68,68,0.7); }

                        50% { border-color: #7f1d1d; box-shadow: 0 0 15px rgba(239,68,68,0.9); }

                        100% { border-color: #ef4444; box-shadow: 0 0 0px rgba(239,68,68,0.7); }

                    }

                `}</style>

            </div>



            {/* SECTION TABS */}

            <div style={{ flexShrink: 0, background: 'white', borderBottom: '1px solid #e5e7eb', padding: '0 1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', height: 40 }}>

                {mcqSection.length > 0 && (

                    <button onClick={() => goToQuestion(0)}

                        style={{ padding: '4px 16px', borderRadius: 20, border: 'none', fontWeight: 700, fontSize: '0.8rem', cursor: 'pointer', background: currentQ.type === 'mcq' ? '#1a5276' : '#f3f4f6', color: currentQ.type === 'mcq' ? 'white' : '#374151' }}>

                        MCQ ({mcqSection.length})

                    </button>

                )}

                {codingSection.length > 0 && (

                    <button onClick={() => goToQuestion(mcqSection.length)}

                        style={{ padding: '4px 16px', borderRadius: 20, border: 'none', fontWeight: 700, fontSize: '0.8rem', cursor: 'pointer', background: currentQ.type === 'coding' ? '#1a5276' : '#f3f4f6', color: currentQ.type === 'coding' ? 'white' : '#374151' }}>

                        Coding ({codingSection.length})

                    </button>

                )}

                <div style={{ flex: 1 }}></div>

                <span style={{ fontSize: '0.78rem', color: '#6b7280' }}>Question <strong style={{ color: '#1a5276' }}>{currentQuestionIdx + 1}</strong> of <strong>{allQs.length}</strong></span>

            </div>



            {/* MAIN BODY */}

            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>



                {/* LEFT: Question Panel */}

                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', borderRight: '1px solid #e5e7eb' }}>



                    {/* Question Meta bar */}

                    <div style={{ flexShrink: 0, padding: '7px 1.5rem', background: '#f9fafb', borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>

                        <span style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600 }}>

                            Question type: <span style={{ color: '#1a5276' }}>{currentQ.type === 'mcq' ? 'Multiple Choice' : 'Coding Challenge'}</span>

                        </span>

                    </div>



                    {/* Question Body */}

                    <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>

                        {currentQ.type === 'mcq' ? (

                            <div style={{ flex: 1, overflowY: 'auto', padding: '1.2rem 1.5rem' }}>

                                <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#111827', margin: '0 0 1.2rem', lineHeight: 1.6 }}>

                                    <span style={{ color: '#1a5276', marginRight: 8 }}>Question No. {currentQuestionIdx + 1}</span>

                                </h2>

                                <p style={{ color: '#111827', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1.2rem' }}>{currentQ.question}</p>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>

                                    {(Array.isArray(currentQ.options) ? currentQ.options : Object.values(currentQ.options || {})).map((opt, i) => {

                                        const selected = answers[currentAnswerKey] === opt;

                                        const labels = ['A', 'B', 'C', 'D', 'E'];

                                        return (

                                            <label key={i} style={{

                                                display: 'flex', alignItems: 'flex-start', gap: 12,

                                                padding: '0.75rem 1rem', borderRadius: 8, cursor: 'pointer',

                                                border: `1.5px solid ${selected ? '#1a5276' : '#e5e7eb'}`,

                                                background: selected ? '#eff6ff' : 'white', transition: 'all 0.15s'

                                            }}>

                                                <input type="radio" name={`q_${currentQ.id}`} checked={selected}

                                                    onChange={() => handleAnswerChange(currentAnswerKey, opt)}

                                                    style={{ marginTop: 2, accentColor: '#1a5276', width: 16, height: 16, flexShrink: 0 }} />

                                                <span style={{ fontSize: '0.92rem', color: '#111827', fontWeight: selected ? 600 : 400, lineHeight: 1.5 }}>

                                                    <strong style={{ color: '#1a5276', marginRight: 6 }}>{labels[i]}.</strong>{opt}

                                                </span>

                                            </label>

                                        );

                                    })}

                                </div>

                            </div>

                        ) : (

                            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

                                {/* Problem statement */}

                                <div style={{ width: '36%', display: 'flex', flexDirection: 'column', borderRight: '1px solid #e5e7eb', overflow: 'hidden', background: 'white' }}>

                                    <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 1.2rem' }}>

                                        {/* Professional Header */}

                                        <div style={{ marginBottom: '1rem' }}>

                                            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#111827', margin: '0 0 0.5rem', display: 'flex', alignItems: 'center', gap: 10 }}>

                                                {currentQ.title || `Challenge ${currentQ.id + 1}`}

                                            </h2>



                                            <div style={{ display: 'flex', gap: 8, marginBottom: '1.2rem' }}>

                                                <div style={{ fontSize: '0.7rem', padding: '3px 10px', background: '#f3f4f6', borderRadius: 15, color: '#4b5563', fontWeight: 600 }}>Topics</div>

                                                <div style={{ fontSize: '0.7rem', padding: '3px 10px', background: '#f3f4f6', borderRadius: 15, color: '#4b5563', fontWeight: 600 }}>Companies</div>

                                                <div style={{ fontSize: '0.7rem', padding: '3px 10px', background: '#f3f4f6', borderRadius: 15, color: '#4b5563', fontWeight: 600 }}>Hint</div>

                                            </div>



                                            <div style={{ color: '#374151', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>

                                                {currentQ.problem_statement

                                                    ? <div dangerouslySetInnerHTML={{ __html: formatText(currentQ.problem_statement) }} />

                                                    : <p style={{ margin: 0 }}>{currentQ.description || 'No description.'}</p>}

                                            </div>

                                        </div>



                                        {/* Examples Section */}

                                        {(currentQ.test_cases?.length > 0 || currentQ.example_input) && (

                                            <div style={{ marginBottom: '1.5rem' }}>

                                                {((currentQ.test_cases && currentQ.test_cases.length > 0) ? currentQ.test_cases.slice(0, 3) :

                                                    (currentQ.example_input ? [{ input: currentQ.example_input, output: currentQ.example_output, explanation: currentQ.explanation }] : [])

                                                ).map((tc, idx) => (

                                                    <div key={idx} style={{ marginBottom: '1.2rem' }}>

                                                        <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#111827', marginBottom: 8 }}>Example {idx + 1}:</div>

                                                        <div style={{

                                                            background: '#f8f9fa',

                                                            borderLeft: '2px solid #e5e7eb',

                                                            padding: '10px 15px',

                                                            fontFamily: 'Menlo, Monaco, Consolas, "Courier New", monospace',

                                                            fontSize: '0.85rem'

                                                        }}>

                                                            <div style={{ marginBottom: 4 }}><strong style={{ color: '#111827' }}>Input:</strong> {typeof tc.input === 'object' ? JSON.stringify(tc.input) : String(tc.input || '').trim()}</div>

                                                            <div style={{ marginBottom: 4 }}><strong style={{ color: '#111827' }}>Output:</strong> {typeof tc.output === 'object' ? JSON.stringify(tc.output) : String(tc.output || '').trim()}</div>

                                                            {tc.explanation && (

                                                                <div><strong style={{ color: '#111827' }}>Explanation:</strong> {tc.explanation}</div>

                                                            )}

                                                        </div>

                                                    </div>

                                                ))}

                                            </div>

                                        )}



                                        {/* Constraints */}

                                        {currentQ.constraints && (Array.isArray(currentQ.constraints) ? currentQ.constraints.length > 0 : String(currentQ.constraints).length > 0) && (

                                            <div style={{ marginBottom: '1.5rem' }}>

                                                <div style={{ fontSize: '1rem', fontWeight: 700, color: '#111827', marginBottom: 8 }}>Constraints:</div>

                                                <ul style={{ margin: 0, paddingLeft: '1.2rem', color: '#111827', fontSize: '0.85rem', lineHeight: 1.6 }}>

                                                    {Array.isArray(currentQ.constraints)

                                                        ? currentQ.constraints.map((c, i) => <li key={i} style={{ marginBottom: 4 }}><code>{c}</code></li>)

                                                        : <li style={{ marginBottom: 4 }}><code>{currentQ.constraints}</code></li>

                                                    }

                                                </ul>

                                            </div>

                                        )}

                                    </div>

                                    <div style={{ flexShrink: 0, borderTop: '1px solid #e5e7eb', padding: '5px 10px', background: '#f9fafb', display: 'flex', alignItems: 'center', gap: 7 }}>

                                        <span style={{ fontSize: '0.68rem', fontWeight: 700, color: '#6b7280', whiteSpace: 'nowrap' }}>stdin:</span>

                                        <textarea value={customInput} onChange={e => setCustomInput(e.target.value)} placeholder="Custom input..."

                                            style={{ flex: 1, height: 30, padding: '4px 8px', borderRadius: 5, border: '1px solid #e5e7eb', fontFamily: 'monospace', fontSize: '0.75rem', resize: 'none', outline: 'none' }} />

                                    </div>

                                </div>



                                {/* Editor + Console */}

                                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>

                                    <div style={{ flexShrink: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 10px', background: '#1e1e1e', borderBottom: '1px solid #2d2d2d' }}>

                                        <select value={selectedLanguage} onChange={e => setSelectedLanguage(e.target.value)}

                                            style={{ padding: '3px 8px', borderRadius: 5, border: '1px solid #3d3d3d', fontSize: '0.75rem', fontWeight: 700, color: '#d4d4d4', background: '#2d2d2d', outline: 'none', cursor: 'pointer' }}>

                                            {supportedLanguages.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}

                                        </select>

                                        <div style={{ display: 'flex', gap: 5 }}>

                                            <button onClick={handleRestoreCode}

                                                style={{ padding: '3px 12px', background: 'transparent', color: '#888', border: '1px solid #3d3d3d', borderRadius: 5, fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', marginRight: 5 }}>

                                                Restore

                                            </button>

                                            <button onClick={() => runCode(currentQ.id, false)} disabled={isExecuting}

                                                style={{ padding: '3px 12px', background: '#2d2d2d', color: '#d4d4d4', border: '1px solid #4d4d4d', borderRadius: 5, fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', opacity: isExecuting ? 0.6 : 1 }}>

                                                Run

                                            </button>

                                            <button onClick={() => runCode(currentQ.id, true)} disabled={isExecuting}

                                                style={{ padding: '3px 12px', background: '#16a34a', color: 'white', border: 'none', borderRadius: 5, fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', opacity: isExecuting ? 0.6 : 1 }}>

                                                Submit Code

                                            </button>

                                        </div>

                                    </div>

                                    <div style={{ flex: 1, overflow: 'hidden' }}>

                                        <Editor

                                            key={`${currentAnswerKey}_${selectedLanguage}`}

                                            height="100%" language={selectedLanguage} theme="vs-dark"

                                            value={answers[currentAnswerKey] || ""}

                                            onChange={val => handleAnswerChange(currentAnswerKey, val)}

                                            options={{ fontSize: 13, minimap: { enabled: false }, scrollBeyondLastLine: false, automaticLayout: true, padding: { top: 10 }, lineNumbers: 'on' }} />

                                    </div>

                                    <div style={{ flexShrink: 0, height: 110, borderTop: '1px solid #2d2d2d', background: '#0d0d1a', display: 'flex', flexDirection: 'column' }}>

                                        <div style={{ padding: '3px 10px', background: '#1a1a2e', borderBottom: '1px solid #2d2d2d', fontSize: '0.65rem', fontWeight: 700, color: '#6b7280', textTransform: 'uppercase' }}>Console Output</div>

                                        <div style={{ flex: 1, overflowY: 'auto', padding: '5px 10px', fontFamily: 'Courier New, monospace', fontSize: '0.78rem' }}>

                                            {executionResult?.type === 'test_cases' ? (

                                                <div>

                                                    <div style={{ fontWeight: 800, color: executionResult.score === executionResult.total ? '#22c55e' : '#ef4444', marginBottom: 4 }}>

                                                        {executionResult.score}{'/'}{executionResult.total} test cases passed

                                                    </div>

                                                    {executionResult.results.map((r, i) => (

                                                        <div key={i} style={{ fontSize: '0.72rem', color: r.passed ? '#22c55e' : '#ef4444', marginBottom: 1 }}>

                                                            {r.passed ? 'PASS' : 'FAIL'} {r.isHidden ? 'Hidden' : 'Sample'} Case {i + 1}

                                                            {!r.passed && <span style={{ color: '#888' }}> exp: "{String(r.expected || '').substring(0, 30)}" got: "{String(r.actual || '').substring(0, 30)}"</span>}

                                                        </div>

                                                    ))}

                                                </div>

                                            ) : codeOutput.length === 0 ? (

                                                <div style={{ color: '#3d3d5c', fontStyle: 'italic' }}>Run code to see output...</div>

                                            ) : (

                                                codeOutput.map((log, i) => (

                                                    <div key={i} style={{ color: log.type === 'error' ? '#f87171' : log.type === 'success' ? '#4ade80' : log.type === 'info' ? '#93c5fd' : '#d1d5db', marginBottom: 1 }}>

                                                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{log.content}</pre>

                                                    </div>

                                                ))

                                            )}

                                        </div>

                                    </div>

                                </div>

                            </div>

                        )}

                    </div>

                </div>



                {/* RIGHT SIDEBAR */}

                <div style={{ width: 230, flexShrink: 0, background: 'white', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

                    <div style={{ flexShrink: 0, padding: '0.8rem', borderBottom: '1px solid #e5e7eb', background: '#fafafa' }}>

                        {[

                            { color: '#3b82f6', label: 'Current' },

                            { color: '#22c55e', label: 'Answered' },

                            { color: '#ef4444', label: 'Not Answered' },

                            { color: '#d1d5db', label: 'Not Visited' },

                            { color: '#a855f7', label: 'Marked for Review' },

                        ].map(({ color, label }) => (

                            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 4 }}>

                                <div style={{ width: 14, height: 14, borderRadius: '50%', background: color, flexShrink: 0 }}></div>

                                <span style={{ fontSize: '0.72rem', color: '#374151', fontWeight: 500 }}>{label}</span>

                            </div>

                        ))}

                    </div>

                    <div style={{ flex: 1, overflowY: 'auto', padding: '0.8rem' }}>

                        {mcqSection.length > 0 && (

                            <div style={{ marginBottom: '0.8rem' }}>

                                <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: 'white', background: '#1a5276', padding: '3px 8px', borderRadius: 5, marginBottom: 8 }}>MCQ Section</div>

                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 5 }}>

                                    {allQs.map((q, idx) => {

                                        if (q.type !== 'mcq') return null;

                                        const st = getQStatus(idx);

                                        return (

                                            <button key={idx} onClick={() => goToQuestion(idx)}

                                                style={{ width: '100%', aspectRatio: '1', borderRadius: '50%', fontWeight: 700, fontSize: '0.72rem', cursor: 'pointer', border: 'none', ...statusStyle(st) }}>

                                                {idx + 1}

                                            </button>

                                        );

                                    })}

                                </div>

                            </div>

                        )}

                        {codingSection.length > 0 && (

                            <div>

                                <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: 'white', background: '#1a5276', padding: '3px 8px', borderRadius: 5, marginBottom: 8 }}>Coding Section</div>

                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 5 }}>

                                    {allQs.map((q, idx) => {

                                        if (q.type !== 'coding') return null;

                                        const st = getQStatus(idx);

                                        return (

                                            <button key={idx} onClick={() => goToQuestion(idx)}

                                                style={{ width: '100%', aspectRatio: '1', borderRadius: '50%', fontWeight: 700, fontSize: '0.72rem', cursor: 'pointer', border: 'none', ...statusStyle(st) }}>

                                                {idx + 1}

                                            </button>

                                        );

                                    })}

                                </div>

                            </div>

                        )}

                    </div>

                </div>

            </div>



            {/* BOTTOM ACTION BAR */}

            <div style={{ flexShrink: 0, background: 'white', borderTop: '1px solid #e5e7eb', padding: '0.6rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>

                <div style={{ display: 'flex', gap: '0.5rem' }}>

                    <button onClick={handleMarkForReview}

                        style={{ padding: '0.5rem 1rem', background: 'white', border: '1.5px solid #a855f7', color: '#a855f7', borderRadius: 8, fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer', fontFamily: 'Poppins' }}>

                        Mark for Review &amp; Next

                    </button>

                    <button onClick={handleClearResponse}

                        style={{ padding: '0.5rem 1rem', background: 'white', border: '1.5px solid #e5e7eb', color: '#374151', borderRadius: 8, fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer', fontFamily: 'Poppins' }}>

                        Clear Response

                    </button>

                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>

                    {currentQuestionIdx > 0 && (

                        <button onClick={() => goToQuestion(currentQuestionIdx - 1)}

                            style={{ padding: '0.5rem 1rem', background: 'white', border: '1.5px solid #1a5276', color: '#1a5276', borderRadius: 8, fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer', fontFamily: 'Poppins' }}>

                            Previous

                        </button>

                    )}

                    {!isLastQ && (

                        <button onClick={handleSaveAndNext}

                            style={{ padding: '0.5rem 1.2rem', background: '#1a5276', color: 'white', border: 'none', borderRadius: 8, fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer', fontFamily: 'Poppins' }}>

                            Save &amp; Next

                        </button>

                    )}

                    {isLastQ && (

                        <button onClick={handleSubmit} disabled={isSubmitting}

                            style={{ padding: '0.5rem 1.5rem', background: '#16a34a', color: 'white', border: 'none', borderRadius: 8, fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer', fontFamily: 'Poppins', opacity: isSubmitting ? 0.7 : 1 }}>

                            {isSubmitting ? 'Submitting...' : 'Submit'}

                        </button>

                    )}

                </div>

            </div>

        </div>

    );

};



export default AiTakeAssessment;

