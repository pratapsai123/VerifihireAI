import React, { useState } from 'react';
import axios from 'axios';
import '../styles/Dashboard.css';

const AiInterview = () => {
    const [jobDescription, setJobDescription] = useState('');
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const [fromDate, setFromDate] = useState('');
    const [fromTime, setFromTime] = useState('');
    const [untilDate, setUntilDate] = useState('');
    const [untilTime, setUntilTime] = useState('');

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
        setError('');

        if (!file || !jobDescription) {
            setError('Please provide both a Candidate List and Job Description.');
            return;
        }

        setIsUploading(true);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('job_description', jobDescription);

        if (fromDate && fromTime) {
            formData.append('available_from', new Date(`${fromDate}T${fromTime}`).toISOString());
        }
        if (untilDate && untilTime) {
            formData.append('available_until', new Date(`${untilDate}T${untilTime}`).toISOString());
        }

        try {
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
        <div className="dashboard-container" style={{ paddingTop: 0 }}>
            <div className="dashboard-main" style={{ width: '100%', maxWidth: '100%', padding: '0', margin: '0' }}>

                {/* 1. Header with Background Glow */}
                <header style={{
                    position: 'relative',
                    padding: '0 2rem',
                    background: 'transparent',
                    marginBottom: '0',
                    overflow: 'hidden'
                }}>

                    <div style={{ position: 'relative', zIndex: 1 }}>
                        <div style={{
                            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                            color: '#4F46E5',
                            padding: '0', fontSize: '0.8rem',
                            fontWeight: '700', marginBottom: '0.2rem'
                        }}>
                            <i className="fa-solid fa-bolt-lightning"></i> AI AUTOMATION HUB
                        </div>
                        <h1 style={{ fontSize: '2.8rem', fontWeight: '900', color: '#111827', margin: '0', letterSpacing: '-0.04em', lineHeight: 1 }}>
                            AI <span style={{ color: '#6366F1' }}>Interview</span> Creation
                        </h1>
                        <p style={{ color: '#6B7280', fontSize: '1.1rem', maxWidth: '600px', lineHeight: '1.6', marginTop: '0.5rem' }}>
                            Design high-fidelity AI interview experiences by providing job context and candidate lists for automated deployment.
                        </p>
                    </div>
                </header>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                    {result ? (
                        <div className="module-card" style={{ padding: '4rem 2rem', textAlign: 'center', background: 'white', borderRadius: '0', borderLeft: 'none', borderRight: 'none' }}>
                            <div className="module-icon-wrapper teal-glow" style={{ margin: '0 auto 2rem', width: '80px', height: '80px', borderRadius: '24px' }}>
                                <i className="fa-solid fa-check-double" style={{ fontSize: '2rem' }}></i>
                            </div>
                            <h2 style={{ fontSize: '2rem', fontWeight: '800', color: '#111827', marginBottom: '1rem' }}>Interviews Deployed!</h2>
                            <p style={{ color: '#64748B', fontSize: '1.1rem', marginBottom: '3rem', maxWidth: '500px', margin: '0 auto 3rem' }}>
                                Invitations have been sent. Your AI Interviewers are now waiting for candidate responses.
                            </p>

                            <div style={{
                                background: '#F8FAFC', padding: '2rem', borderRadius: '24px',
                                marginBottom: '3rem', textAlign: 'left', border: '1px solid #E2E8F0', boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.02)'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                    <h4 style={{ fontSize: '0.9rem', color: '#1E293B', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Generated Session Links</h4>
                                    <span style={{ fontSize: '0.8rem', color: '#64748B', background: '#E2E8F0', padding: '0.3rem 0.8rem', borderRadius: '8px' }}>{result.candidates.length} Tasks</span>
                                </div>

                                {result.candidates.map((c, index) => (
                                    <div key={index} style={{
                                        background: 'white', padding: '1.25rem', borderRadius: '16px', marginBottom: '0.75rem',
                                        border: '1px solid #E5E7EB', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                        transition: 'all 0.2s', cursor: 'default'
                                    }} onMouseEnter={(e) => e.currentTarget.style.borderColor = '#0D9488'}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                            <div style={{ width: '40px', height: '40px', background: '#F1F5F9', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569', fontWeight: '700' }}>
                                                {c.name.charAt(0)}
                                            </div>
                                            <div>
                                                <div style={{ color: '#0F172A', fontWeight: '700', fontSize: '1rem' }}>{c.name}</div>
                                                <div style={{ color: '#64748B', fontSize: '0.85rem' }}>{c.email}</div>
                                            </div>
                                        </div>
                                        <a href={c.link} target="_blank" rel="noopener noreferrer" style={{
                                            color: '#6366f1', fontWeight: '700', fontSize: '0.85rem', textDecoration: 'none',
                                            padding: '0.6rem 1.25rem', background: '#EEF2FF', borderRadius: '12px',
                                            transition: 'all 0.2s'
                                        }} onMouseEnter={(e) => { e.target.style.background = '#4F46E5'; e.target.style.color = 'white'; }}
                                            onMouseLeave={(e) => { e.target.style.background = '#EEF2FF'; e.target.style.color = '#6366f1'; }}>
                                            Launch Session
                                        </a>
                                    </div>
                                ))}
                            </div>

                            <button onClick={() => window.location.reload()} className="primary-link-btn" style={{ padding: '1.25rem 4rem', fontSize: '1.1rem', borderRadius: '18px' }}>
                                <i className="fa-solid fa-plus-circle" style={{ marginRight: '0.75rem' }}></i> Setup New Interviews
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                            {/* Card 1: JD Section with Rich Visuals */}
                            <div className="module-card" style={{ padding: '2.5rem 2rem', background: 'transparent', borderRadius: '0', border: 'none', borderTop: '1px solid #E5E7EB' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <div className="module-icon-wrapper indigo-glow" style={{ width: '45px', height: '45px', borderRadius: '14px' }}>
                                            <i className="fa-solid fa-file-signature"></i>
                                        </div>
                                        <div>
                                            <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#111827', margin: 0 }}>Job Requirements</h3>
                                            <p style={{ color: '#6B7280', fontSize: '0.9rem', margin: '0.2rem 0 0' }}>Provide the context for the AI interviewer.</p>
                                        </div>
                                    </div>
                                </div>

                                <textarea
                                    value={jobDescription}
                                    onChange={(e) => setJobDescription(e.target.value)}
                                    placeholder="Paste the detailed Job Description here. Include technical skills, soft skills, and specific project requirements. AI will use this to dynamically generate probing questions."
                                    style={{
                                        width: '100%', height: '280px', padding: '1.5rem', border: '1px solid #E2E8F0',
                                        borderRadius: '20px', resize: 'vertical', fontSize: '1rem', lineHeight: '1.7',
                                        color: '#1F2937', background: '#F8FAFC', outline: 'none', transition: 'all 0.3s',
                                        fontFamily: 'inherit', boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.02)'
                                    }}
                                    required
                                />
                                <div style={{ marginTop: '1.25rem', display: 'flex', gap: '1.5rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: '#6366F1', fontWeight: '600' }}>
                                        <i className="fa-solid fa-robot"></i> Dynamic Questioning
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: '#10B981', fontWeight: '600' }}>
                                        <i className="fa-solid fa-bolt"></i> Real-time Extraction
                                    </div>
                                </div>
                            </div>

                            {/* Card 2: Batch Upload with Preview Illustration */}
                            <div className="module-card" style={{ padding: '2.5rem 2rem', background: 'transparent', borderRadius: '0', border: 'none', borderTop: '1px solid #E5E7EB' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <div className="module-icon-wrapper indigo-glow" style={{ width: '45px', height: '45px', borderRadius: '14px' }}>
                                            <i className="fa-solid fa-user-plus"></i>
                                        </div>
                                        <div>
                                            <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#111827', margin: 0 }}>Candidate List</h3>
                                            <p style={{ color: '#6B7280', fontSize: '0.9rem', margin: '0.2rem 0 0' }}>Upload your recipient list here.</p>
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                        <span style={{ fontSize: '0.75rem', background: '#F1F5F9', padding: '0.3rem 0.6rem', borderRadius: '8px', color: '#64748B', fontWeight: '600' }}>.CSV</span>
                                        <span style={{ fontSize: '0.75rem', background: '#F1F5F9', padding: '0.3rem 0.6rem', borderRadius: '8px', color: '#64748B', fontWeight: '600' }}>.XLSX</span>
                                    </div>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 200px', gap: '2rem' }}>
                                    <div
                                        onDrop={handleDrop}
                                        onDragOver={handleDragOver}
                                        onClick={() => document.getElementById('candidateList').click()}
                                        style={{
                                            height: '220px', border: '2px dashed #CBD5E1', borderRadius: '24px',
                                            background: '#F8FAFC', cursor: 'pointer', display: 'flex', flexDirection: 'column',
                                            alignItems: 'center', justifyContent: 'center', padding: '2rem', transition: 'all 0.3s'
                                        }}
                                        onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#6366F1'; e.currentTarget.style.background = '#EEF2FF'; }}
                                        onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#CBD5E1'; e.currentTarget.style.background = '#F8FAFC'; }}
                                    >
                                        <input type="file" id="candidateList" onChange={handleFileChange} accept=".csv,.xls,.xlsx" style={{ display: 'none' }} />

                                        {!file ? (
                                            <>
                                                <div style={{
                                                    width: '56px', height: '56px', background: 'white', color: '#6366F1',
                                                    borderRadius: '16px', display: 'flex', alignItems: 'center',
                                                    justifyContent: 'center', marginBottom: '1.5rem', fontSize: '1.5rem',
                                                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05)'
                                                }}>
                                                    <i className="fa-solid fa-file-upload"></i>
                                                </div>
                                                <p style={{ fontSize: '1.1rem', fontWeight: '800', color: '#1E293B', marginBottom: '0.5rem' }}>Select List</p>
                                                <p style={{ fontSize: '0.85rem', color: '#94A3B8', textAlign: 'center' }}>Drag & Drop file here</p>
                                            </>
                                        ) : (
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{ width: '64px', height: '64px', background: '#10B981', color: 'white', borderRadius: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem', fontSize: '1.75rem', boxShadow: '0 10px 15px -3px rgba(16, 185, 129, 0.2)' }}>
                                                    <i className="fa-solid fa-file-circle-check"></i>
                                                </div>
                                                <p style={{ fontSize: '1.1rem', fontWeight: '800', color: '#111827', marginBottom: '0.5rem' }}>{file.name}</p>
                                                <p style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '1.5rem' }}>{(file.size / 1024).toFixed(1)} KB • Ready</p>
                                                <button type="button" onClick={(e) => { e.stopPropagation(); removeFile(); }} style={{ color: '#EF4444', background: '#FEF2F2', border: '1px solid #FEE2E2', padding: '0.6rem 1.5rem', borderRadius: '12px', fontSize: '0.85rem', cursor: 'pointer', fontWeight: '700', transition: 'all 0.2s' }}>Replace File</button>
                                            </div>
                                        )}
                                    </div>

                                    {/* CSV Format Tutorial Guide */}
                                    <div style={{ background: '#F1F5F9', borderRadius: '24px', padding: '1.5rem', border: '1px solid #E2E8F0' }}>
                                        <h4 style={{ fontSize: '0.75rem', fontWeight: '800', color: '#475569', marginBottom: '1rem', textTransform: 'uppercase' }}>Sample Format</h4>
                                        <div style={{ background: 'white', padding: '0.75rem', borderRadius: '12px', fontSize: '0.7rem', fontFamily: 'monospace', color: '#64748B', border: '1px solid #E2E8F0' }}>
                                            <div style={{ fontWeight: '700', color: '#111827', borderBottom: '1px solid #F1F5F9', paddingBottom: '0.3rem', marginBottom: '0.3rem' }}>name, email</div>
                                            <div>John Doe, john@...</div>
                                            <div>Jane Doe, jane@...</div>
                                        </div>
                                        <p style={{ fontSize: '0.7rem', color: '#94A3B8', marginTop: '1rem', lineHeight: '1.4' }}>
                                            Ensure column headers are <b>name</b> and <b>email</b>.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Section 3: Final Deployment Visuals */}
                            <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem' }}>
                                {error && (
                                    <div style={{ width: '100%', padding: '1.25rem', background: '#FEF2F2', color: '#B91C1C', borderRadius: '20px', border: '1px solid #FECACA', display: 'flex', alignItems: 'center', gap: '1rem', fontWeight: '600' }}>
                                        <i className="fa-solid fa-triangle-exclamation" style={{ fontSize: '1.2rem' }}></i> {error}
                                    </div>
                                )}

                                {/* Date & Time Selection Range */}
                                <div className="module-card" style={{ width: '100%', padding: '2.5rem 2rem', background: 'transparent', borderRadius: '0', border: 'none', borderTop: '1px solid #E5E7EB' }}>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                            <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '-0.3rem', display: 'block' }}>
                                                <i className="fa-regular fa-calendar-check" style={{ marginRight: '0.4rem', color: '#6366F1' }}></i>
                                                Available From
                                            </label>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <input
                                                    type="date"
                                                    value={fromDate}
                                                    onChange={(e) => setFromDate(e.target.value)}
                                                    style={{ flex: 1.5, padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC', fontSize: '0.9rem' }}
                                                />
                                                <input
                                                    type="time"
                                                    value={fromTime}
                                                    onChange={(e) => setFromTime(e.target.value)}
                                                    style={{ flex: 1, padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC', fontSize: '0.9rem' }}
                                                />
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                            <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '-0.3rem', display: 'block' }}>
                                                <i className="fa-regular fa-calendar-xmark" style={{ marginRight: '0.4rem', color: '#EF4444' }}></i>
                                                Available Until
                                            </label>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <input
                                                    type="date"
                                                    value={untilDate}
                                                    onChange={(e) => setUntilDate(e.target.value)}
                                                    style={{ flex: 1.5, padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC', fontSize: '0.9rem' }}
                                                />
                                                <input
                                                    type="time"
                                                    value={untilTime}
                                                    onChange={(e) => setUntilTime(e.target.value)}
                                                    style={{ flex: 1, padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC', fontSize: '0.9rem' }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <button type="submit" className="primary-link-btn" disabled={isUploading} style={{
                                    width: '100%', padding: '1.25rem', fontSize: '1.2rem', borderRadius: '24px', background: '#4F46E5',
                                    boxShadow: '0 15px 30px -5px rgba(79, 70, 229, 0.4)', transition: 'all 0.3s transform'
                                }} onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
                                    {isUploading ? (
                                        <><i className="fa-solid fa-atom fa-spin" style={{ marginRight: '1rem' }}></i> Deploying Interview Agents...</>
                                    ) : (
                                        <><i className="fa-solid fa-rocket" style={{ marginRight: '1rem' }}></i> Build and Send Invites</>
                                    )}
                                </button>

                                <div style={{ display: 'flex', gap: '3rem', borderTop: '1px solid #E2E8F0', paddingTop: '2.5rem', width: '100%', justifyContent: 'center' }}>
                                    {[
                                        { icon: 'fa-user-shield', title: 'Secure Proctored', text: 'Anti-cheat active' },
                                        { icon: 'fa-brain', title: 'Adaptive AI', text: 'Tailored questions' },
                                        { icon: 'fa-bolt', title: 'Instant Delivery', text: 'Email & WhatsApp' }
                                    ].map((feat, i) => (
                                        <div key={i} style={{ textAlign: 'center' }}>
                                            <div style={{ color: '#6366F1', fontSize: '1.5rem', marginBottom: '0.5rem' }}>
                                                <i className={`fa-solid ${feat.icon}`}></i>
                                            </div>
                                            <div style={{ fontSize: '0.85rem', fontWeight: '800', color: '#1E293B' }}>{feat.title}</div>
                                            <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>{feat.text}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AiInterview;
