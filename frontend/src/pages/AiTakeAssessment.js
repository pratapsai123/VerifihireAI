import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Editor from "@monaco-editor/react";
import '../styles/Dashboard.css';
import { API_BASE_URL } from '../apiConfig';

const AiTakeAssessment = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [assessment, setAssessment] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [answers, setAnswers] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    // Intake
    const [candidateName, setCandidateName] = useState('');
    const [candidateEmail, setCandidateEmail] = useState('');
    const [isAutoFilled, setIsAutoFilled] = useState(false);
    const [submissionId, setSubmissionId] = useState(null);
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
            // 1. Save current code to draft BEFORE switching
            const currentCode = answers[qKey] || '';
            const draftKeyForOldLang = `${qKey}_${currentLang}`;

            // 2. Determine what code should be in the editor for the NEW language
            const nextDraftKey = `${qKey}_${lang}`;
            let nextCode = codeDrafts[nextDraftKey];

            if (nextCode === undefined) {
                // If no draft exists, check starter_code or fallbacks
                const qIdx = parseInt(qKey.replace('coding_', ''), 10);
                const q = assessment?.generated_content?.coding_challenges?.[qIdx];
                if (q) {
                    if (q.starter_code && typeof q.starter_code === 'object' && q.starter_code[lang]) {
                        nextCode = formatCode(q.starter_code[lang]);
                    } else if (q[`starter_code_${lang}`]) {
                        nextCode = formatCode(q[`starter_code_${lang}`]);
                    } else {
                        nextCode = DEFAULT_BOILERPLATES[lang] || '# Write logic here\n';
                    }
                } else {
                    nextCode = DEFAULT_BOILERPLATES[lang] || '# Write logic here\n';
                }
            }

            // Update everything together to avoid race conditions
            setAnswers(prev => ({ ...prev, [qKey]: nextCode }));
            setCodeDrafts(prev => ({
                ...prev,
                [draftKeyForOldLang]: currentCode,
                [nextDraftKey]: nextCode // Ensure the draft is also initialized so we don't reload starter next time
            }));
        }

        _setSelectedLanguage(lang);
    };
    const [customInput, setCustomInput] = useState('');
    const [executionResult, setExecutionResult] = useState(null);
    const [codingResults, setCodingResults] = useState({}); // { qId: { passed, total } }

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
        return text.replace(/\n/g, '<br />');
    };

    const videoRef = useRef(null);
    const streamRef = useRef(null);
    const detectorRef = useRef(null);
    const lastDetectionTimeRef = useRef(0);
    const screenStreamRef = useRef(null);
    const screenCanvasRef = useRef(null);
    const timerRef = useRef(null);
    const handleSubmitRef = useRef(null); // always points to latest handleSubmit
    const mcqSection = React.useMemo(() => assessment?.generated_content?.mcqs || [], [assessment]);
    const codingSection = React.useMemo(() => assessment?.generated_content?.coding_challenges || [], [assessment]);
    const allQs = React.useMemo(() => [
        ...mcqSection.map((q, i) => ({ ...q, type: 'mcq', id: i })),
        ...codingSection.map((c, i) => ({ ...c, type: 'coding', id: i }))
    ], [mcqSection, codingSection]);

    const currentQ = allQs[currentQuestionIdx] || allQs[0];
    const currentAnswerKey = currentQ?.type === 'mcq' ? `mcq_${currentQ?.id}` : `coding_${currentQ?.id}`;
    const isLastQ = currentQuestionIdx === allQs.length - 1;

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const nameParam = params.get('name');
        const emailParam = params.get('email');
        if (nameParam || emailParam) {
            if (nameParam) setCandidateName(nameParam);
            if (emailParam) setCandidateEmail(emailParam);
            setIsAutoFilled(true);
        }
    }, []);

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

    const handleAnswerChange = (key, val) => {
        setAnswers(prev => ({ ...prev, [key]: val }));

        // Also update draft if this is a coding question
        if (key.startsWith('coding_')) {
            setCodeDrafts(prev => ({ ...prev, [`${key}_${selectedLanguage}`]: val }));
        }

        setAnsweredQs(prev => new Set([...prev, currentQuestionIdx]));
    };

    const startAssessment = async () => {
        if (!candidateName || !candidateEmail) { alert('Please provide your name and email.'); return; }
        try {
            const res = await axios.post(`${API_BASE_URL}/ai/submit/create/`, {
                share_token: token, candidate_name: candidateName, candidate_email: candidateEmail
            });
            const { submission_id, time_left, answers: savedAnswers, current_question_index, codingResults: savedResults, codeDrafts: savedDrafts } = res.data;

            setSubmissionId(submission_id);
            if (savedResults) setCodingResults(savedResults);
            if (savedDrafts) setCodeDrafts(savedDrafts);
            setIsStarted(true);

            // Restore session if resumed
            if (savedAnswers && Object.keys(savedAnswers).length > 0) {
                setAnswers(savedAnswers);

                // Rebuild answeredQs and visitedQs from saved answer keys
                // Keys are like 'mcq_0', 'mcq_3', 'coding_0' — extract the index from the key
                const mcqsArr = assessment?.generated_content?.mcqs || [];
                const totalMcqs = mcqsArr.length;

                const restoredAnswered = new Set();
                const restoredVisited = new Set();

                Object.keys(savedAnswers).forEach(key => {
                    const val = savedAnswers[key];
                    if (!val) return; // skip empty/null answers
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

            // Sync timer
            setTimeLeft(time_left !== undefined ? time_left : assessment.duration_minutes * 60);

            // Mandatory Screen Share
            const success = await startScreenShare();
            if (!success) {
                setIsStarted(false);
                return;
            }

            await startCamera();
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
            };
            return true;
        } catch (err) {
            alert('Screen sharing (Entire Screen) is required to start the test.');
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
                    const tcInput = tc.input || tc.input_data || tc.stdin || '';
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
                        const passed = out === exp;
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
            // Capture Screen
            if (['tab_switch', 'window_blur', 'window_switch'].includes(eventType) && screenStreamRef.current && screenCanvasRef.current) {
                try {
                    const video = document.createElement('video');
                    video.srcObject = screenStreamRef.current;
                    video.muted = true;
                    video.playsInline = true;

                    await new Promise((resolve, reject) => {
                        video.onloadedmetadata = () => {
                            video.play()
                                .then(() => {
                                    setTimeout(resolve, 100);
                                })
                                .catch(reject);
                        };
                        video.onerror = reject;
                    });

                    const canvas = screenCanvasRef.current;
                    const ctx = canvas.getContext('2d');
                    canvas.width = video.videoWidth || 1280;
                    canvas.height = video.videoHeight || 720;
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    screenshot = canvas.toDataURL('image/jpeg', 0.5);

                    video.pause();
                    video.srcObject = null;
                } catch (e) {
                    console.error('Failed to capture AI integrity snapshot', e);
                }
            }

            // Capture Webcam
            if (['multiface_detection', 'phone_detection', 'face_detection_lost', 'face_detection_lost_rechecked'].includes(eventType) && videoRef.current && videoRef.current.readyState >= 2) {
                try {
                    const camCanvas = document.createElement('canvas');
                    camCanvas.width = videoRef.current.videoWidth || 640;
                    camCanvas.height = videoRef.current.videoHeight || 480;
                    const ctx = camCanvas.getContext('2d');
                    ctx.drawImage(videoRef.current, 0, 0, camCanvas.width, camCanvas.height);
                    webcamScreenshot = camCanvas.toDataURL('image/jpeg', 0.5);
                } catch (e) {
                    console.error('Failed to capture AI webcam snapshot', e);
                }
            }

            reportViolation(eventType, screenshot, webcamScreenshot);
        }

        setTimeout(() => setAiToast({ active: false, text: '', urgent: false }), 3000);
    }, [reportViolation]);

    useEffect(() => {
        if (!isStarted || !submissionId) return;
        let detectInterval;
        const initMonitoring = async () => {
            if (window.cocoSsd) {
                detectorRef.current = await window.cocoSsd.load();
                detectInterval = setInterval(async () => {
                    if (videoRef.current && detectorRef.current && videoRef.current.readyState === 4) {
                        const now = Date.now();
                        if (now - lastDetectionTimeRef.current > 2000) {
                            lastDetectionTimeRef.current = now;
                            const preds = await detectorRef.current.detect(videoRef.current);
                            if (preds.find(p => p.class === 'cell phone')) showAiEvent('PHONE DETECTED', true, 'phone_detection');
                            const people = preds.filter(p => p.class === 'person');
                            if (people.length > 1) showAiEvent('MULTIPLE PEOPLE', true, 'multiface_detection');
                            else if (people.length === 0) showAiEvent('FACE NOT DETECTED', true, 'face_detection_lost');
                        }
                    }
                }, 1000);
            }
        };
        const onHide = () => { if (document.hidden) showAiEvent('TAB SWITCHED', true, 'tab_switch'); };
        const onBlur = () => showAiEvent('WINDOW BLURRED', true, 'tab_switch');
        document.addEventListener('visibilitychange', onHide);
        window.addEventListener('blur', onBlur);

        initMonitoring();
        return () => {
            clearInterval(detectInterval);
            document.removeEventListener('visibilitychange', onHide);
            window.removeEventListener('blur', onBlur);
            stopCamera();
        };
    }, [isStarted, submissionId, showAiEvent]);

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
                    codingResults: codingResults,
                    codeDrafts: codeDrafts
                });
            } catch (err) {
                console.error("Failed to save progress", err);
            }
        };

        // Store reference so unload handler can call it
        saveProgressRef.current = { answers, currentQuestionIdx, submissionId, codingResults };

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
                codingResults: ctx.codingResults,
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
                if (q.starter_code && typeof q.starter_code === 'object') {
                    Object.entries(q.starter_code).forEach(([lang, code]) => {
                        const dKey = `${qKey}_${lang.toLowerCase()}`;
                        if (nextDrafts[dKey] === undefined && code) {
                            nextDrafts[dKey] = formatCode(code);
                            changed = true;
                        }
                    });
                }
                // Also check old format
                supportedLanguages.forEach(sl => {
                    const dKey = `${qKey}_${sl.id}`;
                    const oldKey = `starter_code_${sl.id}`;
                    if (nextDrafts[dKey] === undefined && q[oldKey]) {
                        nextDrafts[dKey] = formatCode(q[oldKey]);
                        changed = true;
                    }
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
                codingResults: codingResults,
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
            await axios.post(`${API_BASE_URL}/ai/submit/`, {
                token,
                name: candidateName,
                email: candidateEmail,
                answers,
                codingResults // Added to send test case results
            });
            // Mark as completed locally to prevent re-opening link later
            localStorage.setItem(`assessment_completed_${token}`, 'true');
            setSubmitted(true);
            stopCamera();
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
                    </div>
                    <div style={{ background: '#FFF8E6', border: '1px solid #FFA800', borderRadius: 12, padding: '0.9rem 1rem', marginBottom: '1.5rem', fontSize: '0.82rem', color: '#1B254B' }}>
                        <strong>⚠️ Warning:</strong> This test uses AI video monitoring. Switching tabs or leaving the window will be flagged as malpractice.
                    </div>
                    <button onClick={startAssessment}
                        style={{ width: '100%', padding: '0.9rem', background: '#4318FF', color: 'white', border: 'none', borderRadius: 12, fontSize: '1rem', fontWeight: 700, cursor: 'pointer', fontFamily: 'Poppins', boxShadow: '0 10px 20px rgba(67,24,255,0.2)', transition: 'all 0.2s' }}>
                        Start Test
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
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 25, padding: '4px 12px 4px 4px' }}>
                        <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#1a5276', overflow: 'hidden', flexShrink: 0 }}>
                            <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                        </div>
                        <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#374151' }}>{candidateName}</span>
                    </div>
                </div>
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
                        <span style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600 }}>
                            Marks for Correct Answer <span style={{ color: '#16a34a', fontWeight: 700 }}>1.00</span>
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
                                    {currentQ.options?.map((opt, i) => {
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
                                        <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', fontWeight: 800, color: '#1a5276', letterSpacing: 0.8, marginBottom: 6 }}>Problem Statement</div>
                                        <h3 style={{ fontSize: '0.93rem', fontWeight: 800, color: '#111827', margin: '0 0 0.6rem', lineHeight: 1.4 }}>
                                            {currentQ.title || `Challenge ${currentQ.id + 1}`}
                                        </h3>
                                        <div style={{ color: '#374151', fontSize: '0.82rem', lineHeight: 1.65, marginBottom: '0.8rem' }}>
                                            {currentQ.problem_statement
                                                ? <div dangerouslySetInnerHTML={{ __html: formatText(currentQ.problem_statement) }} />
                                                : <p style={{ margin: 0 }}>{currentQ.description || 'No description.'}</p>}
                                        </div>
                                        {(currentQ.input_format || currentQ.output_format) && (
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem', marginBottom: '0.8rem' }}>
                                                {currentQ.input_format && (
                                                    <div style={{ background: '#eff6ff', padding: '6px 8px', borderRadius: 7 }}>
                                                        <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#1d4ed8', marginBottom: 2 }}>INPUT FORMAT</div>
                                                        <div style={{ fontSize: '0.75rem', color: '#1e3a8a' }}>{currentQ.input_format}</div>
                                                    </div>
                                                )}
                                                {currentQ.output_format && (
                                                    <div style={{ background: '#f0fdf4', padding: '6px 8px', borderRadius: 7 }}>
                                                        <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#16a34a', marginBottom: 2 }}>OUTPUT FORMAT</div>
                                                        <div style={{ fontSize: '0.75rem', color: '#14532d' }}>{currentQ.output_format}</div>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                        {currentQ.constraints && (Array.isArray(currentQ.constraints) ? currentQ.constraints.length > 0 : String(currentQ.constraints).length > 0) && (
                                            <div style={{ marginBottom: '0.8rem' }}>
                                                <div style={{ fontSize: '0.62rem', fontWeight: 800, textTransform: 'uppercase', color: '#374151', marginBottom: 4 }}>Constraints</div>
                                                <ul style={{ margin: 0, paddingLeft: '1rem', color: '#6b7280', fontSize: '0.75rem' }}>
                                                    {Array.isArray(currentQ.constraints)
                                                        ? currentQ.constraints.map((c, i) => <li key={i}>{c}</li>)
                                                        : <li>{currentQ.constraints}</li>
                                                    }
                                                </ul>
                                            </div>
                                        )}
                                        {(currentQ.test_cases?.length > 0 || currentQ.example_input) && (
                                            <div style={{ marginBottom: '1rem' }}>
                                                <div style={{ fontSize: '0.62rem', fontWeight: 800, textTransform: 'uppercase', color: '#374151', marginBottom: 8 }}>Sample Cases</div>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                                    {((currentQ.test_cases && currentQ.test_cases.length > 0) ? currentQ.test_cases.slice(0, 2) :
                                                        (currentQ.example_input ? [{ input: currentQ.example_input, output: currentQ.example_output }] : [])
                                                    ).map((tc, idx) => (
                                                        <div key={idx} style={{ background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 8, padding: '10px' }}>
                                                            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: '#1d4ed8', marginBottom: 6, textTransform: 'uppercase' }}>Case {idx + 1}</div>
                                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 15 }}>
                                                                <div>
                                                                    <div style={{ fontSize: '0.55rem', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', marginBottom: 2 }}>Input</div>
                                                                    <pre style={{ margin: 0, fontSize: '0.72rem', color: '#334155', whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                                                                        {typeof tc.input === 'object' ? JSON.stringify(tc.input, null, 2) : String(tc.input || tc.input_data || '').trim()}
                                                                    </pre>
                                                                </div>
                                                                <div>
                                                                    <div style={{ fontSize: '0.55rem', fontWeight: 800, color: '#94a3b8', textTransform: 'uppercase', marginBottom: 2 }}>Output</div>
                                                                    <pre style={{ margin: 0, fontSize: '0.72rem', color: '#334155', whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                                                                        {typeof tc.output === 'object' ? JSON.stringify(tc.output, null, 2) : String(tc.output || tc.expected_output || '').trim()}
                                                                    </pre>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
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
