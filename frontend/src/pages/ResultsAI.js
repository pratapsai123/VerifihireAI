import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import '../styles/Dashboard.css';
import '../styles/ResultsAI.css';

const ResultsAI = () => {
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'resume');
    const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'pass' | 'fail'

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [toast, setToast] = useState(null);
    const [deletingIds, setDeletingIds] = useState(new Set());
    const [confirmDelete, setConfirmDelete] = useState(null); // { items: [...] }
    const [selected, setSelected] = useState(new Set()); // Set of _deleteKey strings

    const [resumeResults, setResumeResults] = useState([]);
    const [aiAssessments, setAiAssessments] = useState([]);
    const [aiInterviews, setAiInterviews] = useState([]);
    const [summaryModal, setSummaryModal] = useState(null); // Candidate object

    const showToast = (type, message) => {
        setToast({ type, message });
        setTimeout(() => setToast(null), 3500);
    };

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        setSelected(new Set());
        try {
            // Fetch resume/interview candidates
            const candidatesResp = await axios.get(`${API_BASE_URL}/ai-candidates/`);
            const allCandidates = candidatesResp.data || [];
            setAiInterviews(allCandidates.filter(c => c.total_questions > 0));
            setResumeResults(allCandidates);

            // Fetch AI assessments and their submissions from the correct endpoint
            const aiAssessmentsResp = await axios.get(`${API_BASE_URL}/ai/`);
            const assessmentList = aiAssessmentsResp.data || [];

            // Fetch detail for each assessment to get its submissions, then flatten
            const detailPromises = assessmentList.map(a =>
                axios.get(`${API_BASE_URL}/ai/${a.id}/`).then(r => r.data).catch(() => ({ ...a, submissions: [] }))
            );
            const detailResults = await Promise.all(detailPromises);

            const allSubmissions = [];
            detailResults.forEach(assessment => {
                (assessment.submissions || []).forEach(sub => {
                    allSubmissions.push({
                        ...sub,
                        submission_id: `ai_${sub.id}`,
                        assessment: {
                            id: assessment.id,
                            name: assessment.required_skills,
                            display_name: assessment.required_skills,
                        },
                        candidate: {
                            name: sub.candidate_name,
                            email: sub.candidate_email,
                        },
                        score: sub.score,
                        total: assessment.mcq_count + assessment.coding_count,
                        percentage: sub.percentage,
                        status: sub.status,
                        submitted_at: sub.submitted_at,
                    });
                });
            });

            // Show only completed submissions, sorted newest first
            const sorted = allSubmissions
                .filter(s => s.submitted_at && s.status !== 'ONGOING')
                .sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at));
            setAiAssessments(sorted);
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
        setStatusFilter('all'); // Reset filter when switching tabs
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

    /* ---- Helpers to determine pass/fail for filtering ---- */
    const isPass = (r, type) => {
        if (type === 'resume') return r.status === 'Resume Passed' || (r.status !== 'Resume Failed' && r.resume_score > 0 && r.resume_score >= 70);
        if (type === 'assessment') return r.status === 'selected' || (r.percentage != null && r.percentage >= 50);
        if (type === 'interview') return r.status === 'Completed' || (r.score != null && r.total_questions > 0 && (r.score / (r.total_questions * 10)) >= 0.5);
        return false;
    };

    /* ---- Selection ---- */
    const allRows = activeTab === 'resume'
        ? resumeResults.map(r => ({ ...r, _type: 'candidate', _deleteKey: `resume-${r.id}` }))
        : activeTab === 'assessment'
            ? aiAssessments.map(r => ({ ...r, _type: 'ai_assessment', _deleteKey: r.submission_id }))
            : aiInterviews.map(r => ({ ...r, _type: 'candidate', _deleteKey: `interview-${r.id}` }));

    const currentRows = statusFilter === 'all'
        ? allRows
        : allRows.filter(r => {
            const pass = isPass(r, activeTab);
            return statusFilter === 'pass' ? pass : !pass;
        });

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
                    await axios.delete(`${API_BASE_URL}/ai/submission/${subId}/`);
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
    const checkboxStyle = { width: '16px', height: '16px', cursor: 'pointer', accentColor: '#4F46E5' };

    return (
        <div className="results-page">
            {/* Decorative Background Elements */}
            <div className="bg-shape shape-1"></div>
            <div className="bg-shape shape-2"></div>
            <div className="bg-shape shape-3"></div>

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
                <div className="glass-modal-overlay">
                    <div className="glass-modal-content" style={{
                        padding: '2.5rem', maxWidth: '420px', width: '90%', textAlign: 'center',
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>🗑️</div>
                        <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: '#111827', marginBottom: '0.5rem', letterSpacing: '-0.02em' }}>
                            Delete {confirmDelete.items.length > 1 ? `${confirmDelete.items.length} Results` : 'Result'}?
                        </h2>
                        <p style={{ color: '#475569', marginBottom: '1.75rem', lineHeight: '1.6', fontSize: '0.95rem' }}>
                            {confirmDelete.items.length === 1
                                ? <>This will permanently delete the result for <strong>{confirmDelete.items[0].full_name || confirmDelete.items[0].candidate?.name || 'this candidate'}</strong>.</>
                                : <>This will permanently delete <strong>{confirmDelete.items.length} selected results</strong>. This action cannot be undone.</>}
                        </p>
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                            <button onClick={cancelDelete} style={{ padding: '0.7rem 1.5rem', border: '1px solid #cbd5e1', borderRadius: '12px', background: 'rgba(255,255,255,0.7)', cursor: 'pointer', fontWeight: '700', color: '#334155' }}>
                                Cancel
                            </button>
                            <button onClick={confirmAndDelete} style={{ padding: '0.7rem 1.5rem', border: 'none', borderRadius: '12px', background: '#EF4444', color: 'white', cursor: 'pointer', fontWeight: '700', boxShadow: '0 4px 12px rgba(239, 68, 68, 0.25)' }}>
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* AI Interview Summary Modal */}
            {summaryModal && (
                <div className="glass-modal-overlay">
                    <div className="glass-modal-content" style={{
                        width: '100%', maxWidth: '800px', maxHeight: '85vh',
                        display: 'flex', flexDirection: 'column',
                    }}>
                        <div style={{
                            padding: '1.5rem 2rem',
                            borderBottom: '1px solid #F3F4F6',
                            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                            background: 'linear-gradient(to right, #F9FAFB, #FFFFFF)',
                        }}>
                            <div>
                                <h2 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#111827', margin: 0 }}>
                                    Interview Justification
                                </h2>
                                <p style={{ fontSize: '0.85rem', color: '#6B7280', margin: '0.2rem 0 0' }}>
                                    AI Evaluation for <strong>{summaryModal.full_name}</strong>
                                </p>
                            </div>
                            <button
                                onClick={() => setSummaryModal(null)}
                                style={{
                                    width: '36px', height: '36px', borderRadius: '50%',
                                    border: 'none', background: '#F3F4F6', color: '#4B5563',
                                    cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                }}
                            >
                                <i className="fa-solid fa-xmark" />
                            </button>
                        </div>

                        <div style={{ padding: '2rem', overflowY: 'auto', flex: 1 }}>
                            {(!summaryModal.interview_summary || summaryModal.interview_summary.length === 0) ? (
                                <div style={{ textAlign: 'center', padding: '3rem', color: '#9CA3AF' }}>
                                    <i className="fa-solid fa-comment-slash" style={{ fontSize: '3rem', display: 'block', marginBottom: '1rem', opacity: 0.5 }} />
                                    <p>No detailed feedback available for this candidate.</p>
                                </div>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                    {summaryModal.interview_summary.map((item, idx) => (
                                        <div key={idx} style={{
                                            border: '1px solid #E5E7EB',
                                            borderRadius: '16px',
                                            overflow: 'hidden',
                                        }}>
                                            <div style={{
                                                padding: '1rem 1.5rem',
                                                background: '#F9FAFB',
                                                borderBottom: '1px solid #E5E7EB',
                                                display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                                            }}>
                                                <span style={{ fontWeight: '800', fontSize: '0.75rem', color: '#4F46E5', textTransform: 'uppercase' }}>
                                                    Question {idx + 1}
                                                </span>
                                                <div style={{
                                                    background: item.score >= 7 ? '#DCFCE7' : item.score >= 4 ? '#FEF9C3' : '#FEE2E2',
                                                    color: item.score >= 7 ? '#166534' : item.score >= 4 ? '#854D0E' : '#991B1B',
                                                    padding: '0.25rem 0.75rem', borderRadius: '20px', fontSize: '0.75rem', fontWeight: '800'
                                                }}>
                                                    Score: {item.score}/10
                                                </div>
                                            </div>
                                            <div style={{ padding: '1.25rem 1.5rem' }}>
                                                <p style={{ fontWeight: '700', color: '#111827', fontSize: '0.95rem', marginBottom: '0.75rem' }}>
                                                    {item.question}
                                                </p>
                                                <div style={{ background: '#F3F4F6', padding: '0.8rem 1rem', borderRadius: '10px', fontSize: '0.9rem', color: '#4B5563', fontStyle: 'italic', marginBottom: '1rem' }}>
                                                    "{item.answer}"
                                                </div>
                                                <div style={{ display: 'flex', gap: '0.75rem' }}>
                                                    <i className="fa-solid fa-robot" style={{ color: '#4F46E5', marginTop: '0.2rem' }} />
                                                    <div style={{ fontSize: '0.9rem', color: '#374151', lineHeight: '1.6' }}>
                                                        <strong style={{ color: '#4F46E5' }}>AI Justification:</strong> {item.feedback}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div style={{ padding: '1.25rem 2rem', borderTop: '1px solid #F3F4F6', textAlign: 'right', background: '#F9FAFB' }}>
                            <button
                                onClick={() => setSummaryModal(null)}
                                style={{
                                    padding: '0.6rem 1.5rem', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '10px',
                                    fontWeight: '700', fontSize: '0.9rem', cursor: 'pointer', boxShadow: '0 4px 6px -1px rgba(79, 70, 229, 0.4)'
                                }}
                            >
                                Close Summary
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="dashboard-main" style={{ maxWidth: 'none', width: '100%', padding: '0 2rem 3rem' }}>
                <header style={{ marginBottom: '0.25rem', textAlign: 'center', paddingTop: '0' }}>
                    <h1 style={{ fontSize: '3.2rem', fontWeight: '900', color: '#111827', margin: 0, letterSpacing: '-0.04em', lineHeight: 1.1 }}>
                        AI <span style={{ color: '#4F46E5' }}>Results</span>
                    </h1>
                </header>

                {/* Tabs */}
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', background: '#F4F7FE', padding: '0.35rem', borderRadius: '12px', width: 'fit-content' }}>
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
                </div>

                {/* Filter Chips */}
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#9CA3AF', textTransform: 'uppercase', marginRight: '0.25rem' }}>Filter:</span>
                    {[{ key: 'all', label: 'All' }, { key: 'pass', label: 'Pass ✓' }, { key: 'fail', label: 'Fail ✗' }].map(f => (
                        <button key={f.key} onClick={() => setStatusFilter(f.key)} style={{
                            padding: '0.35rem 0.9rem', borderRadius: '20px', border: '1px solid',
                            fontSize: '0.78rem', fontWeight: '700', cursor: 'pointer', transition: 'all 0.15s',
                            borderColor: statusFilter === f.key
                                ? (f.key === 'pass' ? '#05CD99' : f.key === 'fail' ? '#EE5D50' : '#4F46E5')
                                : '#E5E7EB',
                            background: statusFilter === f.key
                                ? (f.key === 'pass' ? '#E6FBF5' : f.key === 'fail' ? '#FFF5F5' : '#EEF2FF')
                                : 'white',
                            color: statusFilter === f.key
                                ? (f.key === 'pass' ? '#05CD99' : f.key === 'fail' ? '#EE5D50' : '#4F46E5')
                                : '#6B7280',
                        }}>{f.label}</button>
                    ))}
                    <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: '#9CA3AF' }}>{currentRows.length} result{currentRows.length !== 1 ? 's' : ''}</span>
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

                <div className="glass-table-card">
                    {loading ? (
                        <div style={{ padding: '6rem 2rem', textAlign: 'center', color: '#64748b' }}>
                            <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2.5rem', display: 'block', marginBottom: '1.5rem', color: '#4f46e5' }} />
                            <p style={{ fontSize: '1.2rem', fontWeight: '600' }}>Gathering intel...</p>
                        </div>
                    ) : error ? (
                        <div style={{ padding: '5rem 2rem', textAlign: 'center', color: '#ef4444' }}>
                            <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '3rem', display: 'block', marginBottom: '1.5rem' }} />
                            <p style={{ fontSize: '1.1rem', fontWeight: '500' }}>{error}</p>
                            <button onClick={fetchData} style={{ marginTop: '1.5rem', padding: '0.75rem 2rem', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: '800', fontSize: '1rem', boxShadow: '0 4px 15px rgba(79, 70, 229, 0.3)' }}>
                                Retry Fetching
                            </button>
                        </div>
                    ) : (
                        <div style={{ overflowX: 'auto' }}>
                            <table className="results-table">
                                <thead>
                                    <tr>
                                        {/* Select All checkbox */}
                                        <th style={{ width: '60px', textAlign: 'center' }}>
                                            <input
                                                type="checkbox"
                                                style={checkboxStyle}
                                                checked={allSelected}
                                                ref={el => { if (el) el.indeterminate = someSelected && !allSelected; }}
                                                onChange={toggleSelectAll}
                                            />
                                        </th>
                                        <th>Candidate Info</th>
                                        {activeTab === 'resume' && <th>Match Score</th>}
                                        {activeTab === 'assessment' && <th>Assessment Data</th>}
                                        {activeTab === 'interview' && <th>Interview Score</th>}
                                        <th>Date</th>
                                        <th>AI Status</th>
                                        <th style={{ textAlign: 'center' }}>Action Matrix</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {currentRows.length === 0 && (
                                        <tr>
                                            <td colSpan="8" style={{ padding: '6rem 2rem', textAlign: 'center', color: '#64748b' }}>
                                                <i className="fa-solid fa-folder-open" style={{ fontSize: '3.5rem', display: 'block', marginBottom: '1.25rem', opacity: 0.3 }} />
                                                <span style={{ fontSize: '1.2rem', fontWeight: '600' }}>No candidates found in this category.</span>
                                            </td>
                                        </tr>
                                    )}

                                    {/* RESUME TAB */}
                                    {activeTab === 'resume' && currentRows.map((r) => {
                                        const isSelected = selected.has(r._deleteKey);
                                        const isDeleting = deletingIds.has(r._deleteKey);
                                        return (
                                            <tr className={`results-row ${isSelected ? 'selected' : ''}`} key={r.id}>
                                                <td style={{ textAlign: 'center' }}>
                                                    <input type="checkbox" style={checkboxStyle} checked={isSelected} onChange={() => toggleSelect(r._deleteKey)} />
                                                </td>
                                                <td>
                                                    <div style={{ fontWeight: '800', color: '#0f172a', fontSize: '1rem' }}>{r.full_name}</div>
                                                    <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '500' }}>{r.email}</div>
                                                </td>
                                                <td>
                                                    <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(238, 242, 255, 0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4f46e5', fontWeight: '900', fontSize: '0.85rem', boxShadow: 'inset 0 0 0 1px rgba(79, 70, 229, 0.1)' }}>
                                                        {r.resume_score || 0}%
                                                    </div>
                                                </td>
                                                <td style={{ color: '#475569', fontSize: '0.9rem', fontWeight: '500' }}>
                                                    {r.created_at ? new Date(r.created_at).toLocaleDateString() : '—'}
                                                </td>
                                                <td>
                                                    {(() => {
                                                        const isPassed = r.status === 'Resume Passed'
                                                            || (r.status !== 'Resume Failed' && r.resume_score > 0 && r.resume_score >= 70);
                                                        const isScored = r.status === 'Resume Passed' || r.status === 'Resume Failed' || r.resume_score > 0;
                                                        if (!isScored) return (
                                                            <span style={{ padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800', background: '#F4F7FE', color: '#A3AED0' }}>
                                                                Not Screened
                                                            </span>
                                                        );
                                                        return (
                                                            <span style={{
                                                                padding: '0.3rem 0.75rem', borderRadius: '8px',
                                                                fontSize: '0.7rem', fontWeight: '800',
                                                                ...(isPassed ? { background: '#E6FBF5', color: '#05CD99' } : { background: '#FFF5F5', color: '#EE5D50' })
                                                            }}>
                                                                {isPassed ? 'Pass ✓' : 'Fail ✗'}
                                                            </span>
                                                        );
                                                    })()}
                                                </td>

                                                <td style={{ textAlign: 'center' }}>
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
                                            <tr className={`results-row ${isSelected ? 'selected' : ''}`} key={r.submission_id}>
                                                <td style={{ textAlign: 'center' }}>
                                                    <input type="checkbox" style={checkboxStyle} checked={isSelected} onChange={() => toggleSelect(r._deleteKey)} />
                                                </td>
                                                <td>
                                                    <div style={{ fontWeight: '800', color: '#0f172a', fontSize: '1rem' }}>{r.candidate?.name || 'Candidate'}</div>
                                                    <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '500' }}>{r.candidate?.email}</div>
                                                </td>
                                                <td>
                                                    <div style={{ fontWeight: '800', color: '#334155', fontSize: '0.95rem', letterSpacing: '-0.01em' }}>{r.assessment?.display_name || r.assessment?.name}</div>
                                                    <div style={{ fontSize: '0.8rem', color: '#4f46e5', fontWeight: '700' }}>Score: {r.score}/{r.total}</div>
                                                </td>
                                                <td style={{ color: '#475569', fontSize: '0.9rem', fontWeight: '500' }}>
                                                    {r.submitted_at ? new Date(r.submitted_at).toLocaleDateString() : '—'}
                                                </td>
                                                <td>
                                                    <span style={{ padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>
                                                        {r.status === 'selected' ? 'QUALIFIED' : 'NOT QUALIFIED'}
                                                    </span>
                                                </td>
                                                <td style={{ textAlign: 'center' }}>
                                                    <div style={{ display: 'flex', gap: '0.6rem', justifyContent: 'center' }}>
                                                        <button onClick={() => navigate(`/ai-assessments/${r.assessment?.id}?tab=submissions`)} style={{
                                                            padding: '0.45rem 0.9rem', borderRadius: '10px',
                                                            border: '1px solid rgba(255,255,255,0.8)', background: 'rgba(255,255,255,0.6)',
                                                            cursor: 'pointer', fontSize: '0.85rem', fontWeight: '700', color: '#334155',
                                                            boxShadow: '0 2px 5px rgba(0,0,0,0.02)', backdropFilter: 'blur(5px)'
                                                        }}>
                                                            Review
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
                                            <tr className={`results-row ${isSelected ? 'selected' : ''}`} key={r.id}>
                                                <td style={{ textAlign: 'center' }}>
                                                    <input type="checkbox" style={checkboxStyle} checked={isSelected} onChange={() => toggleSelect(r._deleteKey)} />
                                                </td>
                                                <td>
                                                    <div style={{ fontWeight: '800', color: '#0f172a', fontSize: '1rem' }}>{r.full_name}</div>
                                                    <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '500' }}>{r.email}</div>
                                                </td>
                                                <td>
                                                    <div style={{ fontSize: '1.3rem', fontWeight: '900', color: '#4F46E5', letterSpacing: '-0.02em' }}>{r.score}</div>
                                                    <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>{r.total_questions} Qs</div>
                                                </td>
                                                <td style={{ color: '#475569', fontSize: '0.9rem', fontWeight: '500' }}>
                                                    {r.completed_at ? new Date(r.completed_at).toLocaleDateString() : 'In Progress'}
                                                </td>
                                                <td>
                                                    <span style={{ padding: '0.35rem 0.8rem', borderRadius: '10px', fontSize: '0.75rem', fontWeight: '800', ...getStatusStyle(r.status), border: `1px solid ${getStatusStyle(r.status).color}30` }}>
                                                        {getStatusLabel(r.status)}
                                                    </span>
                                                </td>
                                                <td style={{ textAlign: 'center' }}>
                                                    <div style={{ display: 'flex', gap: '0.6rem', justifyContent: 'center' }}>
                                                        <button
                                                            onClick={() => setSummaryModal(r)}
                                                            style={{
                                                                padding: '0.45rem 0.9rem', borderRadius: '10px',
                                                                border: '1px solid rgba(255,255,255,0.8)', background: 'rgba(255,255,255,0.6)',
                                                                cursor: 'pointer', fontSize: '0.85rem', fontWeight: '700', color: '#334155',
                                                                boxShadow: '0 2px 5px rgba(0,0,0,0.02)', backdropFilter: 'blur(5px)'
                                                            }}
                                                        >
                                                            Review
                                                        </button>
                                                        <RowDeleteBtn item={r} isDeleting={isDeleting} onDelete={() => requestDelete([r])} />
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

/* Small inline delete button per row */
const RowDeleteBtn = ({ item, isDeleting, onDelete }) => (
    <button
        className="delete-btn-glass"
        onClick={onDelete}
        disabled={isDeleting}
        title="Delete Record"
        style={{
            background: isDeleting ? '#FEE2E2' : 'rgba(254, 226, 226, 0.6)',
            border: '1px solid rgba(252, 165, 165, 0.8)',
            color: '#ef4444',
            borderRadius: '10px',
            padding: '0.45rem 0.9rem',
            cursor: isDeleting ? 'not-allowed' : 'pointer',
            fontSize: '0.85rem',
            fontWeight: '700',
            display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
            whiteSpace: 'nowrap',
            backdropFilter: 'blur(5px)',
            transition: 'all 0.2s cubic-bezier(0.19, 1, 0.22, 1)',
            boxShadow: '0 2px 5px rgba(239, 68, 68, 0.05)'
        }}
    >
        <i className={isDeleting ? 'fa-solid fa-spinner fa-spin' : 'fa-solid fa-trash-can'} />
        {isDeleting ? '…' : 'Delete'}
    </button>
);

export default ResultsAI;