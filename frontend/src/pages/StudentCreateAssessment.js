import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Brain, Sparkles, Briefcase, Calendar, Clock, Award, Zap } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';
import '../styles/CreateAssessment.css'; // Reuse premium recruiter assessment styles

const StudentCreateAssessment = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [progressMsg, setProgressMsg] = useState('');
    const [jobTitle, setJobTitle] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [numMcqs, setNumMcqs] = useState(10);
    const [numCoding, setNumCoding] = useState(1);
    const [mcqDuration, setMcqDuration] = useState(10);
    const [codingDuration, setCodingDuration] = useState(30);
    const [showConfirm, setShowConfirm] = useState(false);
    const [availableCredits, setAvailableCredits] = useState(0);

    const pollIntervalRef = useRef(null);

    // Credit cost: 0.5 per MCQ + 1 per coding
    const creditCost = Math.max(1, Math.round((numMcqs * 0.5) + (numCoding * 1)));

    useEffect(() => {
        const fetchCredits = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get(`${API_BASE_URL}/students/wallet/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setAvailableCredits(res.data.ai_credits || 0);
            } catch (e) {}
        };
        fetchCredits();
        return () => {
            if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
            }
        };
    }, []);

    const handleGenerate = async (e) => {
        e.preventDefault();

        if (!jobTitle.trim()) {
            alert('Please enter a Job Title before generating.');
            return;
        }
        if (!jobDescription.trim()) {
            alert('Please enter a Job Description before generating.');
            return;
        }
        if (numMcqs === 0 && numCoding === 0) {
            alert('Please choose at least one MCQ question or one Coding task.');
            return;
        }
        if (numMcqs > 0 && mcqDuration <= 0) {
            alert('MCQ Duration must be greater than 0 minutes.');
            return;
        }
        if (numCoding > 0 && codingDuration <= 0) {
            alert('Coding Duration must be greater than 0 minutes.');
            return;
        }
        if (availableCredits < creditCost) {
            alert(`Insufficient credits. You need ${creditCost} credits but have ${availableCredits}. Please add credits from your wallet.`);
            return;
        }
        setShowConfirm(true);
    };

    const proceedWithGeneration = async () => {
        setShowConfirm(false);
        setLoading(true);
        setProgressMsg('Initializing practice assessment generation...');

        try {
            const response = await axios.post(`${API_BASE_URL}/students/assessments/`, {
                job_title: jobTitle,
                job_description: jobDescription,
                num_mcqs: numMcqs,
                num_coding: numCoding,
                mcq_duration: mcqDuration,
                coding_duration: codingDuration,
            });

            const taskId = response.data.task_id;
            if (taskId) {
                if (pollIntervalRef.current) {
                    clearInterval(pollIntervalRef.current);
                }
                pollIntervalRef.current = setInterval(async () => {
                    try {
                        const statusRes = await axios.get(`${API_BASE_URL}/ai/generation-status/${taskId}/`);
                        const statusData = statusRes.data;

                        if (statusData.status === 'completed') {
                            if (pollIntervalRef.current) {
                                clearInterval(pollIntervalRef.current);
                                pollIntervalRef.current = null;
                            }
                            setProgressMsg('Fetching assessment token...');
                            
                            // Retrieve the generated assessment to get the share_token
                            const assessmentId = statusData.assessment_id;
                            const detailRes = await axios.get(`${API_BASE_URL}/ai/${assessmentId}/`);
                            const shareToken = detailRes.data.share_token;

                            // Retrieve student info from localStorage to prefill taking assessment parameters
                            const user = JSON.parse(localStorage.getItem('user') || '{}');
                            const name = user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.username;
                            const email = user.email;

                            setLoading(false);
                            
                            // Redirect directly to secure exam view with name, email, practice=true, and autoStart=true parameters
                            navigate(`/take-ai-assessment/${shareToken}?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}&practice=true&autoStart=true`);
                        } else if (statusData.status === 'failed') {
                            if (pollIntervalRef.current) {
                                clearInterval(pollIntervalRef.current);
                                pollIntervalRef.current = null;
                            }
                            alert(`Generation failed: ${statusData.message || statusData.error}`);
                            setLoading(false);
                            setProgressMsg('');
                        } else {
                            setProgressMsg(statusData.progress || 'Processing AI generation...');
                        }
                    } catch (err) {
                        console.error('Error polling status:', err);
                    }
                }, 3000);
            }
        } catch (error) {
            console.error('Error:', error);
            const errMsg = error?.response?.data?.error || error?.response?.data?.message || error?.message || 'Generation failed. Please try again.';
            alert(`Generation failed: ${errMsg}`);
            setLoading(false);
            setProgressMsg('');
        }
    };

    return (
        <div className="create-assessment-page" style={{ paddingTop: '2rem', paddingBottom: '4rem' }}>
            <div className="assessment-container" style={{ maxWidth: '800px', margin: '0 auto' }}>
                
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <header className="assessment-header" style={{ margin: 0, textAlign: 'left' }}>
                        <h1 style={{ fontSize: '2rem', fontWeight: '800', color: '#0f172a', margin: 0, letterSpacing: '-0.025em' }}>
                            Setup <span style={{ color: '#4f46e5' }}>New</span> Assessment
                        </h1>
                        <p style={{ color: '#64748b', fontSize: '0.95rem', marginTop: '0.5rem', fontWeight: '500' }}>
                            Refine your skills with AI-powered feedback tailored to your target role.
                        </p>
                    </header>
                    <button 
                        className="global-btn-back" 
                        type="button" 
                        onClick={() => navigate(-1)}
                        style={{ flexShrink: 0, background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '10px', padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontWeight: '600', color: '#475569' }}
                    >
                        &larr; Back
                    </button>
                </div>

                {/* Form Wrapper */}
                <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    
                    {/* Job Title Card */}
                    <div className="section-container" style={{ background: '#ffffff', padding: '2rem', borderRadius: '20px', border: '1px solid #e2e8f0' }}>
                        <div className="form-group" style={{ margin: 0 }}>
                            <label style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1e293b', marginBottom: '0.75rem', display: 'block' }}>
                                Job Title
                            </label>
                            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                                <Briefcase size={20} style={{ position: 'absolute', left: '1.25rem', color: '#94a3b8' }} />
                                <input
                                    type="text"
                                    value={jobTitle}
                                    onChange={(e) => setJobTitle(e.target.value)}
                                    placeholder="e.g. Software Engineer"
                                    disabled={loading}
                                    style={{ paddingLeft: '3.25rem', width: '100%', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '0.95rem', outline: 'none', height: '50px' }}
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    {/* Job Description Card */}
                    <div className="section-container" style={{ background: '#ffffff', padding: '2rem', borderRadius: '20px', border: '1px solid #e2e8f0' }}>
                        <div className="form-group" style={{ margin: 0 }}>
                            <label style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1e293b', marginBottom: '0.75rem', display: 'block' }}>
                                Job Description
                            </label>
                            <textarea
                                value={jobDescription}
                                onChange={(e) => setJobDescription(e.target.value)}
                                placeholder="Paste the job details here..."
                                disabled={loading}
                                style={{ width: '100%', minHeight: '160px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '1rem', fontSize: '0.95rem', outline: 'none', resize: 'vertical', fontFamily: 'inherit' }}
                                required
                            />
                        </div>
                    </div>

                    {/* Structure & Difficulty Card */}
                    <div className="section-container" style={{ background: '#ffffff', padding: '2rem', borderRadius: '20px', border: '1px solid #e2e8f0' }}>
                        <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#0f172a', margin: 0, marginBottom: '1.5rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.75rem' }}>
                            Structure & Difficulty
                        </h3>

                        <div className="parameters-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
                            
                            {/* MCQ Count */}
                            <div className="form-group" style={{ margin: 0 }}>
                                <label style={{ fontSize: '0.85rem', fontWeight: '750', color: '#475569', marginBottom: '0.5rem' }}>
                                    MCQ Questions
                                </label>
                                <div className="input-with-marker" style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                                    <input
                                        type="number"
                                        min="0"
                                        max="100"
                                        value={numMcqs}
                                        onChange={(e) => {
                                            const val = Math.min(Math.max(0, parseInt(e.target.value) || 0), 100);
                                            setNumMcqs(val);
                                            setMcqDuration(val); // Auto-calculate MCQ time: 1 min per MCQ
                                        }}
                                        disabled={loading}
                                        style={{ width: '100%', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '0.8rem 1rem', fontSize: '0.95rem', fontWeight: '600', paddingRight: '3.5rem' }}
                                    />
                                    <span className="marker" style={{ position: 'absolute', right: '0.75rem', background: '#4f46e5', color: '#ffffff', borderRadius: '8px', padding: '0.25rem 0.5rem', fontSize: '0.8rem', fontWeight: '800' }}>
                                        {numMcqs}
                                    </span>
                                </div>
                            </div>

                            {/* Coding Count */}
                            <div className="form-group" style={{ margin: 0 }}>
                                <label style={{ fontSize: '0.85rem', fontWeight: '750', color: '#475569', marginBottom: '0.5rem' }}>
                                    Coding Tasks
                                </label>
                                <div className="input-with-marker" style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                                    <input
                                        type="number"
                                        min="0"
                                        max="5"
                                        value={numCoding}
                                        onChange={(e) => {
                                            const val = Math.min(Math.max(0, parseInt(e.target.value) || 0), 5);
                                            setNumCoding(val);
                                            setCodingDuration(val * 20); // Auto-calculate: 20 min per coding task
                                        }}
                                        disabled={loading}
                                        style={{ width: '100%', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '0.8rem 1rem', fontSize: '0.95rem', fontWeight: '600', paddingRight: '3.5rem' }}
                                    />
                                    <span className="marker" style={{ position: 'absolute', right: '0.75rem', background: '#4f46e5', color: '#ffffff', borderRadius: '8px', padding: '0.25rem 0.5rem', fontSize: '0.8rem', fontWeight: '800' }}>
                                        {numCoding}
                                    </span>
                                    <span className="marker" style={{ position: 'absolute', right: '0.75rem', background: '#94a3b8', color: '#ffffff', borderRadius: '8px', padding: '0.25rem 0.5rem', fontSize: '0.8rem', fontWeight: '800' }}>
                                        1
                                    </span>
                                </div>
                            </div>

                            {/* Duration Splits */}
                            <div className="form-group" style={{ margin: 0 }}>
                                <label style={{ fontSize: '0.85rem', fontWeight: '750', color: '#475569', marginBottom: '0.5rem' }}>
                                    Assessment Duration (Mins)
                                </label>
                                <div className="duration-split-box" style={{ display: 'flex', border: '1px solid #e2e8f0', borderRadius: '12px', background: '#f8fafc', overflow: 'hidden' }}>
                                    
                                    {/* MCQ Duration */}
                                    <div className="duration-col" style={{ flex: 1, padding: '0.5rem 0.75rem', borderRight: '1px solid #e2e8f0', position: 'relative' }}>
                                        <label style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: '#64748b', fontWeight: '700', marginBottom: '2px', display: 'block' }}>MCQ</label>
                                        <input
                                            type="number"
                                            min="0"
                                            value={mcqDuration}
                                            onChange={(e) => setMcqDuration(parseInt(e.target.value) || 0)}
                                            disabled={loading || numMcqs === 0}
                                            style={{ border: 'none', background: 'transparent', width: '100%', outline: 'none', fontSize: '1rem', fontWeight: '800', color: '#1e293b' }}
                                        />
                                        <span className="mini-marker" style={{ position: 'absolute', right: '6px', bottom: '6px', fontSize: '0.6rem', fontWeight: '800', background: '#dcfce7', color: '#15803d', padding: '2px 4px', borderRadius: '4px' }}>
                                            AUTO
                                        </span>
                                    </div>

                                    {/* Coding Duration */}
                                    <div className="duration-col" style={{ flex: 1, padding: '0.5rem 0.75rem', position: 'relative' }}>
                                        <label style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: '#64748b', fontWeight: '700', marginBottom: '2px', display: 'block' }}>Coding</label>
                                        <input
                                            type="number"
                                            min="0"
                                            value={codingDuration}
                                            onChange={(e) => setCodingDuration(parseInt(e.target.value) || 0)}
                                            disabled={loading || numCoding === 0}
                                            style={{ border: 'none', background: 'transparent', width: '100%', outline: 'none', fontSize: '1rem', fontWeight: '800', color: '#1e293b' }}
                                        />
                                        <span className="mini-marker" style={{ position: 'absolute', right: '6px', bottom: '6px', fontSize: '0.6rem', fontWeight: '800', background: '#f3e8ff', color: '#6b21a8', padding: '2px 4px', borderRadius: '4px' }}>
                                            MIN
                                        </span>
                                    </div>

                                </div>
                            </div>

                        </div>
                    </div>

                    {/* Progress / Loading message */}
                    {loading && (
                        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '15px', padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                            <div className="spinner"></div>
                            <span style={{ fontSize: '0.95rem', fontWeight: '600', color: '#4f46e5', textAlign: 'center' }}>
                                {progressMsg}
                            </span>
                            <span style={{ fontSize: '0.8rem', color: '#64748b', textAlign: 'center' }}>
                                Generating premium AI practice questions takes about 1-2 minutes. Please do not close or reload this page.
                            </span>
                        </div>
                    )}

                    {/* Action Button */}
                    <button
                        type="submit"
                        className={`generate-btn ${loading ? 'loading' : ''}`}
                        disabled={loading}
                        style={{ width: '100%', height: '54px', fontSize: '1.05rem', fontWeight: '700', borderRadius: '15px' }}
                    >
                        {loading ? (
                            <>
                                <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2.5px' }}></div>
                                Generating Practice Test...
                            </>
                        ) : (
                            <>
                                <Sparkles size={20} />
                                Start Practice Assessment
                            </>
                        )}
                    </button>

                    {/* Credit cost indicator */}
                    <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', color: '#6366f1', fontSize: '0.85rem', fontWeight: 600 }}>
                        <Zap size={16} />
                        <span>This assessment costs <strong>{creditCost} credits</strong></span>
                        <span style={{ color: '#94a3b8', fontWeight: 400 }}>({availableCredits} available)</span>
                    </div>

                </form>
            </div>

            {/* Credit Confirmation Popup */}
            {showConfirm && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
                    <div style={{ background: 'white', borderRadius: '20px', padding: '2rem', maxWidth: '400px', width: '90%', boxShadow: '0 20px 60px rgba(0,0,0,0.2)' }}>
                        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                            <div style={{ width: '56px', height: '56px', borderRadius: '16px', background: 'linear-gradient(135deg, #eef2ff, #e0e7ff)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                                <Zap size={28} style={{ color: '#6366f1' }} />
                            </div>
                            <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.2rem', fontWeight: 700, color: '#1e293b' }}>Confirm Credit Usage</h3>
                            <p style={{ margin: 0, color: '#64748b', fontSize: '0.9rem' }}>
                                This assessment will use <strong style={{ color: '#6366f1' }}>{creditCost} credits</strong> from your wallet.
                            </p>
                            <p style={{ margin: '0.75rem 0 0', color: '#94a3b8', fontSize: '0.8rem' }}>
                                {numMcqs} MCQs ({(numMcqs * 0.5).toFixed(1)} credits) + {numCoding} Coding ({numCoding} credits)
                            </p>
                            <p style={{ margin: '0.25rem 0 0', color: '#94a3b8', fontSize: '0.8rem' }}>
                                Remaining after: {availableCredits - creditCost} credits
                            </p>
                        </div>
                        <div style={{ display: 'flex', gap: '0.75rem' }}>
                            <button
                                onClick={() => setShowConfirm(false)}
                                style={{ flex: 1, padding: '0.85rem', borderRadius: '12px', border: '1px solid #e2e8f0', background: 'white', color: '#475569', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer' }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={proceedWithGeneration}
                                style={{ flex: 1, padding: '0.85rem', borderRadius: '12px', border: 'none', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px rgba(99,102,241,0.3)' }}
                            >
                                Proceed
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StudentCreateAssessment;
