import React, { useState } from 'react';
import axios from 'axios';
import '../styles/Dashboard.css';
import '../styles/AiInterviewCreation.css';
import { API_BASE_URL } from '../apiConfig';

const AiInterview = () => {
    const [jobDescription, setJobDescription] = useState('');
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const [highlightField, setHighlightField] = useState(null); // Field to highlight with orange border
    const [fromDate, setFromDate] = useState('');
    const [fromTime, setFromTime] = useState('');
    const [untilDate, setUntilDate] = useState('');
    const [untilTime, setUntilTime] = useState('');
    const [customRoleTitle, setCustomRoleTitle] = useState('');
    const [experienceLevel, setExperienceLevel] = useState('');
    const [interviewPassThreshold, setInterviewPassThreshold] = useState(50);
    const [interviewDuration, setInterviewDuration] = useState(60); // minutes


    // Job Roles State
    const [jobRoles, setJobRoles] = useState([]);
    const [selectedRoleId, setSelectedRoleId] = useState('');

    React.useEffect(() => {
        const fetchRoles = async () => {
            try {
                const res = await axios.get(`${API_BASE_URL}/job-roles/`);
                setJobRoles(res.data);
            } catch (err) {
                console.error("Error fetching job roles:", err);
            }
        };
        fetchRoles();
    }, []);

    const validateFile = (file) => {
        const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        const validExtensions = ['.csv', '.xls', '.xlsx'];
        const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
        
        if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
            setError('Please upload a valid CSV or Excel file (.csv, .xls, .xlsx)');
            return false;
        }
        return true;
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            if (validateFile(selectedFile)) {
                setFile(selectedFile);
            }
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFile = e.dataTransfer.files[0];
            if (validateFile(droppedFile)) {
                setFile(droppedFile);
            }
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const removeFile = () => {
        setFile(null);
    };

    const downloadTemplate = () => {
        const headers = "name,email\n";
        const blob = new Blob([headers], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", "ai_interview_template.csv");
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setHighlightField(null);

        if (!file) {
            setError('Please upload a Candidate List (CSV/Excel).');
            setHighlightField('field-candidate-list');
            document.getElementById('field-candidate-list')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        if (!jobDescription || jobDescription.trim().length < 50) {
            setError('Please provide a detailed Job Description (at least 50 characters) for the AI to generate meaningful interview questions.');
            setHighlightField('field-job-description');
            document.getElementById('field-job-description')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        if (selectedRoleId === 'custom') {
            if (!customRoleTitle || !customRoleTitle.trim()) {
                setError('Please enter a custom role title.');
                setHighlightField('field-role-title');
                document.getElementById('field-role-title')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }
            if (customRoleTitle.trim().length < 3) {
                setError('Custom role title must be at least 3 characters long.');
                setHighlightField('field-role-title');
                document.getElementById('field-role-title')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }
        }

        if (!experienceLevel) {
            setError('Please select an Experience Level.');
            setHighlightField('field-experience-level');
            document.getElementById('field-experience-level')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        // Mandatory Scheduling Validation
        if (!fromDate || !fromTime) {
            setError('Please provide a complete starting Date and Time for the interviews.');
            setHighlightField('field-availability');
            document.getElementById('field-availability')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }
        if (!untilDate || !untilTime) {
            setError('Please provide a complete ending Date and Time for the interviews.');
            setHighlightField('field-availability');
            document.getElementById('field-availability')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        setIsUploading(true);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('job_description', jobDescription);

        // Include Job Title for persistence
        if (selectedRoleId === 'custom') {
            formData.append('role_title', customRoleTitle);
        } else {
            const role = jobRoles.find(r => r.id.toString() === selectedRoleId);
            if (role) formData.append('role_title', role.title);
        }

        if (fromDate && fromTime) {
            formData.append('available_from', new Date(`${fromDate}T${fromTime}`).toISOString());
        }
        if (untilDate && untilTime) {
            formData.append('available_until', new Date(`${untilDate}T${untilTime}`).toISOString());
        }

        if (experienceLevel) {
            formData.append('experience_level', experienceLevel);
        }
        formData.append('interview_pass_threshold', interviewPassThreshold);
        formData.append('interview_duration_minutes', interviewDuration);


        try {
            const response = await axios.post(`${API_BASE_URL}/ai-candidates/bulk-invite/`, formData, {
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
        <div className="ai-creation-page">
            <div className="mesh-bg"></div>
            <div className="bg-shape" style={{ width: '600px', height: '600px', background: 'rgba(99, 102, 241, 0.15)', top: '-10%', right: '-5%' }}></div>
            <div className="bg-shape" style={{ width: '500px', height: '500px', background: 'rgba(168, 85, 247, 0.15)', bottom: '-10%', left: '-5%', animationDelay: '-5s' }}></div>

            <div className="creation-container" style={{ paddingTop: '1rem', marginTop: 0 }}>
                <header className="page-header" style={{ marginBottom: '1.5rem', marginTop: 0 }}>
                    <h1>AI <span style={{ color: '#6366F1' }}>Interview</span> Creation</h1>
                    <p>
                        Design high-fidelity AI interview experiences by providing job context and candidate lists for automated deployment.
                    </p>
                </header>

                <div className="form-stack">
                    {result ? (
                        <div className="glass-card" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
                            <div className="module-icon-wrapper teal-glow" style={{ margin: '0 auto 2rem', width: '80px', height: '80px', borderRadius: '24px' }}>
                                <i className="fa-solid fa-check-double" style={{ fontSize: '2rem' }}></i>
                            </div>
                            <h2 style={{ fontSize: '2rem', fontWeight: '800', color: '#111827', marginBottom: '1rem' }}>Interviews Deployed!</h2>
                            <p style={{ color: '#64748B', fontSize: '1.1rem', marginBottom: '3rem', maxWidth: '500px', margin: '0 auto 3rem' }}>
                                Invitations have been sent. Your AI Interviewers are now waiting for candidate responses.
                            </p>

                            <div style={{
                                background: 'rgba(248, 250, 252, 0.5)', padding: '2rem', borderRadius: '24px',
                                marginBottom: '3rem', textAlign: 'left', border: '1px solid rgba(226, 232, 240, 0.6)'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                    <h4 style={{ fontSize: '0.9rem', color: '#1E293B', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Generated Session {result.candidates.length === 1 ? 'Link' : 'Links'}</h4>
                                    <span style={{ fontSize: '0.8rem', color: '#64748B', background: '#E2E8F0', padding: '0.3rem 0.8rem', borderRadius: '8px' }}>{result.candidates.length} Candidate{result.candidates.length !== 1 ? 's' : ''}</span>
                                </div>

                                {result.candidates.map((c, index) => (
                                    <div key={index} style={{
                                        background: 'white', padding: '1.25rem', borderRadius: '16px', marginBottom: '0.75rem',
                                        border: '1px solid #E5E7EB', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                        transition: 'all 0.2s', cursor: 'default'
                                    }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                            <div style={{ width: '40px', height: '40px', background: '#F1F5F9', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569', fontWeight: '700' }}>
                                                {c.name.charAt(0)}
                                            </div>
                                            <div>
                                                <div style={{ color: '#0F172A', fontWeight: '700', fontSize: '1rem' }}>{c.name}</div>
                                                <div style={{ color: '#64748B', fontSize: '0.85rem' }}>{c.email}</div>
                                            </div>
                                        </div>
                                        <div style={{
                                            color: '#6366f1', fontWeight: '700', fontSize: '0.85rem', textDecoration: 'none',
                                            padding: '0.6rem 1.25rem', background: '#EEF2FF', borderRadius: '12px',
                                            transition: 'all 0.2s', opacity: 0.7
                                        }}>
                                            Invite Sent
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <button onClick={() => window.location.reload()} className="deploy-btn" style={{ maxWidth: '400px', margin: '0 auto' }}>
                                <i className="fa-solid fa-plus-circle"></i> Setup New Interviews
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="form-stack">

                            {/* Card 1: JD Section with Rich Visuals */}
                            <div id="field-job-description" className="module-card" style={{ padding: '2.5rem 2rem', background: 'transparent', borderRadius: '0', border: 'none', borderTop: '1px solid #E5E7EB' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <div className="module-icon-wrapper indigo-glow" style={{ width: '45px', height: '45px', borderRadius: '14px' }}>
                                            <i className="fa-solid fa-file-signature"></i>
                                        </div>
                                        <div>
                                            <h3 style={{ fontSize: '1.1rem', fontWeight: '500', color: '#111827', margin: 0 }}>Job Requirements</h3>
                                            <p style={{ color: '#6B7280', fontSize: '0.9rem', margin: '0.2rem 0 0' }}>Provide the context for the AI interviewer.</p>
                                        </div>
                                    </div>
                                    <div className="info-banner" style={{ padding: '0.5rem 1rem' }}>
                                        <i className="fa-solid fa-circle-check"></i> Intelligence Active
                                    </div>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    <select
                                        className="modern-input"
                                        style={{ width: '100%', padding: '0.85rem', borderRadius: '12px', border: '1px solid #E2E8F0', outline: 'none', background: 'white' }}
                                        value={selectedRoleId}
                                        onChange={(e) => {
                                            const roleId = e.target.value;
                                            setSelectedRoleId(roleId);
                                            const role = jobRoles.find(r => r.id.toString() === roleId);
                                            if (role) {
                                                setJobDescription(role.description);
                                            } else {
                                                setJobDescription('');
                                            }
                                        }}
                                    >
                                        <option value="">-- Select a Saved Role --</option>
                                        {jobRoles.map(r => (
                                            <option key={r.id} value={r.id}>{r.title}</option>
                                        ))}
                                        <option value="custom">Custom (Type Manually)</option>
                                    </select>

                                    {selectedRoleId && (
                                        <div id="field-role-title" className="input-group" style={{ marginTop: '1rem' }}>
                                            <label className="input-label">Role Title</label>
                                            <input
                                                type="text"
                                                value={selectedRoleId === 'custom' ? customRoleTitle : (jobRoles.find(r => r.id.toString() === selectedRoleId)?.title || '')}
                                                onChange={(e) => { if (selectedRoleId === 'custom') { setCustomRoleTitle(e.target.value); if (highlightField === 'field-role-title') setHighlightField(null); } }}
                                                readOnly={selectedRoleId !== 'custom'}
                                                placeholder="e.g. Senior Frontend Developer"
                                                className="modern-input"
                                                style={selectedRoleId !== 'custom' ? { background: '#f8fafc', cursor: 'default' } : (highlightField === 'field-role-title' ? { border: '2px solid #f97316', boxShadow: '0 0 0 3px rgba(249,115,22,0.15)' } : {})}
                                            />
                                        </div>
                                    )}

                                    {selectedRoleId && (
                                        <textarea
                                            value={jobDescription}
                                            onChange={(e) => { setJobDescription(e.target.value); if (highlightField === 'field-job-description') setHighlightField(null); }}
                                            placeholder="Detailed Job Description. AI will use this to dynamically generate probing questions."
                                            className="modern-textarea"
                                            style={{ marginTop: '1rem', minHeight: '150px', ...(highlightField === 'field-job-description' ? { border: '2px solid #f97316', boxShadow: '0 0 0 3px rgba(249,115,22,0.15)' } : {}) }}
                                            required
                                        />
                                    )}

                                    {selectedRoleId && (
                                        <div id="field-experience-level" className="input-group" style={{ marginTop: '1rem' }}>
                                            <label className="input-label">
                                                <i className="fa-solid fa-layer-group" style={{ marginRight: '0.4rem', color: '#6366F1' }}></i>
                                                Experience Level
                                            </label>
                                            <select
                                                className="modern-input"
                                                style={{ width: '100%', padding: '0.85rem', borderRadius: '12px', border: highlightField === 'field-experience-level' ? '2px solid #f97316' : '1px solid #E2E8F0', outline: 'none', background: 'white', boxShadow: highlightField === 'field-experience-level' ? '0 0 0 3px rgba(249,115,22,0.15)' : 'none' }}
                                                value={experienceLevel}
                                                onChange={(e) => { setExperienceLevel(e.target.value); if (highlightField === 'field-experience-level') setHighlightField(null); }}
                                            >
                                                <option value="">-- Select Experience Level --</option>
                                                <option value="fresher">Fresher (0 Years)</option>
                                                <option value="1-2">1-2 Years</option>
                                                <option value="3-5">3-5 Years</option>
                                                <option value="5+">5+ Years</option>
                                            </select>
                                        </div>
                                    )}
                                </div>

                                <div style={{ marginTop: '1.25rem', display: 'flex', gap: '1.5rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: '#6366F1', fontWeight: '600' }}>
                                        <i className="fa-solid fa-robot"></i> Dynamic Questioning
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: '#10B981', fontWeight: '600' }}>
                                        <i className="fa-solid fa-bolt"></i> Real-time Extraction
                                    </div>
                                </div>
                            </div>

                            <div id="field-candidate-list" className="glass-card">
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <div className="module-icon-wrapper indigo-glow" style={{ width: '45px', height: '45px', borderRadius: '14px' }}>
                                            <i className="fa-solid fa-user-plus"></i>
                                        </div>
                                        <div>
                                            <h3 style={{ fontSize: '1.1rem', fontWeight: '500', color: '#111827', margin: 0 }}>Candidate List</h3>
                                            <p style={{ color: '#6B7280', fontSize: '0.9rem', margin: '0.2rem 0 0' }}>Upload your recipient list here.</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="grid-2">
                                    <div
                                        onDrop={(e) => { handleDrop(e); if (highlightField === 'field-candidate-list') setHighlightField(null); }}
                                        onDragOver={handleDragOver}
                                        onClick={() => document.getElementById('candidateList').click()}
                                        className="upload-zone"
                                        style={highlightField === 'field-candidate-list' ? { border: '2px solid #f97316', boxShadow: '0 0 0 3px rgba(249,115,22,0.15)' } : {}}
                                    >
                                        <input type="file" id="candidateList" onChange={(e) => { handleFileChange(e); if (highlightField === 'field-candidate-list') setHighlightField(null); }} accept=".csv,.xls,.xlsx" style={{ display: 'none' }} />

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
                                                <p style={{ fontSize: '1rem', fontWeight: '500', color: '#1E293B', marginBottom: '0.5rem' }}>Select List</p>
                                                <p style={{ fontSize: '0.85rem', color: '#94A3B8' }}>Drag & Drop file here</p>
                                            </>
                                        ) : (
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{ width: '64px', height: '64px', background: '#10B981', color: 'white', borderRadius: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem', fontSize: '1.75rem', boxShadow: '0 10px 15px -3px rgba(16, 185, 129, 0.2)' }}>
                                                    <i className="fa-solid fa-file-circle-check"></i>
                                                </div>
                                                <p style={{ fontSize: '1.1rem', fontWeight: '800', color: '#111827', marginBottom: '0.5rem' }}>{file.name}</p>
                                                <p style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '1.5rem' }}>{(file.size / 1024).toFixed(1)} KB • Ready</p>
                                                <button type="button" onClick={(e) => { e.stopPropagation(); removeFile(); }} style={{ color: '#EF4444', background: '#FEF2F2', border: '1px solid #FEE2E2', padding: '0.6rem 1.5rem', borderRadius: '12px', fontSize: '0.85rem', cursor: 'pointer', fontWeight: '700' }}>Replace File</button>
                                            </div>
                                        )}
                                    </div>

                                    <div style={{ background: 'rgba(241, 245, 249, 0.5)', borderRadius: '24px', padding: '1.5rem', border: '1px solid rgba(226, 232, 240, 0.6)' }}>
                                        <h4 style={{ fontSize: '0.75rem', fontWeight: '600', color: '#475569', marginBottom: '1rem', textTransform: 'uppercase' }}>Sample Format</h4>
                                        <div style={{ background: 'white', padding: '1rem', borderRadius: '12px', fontSize: '0.75rem', fontFamily: 'monospace', color: '#64748B', border: '1px solid #E2E8F0' }}>
                                            <div style={{ fontWeight: '500', color: '#111827', borderBottom: '1px solid #F1F5F9', paddingBottom: '0.3rem', marginBottom: '0.3rem' }}>name, email</div>
                                            <div>John Doe, john@example.com</div>
                                            <div>Jane Smith, jane@example.com</div>
                                        </div>
                                        <p style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '1rem', lineHeight: '1.5' }}>
                                            Ensure column headers are <b>name</b> and <b>email</b>.
                                        </p>
                                        <button 
                                            type="button" 
                                            onClick={downloadTemplate} 
                                            style={{ marginTop: '1rem', background: 'white', color: '#6366f1', border: '1px solid #cbd5e1', padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.75rem', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', transition: 'all 0.2s', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}
                                            onMouseOver={(e) => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.background = '#f8fafc'; }}
                                            onMouseOut={(e) => { e.currentTarget.style.borderColor = '#cbd5e1'; e.currentTarget.style.background = 'white'; }}
                                        >
                                            <i className="fa-solid fa-download"></i> Download Template
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div id="field-availability" className="glass-card">
                                <div className="grid-2">
                                    <div className="input-group">
                                        <label className="input-label">
                                            <i className="fa-regular fa-calendar-check" style={{ marginRight: '0.4rem', color: '#6366F1' }}></i>
                                            Available From
                                        </label>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <input
                                                type="date"
                                                min={new Date().toISOString().split('T')[0]}
                                                value={fromDate}
                                                onChange={(e) => {
                                                    setFromDate(e.target.value);
                                                    if (highlightField === 'field-availability') setHighlightField(null);
                                                    // Clear untilDate if it's now before the new fromDate
                                                    if (untilDate && e.target.value && untilDate < e.target.value) {
                                                        setUntilDate('');
                                                        setUntilTime('');
                                                    }
                                                }}
                                                onClick={(e) => e.target.showPicker && e.target.showPicker()}
                                                style={{ flex: 1.5, padding: '0.85rem', border: highlightField === 'field-availability' && !fromDate ? '2px solid #f97316' : '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: 'white', fontSize: '0.9rem', cursor: 'pointer', boxShadow: highlightField === 'field-availability' && !fromDate ? '0 0 0 3px rgba(249,115,22,0.15)' : 'none' }}
                                            />
                                            <input
                                                type="time"
                                                value={fromTime}
                                                onChange={(e) => {
                                                    const newTime = e.target.value;
                                                    // If from date is today, don't allow past time
                                                    const today = new Date().toISOString().split('T')[0];
                                                    if (fromDate === today && newTime) {
                                                        const now = new Date();
                                                        const [h, m] = newTime.split(':').map(Number);
                                                        if (h < now.getHours() || (h === now.getHours() && m < now.getMinutes())) {
                                                            alert('Cannot select a time in the past.');
                                                            return;
                                                        }
                                                    }
                                                    setFromTime(newTime);
                                                    if (highlightField === 'field-availability') setHighlightField(null);
                                                    // Clear until time if it's now invalid (same date, until < from)
                                                    if (untilDate && fromDate && untilDate === fromDate && untilTime && newTime && untilTime <= newTime) {
                                                        setUntilTime('');
                                                    }
                                                }}
                                                onClick={(e) => e.target.showPicker && e.target.showPicker()}
                                                style={{ flex: 1, padding: '0.85rem', border: highlightField === 'field-availability' && !fromTime ? '2px solid #f97316' : '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: 'white', fontSize: '0.9rem', cursor: 'pointer', boxShadow: highlightField === 'field-availability' && !fromTime ? '0 0 0 3px rgba(249,115,22,0.15)' : 'none' }}
                                            />
                                        </div>
                                    </div>
                                    <div className="input-group">
                                        <label className="input-label">
                                            <i className="fa-regular fa-calendar-xmark" style={{ marginRight: '0.4rem', color: '#EF4444' }}></i>
                                            Available Until
                                        </label>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <input
                                                type="date"
                                                min={fromDate || new Date().toISOString().split('T')[0]}
                                                value={untilDate}
                                                onChange={(e) => { setUntilDate(e.target.value); if (highlightField === 'field-availability') setHighlightField(null); }}
                                                onClick={(e) => e.target.showPicker && e.target.showPicker()}
                                                style={{ flex: 1.5, padding: '0.85rem', border: highlightField === 'field-availability' && !untilDate ? '2px solid #f97316' : '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: 'white', fontSize: '0.9rem', cursor: 'pointer', boxShadow: highlightField === 'field-availability' && !untilDate ? '0 0 0 3px rgba(249,115,22,0.15)' : 'none' }}
                                            />
                                            <input
                                                type="time"
                                                value={untilTime}
                                                onChange={(e) => {
                                                    const newTime = e.target.value;
                                                    // If same date, ensure until time is after from time
                                                    if (untilDate && fromDate && untilDate === fromDate && fromTime && newTime) {
                                                        if (newTime <= fromTime) {
                                                            alert('Until time must be after From time when dates are the same.');
                                                            return;
                                                        }
                                                    }
                                                    setUntilTime(newTime);
                                                    if (highlightField === 'field-availability') setHighlightField(null);
                                                }}
                                                onClick={(e) => e.target.showPicker && e.target.showPicker()}
                                                style={{ flex: 1, padding: '0.85rem', border: highlightField === 'field-availability' && !untilTime ? '2px solid #f97316' : '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: 'white', fontSize: '0.9rem', cursor: 'pointer', boxShadow: highlightField === 'field-availability' && !untilTime ? '0 0 0 3px rgba(249,115,22,0.15)' : 'none' }}
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Card 4: Threshold Settings */}
                            <div className="glass-card">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                                    <div className="module-icon-wrapper indigo-glow" style={{ width: '45px', height: '45px', borderRadius: '14px' }}>
                                        <i className="fa-solid fa-sliders"></i>
                                    </div>
                                    <div>
                                        <h3 style={{ fontSize: '1.1rem', fontWeight: '500', color: '#111827', margin: 0 }}>Interview Settings</h3>
                                        <p style={{ color: '#6B7280', fontSize: '0.9rem', margin: '0.2rem 0 0' }}>Configure passing benchmarks.</p>
                                    </div>
                                </div>

                                <div className="input-group" style={{ marginBottom: 0 }}>
                                    <label className="input-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <span>AI Interview Pass Threshold</span>
                                        <span style={{ color: '#6366F1', fontWeight: '700' }}>{interviewPassThreshold}%</span>
                                    </label>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginTop: '0.5rem' }}>
                                        <input
                                            type="range"
                                            min="0"
                                            max="100"
                                            value={interviewPassThreshold}
                                            onChange={(e) => setInterviewPassThreshold(parseInt(e.target.value))}
                                            style={{ flex: 1, accentColor: '#6366F1', height: '6px', cursor: 'pointer' }}
                                        />
                                    </div>
                                    <p style={{ color: '#94A3B8', fontSize: '0.75rem', marginTop: '0.75rem' }}>
                                        Candidates scoring below this in the AI interview will be automatically rejected.
                                    </p>
                                </div>

                                <div className="input-group" style={{ marginTop: '1.5rem', marginBottom: 0 }}>
                                    <label className="input-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <span>Interview Duration</span>
                                        <span style={{ color: '#6366F1', fontWeight: '700' }}>{interviewDuration} min</span>
                                    </label>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginTop: '0.5rem' }}>
                                        <input
                                            type="range"
                                            min="15"
                                            max="120"
                                            step="5"
                                            value={interviewDuration}
                                            onChange={(e) => setInterviewDuration(parseInt(e.target.value))}
                                            style={{ flex: 1, accentColor: '#6366F1', height: '6px', cursor: 'pointer' }}
                                        />
                                    </div>
                                    <p style={{ color: '#94A3B8', fontSize: '0.75rem', marginTop: '0.75rem' }}>
                                        Maximum time allowed for the candidate to complete the interview.
                                    </p>
                                </div>
                            </div>


                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem' }}>
                                {error && (
                                    <div className="info-banner" style={{ width: '100%', background: '#FEF2F2', color: '#B91C1C', borderColor: '#FECACA' }}>
                                        <i className="fa-solid fa-triangle-exclamation"></i> {error}
                                    </div>
                                )}



                                <button type="submit" className="generate-btn" disabled={isUploading}>
                                    {isUploading ? (
                                        <><i className="fa-solid fa-atom fa-spin"></i> Deploying Interview Agents...</>
                                    ) : (
                                        <><i className="fa-solid fa-rocket"></i> Build and Send Invites</>
                                    )}
                                </button>


                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AiInterview;
