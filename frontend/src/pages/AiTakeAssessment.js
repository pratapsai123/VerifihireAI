import React, { useState, useEffect, useRef, useCallback } from 'react';
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

    // Intake & Session State
    const [candidateName, setCandidateName] = useState('');
    const [candidateEmail, setCandidateEmail] = useState('');
    const [submissionId, setSubmissionId] = useState(null);
    const [timeLeft, setTimeLeft] = useState(null);
    const [isStarted, setIsStarted] = useState(false);

    // Monitoring State
    const [aiStatus, setAiStatus] = useState('Monitoring Stopped');
    const [aiToast, setAiToast] = useState({ active: false, text: '', urgent: false });

    // IDE State
    const [codeOutput, setCodeOutput] = useState([]);
    const [isExecuting, setIsExecuting] = useState(false);
    const [selectedLanguage, setSelectedLanguage] = useState('javascript');
    const [customInput, setCustomInput] = useState('');

    const supportedLanguages = [
        { id: 'javascript', name: 'JavaScript', version: '18.15.0', icon: 'fa-brands fa-js', color: '#F7DF1E' },
        { id: 'python', name: 'Python', version: '3.10.0', icon: 'fa-brands fa-python', color: '#3776AB' },
        { id: 'cpp', name: 'C++', version: '10.2.0', icon: 'fa-solid fa-code', color: '#00599C' },
        { id: 'java', name: 'Java', version: '15.0.2', icon: 'fa-brands fa-java', color: '#007396' }
    ];

    // Refs
    const videoRef = useRef(null);
    const streamRef = useRef(null);
    const detectorRef = useRef(null);
    const lastDetectionTimeRef = useRef(0);
    const timerRef = useRef(null);

    useEffect(() => {
        const fetchAssessment = async () => {
            try {
                const response = await axios.get(`http://localhost:8001/api/ai/public/${token}/`);
                setAssessment(response.data);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching assessment:', err);
                setError('Invalid or expired assessment link.');
                setLoading(false);
            }
        };

        fetchAssessment();
    }, [token]);

    const handleAnswerChange = (qIndex, answer) => {
        setAnswers(prev => ({
            ...prev,
            [qIndex]: answer
        }));
    };

    const startAssessment = async () => {
        if (!candidateName || !candidateEmail) {
            alert('Please provide your name and email.');
            return;
        }

        try {
            const res = await axios.post('http://localhost:8001/api/ai/submit/create/', {
                share_token: token,
                candidate_name: candidateName,
                candidate_email: candidateEmail
            });
            setSubmissionId(res.data.submission_id);
            setIsStarted(true);
            setTimeLeft(assessment.duration_minutes * 60);
            await startCamera();
        } catch (err) {
            console.error('Intake error:', err);
            alert('Failed to start assessment. Please check your connection.');
        }
    };

    const runCode = async (qId) => {
        const code = answers[`coding_${qId}`] || "";
        if (!code.trim()) return;

        setIsExecuting(true);
        setCodeOutput([{ type: 'info', content: `Compiling & running ${selectedLanguage}...` }]);

        try {
            const langData = supportedLanguages.find(l => l.id === selectedLanguage);
            const response = await axios.post('https://emkc.org/api/v2/piston/execute', {
                language: selectedLanguage === 'cpp' ? 'cpp' : selectedLanguage,
                version: langData.version,
                files: [{ content: code }],
                stdin: customInput
            });

            const { run } = response.data;
            const logs = [];

            if (run.stdout) {
                logs.push({ type: 'log', content: run.stdout });
            }
            if (run.stderr) {
                logs.push({ type: 'error', content: run.stderr });
            }

            if (run.code === 0 && !run.stderr) {
                logs.push({ type: 'success', content: `Execution successful (Exit Code 0).` });
            } else {
                logs.push({ type: 'error', content: `Exited with code ${run.code}.` });
            }

            setCodeOutput(logs);
        } catch (err) {
            setCodeOutput([{ type: 'error', content: `Connection Error: Failed to reach execution engine.` }]);
            console.error(err);
        } finally {
            setIsExecuting(false);
        }
    };

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                // Explicitly call play to handle stricter browser policies
                videoRef.current.play().catch(e => console.warn("Camera play blocked:", e));
            }
            streamRef.current = stream;
        } catch (err) {
            console.error("Camera error:", err);
            setAiToast({ active: true, text: 'Camera Access Denied', urgent: true });
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
    };

    const reportViolation = async (eventType) => {
        if (!submissionId) return;
        try {
            await axios.post(`http://localhost:8001/api/ai/submission/${submissionId}/integrity/`, {
                event_type: eventType
            });
        } catch (err) {
            console.error("Failed to report violation:", err);
        }
    };

    const showAiEvent = (text, urgent = false, eventType = null) => {
        setAiToast({ active: true, text, urgent });
        if (eventType) reportViolation(eventType);
        setTimeout(() => setAiToast({ active: false, text: '', urgent: false }), 3000);
    };

    // Monitoring Loop
    useEffect(() => {
        if (!isStarted || !submissionId) return;

        let detectInterval;
        const initMonitoring = async () => {
            if (window.cocoSsd) {
                detectorRef.current = await window.cocoSsd.load();
                setAiStatus('Monitoring Active');
                detectInterval = setInterval(async () => {
                    if (videoRef.current && detectorRef.current && videoRef.current.readyState === 4) {
                        const now = Date.now();
                        if (now - lastDetectionTimeRef.current > 2000) {
                            lastDetectionTimeRef.current = now;
                            const predictions = await detectorRef.current.detect(videoRef.current);
                            const phone = predictions.find(p => p.class === 'cell phone');
                            if (phone) showAiEvent("PHONE DETECTED", true, 'phone_detection');
                            const people = predictions.filter(p => p.class === 'person');
                            if (people.length > 1) showAiEvent("MULTIPLE PEOPLE", true, 'multiface_detection');
                            else if (people.length === 0) showAiEvent("FACE NOT DETECTED", true, 'face_detection_lost');
                        }
                    }
                }, 1000);
            }
        };

        const handleVisibilityChange = () => {
            if (document.hidden) showAiEvent("TAB SWITCHED", true, 'tab_switch');
        };
        const handleBlur = () => showAiEvent("WINDOW BLURRED", true, 'tab_switch');

        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('blur', handleBlur);
        initMonitoring();

        return () => {
            clearInterval(detectInterval);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('blur', handleBlur);
            stopCamera();
        };
    }, [isStarted, submissionId]);

    // Timer & Pagination State
    const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);

    // Timer Loop
    useEffect(() => {
        if (isStarted && timeLeft > 0) {
            timerRef.current = setInterval(() => {
                setTimeLeft(prev => prev - 1);
            }, 1000);
        } else if (timeLeft === 0) {
            clearInterval(timerRef.current);
            handleSubmit(); // Auto-submit
        }
        return () => clearInterval(timerRef.current);
    }, [isStarted, timeLeft]);

    // Clear console when switching questions
    useEffect(() => {
        setCodeOutput([]);
    }, [currentQuestionIdx]);

    const handleNext = () => {
        const mcqs = assessment?.generated_content?.mcqs || [];
        const coding = assessment?.generated_content?.coding_challenges || [];
        const totalQs = mcqs.length + coding.length;
        if (currentQuestionIdx < totalQs - 1) {
            setCurrentQuestionIdx(prev => prev + 1);
            window.scrollTo(0, 0); // Scroll to top for new question
        }
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        setIsSubmitting(true);
        try {
            await axios.post('http://localhost:8001/api/ai/submit/', {
                token: token,
                name: candidateName,
                email: candidateEmail,
                answers: answers
            });
            setSubmitted(true);
            stopCamera();
        } catch (err) {
            console.error('Submission error:', err);
            alert('Failed to submit assessment.');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (loading) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins' }}>
            <div style={{ textAlign: 'center' }}>
                <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', color: '#4318FF', marginBottom: '1rem' }}></i>
                <p>Loading assessment...</p>
            </div>
        </div>
    );

    if (error) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins' }}>
            <div style={{ textAlign: 'center', maxWidth: '400px', padding: '2rem', background: 'white', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
                <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '3rem', color: '#ee5d50', marginBottom: '1rem' }}></i>
                <h2>Link Error</h2>
                <p style={{ color: '#A3AED0' }}>{error}</p>
            </div>
        </div>
    );

    if (submitted) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins' }}>
            <div style={{ textAlign: 'center', maxWidth: '500px', padding: '3rem', background: 'white', borderRadius: '30px', boxShadow: '0 20px 50px rgba(0,0,0,0.05)' }}>
                <div style={{ width: '80px', height: '80px', background: '#E6FBF5', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#05CD99', fontSize: '2.5rem', margin: '0 auto 1.5rem' }}>
                    <i className="fa-solid fa-check"></i>
                </div>
                <h1 style={{ color: '#1B254B', marginBottom: '1rem' }}>Assessment Submitted!</h1>
                <p style={{ color: '#A3AED0', fontSize: '1.1rem' }}>Thank you for completing the test. The recruiter has been notified of your submission.</p>
            </div>
        </div>
    );

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    };

    if (!isStarted) return (
        <div style={{ background: '#F4F7FE', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', fontFamily: 'Poppins', padding: '20px' }}>
            <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '3rem', background: 'white', borderRadius: '30px', boxShadow: '0 20px 50px rgba(0,0,0,0.05)' }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div style={{ width: '70px', height: '70px', background: '#F4F7FE', borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem', color: '#4318FF', fontSize: '1.8rem' }}>
                        <i className="fa-solid fa-user-pen"></i>
                    </div>
                    <h1 style={{ color: '#1B254B', fontSize: '2rem', fontWeight: '700', marginBottom: '0.2rem' }}>Candidate Intake</h1>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#707EAE', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                        <i className="fa-regular fa-clock"></i>
                        <span>Generated on: <strong>{assessment.created_at}</strong></span>
                    </div>
                    <p style={{ color: '#A3AED0' }}>Please fill in your details to begin the technical assessment.</p>
                </div>

                <div style={{ display: 'grid', gap: '1.5rem', marginBottom: '2.5rem' }}>
                    <div>
                        <label style={{ color: '#1B254B', fontWeight: '600', marginBottom: '0.5rem', display: 'block' }}>Full Name</label>
                        <input
                            type="text" value={candidateName} onChange={(e) => setCandidateName(e.target.value)}
                            placeholder="Enter your full name"
                            style={{ width: '100%', padding: '1rem 1.2rem', borderRadius: '15px', border: '2px solid #E0E5F2', outline: 'none', background: '#F4F7FE', fontWeight: '500' }}
                        />
                    </div>
                    <div>
                        <label style={{ color: '#1B254B', fontWeight: '600', marginBottom: '0.5rem', display: 'block' }}>Email Address</label>
                        <input
                            type="email" value={candidateEmail} onChange={(e) => setCandidateEmail(e.target.value)}
                            placeholder="Enter your email"
                            style={{ width: '100%', padding: '1rem 1.2rem', borderRadius: '15px', border: '2px solid #E0E5F2', outline: 'none', background: '#F4F7FE', fontWeight: '500' }}
                        />
                    </div>
                </div>

                <div style={{ background: '#FFF5F5', padding: '1.2rem', borderRadius: '15px', marginBottom: '2rem', border: '1px solid #FFE4E4', display: 'flex', gap: '15px', alignItems: 'flex-start' }}>
                    <i className="fa-solid fa-shield-halved" style={{ color: '#F56565', marginTop: '3px' }}></i>
                    <p style={{ color: '#C53030', fontSize: '0.85rem', margin: '0', fontWeight: '500', lineHeight: '1.4' }}>
                        This assessment uses AI Video Monitoring. Ensure your camera is active and you remain in a well-lit area. Tab switching is strictly prohibited.
                    </p>
                </div>

                <button
                    onClick={startAssessment}
                    style={{ width: '100%', padding: '1.2rem', background: 'linear-gradient(135deg, #4318FF 0%, #7551FF 100%)', color: 'white', border: 'none', borderRadius: '18px', fontSize: '1.1rem', fontWeight: '700', cursor: 'pointer', boxShadow: '0 15px 30px rgba(67, 24, 255, 0.2)' }}
                >
                    Start Assessment
                </button>
            </div>
        </div>
    );

    const mcqs = assessment?.generated_content?.mcqs || [];
    const coding = assessment?.generated_content?.coding_challenges || [];
    const assessmentQuestions = [...mcqs.map((q, i) => ({ ...q, type: 'mcq', id: i })), ...coding.map((c, i) => ({ ...c, type: 'coding', id: i }))];
    const currentQ = assessmentQuestions[currentQuestionIdx];
    const isLastQ = assessmentQuestions.length > 0 && currentQuestionIdx === assessmentQuestions.length - 1;

    return (
        <div style={{ background: '#F4F7FE', height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', fontFamily: 'Poppins' }}>
            {/* Optimized Sticky Header */}
            <div style={{
                flexShrink: 0,
                padding: '8px 40px',
                background: 'white',
                borderBottom: '1px solid #E0E5F2',
                boxShadow: '0 2px 10px rgba(0,0,0,0.03)',
                zIndex: 1000
            }}>
                <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'grid', gridTemplateColumns: '80px 1fr 180px', gap: '1.5rem', alignItems: 'center' }}>

                    {/* Camera (Mini) */}
                    <div style={{ position: 'relative', width: '80px', aspectRatio: '4/3', background: '#000', borderRadius: '6px', overflow: 'hidden' }}>
                        <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                    </div>

                    {/* Progress & Title */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                            <h1 style={{ color: '#1B254B', margin: 0, fontSize: '1.2rem', fontWeight: '800' }}>
                                Technical Assessment <span style={{ color: '#707EAE', fontSize: '0.85rem', fontWeight: '400', marginLeft: '8px' }}>({assessment.required_skills})</span>
                            </h1>
                            <div style={{ fontSize: '0.85rem', fontWeight: '700', color: '#4318FF', background: '#F0F3FF', padding: '2px 10px', borderRadius: '5px' }}>
                                Q{currentQuestionIdx + 1}/{assessmentQuestions.length}
                            </div>
                        </div>
                        <div style={{ width: '100%', height: '5px', background: '#E0E5F2', borderRadius: '10px', overflow: 'hidden' }}>
                            <div style={{ width: `${(assessmentQuestions.length > 0 ? ((currentQuestionIdx + 1) / assessmentQuestions.length) : 0) * 100}%`, height: '100%', background: '#4318FF', transition: 'width 0.3s ease' }}></div>
                        </div>
                    </div>

                    {/* Timer & Status */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '15px' }}>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '0.6rem', color: timeLeft < 300 ? '#E53E3E' : '#707EAE', fontWeight: '700', textTransform: 'uppercase' }}>Timer</div>
                            <div style={{ fontSize: '1.2rem', fontWeight: '800', color: timeLeft < 300 ? '#E53E3E' : '#1B254B' }}>{formatTime(timeLeft)}</div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#05CD99', fontSize: '0.65rem', fontWeight: '700' }}>
                            <span style={{ width: '6px', height: '6px', background: '#05CD99', borderRadius: '50%' }}></span>
                            LIVE
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content Area - Responsive Split */}
            <div style={{ flex: 1, padding: '10px 20px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <div style={{
                    maxWidth: currentQ.type === 'mcq' ? '950px' : '100%',
                    width: '100%',
                    margin: '0 auto',
                    maxHeight: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    flex: 1
                }}>

                    {/* Question Card */}
                    <div className="card" style={{
                        flexShrink: 1,
                        background: 'white',
                        borderRadius: '25px',
                        boxShadow: '0 10px 30px rgba(0,0,0,0.04)',
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden',
                        border: '1px solid #E0E5F2'
                    }}>

                        {/* Question Content - Further Optimized */}
                        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 1.5rem' }}>
                            {currentQ.type === 'mcq' ? (
                                <div>
                                    <h2 style={{ color: '#1B254B', marginBottom: '1.2rem', fontSize: '1.2rem', fontWeight: '700', lineHeight: '1.4' }}>
                                        {currentQ.question}
                                    </h2>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                                        {currentQ.options.map((opt, optIdx) => (
                                            <label key={optIdx} style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                padding: '0.9rem 1.5rem',
                                                background: answers[`mcq_${currentQ.id}`] === opt ? '#F0F3FF' : '#F8F9FF',
                                                borderRadius: '12px',
                                                cursor: 'pointer',
                                                border: '2px solid',
                                                borderColor: answers[`mcq_${currentQ.id}`] === opt ? '#4318FF' : 'transparent',
                                                transition: 'all 0.15s'
                                            }}>
                                                <input type="radio" checked={answers[`mcq_${currentQ.id}`] === opt} onChange={() => handleAnswerChange(`mcq_${currentQ.id}`, opt)} style={{ width: '18px', height: '18px', marginRight: '12px', accentColor: '#4318FF' }} />
                                                <span style={{ color: '#1B254B', fontWeight: '600', fontSize: '0.95rem' }}>{opt}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <div style={{ height: '100%', display: 'flex', gap: '2rem' }}>

                                    {/* Left Panel: Problem Statement */}
                                    <div style={{ flex: '0 0 320px', display: 'flex', flexDirection: 'column', gap: '1rem', borderRight: '1px solid #E0E5F2', paddingRight: '1.5rem' }}>
                                        <div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.8rem' }}>
                                                <span style={{ padding: '2px 8px', background: '#F0F3FF', color: '#4318FF', borderRadius: '4px', fontSize: '0.65rem', fontWeight: '800', textTransform: 'uppercase' }}>Challenge</span>
                                                <h2 style={{ color: '#1B254B', margin: 0, fontSize: '1.1rem', fontWeight: '800' }}>{currentQ.title}</h2>
                                            </div>
                                            <div style={{ color: '#707EAE', fontSize: '0.85rem', lineHeight: '1.5', background: '#F8F9FF', padding: '1rem', borderRadius: '12px', border: '1px solid #E0E5F2' }}>
                                                {currentQ.problem_statement}
                                            </div>

                                            {/* Sample Testcases */}
                                            {currentQ.examples && currentQ.examples.length > 0 && (
                                                <div style={{ marginTop: '1rem' }}>
                                                    <div style={{ fontSize: '0.7rem', fontWeight: '800', color: '#1B254B', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Examples</div>
                                                    {currentQ.examples.map((ex, i) => (
                                                        <div key={i} style={{ background: '#F0F3FF', padding: '8px', borderRadius: '8px', marginBottom: '8px', border: '1px solid #E0E5F2' }}>
                                                            <div style={{ fontSize: '0.75rem', color: '#4318FF', fontWeight: '700' }}>Input: <span style={{ color: '#1B254B', fontWeight: '500' }}>{ex.input}</span></div>
                                                            <div style={{ fontSize: '0.75rem', color: '#05CD99', fontWeight: '700' }}>Output: <span style={{ color: '#1B254B', fontWeight: '500' }}>{ex.output}</span></div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>

                                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                                            <div style={{ fontSize: '0.7rem', fontWeight: '700', color: '#707EAE', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                <i className="fa-solid fa-keyboard" style={{ color: '#4318FF' }}></i> Custom Input (STDIN)
                                            </div>
                                            <textarea
                                                style={{
                                                    flex: 1,
                                                    width: '100%',
                                                    padding: '0.8rem',
                                                    borderRadius: '12px',
                                                    border: '1px solid #E0E5F2',
                                                    background: '#F4F7FE',
                                                    fontFamily: 'monospace',
                                                    fontSize: '0.8rem',
                                                    outline: 'none',
                                                    resize: 'none',
                                                    maxHeight: '120px'
                                                }}
                                                placeholder="Custom input..."
                                                value={customInput}
                                                onChange={(e) => setCustomInput(e.target.value)}
                                            />
                                        </div>
                                    </div>

                                    {/* Right Panel: Editor & Console */}
                                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>

                                        {/* Editor Header: Language Switcher Dropdown */}
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#F8F9FF', padding: '0.5rem 1rem', borderRadius: '10px', border: '1px solid #E0E5F2' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#707EAE' }}>LANGUAGE:</span>
                                                <select
                                                    value={selectedLanguage}
                                                    onChange={(e) => setSelectedLanguage(e.target.value)}
                                                    style={{
                                                        padding: '6px 15px',
                                                        borderRadius: '8px',
                                                        border: '1px solid #E0E5F2',
                                                        fontSize: '0.8rem',
                                                        fontWeight: '700',
                                                        color: '#4318FF',
                                                        background: 'white',
                                                        outline: 'none',
                                                        cursor: 'pointer'
                                                    }}
                                                >
                                                    {supportedLanguages.map(lang => (
                                                        <option key={lang.id} value={lang.id}>
                                                            {lang.name}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div style={{ fontSize: '0.7rem', color: '#A3AED0', fontWeight: '500' }}>
                                                Theme: <span style={{ color: '#1B254B', fontWeight: '700' }}>VS Dark</span>
                                            </div>
                                        </div>

                                        {/* Monaco Editor Container - Expanded */}
                                        <div style={{
                                            flex: '1 1 500px', // Allow it to grow and set a healthy base height
                                            minHeight: '400px',
                                            border: '1px solid #E0E5F2',
                                            borderRadius: '16px',
                                            overflow: 'hidden',
                                            background: '#1e1e1e',
                                            boxShadow: '0 4px 15px rgba(0,0,0,0.05)'
                                        }}>
                                            <Editor
                                                height="100%"
                                                language={selectedLanguage}
                                                theme="vs-dark"
                                                value={answers[`coding_${currentQ.id}`] || currentQ.starter_code || (selectedLanguage === 'python' ? "# Write your python code here..." : "// Write your code here...")}
                                                onChange={(val) => handleAnswerChange(`coding_${currentQ.id}`, val)}
                                                options={{
                                                    fontSize: 14,
                                                    minimap: { enabled: false },
                                                    scrollbar: { vertical: 'hidden', horizontal: 'hidden' },
                                                    lineNumbers: 'on',
                                                    roundedSelection: true,
                                                    scrollBeyondLastLine: false,
                                                    automaticLayout: true,
                                                    padding: { top: 20 }
                                                }}
                                            />
                                        </div>

                                        {/* Compiler Controls & Simplified Output Area */}
                                        <div style={{
                                            flexShrink: 0,
                                            background: '#FFFFFF',
                                            borderRadius: '12px',
                                            padding: '1rem',
                                            border: '1px solid #E0E5F2'
                                        }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.8rem' }}>
                                                <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#1B254B', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                    <i className="fa-solid fa-square-poll-horizontal" style={{ color: '#4318FF' }}></i> Results
                                                </div>
                                                <button
                                                    onClick={() => runCode(currentQ.id)}
                                                    disabled={isExecuting}
                                                    style={{
                                                        padding: '0.6rem 1.5rem',
                                                        background: '#4318FF',
                                                        color: 'white',
                                                        border: 'none',
                                                        borderRadius: '8px',
                                                        fontSize: '0.85rem',
                                                        fontWeight: '800',
                                                        cursor: 'pointer',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '8px',
                                                        boxShadow: '0 4px 15px rgba(67, 24, 255, 0.2)',
                                                        transition: 'all 0.2s'
                                                    }}
                                                >
                                                    {isExecuting ? <i className="fa-solid fa-spinner fa-spin"></i> : <i className="fa-solid fa-play"></i>}
                                                    {isExecuting ? 'Running...' : 'Run & Test'}
                                                </button>
                                            </div>

                                            <div style={{
                                                padding: '0.5rem 0',
                                                maxHeight: '120px',
                                                overflowY: 'auto',
                                                fontFamily: "'Fira Code', 'Courier New', monospace",
                                                fontSize: '0.85rem'
                                            }}>
                                                {codeOutput.length === 0 ? (
                                                    <div style={{ color: '#A3AED0', fontStyle: 'italic' }}>Output will be displayed here...</div>
                                                ) : (
                                                    codeOutput.map((log, i) => (
                                                        <div key={i} style={{
                                                            color: log.type === 'error' ? '#E53E3E' : log.type === 'success' ? '#05CD99' : log.type === 'info' ? '#4318FF' : '#1B254B',
                                                            marginBottom: '4px',
                                                            display: 'flex',
                                                            gap: '10px',
                                                            lineHeight: '1.4',
                                                            background: log.type === 'error' ? '#FFF5F5' : 'transparent',
                                                            padding: log.type === 'error' ? '4px 8px' : '0',
                                                            borderRadius: '4px'
                                                        }}>
                                                            <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{log.content}</pre>
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Navigation Footer - Slimmer & Clean */}
                        <div style={{
                            flexShrink: 0,
                            padding: '0.6rem 2rem',
                            background: '#F8F9FF',
                            borderTop: '1px solid #E0E5F2',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                        }}>
                            {/* Previous Button */}
                            <button
                                onClick={() => setCurrentQuestionIdx(prev => Math.max(0, prev - 1))}
                                disabled={currentQuestionIdx === 0}
                                style={{
                                    padding: '0.5rem 1.5rem',
                                    background: 'white',
                                    color: currentQuestionIdx === 0 ? '#A0AEC0' : '#4318FF',
                                    border: '1px solid',
                                    borderColor: currentQuestionIdx === 0 ? '#E2E8F0' : '#4318FF',
                                    borderRadius: '8px',
                                    fontSize: '0.85rem',
                                    fontWeight: '700',
                                    cursor: currentQuestionIdx === 0 ? 'not-allowed' : 'pointer',
                                    transition: 'all 0.2s',
                                    visibility: currentQuestionIdx === 0 ? 'hidden' : 'visible'
                                }}
                            >
                                <i className="fa-solid fa-arrow-left" style={{ marginRight: '8px' }}></i> Previous
                            </button>

                            {/* Next / Submit Button */}
                            {!isLastQ ? (
                                <button
                                    onClick={handleNext}
                                    style={{
                                        padding: '0.5rem 2rem',
                                        background: 'linear-gradient(135deg, #4318FF 0%, #7551FF 100%)',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '8px',
                                        fontSize: '0.9rem',
                                        fontWeight: '700',
                                        cursor: 'pointer',
                                        boxShadow: '0 4px 10px rgba(67, 24, 255, 0.15)'
                                    }}
                                >
                                    Next <i className="fa-solid fa-arrow-right" style={{ marginLeft: '8px' }}></i>
                                </button>
                            ) : (
                                <button
                                    onClick={handleSubmit} disabled={isSubmitting}
                                    style={{
                                        padding: '0.5rem 2.5rem',
                                        background: '#05CD99',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '8px',
                                        fontSize: '0.9rem',
                                        fontWeight: '700',
                                        cursor: 'pointer',
                                        boxShadow: '0 4px 10px rgba(5, 205, 153, 0.15)',
                                        opacity: isSubmitting ? 0.7 : 1
                                    }}
                                >
                                    {isSubmitting ? 'Submitting...' : 'Submit'} <i className="fa-solid fa-paper-plane" style={{ marginLeft: '8px' }}></i>
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AiTakeAssessment;
