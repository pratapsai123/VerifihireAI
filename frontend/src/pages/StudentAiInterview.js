import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Briefcase, Play, Loader2 } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig'; 
import '../styles/StudentAiInterview.css';

const StudentAiInterview = () => {
    const [jobTitle, setJobTitle] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [resumeFile, setResumeFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);
    const navigate = useNavigate();

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
        formData.append('resume', resumeFile);

        try {
            const response = await axios.post(`${API_BASE_URL}/api/students/practice/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            if (response.data && response.data.public_token) {
                navigate(`/interview-start/${response.data.public_token}`);
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
            </div>
        </div>
    );
};

export default StudentAiInterview;
