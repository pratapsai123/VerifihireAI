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
                setCandidate(response.data);
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

    const handleStartInterview = async () => {
        if (!resumeFile && !window.confirm("No new resume selected. Use existing resume if available?")) return;
        setIsStarting(true);
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
            <div style={{ background: 'white', padding: '3rem', borderRadius: '24px', boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)', textAlign: 'center', maxWidth: '500px', width: '100%' }}>
                <div style={{ width: '80px', height: '80px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '2rem', margin: '0 auto 1.5rem', boxShadow: '0 10px 20px rgba(102, 126, 234, 0.3)' }}>
                    <i className="fa-solid fa-microphone-lines"></i>
                </div>
                <h1 style={{ color: '#2d3748', margin: '0 0 1rem' }}>Welcome, {candidate?.full_name?.split(' ')[0]}!</h1>
                <p style={{ color: '#718096', marginBottom: '2rem', lineHeight: '1.6' }}>Please upload your resume to begin the AI-powered video interview.</p>

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
                    disabled={isStarting || !timeAllowed}
                    style={{
                        background: !timeAllowed ? '#cbd5e0' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white', border: 'none',
                        padding: '1.2rem 2rem', borderRadius: '12px', fontSize: '1.1rem', fontWeight: '600',
                        cursor: (isStarting || !timeAllowed) ? 'not-allowed' : 'pointer', width: '100%', transition: 'transform 0.2s',
                        opacity: (isStarting || !timeAllowed) ? 0.7 : 1
                    }}
                >
                    {isStarting ? <><i className="fa-solid fa-spinner fa-spin"></i> Processing...</> :
                        !timeAllowed ? (pastWindow ? '⛔ Window Closed' : `⏳ Opens at ${candidate.available_from ? new Date(candidate.available_from).toLocaleTimeString([], { timeStyle: 'short' }) : candidate.interview_time}`) :
                            'Start Interview Now'}
                </button>
            </div>
        </div>
    );
};

export default InterviewStart;
