import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

const ResultsAI = () => {
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'resume');

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [toast, setToast] = useState(null);
    const [deletingIds, setDeletingIds] = useState(new Set());
    const [confirmDelete, setConfirmDelete] = useState(null); // { items: [...] }
    const [selected, setSelected] = useState(new Set()); // Set of _deleteKey strings

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
        setSelected(new Set());
        try {
            const candidatesResp = await axios.get(`${API_BASE_URL}/ai-candidates/`);
            const allCandidates = candidatesResp.data || [];
            setAiInterviews(allCandidates.filter(c => c.total_questions > 0));
            setResumeResults(allCandidates);

            const resultsResp = await axios.get(`${API_BASE_URL}/results/`);
            const allResults = resultsResp.data?.results || [];
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
        setSelected(new Set());
    };

    const getStatusStyle = (rawStatus) => {
        const s = rawStatus?.toLowerCase();
        if (s === 'selected' || s === 'resume passed') return { background: '#E6FBF5', color: '#05CD99' };
        if (s === 'rejected' || s === 'resume failed') return { background: '#FFF5F5', color: '#EE5D50' };
        if (s === 'completed' || s === 'hired') return { background: '#E6FBF5', color: '#05CD99' };
        return { background: '#F4F7FE', color: '#A3AED0' };
    };

    const getStatusLabel = (rawStatus) => {
        const map = {
            'Resume Passed': 'Pass ✓',
            'Resume Failed': 'Fail ✗',
            'selected': 'Qualified ✓',
            'rejected': 'Not Qualified',
            'Completed': 'Completed',
            'Hired': 'Hired',
            'New': 'Pending',
            'Invited': 'Invited',
            'Interview': 'Interviewing',
        };
        return map[rawStatus] || rawStatus;
    };

    /* ---- Selection ---- */
    const currentRows = activeTab === 'resume'
        ? resumeResults.map(r => ({ ...r, _type: 'candidate', _deleteKey: `resume-${r.id}` }))
        : activeTab === 'assessment'
            ? aiAssessments.map(r => ({ ...r, _type: 'ai_assessment', _deleteKey: r.submission_id }))
            : aiInterviews.map(r => ({ ...r, _type: 'candidate', _deleteKey: `interview-${r.id}` }));

    const allKeys = currentRows.map(r => r._deleteKey);
    const allSelected = allKeys.length > 0 && allKeys.every(k => selected.has(k));
    const someSelected = allKeys.some(k => selected.has(k));

    const toggleSelectAll = () => {
        if (allSelected) {
            setSelected(prev => { const s = new Set(prev); allKeys.forEach(k => s.delete(k)); return s; });
        } else {
            setSelected(prev => { const s = new Set(prev); allKeys.forEach(k => s.add(k)); return s; });
        }
    };

    const toggleSelect = (key) => {
        setSelected(prev => {
            const s = new Set(prev);
            s.has(key) ? s.delete(key) : s.add(key);
            return s;
        });
    };

    /* ---- Delete ---- */
    const requestDelete = (items) => setConfirmDelete({ items });
    const cancelDelete = () => setConfirmDelete(null);

    const performDelete = async (items) => {
        const ids = new Set(items.map(i => i._deleteKey));
        setDeletingIds(prev => new Set([...prev, ...ids]));

        let successCount = 0;
        let failCount = 0;

        await Promise.all(items.map(async (item) => {
            try {
                if (item._type === 'candidate') {
                    await axios.delete(`${API_BASE_URL}/ai-candidates/${item.id}/`);
                    successCount++;
                } else if (item._type === 'ai_assessment') {
                    const subId = item.submission_id.replace('ai_', '');
                    await axios.delete(`${API_BASE_URL}/ai-assessments/submission/${subId}/`);
                    successCount++;
                }
            } catch (err) {
                console.error('Delete failed for', item._deleteKey, err);
                failCount++;
            }
        }));

        // Remove from state
        const deletedCandidateIds = new Set(
            items.filter(i => i._type === 'candidate').map(i => i.id)
        );
        const deletedAssessmentKeys = new Set(
            items.filter(i => i._type === 'ai_assessment').map(i => i.submission_id)
        );

        setResumeResults(prev => prev.filter(r => !deletedCandidateIds.has(r.id)));
        setAiInterviews(prev => prev.filter(r => !deletedCandidateIds.has(r.id)));
        setAiAssessments(prev => prev.filter(r => !deletedAssessmentKeys.has(r.submission_id)));
        setSelected(prev => { const s = new Set(prev); ids.forEach(k => s.delete(k)); return s; });
        setDeletingIds(prev => { const s = new Set(prev); ids.forEach(k => s.delete(k)); return s; });

        if (successCount > 0 && failCount === 0) showToast('success', `${successCount} result${successCount > 1 ? 's' : ''} deleted.`);
        else if (failCount > 0) showToast('error', `${failCount} deletion(s) failed.`);
    };

    const confirmAndDelete = async () => {
        if (!confirmDelete) return;
        const items = confirmDelete.items;
        setConfirmDelete(null);
        await performDelete(items);
    };

    const selectedItems = currentRows.filter(r => selected.has(r._deleteKey));
    const selectedCount = selectedItems.length;

    /* ---- Styles ---- */
    const thStyle = { padding: '1rem 1.2rem', textAlign: 'left', color: '#6B7280', fontWeight: '700', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.04em', background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' };
    const tdStyle = { padding: '0.9rem 1.2rem', borderBottom: '1px solid #F3F4F6' };
    const checkboxStyle = { width: '16px', height: '16px', cursor: 'pointer', accentColor: '#4F46E5' };

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
                }}>
                    <i className={`fa-solid ${toast.type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}`} />
                    {toast.message}
                </div>
            )}

            {/* Confirm Modal */}
            {confirmDelete && (
                <div style={{
                    position: 'fixed', inset: 0, zIndex: 9999,
                    background: 'rgba(0,0,0,0.45)', backdropFilter: 'blur(4px)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                    <div style={{
                        background: 'white', borderRadius: '16px',
                        padding: '2rem 2.5rem', maxWidth: '420px', width: '90%',
                        boxShadow: '0 20px 60px rgba(0,0,0,0.15)', textAlign: 'center',
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>🗑️</div>
                        <h2 style={{ fontSize: '1.3rem', fontWeight: '800', color: '#111827', marginBottom: '0.5rem' }}>
                            Delete {confirmDelete.items.length > 1 ? `${confirmDelete.items.length} Results` : 'Result'}?
                        </h2>
                        <p style={{ color: '#6B7280', marginBottom: '1.5rem', lineHeight: '1.6' }}>
                            {confirmDelete.items.length === 1
                                ? <>This will permanently delete the result for <strong>{confirmDelete.items[0].full_name || confirmDelete.items[0].candidate?.name || 'this candidate'}</strong>.</>
                                : <>This will permanently delete <strong>{confirmDelete.items.length} selected results</strong>. This action cannot be undone.</>}
                        </p>
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                            <button onClick={cancelDelete} style={{ padding: '0.7rem 1.5rem', border: '1px solid #E5E7EB', borderRadius: '10px', background: 'white', cursor: 'pointer', fontWeight: '700', color: '#374151' }}>
                                Cancel
                            </button>
                            <button onClick={confirmAndDelete} style={{ padding: '0.7rem 1.5rem', border: 'none', borderRadius: '10px', background: '#EF4444', color: 'white', cursor: 'pointer', fontWeight: '700' }}>
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="dashboard-main" style={{ maxWidth: '1200px' }}>
                <header style={{ marginBottom: '2rem' }}>
                    <h1 style={{ fontSize: '2.4rem', fontWeight: '900', color: '#111827', margin: 0, letterSpacing: '-0.03em' }}>
                        AI <span style={{ color: '#4F46E5' }}>Results</span>
                    </h1>
                    <p style={{ color: '#6B7280', fontSize: '1rem', marginTop: '0.4rem', marginBottom: 0 }}>
                        Centralized analytics for all AI-powered selection processes.
                    </p>
                </header>

                {/* Tabs */}
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', background: '#F4F7FE', padding: '0.4rem', borderRadius: '12px', width: 'fit-content' }}>
                    {[
                        { id: 'resume', label: 'Resume Screening', icon: 'fa-file-magnifying-glass' },
                        { id: 'assessment', label: 'AI Assessments', icon: 'fa-brain' },
                        { id: 'interview', label: 'AI Interviews', icon: 'fa-microphone-lines' }
                    ].map(tab => (
                        <button key={tab.id} onClick={() => handleTabChange(tab.id)} style={{
                            background: activeTab === tab.id ? 'white' : 'transparent',
                            border: 'none', padding: '0.65rem 1.3rem', borderRadius: '10px',
                            fontWeight: '700', color: activeTab === tab.id ? '#4F46E5' : '#718096',
                            cursor: 'pointer', transition: 'all 0.2s',
                            display: 'flex', alignItems: 'center', gap: '0.5rem',
                            boxShadow: activeTab === tab.id ? '0 4px 10px rgba(0,0,0,0.05)' : 'none',
                        }}>
                            <i className={`fa-solid ${tab.icon}`} />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Bulk Action Toolbar */}
                <div style={{
                    height: selectedCount > 0 ? 'auto' : 0,
                    overflow: 'hidden',
                    transition: 'height 0.2s ease',
                    marginBottom: selectedCount > 0 ? '1rem' : 0,
                }}>
                    {selectedCount > 0 && (
                        <div style={{
                            display: 'flex', alignItems: 'center', gap: '1rem',
                            background: '#EEF2FF', border: '1px solid #C7D2FE',
                            borderRadius: '12px', padding: '0.75rem 1.2rem',
                        }}>
                            <span style={{ fontWeight: '700', color: '#4338CA', fontSize: '0.9rem' }}>
                                <i className="fa-solid fa-check-square" style={{ marginRight: '0.5rem' }} />
                                {selectedCount} selected
                            </span>
                            <button
                                onClick={() => requestDelete(selectedItems)}
                                style={{
                                    background: '#EF4444', color: 'white', border: 'none',
                                    borderRadius: '8px', padding: '0.45rem 1rem',
                                    fontWeight: '700', fontSize: '0.85rem', cursor: 'pointer',
                                    display: 'flex', alignItems: 'center', gap: '0.4rem',
                                }}
                            >
                                <i className="fa-solid fa-trash-can" /> Delete Selected
                            </button>
                            <button
                                onClick={() => setSelected(new Set())}
                                style={{
                                    background: 'transparent', color: '#6B7280', border: '1px solid #C7D2FE',
                                    borderRadius: '8px', padding: '0.45rem 0.9rem',
                                    fontWeight: '700', fontSize: '0.85rem', cursor: 'pointer',
                                }}
                            >
                                Clear Selection
                            </button>
                        </div>
                    )}
                </div>

                <div className="module-card" style={{ padding: '0', overflow: 'hidden', border: '1px solid #E5E7EB' }}>
                    {loading ? (
                        <div style={{ padding: '4rem', textAlign: 'center', color: '#6B7280' }}>
                            <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', display: 'block', marginBottom: '1rem' }} />
                            <p>Analyzing data...</p>
                        </div>
                    ) : error ? (
                        <div style={{ padding: '4rem', textAlign: 'center', color: '#EF4444' }}>
                            <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '2.5rem', display: 'block', marginBottom: '1rem' }} />
                            <p>{error}</p>
                            <button onClick={fetchData} style={{ marginTop: '1rem', padding: '0.5rem 1.5rem', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '700' }}>
                                Retry
                            </button>
                        </div>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr>
                                    {/* Select All checkbox */}
                                    <th style={{ ...thStyle, width: '48px', textAlign: 'center' }}>
                                        <input
                                            type="checkbox"
                                            style={checkboxStyle}
                                            checked={allSelected}
                                            ref={el => { if (el) el.indeterminate = someSelected && !allSelected; }}
                                            onChange={toggleSelectAll}
                                        />
                                    </th>
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
                                {currentRows.length === 0 && (
                                    <tr>
                                        <td colSpan="6" style={{ padding: '3rem', textAlign: 'center', color: '#9CA3AF' }}>
                                            No results found for this tab.
                                        </td>
                                    </tr>
                                )}

                                {/* RESUME TAB */}
                                {activeTab === 'resume' && currentRows.map((r) => {
                                    const isSelected = selected.has(r._deleteKey);
                                    const isDeleting = deletingIds.has(r._deleteKey);
                                    return (
                                        <tr key={r.id} style={{ background: isSelected ? '#F5F3FF' : 'white', transition: 'background 0.15s' }}>
                                            <td style={{ ...tdStyle, textAlign: 'center' }}>
                                                <input type="checkbox" style={checkboxStyle} checked={isSelected} onChange={() => toggleSelect(r._deleteKey)} />
                                            </td>
                                            <td style={tdStyle}>
                                                <div style={{ fontWeight: '700', color: '#111827' }}>{r.full_name}</div>
                                                <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>{r.email}</div>
                                            </td>
                                            <td style={tdStyle}>
                                                <div style={{ width: '44px', height: '44px', borderRadius: '50%', background: '#EEF2FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4F46E5', fontWeight: '800', fontSize: '0.78rem' }}>
                                                    {r.resume_score || 0}%
                                                </div>
                                            </td>
                                            <td style={{ ...tdStyle, color: '#6B7280', fontSize: '0.85rem' }}>
                                                {r.created_at ? new Date(r.created_at).toLocaleDateString() : '—'}
                                            </td>
                                            <td style={tdStyle}>
                                                <span style={{
                                                    padding: '0.3rem 0.75rem', borderRadius: '8px',
                                                    fontSize: '0.7rem', fontWeight: '800',
                                                    ...(r.resume_score >= 70
                                                        ? { background: '#E6FBF5', color: '#05CD99' }
                                                        : { background: '#FFF5F5', color: '#EE5D50' })
                                                }}>
                                                    {r.resume_score >= 70 ? 'Pass ✓' : 'Fail ✗'}
                                                </span>
                                            </td>
                                            <td style={{ ...tdStyle, textAlign: 'center' }}>
                                                <RowDeleteBtn item={r} isDeleting={isDeleting} onDelete={() => requestDelete([r])} />
                                            </td>
                                        </tr>
                                    );
                                })}

                                {/* ASSESSMENT TAB */}
                                {activeTab === 'assessment' && currentRows.map((r) => {
                                    const isSelected = selected.has(r._deleteKey);
                                    const isDeleting = deletingIds.has(r._deleteKey);
                                    return (
                                        <tr key={r.submission_id} style={{ background: isSelected ? '#F5F3FF' : 'white', transition: 'background 0.15s' }}>
                                            <td style={{ ...tdStyle, textAlign: 'center' }}>
                                                <input type="checkbox" style={checkboxStyle} checked={isSelected} onChange={() => toggleSelect(r._deleteKey)} />
                                            </td>
                                            <td style={tdStyle}>
                                                <div style={{ fontWeight: '700', color: '#111827' }}>{r.candidate?.name || 'Candidate'}</div>
                                                <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>{r.candidate?.email}</div>
                                            </td>
                                            <td style={tdStyle}>
                                                <div style={{ fontWeight: '600', color: '#374151', fontSize: '0.9rem' }}>{r.assessment?.display_name || r.assessment?.name}</div>
                                                <div style={{ fontSize: '0.78rem', color: '#6B7280' }}>Score: {r.score}/{r.total}</div>
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
                                                <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                                                    <button onClick={() => navigate(`/ai-assessments/${r.assessment?.id}?tab=submissions`)} style={{ padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid #E5E7EB', background: 'white', cursor: 'pointer', fontSize: '0.8rem', fontWeight: '700', color: '#374151' }}>
                                                        Details
                                                    </button>
                                                    <RowDeleteBtn item={r} isDeleting={isDeleting} onDelete={() => requestDelete([r])} />
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}

                                {/* INTERVIEW TAB */}
                                {activeTab === 'interview' && currentRows.map((r) => {
                                    const isSelected = selected.has(r._deleteKey);
                                    const isDeleting = deletingIds.has(r._deleteKey);
                                    return (
                                        <tr key={r.id} style={{ background: isSelected ? '#F5F3FF' : 'white', transition: 'background 0.15s' }}>
                                            <td style={{ ...tdStyle, textAlign: 'center' }}>
                                                <input type="checkbox" style={checkboxStyle} checked={isSelected} onChange={() => toggleSelect(r._deleteKey)} />
                                            </td>
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
                                                <span style={{ padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>{getStatusLabel(r.status)}</span>
                                            </td>
                                            <td style={{ ...tdStyle, textAlign: 'center' }}>
                                                <RowDeleteBtn item={r} isDeleting={isDeleting} onDelete={() => requestDelete([r])} />
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
};

/* Small inline delete button per row */
const RowDeleteBtn = ({ item, isDeleting, onDelete }) => (
    <button
        onClick={onDelete}
        disabled={isDeleting}
        title="Delete"
        style={{
            background: isDeleting ? '#FEE2E2' : '#FFF5F5',
            border: '1px solid #FECACA', color: '#EF4444',
            borderRadius: '8px', padding: '0.4rem 0.8rem',
            cursor: isDeleting ? 'not-allowed' : 'pointer',
            fontSize: '0.8rem', fontWeight: '700',
            display: 'inline-flex', alignItems: 'center', gap: '0.35rem',
            whiteSpace: 'nowrap',
        }}
    >
        <i className={isDeleting ? 'fa-solid fa-spinner fa-spin' : 'fa-solid fa-trash-can'} />
        {isDeleting ? '…' : 'Delete'}
    </button>
);

export default ResultsAI;
