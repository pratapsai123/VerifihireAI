import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';
import '../styles/AiInterviewSession.css';

const AiInterviewSession = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [candidateName, setCandidateName] = useState('Candidate');
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [questions, setQuestions] = useState([]);
    const [chatMessages, setChatMessages] = useState([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [userInputMode, setUserInputMode] = useState('audio'); // 'audio' or 'text'
    const [aiStatus, setAiStatus] = useState('AI Interviewer Online');
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [progress, setProgress] = useState(0);
    const [showQuotaWarning, setShowQuotaWarning] = useState(false);
    const [responseInput, setResponseInput] = useState('');
    const [integrityBreech, setIntegrityBreech] = useState({ active: false, text: '' });
    const [aiToast, setAiToast] = useState({ active: false, text: '', urgent: false });

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
            }
            streamRef.current = stream;
        } catch (err) {
            console.error("Camera access error:", err);
            setAiToast({ active: true, text: 'Camera Blocked', urgent: true });
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
    };

    const reportViolation = async (eventType) => {
        try {
            await axios.post(`http://localhost:8001/api/ai-candidates/${token}/integrity/`, {
                event_type: eventType
            });
        } catch (err) {
            console.error("Failed to report violation:", err);
        }
    };

    const showAiEvent = (text, urgent = false, eventType = null) => {
        setAiToast({ active: true, text, urgent });
        if (urgent) {
            setIntegrityBreech({ active: true, text });
            setTimeout(() => setIntegrityBreech({ active: false, text: '' }), 3000);
        }
        if (eventType) reportViolation(eventType);
        setTimeout(() => setAiToast({ active: false, text: '', urgent: false }), 3000);
    };

    useEffect(() => {
        let detectInterval;
        const initAiMonitoring = async () => {
            setAiStatus('Initializing AI Safeguards...');
            try {
                const cocoSsd = window.cocoSsd;
                if (!cocoSsd) {
                    let retryCount = 0;
                    const waitForCoco = setInterval(async () => {
                        retryCount++;
                        if (window.cocoSsd) {
                            clearInterval(waitForCoco);
                            setupDetector();
                        } else if (retryCount > 10) {
                            clearInterval(waitForCoco);
                            setAiStatus('AI Monitoring Limited');
                        }
                    }, 1000);
                    return;
                }
                setupDetector();
            } catch (err) {
                console.error("AI Monitor Init error:", err);
                setAiStatus('Safeguards Partially Active');
            }
        };

        const setupDetector = async () => {
            detectorRef.current = await window.cocoSsd.load();
            setAiStatus('AI Monitoring Active');

            detectInterval = setInterval(async () => {
                if (videoRef.current && detectorRef.current && videoRef.current.readyState === 4) {
                    const now = Date.now();
                    if (now - lastDetectionTimeRef.current > 2000) {
                        lastDetectionTimeRef.current = now;
                        try {
                            const predictions = await detectorRef.current.detect(videoRef.current);
                            const phone = predictions.find(p => p.class === 'cell phone');
                            if (phone) showAiEvent("CELL PHONE DETECTED", true, 'phone_detection');

                            const people = predictions.filter(p => p.class === 'person');
                            if (people.length > 1) showAiEvent("MULTIPLE PEOPLE DETECTED", true, 'multiface_detection');
                            else if (people.length === 0) showAiEvent("CANDIDATE NOT DETECTED", true, 'no_face_detection');
                        } catch (e) {
                            console.error("Detection loop error:", e);
                        }
                    }
                }
            }, 1000);
        };

        const handleVisibilityChange = () => {
            if (document.hidden || document.visibilityState === 'hidden') {
                showAiEvent("TAB SWITCHED", true, 'tab_switch');
            }
        };

        const handleBlur = () => {
            showAiEvent("WINDOW BLURRED", true, 'tab_switch');
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('blur', handleBlur);
        initAiMonitoring();

        return () => {
            if (detectInterval) clearInterval(detectInterval);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('blur', handleBlur);
        };
    }, [token]);

    // 3. Speech and Interactions
    const speak = (content) => {
        const text = typeof content === 'object' ? (content.question || JSON.stringify(content)) : content;
        return new Promise((resolve) => {
            if (!text) return resolve();
            synthRef.current.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            const voice = voicesRef.current.find(v => v.name.includes('Google US English') && v.name.includes('Female')) ||
                voicesRef.current.find(v => v.name.includes('US English')) ||
                voicesRef.current[0];

            if (voice) utterance.voice = voice;
            utterance.onstart = () => { setIsSpeaking(true); setAiStatus("Speaking..."); };
            utterance.onend = () => { setIsSpeaking(false); setAiStatus("AI Interviewer Online"); resolve(); };
            utterance.onerror = () => { setIsSpeaking(false); setAiStatus("AI Interviewer Online"); resolve(); };
            synthRef.current.speak(utterance);
        });
    };

    const addMessage = (sender, text) => {
        const displayText = typeof text === 'object' ? (text.question || JSON.stringify(text)) : text;
        setChatMessages(prev => [...prev, { sender, text: displayText }]);
        chatHistoryRef.current.push({ role: sender === 'ai' ? 'assistant' : 'user', content: displayText });
    };

    const askCurrentQuestion = useCallback((index, qs) => {
        const question = qs[index];
        if (!question) return;
        addMessage('ai', question);
        speak(question);
    }, []);

    const handleAnswerSubmission = async (answer) => {
        if (!answer.trim() || isProcessing) return;
        setIsProcessing(true);
        addMessage('user', answer);
        setResponseInput('');

        try {
            const response = await axios.post('http://localhost:8001/api/ai-candidates/process-answer/', {
                candidate_id: token,
                question: questions[currentQuestionIndex],
                answer: answer,
                next_question: questions[currentQuestionIndex + 1] || null,
                chat_history: chatHistoryRef.current
            });

            const data = response.data;
            let fullFeedback = data.feedback;
            if (data.follow_up_question) fullFeedback += " " + data.follow_up_question;

            if (data.refined_next_question && !data.follow_up_question) {
                const nextIdx = currentQuestionIndex + 1;
                if (nextIdx < questions.length) {
                    setQuestions(prev => {
                        const newQs = [...prev];
                        newQs[nextIdx] = data.refined_next_question;
                        return newQs;
                    });
                }
            }

            if (fullFeedback) {
                addMessage('ai', fullFeedback);
                await speak(fullFeedback);
            }

            if (data.follow_up_question) {
                setIsProcessing(false);
            } else {
                const nextIdx = currentQuestionIndex + 1;
                setCurrentQuestionIndex(nextIdx);
                setProgress((nextIdx / questions.length) * 100);

                if (nextIdx < questions.length) {
                    const nextQ = questions[nextIdx];
                    addMessage('ai', nextQ);
                    await speak(nextQ);
                    setIsProcessing(false);
                } else {
                    completeInterview();
                }
            }
        } catch (err) {
            console.error("Submission error:", err);
            if (err.response?.status === 429) setShowQuotaWarning(true);
            setIsProcessing(false);
        }
    };

    const completeInterview = () => {
        stopCamera();
        const finishMessage = "Thank you for your time. Your assessment has been completed successfully. Goodbye!";
        addMessage('ai', finishMessage);
        speak(finishMessage);
        axios.patch(`http://localhost:8001/api/ai-candidates/${token}/status/`, { status: 'Completed' }).catch(console.error);
    };

    // 4. Lifecycle
    useEffect(() => {
        if (isInitializedRef.current) return;
        isInitializedRef.current = true;

        const initSession = async () => {
            const storedData = sessionStorage.getItem('interviewData');
            if (storedData) {
                const data = JSON.parse(storedData);
                setCandidateName(data.candidateName);
                setQuestions(data.questions);
                startInterview(data.candidateName, data.questions);
            } else {
                try {
                    const res = await axios.get(`http://localhost:8001/api/ai-candidates/${token}/`);
                    setCandidateName(res.data.full_name);
                    const matchRes = await axios.post('http://localhost:8001/api/ai-candidates/match/', {
                        candidate_id: token,
                        job_description: res.data.job_description
                    });
                    setQuestions(matchRes.data.interview_questions);
                    startInterview(res.data.full_name, matchRes.data.interview_questions);
                } catch (err) {
                    console.error("Init session error:", err);
                }
            }
        };

        const startInterview = async (name, qs) => {
            await startCamera();
            const firstName = name.split(' ')[0];
            const welcome = `Hello ${firstName}! I'm your AI interviewer for VerifiHireAI. Let's begin the session!`;
            addMessage('ai', welcome);
            await speak(welcome);

            const introQ = "Could you please introduce yourself and provide a brief overview of your professional background?";

            // Ensure introQ is the first question
            let finalQs = [...qs];
            if (finalQs[0] !== introQ) {
                finalQs = [introQ, ...finalQs];
                setQuestions(finalQs);
            }

            setTimeout(() => askCurrentQuestion(0, finalQs), 1000);
        };

        initSession();
        return () => stopCamera();
    }, [token, askCurrentQuestion]);

    // Speech Recognition
    useEffect(() => {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new window.webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            recognition.onstart = () => setIsRecording(true);
            recognition.onresult = (event) => handleAnswerSubmission(event.results[0][0].transcript);
            recognition.onerror = () => setIsRecording(false);
            recognition.onend = () => setIsRecording(false);
            recognitionRef.current = recognition;
        }
    }, [currentQuestionIndex, questions]);

    const toggleRecording = () => {
        if (!recognitionRef.current) return alert("Speech recognition not supported");
        if (isRecording) recognitionRef.current.stop();
        else recognitionRef.current.start();
    };

    useEffect(() => {
        if (chatContainerRef.current) chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }, [chatMessages]);

    return (
        <div className="dashboard-page" style={{ height: '100vh', overflow: 'hidden' }}>
            {showQuotaWarning && (
                <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', padding: '15px', background: '#ff4444', color: 'white', textAlign: 'center', zIndex: 10000, fontWeight: 'bold' }}>
                    ⚠️ AI Service Limit Reached. The interview cannot continue at this time.
                </div>
            )}

            <div className="ai-session-container">
                <div className="ai-sidebar">
                    <div className="camera-container">
                        <video ref={videoRef} autoPlay playsInline muted id="candidateVideo" style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                        <div className="ai-scan-bar"></div>
                        {integrityBreech.active && <div className="integrity-overlay"><span>{integrityBreech.text}</span></div>}
                        {aiToast.active && <div className={`ai-event-toast ${aiToast.urgent ? 'urgent' : ''}`}>{aiToast.text}</div>}
                    </div>
                    <div style={{ marginTop: '20px', textAlign: 'center', width: '100%' }}>
                        <div className="ai-status-badge"><span className="speaking-indicator"></span>{aiStatus}</div>
                    </div>
                    <div className={`ai-full-body ${isSpeaking ? 'speaking' : ''}`}></div>
                </div>

                <div className="ai-main-content" style={{ padding: '0' }}>
                    <div style={{ background: 'white', padding: '1.25rem 2rem', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <i className="fa-solid fa-user-tie" style={{ color: '#667eea' }}></i>
                            <span style={{ fontWeight: 600 }}>{candidateName}</span>
                        </div>
                        <div className="progress-bar"><div className="progress-fill" style={{ width: `${progress}%` }}></div></div>
                        <button onClick={() => navigate('/ai-interview')} style={{ background: 'none', border: 'none', color: '#718096', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}><i className="fa-solid fa-xmark"></i> Exit</button>
                    </div>

                    <div style={{ padding: '0 2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', flex: 1, overflowY: 'auto' }}>

                        <div className="question-card">
                            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: '#667eea', fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>Current Question</span>
                            <div style={{ fontSize: '1.3rem', fontWeight: 600, color: '#2d3748' }}>
                                {questions[currentQuestionIndex] ? (
                                    typeof questions[currentQuestionIndex] === 'object'
                                        ? (questions[currentQuestionIndex].question || JSON.stringify(questions[currentQuestionIndex]))
                                        : questions[currentQuestionIndex]
                                ) : 'Starting interview...'}
                            </div>
                        </div>

                        <div ref={chatContainerRef} className="chat-container">
                            {chatMessages.length === 0 && <div style={{ textAlign: 'center', color: '#a0aec0', marginTop: '3rem', fontStyle: 'italic' }}>Conversation history will appear here...</div>}
                            {chatMessages.map((msg, i) => <div key={i} className={`message ${msg.sender}`}>{msg.text}</div>)}
                        </div>

                        <div style={{ background: 'white', padding: '1.5rem', borderRadius: '24px', boxShadow: '0 -4px 20px rgba(0,0,0,0.05)' }}>
                            {userInputMode === 'audio' ? (
                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                                    <button onClick={toggleRecording} className={`mic-btn ${isRecording ? 'listening' : ''}`}><i className={isRecording ? "fa-solid fa-stop" : "fa-solid fa-microphone"}></i></button>
                                    <span style={{ color: '#718096', fontWeight: 500 }}>{isRecording ? "Listening..." : "Tap mic to speak"}</span>
                                </div>
                            ) : (
                                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
                                    <textarea className="response-input" value={responseInput} onChange={(e) => setResponseInput(e.target.value)} placeholder="Type your answer here..." style={{ flex: 1, border: '2px solid #e2e8f0', borderRadius: '16px', padding: '12px', resize: 'none', height: '60px', fontFamily: 'inherit' }} />
                                    <button onClick={() => handleAnswerSubmission(responseInput)} disabled={isProcessing} style={{ background: '#667eea', color: 'white', border: 'none', padding: '12px 24px', borderRadius: '12px', fontWeight: 'bold', cursor: 'pointer' }}><i className="fa-solid fa-paper-plane"></i></button>
                                </div>
                            )}
                            <div style={{ textAlign: 'center', marginTop: '15px' }}>
                                <button onClick={() => setUserInputMode(userInputMode === 'audio' ? 'text' : 'audio')} style={{ background: 'none', border: 'none', color: '#667eea', fontWeight: 600, cursor: 'pointer', fontSize: '0.9rem' }}><i className={userInputMode === 'audio' ? "fa-solid fa-keyboard" : "fa-solid fa-microphone"}></i>{userInputMode === 'audio' ? " Switch to Text Input" : " Switch to Voice Input"}</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AiInterviewSession;
