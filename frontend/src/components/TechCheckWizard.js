import React, { useState, useEffect, useRef } from 'react';

const TechCheckWizard = ({ onComplete }) => {
    const [step, setStep] = useState(1);
    const [networkStatus, setNetworkStatus] = useState('pending'); // pending, testing, success, fail
    const [micStatus, setMicStatus] = useState('pending'); // pending, recording, playing, success, fail
    const [cameraStatus, setCameraStatus] = useState('pending'); // pending, checking, success, fail
    
    // Refs for streams and media
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const micStreamRef = useRef(null);
    const camStreamRef = useRef(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const canvasVisualizerRef = useRef(null);
    const animationFrameRef = useRef(null);

    // Clean up streams on unmount
    useEffect(() => {
        return () => {
            stopAllStreams();
        };
    }, []);

    const stopAllStreams = () => {
        if (micStreamRef.current) {
            micStreamRef.current.getTracks().forEach(t => t.stop());
            micStreamRef.current = null;
        }
        if (camStreamRef.current) {
            camStreamRef.current.getTracks().forEach(t => t.stop());
            camStreamRef.current = null;
        }
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
        }
    };

    // Step 1: Network Test
    const runNetworkTest = async () => {
        setNetworkStatus('testing');
        try {
            // Simple latency test using a public reliable endpoint or our API
            const startTime = Date.now();
            await fetch('https://api.github.com/zen', { cache: 'no-store' });
            const latency = Date.now() - startTime;
            
            if (latency < 1000) {
                setTimeout(() => setNetworkStatus('success'), 1000);
            } else {
                setNetworkStatus('fail');
            }
        } catch (e) {
            setNetworkStatus('fail');
        }
    };

    // Step 2: Mic Test
    const runMicTest = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            micStreamRef.current = stream;
            setMicStatus('recording');
            
            // Setup visualizer
            audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
            analyserRef.current = audioContextRef.current.createAnalyser();
            const source = audioContextRef.current.createMediaStreamSource(stream);
            source.connect(analyserRef.current);
            analyserRef.current.fftSize = 256;
            
            drawAudioVisualizer();

            // Record 3 seconds
            mediaRecorderRef.current = new MediaRecorder(stream);
            audioChunksRef.current = [];
            
            mediaRecorderRef.current.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunksRef.current.push(e.data);
            };
            
            mediaRecorderRef.current.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                setMicStatus('playing');
                audio.play();
                audio.onended = () => {
                    setMicStatus('success');
                };
            };

            mediaRecorderRef.current.start();
            setTimeout(() => {
                if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
                    mediaRecorderRef.current.stop();
                }
            }, 3000);

        } catch (e) {
            console.error("Mic test error:", e);
            setMicStatus('fail');
        }
    };

    const drawAudioVisualizer = () => {
        if (!canvasVisualizerRef.current || !analyserRef.current) return;
        const canvas = canvasVisualizerRef.current;
        const ctx = canvas.getContext('2d');
        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const draw = () => {
            animationFrameRef.current = requestAnimationFrame(draw);
            analyserRef.current.getByteFrequencyData(dataArray);
            
            ctx.fillStyle = '#f8fafc';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const barWidth = (canvas.width / bufferLength) * 2.5;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                const barHeight = dataArray[i] / 2;
                ctx.fillStyle = `rgb(${barHeight + 100}, 100, 250)`;
                ctx.fillRect(x, canvas.height - barHeight / 2, barWidth, barHeight / 2);
                x += barWidth + 1;
            }
        };
        draw();
    };

    // Step 3: Camera & Lighting Test
    const runCameraTest = async () => {
        try {
            setCameraStatus('checking');
            const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: "user" } });
            camStreamRef.current = stream;
            
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.play();
            }

            // Check lighting after a short delay to let camera adjust
            setTimeout(() => {
                checkLighting();
            }, 1500);

        } catch (e) {
            console.error("Camera test error:", e);
            setCameraStatus('fail');
        }
    };

    const checkLighting = () => {
        if (!videoRef.current || !canvasRef.current) {
            setCameraStatus('fail');
            return;
        }

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        
        let brightness = 0;
        for (let i = 0; i < data.length; i += 4) {
            // Calculate luminance
            brightness += (0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
        }
        
        brightness = brightness / (data.length / 4);
        
        // Very simple threshold: 0 is black, 255 is white.
        if (brightness > 40 && brightness < 240) {
            setCameraStatus('success');
        } else {
            setCameraStatus('fail');
        }
    };

    const handleNext = () => {
        if (step === 1) {
            setStep(2);
        } else if (step === 2) {
            if (micStreamRef.current) {
                micStreamRef.current.getTracks().forEach(t => t.stop());
            }
            if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
            setStep(3);
            runCameraTest();
        } else if (step === 3) {
            stopAllStreams();
            onComplete();
        }
    };

    const styles = {
        overlay: { position: 'fixed', inset: 0, background: 'rgba(255, 255, 255, 0.98)', zIndex: 35000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' },
        card: { maxWidth: '600px', width: '100%', background: 'white', padding: '2.5rem', borderRadius: '30px', boxShadow: '0 20px 50px rgba(0,0,0,0.1)', textAlign: 'center' },
        title: { fontSize: '1.8rem', color: '#1a202c', marginBottom: '1rem', fontWeight: '800' },
        button: { background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none', padding: '1rem 2rem', borderRadius: '50px', fontSize: '1.1rem', fontWeight: '700', cursor: 'pointer', marginTop: '2rem', transition: 'all 0.2s', boxShadow: '0 10px 20px rgba(102, 126, 234, 0.3)' },
        buttonDisabled: { background: '#cbd5e1', cursor: 'not-allowed', color: 'white', border: 'none', padding: '1rem 2rem', borderRadius: '50px', fontSize: '1.1rem', fontWeight: '700', marginTop: '2rem' },
        iconBox: { width: '80px', height: '80px', borderRadius: '50%', background: '#e0e7ff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', color: '#6366f1', margin: '0 auto 1.5rem' }
    };

    return (
        <div style={styles.overlay}>
            <div style={styles.card}>
                <h2 style={styles.title}>System Tech Check</h2>
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginBottom: '2rem' }}>
                    <div style={{ height: '6px', flex: 1, borderRadius: '3px', background: step >= 1 ? '#6366f1' : '#e2e8f0' }}></div>
                    <div style={{ height: '6px', flex: 1, borderRadius: '3px', background: step >= 2 ? '#6366f1' : '#e2e8f0' }}></div>
                    <div style={{ height: '6px', flex: 1, borderRadius: '3px', background: step >= 3 ? '#6366f1' : '#e2e8f0' }}></div>
                </div>

                {step === 1 && (
                    <div>
                        <div style={styles.iconBox}><i className="fa-solid fa-wifi"></i></div>
                        <h3 style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Network Speed</h3>
                        <p style={{ color: '#64748b', marginBottom: '2rem' }}>We need to make sure your internet connection is stable for the video interview.</p>
                        
                        {networkStatus === 'pending' && <button onClick={runNetworkTest} style={styles.button}>Run Test</button>}
                        {networkStatus === 'testing' && <p style={{ color: '#6366f1', fontWeight: 'bold' }}>Testing latency...</p>}
                        {networkStatus === 'success' && <div><p style={{ color: '#22c55e', fontWeight: 'bold' }}>✓ Connection is excellent!</p><button onClick={handleNext} style={styles.button}>Next Step</button></div>}
                        {networkStatus === 'fail' && <div><p style={{ color: '#ef4444', fontWeight: 'bold' }}>✗ Connection is weak or failed. Please check your network.</p><button onClick={runNetworkTest} style={{...styles.button, marginRight: '1rem'}}>Retry</button><button onClick={handleNext} style={{...styles.button, background: '#94a3b8'}}>Skip Anyway</button></div>}
                    </div>
                )}

                {step === 2 && (
                    <div>
                        <div style={styles.iconBox}><i className="fa-solid fa-microphone"></i></div>
                        <h3 style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Microphone Check</h3>
                        <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>We'll record you for 3 seconds and play it back to ensure your microphone works.</p>
                        
                        <div style={{ width: '100%', height: '40px', background: '#f8fafc', borderRadius: '8px', marginBottom: '1rem', overflow: 'hidden' }}>
                            <canvas ref={canvasVisualizerRef} width="400" height="40" style={{ width: '100%', height: '100%' }}></canvas>
                        </div>

                        {micStatus === 'pending' && <button onClick={runMicTest} style={styles.button}>Start Recording (3s)</button>}
                        {micStatus === 'recording' && <p style={{ color: '#ef4444', fontWeight: 'bold', animation: 'pulse 1s infinite' }}>🔴 Recording...</p>}
                        {micStatus === 'playing' && <p style={{ color: '#6366f1', fontWeight: 'bold' }}>🔊 Playing back your audio...</p>}
                        {micStatus === 'success' && <div><p style={{ color: '#22c55e', fontWeight: 'bold' }}>✓ Did you hear yourself clearly?</p><button onClick={handleNext} style={styles.button}>Yes, Next Step</button><button onClick={runMicTest} style={{...styles.button, background: '#94a3b8', marginLeft: '1rem'}}>Retry Test</button></div>}
                        {micStatus === 'fail' && <div><p style={{ color: '#ef4444', fontWeight: 'bold' }}>✗ Microphone error. Please check permissions.</p><button onClick={runMicTest} style={{...styles.button, marginRight: '1rem'}}>Retry</button><button onClick={handleNext} style={{...styles.button, background: '#94a3b8'}}>Skip Anyway</button></div>}
                    </div>
                )}

                {step === 3 && (
                    <div>
                        <div style={styles.iconBox}><i className="fa-solid fa-video"></i></div>
                        <h3 style={{ fontSize: '1.4rem', marginBottom: '1rem' }}>Camera & Lighting Check</h3>
                        <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>Make sure your face is clearly visible and well-lit.</p>
                        
                        <div style={{ position: 'relative', width: '320px', height: '240px', margin: '0 auto 1.5rem', borderRadius: '12px', overflow: 'hidden', background: '#000' }}>
                            <video ref={videoRef} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} autoPlay playsInline muted></video>
                            <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
                        </div>

                        {cameraStatus === 'pending' && <button onClick={runCameraTest} style={styles.button}>Enable Camera</button>}
                        {cameraStatus === 'checking' && <p style={{ color: '#f59e0b', fontWeight: 'bold' }}>Checking lighting...</p>}
                        {cameraStatus === 'success' && <div><p style={{ color: '#22c55e', fontWeight: 'bold' }}>✓ Camera and lighting look great!</p><button onClick={handleNext} style={styles.button}>Complete Setup</button></div>}
                        {cameraStatus === 'fail' && <div><p style={{ color: '#ef4444', fontWeight: 'bold' }}>⚠ Lighting might be too dark or too bright, but you can continue.</p><button onClick={runCameraTest} style={{...styles.button, marginRight: '1rem'}}>Retry</button><button onClick={handleNext} style={styles.button}>Continue Anyway</button></div>}
                    </div>
                )}
            </div>
        </div>
    );
};

export default TechCheckWizard;
