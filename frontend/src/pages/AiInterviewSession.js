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

    const addMessage = useCallback((sender, text) => {
        const displayText = typeof text === 'object' ? (text.question || JSON.stringify(text)) : text;
        setChatMessages(prev => [...prev, { sender, text: displayText }]);
        chatHistoryRef.current.push({ role: sender === 'ai' ? 'assistant' : 'user', content: displayText });
    }, []);

    const completeInterview = useCallback(async () => {
        stopCamera();
        const finishMessage = "The interview is now complete. Thank you for your time and we will get back to you soon. Goodbye!";
        addMessage('ai', finishMessage);
        await speak(finishMessage);
        axios.patch(`http://localhost:8001/api/ai-candidates/${token}/status/`, { status: 'Completed' }).catch(console.error);
        setIsProcessing(true);
        setAiStatus("Session Finished");
    }, [token, speak, addMessage]);

    const startListening = useCallback(() => {
        if (userInputMode !== 'audio' || !recognitionRef.current || isRecording) return;

        let attempts = 0;
        const maxAttempts = 10;

        const tryStart = () => {
            // Check if AI is occupied
            if (isProcessing || isSpeaking) {
                if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(tryStart, 300); // Retry every 300ms
                }
                return;
            }

            try {
                recognitionRef.current.start();
                console.log("Auto-mic activated successfully");
            } catch (e) {
                if (e.name === 'InvalidStateError') {
                    // Already started, ignore
                } else {
                    console.warn("Auto-start mic error:", e);
                }
            }
        };

        tryStart();
    }, [userInputMode, isRecording, isProcessing, isSpeaking]);

    const handleAnswerSubmission = useCallback(async (answer) => {
        if (!answer || !answer.trim() || isProcessing) return;

        setIsProcessing(true);
        addMessage('user', answer);
        setResponseInput('');
        setAiStatus("AI is thinking...");

        try {
            const currentQ = questions[currentQuestionIndex] || "Introduction and Background";
            const response = await axios.post('http://localhost:8001/api/ai-candidates/process-answer/', {
                candidate_id: token,
                question: typeof currentQ === 'object' ? currentQ.question : currentQ,
                answer: answer,
                remaining_questions: questions.slice(currentQuestionIndex + 1),
                chat_history: chatHistoryRef.current
            });

            const data = response.data;
            let fullFeedback = data.feedback || "";
            const nextIdx = currentQuestionIndex + 1;

            // Extract the question string from potential object or string
            const extractQ = (q) => {
                if (!q) return null;
                if (typeof q === 'object') return q.question || JSON.stringify(q);
                return q;
            };

            const followUpQ = extractQ(data.follow_up_question);
            const refinedNextQ = extractQ(data.refined_next_question);

            // Bundle feedback for display and voice
            let fullVoiceOutput = "";
            if (fullFeedback.trim()) {
                addMessage('ai', fullFeedback);
                fullVoiceOutput += fullFeedback + " ";
            }

            if (followUpQ) {
                // If AI wants a quick follow-up before moving to next main question
                addMessage('ai', followUpQ);
                fullVoiceOutput += followUpQ;
                await speak(fullVoiceOutput);
                setIsProcessing(false);
                setAiStatus("Listening...");
                startListening();
            } else if (refinedNextQ === null && nextIdx >= questions.length) {
                // End of interview
                if (fullVoiceOutput) await speak(fullVoiceOutput);
                completeInterview();
            } else {
                // Moving to next main question
                const nextQ = refinedNextQ || questions[nextIdx] || "Could you tell me more about your experience?";
                setCurrentQuestionIndex(nextIdx);
                setProgress((nextIdx / (questions.length || 1)) * 100);

                setQuestions(prev => {
                    const newQs = [...prev];
                    if (nextIdx < newQs.length) newQs[nextIdx] = nextQ;
                    else newQs.push(nextQ);
                    return newQs;
                });

                addMessage('ai', nextQ);
                fullVoiceOutput += nextQ;

                if (fullVoiceOutput) await speak(fullVoiceOutput);

                setIsProcessing(false);
                setAiStatus("AI Interviewer Online");
                startListening();
            }
        } catch (err) {
            console.error("Submission error:", err);
            if (err.response?.status === 429) setShowQuotaWarning(true);
            setIsProcessing(false);
            setAiStatus("Error - Try again");
        }
    }, [token, questions, currentQuestionIndex, isProcessing, addMessage, speak, completeInterview, startListening]);

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

            const introQ = "Could you please introduce yourself and provide a brief overview of your professional background?";
            let finalQs = [...qs];
            if (finalQs[0] !== introQ) {
                finalQs = [introQ, ...finalQs];
                setQuestions(finalQs);
            }

            // Bundle welcome and intro question for smooth voice output
            addMessage('ai', welcome);
            addMessage('ai', introQ);
            await speak(`${welcome} ${introQ}`);
            startListening();
        };

        initSession();
        return () => stopCamera();
    }, [token, addMessage, startListening]);

    const silenceTimerRef = useRef(null);
    const transcriptRef = useRef("");

    const submitHandlerRef = useRef(handleAnswerSubmission);
    useEffect(() => {
        submitHandlerRef.current = handleAnswerSubmission;
    }, [handleAnswerSubmission]);

    // stable Speech Recognition Setup
    useEffect(() => {
        if (!('webkitSpeechRecognition' in window)) return;

        const recognition = new window.webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            setIsRecording(true);
            setAiStatus("Listening...");
            transcriptRef.current = "";
        };

        recognition.onresult = (event) => {
            let interimTranscript = "";
            let finalTranscript = "";

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (finalTranscript) {
                transcriptRef.current += finalTranscript;
            }

            const currentTotal = (transcriptRef.current + interimTranscript).trim();
            if (currentTotal) {
                setAiStatus(`Heard: "${currentTotal.length > 35 ? '...' + currentTotal.slice(-35) : currentTotal}"`);
            }

            // Reset silence timer every time user speaks
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

            if (currentTotal.length > 2) {
                silenceTimerRef.current = setTimeout(() => {
                    const finalSubmission = transcriptRef.current + interimTranscript;
                    if (finalSubmission.trim().length > 3) {
                        console.log("5.0s silence detected. Processing final submission.");
                        setIsProcessing(true);
                        setAiStatus("Processing answer...");
                        try { recognition.stop(); } catch (e) { }
                        if (submitHandlerRef.current) submitHandlerRef.current(finalSubmission);
                    }
                }, 5000); // Increased to 5 seconds for massive patience
            }
        };

        recognition.onerror = (event) => {
            if (event.error === 'no-speech') return; // Ignore harmless noise errors
            console.error("Recognition Error:", event.error);
            setIsRecording(false);
            setAiStatus("Mic error: " + event.error);
        };

        recognition.onend = () => {
            setIsRecording(false);
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
            console.log("Recognition session ended.");
        };

        recognitionRef.current = recognition;

        return () => {
            if (recognitionRef.current) {
                try { recognitionRef.current.stop(); } catch (e) { }
            }
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        };
    }, []);

    // Unified Reactive Microphone Trigger
    useEffect(() => {
        // Only attempt to start if we are in audio mode AND the AI is not busy
        const shouldBeListening = userInputMode === 'audio' && !isProcessing && !isSpeaking;

        if (shouldBeListening && !isRecording && recognitionRef.current) {
            const timer = setTimeout(() => {
                // Double check states before starting
                if (userInputMode === 'audio' && !isProcessing && !isSpeaking && !isRecording) {
                    try {
                        recognitionRef.current.start();
                        console.log("Mic auto-started via state sync");
                    } catch (e) {
                        if (e.name !== 'InvalidStateError') {
                            console.warn("Auto-start mic skipped:", e.message);
                        }
                    }
                }
            }, 600); // 600ms buffer to allow states to settle
            return () => clearTimeout(timer);
        }
    }, [isRecording, isProcessing, isSpeaking, userInputMode]);

    const toggleRecording = () => {
        if (!recognitionRef.current) return alert("Speech recognition not supported");

        if (isRecording) {
            try { recognitionRef.current.stop(); } catch (e) { }
            setIsRecording(false);
        } else {
            // Cancel any AI speech if user wants to speak
            if (synthRef.current.speaking) {
                synthRef.current.cancel();
                setIsSpeaking(false);
            }

            try {
                recognitionRef.current.start();
            } catch (e) {
                if (e.name === 'InvalidStateError') {
                    // Already starting/running
                    console.log("Recognition already active");
                } else {
                    console.error("Manual mic start error:", e);
                    setAiStatus("Mic Error - Refresh");
                }
            }
        }
    };

    useEffect(() => {
        if (chatContainerRef.current) chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }, [chatMessages]);

    return (
        <div className="ai-session-page">
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

                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.75rem', height: '100%' }}>
                    <div style={{ background: 'white', padding: '0.75rem 1.5rem', borderRadius: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 4px 15px rgba(0,0,0,0.05)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <i className="fa-solid fa-user-tie" style={{ color: '#667eea', fontSize: '0.9rem' }}></i>
                            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{candidateName}</span>
                        </div>
                        <div className="progress-bar"><div className="progress-fill" style={{ width: `${progress}%` }}></div></div>
                        <button onClick={() => navigate('/ai-interview')} style={{ background: 'none', border: 'none', color: '#718096', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.85rem' }}><i className="fa-solid fa-xmark"></i> Exit</button>
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
                        {chatMessages.map((msg, i) => <div key={i} className={`message ${msg.sender}`}>{msg.text}</div>)}
                    </div>

                    <div style={{ background: 'white', padding: '0.6rem 1rem', borderRadius: '12px', boxShadow: '0 -2px 10px rgba(0,0,0,0.03)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        {userInputMode === 'audio' ? (
                            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <button
                                    onClick={toggleRecording}
                                    disabled={isProcessing}
                                    className={`mic-btn ${isRecording ? 'listening' : ''}`}
                                    style={{ width: '40px', height: '40px', fontSize: '1rem', cursor: isProcessing ? 'not-allowed' : 'pointer', opacity: isProcessing ? 0.6 : 1 }}
                                >
                                    <i className={isRecording ? "fa-solid fa-stop" : "fa-solid fa-microphone"}></i>
                                </button>
                                <span style={{ color: '#4a5568', fontWeight: 600, fontSize: '0.8rem' }}>{isRecording ? "Listening..." : "Click to Speak"}</span>
                            </div>
                        ) : (
                            <div style={{ flex: 1, display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                <input
                                    className="response-input"
                                    style={{ flex: 1, border: '1px solid #cbd5e0', borderRadius: '8px', padding: '6px 12px', fontSize: '0.85rem', outline: 'none' }}
                                    value={responseInput}
                                    onChange={(e) => setResponseInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleAnswerSubmission(responseInput)}
                                    placeholder="Type answer..."
                                />
                                <button onClick={() => handleAnswerSubmission(responseInput)} disabled={isProcessing} style={{ background: '#667eea', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '6px', fontSize: '0.9rem', cursor: 'pointer' }}><i className="fa-solid fa-paper-plane"></i></button>
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
        </div>
    );
};

export default AiInterviewSession;
