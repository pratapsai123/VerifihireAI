import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import { ROUTES, generatePath } from '../routes';

// Parse time string like "10:00 AM", "10 AM", "14:30" into a Date object (today)
function parseScheduledTime(timeStr) {
    if (!timeStr) return null;
    const str = timeStr.trim().toUpperCase();
    let hours = 0, minutes = 0;

    // Try "HH:MM AM/PM"
    let match = str.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/);
    if (match) {
        hours = parseInt(match[1]);
        minutes = parseInt(match[2]);
        if (match[3] === 'PM' && hours !== 12) hours += 12;
        if (match[3] === 'AM' && hours === 12) hours = 0;
    } else {
        // Try "H AM/PM"
        match = str.match(/^(\d{1,2})\s*(AM|PM)$/);
        if (match) {
            hours = parseInt(match[1]);
            if (match[2] === 'PM' && hours !== 12) hours += 12;
            if (match[2] === 'AM' && hours === 12) hours = 0;
        } else {
            // Try "HH:MM" 24-hr
            match = str.match(/^(\d{1,2}):(\d{2})$/);
            if (match) {
                hours = parseInt(match[1]);
                minutes = parseInt(match[2]);
            } else {
                return null;
            }
        }
    }

    const d = new Date();
    d.setHours(hours, minutes, 0, 0);
    return d;
}

// Returns { allowed: bool, secondsUntil: number (negative means past window) }
function checkTimeWindow(scheduledTime, windowMinutes = 30) {
    if (!scheduledTime) return { allowed: true, secondsUntil: 0 };
    const now = new Date();
    const windowEnd = new Date(scheduledTime.getTime() + windowMinutes * 60000);
    if (now < scheduledTime) {
        return { allowed: false, secondsUntil: Math.ceil((scheduledTime - now) / 1000) };
    }
    if (now > windowEnd) {
        return { allowed: false, secondsUntil: -1 };
    }
    return { allowed: true, secondsUntil: 0 };
}

function formatCountdown(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
}

