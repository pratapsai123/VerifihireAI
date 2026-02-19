import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const InterviewStart = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [candidate, setCandidate] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [resumeFile, setResumeFile] = useState(null);
    const [isStarting, setIsStarting] = useState(false);

    useEffect(() => {
        const fetchCandidate = async () => {
            if (!token) {
                setError('No interview token provided.');
                setLoading(false);
                return;
            }

            try {
                const response = await axios.get(`http://localhost:8001/api/ai-candidates/${token}/`);
                setCandidate(response.data);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching candidate:', err);
                setError('Invalid or expired interview link.');
                setLoading(false);
            }
        };

        fetchCandidate();
    }, [token]);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setResumeFile(e.target.files[0]);
        }
    };

    const handleStartInterview = async () => {
        if (!resumeFile && !window.confirm("No new resume selected. Use existing resume if available?")) {
            return;
        }

        setIsStarting(true);
        const formData = new FormData();
        if (resumeFile) {
            formData.append('resume', resumeFile);
        }
        formData.append('candidate_id', candidate.id);

        try {
            const response = await axios.post('http://localhost:8001/api/ai-candidates/match/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (!response.data.interview_questions) {
                throw new Error('No questions generated');
            }

            // Store session data
            const sessionData = {
                candidateId: candidate.id,
                candidateName: candidate.full_name,
                questions: response.data.interview_questions,
                status: 'interview_started'
            };
            sessionStorage.setItem('interviewData', JSON.stringify(sessionData));

            // Redirect to session
            navigate(`/ai-interview-session/${token}`);
        } catch (err) {
            console.error('Error starting interview:', err);
            setError(`Error: ${err.response?.data?.error || err.message}`);
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

    if (error) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins' }}>
            <div style={{ textAlign: 'center', maxWidth: '400px', padding: '2rem', background: 'white', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
                <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '3rem', color: '#e53e3e', marginBottom: '1rem' }}></i>
                <h2 style={{ color: '#2d3748' }}>Interview Link Error</h2>
                <p style={{ color: '#718096' }}>{error}</p>
                <button onClick={() => navigate('/')} style={{ marginTop: '1.5rem', padding: '0.8rem 2rem', background: '#667eea', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer' }}>Return Home</button>
            </div>
        </div>
    );

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
                </div>

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
                    disabled={isStarting}
                    style={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none',
                        padding: '1.2rem 2rem', borderRadius: '12px', fontSize: '1.1rem', fontWeight: '600',
                        cursor: isStarting ? 'not-allowed' : 'pointer', width: '100%', transition: 'transform 0.2s',
                        opacity: isStarting ? 0.7 : 1
                    }}
                >
                    {isStarting ? <><i className="fa-solid fa-spinner fa-spin"></i> Processing...</> : 'Start Interview Now'}
                </button>
            </div>
        </div>
    );
};

export default InterviewStart;
