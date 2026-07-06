import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Briefcase, Play, Loader2, Clock, Code, Zap } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig'; 
import '../styles/StudentAiInterview.css';

const CREDIT_COSTS = { 5: 30, 10: 60, 14: 80, 20: 100 };

const StudentAiInterview = () => {
    const [jobTitle, setJobTitle] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [experienceLevel, setExperienceLevel] = useState('fresher');
    const [questionCount, setQuestionCount] = useState(14);
    const [includeCoding, setIncludeCoding] = useState(true);
    const [resumeFile, setResumeFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);
    const [availableCredits, setAvailableCredits] = useState(0);
    const [highlightField, setHighlightField] = useState(null);
    const fileInputRef = useRef(null);
    const jobTitleRef = useRef(null);
    const jobDescRef = useRef(null);
    const resumeDropRef = useRef(null);
    const navigate = useNavigate();

    const creditCost = CREDIT_COSTS[questionCount] || 80;

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
    }, []);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setResumeFile(e.target.files[0]);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setResumeFile(e.dataTransfer.files[0]);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragActive(true);
    };

    const handleDragLeave = () => {
        setDragActive(false);
    };

    const scrollAndHighlight = (ref, fieldName) => {
        setHighlightField(fieldName);
        if (ref?.current) {
            ref.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
            ref.current.focus?.();
        }
        setTimeout(() => setHighlightField(null), 3000);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (!jobTitle || jobTitle.trim().length < 2) {
            setError("Please enter a job title.");
            scrollAndHighlight(jobTitleRef, 'jobTitle');
            return;
        }
        if (!jobDescription || jobDescription.length < 50) {
            setError("Please provide a more detailed job description (min 50 characters).");
            scrollAndHighlight(jobDescRef, 'jobDesc');
            return;
        }
        if (!resumeFile) {
            setError("Please upload your resume to continue.");
            scrollAndHighlight(resumeDropRef, 'resume');
            return;
        }
        if (availableCredits < creditCost) {
            setError(`Insufficient credits. You need ${creditCost} credits but have ${availableCredits}. Please add credits from your wallet.`);
            return;
        }
        setShowConfirm(true);
    };

    const proceedWithInterview = async () => {
        setShowConfirm(false);
        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('job_title', jobTitle);
        formData.append('job_description', jobDescription);
        formData.append('experience_level', experienceLevel);
        formData.append('question_count', questionCount);
        formData.append('include_coding', includeCoding);
        formData.append('resume', resumeFile);

        try {
            const response = await axios.post(`${API_BASE_URL}/students/practice/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            if (response.data && response.data.public_token) {
                navigate(`/ai-interview-session/${response.data.public_token}`);
            } else {
                setError("Something went wrong. Please try again.");
            }
        } catch (err) {
            setError(err.response?.data?.error || "Failed to start practice session.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="student-ai-wrapper">
            <div className="student-ai-mesh-bg"></div>
            
            <div className="student-ai-content">
                <section className="glass-panel shimmer-sweep">
                    <div className="text-center mb-8 relative z-10">
                        <h2 className="student-ai-title">Setup New Interview</h2>
                        <p className="student-ai-subtitle">Refine your skills with AI-powered feedback tailored to your target role.</p>
                    </div>

                    {error && (
                        <div style={{ color: '#ba1a1a', backgroundColor: '#ffdad6', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem', border: '1px solid #ba1a1a', fontSize: '0.9rem', fontWeight: 500, position: 'relative', zIndex: 10 }}>
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="relative z-10">
                        <div className="form-group">
                            <label className="form-label">Job Title</label>
                            <div className="input-icon-wrapper" style={highlightField === 'jobTitle' ? { boxShadow: '0 0 0 3px rgba(239,68,68,0.3)', borderRadius: '12px', transition: 'box-shadow 0.3s' } : {}}>
                                <Briefcase className="input-icon" size={18} />
                                <input 
                                    type="text" 
                                    ref={jobTitleRef}
                                    className="glass-input" 
                                    value={jobTitle} 
                                    onChange={(e) => setJobTitle(e.target.value)} 
                                    placeholder="e.g. Software Engineer"
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Job Description</label>
                            <textarea 
                                ref={jobDescRef}
                                className="glass-input glass-textarea" 
                                value={jobDescription} 
                                onChange={(e) => setJobDescription(e.target.value)}
                                placeholder="Paste the job details here..."
                                required
                                style={highlightField === 'jobDesc' ? { boxShadow: '0 0 0 3px rgba(239,68,68,0.3)', transition: 'box-shadow 0.3s' } : {}}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Difficulty Level</label>
                            <div className="input-icon-wrapper">
                                <Briefcase className="input-icon" size={18} />
                                <select
                                    className="glass-input"
                                    value={experienceLevel}
                                    onChange={(e) => setExperienceLevel(e.target.value)}
                                    style={{ cursor: 'pointer', appearance: 'auto' }}
                                >
                                    <option value="fresher">Fresher (Easy)</option>
                                    <option value="1-2">1-2 Years (Moderate)</option>
                                    <option value="3-5">3-5 Years (Intermediate-Hard)</option>
                                    <option value="5+">5+ Years (Hard)</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Interview Length</label>
                            <div className="input-icon-wrapper">
                                <Clock className="input-icon" size={18} />
                                <select
                                    className="glass-input"
                                    value={questionCount}
                                    onChange={(e) => setQuestionCount(Number(e.target.value))}
                                    style={{ cursor: 'pointer', appearance: 'auto' }}
                                >
                                    <option value={5}>Quick (5 questions, ~10 min)</option>
                                    <option value={10}>Short (10 questions, ~20 min)</option>
                                    <option value={14}>Standard (14 questions, ~30 min)</option>
                                    <option value={20}>Deep (20 questions, ~45 min)</option>
                                </select>
                            </div>
                        </div>

                        {/* Include Coding Toggle */}
                        <div className="form-group">
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 1.25rem', background: includeCoding ? 'rgba(99,102,241,0.05)' : 'rgba(0,0,0,0.02)', border: includeCoding ? '1px solid rgba(99,102,241,0.2)' : '1px solid rgba(0,0,0,0.08)', borderRadius: '14px', transition: 'all 0.3s ease' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <Code size={18} style={{ color: includeCoding ? '#6366f1' : '#94a3b8' }} />
                                    <div>
                                        <p style={{ margin: 0, fontSize: '0.9rem', fontWeight: 600, color: '#1e293b' }}>Include Coding Questions</p>
                                        <p style={{ margin: '2px 0 0', fontSize: '0.75rem', color: '#64748b' }}>
                                            {includeCoding ? 'Last 1-2 questions will require writing code' : 'All questions will be verbal/conversational only'}
                                        </p>
                                    </div>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => setIncludeCoding(!includeCoding)}
                                    style={{
                                        width: '48px',
                                        height: '26px',
                                        borderRadius: '13px',
                                        border: 'none',
                                        background: includeCoding ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : '#cbd5e1',
                                        position: 'relative',
                                        cursor: 'pointer',
                                        transition: 'background 0.3s ease',
                                        flexShrink: 0,
                                    }}
                                >
                                    <div style={{
                                        width: '20px',
                                        height: '20px',
                                        borderRadius: '50%',
                                        background: 'white',
                                        position: 'absolute',
                                        top: '3px',
                                        left: includeCoding ? '25px' : '3px',
                                        transition: 'left 0.3s ease',
                                        boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                                    }}></div>
                                </button>
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Your Resume (PDF or DOCX)</label>
                            <div 
                                ref={resumeDropRef}
                                className={`dropzone ${dragActive ? 'drag-active' : ''}`}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onClick={() => fileInputRef.current?.click()}
                                style={highlightField === 'resume' ? { boxShadow: '0 0 0 3px rgba(239,68,68,0.3)', transition: 'box-shadow 0.3s' } : {}}
                            >
                                <input 
                                    type="file" 
                                    ref={fileInputRef} 
                                    onChange={handleFileChange} 
                                    accept=".pdf,.doc,.docx"
                                    style={{ display: 'none' }}
                                />
                                <div className="dropzone-icon-bg">
                                    {resumeFile ? (
                                        <FileText className="dropzone-icon" size={32} />
                                    ) : (
                                        <Upload className="dropzone-icon" size={32} />
                                    )}
                                </div>
                                <div>
                                    {resumeFile ? (
                                        <>
                                            <p className="dropzone-text" style={{color: '#7c3aed'}}>Selected File:</p>
                                            <p className="dropzone-subtext mt-1">{resumeFile.name}</p>
                                        </>
                                    ) : (
                                        <>
                                            <p className="dropzone-text">Click or drag to upload</p>
                                            <p className="dropzone-subtext mt-1">Maximum file size 5MB</p>
                                        </>
                                    )}
                                </div>
                            </div>
                        </div>

                        <button type="submit" className="gradient-btn" disabled={loading}>
                            {loading ? (
                                <>
                                    <Loader2 size={20} className="loading-spinner" />
                                    <span>Preparing Interview...</span>
                                </>
                            ) : (
                                <>
                                    <Play size={20} />
                                    <span>Start Practice Interview</span>
                                </>
                            )}
                        </button>

                        {/* Credit cost indicator */}
                        <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', color: '#6366f1', fontSize: '0.85rem', fontWeight: 600 }}>
                            <Zap size={16} />
                            <span>This interview costs <strong>{creditCost} credits</strong></span>
                            <span style={{ color: '#94a3b8', fontWeight: 400 }}>({availableCredits} available)</span>
                        </div>
                    </form>
                </section>

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
                                    This interview will use <strong style={{ color: '#6366f1' }}>{creditCost} credits</strong> from your wallet.
                                </p>
                                <p style={{ margin: '0.5rem 0 0', color: '#94a3b8', fontSize: '0.8rem' }}>
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
                                    onClick={proceedWithInterview}
                                    style={{ flex: 1, padding: '0.85rem', borderRadius: '12px', border: 'none', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px rgba(99,102,241,0.3)' }}
                                >
                                    Proceed
                                </button>
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};

export default StudentAiInterview;
