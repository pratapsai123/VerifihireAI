import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import '../styles/Dashboard.css';
import '../styles/ResumeMatcher.css';

const ResumeMatcher = () => {
    const [files, setFiles] = useState([]);
    const [jobDescription, setJobDescription] = useState('');
    const [threshold, setThreshold] = useState(70);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [results, setResults] = useState(null);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setFiles(Array.from(e.target.files));
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            setFiles(Array.from(e.dataTransfer.files));
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const removeFile = (index) => {
        const newFiles = [...files];
        newFiles.splice(index, 1);
        setFiles(newFiles);
    };

    const handleMatch = async () => {
        if (files.length === 0 || !jobDescription) {
            alert('Please provide at least one resume and a job description.');
            return;
        }

        setIsAnalyzing(true);
        const formData = new FormData();
        files.forEach(file => {
            formData.append('resume', file);
        });
        formData.append('job_description', jobDescription);
        formData.append('threshold', threshold);

        try {
            const response = await axios.post(`${API_BASE_URL}/ai-candidates/match/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            const data = response.data;
            setResults(Array.isArray(data) ? data : [data]);
        } catch (error) {
            console.error('Error:', error);
            alert(`Failed to analyze: ${error.response?.data?.detail || error.message || 'Analysis failed'}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const getProgressColor = (percentage) => {
        if (percentage >= 70) return '#10B981';
        if (percentage >= 40) return '#F59E0B';
        return '#EF4444';
    };

    return (
        <div className="resume-matcher-page">
            <div className="mesh-bg"></div>
            <div className="bg-shape" style={{ width: '600px', height: '600px', background: 'rgba(99, 102, 241, 0.15)', top: '-10%', right: '-5%' }}></div>
            <div className="bg-shape" style={{ width: '500px', height: '500px', background: 'rgba(168, 85, 247, 0.15)', bottom: '-10%', left: '-5%', animationDelay: '-5s' }}></div>

            <div className="matcher-container">
                <header className="glass-card page-header">
                    <div className="badge">
                        <i className="fa-solid fa-magnifying-glass-chart"></i> RESUME ANALYTICS
                    </div>
                    <h1>Resume <span style={{ color: '#6366F1' }}>Matcher</span></h1>
                    <p>
                        AI-powered side-by-side analysis of candidate fit against specific role requirements.
                    </p>
                </header>

                <div className="form-stack">
                    {!results ? (
                        <>
                            <div className="glass-card">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                                    <div className="module-icon-wrapper indigo-glow" style={{ width: '40px', height: '40px', borderRadius: '10px' }}>
                                        <i className="fa-solid fa-file-contract"></i>
                                    </div>
                                    <div>
                                        <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#111827', margin: 0 }}>Job Description</h3>
                                        <p style={{ color: '#6B7280', fontSize: '0.85rem' }}>Define the benchmark for comparison.</p>
                                    </div>
                                </div>
                                <textarea
                                    value={jobDescription}
                                    onChange={(e) => setJobDescription(e.target.value)}
                                    placeholder="Paste the job requirements, responsibilities, and qualifications..."
                                    className="modern-textarea"
                                />
                            </div>

                            <div className="glass-card">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                                    <div className="module-icon-wrapper indigo-glow" style={{ width: '40px', height: '40px', borderRadius: '10px' }}>
                                        <i className="fa-solid fa-file-pdf"></i>
                                    </div>
                                    <div>
                                        <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#111827', margin: 0 }}>Candidate Resumes</h3>
                                        <p style={{ color: '#6B7280', fontSize: '0.85rem' }}>Match multiple candidates at once.</p>
                                    </div>
                                </div>

                                <div
                                    onDrop={handleDrop}
                                    onDragOver={handleDragOver}
                                    onClick={() => document.getElementById('resumeFile').click()}
                                    className="upload-zone"
                                >
                                    <input type="file" id="resumeFile" accept=".pdf" multiple style={{ display: 'none' }} onChange={handleFileChange} />

                                    {files.length === 0 ? (
                                        <>
                                            <div style={{
                                                width: '56px', height: '56px', background: 'white', color: '#6366F1',
                                                borderRadius: '16px', display: 'flex', alignItems: 'center',
                                                justifyContent: 'center', marginBottom: '1.5rem', fontSize: '1.5rem',
                                                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05)'
                                            }}>
                                                <i className="fa-solid fa-cloud-arrow-up"></i>
                                            </div>
                                            <p style={{ fontSize: '1.1rem', fontWeight: '800', color: '#1E293B', marginBottom: '0.5rem' }}>Select Resumes</p>
                                            <p style={{ fontSize: '0.85rem', color: '#94A3B8' }}>Click or drag PDF files here</p>
                                        </>
                                    ) : (
                                        <div style={{ width: '100%', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
                                            {files.map((file, idx) => (
                                                <div key={idx} style={{
                                                    background: 'white', padding: '1rem', borderRadius: '16px', border: '1px solid #E2E8F0',
                                                    display: 'flex', alignItems: 'center', gap: '0.75rem', position: 'relative'
                                                }}>
                                                    <i className="fa-solid fa-file-pdf" style={{ color: '#EF4444' }}></i>
                                                    <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#1E293B', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                        {file.name}
                                                    </span>
                                                    <button
                                                        onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                                                        style={{
                                                            position: 'absolute', top: '-10px', right: '-10px', background: '#EF4444', color: 'white',
                                                            border: 'none', borderRadius: '50%', width: '22px', height: '22px', fontSize: '12px', cursor: 'pointer',
                                                            display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 8px rgba(239, 68, 68, 0.3)'
                                                        }}
                                                    >
                                                        <i className="fa-solid fa-xmark"></i>
                                                    </button>
                                                </div>
                                            ))}
                                            <div style={{
                                                border: '2px dashed #6366F1', borderRadius: '16px', padding: '1rem',
                                                display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6366F1', fontSize: '0.8rem', fontWeight: '700',
                                                background: 'rgba(99, 102, 241, 0.05)'
                                            }}>
                                                <i className="fa-solid fa-plus" style={{ marginRight: '6px' }}></i> Add More
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="glass-card">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                                    <div className="module-icon-wrapper indigo-glow" style={{ width: '40px', height: '40px', borderRadius: '10px' }}>
                                        <i className="fa-solid fa-percent"></i>
                                    </div>
                                    <div>
                                        <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#111827', margin: 0 }}>Sensitivity Settings</h3>
                                        <p style={{ color: '#6B7280', fontSize: '0.85rem' }}>Set the minimum match score for qualification.</p>
                                    </div>
                                </div>
                                <div className="threshold-container">
                                    <div style={{ flex: 1 }}>
                                        <input
                                            type="range" min="0" max="100" value={threshold}
                                            onChange={(e) => setThreshold(e.target.value)}
                                            style={{ width: '100%', accentColor: '#6366F1', height: '6px', cursor: 'pointer' }}
                                        />
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem', color: '#94A3B8', fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase' }}>
                                            <span>LENIENT</span>
                                            <span>STRICT</span>
                                        </div>
                                    </div>
                                    <div className="threshold-display">
                                        <div style={{ fontSize: '0.65rem', color: '#6366F1', fontWeight: '800', textTransform: 'uppercase', marginBottom: '2px' }}>THRESHOLD</div>
                                        <div style={{ fontSize: '1.6rem', fontWeight: '900', color: '#1E293B' }}>{threshold}%</div>
                                    </div>
                                </div>
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', alignItems: 'center' }}>
                                <button
                                    onClick={handleMatch}
                                    disabled={isAnalyzing}
                                    className="match-btn"
                                >
                                    {isAnalyzing ? (
                                        <><i className="fa-solid fa-atom fa-spin"></i> Analyzing Candidate Profiles...</>
                                    ) : (
                                        <><i className="fa-solid fa-wand-magic-sparkles"></i> Compare Resumes</>
                                    )}
                                </button>


                            </div>
                        </>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                <h2 style={{ fontSize: '2rem', fontWeight: '800', color: '#1e293b', letterSpacing: '-0.02em' }}>Match <span style={{ color: '#6366F1' }}>Insights</span></h2>
                                <button onClick={() => setResults(null)} className="view-details-btn">
                                    <i className="fa-solid fa-chevron-left" style={{ marginRight: '0.5rem' }}></i> New Analysis
                                </button>
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                                {results.map((data, index) => {
                                    const percentage = data.match_percentage || 0;
                                    const progressColor = getProgressColor(percentage);
                                    return (
                                        <div key={index} className="glass-card result-card">
                                            <div className="score-circle" style={{ background: `conic-gradient(${progressColor} ${percentage * 3.6}deg, #f1f5f9 0deg)` }}>
                                                <div className="score-inner">
                                                    <span className="score-value" style={{ color: progressColor }}>{percentage}%</span>
                                                    <span className="score-label">MATCH</span>
                                                </div>
                                            </div>

                                            <div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
                                                    <h4 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '800', color: '#1e293b' }}>{data.filename || 'Untitled Resume'}</h4>
                                                    <span className="status-tag" style={{
                                                        background: data.is_eligible ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                                        color: data.is_eligible ? '#059669' : '#dc2626'
                                                    }}>
                                                        {data.is_eligible ? 'ELIGIBLE' : 'GAP DETECTED'}
                                                    </span>
                                                </div>
                                                <p style={{ margin: 0, color: '#64748b', fontSize: '1rem', lineHeight: '1.6', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                                    {data.summary || 'AI has analyzed this profile against role expectations.'}
                                                </p>
                                            </div>

                                            <div style={{ textAlign: 'right' }}>
                                                <button className="view-details-btn">
                                                    View Details
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ResumeMatcher;