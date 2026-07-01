import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Briefcase, Play, Loader2, Clock, CheckCircle, XCircle, RotateCcw } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig'; 
import '../styles/StudentAiInterview.css';

const StudentAiInterview = () => {
    const [jobTitle, setJobTitle] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [experienceLevel, setExperienceLevel] = useState('fresher');
    const [resumeFile, setResumeFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);
    const navigate = useNavigate();

    const [interviews, setInterviews] = useState([]);
    const [loadingHistory, setLoadingHistory] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const resp = await axios.get(`${API_BASE_URL}/students/my-interviews/`);
                setInterviews(resp.data || []);
            } catch (err) {
                console.error('Failed to load interview history:', err);
            } finally {
                setLoadingHistory(false);
            }
        };
        fetchHistory();
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

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!jobDescription || jobDescription.length < 50) {
            setError("Please provide a more detailed job description (min 50 characters).");
            return;
        }
        if (!resumeFile) {
            setError("Please upload your resume to continue.");
            return;
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('job_title', jobTitle);
        formData.append('job_description', jobDescription);
        formData.append('experience_level', experienceLevel);
        formData.append('resume', resumeFile);

        try {
            const response = await axios.post(`${API_BASE_URL}/students/practice/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            if (response.data && response.data.public_token) {
                // Skip InterviewStart page — student already provided resume, no PAN/identity needed
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
                            <div className="input-icon-wrapper">
                                <Briefcase className="input-icon" size={18} />
                                <input 
                                    type="text" 
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
                                className="glass-input glass-textarea" 
                                value={jobDescription} 
                                onChange={(e) => setJobDescription(e.target.value)}
                                placeholder="Paste the job details here..."
                                required
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
                            <label className="form-label">Your Resume (PDF or DOCX)</label>
                            <div 
                                className={`dropzone ${dragActive ? 'drag-active' : ''}`}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onClick={() => fileInputRef.current?.click()}
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
                    </form>
                </section>

                {/* My Interviews History */}
                {!loadingHistory && interviews.length > 0 && (
                    <section className="glass-panel" style={{ marginTop: '2rem' }}>
                        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#1e293b', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <Clock size={20} />
                            My Practice Sessions
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {interviews.map((item) => {
                                const isActive = ['Invited', 'Interview', 'New'].includes(item.status);
                                const isCompleted = ['Completed', 'Hired', 'Rejected', 'On-Hold', 'Interview Passed', 'Interview Failed'].includes(item.status);
                                return (
                                    <div key={item.id} style={{
                                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                        padding: '1rem 1.25rem', borderRadius: '12px',
                                        background: isActive ? '#f0fdf4' : isCompleted ? '#f8fafc' : '#fefce8',
                                        border: `1px solid ${isActive ? '#bbf7d0' : isCompleted ? '#e2e8f0' : '#fde68a'}`,
                                    }}>
                                        <div>
                                            <div style={{ fontWeight: 600, color: '#1e293b', fontSize: '0.95rem' }}>{item.job_title}</div>
                                            <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px' }}>
                                                {item.experience_level} • {new Date(item.created_at).toLocaleDateString()}
                                                {isCompleted && ` • Score: ${item.score_percentage}%`}
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                            {isCompleted && (
                                                <span style={{
                                                    fontSize: '0.75rem', fontWeight: 700, padding: '4px 10px', borderRadius: '8px',
                                                    background: item.status === 'Hired' || item.status === 'Interview Passed' ? '#dcfce7' : item.status === 'On-Hold' ? '#fef3c7' : '#fee2e2',
                                                    color: item.status === 'Hired' || item.status === 'Interview Passed' ? '#166534' : item.status === 'On-Hold' ? '#92400e' : '#991b1b',
                                                }}>
                                                    {item.status === 'Hired' || item.status === 'Interview Passed' ? 'Passed' : item.status === 'On-Hold' ? 'Review' : 'Failed'}
                                                </span>
                                            )}
                                            {isActive ? (
                                                <button
                                                    onClick={() => navigate(`/ai-interview-session/${item.public_token}`)}
                                                    style={{
                                                        padding: '6px 16px', borderRadius: '8px', border: 'none',
                                                        background: '#22c55e', color: 'white', fontSize: '0.8rem',
                                                        fontWeight: 600, cursor: 'pointer'
                                                    }}
                                                >
                                                    <Play size={14} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                                                    Resume
                                                </button>
                                            ) : isCompleted ? (
                                                <CheckCircle size={20} style={{ color: '#22c55e' }} />
                                            ) : null}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </section>
                )}
            </div>
        </div>
    );
};

export default StudentAiInterview;