const InterviewStart = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [candidate, setCandidate] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [linkExpired, setLinkExpired] = useState(false);
    const [resumeFile, setResumeFile] = useState(null);
    const [isStarting, setIsStarting] = useState(false);
    const [isResuming, setIsResuming] = useState(false);
    const [isAlreadyRegistered, setIsAlreadyRegistered] = useState(false);

    // Registration fields
    const [phone, setPhone] = useState('');
    const [panNumber, setPanNumber] = useState('');
    const [panPhoto, setPanPhoto] = useState(null);
    const [panPhotoPreview, setPanPhotoPreview] = useState(null);
    const [panValidating, setPanValidating] = useState(false);
    const [panVerified, setPanVerified] = useState(false);
    const [panError, setPanError] = useState('');
    const [formError, setFormError] = useState('');

    // Time-lock state
    const [timeAllowed, setTimeAllowed] = useState(true);
    const [countdown, setCountdown] = useState(0);
    const [pastWindow, setPastWindow] = useState(false);

    useEffect(() => {
        const fetchCandidate = async () => {
            if (!token) {
                setError('No interview token provided.');
                setLoading(false);
                return;
            }
            try {
                const response = await axios.get(`${API_BASE_URL}/ai-candidates/public/${token}/`);
                const candidateData = response.data;
                setCandidate(candidateData);
                
                // Check if candidate has already completed registration
                if (candidateData.phone && candidateData.pan_number && candidateData.resume) {
                    setIsAlreadyRegistered(true);
                    // Pre-fill the form fields for display
                    setPhone(candidateData.phone || '');
                    setPanNumber(candidateData.pan_number || '');
                    setPanVerified(true);
                }
                
                setLoading(false);

                // Keep candidate on this page even when questions already exist.
                // This ensures the same pre-start UX (timing visibility + explicit start action).
            } catch (err) {
                if (err.response?.status === 403 && err.response?.data?.link_expired) {
                    setLinkExpired(true);
                } else if (err.response?.status === 404) {
                    setError('Candidate not found. Testing the link as a scoped user? Or the link is invalid.');
                } else {
                    setError(err.response?.data?.error || err.message || 'Invalid or expired interview link.');
                }
                setLoading(false);
            }
        };
        fetchCandidate();
    }, [token]);

    const checkWindow = useCallback(() => {
        if (!candidate) return;

        const now = new Date();

        // Priority: available_from/until (ISO)
        if (candidate.available_from) {
            const start = new Date(candidate.available_from);
            const end = candidate.available_until ? new Date(candidate.available_until) : null;

            if (now < start) {
                setTimeAllowed(false);
                setCountdown(Math.ceil((start - now) / 1000));
                setPastWindow(false);
                return;
            }
            if (end && now > end) {
                setTimeAllowed(false);
                setCountdown(0);
                setPastWindow(true);
                return;
            }
            // Within window
            setTimeAllowed(true);
            setCountdown(0);
            setPastWindow(false);
            return;
        }

        // Legacy fallback: interview_time (string)
        if (!candidate.interview_time) {
            setTimeAllowed(true);
            return;
        }
        const scheduled = parseScheduledTime(candidate.interview_time);
        if (!scheduled) {
            setTimeAllowed(true);
            return;
        }
        const { allowed, secondsUntil } = checkTimeWindow(scheduled);
        setTimeAllowed(allowed);
        setCountdown(secondsUntil > 0 ? secondsUntil : 0);
        setPastWindow(secondsUntil === -1);
    }, [candidate]);

    useEffect(() => {
        if (!candidate) return;
        checkWindow();
        const interval = setInterval(checkWindow, 1000);
        return () => clearInterval(interval);
    }, [candidate, checkWindow]);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) setResumeFile(e.target.files[0]);
    };

    const handlePanPhotoChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setPanPhoto(file);
            setPanPhotoPreview(URL.createObjectURL(file));
            setPanVerified(false);
            setPanError('');
        }
    };

    const validatePanFormat = (pan) => {
        const panPattern = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
        return panPattern.test(pan.toUpperCase().trim());
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

    const handleResumeInterview = async () => {
        setIsResuming(true);
        setFormError('');

        try {
            // Re-fetch resume match to get questions (sessionStorage was cleared when tab closed)
            const formData = new FormData();
            formData.append('candidate_id', candidate.id);
            // Note: resume is already on server, we just need to trigger match

            const response = await axios.post(`${API_BASE_URL}/ai-candidates/match/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (!response.data.interview_questions) {
                throw new Error('No questions generated');
            }

            const sessionData = {
                candidateId: candidate.id,
                candidateName: candidate.full_name,
                questions: response.data.interview_questions,
                status: 'interview_started'
            };
            sessionStorage.setItem('interviewData', JSON.stringify(sessionData));

            import('../utils/activityLogger').then(({ logCandidateActivity }) => {
                logCandidateActivity(token, 'Interview Resumed', 'Candidate resumed the AI interview after closing/reopening the link.');
            });

            navigate(generatePath(ROUTES.AI_INTERVIEW_SESSION, { token }));
        } catch (err) {
            setFormError(err.response?.data?.error || err.message || 'Failed to resume interview. Please try again.');
            setIsResuming(false);
        }
    };

    const handleStartInterview = async () => {
        // Validate required fields
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

        if (!resumeFile && !window.confirm("No new resume selected. Use existing resume if available?")) return;

        setIsStarting(true);
        setFormError('');

        // First, save registration details
        try {
            const regFormData = new FormData();
            regFormData.append('phone', phone);
            regFormData.append('pan_number', panNumber.toUpperCase().trim());
            regFormData.append('pan_verified', 'true');
            if (panPhoto) regFormData.append('pan_photo', panPhoto);
            if (resumeFile) regFormData.append('resume', resumeFile);

            await axios.post(`${API_BASE_URL}/ai-candidates/public/${token}/register/`, regFormData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
        } catch (err) {
            const errorData = err.response?.data;
            // If PAN requires face verification, store details and proceed to interview for face check
            if (errorData?.requires_face_verification) {
                sessionStorage.setItem('verify_against_person_id', errorData.verify_against_person_id || '');
                sessionStorage.setItem('pending_pan', panNumber.toUpperCase().trim());
                // Proceed to interview - face verification will happen there
            } else {
                setFormError(errorData?.error || 'Failed to save registration details');
                setIsStarting(false);
                return;
            }
        }

        // Then proceed with resume matching
        const formData = new FormData();
        if (resumeFile) formData.append('resume', resumeFile);
        formData.append('candidate_id', candidate.id);

        try {
            const response = await axios.post(`${API_BASE_URL}/ai-candidates/match/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            if (!response.data.interview_questions) throw new Error('No questions generated');
            const sessionData = {
                candidateId: candidate.id,
                candidateName: candidate.full_name,
                questions: response.data.interview_questions,
                status: 'interview_started'
            };
            sessionStorage.setItem('interviewData', JSON.stringify(sessionData));
            import('../utils/activityLogger').then(({ logCandidateActivity }) => {
                logCandidateActivity(token, 'Live Interview Started', 'Candidate started the live/AI interview session.');
            });
            navigate(generatePath(ROUTES.AI_INTERVIEW_SESSION, { token }));
        } catch (err) {
            if (err.response?.data?.time_locked) {
                setError(err.response.data.error);
            } else {
                setError(`Error: ${err.response?.data?.error || err.message}`);
            }
            setIsStarting(false);
        }
    };

    if (loading) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins' }}>
            <div style={{ textAlign: 'center' }}>
                <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', color: '#667eea', marginBottom: '1rem' }}></i>
                <p>Verifying candidate...</p>
            </div>
        </div>
    );

    if (linkExpired) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins', background: '#f4f6f8' }}>
            <div style={{ textAlign: 'center', maxWidth: '420px', padding: '3rem 2.5rem', background: 'white', borderRadius: '24px', boxShadow: '0 20px 60px rgba(0,0,0,0.1)' }}>
                <div style={{ width: '80px', height: '80px', background: '#FFF5F5', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
                    <i className="fa-solid fa-hourglass-end" style={{ fontSize: '2rem', color: '#E53E3E' }} />
                </div>
                <h2 style={{ color: '#2D3748', margin: '0 0 0.75rem', fontSize: '1.6rem', fontWeight: '800' }}>Interview Link Expired</h2>
                <p style={{ color: '#718096', lineHeight: '1.7', margin: '0 0 1.5rem' }}>
                    This interview link was valid for <strong>60 minutes</strong> from when it was first opened and has now expired.
                </p>
                <p style={{ color: '#A0AEC0', fontSize: '0.85rem' }}>Please contact HR to receive a new interview link.</p>
            </div>
        </div>
    );

    if (error && !candidate) {
        const isExpired = error.toLowerCase().includes('expired');
        const isCompleted = error.toLowerCase().includes('completed');

        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                fontFamily: 'Inter, Poppins, sans-serif',
                background: 'linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%)',
                padding: '20px'
            }}>
                <div style={{
                    textAlign: 'center',
                    maxWidth: '450px',
                    width: '100%',
                    padding: '3.5rem 2.5rem',
                    background: 'white',
                    borderRadius: '32px',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.08)',
                    border: '1px solid #E2E8F0'
                }}>
                    <div style={{
                        width: '88px',
                        height: '88px',
                        background: isExpired || isCompleted ? '#FFF5F5' : '#F0F9FF',
                        borderRadius: '24px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 2rem',
                        transform: 'rotate(-5deg)'
                    }}>
                        {isExpired ? (
                            <i className="fa-solid fa-hourglass-end" style={{ fontSize: '2.5rem', color: '#EF4444' }}></i>
                        ) : isCompleted ? (
                            <i className="fa-solid fa-circle-check" style={{ fontSize: '2.5rem', color: '#10B981' }}></i>
                        ) : (
                            <i className="fa-solid fa-link-slash" style={{ fontSize: '2.5rem', color: '#3B82F6' }}></i>
                        )}
                    </div>

                    <h2 style={{
                        color: '#1E293B',
                        fontSize: '1.75rem',
                        fontWeight: '800',
                        marginBottom: '1rem',
                        letterSpacing: '-0.02em'
                    }}>
                        {isExpired ? 'Link Expired' : isCompleted ? 'Interview Completed' : 'Link Access Issue'}
                    </h2>

                    <p style={{
                        color: '#64748B',
                        fontSize: '1.05rem',
                        lineHeight: '1.6',
                        marginBottom: '2.5rem'
                    }}>
                        {error}
                    </p>

                    <button
                        onClick={() => navigate('/')}
                        style={{
                            width: '100%',
                            padding: '1rem 2rem',
                            background: '#1E293B',
                            color: 'white',
                            border: 'none',
                            borderRadius: '16px',
                            fontWeight: '700',
                            fontSize: '1rem',
                            cursor: 'pointer',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                        }}
                        onMouseOver={(e) => {
                            e.currentTarget.style.transform = 'translateY(-2px)';
                            e.currentTarget.style.backgroundColor = '#0F172A';
                        }}
                        onMouseOut={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.backgroundColor = '#1E293B';
                        }}
                    >
                        Go to Homepage
                    </button>
                    
                    <p style={{ marginTop: '1.5rem', color: '#94A3B8', fontSize: '0.875rem' }}>
                        Need help? Please contact your hiring manager.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div style={{ background: '#f4f6f8', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px', fontFamily: 'Poppins' }}>
            <div style={{ background: 'white', padding: '3rem', borderRadius: '24px', boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)', textAlign: 'center', maxWidth: '600px', width: '100%' }}>
                <div style={{ width: '80px', height: '80px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '2rem', margin: '0 auto 1.5rem', boxShadow: '0 10px 20px rgba(102, 126, 234, 0.3)' }}>
                    <i className="fa-solid fa-microphone-lines"></i>
                </div>
                <h1 style={{ color: '#2d3748', margin: '0 0 1rem' }}>Welcome, {candidate?.full_name?.split(' ')[0]}!</h1>
                <p style={{ color: '#718096', marginBottom: '2rem', lineHeight: '1.6' }}>Please complete your details and upload your resume to begin the AI-powered video interview.</p>

                <div style={{ background: '#f8f9fa', padding: '1.2rem', borderRadius: '16px', marginBottom: '2rem', textAlign: 'left' }}>
                    <p style={{ margin: '0', color: '#2d3748', fontWeight: '600', display: 'flex', alignItems: 'center' }}>
                        <i className="fa-regular fa-user" style={{ marginRight: '10px', color: '#667eea' }}></i> {candidate?.full_name}
                    </p>
                    <p style={{ margin: '0.5rem 0 0 0', color: '#718096', fontSize: '0.9rem', display: 'flex', alignItems: 'center' }}>
                        <i className="fa-regular fa-envelope" style={{ marginRight: '10px', color: '#667eea' }}></i> {candidate?.email}
                    </p>
                    {candidate?.available_from ? (
                        <p style={{ margin: '0.5rem 0 0 0', color: '#667eea', fontWeight: '600', fontSize: '0.9rem', display: 'flex', alignItems: 'center' }}>
                            <i className="fa-regular fa-clock" style={{ marginRight: '10px' }}></i>
                            Window: {new Date(candidate.available_from).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })} - {candidate.available_until ? new Date(candidate.available_until).toLocaleTimeString([], { timeStyle: 'short' }) : '∞'}
                        </p>
                    ) : candidate?.interview_time && (
                        <p style={{ margin: '0.5rem 0 0 0', color: '#667eea', fontWeight: '600', fontSize: '0.9rem', display: 'flex', alignItems: 'center' }}>
                            <i className="fa-regular fa-clock" style={{ marginRight: '10px' }}></i>
                            Scheduled: {candidate.interview_time}
                        </p>
                    )}
                </div>

                {/* Already Registered - Resume Interview */}
                {isAlreadyRegistered && (
                    <div style={{
                        background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                        border: '2px solid #22c55e',
                        borderRadius: '20px',
                        padding: '2rem',
                        marginBottom: '2rem',
                        textAlign: 'center'
                    }}>
                        <div style={{
                            width: '64px', height: '64px', background: '#22c55e', borderRadius: '50%',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            margin: '0 auto 1rem', color: 'white', fontSize: '1.75rem'
                        }}>
                            <i className="fa-solid fa-circle-check"></i>
                        </div>
                        <h3 style={{ color: '#166534', margin: '0 0 0.5rem', fontWeight: '700' }}>
                            Registration Complete
                        </h3>
                        <p style={{ color: '#15803d', margin: '0 0 1.5rem', fontSize: '0.95rem' }}>
                            Your details are already on file. Click below to resume your interview.
                        </p>
                        <div style={{ background: 'white', borderRadius: '12px', padding: '1rem', marginBottom: '1.5rem', textAlign: 'left' }}>
                            <p style={{ margin: '0 0 0.5rem', color: '#374151', fontSize: '0.9rem' }}>
                                <i className="fa-solid fa-phone" style={{ marginRight: '8px', color: '#22c55e' }}></i>
                                {candidate?.phone}
                            </p>
                            <p style={{ margin: '0 0 0.5rem', color: '#374151', fontSize: '0.9rem' }}>
                                <i className="fa-solid fa-id-card" style={{ marginRight: '8px', color: '#22c55e' }}></i>
                                {candidate?.pan_number}
                            </p>
                            <p style={{ margin: '0', color: '#374151', fontSize: '0.9rem' }}>
                                <i className="fa-solid fa-file-pdf" style={{ marginRight: '8px', color: '#22c55e' }}></i>
                                Resume uploaded
                            </p>
                        </div>
                        <button
                            onClick={handleResumeInterview}
                            disabled={isResuming || !timeAllowed}
                            style={{
                                width: '100%', padding: '1.2rem', borderRadius: '14px', border: 'none',
                                background: !timeAllowed ? '#cbd5e0' : 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                                color: 'white', fontSize: '1.1rem', fontWeight: '700', cursor: !timeAllowed ? 'not-allowed' : 'pointer',
                                opacity: !timeAllowed ? 0.7 : 1, transition: 'transform 0.2s'
                            }}
                            onMouseOver={(e) => { if (timeAllowed) e.currentTarget.style.transform = 'translateY(-2px)'; }}
                            onMouseOut={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
                        >
                            {isResuming ? (
                                <><i className="fa-solid fa-spinner fa-spin" style={{ marginRight: '8px' }}></i> Loading Interview...</>
                            ) : !timeAllowed ? (
                                '⏳ Interview Not Yet Available'
                            ) : (
                                <><i className="fa-solid fa-play" style={{ marginRight: '8px' }}></i> Resume Interview</>
                            )}
                        </button>
                    </div>
                )}

                {/* Registration Form - only show if not already registered */}
                {!isAlreadyRegistered && (
                    <>
                {/* Phone Number */}
                <div style={{ textAlign: 'left', marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', fontWeight: '600', color: '#2d3748', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        <i className="fa-solid fa-phone" style={{ marginRight: '8px', color: '#667eea' }}></i>Phone Number *
                    </label>
                    <input
                        type="tel"
                        value={phone}
                        onChange={(e) => {
                            const value = e.target.value.replace(/\D/g, ''); // Remove non-digits
                            if (value.length <= 10) setPhone(value);
                        }}
                        placeholder="Enter your phone number"
                        maxLength={10}
                        style={{
                            width: '100%', padding: '0.75rem 1rem', border: '1.5px solid #e2e8f0', borderRadius: '12px',
                            fontSize: '1rem', outline: 'none', transition: 'border-color 0.2s',
                            boxSizing: 'border-box'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#667eea'}
                        onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                    />
                </div>

                {/* PAN Card Number */}
                <div style={{ textAlign: 'left', marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', fontWeight: '600', color: '#2d3748', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        <i className="fa-solid fa-id-card" style={{ marginRight: '8px', color: '#667eea' }}></i>PAN Card Number *
                    </label>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <input
                            type="text"
                            value={panNumber}
                            onChange={(e) => {
                                const value = e.target.value.toUpperCase();
                                const position = value.length - 1;
                                const lastChar = value[position];

                                // Validate based on position
                                if (position >= 0 && position < 5) {
                                    // First 5 chars: only letters
                                    if (!/^[A-Z]$/.test(lastChar)) return;
                                } else if (position >= 5 && position < 9) {
                                    // Next 4 chars: only numbers
                                    if (!/^[0-9]$/.test(lastChar)) return;
                                } else if (position === 9) {
                                    // Last char: only letter
                                    if (!/^[A-Z]$/.test(lastChar)) return;
                                }

                                setPanNumber(value);
                                setPanVerified(false);
                                setPanError('');
                            }}
                            placeholder="e.g. ABCDE1234F"
                            maxLength={10}
                            style={{
                                flex: 1, padding: '0.75rem 1rem', border: '1.5px solid #e2e8f0', borderRadius: '12px',
                                fontSize: '1rem', outline: 'none', transition: 'border-color 0.2s',
                                textTransform: 'uppercase', letterSpacing: '0.05em',
                                borderColor: panVerified ? '#22c55e' : panError ? '#ef4444' : '#e2e8f0'
                            }}
                            onFocus={(e) => { if (!panVerified && !panError) e.target.style.borderColor = '#667eea'; }}
                            onBlur={(e) => { if (!panVerified && !panError) e.target.style.borderColor = '#e2e8f0'; }}
                        />
                        {panVerified && (
                            <span style={{ display: 'flex', alignItems: 'center', color: '#22c55e', fontWeight: '700', fontSize: '0.85rem', whiteSpace: 'nowrap' }}>
                                <i className="fa-solid fa-circle-check" style={{ marginRight: '4px' }}></i>Verified
                            </span>
                        )}
                    </div>
                    <p style={{ margin: '0.25rem 0 0', fontSize: '0.75rem', color: '#a0aec0' }}>Format: 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F)</p>
                </div>

                {/* PAN Card Photo Upload */}
                <div style={{ textAlign: 'left', marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', fontWeight: '600', color: '#2d3748', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        <i className="fa-solid fa-camera" style={{ marginRight: '8px', color: '#667eea' }}></i>PAN Card Photo *
                    </label>
                    <div
                        onClick={() => document.getElementById('panPhotoInput').click()}
                        style={{
                            border: '2px dashed #cbd5e0', borderRadius: '12px', padding: '1rem', cursor: 'pointer',
                            transition: 'all 0.2s', background: panPhotoPreview ? '#f0fdf4' : 'transparent',
                            borderColor: panVerified ? '#22c55e' : panPhotoPreview ? '#38b2ac' : '#cbd5e0',
                            display: 'flex', alignItems: 'center', gap: '1rem'
                        }}
                    >
                        <input type="file" id="panPhotoInput" accept="image/*" hidden onChange={handlePanPhotoChange} />
                        {panPhotoPreview ? (
                            <img src={panPhotoPreview} alt="PAN card" style={{ width: '80px', height: '60px', objectFit: 'cover', borderRadius: '8px' }} />
                        ) : (
                            <i className="fa-solid fa-cloud-arrow-up" style={{ fontSize: '1.5rem', color: '#667eea' }}></i>
                        )}
                        <div>
                            <p style={{ margin: '0 0 0.25rem', fontWeight: '600', color: '#4a5568', fontSize: '0.9rem' }}>
                                {panPhoto ? panPhoto.name : 'Upload PAN Card Photo'}
                            </p>
                            <p style={{ margin: 0, fontSize: '0.75rem', color: '#a0aec0' }}>Click to browse</p>
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
                            background: panValidating || !validatePanFormat(panNumber) ? '#cbd5e0' : 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                            color: 'white', border: 'none', borderRadius: '12px',
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
                        background: '#FEF2F2', border: '1px solid #FCA5A5', borderRadius: '12px',
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

                {/* Availability Status Banner */}
                {candidate?.interview_time && !timeAllowed && (
                    <div style={{
                        background: pastWindow ? '#FFF5F5' : '#FFFBEB',
                        border: pastWindow ? '1px solid #FECACA' : '1px solid #FDE68A',
                        borderRadius: '20px',
                        padding: '1.5rem',
                        marginBottom: '2rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1.25rem',
                        textAlign: 'left',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)'
                    }}>
                        <div style={{
                            background: 'white',
                            width: '48px',
                            height: '48px',
                            borderRadius: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0,
                            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                        }}>
                            {pastWindow ? (
                                <i className="fa-solid fa-calendar-xmark" style={{ color: '#EF4444', fontSize: '1.5rem' }}></i>
                            ) : (
                                <i className="fa-solid fa-clock-rotate-left" style={{ color: '#D97706', fontSize: '1.5rem' }}></i>
                            )}
                        </div>
                        <div>
                            <p style={{ 
                                margin: 0, 
                                fontWeight: '800', 
                                color: pastWindow ? '#991B1B' : '#92400E', 
                                fontSize: '1.1rem' 
                            }}>
                                {pastWindow ? 'Interview Window Closed' : 'Interview Not Yet Available'}
                            </p>
                            <p style={{ 
                                margin: '0.25rem 0 0', 
                                color: pastWindow ? '#B91C1C' : '#B45309', 
                                fontSize: '0.95rem', 
                                lineHeight: '1.4' 
                            }}>
                                {pastWindow ? (
                                    'The availability window for this interview has passed. Please contact your hiring manager for assistance.'
                                ) : (
                                    <>
                                        This session is scheduled for <strong style={{ color: '#78350F' }}>{candidate.available_from ? new Date(candidate.available_from).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) : candidate.interview_time}</strong>.
                                        <div style={{ marginTop: '0.5rem', fontSize: '1.25rem', fontWeight: '800', letterSpacing: '0.05em' }}>
                                            {formatCountdown(countdown)}
                                        </div>
                                    </>
                                )}
                            </p>
                        </div>
                    </div>
                )}

                {/* Error Banner */}
                {error && (
                    <div style={{
                        background: '#FEF2F2',
                        border: '1px solid #FCA5A5',
                        borderRadius: '14px',
                        padding: '0.8rem 1.2rem',
                        marginBottom: '1.5rem',
                        color: '#991B1B',
                        fontSize: '0.9rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        boxShadow: '0 2px 4px rgba(153, 27, 27, 0.05)'
                    }}>
                        <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '1.1rem' }}></i>
                        <span style={{ fontWeight: '500' }}>{error}</span>
                    </div>
                )}

                <div
                    onClick={() => document.getElementById('resumeInput').click()}
                    style={{
                        border: '2px dashed #cbd5e0', borderRadius: '16px', padding: '2rem', cursor: 'pointer',
                        transition: 'all 0.2s', marginBottom: '2rem', background: resumeFile ? '#e6fffa' : 'transparent',
                        borderColor: resumeFile ? '#38b2ac' : '#cbd5e0'
                    }}
                >
                    <input type="file" id="resumeInput" accept=".pdf,.doc,.docx" hidden onChange={handleFileChange} />
                    <i className="fa-solid fa-cloud-arrow-up" style={{ fontSize: '2.2rem', color: resumeFile ? '#38b2ac' : '#667eea', marginBottom: '1rem' }}></i>
                    <p style={{ margin: '0 0 0.5rem 0', fontWeight: '600', color: '#4a5568' }}>
                        {resumeFile ? 'Resume Selected' : 'Upload Resume'}
                    </p>
                    <p style={{ margin: '0', fontSize: '0.85rem', color: '#a0aec0' }}>
                        {resumeFile ? resumeFile.name : 'Drag & drop or click to browse'}
                    </p>
                </div>

                <button
                    className="start-btn"
                    onClick={handleStartInterview}
                    disabled={isStarting || !timeAllowed || !panVerified}
                    style={{
                        background: !timeAllowed || !panVerified ? '#cbd5e0' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white', border: 'none',
                        padding: '1.2rem 2rem', borderRadius: '12px', fontSize: '1.1rem', fontWeight: '600',
                        cursor: (isStarting || !timeAllowed || !panVerified) ? 'not-allowed' : 'pointer', width: '100%', transition: 'transform 0.2s',
                        opacity: (isStarting || !timeAllowed || !panVerified) ? 0.7 : 1
                    }}
                >
                    {isStarting ? <><i className="fa-solid fa-spinner fa-spin"></i> Processing...</> :
                        !panVerified ? 'Complete PAN verification first' :
                        !timeAllowed ? (pastWindow ? '⛔ Window Closed' : `⏳ Opens at ${candidate.available_from ? new Date(candidate.available_from).toLocaleTimeString([], { timeStyle: 'short' }) : candidate.interview_time}`) :
                            'Start Interview Now'}
                </button>
                    </>
                )}
            </div>
        </div>
    );
};

export default InterviewStart;
