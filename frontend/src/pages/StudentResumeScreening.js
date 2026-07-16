import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, FileText, Briefcase, Zap, Loader2 } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

const CREDITS_PER_RESUME = 3;

const StudentResumeScreening = () => {
    const navigate = useNavigate();
    const [files, setFiles] = useState([]);
    const [jobTitle, setJobTitle] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [threshold, setThreshold] = useState(70);
    const [experienceLevel, setExperienceLevel] = useState('fresher');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [screeningResult, setScreeningResult] = useState(null);
    const [batchId, setBatchId] = useState(null);
    const [showConfirm, setShowConfirm] = useState(false);
    const [availableCredits, setAvailableCredits] = useState(0);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);

    const creditCost = files.length * CREDITS_PER_RESUME;

    useEffect(() => {
        const fetchCredits = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get(`${API_BASE_URL}/students/wallet/`, { headers: { Authorization: `Bearer ${token}` } });
                setAvailableCredits(res.data.ai_credits || 0);
            } catch (e) {}
        };
        fetchCredits();
    }, []);

    const handleFileChange = (e) => {
        if (e.target.files) {
            setFiles(Array.from(e.target.files));
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragActive(false);
        if (e.dataTransfer.files) {
            setFiles(Array.from(e.dataTransfer.files));
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError(null);
        if (files.length === 0) { setError('Please upload at least one resume.'); return; }
        if (!jobDescription || jobDescription.length < 50) { setError('Job description must be at least 50 characters.'); return; }
        if (!experienceLevel) { setError('Please select an experience level.'); return; }
        if (availableCredits < creditCost) { setError(`Insufficient credits. You need ${creditCost} credits but have ${availableCredits}.`); return; }
        setShowConfirm(true);
    };

    const proceedWithScreening = async () => {
        setShowConfirm(false);
        setLoading(true);
        setProcessing(true);
        setError(null);
        setScreeningResult(null);

        const formData = new FormData();
        files.forEach(f => formData.append('resume', f));
        formData.append('job_description', jobDescription);
        formData.append('threshold', threshold);
        formData.append('experience_level', experienceLevel);
        if (jobTitle) formData.append('role_title', jobTitle);
        formData.append('is_fully_automatic', 'false');

        try {
            const res = await axios.post(`${API_BASE_URL}/ai-candidates/match/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const resBatchId = res.data?.batch_id;
            setBatchId(resBatchId);
            setLoading(false);

            // Poll for results
            if (resBatchId) {
                const pollInterval = setInterval(async () => {
                    try {
                        const token = localStorage.getItem('token');
                        const pollRes = await axios.get(`${API_BASE_URL}/ai-candidates/batch-progress/${resBatchId}/`, {
                            headers: { Authorization: `Bearer ${token}` }
                        });
                        if (pollRes.data?.is_complete) {
                            clearInterval(pollInterval);
                            setProcessing(false);
                            // Fetch the actual result from resume-results
                            const resultRes = await axios.get(`${API_BASE_URL}/ai-candidates/resume-results/`, {
                                headers: { Authorization: `Bearer ${token}` }
                            });
                            const allResults = resultRes.data?.results || [];
                            // Show the latest result
                            if (allResults.length > 0) {
                                setScreeningResult(allResults[0]);
                            }
                        }
                    } catch (e) {}
                }, 3000);
                // Safety timeout after 2 minutes
                setTimeout(() => {
                    clearInterval(pollInterval);
                    if (processing) {
                        setProcessing(false);
                        setError('Screening is taking longer than expected. Check results page later.');
                    }
                }, 120000);
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to process resumes.');
            setLoading(false);
            setProcessing(false);
        }
    };

    return (
        <div style={{ minHeight: '100vh', background: '#f8fafc', position: 'relative' }}>
            <div style={{ position: 'fixed', inset: 0, background: 'radial-gradient(ellipse at 20% 0%, rgba(99,102,241,0.06) 0%, transparent 50%)', pointerEvents: 'none', zIndex: 0 }}></div>
            <div style={{ position: 'relative', zIndex: 1, maxWidth: '700px', margin: '0 auto', padding: '2rem 1.5rem 4rem' }}>

                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                    <button onClick={() => navigate('/dashboard')} style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', width: '42px', height: '42px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#6366f1' }}>
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800, color: '#0f172a' }}>Resume Screening</h1>
                        <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: '#64748b' }}>See how well your resume matches a job description</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} style={{ background: 'white', borderRadius: '20px', padding: '2rem', border: '1px solid #e2e8f0', boxShadow: '0 2px 12px rgba(0,0,0,0.03)' }}>

                        {/* Job Title */}
                        <div style={{ marginBottom: '1.25rem' }}>
                            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.5rem' }}>Job Title</label>
                            <input type="text" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} placeholder="e.g. Software Engineer" style={{ width: '100%', padding: '0.85rem', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box' }} />
                        </div>

                        {/* Job Description */}
                        <div style={{ marginBottom: '1.25rem' }}>
                            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.5rem' }}>Job Description *</label>
                            <textarea value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} placeholder="Paste the full job description here..." required style={{ width: '100%', minHeight: '120px', padding: '0.85rem', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '0.9rem', outline: 'none', resize: 'vertical', boxSizing: 'border-box' }} />
                        </div>

                        {/* Experience Level */}
                        <div style={{ marginBottom: '1.25rem' }}>
                            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.5rem' }}>Experience Level</label>
                            <select value={experienceLevel} onChange={(e) => setExperienceLevel(e.target.value)} style={{ width: '100%', padding: '0.85rem', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box' }}>
                                <option value="fresher">Fresher</option>
                                <option value="1-2">1-2 Years</option>
                                <option value="3-5">3-5 Years</option>
                                <option value="5+">5+ Years</option>
                            </select>
                        </div>

                        {/* Resume Upload */}
                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '0.5rem' }}>Upload Resume(s) *</label>
                            <div
                                onDrop={handleDrop}
                                onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                                onDragLeave={() => setDragActive(false)}
                                onClick={() => fileInputRef.current?.click()}
                                style={{ border: `2px dashed ${dragActive ? '#6366f1' : '#e2e8f0'}`, borderRadius: '14px', padding: '2rem', textAlign: 'center', cursor: 'pointer', background: dragActive ? '#eef2ff' : '#fafafa', transition: 'all 0.2s' }}
                            >
                                <input ref={fileInputRef} type="file" accept=".pdf" multiple onChange={handleFileChange} style={{ display: 'none' }} />
                                {files.length > 0 ? (
                                    <div>
                                        <FileText size={28} style={{ color: '#6366f1', marginBottom: '0.5rem' }} />
                                        <p style={{ margin: 0, fontWeight: 600, color: '#1e293b' }}>{files.length} file(s) selected</p>
                                        <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: '#64748b' }}>{files.map(f => f.name).join(', ')}</p>
                                    </div>
                                ) : (
                                    <div>
                                        <Upload size={28} style={{ color: '#94a3b8', marginBottom: '0.5rem' }} />
                                        <p style={{ margin: 0, fontWeight: 600, color: '#64748b' }}>Click or drag PDF files here</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        {error && <div style={{ padding: '0.75rem 1rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', color: '#dc2626', fontSize: '0.85rem', marginBottom: '1rem' }}>{error}</div>}

                        <button type="submit" disabled={loading} style={{ width: '100%', padding: '1rem', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', border: 'none', borderRadius: '14px', fontSize: '1rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px rgba(99,102,241,0.3)' }}>
                            {loading ? <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Screening...</> : 'Screen Resume'}
                        </button>

                        {files.length > 0 && (
                            <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', color: '#6366f1', fontSize: '0.85rem', fontWeight: 600 }}>
                                <Zap size={16} />
                                <span>This will use <strong>{creditCost} credits</strong></span>
                                <span style={{ color: '#94a3b8', fontWeight: 400 }}>({availableCredits} available)</span>
                            </div>
                        )}
                </form>

                {/* Processing State */}
                {processing && (
                    <div style={{ marginTop: '1.5rem', background: 'white', borderRadius: '20px', padding: '2.5rem', border: '1px solid #e2e8f0', textAlign: 'center' }}>
                        <Loader2 size={36} style={{ color: '#6366f1', animation: 'spin 1s linear infinite', margin: '0 auto' }} />
                        <p style={{ marginTop: '1rem', color: '#6366f1', fontWeight: 600, fontSize: '1rem' }}>Screening your resume...</p>
                        <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>This usually takes 15-30 seconds</p>
                    </div>
                )}

                {/* Screening Result */}
                {screeningResult && !processing && (
                    <div style={{ marginTop: '1.5rem', background: 'white', borderRadius: '20px', padding: '2rem', border: '1px solid #e2e8f0' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700, color: '#1e293b' }}>Your Results</h2>
                            <span style={{
                                fontSize: '1.5rem', fontWeight: 900, padding: '6px 16px', borderRadius: '12px',
                                background: (screeningResult.match_percentage || 0) >= 70 ? '#dcfce7' : (screeningResult.match_percentage || 0) >= 50 ? '#fef3c7' : '#fee2e2',
                                color: (screeningResult.match_percentage || 0) >= 70 ? '#166534' : (screeningResult.match_percentage || 0) >= 50 ? '#92400e' : '#991b1b',
                            }}>
                                {screeningResult.match_percentage || 0}%
                            </span>
                        </div>

                        {screeningResult.summary && (
                            <div style={{ padding: '1.25rem', background: '#f8fafc', borderRadius: '14px', border: '1px solid #e2e8f0' }}>
                                <p style={{ margin: 0, fontSize: '0.88rem', color: '#374151', lineHeight: '1.7', whiteSpace: 'pre-wrap' }}>{screeningResult.summary}</p>
                            </div>
                        )}

                        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
                            <button onClick={() => { setScreeningResult(null); setFiles([]); }} style={{ flex: 1, padding: '0.85rem', borderRadius: '12px', border: '1px solid #e2e8f0', background: 'white', color: '#6366f1', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer' }}>Screen Another</button>
                            <button onClick={() => navigate('/student/results?tab=resume')} style={{ flex: 1, padding: '0.85rem', borderRadius: '12px', border: 'none', background: '#6366f1', color: 'white', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer' }}>View All Results</button>
                        </div>
                    </div>
                )}

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
                                    This will use <strong style={{ color: '#6366f1' }}>{creditCost} credits</strong> from your wallet.
                                </p>
                                <p style={{ margin: '0.25rem 0 0', color: '#94a3b8', fontSize: '0.8rem' }}>
                                    Remaining after: {availableCredits - creditCost} credits
                                </p>
                            </div>
                            <div style={{ display: 'flex', gap: '0.75rem' }}>
                                <button onClick={() => setShowConfirm(false)} style={{ flex: 1, padding: '0.85rem', borderRadius: '12px', border: '1px solid #e2e8f0', background: 'white', color: '#475569', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer' }}>Cancel</button>
                                <button onClick={proceedWithScreening} style={{ flex: 1, padding: '0.85rem', borderRadius: '12px', border: 'none', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px rgba(99,102,241,0.3)' }}>Proceed</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default StudentResumeScreening;
