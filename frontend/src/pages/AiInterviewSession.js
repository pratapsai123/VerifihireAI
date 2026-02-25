import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ReadyPlayerMeAvatar from '../components/ReadyPlayerMeAvatar';
import '../styles/Dashboard.css';
import '../styles/AiInterviewSession.css';
import { API_BASE_URL } from '../apiConfig';

const AiInterviewSession = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [candidateName, setCandidateName] = useState('Candidate');
    const MAX_QUESTIONS = 10;
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
    const isProcessingRef = useRef(false);
    const isSpeakingRef = useRef(false);
    const isRecordingRef = useRef(false);

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

    const reportViolation = useCallback(async (eventType) => {
        try {
            await axios.post(`${API_BASE_URL}/ai-candidates/${token}/integrity/`, {
                event_type: eventType
            });
        } catch (err) {
            console.error("Failed to report violation:", err);
        }
    }, [token]);

    const showAiEvent = useCallback((text, urgent = false, eventType = null) => {
        setAiToast({ active: true, text, urgent });
        if (urgent) {
            setIntegrityBreech({ active: true, text });
            setTimeout(() => setIntegrityBreech({ active: false, text: '' }), 3000);
        }
        if (eventType) reportViolation(eventType);
        setTimeout(() => setAiToast({ active: false, text: '', urgent: false }), 3000);
    }, [reportViolation]);

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
        const sc = startCamera; // Reference for cleanup if needed

        return () => {
            if (detectInterval) clearInterval(detectInterval);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('blur', handleBlur);
            // sc(); // Optional: stop camera on unmount if appropriate
        };
    }, [token, showAiEvent]);

    // 3. Speech and Interactions
    const speak = useCallback((content) => {
        const text = typeof content === 'object' ? (content.question || JSON.stringify(content)) : content;
        return new Promise((resolve) => {
            if (!text) return resolve();

            // Safety Watchdog: If speech fails to end, resolve anyway after a timeout
            // 200ms per character + 3s buffer is extremely safe
            const timeoutMs = Math.max(3000, (text.length * 200) + 3000);
            const watchdog = setTimeout(() => {
                console.warn("📢 Speak Watchdog triggered (Possible browser speech hang)");
                setIsSpeaking(false);
                isSpeakingRef.current = false;
                resolve();
            }, timeoutMs);

            synthRef.current.cancel();
            // Force resume (Chrome bug fix)
            if (synthRef.current.paused) synthRef.current.resume();

            const utterance = new SpeechSynthesisUtterance(text);
            const voice = voicesRef.current.find(v => v.lang.includes('IN') && (v.name.includes('Heera') || v.name.includes('Ravi'))) ||
                voicesRef.current.find(v => v.lang.includes('IN')) ||
                voicesRef.current.find(v => v.name.toLowerCase().includes('india')) ||
                voicesRef.current.find(v => v.name.includes('Google US English') && v.name.includes('Female')) ||
                voicesRef.current.find(v => v.name.includes('US English')) ||
                voicesRef.current[0];

            if (voice) {
                utterance.voice = voice;
            }

            utterance.onstart = () => {
                setIsSpeaking(true);
                isSpeakingRef.current = true;
                setAiStatus("Speaking...");
            };

            utterance.onend = () => {
                clearTimeout(watchdog);
                setIsSpeaking(false);
                isSpeakingRef.current = false;
                setAiStatus("Indu is Online");
                resolve();
            };

            utterance.onerror = (event) => {
                console.error("SpeechSynthesis error:", event);
                clearTimeout(watchdog);
                setIsSpeaking(false);
                isSpeakingRef.current = false;
                setAiStatus("Indu is Online");
                resolve();
            };

            synthRef.current.speak(utterance);
        });
    }, []);

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
        axios.patch(`${API_BASE_URL}/ai-candidates/${token}/status/`, { status: 'Completed' }).catch(console.error);
        setIsProcessing(true);
        setAiStatus("Session Finished");
    }, [token, speak, addMessage]);

    const startListening = useCallback(() => {
        if (userInputMode !== 'audio' || !recognitionRef.current || isRecordingRef.current) return;

        let attempts = 0;
        const maxAttempts = 10;

        const tryStart = () => {
            // Check if AI is occupied - Use REFS to avoid stale closures
            if (isProcessingRef.current || isSpeakingRef.current) {
                if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(tryStart, 350); // Retry 
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
    }, [userInputMode]);

    const handleAnswerSubmission = useCallback(async (answer) => {
        if (!answer || !answer.trim() || isProcessing) {
            console.log("Submission skipped: answer empty or already processing");
            return;
        }

        // 1. Immediate UI Lock & Reset Nudge
        setIsProcessing(true);
        isProcessingRef.current = true;
        setAiStatus("AI is thinking...");
        nudgeCountRef.current = 0; // Reset nudge for the new question turn
        if (globalSilenceTimerRef.current) clearTimeout(globalSilenceTimerRef.current);

        // 2. Force Microphone Stop
        if (recognitionRef.current) {
            try { recognitionRef.current.stop(); } catch (e) { }
        }
        if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

        addMessage('user', answer);
        setResponseInput('');
        console.log("Submitting answer turn...");

        try {
            const currentQ = questions[currentQuestionIndex] || "Introduction and Background";
            const response = await axios.post(`${API_BASE_URL}/ai-candidates/process-answer/`, {
                candidate_id: token,
                question: typeof currentQ === 'object' ? currentQ.question : currentQ,
                answer: answer,
                remaining_questions: questions.slice(currentQuestionIndex + 1),
                chat_history: chatHistoryRef.current
            }, { timeout: 35000 }); // 35s for more complex reasoning

            const data = response.data;
            const isClarification = data.is_clarification === true;
            let fullFeedback = data.feedback || "";

            if (isClarification) {
                // Scenario A: Candidate asked for help/clarification
                addMessage('ai', fullFeedback);
                try {
                    await speak(fullFeedback);
                } catch (e) {
                    console.error("Clarification speak error:", e);
                }

                setIsProcessing(false);
                isProcessingRef.current = false;
                setAiStatus("Indu is Online");
                if (userInputMode === 'audio' && !showQuotaWarning) startListening();
                return; // STOP HERE: Don't move to next question
            }

            const nextIdx = currentQuestionIndex + 1;
            const totalAnswered = nextIdx; // questions answered so far

            // --- HARD STOP: end after MAX_QUESTIONS ---
            if (totalAnswered >= MAX_QUESTIONS) {
                if (fullFeedback.trim()) {
                    addMessage('ai', fullFeedback.trim());
                    await speak(fullFeedback.trim());
                }
                completeInterview();
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
                await speak(followUpText);
                setIsProcessing(false);
                if (userInputMode === 'audio' && !showQuotaWarning) startListening();
                setAiStatus("Indu is Online");
            } else if (refinedNextQ === null && nextIdx >= questions.length) {
                if (fullTurnText) addMessage('ai', fullTurnText);
                if (fullTurnText) await speak(fullTurnText);
                completeInterview();
            } else {
                const nextQ = refinedNextQ || questions[nextIdx] || "Could you tell me more about your experience?";
                setCurrentQuestionIndex(nextIdx);
                setProgress((nextIdx / MAX_QUESTIONS) * 100);

                setQuestions(prev => {
                    const newQs = [...prev];
                    if (nextIdx < newQs.length) newQs[nextIdx] = nextQ;
                    else newQs.push(nextQ);
                    return newQs;
                });

                // De-duplicate if feedback and next question are identical
                const finalTurnText = (fullFeedback.trim() === nextQ.trim())
                    ? nextQ
                    : (fullFeedback.trim() + " " + nextQ);

                addMessage('ai', finalTurnText);
                await speak(finalTurnText);

                setIsProcessing(false);
                isProcessingRef.current = false;
                if (userInputMode === 'audio' && !showQuotaWarning) startListening();
                setAiStatus("Indu is Online");
            }
        } catch (err) {
            console.error("Submission error:", err.code === 'ECONNABORTED' ? "AI Timeout (35s)" : err.message);
            if (err.response?.status === 429) setShowQuotaWarning(true);

            // AUTOMATIC RECOVERY: If the AI engine times out or fails (e.g. Groq is slow), 
            // don't get stuck. Just move to the next question manually.
            const nextIdx = currentQuestionIndex + 1;
            const fallbacks = [
                "Understood. Moving along, let's explore another area.",
                "I see where you're coming from. Let's pivot slightly.",
                "Thanks for that input. Let's touch upon a different technical topic.",
                "Got it. Switching gears, I have a question about your project work."
            ];
            const fallbackMsg = fallbacks[Math.floor(Math.random() * fallbacks.length)];
            const fallbackNextQ = questions[nextIdx] || "Could you tell me more about your overall professional journey?";

            addMessage('ai', fallbackMsg);

            if (nextIdx < questions.length || (typeof fallbackNextQ === 'string' && fallbackNextQ.length > 5)) {
                addMessage('ai', fallbackNextQ);
                await speak(fallbackMsg + " " + fallbackNextQ);
                setCurrentQuestionIndex(nextIdx);
                setProgress((nextIdx / MAX_QUESTIONS) * 100);
            } else {
                await speak(fallbackMsg);
                completeInterview();
            }

            setIsProcessing(false);
            setAiStatus("AI Interviewer Online");
        }
    }, [token, questions, currentQuestionIndex, isProcessing, addMessage, speak, completeInterview, startListening, showQuotaWarning, userInputMode]);

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
                    const res = await axios.get(`${API_BASE_URL}/ai-candidates/${token}/`);
                    setCandidateName(res.data.full_name);
                    const matchRes = await axios.post(`${API_BASE_URL}/ai-candidates/match/`, {
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
            const welcome = `Hi ${firstName}! This is Indu. Hope you're doing well, I'll be your interviewer today.`;

            const introQ = "To get started, please introduce yourself and your professional background.";
            let finalQs = [...qs];
            if (finalQs[0] !== introQ) {
                finalQs = [introQ, ...finalQs];
                setQuestions(finalQs);
            }

            // Combine welcome and intro question for a smooth start
            const combinedStart = `${welcome} ${introQ}`;
            addMessage('ai', combinedStart);
            await speak(combinedStart);
            if (userInputMode === 'audio') startListening();
        };

        initSession();
        return () => stopCamera();
    }, [token, addMessage, speak, startListening, userInputMode]); // Only re-init if token changes, perfectly stable camera feed

    const silenceTimerRef = useRef(null);
    const globalSilenceTimerRef = useRef(null);
    const nudgeCountRef = useRef(0);
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
        recognition.lang = 'en-IN';

        recognition.onstart = () => {
            console.log("INFINITE MIC: Speech recognition is now active and stay on.");
            setIsRecording(true);
            isRecordingRef.current = true;
            setAiStatus("Listening...");
            transcriptRef.current = "";

            // Start Global Silence Watchdog (15s for first nudge)
            startSilenceWatchdog(15000);
        };

        recognition.onresult = (event) => {
            let interimTranscript = "";
            let newFinals = "";

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    newFinals += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (newFinals) {
                transcriptRef.current += newFinals;
            }

            const currentTotal = (transcriptRef.current + interimTranscript).trim();
            if (currentTotal) {
                const display = currentTotal.length > 35 ? '...' + currentTotal.slice(-35) : currentTotal;
                setAiStatus(`Heard: "${display}"`);
            }

            // PATIENT SILENCE: Reset timer every time we hear ANY sound/speech
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
            if (globalSilenceTimerRef.current) {
                clearTimeout(globalSilenceTimerRef.current);
                globalSilenceTimerRef.current = null;
            }

            // Only submit if we have a significant answer length
            if (currentTotal.length > 3) {
                silenceTimerRef.current = setTimeout(() => {
                    const finalSubmission = transcriptRef.current + interimTranscript;
                    if (finalSubmission.trim().length > 4) {
                        console.log("Planned pause detected. Processing answer...");
                        setIsProcessing(true);
                        setAiStatus("Processing answer...");
                        try { recognition.stop(); } catch (e) { }
                        if (submitHandlerRef.current) submitHandlerRef.current(finalSubmission);
                    }
                }, 3500); // 3.5 seconds - perfect balance of patience and speed
            }
        };

        recognition.onerror = (event) => {
            // Ignore no-speech and stay active
            if (event.error === 'no-speech' || event.error === 'aborted') {
                console.log("Mic background silence...");
                return;
            }
            console.warn("Recognition Error:", event.error);
            setIsRecording(false);
            setAiStatus(`Mic ready`);
        };

        recognition.onend = () => {
            setIsRecording(false);
            isRecordingRef.current = false;
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
            if (globalSilenceTimerRef.current) clearTimeout(globalSilenceTimerRef.current); // Clear global timer on recognition end
            console.log("Recognition session ended.");
        };

        recognitionRef.current = recognition;

        return () => {
            if (recognitionRef.current) {
                try { recognitionRef.current.stop(); } catch (e) { }
            }
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
            if (globalSilenceTimerRef.current) clearTimeout(globalSilenceTimerRef.current);
        };
    }, [startSilenceWatchdog]);

    const startSilenceWatchdog = useCallback((delay) => {
        if (globalSilenceTimerRef.current) clearTimeout(globalSilenceTimerRef.current);
        globalSilenceTimerRef.current = setTimeout(async () => {
            if (!isRecordingRef.current || isProcessingRef.current || isSpeakingRef.current) return;

            if (nudgeCountRef.current === 0) {
                // First nudge
                nudgeCountRef.current = 1;
                const nudgeText = "I didn't quite catch that. Could you please share your answer when you're ready?";
                addMessage('ai', nudgeText);
                try {
                    if (recognitionRef.current) recognitionRef.current.stop();
                    await speak(nudgeText);
                    startListening(); // Restart with a fresh 15s timer
                } catch (e) { }
            } else {
                // Second nudge = AUTO SKIP
                const skipText = "It seems you're having some trouble. Let's move to the next question for now.";
                addMessage('ai', skipText);
                try {
                    if (recognitionRef.current) recognitionRef.current.stop();
                    await speak(skipText);
                    // Force submission with a "skipped" tag
                    if (submitHandlerRef.current) submitHandlerRef.current("[Candidate remained silent/skipped]");
                } catch (e) { }
            }
        }, delay);
    }, [addMessage, speak, startListening]);


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
                    <div style={{ flex: 1, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', paddingBottom: '0.5rem' }}>
                        <ReadyPlayerMeAvatar isSpeaking={isSpeaking} />
                    </div>
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

                    {/* Live Transcript Display */}
                    {(isRecording && aiStatus.startsWith('Heard:')) && (
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