import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Editor from "@monaco-editor/react";
import '../styles/Dashboard.css';

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

    // IDE
    const [codeOutput, setCodeOutput] = useState([]);
    const [isExecuting, setIsExecuting] = useState(false);
    const [selectedLanguage, setSelectedLanguage] = useState('javascript');
    const [customInput, setCustomInput] = useState('');
    const [executionResult, setExecutionResult] = useState(null);
    const [codingResults, setCodingResults] = useState({}); // { qId: { passed, total } }

    const supportedLanguages = [
        { id: 'javascript', name: 'JavaScript', version: '18.15.0' },
        { id: 'python', name: 'Python', version: '3.10.0' },
        { id: 'cpp', name: 'C++', version: '10.2.0' },
        { id: 'java', name: 'Java', version: '15.0.2' }
    ];

    const formatText = (text) => {
        if (!text) return '';
        return text.replace(/\n/g, '<br />');
    };

    const videoRef = useRef(null);
    const streamRef = useRef(null);
    const detectorRef = useRef(null);
    const lastDetectionTimeRef = useRef(0);
    const timerRef = useRef(null);

    useEffect(() => {
        const fetchAssessment = async () => {
            try {
                const response = await axios.get(`http://localhost:8001/api/ai/public/${token}/`);
                const data = response.data;
                setAssessment(data);

                // Availability Window Check
                const now = new Date();
                const from = data.available_from ? new Date(data.available_from) : null;
                const until = data.available_until ? new Date(data.available_until) : null;

                if (from && now < from) {
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
    }, [token]);

    const handleAnswerChange = (key, val) => {
        setAnswers(prev => ({ ...prev, [key]: val }));
        setAnsweredQs(prev => new Set([...prev, currentQuestionIdx]));
    };

    const startAssessment = async () => {
        if (!candidateName || !candidateEmail) { alert('Please provide your name and email.'); return; }
        try {
            const res = await axios.post('http://localhost:8001/api/ai/submit/create/', {
                share_token: token, candidate_name: candidateName, candidate_email: candidateEmail
            });
            setSubmissionId(res.data.submission_id);
            setIsStarted(true);
            setTimeLeft(assessment.duration_minutes * 60);
            await startCamera();
        } catch (err) {
            const msg = err.response?.data?.error || 'Failed to start assessment.';
            alert(msg);
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
            const results = [];
            let passedCount = 0;
            for (const tc of currentQ.test_cases) {
                try {
                    const r = await axios.post('http://localhost:8001/api/ai/execute/', {
                        language: selectedLanguage, version: langData.version,
                        files: [{ content: code }], stdin: tc.input
                    });
                    const out = (r.data.run.stdout || r.data.run.stderr || '').trim();
                    const exp = (tc.output || '').trim();
                    const passed = out === exp;
                    if (passed) passedCount++;
                    results.push({ input: tc.input, expected: exp, actual: out, passed });
                } catch { results.push({ input: tc.input, expected: tc.output || '', actual: 'Error', passed: false }); }
            }
            setExecutionResult({ type: 'test_cases', results, score: passedCount, total: currentQ.test_cases.length });
            setCodingResults(prev => ({ ...prev, [qId]: { passed: passedCount, total: currentQ.test_cases.length } }));
            setIsExecuting(false);
            return;
        }

        // If Submit Code but NO test cases available — show message and fall through to plain run
        if (isTestRun && (!currentQ?.test_cases || currentQ.test_cases.length === 0)) {
            setCodeOutput([{ type: 'info', content: '⚠️ No hidden test cases found for this question. Running your code with custom input instead...' }]);
        }

        setCodeOutput([{ type: 'info', content: `Running ${selectedLanguage}...` }]);
        try {
            const r = await axios.post('http://localhost:8001/api/ai/execute/', {
                language: selectedLanguage, version: langData.version,
                files: [{ content: code }], stdin: customInput
            });
            const { run } = r.data;
            const logs = [];
            if (run.stdout) logs.push({ type: 'log', content: run.stdout });
            if (run.stderr) logs.push({ type: 'error', content: run.stderr });
            logs.push({ type: run.code === 0 && !run.stderr ? 'success' : 'error', content: `Exit code: ${run.code}` });
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

    const reportViolation = async (eventType) => {
        if (!submissionId) return;
        try { await axios.post(`http://localhost:8001/api/ai/submission/${submissionId}/integrity/`, { event_type: eventType }); } catch { }
    };

    const showAiEvent = (text, urgent = false, eventType = null) => {
        setAiToast({ active: true, text, urgent });
        if (eventType) reportViolation(eventType);
        setTimeout(() => setAiToast({ active: false, text: '', urgent: false }), 3000);
    };

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
    }, [isStarted, submissionId]);

    useEffect(() => {
        if (isStarted && timeLeft > 0) {
            timerRef.current = setInterval(() => setTimeLeft(p => p - 1), 1000);
        } else if (timeLeft === 0) {
            clearInterval(timerRef.current);
            handleSubmit();
        }
        return () => clearInterval(timerRef.current);
    }, [isStarted, timeLeft]);

    useEffect(() => {
        setCodeOutput([]);
        setExecutionResult(null);

        // Auto-populate custom input with sample case for coding challenges
        const mcqs = assessment?.generated_content?.mcqs || [];
        const coding = assessment?.generated_content?.coding_challenges || [];
        const allQs = [...mcqs.map((q, i) => ({ ...q, type: 'mcq', id: i })), ...coding.map((c, i) => ({ ...c, type: 'coding', id: i }))];
        const cQ = allQs[currentQuestionIdx];

        if (cQ?.type === 'coding') {
            const sampleInput = cQ.example_input || cQ.examples?.[0]?.input || '';
            setCustomInput(sampleInput.trim());
        } else {
            setCustomInput('');
        }
    }, [currentQuestionIdx, assessment]);

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
            await axios.post('http://localhost:8001/api/ai/submit/', {
                token,
                name: candidateName,
                email: candidateEmail,
                answers,
                codingResults // Added to send test case results
            });
            setSubmitted(true);
            stopCamera();
        } catch { alert('Failed to submit.'); }
        finally { setIsSubmitting(false); }
    };

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
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: 12, border: '1px solid #E0E5F2', outline: 'none', fontSize: '0.95rem', fontFamily: 'Poppins', boxSizing: 'border-box', color: '#1B254B' }} />
                        </div>
                        <div>
                            <label style={{ display: 'block', fontWeight: 700, color: '#1B254B', marginBottom: 6, fontSize: '0.85rem' }}>Email Address *</label>
                            <input type="email" value={candidateEmail} onChange={e => setCandidateEmail(e.target.value)} placeholder="Enter your email"
                                style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: 12, border: '1px solid #E0E5F2', outline: 'none', fontSize: '0.95rem', fontFamily: 'Poppins', boxSizing: 'border-box', color: '#1B254B' }} />
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

    const mcqs = assessment?.generated_content?.mcqs || [];
    const codingChallenges = assessment?.generated_content?.coding_challenges || [];
    const allQs = [
        ...mcqs.map((q, i) => ({ ...q, type: 'mcq', id: i })),
        ...codingChallenges.map((c, i) => ({ ...c, type: 'coding', id: i }))
    ];
    const currentQ = allQs[currentQuestionIdx];
    const isLastQ = currentQuestionIdx === allQs.length - 1;
    const currentAnswerKey = currentQ.type === 'mcq' ? `mcq_${currentQ.id}` : `coding_${currentQ.id}`;

    const mcqSection = allQs.filter(q => q.type === 'mcq');
    const codingSection = allQs.filter(q => q.type === 'coding');

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
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: '#f0fdf4', display: 'flex', flexDirection: 'column', overflow: 'hidden', fontFamily: 'Poppins' }}>

            {aiToast.active && (
                <div style={{ position: 'fixed', top: 100, left: '50%', transform: 'translateX(-50%)', zIndex: 99999, background: aiToast.urgent ? '#dc2626' : '#1d4ed8', color: 'white', padding: '10px 24px', borderRadius: 25, fontWeight: 700, fontSize: '0.82rem', boxShadow: '0 6px 24px rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', gap: 8, letterSpacing: 0.5 }}>
                    <span style={{ fontSize: '1rem' }}>{aiToast.urgent ? '' : ''}</span>
                    {aiToast.text}
                </div>
            )}

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
                                        {currentQ.constraints?.length > 0 && (
                                            <div style={{ marginBottom: '0.8rem' }}>
                                                <div style={{ fontSize: '0.62rem', fontWeight: 800, textTransform: 'uppercase', color: '#374151', marginBottom: 4 }}>Constraints</div>
                                                <ul style={{ margin: 0, paddingLeft: '1rem', color: '#6b7280', fontSize: '0.75rem' }}>
                                                    {currentQ.constraints.map((c, i) => <li key={i}>{c}</li>)}
                                                </ul>
                                            </div>
                                        )}
                                        {(currentQ.example_input || currentQ.examples?.length > 0) && (
                                            <div>
                                                <div style={{ fontSize: '0.62rem', fontWeight: 800, textTransform: 'uppercase', color: '#374151', marginBottom: 5 }}>Sample Case</div>
                                                <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, overflow: 'hidden', background: '#f9fafb' }}>
                                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
                                                        <div style={{ padding: '6px 8px', borderRight: '1px solid #e5e7eb' }}>
                                                            <div style={{ fontSize: '0.6rem', color: '#1d4ed8', fontWeight: 700, marginBottom: 2 }}>INPUT</div>
                                                            <pre style={{ margin: 0, fontSize: '0.75rem', fontFamily: 'monospace', color: '#111827', whiteSpace: 'pre-wrap' }}>
                                                                {currentQ.example_input || currentQ.examples?.[0]?.input}
                                                            </pre>
                                                        </div>
                                                        <div style={{ padding: '6px 8px' }}>
                                                            <div style={{ fontSize: '0.6rem', color: '#16a34a', fontWeight: 700, marginBottom: 2 }}>OUTPUT</div>
                                                            <pre style={{ margin: 0, fontSize: '0.75rem', fontFamily: 'monospace', color: '#111827', whiteSpace: 'pre-wrap' }}>
                                                                {currentQ.example_output || currentQ.examples?.[0]?.output}
                                                            </pre>
                                                        </div>
                                                    </div>
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
                                        <Editor height="100%" language={selectedLanguage} theme="vs-dark"
                                            value={answers[currentAnswerKey] || currentQ[`starter_code_${selectedLanguage}`] || (() => {
                                                const defaultComments = { python: '# Write your code here\n', java: '// Write your code here\n', cpp: '// Write your code here\n', javascript: '// Write your code here\n' };
                                                const raw = currentQ.starter_code;
                                                // If backend starter code is just a JS-style placeholder comment, replace with language-correct one
                                                if (!raw || raw.trim() === '// Write your code here') return defaultComments[selectedLanguage] || '# Write your code here\n';
                                                return raw;
                                            })()}
                                            onChange={val => handleAnswerChange(currentAnswerKey, val)}
                                            options={{ fontSize: 13, minimap: { enabled: false }, scrollBeyondLastLine: false, automaticLayout: true, padding: { top: 10 }, lineNumbers: 'on' }} />
                                    </div>
                                    <div style={{ flexShrink: 0, height: 110, borderTop: '1px solid #2d2d2d', background: '#0d0d1a', display: 'flex', flexDirection: 'column' }}>
                                        <div style={{ padding: '3px 10px', background: '#1a1a2e', borderBottom: '1px solid #2d2d2d', fontSize: '0.65rem', fontWeight: 700, color: '#6b7280', textTransform: 'uppercase' }}>Console Output</div>
                                        <div style={{ flex: 1, overflowY: 'auto', padding: '5px 10px', fontFamily: 'Courier New, monospace', fontSize: '0.78rem' }}>
                                            {executionResult?.type === 'test_cases' ? (
                                                <div>
                                                    <div style={{ fontWeight: 800, color: executionResult.score === executionResult.total ? '#22c55e' : '#ef4444', marginBottom: 4 }}>
                                                        {executionResult.score}/{executionResult.total} test cases passed
                                                    </div>
                                                    {executionResult.results.map((r, i) => (
                                                        <div key={i} style={{ fontSize: '0.72rem', color: r.passed ? '#22c55e' : '#ef4444', marginBottom: 1 }}>
                                                            {r.passed ? 'PASS' : 'FAIL'} TC{i + 1}
                                                            {!r.passed && <span style={{ color: '#888' }}> expected: {String(r.expected || '').substring(0, 30)} got: {String(r.actual || '').substring(0, 30)}</span>}
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
