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
            const response = await axios.post('http://localhost:8001/api/ai-candidates/match/', formData, {
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

    // Premium UI Elements
    const SectionHeader = ({ iconClass, title, subtitle, colorClass }) => (
        <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.4rem' }}>
                <div className={`module-icon-wrapper ${colorClass}`} style={{ width: '32px', height: '32px', borderRadius: '8px' }}>
                    <i className={`${iconClass}`} style={{ fontSize: '0.9rem' }}></i>
                </div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '800', color: '#111827', margin: 0, letterSpacing: '-0.01em' }}>{title}</h3>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#6B7280', margin: 0 }}>{subtitle}</p>
        </div>
    );

    return (
        <div className="dashboard-container">
            <div className="dashboard-main" style={{ maxWidth: '900px', paddingTop: '2rem' }}>

                {/* Header Section */}
                <header style={{
                    position: 'relative',
                    padding: '2.5rem 2rem',
                    background: 'white',
                    borderRadius: '24px',
                    marginBottom: '2rem',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
                    border: '1px solid #E5E7EB',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        position: 'absolute', top: '-40px', right: '-40px', width: '180px', height: '180px',
                        background: 'radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%)', borderRadius: '50%'
                    }}></div>

                    <div style={{ position: 'relative', zIndex: 1 }}>
                        <div style={{
                            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                            background: '#EEF2FF', color: '#4F46E5',
                            padding: '0.4rem 0.8rem', borderRadius: '10px', fontSize: '0.75rem',
                            fontWeight: '700', marginBottom: '1rem', border: '1px solid rgba(79, 70, 229, 0.1)'
                        }}>
                            <i className="fa-solid fa-magnifying-glass-chart"></i> RESUME ANALYTICS
                        </div>
                        <h1 style={{ fontSize: '2.4rem', fontWeight: '900', color: '#111827', margin: '0 0 0.5rem', letterSpacing: '-0.03em' }}>
                            Resume <span style={{ color: '#4F46E5' }}>Matcher</span>
                        </h1>
                        <p style={{ color: '#6B7280', fontSize: '1rem', maxWidth: '500px' }}>
                            AI-powered side-by-side analysis of candidate fit against specific role requirements.
                        </p>
                    </div>
                </header>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                    {!results ? (
                        <>
                            {/* Role Context Card */}
                            <div className="module-card" style={{ padding: '2rem', background: 'white', borderRadius: '24px', border: '1px solid #E5E7EB' }}>
                                <SectionHeader
                                    iconClass="fa-solid fa-file-contract"
                                    title="Job Description"
                                    subtitle="Define the benchmark for comparison."
                                    colorClass="indigo-glow"
                                />
                                <textarea
                                    value={jobDescription}
                                    onChange={(e) => setJobDescription(e.target.value)}
                                    placeholder="Paste the job requirements, responsibilities, and qualifications..."
                                    style={{
                                        width: '100%', height: '180px', padding: '1.25rem', border: '1px solid #E2E8F0',
                                        borderRadius: '16px', resize: 'vertical', fontSize: '0.95rem', lineHeight: '1.6',
                                        color: '#1F2937', background: '#F8FAFC', outline: 'none', transition: 'all 0.3s'
                                    }}
                                />
                            </div>

                            {/* Resume Upload Card */}
                            <div className="module-card" style={{ padding: '2rem', background: 'white', borderRadius: '24px', border: '1px solid #E5E7EB' }}>
                                <SectionHeader
                                    iconClass="fa-solid fa-file-pdf"
                                    title="Candidate Resumes"
                                    subtitle="Match multiple candidates at once."
                                    colorClass="indigo-glow"
                                />

                                <div
                                    onDrop={handleDrop}
                                    onDragOver={handleDragOver}
                                    onClick={() => document.getElementById('resumeFile').click()}
                                    style={{
                                        minHeight: '180px', border: '2px dashed #CBD5E1', borderRadius: '24px',
                                        background: '#F8FAFC', cursor: 'pointer', display: 'flex', flexDirection: 'column',
                                        alignItems: 'center', justifyContent: 'center', padding: '2rem', transition: 'all 0.3s'
                                    }}
                                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#4F46E5'; e.currentTarget.style.background = '#EEF2FF'; }}
                                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#CBD5E1'; e.currentTarget.style.background = '#F8FAFC'; }}
                                >
                                    <input type="file" id="resumeFile" accept=".pdf" multiple style={{ display: 'none' }} onChange={handleFileChange} />

                                    {files.length === 0 ? (
                                        <>
                                            <div style={{
                                                width: '56px', height: '56px', background: 'white', color: '#4F46E5',
                                                borderRadius: '16px', display: 'flex', alignItems: 'center',
                                                justifyContent: 'center', marginBottom: '1.25rem', fontSize: '1.5rem',
                                                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05)'
                                            }}>
                                                <i className="fa-solid fa-cloud-arrow-up"></i>
                                            </div>
                                            <p style={{ fontSize: '1.1rem', fontWeight: '800', color: '#1E293B', marginBottom: '0.25rem' }}>Select Resumes</p>
                                            <p style={{ fontSize: '0.85rem', color: '#94A3B8' }}>Click or drag PDF files here</p>
                                        </>
                                    ) : (
                                        <div style={{ width: '100%', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '1rem' }}>
                                            {files.map((file, idx) => (
                                                <div key={idx} style={{
                                                    background: 'white', padding: '0.75rem', borderRadius: '12px', border: '1px solid #E2E8F0',
                                                    display: 'flex', alignItems: 'center', gap: '0.75rem', position: 'relative'
                                                }}>
                                                    <i className="fa-solid fa-file-pdf" style={{ color: '#EF4444' }}></i>
                                                    <span style={{ fontSize: '0.8rem', fontWeight: '600', color: '#1E293B', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                        {file.name}
                                                    </span>
                                                    <button
                                                        onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                                                        style={{
                                                            position: 'absolute', top: '-8px', right: '-8px', background: '#EF4444', color: 'white',
                                                            border: 'none', borderRadius: '50%', width: '18px', height: '18px', fontSize: '10px', cursor: 'pointer'
                                                        }}
                                                    >
                                                        <i className="fa-solid fa-xmark"></i>
                                                    </button>
                                                </div>
                                            ))}
                                            <div style={{
                                                border: '1px dashed #4F46E5', borderRadius: '12px', padding: '0.75rem',
                                                display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4F46E5', fontSize: '12px', fontWeight: '700'
                                            }}>
                                                <i className="fa-solid fa-plus" style={{ marginRight: '4px' }}></i> Add More
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Match Parameters Card */}
                            <div className="module-card" style={{ padding: '2rem', background: 'white', borderRadius: '24px', border: '1px solid #E5E7EB' }}>
                                <SectionHeader
                                    iconClass="fa-solid fa-percent"
                                    title="Sensitivity Settings"
                                    subtitle="Set the minimum match score for qualification."
                                    colorClass="indigo-glow"
                                />
                                <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                                    <div style={{ flex: 1 }}>
                                        <input
                                            type="range" min="0" max="100" value={threshold}
                                            onChange={(e) => setThreshold(e.target.value)}
                                            style={{ width: '100%', accentColor: '#4F46E5', height: '6px', cursor: 'pointer' }}
                                        />
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.75rem', color: '#94A3B8', fontSize: '0.75rem', fontWeight: '600' }}>
                                            <span>LENIENT</span>
                                            <span>STRICT</span>
                                        </div>
                                    </div>
                                    <div style={{
                                        padding: '1rem 1.5rem', background: '#EEF2FF', borderRadius: '16px', border: '1px solid rgba(79, 70, 229, 0.1)',
                                        textAlign: 'center', minWidth: '100px'
                                    }}>
                                        <div style={{ fontSize: '0.7rem', color: '#4F46E5', fontWeight: '800', textTransform: 'uppercase' }}>THRESHOLD</div>
                                        <div style={{ fontSize: '1.5rem', fontWeight: '900', color: '#111827' }}>{threshold}%</div>
                                    </div>
                                </div>
                            </div>

                            {/* Action Area */}
                            <div style={{ marginTop: '0.5rem' }}>
                                <button
                                    onClick={handleMatch}
                                    disabled={isAnalyzing}
                                    style={{
                                        width: '100%', padding: '1.25rem', background: '#4F46E5', color: 'white',
                                        border: 'none', borderRadius: '20px', fontSize: '1.1rem', fontWeight: '700',
                                        cursor: isAnalyzing ? 'not-allowed' : 'pointer',
                                        boxShadow: '0 10px 20px -5px rgba(79, 70, 229, 0.4)',
                                        transition: 'all 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem'
                                    }}
                                >
                                    {isAnalyzing ? (
                                        <><i className="fa-solid fa-spinner fa-spin"></i> Analyzing Candidate Profiles...</>
                                    ) : (
                                        <><i className="fa-solid fa-wand-magic-sparkles"></i> Compare Resumes</>
                                    )}
                                </button>

                                <div style={{ marginTop: '2.5rem', display: 'flex', justifyContent: 'center', gap: '4rem' }}>
                                    {[
                                        { icon: 'fa-brain', text: 'AI Feature Extraction' },
                                        { icon: 'fa-check-double', text: 'Bias-Free Screening' },
                                        { icon: 'fa-table-columns', text: 'Multi-Resumes Support' }
                                    ].map((feat, i) => (
                                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: '#94A3B8', fontSize: '0.8rem', fontWeight: '700' }}>
                                            <i className={`fa-solid ${feat.icon}`} style={{ color: '#4F46E5' }}></i> {feat.text}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                <h2 style={{ fontSize: '1.8rem', fontWeight: '900', color: '#111827', letterSpacing: '-0.02em' }}>Match <span style={{ color: '#4F46E5' }}>Insights</span></h2>
                                <button onClick={() => setResults(null)} style={{ padding: '0.6rem 1.25rem', background: 'white', border: '1px solid #E2E8F0', borderRadius: '12px', fontWeight: '700', color: '#64748B', cursor: 'pointer' }}>
                                    <i className="fa-solid fa-chevron-left" style={{ marginRight: '0.5rem' }}></i> New Analysis
                                </button>
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                {results.map((data, index) => {
                                    const percentage = data.match_percentage || 0;
                                    const progressColor = getProgressColor(percentage);
                                    return (
                                        <div key={index} className="module-card" style={{ padding: '1.5rem', background: 'white', borderRadius: '24px', border: '1px solid #E5E7EB', display: 'grid', gridTemplateColumns: '120px 1fr 200px', gap: '2rem', alignItems: 'center' }}>
                                            {/* Score Circle */}
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{
                                                    width: '80px', height: '80px', borderRadius: '50%',
                                                    background: `conic-gradient(${progressColor} ${percentage * 3.6}deg, #F1F5F9 0deg)`,
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto', position: 'relative'
                                                }}>
                                                    <div style={{ width: '64px', height: '64px', background: 'white', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '900', fontSize: '1.2rem', color: '#111827' }}>
                                                        {percentage}%
                                                    </div>
                                                </div>
                                                <div style={{ fontSize: '0.7rem', fontWeight: '800', color: '#94A3B8', marginTop: '0.5rem', textTransform: 'uppercase' }}>MATCH</div>
                                            </div>

                                            {/* Content */}
                                            <div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                                                    <h4 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '800', color: '#111827' }}>{data.filename || 'Untitled Resume'}</h4>
                                                    <span style={{
                                                        padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800',
                                                        background: data.is_eligible ? '#DCFCE7' : '#FEF2F2', color: data.is_eligible ? '#16A34A' : '#EF4444'
                                                    }}>
                                                        {data.is_eligible ? 'ELIGIBLE' : 'GAP DETECTED'}
                                                    </span>
                                                </div>
                                                <p style={{ margin: 0, color: '#64748B', fontSize: '0.9rem', lineHeight: '1.5', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                                    {data.summary || 'AI has analyzed this profile against role expectations.'}
                                                </p>
                                            </div>

                                            {/* Action */}
                                            <div style={{ textAlign: 'right' }}>
                                                <button style={{
                                                    padding: '0.75rem 1.5rem', background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px',
                                                    fontWeight: '700', fontSize: '0.85rem', color: '#111827', cursor: 'pointer', transition: 'all 0.2s'
                                                }} onMouseEnter={(e) => { e.target.style.background = '#F1F5F9'; }}>
                                                    View Match Details
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
