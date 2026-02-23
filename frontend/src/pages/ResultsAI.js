import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

const ResultsAI = () => {
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const initialTab = searchParams.get('tab') || 'resume';
    const [activeTab, setActiveTab] = useState(initialTab);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [toast, setToast] = useState(null); // { type: 'success'|'error', message }
    const [deletingId, setDeletingId] = useState(null);
    const [confirmDelete, setConfirmDelete] = useState(null); // the item to confirm deletion

    const [resumeResults, setResumeResults] = useState([]);
    const [aiAssessments, setAiAssessments] = useState([]);
    const [aiInterviews, setAiInterviews] = useState([]);

    const showToast = (type, message) => {
        setToast({ type, message });
        setTimeout(() => setToast(null), 3500);
    };

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const candidatesResp = await axios.get(`${API_BASE_URL}/ai-candidates/`);
            const allCandidates = candidatesResp.data || [];

            setAiInterviews(allCandidates.filter(c => c.total_questions > 0));
            setResumeResults(allCandidates);

            const resultsResp = await axios.get(`${API_BASE_URL}/results/`);
            const allResults = resultsResp.data?.results || [];
            // Only assessment-type results (submission_id starts with 'ai_')
            setAiAssessments(allResults.filter(r => r.submission_id?.startsWith('ai_')));

        } catch (err) {
            console.error('Error fetching AI results:', err);
            setError('Failed to load results. Please ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    useEffect(() => {
        const tab = searchParams.get('tab');
        if (tab && tab !== activeTab) setActiveTab(tab);
    }, [searchParams, activeTab]);

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        setSearchParams({ tab });
    };

    const getStatusStyle = (status) => {
        const s = status?.toLowerCase();
        if (s === 'selected' || s === 'completed' || s === 'resume passed')
            return { background: '#E6FBF5', color: '#05CD99' };
        if (s === 'rejected' || s === 'resume failed')
            return { background: '#FFF5F5', color: '#EE5D50' };
        return { background: '#F4F7FE', color: '#A3AED0' };
    };

    const requestDelete = (item) => setConfirmDelete(item);
    const cancelDelete = () => setConfirmDelete(null);

    const confirmAndDelete = async () => {
        if (!confirmDelete) return;
        const item = confirmDelete;
        setConfirmDelete(null);
        setDeletingId(item._deleteKey);

        try {
            if (item._type === 'candidate') {
                await axios.delete(`${API_BASE_URL}/ai-candidates/${item.id}/`);
                setResumeResults(prev => prev.filter(r => r.id !== item.id));
                setAiInterviews(prev => prev.filter(r => r.id !== item.id));
            } else if (item._type === 'ai_assessment') {
                const subId = item.submission_id.replace('ai_', '');
                await axios.delete(`${API_BASE_URL}/ai-assessments/submission/${subId}/`);
                setAiAssessments(prev => prev.filter(r => r.submission_id !== item.submission_id));
            }
            showToast('success', 'Result deleted successfully.');
        } catch (err) {
            console.error('Delete failed:', err);
            showToast('error', 'Failed to delete. Please try again.');
        } finally {
            setDeletingId(null);
        }
    };

    const DeleteBtn = ({ item }) => {
        const isLoading = deletingId === item._deleteKey;
        return (
            <button
                onClick={() => requestDelete(item)}
                disabled={isLoading}
                title="Delete result"
                style={{
                    background: isLoading ? '#FEE2E2' : '#FFF5F5',
                    border: '1px solid #FECACA',
                    color: '#EF4444',
                    borderRadius: '8px',
                    padding: '0.4rem 0.8rem',
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    fontSize: '0.8rem',
                    fontWeight: '700',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    transition: 'all 0.2s',
                    whiteSpace: 'nowrap',
                }}
                onMouseEnter={e => { if (!isLoading) e.currentTarget.style.background = '#FEE2E2'; }}
                onMouseLeave={e => { if (!isLoading) e.currentTarget.style.background = '#FFF5F5'; }}
            >
                <i className={isLoading ? 'fa-solid fa-spinner fa-spin' : 'fa-solid fa-trash-can'} />
                {isLoading ? 'Deleting…' : 'Delete'}
            </button>
        );
    };

    const thStyle = { padding: '1rem 1.5rem', textAlign: 'left', color: '#6B7280', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase' };
    const tdStyle = { padding: '1rem 1.5rem' };

    return (
        <div className="dashboard-container">
            {/* Toast */}
            {toast && (
                <div style={{
                    position: 'fixed', top: '1.5rem', right: '1.5rem', zIndex: 9999,
                    background: toast.type === 'success' ? '#ECFDF5' : '#FFF5F5',
                    border: `1px solid ${toast.type === 'success' ? '#6EE7B7' : '#FECACA'}`,
                    color: toast.type === 'success' ? '#065F46' : '#B91C1C',
                    padding: '0.9rem 1.4rem', borderRadius: '12px',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                    display: 'flex', alignItems: 'center', gap: '0.6rem', fontWeight: '600',
                    animation: 'fadeIn 0.2s ease',
                }}>
                    <i className={`fa-solid ${toast.type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}`} />
                    {toast.message}
                </div>
            )}

            {/* Confirm Deletion Modal */}
            {confirmDelete && (
                <div style={{
                    position: 'fixed', inset: 0, zIndex: 9999,
                    background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                    <div style={{
                        background: 'white', borderRadius: '16px',
                        padding: '2rem 2.5rem', maxWidth: '420px', width: '90%',
                        boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
                        textAlign: 'center',
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🗑️</div>
                        <h2 style={{ fontSize: '1.3rem', fontWeight: '800', color: '#111827', marginBottom: '0.5rem' }}>
                            Delete Result?
                        </h2>
                        <p style={{ color: '#6B7280', marginBottom: '1.5rem', lineHeight: '1.6' }}>
                            This will permanently delete the result for <strong>{confirmDelete.full_name || confirmDelete.candidate?.name || 'this candidate'}</strong>. This action cannot be undone.
                        </p>
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                            <button onClick={cancelDelete} style={{
                                padding: '0.7rem 1.5rem', border: '1px solid #E5E7EB',
                                borderRadius: '10px', background: 'white', cursor: 'pointer',
                                fontWeight: '700', color: '#374151',
                            }}>
                                Cancel
                            </button>
                            <button onClick={confirmAndDelete} style={{
                                padding: '0.7rem 1.5rem', border: 'none',
                                borderRadius: '10px', background: '#EF4444', color: 'white',
                                cursor: 'pointer', fontWeight: '700',
                            }}>
                                Yes, Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="dashboard-main" style={{ maxWidth: '1200px' }}>
                <header style={{ marginBottom: '2.5rem' }}>
                    <h1 style={{ fontSize: '2.4rem', fontWeight: '900', color: '#111827', margin: 0, letterSpacing: '-0.03em' }}>
                        AI <span style={{ color: '#4F46E5' }}>Results</span>
                    </h1>
                    <p style={{ color: '#6B7280', fontSize: '1rem', marginTop: '0.5rem' }}>
                        Centralized analytics for all AI-powered selection processes.
                    </p>
                </header>

                {/* Tabs */}
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', background: '#F4F7FE', padding: '0.4rem', borderRadius: '12px', width: 'fit-content' }}>
                    {[
                        { id: 'resume', label: 'Resume Screening', icon: 'fa-file-magnifying-glass' },
                        { id: 'assessment', label: 'AI Assessments', icon: 'fa-brain' },
                        { id: 'interview', label: 'AI Interviews', icon: 'fa-microphone-lines' }
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => handleTabChange(tab.id)}
                            style={{
                                background: activeTab === tab.id ? 'white' : 'transparent',
                                border: 'none', padding: '0.75rem 1.5rem', borderRadius: '10px',
                                fontWeight: '700', color: activeTab === tab.id ? '#4F46E5' : '#718096',
                                cursor: 'pointer', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '0.6rem',
                                boxShadow: activeTab === tab.id ? '0 4px 10px rgba(0, 0, 0, 0.05)' : 'none'
                            }}
                        >
                            <i className={`fa-solid ${tab.icon}`} />
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div className="module-card" style={{ padding: '0', overflow: 'hidden', border: '1px solid #E5E7EB' }}>
                    {loading ? (
                        <div style={{ padding: '4rem', textAlign: 'center', color: '#6B7280' }}>
                            <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', marginBottom: '1rem' }} />
                            <p>Analyzing data...</p>
                        </div>
                    ) : error ? (
                        <div style={{ padding: '4rem', textAlign: 'center', color: '#EF4444' }}>
                            <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '2.5rem', marginBottom: '1rem' }} />
                            <p>{error}</p>
                            <button onClick={fetchData} style={{ marginTop: '1rem', padding: '0.5rem 1.5rem', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>Retry</button>
                        </div>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>
                                    <th style={thStyle}>Candidate</th>
                                    {activeTab === 'resume' && <th style={thStyle}>Match %</th>}
                                    {activeTab === 'assessment' && <th style={thStyle}>Assessment</th>}
                                    {activeTab === 'interview' && <th style={thStyle}>AI Score</th>}
                                    <th style={thStyle}>Date</th>
                                    <th style={thStyle}>Status</th>
                                    <th style={{ ...thStyle, textAlign: 'center' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {/* ---- RESUME TAB ---- */}
                                {activeTab === 'resume' && (resumeResults.length > 0 ? resumeResults.map((r) => (
                                    <tr key={r.id} style={{ borderBottom: '1px solid #F3F4F6' }}>
                                        <td style={tdStyle}>
                                            <div style={{ fontWeight: '700', color: '#111827' }}>{r.full_name}</div>
                                            <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>{r.email}</div>
                                        </td>
                                        <td style={tdStyle}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#EEF2FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4F46E5', fontWeight: '800', fontSize: '0.8rem' }}>
                                                    {r.score || 0}%
                                                </div>
                                            </div>
                                        </td>
                                        <td style={{ ...tdStyle, color: '#6B7280', fontSize: '0.85rem' }}>
                                            {r.created_at ? new Date(r.created_at).toLocaleDateString() : '—'}
                                        </td>
                                        <td style={tdStyle}>
                                            <span style={{ padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>
                                                {r.status}
                                            </span>
                                        </td>
                                        <td style={{ ...tdStyle, textAlign: 'center' }}>
                                            <DeleteBtn item={{ ...r, _type: 'candidate', _deleteKey: `resume-${r.id}` }} />
                                        </td>
                                    </tr>
                                )) : (
                                    <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: '#9CA3AF' }}>No resume screening results found.</td></tr>
                                ))}

                                {/* ---- ASSESSMENT TAB ---- */}
                                {activeTab === 'assessment' && (aiAssessments.length > 0 ? aiAssessments.map((r) => (
                                    <tr key={r.submission_id} style={{ borderBottom: '1px solid #F3F4F6' }}>
                                        <td style={tdStyle}>
                                            <div style={{ fontWeight: '700', color: '#111827' }}>{r.candidate?.name || 'Candidate'}</div>
                                            <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>{r.candidate?.email}</div>
                                        </td>
                                        <td style={tdStyle}>
                                            <div style={{ fontWeight: '600', color: '#374151', fontSize: '0.9rem' }}>{r.assessment?.display_name || r.assessment?.name}</div>
                                            <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>Score: {r.score}/{r.total}</div>
                                        </td>
                                        <td style={{ ...tdStyle, color: '#6B7280', fontSize: '0.85rem' }}>
                                            {r.submitted_at ? new Date(r.submitted_at).toLocaleDateString() : '—'}
                                        </td>
                                        <td style={tdStyle}>
                                            <span style={{ padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>
                                                {r.status === 'selected' ? 'QUALIFIED' : 'NOT QUALIFIED'}
                                            </span>
                                        </td>
                                        <td style={{ ...tdStyle, textAlign: 'center' }}>
                                            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                                                <button
                                                    className="action-btn"
                                                    style={{ width: 'fit-content' }}
                                                    onClick={() => navigate(`/ai-assessments/${r.assessment?.id}?tab=submissions`)}
                                                >
                                                    Details
                                                </button>
                                                <DeleteBtn item={{ ...r, _type: 'ai_assessment', _deleteKey: r.submission_id }} />
                                            </div>
                                        </td>
                                    </tr>
                                )) : (
                                    <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: '#9CA3AF' }}>No AI assessment attempts found.</td></tr>
                                ))}

                                {/* ---- INTERVIEW TAB ---- */}
                                {activeTab === 'interview' && (aiInterviews.length > 0 ? aiInterviews.map((r) => (
                                    <tr key={r.id} style={{ borderBottom: '1px solid #F3F4F6' }}>
                                        <td style={tdStyle}>
                                            <div style={{ fontWeight: '700', color: '#111827' }}>{r.full_name}</div>
                                            <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>{r.email}</div>
                                        </td>
                                        <td style={tdStyle}>
                                            <div style={{ fontSize: '1.2rem', fontWeight: '900', color: '#4F46E5' }}>{r.score}</div>
                                            <div style={{ fontSize: '0.7rem', color: '#A3AED0', fontWeight: '700' }}>{r.total_questions} Questions</div>
                                        </td>
                                        <td style={{ ...tdStyle, color: '#6B7280', fontSize: '0.85rem' }}>
                                            {r.completed_at ? new Date(r.completed_at).toLocaleDateString() : 'In Progress'}
                                        </td>
                                        <td style={tdStyle}>
                                            <span style={{ padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>
                                                {r.status}
                                            </span>
                                        </td>
                                        <td style={{ ...tdStyle, textAlign: 'center' }}>
                                            <DeleteBtn item={{ ...r, _type: 'candidate', _deleteKey: `interview-${r.id}` }} />
                                        </td>
                                    </tr>
                                )) : (
                                    <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: '#9CA3AF' }}>No AI interview sessions found.</td></tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ResultsAI;
