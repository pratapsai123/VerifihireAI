import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import RecordRTC, { StereoAudioRecorder } from 'recordrtc';
import { RealtimeTranscriber } from 'assemblyai';
import ReadyPlayerMeAvatar from '../components/ReadyPlayerMeAvatar';
import '../styles/Dashboard.css';
import '../styles/AiInterviewSession.css';
import { API_BASE_URL } from '../apiConfig';

const AiInterviewSession = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [candidateName, setCandidateName] = useState('Candidate');
    const [maxQuestions, setMaxQuestions] = useState(10);
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
    const [isCompleted, setIsCompleted] = useState(false);
    const [timeLeft, setTimeLeft] = useState(null); // Timer in seconds
    const [sttReady, setSttReady] = useState(false); // New state for WS status
    const [silenceCountdown, setSilenceCountdown] = useState(0);

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
    const unlockSpeech = useCallback(() => {
        if (!synthRef.current) return;
        // Playing a silent 0.01s utterance unlocks the browser's speech synthesis
        const silentU = new SpeechSynthesisUtterance(" ");
        silentU.volume = 0;
        synthRef.current.speak(silentU);
    }, []);

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
            const voice =
                voicesRef.current.find(v => (v.name.includes('Siri') || v.name.includes('Samantha')) && v.name.toLowerCase().includes('female')) ||
                voicesRef.current.find(v => v.name.includes('Google US English') && v.name.toLowerCase().includes('female')) ||
                voicesRef.current.find(v => (v.name.includes('Jenny') || v.name.includes('Aria')) && v.name.toLowerCase().includes('female')) ||
                voicesRef.current.find(v => v.name.toLowerCase().includes('female')) ||
                voicesRef.current.find(v => v.name.includes('Siri') || v.name.includes('Samantha')) ||
                voicesRef.current.find(v => v.lang.startsWith('en')) ||
                voicesRef.current[0];

            if (voice) {
                utterance.voice = voice;
            }

            utterance.onstart = () => {
                setIsSpeaking(true);
                isSpeakingRef.current = true;
                setAiStatus("Speaking...");
                // Physically mute the mic hardware so it captures zero audio while Indu speaks
                if (micStreamRef.current) {
                    micStreamRef.current.getAudioTracks().forEach(track => { track.enabled = false; });
                }
            };

            utterance.onend = () => {
                clearTimeout(watchdog);
                // Delay the unlock by 500ms to allow physical speaker audio tail (echo) to finish
                setTimeout(() => {
                    setIsSpeaking(false);
                    isSpeakingRef.current = false;
                    // Re-enable the mic hardware
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
                clearTimeout(watchdog);
                setIsSpeaking(false);
                isSpeakingRef.current = false;
                setAiStatus("Indu is Online");
                resolve();
            };

            setIsSpeaking(true);
            isSpeakingRef.current = true;
            synthRef.current.speak(utterance);
        });
    }, []);

    const addMessage = useCallback((sender, text) => {
        const displayText = typeof text === 'object' ? (text.question || JSON.stringify(text)) : text;
        setChatMessages(prev => {
            // Optional: De-duplicate consecutive identical AI messages
            if (prev.length > 0 && prev[prev.length - 1].sender === sender && prev[prev.length - 1].text === displayText) {
                return prev;
            }
            return [...prev, { sender, text: displayText }];
        });
        chatHistoryRef.current.push({ role: sender === 'ai' ? 'assistant' : 'user', content: displayText });
    }, []);

    const completeInterview = useCallback(async (customMessage = null) => {
        if (isCompletedRef.current) return;
        isCompletedRef.current = true;
        setIsCompleted(true);
        stopCamera();
        const finishMessage = customMessage || "The interview is now complete. Thank you for your time and we will get back to you soon. Goodbye!";
        addMessage('ai', finishMessage);
        await speak(finishMessage);
        axios.patch(`${API_BASE_URL}/ai-candidates/${token}/status/`, { status: 'Completed' }).catch(console.error);

        // Mark as completed locally to prevent re-opening link
        localStorage.setItem(`interview_completed_${token}`, 'true');

        setIsProcessing(true);
        setAiStatus("Session Finished");
    }, [token, speak, addMessage]);

    const startSilenceWatchdog = useCallback((delay) => {
        if (globalSilenceTimerRef.current) clearInterval(globalSilenceTimerRef.current);
        lastSpokenTimeRef.current = Date.now(); // Baseline reset
        globalSilenceTimerRef.current = setInterval(async () => {
            if (!isRecordingRef.current || isProcessingRef.current || isSpeakingRef.current) {
                lastSpokenTimeRef.current = Date.now(); // Move baseline forward while busy
                return;
            }

            if (Date.now() - lastSpokenTimeRef.current > delay) {
                clearInterval(globalSilenceTimerRef.current);
                if (nudgeCountRef.current === 0) {
                    // First nudge
                nudgeCountRef.current = 1;
                const nudgeText = "I didn't quite catch that. Could you please share your answer when you're ready?";
                addMessage('ai', nudgeText);
                try {
                    if (assemblyAIRef.current) assemblyAIRef.current.stop();
                    await speak(nudgeText);
                    if (startListeningRef.current) startListeningRef.current(); // Restart with a fresh 15s timer via ref
                } catch (e) { }
            } else {
                // Second nudge = AUTO SKIP
                const skipText = "It seems you're having some trouble. Let's move to the next question for now.";
                addMessage('ai', skipText);
                try {
                    if (assemblyAIRef.current) assemblyAIRef.current.stop();
                    await speak(skipText);
                    // Force submission with a "skipped" tag
                    if (submitHandlerRef.current) submitHandlerRef.current("[Candidate remained silent/skipped]");
                } catch (e) { }
            }
        }
        }, 1000);
    }, [addMessage, speak]);

    const startListening = useCallback(async () => {
        if (userInputMode !== 'audio' || isRecordingRef.current) return;

        let attempts = 0;
        const maxAttempts = 10;

        const tryStart = async () => {
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
                    while(audioBufferQueue.length > 0) {
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
                            for(let i = 0; i < visualBins; i++) {
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
                        for(let i = 2; i < 12; i++) {
                            vocalVolume += dataArray[i];
                        }
                        const averageVocal = vocalVolume / 10;
                        if (averageVocal > 110) isSpeakingLocal = true; // Increased threshold to 110 to ignore background noise/fans
                        
                        for(let i = 0; i < visualBins; i++) {
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
                } catch(e) { console.error("Visualizer Error:", e); }

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

                assemblyAIRef.current = {
                    stop: () => {
                        try {
                            if (animationRef.current) cancelAnimationFrame(animationRef.current);
                            if (visualizerCtxRef.current) {
                                visualizerCtxRef.current.close().catch(e => {});
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
                                
                                for(let i = 0; i < visualBins; i++) {
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
                                    try { if (recorder && recorder.destroy) recorder.destroy(); } catch(e){}
                                }, 1500);
                            });
                            ws.close(1000); // 1000 = Normal Closure, prevents auto-reconnect loops
                        } catch (e) { }
                    }
                };

                // Allow toggle functions to use this reference logic
                recognitionRef.current = assemblyAIRef.current;

            } catch (e) {
                console.error("AssemblyAI start error:", e);
                setIsRecording(false);
                isRecordingRef.current = false;
            }
        };

        tryStart();

        return () => {
            if (assemblyAIRef.current) {
                try { assemblyAIRef.current.stop(); } catch (e) { }
            }
        };
    }, [userInputMode, startSilenceWatchdog]);

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
        if (globalSilenceTimerRef.current) clearInterval(globalSilenceTimerRef.current);

        // 2. Force Microphone Stop
        if (recognitionRef.current) {
            try { recognitionRef.current.stop(); } catch (e) { }
        }
        if (silenceTimerRef.current) clearInterval(silenceTimerRef.current);
        setSilenceCountdown(0);

        // 3. Track Consecutive Silence (to end interview if candidate leaves)
        if (answer === "[Candidate remained silent/skipped]") {
            consecutiveSilenceRef.current += 1;
        } else {
            consecutiveSilenceRef.current = 0;
        }

        if (consecutiveSilenceRef.current >= 3) {
            console.log("Consecutive silence limit reached (3). Ending interview.");
            completeInterview("The interview has been ended due to lack of response. We will review the answers provided so far. Thank you.");
            return;
        }

        addMessage('user', answer);
        setResponseInput('');
        
        // 3. Clear all speech buffers to prevent the "Repeated Input" bug
        transcriptRef.current = "";
        interimTranscriptRef.current = "";
        lastTranscriptStrRef.current = "";
        lastSpokenTimeRef.current = Date.now();
        
        console.log("Submitting answer turn...");

        try {
            const currentQ = questions[currentQuestionIndex] || "Introduction and Background";
            const response = await axios.post(`${API_BASE_URL}/ai-candidates/process-answer/`, {
                candidate_id: token,
                question: typeof currentQ === 'object' ? currentQ.question : currentQ,
                answer: answer,
                remaining_questions: questions.slice(currentQuestionIndex + 1),
                chat_history: chatHistoryRef.current
            }, { timeout: 60000 }); // 60s for more complex reasoning (increased for stability)

            const data = response.data;
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

            // --- HARD STOP: end after maxQuestions ---
            if (totalAnswered >= maxQuestions) {
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
                    try { if (assemblyAIRef.current) assemblyAIRef.current.stop(); } catch(e){}
                    setIsRecording(false);
                    isRecordingRef.current = false;
                } else {
                    setAiStatus("Indu is Online");
                }

                await speak(followUpText);
                setIsProcessing(false);
                isProcessingRef.current = false;

                if (effectiveMode === 'audio' && !showQuotaWarning) startListening();
            } else if (refinedNextQ === null && nextIdx >= questions.length) {
                if (fullTurnText) addMessage('ai', fullTurnText);
                if (fullTurnText) await speak(fullTurnText);
                completeInterview();
            } else {
                const nextQ = refinedNextQ || questions[nextIdx] || "Could you tell me more about your experience?";
                setCurrentQuestionIndex(nextIdx);
                setProgress((nextIdx / maxQuestions) * 100);

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
                // we don't want "No worries, let's move on" right before the goodbye.
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
                    try { if (assemblyAIRef.current) assemblyAIRef.current.stop(); } catch(e){}
                    setIsRecording(false);
                    isRecordingRef.current = false;
                } else {
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
                if (effectiveMode === 'audio' && !showQuotaWarning) {
                    startListening();
                }
            }
        } catch (err) {
            console.error("Submission error:", err.code === 'ECONNABORTED' ? "AI Timeout (60s)" : err.message);

            // ALWAYS reset processing state so the UI doesn't "stick"
            setIsProcessing(false);
            isProcessingRef.current = false;

            if (err.response?.status === 429 || err.response?.data?.retryable) {
                // Track retry count to prevent infinite loops
                const currentRetry = (answer._retryCount || 0);
                const maxRetries = 3;
                
                if (currentRetry < maxRetries) {
                    const backoffDelay = 8000 * Math.pow(2, currentRetry); // 8s, 16s, 32s
                    const retryMsg = `AI is busy... retrying in ${backoffDelay / 1000}s (attempt ${currentRetry + 1}/${maxRetries})`;
                    setAiStatus(retryMsg);
                    setShowQuotaWarning(true);
                    
                    setTimeout(() => {
                        setShowQuotaWarning(false);
                        // Tag the answer string with retry count
                        const taggedAnswer = new String(answer);
                        taggedAnswer._retryCount = currentRetry + 1;
                        handleAnswerSubmission(taggedAnswer);
                    }, backoffDelay);
                } else {
                    // Max retries exceeded — give up gracefully and move on
                    setShowQuotaWarning(false);
                    const sorryMsg = "I apologize, there seems to be a temporary issue on my end. Let's move on to the next question.";
                    addMessage('ai', sorryMsg);
                    await speak(sorryMsg);
                    setIsProcessing(false);
                    isProcessingRef.current = false;
                    if (userInputMode === 'audio' && !showQuotaWarning) startListening();
                    setAiStatus("Indu is Online");
                }
                return;
            }

            // Show AI failure popup
            const errorMessage = err.response?.data?.error || err.message || "Unknown error";
            setAiStatus("Connection Issue");
            alert(`AI is having trouble connecting. Please try again.\nError: ${errorMessage}`);

            // Automatically try to restart the mic to help the user
            if (userInputMode === 'audio') {
                setTimeout(() => startListening(), 1000);
            }
        }
    }, [token, questions, currentQuestionIndex, isProcessing, addMessage, speak, completeInterview, startListening, showQuotaWarning, userInputMode]);

    // 4. Lifecycle
    useEffect(() => {
        if (isInitializedRef.current) return;
        isInitializedRef.current = true;

        const initSession = async () => {
            // Check localStorage first for instant blocking
            if (localStorage.getItem(`interview_completed_${token}`)) {
                setAiToast({ active: true, text: 'You have already completed this interview.', urgent: true });
                setIsCompleted(true);
                return;
            }

            const res = await axios.get(`${API_BASE_URL}/ai-candidates/${token}/?_t=${Date.now()}`);
            const candidate = res.data;
            setCandidateName(candidate.full_name);

            // 1. Timer Initialization
            if (candidate.link_opened_at) {
                const startTime = new Date(candidate.link_opened_at).getTime();
                const now = new Date().getTime();
                const secondsElapsed = Math.floor((now - startTime) / 1000);
                const initialTimeLeft = Math.max(0, (60 * 60) - secondsElapsed);
                setTimeLeft(initialTimeLeft);
            }

            // 2. Persistence Logic: Check if we have history
            if (candidate.interview_summary && candidate.interview_summary.length > 0) {
                console.log("Restoring session from backend summary...");
                const summary = candidate.interview_summary;

                // Reconstruct Chat History
                const restoredMessages = [];
                const restoredHistory = [];
                summary.forEach(turn => {
                    restoredMessages.push({ sender: 'ai', text: turn.question });
                    restoredMessages.push({ sender: 'user', text: turn.answer });
                    restoredHistory.push({ role: 'assistant', content: turn.question });
                    restoredHistory.push({ role: 'user', content: turn.answer });
                });

                setChatMessages(restoredMessages);
                chatHistoryRef.current = restoredHistory;

                const nextIdx = summary.length;
                setCurrentQuestionIndex(nextIdx);
                setProgress((nextIdx / maxQuestions) * 100);

                const currentQs = candidate.interview_questions || [];
                setQuestions(currentQs);

                await startCamera();
                setAiStatus("Resuming Session...");

                // Ask the current question again (or the next one)
                const resumeQ = currentQs[nextIdx] || "Let's continue. Please share more about your experience.";
                addMessage('ai', resumeQ);
                await speak(resumeQ);
                if (userInputMode === 'audio') startListening();

            } else {
                // Fresh Start or SessionStorage fallback
                const storedData = sessionStorage.getItem('interviewData');
                if (storedData) {
                    const data = JSON.parse(storedData);
                    setQuestions(data.questions);
                    startInterview(data.candidateName, data.questions);
                } else {
                    const qList = candidate.interview_questions || [];
                    setQuestions(qList);
                    startInterview(candidate.full_name, qList);
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

    useEffect(() => {
        startListeningRef.current = startListening;
    }, [startListening]);

    useEffect(() => {
        submitHandlerRef.current = handleAnswerSubmission;
    }, [handleAnswerSubmission]);

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
                return;
            }

            // Otherwise, proceed with the visible countdown (5-4-3-2-1)
            secondsRemaining = 5 - Math.floor((timeSinceActivity - 2000) / 1000);
            
            if (secondsRemaining > 0) {
                setSilenceCountdown(secondsRemaining + "s");
            } else if (secondsRemaining === 0 || secondsRemaining === -1) {
                setSilenceCountdown("..."); 
            } else if (secondsRemaining <= -2) {
                // TRUE EXPIRATION
                console.log("Unified Watchdog: Maximum silence exceeded. Forcing submission.");
                clearInterval(watchdog);
                setSilenceCountdown(0);
                setIsProcessing(true);
                setAiStatus("Processing answer...");
                
                if (assemblyAIRef.current) {
                    try { assemblyAIRef.current.stop(); } catch(e) {}
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
        // Unlock speech on first user click if not already
        unlockSpeech();

        if (isRecording) {
            // Capture any final speech before stopping
            const finalSubmission = (transcriptRef.current + interimTranscriptRef.current).trim();
            
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

        const timer = setInterval(() => {
            setTimeLeft(prev => prev - 1);
        }, 1000);

        return () => clearInterval(timer);
    }, [timeLeft, isCompleted, completeInterview]);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    useEffect(() => {
        return () => {
            if (animationRef.current) cancelAnimationFrame(animationRef.current);
            if (visualizerCtxRef.current) {
                try { visualizerCtxRef.current.close(); } catch(e){}
            }
        };
    }, []);

    return (
        <div className="ai-session-page">
            {showQuotaWarning && (
                <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', padding: '15px', background: '#667eea', color: 'white', textAlign: 'center', zIndex: 10000, fontWeight: 'bold', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
                    ⏳ Indu is taking a moment to think (AI Busy). Please wait, your answer is being saved and will process automatically...
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
                        {chatMessages.map((msg, i) => <div key={i} className={`message ${msg.sender}`}>{msg.text}</div>)}
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
                                    disabled={isProcessing}
                                    className={`mic-btn ${isRecording ? 'listening' : ''}`}
                                    style={{ width: '40px', height: '40px', fontSize: '1rem', cursor: isProcessing ? 'not-allowed' : 'pointer', opacity: isProcessing ? 0.6 : 1 }}
                                >
                                    <i className={isRecording ? "fa-solid fa-stop" : "fa-solid fa-microphone"}></i>
                                </button>
                                <span style={{ color: '#4a5568', fontWeight: 600, fontSize: '0.8rem' }}>{isRecording ? "Listening..." : "Click to Speak"}</span>
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
            {isCompleted && (
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
            )}
        </div>
    );
};

export default AiInterviewSession;