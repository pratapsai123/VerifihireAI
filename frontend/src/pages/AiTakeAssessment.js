import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
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

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });
            if (videoRef.current) videoRef.current.srcObject = stream;
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

    if (!isStarted) return (
        <div style={{ background: '#F4F7FE', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', fontFamily: 'Poppins', padding: '20px' }}>
            <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '3rem', background: 'white', borderRadius: '30px', boxShadow: '0 20px 50px rgba(0,0,0,0.05)' }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div style={{ width: '70px', height: '70px', background: '#F4F7FE', borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem', color: '#4318FF', fontSize: '1.8rem' }}>
                        <i className="fa-solid fa-user-pen"></i>
                    </div>
                    <h1 style={{ color: '#1B254B', fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>Candidate Intake</h1>
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

    return (
        <div style={{ background: '#F4F7FE', minHeight: '100vh', padding: '40px 20px', fontFamily: 'Poppins' }}>
            <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>

                {/* Left Side: Questions */}
                <div style={{ minWidth: 0 }}>
                    <div className="card" style={{ padding: '2rem', marginBottom: '2rem', background: 'white', borderRadius: '25px', boxShadow: '0 10px 30px rgba(0,0,0,0.03)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <h1 style={{ color: '#1B254B', margin: '0 0 0.5rem', fontSize: '1.6rem' }}>Technical Assessment</h1>
                                <p style={{ color: '#707EAE', margin: 0 }}>Skills: <span style={{ color: '#4318FF', fontWeight: '600' }}>{assessment.required_skills}</span></p>
                            </div>
                            <div style={{ background: timeLeft < 300 ? '#FFF5F5' : '#F4F7FE', padding: '0.8rem 1.5rem', borderRadius: '15px', border: '1px solid', borderColor: timeLeft < 300 ? '#FEB2B2' : '#E0E5F2', textAlign: 'center' }}>
                                <div style={{ fontSize: '0.7rem', color: timeLeft < 300 ? '#E53E3E' : '#707EAE', fontWeight: '700', textTransform: 'uppercase' }}>Time Remaining</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: '800', color: timeLeft < 300 ? '#E53E3E' : '#1B254B' }}>{formatTime(timeLeft)}</div>
                            </div>
                        </div>
                    </div>

                    {/* Questions loop... */}
                    {mcqs.length > 0 && (
                        <div style={{ marginBottom: '2rem' }}>
                            <h2 style={{ color: '#1B254B', marginBottom: '1.5rem', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                                <i className="fa-solid fa-list-check" style={{ color: '#4318FF' }}></i> Multiple Choice
                            </h2>
                            {mcqs.map((q, idx) => (
                                <div key={idx} className="card" style={{ padding: '2rem', marginBottom: '1.5rem', background: 'white', borderRadius: '20px' }}>
                                    <p style={{ fontWeight: '600', color: '#2B3674', fontSize: '1.05rem', marginBottom: '1.2rem' }}>{idx + 1}. {q.question}</p>
                                    <div style={{ display: 'grid', gap: '0.8rem' }}>
                                        {q.options.map((opt, optIdx) => (
                                            <label key={optIdx} style={{ display: 'flex', alignItems: 'center', padding: '1rem', background: answers[`mcq_${idx}`] === opt ? '#F0F3FF' : '#F8F9FF', borderRadius: '12px', cursor: 'pointer', border: '2px solid', borderColor: answers[`mcq_${idx}`] === opt ? '#4318FF' : 'transparent', transition: 'all 0.2s' }}>
                                                <input type="radio" name={`q-${idx}`} checked={answers[`mcq_${idx}`] === opt} onChange={() => handleAnswerChange(`mcq_${idx}`, opt)} style={{ marginRight: '15px', accentColor: '#4318FF' }} />
                                                <span style={{ color: '#1B254B', fontWeight: '500' }}>{opt}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {coding.length > 0 && (
                        <div style={{ marginBottom: '3rem' }}>
                            <h2 style={{ color: '#1B254B', marginBottom: '1.5rem', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                                <i className="fa-solid fa-code" style={{ color: '#4318FF' }}></i> Coding Challenges
                            </h2>
                            {coding.map((c, idx) => (
                                <div key={idx} className="card" style={{ padding: '2rem', marginBottom: '1.5rem', background: 'white', borderRadius: '20px' }}>
                                    <h3 style={{ color: '#1B254B', fontSize: '1.1rem', marginBottom: '0.8rem' }}>{c.title}</h3>
                                    <p style={{ color: '#707EAE', fontSize: '0.9rem', lineHeight: '1.6', marginBottom: '1.2rem' }}>{c.problem_statement}</p>
                                    <textarea
                                        placeholder="Write your solution code here..."
                                        style={{ width: '100%', height: '240px', padding: '1.2rem', borderRadius: '12px', border: '1px solid #E0E5F2', fontFamily: 'Monaco, monospace', fontSize: '0.9rem', outline: 'none', background: '#F8F9FF' }}
                                        onChange={(e) => handleAnswerChange(`coding_${idx}`, e.target.value)}
                                    ></textarea>
                                </div>
                            ))}
                        </div>
                    )}

                    <button
                        onClick={handleSubmit} disabled={isSubmitting}
                        style={{ width: '100%', padding: '1.2rem', background: '#4318FF', color: 'white', border: 'none', borderRadius: '15px', fontSize: '1.1rem', fontWeight: '700', cursor: 'pointer', boxShadow: '0 10px 20px rgba(67, 24, 255, 0.2)', opacity: isSubmitting ? 0.7 : 1 }}
                    >
                        {isSubmitting ? 'Submitting...' : 'Complete Assessment'}
                    </button>
                </div>

                {/* Right Side: Monitoring Sidebar */}
                <div style={{ position: 'sticky', top: '20px', height: 'fit-content' }}>
                    <div className="card" style={{ padding: '1.5rem', background: 'white', borderRadius: '25px', boxShadow: '0 10px 30px rgba(0,0,0,0.05)', textAlign: 'center' }}>
                        <div style={{ position: 'relative', width: '100%', aspectRatio: '4/3', background: '#000', borderRadius: '15px', overflow: 'hidden', marginBottom: '1.5rem' }}>
                            <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                            {aiToast.active && (
                                <div style={{ position: 'absolute', bottom: '10px', left: '50%', transform: 'translateX(-50%)', background: aiToast.urgent ? '#e11d48' : '#4318FF', color: 'white', padding: '5px 10px', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '700', whiteSpace: 'nowrap', animation: 'shake 0.5s' }}>
                                    {aiToast.text}
                                </div>
                            )}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#05CD99', fontSize: '0.85rem', fontWeight: '600' }}>
                            <span style={{ width: '8px', height: '8px', background: '#05CD99', borderRadius: '50%', display: 'inline-block' }}></span>
                            AI Monitoring Active
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default AiTakeAssessment;
