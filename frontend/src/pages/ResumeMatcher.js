import React, { useState } from 'react';
import axios from 'axios';
import '../styles/Dashboard.css';

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
            // Using localhost:8001 as per original matcher.js
            const response = await axios.post('http://localhost:8001/api/ai-candidates/match/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            // Ensure results is always an array
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
        if (percentage >= 70) return '#05CD99';
        if (percentage >= 40) return '#FFB547';
        return '#EE5D50';
    };

    return (
        <div className="dashboard-container" style={{ paddingTop: '2rem', display: 'flex', justifyContent: 'center' }}>
            <div className="matcher-container" style={{ width: '100%', maxWidth: '800px' }}>
                {/* Hero Section */}
                <div className="matcher-hero" style={{
                    background: 'linear-gradient(135deg, #4318FF 0%, #764ba2 100%)',
                    borderRadius: '24px',
                    padding: '3rem',
                    marginBottom: '2rem',
                    color: 'white',
                    textAlign: 'center',
                    position: 'relative',
                    overflow: 'hidden',
                    boxShadow: '0 20px 40px rgba(67, 24, 255, 0.2)'
                }}>
                    <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', position: 'relative', zIndex: 1, color: 'white' }}>Resume Matcher</h1>
                    <p style={{ fontSize: '1.1rem', opacity: 0.9, position: 'relative', zIndex: 1, color: 'rgba(255, 255, 255, 0.9)' }}>
                        AI-powered side-by-side analysis of candidate fit.
                    </p>
                </div>

                {!results ? (
                    <div id="inputSection">
                        <div className="main-card" style={{
                            background: 'white',
                            borderRadius: '24px',
                            padding: '2.5rem',
                            boxShadow: '0 10px 30px rgba(112, 144, 176, 0.1)',
                            marginBottom: '2rem',
                            border: '1px solid rgba(255, 255, 255, 0.5)'
                        }}>
                            {/* Step 1: Upload */}
                            <div style={{ marginBottom: '2.5rem' }}>
                                <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#1B254B', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <div style={{
                                        color: '#4318FF', background: '#eef2ff', width: '36px', height: '36px', display: 'flex',
                                        alignItems: 'center', justifyContent: 'center', borderRadius: '10px', fontSize: '1.1rem'
                                    }}><i className="fa-solid fa-cloud-arrow-up"></i></div>
                                    Upload Candidates
                                </h3>
                                <div
                                    className="enhanced-drop-zone"
                                    onDrop={handleDrop}
                                    onDragOver={handleDragOver}
                                    onClick={() => document.getElementById('resumeFile').click()}
                                    style={{
                                        border: '2px dashed #E0E5F2', borderRadius: '16px', background: '#F8F9FF', padding: '2.5rem',
                                        textAlign: 'center', transition: 'all 0.3s ease', cursor: 'pointer'
                                    }}
                                >
                                    <i className="fa-solid fa-file-pdf" style={{ fontSize: '3rem', color: '#4318FF', marginBottom: '1rem' }}></i>
                                    <h4 style={{ margin: '0 0 0.5rem 0', color: '#1B254B' }}>{files.length > 0 ? `Selected: ${files.length} file(s)` : 'Drag & Drop Resumes Here'}</h4>
                                    <p style={{ color: '#A3AED0', fontSize: '0.9rem', marginBottom: '0' }}>
                                        or <span style={{ color: '#4318FF', fontWeight: '600', textDecoration: 'underline' }}>browse files</span> from your computer
                                    </p>
                                    <input type="file" id="resumeFile" accept=".pdf" multiple style={{ display: 'none' }} onChange={handleFileChange} />
                                </div>
                            </div>

                            {/* Step 2: Job Description */}
                            <div style={{ marginBottom: '2.5rem' }}>
                                <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#1B254B', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <div style={{
                                        color: '#4318FF', background: '#eef2ff', width: '36px', height: '36px', display: 'flex',
                                        alignItems: 'center', justifyContent: 'center', borderRadius: '10px', fontSize: '1.1rem'
                                    }}><i className="fa-solid fa-briefcase"></i></div>
                                    Job Description
                                </h3>
                                <textarea
                                    value={jobDescription}
                                    onChange={(e) => setJobDescription(e.target.value)}
                                    placeholder="Paste the job requirements, responsibilities, and qualifications here..."
                                    style={{
                                        width: '100%', minHeight: '150px', padding: '1.25rem', border: '1px solid #E0E5F2',
                                        borderRadius: '16px', background: '#F8F9FF', fontFamily: "'DM Sans', sans-serif",
                                        fontSize: '0.95rem', lineHeight: '1.6', color: '#1B254B', resize: 'vertical',
                                        transition: 'all 0.3s ease'
                                    }}
                                ></textarea>
                            </div>

                            {/* Step 3: Settings */}
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                    <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#1B254B', marginBottom: '0', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <div style={{
                                            color: '#4318FF', background: '#eef2ff', width: '36px', height: '36px', display: 'flex',
                                            alignItems: 'center', justifyContent: 'center', borderRadius: '10px', fontSize: '1.1rem'
                                        }}><i className="fa-solid fa-sliders"></i></div>
                                        Match Threshold
                                    </h3>
                                    <span style={{ fontSize: '1.1rem', fontWeight: '700', color: '#4318FF', background: '#eef2ff', padding: '0.25rem 0.75rem', borderRadius: '8px' }}>
                                        {threshold}%
                                    </span>
                                </div>
                                <input
                                    type="range" min="0" max="100" value={threshold}
                                    onChange={(e) => setThreshold(e.target.value)}
                                    style={{ width: '100%', accentColor: '#4318FF', cursor: 'pointer', height: '6px', background: '#E0E5F2', borderRadius: '5px' }}
                                />
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', color: '#A3AED0', fontSize: '0.8rem' }}>
                                    <span>Lenient (0%)</span>
                                    <span>Strict (100%)</span>
                                </div>
                            </div>
                        </div>

                        {/* Action */}
                        <div className="matcher-actions">
                            <button
                                onClick={handleMatch}
                                disabled={isAnalyzing}
                                style={{
                                    width: '100%', justifyContent: 'center', padding: '1.25rem', background: '#4318FF',
                                    color: 'white', borderRadius: '0.75rem', fontWeight: '600', border: 'none', cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                                    display: 'flex', alignItems: 'center', gap: '0.5rem', opacity: isAnalyzing ? 0.7 : 1
                                }}
                            >
                                {isAnalyzing ? (
                                    <>
                                        <i className="fa-solid fa-spinner fa-spin"></i> Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <i className="fa-solid fa-wand-magic-sparkles"></i> Analyze Candidate Fit
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                ) : (
                    <div id="resultSection" className="result-container" style={{ marginTop: '2rem', display: 'block' }}>
                        <div className="result-header" style={{ textAlign: 'center', marginBottom: '2rem' }}>
                            <h2 style={{ fontSize: '2rem', background: 'linear-gradient(135deg, #1B254B, #4318FF)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Analysis Results</h2>
                            <button
                                onClick={() => setResults(null)}
                                style={{
                                    margin: '1.5rem auto', padding: '0.75rem 2rem', fontSize: '1rem', background: '#4318FF',
                                    color: 'white', borderRadius: '0.75rem', fontWeight: '600', border: 'none', cursor: 'pointer',
                                    display: 'flex', alignItems: 'center', gap: '0.5rem'
                                }}
                            >
                                <i className="fa-solid fa-rotate-right"></i> Analyze More
                            </button>
                        </div>
                        <div className="results-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
                            {results.map((data, index) => {
                                const percentage = data.match_percentage || 0;
                                const progressColor = getProgressColor(percentage);
                                return (
                                    <div key={index} className="matcher-card result-card-item" style={{
                                        background: 'white', borderRadius: '24px', padding: '2.5rem', boxShadow: '0 10px 30px rgba(112, 144, 176, 0.1)', border: '1px solid rgba(255, 255, 255, 0.5)'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                            <h4 style={{ margin: '0', fontSize: '1.1rem', color: '#1B254B', display: 'flex', alignItems: 'center', gap: '0.5rem', maxWidth: '65%' }}>
                                                <i className="fa-solid fa-file-pdf" style={{ color: '#4318FF' }}></i>
                                                <span style={{ textOverflow: 'ellipsis', whiteSpace: 'nowrap', overflow: 'hidden' }}>{data.filename || 'Candidate Resume'}</span>
                                            </h4>
                                            <span style={{
                                                padding: '0.5rem 1rem', borderRadius: '12px', fontSize: '0.85rem', fontWeight: '700',
                                                background: data.is_eligible ? '#E6FBF5' : '#FFF8E6', color: data.is_eligible ? '#05CD99' : '#FFA800'
                                            }}>
                                                {data.is_eligible ? 'Eligible' : 'Not Eligible'}
                                            </span>
                                        </div>

                                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '2rem 0' }}>
                                            <div style={{
                                                position: 'relative', width: '140px', height: '140px', borderRadius: '50%',
                                                background: `conic-gradient(${progressColor} ${percentage}%, #F0F2F9 ${percentage}%)`,
                                                display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: 'inset 0 0 10px rgba(0,0,0,0.05)'
                                            }}>
                                                <div style={{
                                                    position: 'absolute', width: '115px', height: '115px', background: 'white',
                                                    borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    boxShadow: '0 5px 15px rgba(0,0,0,0.05)'
                                                }}>
                                                    <span style={{ fontSize: '2rem', fontWeight: '800', color: '#1B254B' }}>{percentage}%</span>
                                                </div>
                                            </div>
                                            <p style={{ marginTop: '1rem', color: '#A3AED0', fontSize: '0.9rem' }}>Match Score</p>
                                        </div>

                                        <div style={{ background: '#F8F9FF', padding: '1.5rem', borderRadius: '16px', minHeight: '120px' }}>
                                            <h5 style={{ margin: '0 0 0.5rem 0', color: '#1B254B', fontSize: '0.95rem' }}>AI Summary</h5>
                                            <p style={{ fontSize: '0.9rem', color: '#A3AED0', lineHeight: '1.6', margin: '0' }}>{data.summary || 'No summary provided.'}</p>
                                        </div>

                                        <button
                                            className="action-btn"
                                            style={{
                                                width: '100%', marginTop: '1.5rem', justifyContent: 'center', display: 'flex',
                                                background: '#F4F7FE', border: 'none', padding: '0.6rem 1.2rem', borderRadius: '10px',
                                                fontWeight: '700', fontSize: '0.9rem', color: '#4318FF', cursor: 'pointer'
                                            }}
                                            onClick={() => alert('Detailed report feature coming soon!')}
                                        >
                                            View Full Report
                                        </button>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResumeMatcher;
