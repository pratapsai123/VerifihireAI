import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';

const AiInterview = () => {
    const [jobDescription, setJobDescription] = useState('');
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const removeFile = () => {
        setFile(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            alert('Please upload a candidate list.');
            return;
        }

        setIsUploading(true);
        setError('');
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('job_description', jobDescription);

        try {
            // Using localhost:8001 as per original html
            const response = await axios.post('http://localhost:8001/api/ai-candidates/bulk-invite/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setResult(response.data);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || err.message || 'Failed to process bulk invite');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="dashboard-container" style={{ paddingTop: '2rem' }}>
            <div className="interview-hero" style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '24px',
                padding: '3rem',
                marginBottom: '2.5rem',
                color: 'white',
                position: 'relative',
                overflow: 'hidden'
            }}>
                <div className="hero-icon" style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '80px',
                    height: '80px',
                    background: 'rgba(255, 255, 255, 0.2)',
                    borderRadius: '20px',
                    marginBottom: '1.5rem',
                    backdropFilter: 'blur(10px)',
                    fontSize: '2.5rem'
                }}>
                    <i className="fa-solid fa-robot"></i>
                </div>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', position: 'relative', zIndex: 1 }}>AI-Powered Interview</h1>
                <p style={{ fontSize: '1.1rem', opacity: 0.95, position: 'relative', zIndex: 1 }}>
                    Experience next-generation candidate assessment with AI that analyzes resumes, generates tailored questions, and provides intelligent insights in real-time.
                </p>
            </div>

            <div className="form-card" style={{
                background: 'white',
                borderRadius: '24px',
                padding: '3rem',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.08)',
                marginBottom: '2.5rem',
                border: '1px solid rgba(102, 126, 234, 0.1)'
            }}>
                {result ? (
                    <div style={{ textAlign: 'center', padding: '1rem' }}>
                        <div style={{
                            width: '70px', height: '70px', background: '#d1fae5', color: '#10b981',
                            borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: '2rem', margin: '0 auto 1rem'
                        }}>
                            <i className="fa-solid fa-check"></i>
                        </div>
                        <h2 style={{ justifyContent: 'center', marginBottom: '0.5rem', color: '#065f46' }}>{result.message}</h2>
                        <p style={{ color: '#4b5563', marginBottom: '1.5rem' }}>
                            Invites have been sent internally. Here are the generated links for testing:
                        </p>

                        <div style={{
                            background: '#f9fafb', padding: '1rem', borderRadius: '12px',
                            marginBottom: '1.5rem', textAlign: 'left', maxHeight: '300px', overflowY: 'auto'
                        }}>
                            {result.candidates.map((c, index) => (
                                <div key={index} style={{
                                    background: 'white', padding: '1rem', borderRadius: '8px', marginBottom: '0.5rem',
                                    border: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                                }}>
                                    <div>
                                        <strong style={{ color: '#374151' }}>{c.name}</strong>
                                        <div style={{ color: '#6b7280', fontSize: '0.85rem' }}>{c.email}</div>
                                    </div>
                                    <a href={c.link} target="_blank" rel="noopener noreferrer" style={{
                                        color: '#667eea', fontWeight: '600', fontSize: '0.9rem', textDecoration: 'none',
                                        border: '1px solid #667eea', padding: '0.25rem 0.75rem', borderRadius: '6px'
                                    }}>
                                        Open Link
                                    </a>
                                </div>
                            ))}
                        </div>

                        <button onClick={() => window.location.reload()} className="enhanced-btn" style={{
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            color: 'white', border: 'none', padding: '1.2rem 3rem', borderRadius: '12px',
                            fontSize: '1.1rem', fontWeight: '600', cursor: 'pointer', display: 'inline-flex',
                            alignItems: 'center', gap: '0.75rem', width: 'auto'
                        }}>
                            <i className="fa-solid fa-plus"></i> Send More Invites
                        </button>
                    </div>
                ) : (
                    <>
                        <h2 style={{ fontSize: '1.8rem', color: '#1f2937', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <i className="fa-solid fa-user-plus" style={{ color: '#667eea' }}></i> Candidate Information
                        </h2>
                        <p className="form-subtitle" style={{ color: '#6b7280', marginBottom: '2.5rem', fontSize: '1rem' }}>
                            Enter candidate details to begin the AI interview session
                        </p>

                        {error && (
                            <div style={{
                                padding: '1rem', backgroundColor: '#fee2e2', color: '#b91c1c', borderRadius: '8px', marginBottom: '1.5rem', border: '1px solid #fecaca'
                            }}>
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit}>
                            <div className="input-grid" style={{ marginTop: '1rem' }}>
                                <label htmlFor="jobDescription" style={{ fontSize: '1rem', fontWeight: '600', color: '#1f2937', marginBottom: '1rem', display: 'block' }}>
                                    <i className="fa-solid fa-briefcase" style={{ marginRight: '0.5rem', color: '#667eea' }}></i>
                                    Job Description
                                </label>
                                <textarea
                                    id="jobDescription"
                                    value={jobDescription}
                                    onChange={(e) => setJobDescription(e.target.value)}
                                    style={{
                                        width: '100%', height: '150px', padding: '1rem', border: '2px solid #e2e8f0',
                                        borderRadius: '16px', resize: 'vertical', fontFamily: 'inherit', fontSize: '0.95rem',
                                        lineHeight: '1.5', color: '#1f2937', background: '#f8f9fa', transition: 'all 0.3s ease'
                                    }}
                                    placeholder="Paste the job description here to help the AI tailor questions..."
                                    required
                                />
                            </div>

                            <div style={{ marginTop: '2rem' }}>
                                <label style={{ fontSize: '1rem', fontWeight: '600', color: '#1f2937', marginBottom: '1rem', display: 'block' }}>
                                    <i className="fa-solid fa-users" style={{ marginRight: '0.5rem', color: '#667eea' }}></i>
                                    Candidate List (CSV / Excel)
                                </label>
                                <div
                                    className="enhanced-upload-zone"
                                    onDrop={handleDrop}
                                    onDragOver={handleDragOver}
                                    onClick={() => document.getElementById('candidateList').click()}
                                    style={{
                                        border: '3px dashed #d1d5db', borderRadius: '16px', padding: '3rem 2rem', textAlign: 'center',
                                        background: 'linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%)', transition: 'all 0.3s ease', cursor: 'pointer',
                                        position: 'relative', overflow: 'hidden', height: '200px', display: 'flex', flexDirection: 'column', justifyContent: 'center'
                                    }}
                                >
                                    <input
                                        type="file"
                                        id="candidateList"
                                        onChange={handleFileChange}
                                        accept=".csv,.xls,.xlsx"
                                        style={{ display: 'none' }}
                                    />

                                    {!file ? (
                                        <div className="upload-content-wrapper">
                                            <div className="upload-icon-large" style={{
                                                width: '60px', height: '60px', fontSize: '2rem', margin: '0 auto 1rem',
                                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '20px',
                                                display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white',
                                                boxShadow: '0 10px 30px rgba(102, 126, 234, 0.3)'
                                            }}>
                                                <i className="fa-solid fa-file-csv"></i>
                                            </div>
                                            <p className="upload-text-main" style={{ fontSize: '1.1rem', fontWeight: '600', color: '#1f2937', marginBottom: '0.5rem' }}>Drop candidate list here</p>
                                            <p className="upload-text-sub" style={{ color: '#6b7280', fontSize: '0.95rem' }}>CSV or Excel with columns: <strong>Name, Email</strong></p>
                                        </div>
                                    ) : (
                                        <div className="file-selected active" style={{
                                            display: 'flex', marginTop: '1rem', padding: '1rem 1.5rem', background: 'white',
                                            borderRadius: '12px', alignItems: 'center', gap: '1rem', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)'
                                        }}>
                                            <div className="file-icon" style={{
                                                width: '40px', height: '40px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                                borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '1.3rem'
                                            }}>
                                                <i className="fa-solid fa-file-excel"></i>
                                            </div>
                                            <div className="file-info" style={{ flex: 1, textAlign: 'left' }}>
                                                <div className="file-name-display" style={{ fontWeight: '600', color: '#1f2937', fontSize: '0.9rem' }}>{file.name}</div>
                                            </div>
                                            <button type="button" onClick={(e) => { e.stopPropagation(); removeFile(); }} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '1.1rem' }}>
                                                <i className="fa-solid fa-xmark"></i>
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div style={{ marginTop: '2.5rem' }}>
                                <button type="submit" className="enhanced-btn" disabled={isUploading} style={{
                                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none',
                                    padding: '1.2rem 3rem', borderRadius: '12px', fontSize: '1.1rem', fontWeight: '600', cursor: isUploading ? 'not-allowed' : 'pointer',
                                    transition: 'all 0.3s ease', boxShadow: '0 10px 30px rgba(102, 126, 234, 0.3)', display: 'inline-flex',
                                    alignItems: 'center', gap: '0.75rem', width: '100%', justifyContent: 'center', opacity: isUploading ? 0.6 : 1
                                }}>
                                    {isUploading ? (
                                        <>
                                            <i className="fa-solid fa-spinner fa-spin"></i>
                                            <span>Processing Bulk Invites...</span>
                                        </>
                                    ) : (
                                        <>
                                            <i className="fa-regular fa-paper-plane"></i>
                                            <span>Send Bulk Invites</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </>
                )}
            </div>
            {/* How It Works Section */}
            <section style={{ marginBottom: '4rem' }}>
                <h2 style={{ fontSize: '1.8rem', marginBottom: '1.5rem', color: '#1f2937' }}>
                    <i className="fa-solid fa-lightbulb" style={{ color: '#667eea', marginRight: '0.75rem' }}></i>
                    How Bulk Invite Works
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem' }}>
                    {[
                        { icon: 'fa-file-csv', title: 'Upload List', text: 'Upload a CSV or Excel file containing candidate names and email addresses.', color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', step: 1 },
                        { icon: 'fa-wand-magic-sparkles', title: 'Auto-Invite', text: 'The system generates unique interview links and sends invitations internally.', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', step: 2 },
                        { icon: 'fa-user-pen', title: 'Candidate Input', text: 'Candidates click the link, verify details, and upload their resume.', color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', step: 3 },
                        { icon: 'fa-brain', title: 'AI Extraction', text: 'AI extracts resume data and starts the interview based on the Job Description.', color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', step: 4 }
                    ].map((item, i) => (
                        <div key={i} style={{
                            background: 'white', borderRadius: '20px', padding: '2rem', transition: 'all 0.3s ease',
                            position: 'relative', overflow: 'hidden', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                        }}>
                            <div style={{
                                width: '64px', height: '64px', borderRadius: '16px', display: 'flex', alignItems: 'center',
                                justifyContent: 'center', marginBottom: '1.25rem', fontSize: '1.8rem', color: 'white', background: item.color
                            }}>
                                <i className={`fa-solid ${item.icon}`}></i>
                            </div>
                            <h3 style={{ fontSize: '1.1rem', color: '#1f2937', marginBottom: '0.75rem' }}>
                                <span style={{
                                    display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '32px', height: '32px',
                                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', borderRadius: '50%',
                                    fontWeight: '700', fontSize: '0.9rem', marginRight: '0.5rem'
                                }}>{item.step}</span>
                                {item.title}
                            </h3>
                            <p style={{ color: '#6b7280', fontSize: '0.95rem', lineHeight: '1.6' }}>{item.text}</p>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default AiInterview;
