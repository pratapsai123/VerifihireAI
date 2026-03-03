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
    const [currentPage, setCurrentPage] = useState(1);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [toast, setToast] = useState(null);
    const [deletingIds, setDeletingIds] = useState(new Set());
    const [confirmDelete, setConfirmDelete] = useState(null); // { items: [...] }
    const [selected, setSelected] = useState(new Set()); // Set of _deleteKey strings

    const [resumeResults, setResumeResults] = useState([]);
    const [aiAssessments, setAiAssessments] = useState([]);
    const [aiInterviews, setAiInterviews] = useState([]);
    const [groupedData, setGroupedData] = useState({}); // { roleName: { resume: [], assessment: [], interview: [] } }
    const [viewMode, setViewMode] = useState('overview'); // 'overview' | 'detail'
    const [selectedRole, setSelectedRole] = useState(null);
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
            const [candidatesResp, aiResp, rolesResp] = await Promise.all([
                axios.get(`${API_BASE_URL}/ai-candidates/`),
                axios.get(`${API_BASE_URL}/ai/`),
                axios.get(`${API_BASE_URL}/job-roles/`)
            ]);

            const rolesList = rolesResp.data || [];
            const validRoleTitles = new Set(rolesList.map(r => r.title.trim()));

            const allCandidates = candidatesResp.data || [];
            setAiInterviews(allCandidates.filter(c => c.total_questions > 0));
            setResumeResults(allCandidates);

            const assessmentList = aiResp.data || [];
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
                            display_name: assessment.role || assessment.required_skills, // Use role if available
                            role: assessment.role,
                        },
                        candidate: {
                            name: sub.candidate_name,
                            email: sub.candidate_email,
                        },
                        score: sub.score,
                        total: sub.results_breakdown?.total_possible || (assessment.total_points || 100),
                        percentage: sub.percentage,
                        status: sub.status,
                        submitted_at: sub.submitted_at,
                    });
                });
            });

            const sorted = allSubmissions
                .filter(s => s.submitted_at && s.status !== 'ONGOING')
                .sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at));
            setAiAssessments(sorted);

            const groups = {};
            // Initialize with all valid job roles so they appear even if empty
            rolesList.forEach(r => {
                groups[r.title.trim()] = { resume: [], assessment: [], interview: [], total: 0 };
            });

            const addToGroup = (role, item, type) => {
                const name = (role || '').trim();
                // Only add to group if it's a known job role title
                if (groups[name]) {
                    groups[name][type].push(item);
                    groups[name].total += 1;
                }
            };

            allCandidates.forEach(c => {
                if (c.total_questions > 0) addToGroup(c.job_title, c, 'interview');
                else addToGroup(c.job_title, c, 'resume');
            });

            sorted.forEach(s => {
                addToGroup(s.assessment.role || s.assessment.display_name, s, 'assessment');
            });

            setGroupedData(groups);
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
        setStatusFilter('all');
        setCurrentPage(1);
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

    const isPass = (r, type) => {
        if (type === 'resume') return r.status === 'Resume Passed' || (r.status !== 'Resume Failed' && r.resume_score > 0 && r.resume_score >= 70);
        if (type === 'assessment') return r.status === 'selected' || (r.percentage != null && r.percentage >= 50);
        if (type === 'interview') return r.status === 'Completed' || (r.score != null && (r.score / 100) >= 0.5);
        return false;
    };

    const getDataForActiveContext = () => {
        if (!selectedRole || !groupedData[selectedRole]) return [];
        const roleData = groupedData[selectedRole];
        if (activeTab === 'resume') return roleData.resume.map(r => ({ ...r, _type: 'candidate', _deleteKey: `resume-${r.id}` }));
        if (activeTab === 'assessment') return roleData.assessment.map(r => ({ ...r, _type: 'ai_assessment', _deleteKey: r.submission_id }));
        if (activeTab === 'interview') return roleData.interview.map(r => ({ ...r, _type: 'candidate', _deleteKey: `interview-${r.id}` }));
        return [];
    };

    const allRows = viewMode === 'detail' ? getDataForActiveContext() : [];

    const currentRows = statusFilter === 'all'
        ? allRows
        : allRows.filter(r => {
            const pass = isPass(r, activeTab);
            return statusFilter === 'pass' ? pass : !pass;
        });

    const itemsPerPage = 10;
    const indexOfLastRow = currentPage * itemsPerPage;
    const indexOfFirstRow = indexOfLastRow - itemsPerPage;
    const paginatedRows = currentRows.slice(indexOfFirstRow, indexOfLastRow);
    const totalPages = Math.ceil(currentRows.length / itemsPerPage);

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

        const deletedCandidateIds = new Set(items.filter(i => i._type === 'candidate').map(i => i.id));
        const deletedAssessmentKeys = new Set(items.filter(i => i._type === 'ai_assessment').map(i => i.submission_id));

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

    const handleRoleClick = (roleName) => {
        setSelectedRole(roleName);
        setViewMode('detail');
        setActiveTab('resume');
        setSearchParams({ tab: 'resume' });
        setCurrentPage(1);
    };

    const handleBackToOverview = () => {
        setViewMode('overview');
        setSelectedRole(null);
    };

    const checkboxStyle = { width: '16px', height: '16px', cursor: 'pointer', accentColor: '#4F46E5' };

    return (
        <div className="results-page">
            <div className="bg-shape shape-1"></div>
            <div className="bg-shape shape-2"></div>
            <div className="bg-shape shape-3"></div>

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

            {confirmDelete && (
                <div className="glass-modal-overlay">
                    <div className="glass-modal-content" style={{ padding: '2.5rem', maxWidth: '420px', width: '90%', textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>🗑️</div>
                        <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: '#111827', marginBottom: '0.5rem' }}>
                            Delete {confirmDelete.items.length > 1 ? `${confirmDelete.items.length} Results` : 'Result'}?
                        </h2>
                        <p style={{ color: '#475569', marginBottom: '1.75rem', lineHeight: '1.6', fontSize: '0.95rem' }}>
                            {confirmDelete.items.length === 1
                                ? <>This will permanently delete the result for <strong>{confirmDelete.items[0].full_name || confirmDelete.items[0].candidate?.name || 'this candidate'}</strong>.</>
                                : <>This will permanently delete <strong>{confirmDelete.items.length} selected results</strong>. This action cannot be undone.</>}
                        </p>
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                            <button onClick={cancelDelete} style={{ padding: '0.7rem 1.5rem', border: '1px solid #cbd5e1', borderRadius: '12px', background: 'white', cursor: 'pointer', fontWeight: '700' }}>Cancel</button>
                            <button onClick={confirmAndDelete} style={{ padding: '0.7rem 1.5rem', border: 'none', borderRadius: '12px', background: '#EF4444', color: 'white', cursor: 'pointer', fontWeight: '700' }}>Delete</button>
                        </div>
                    </div>
                </div>
            )}

            {summaryModal && (
                <div className="glass-modal-overlay">
                    <div className="glass-modal-content" style={{ width: '100%', maxWidth: '800px', maxHeight: '85vh', display: 'flex', flexDirection: 'column' }}>
                        <div style={{ padding: '1.5rem 2rem', borderBottom: '1px solid #F3F4F6', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <div>
                                <h2 style={{ fontSize: '1.25rem', fontWeight: '800', margin: 0 }}>Interview Justification</h2>
                                <p style={{ fontSize: '0.85rem', color: '#6B7280', margin: '0.2rem 0 0' }}>AI Evaluation for <strong>{summaryModal.full_name}</strong></p>
                            </div>
                            <button onClick={() => setSummaryModal(null)} style={{ border: 'none', background: '#F3F4F6', borderRadius: '50%', width: '36px', height: '36px', cursor: 'pointer' }}>
                                <i className="fa-solid fa-xmark" />
                            </button>
                        </div>
                        <div style={{ padding: '2rem', overflowY: 'auto', flex: 1 }}>
                            {(!summaryModal.interview_summary || summaryModal.interview_summary.length === 0) ? (
                                <p>No feedback available.</p>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                    {summaryModal.interview_summary.map((item, idx) => (
                                        <div key={idx} style={{ border: '1px solid #E5E7EB', borderRadius: '16px', overflow: 'hidden' }}>
                                            <div style={{ padding: '1rem', background: '#F9FAFB', borderBottom: '1px solid #E5E7EB', display: 'flex', justifyContent: 'space-between' }}>
                                                <span style={{ fontWeight: '800', color: '#4F46E5' }}>Question {idx + 1}</span>
                                                <div style={{ fontWeight: '800' }}>Score: {item.score}/10</div>
                                            </div>
                                            <div style={{ padding: '1.25rem' }}>
                                                <p style={{ fontWeight: '700', marginBottom: '0.5rem' }}>{item.question}</p>
                                                <p style={{ fontStyle: 'italic', color: '#4B5563' }}>"{item.answer}"</p>
                                                <p style={{ marginTop: '1rem' }}><strong>AI Justification:</strong> {item.feedback}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        <div style={{ padding: '1.25rem 2rem', borderTop: '1px solid #F3F4F6', textAlign: 'right' }}>
                            <button onClick={() => setSummaryModal(null)} style={{ padding: '0.6rem 1.5rem', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '10px', fontWeight: '700' }}>Close</button>
                        </div>
                    </div>
                </div>
            )}

            <div className="dashboard-main" style={{ width: '100%', padding: '0 2rem 3rem' }}>
                <header style={{ marginBottom: '2rem', textAlign: 'center' }}>
                    <h1 style={{ fontSize: '3.2rem', fontWeight: '900', color: '#111827', margin: 0 }}>
                        AI <span style={{ color: '#4F46E5' }}>Results</span>
                    </h1>
                    {viewMode === 'detail' && (
                        <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
                            <button onClick={handleBackToOverview} style={{ background: '#F3F4F6', border: 'none', padding: '0.6rem 1.2rem', borderRadius: '10px', cursor: 'pointer', fontWeight: '700', color: '#4B5563' }}>
                                <i className="fa-solid fa-arrow-left" /> Back to Roles
                            </button>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: '800' }}>{selectedRole}</h2>
                        </div>
                    )}
                </header>

                {viewMode === 'overview' && (
                    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                        <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <div style={{ width: '4px', height: '24px', background: '#4F46E5', borderRadius: '2px' }} />
                            <h2 style={{ fontSize: '1.4rem', fontWeight: '800', margin: 0, color: '#1E293B' }}>Job Roles</h2>
                            <span style={{ fontSize: '0.85rem', color: '#64748B', fontWeight: '600', marginLeft: 'auto' }}>
                                {Object.keys(groupedData).length} Roles Found
                            </span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {Object.entries(groupedData).map(([roleName, data]) => (
                                <div key={roleName} onClick={() => handleRoleClick(roleName)} className="glass-table-card role-card" style={{
                                    padding: '1.25rem 2rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)', borderLeft: '4px solid transparent'
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                                        <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: 'rgba(79, 70, 229, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4F46E5' }}>
                                            <i className="fa-solid fa-briefcase" />
                                        </div>
                                        <div>
                                            <h3 style={{ fontSize: '1.1rem', fontWeight: '800', margin: 0, color: '#1E293B' }}>{roleName}</h3>
                                            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.25rem' }}>
                                                <span style={{ fontSize: '0.8rem', color: '#64748B', fontWeight: '600' }}>
                                                    {data.total} Submission{data.total !== 1 ? 's' : ''}
                                                </span>
                                                {data.total > 0 && (
                                                    <div style={{ display: 'flex', gap: '0.5rem', opacity: 0.7 }}>
                                                        {data.resume.length > 0 && <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>• {data.resume.length} Screening</span>}
                                                        {data.assessment.length > 0 && <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>• {data.assessment.length} Assessment</span>}
                                                        {data.interview.length > 0 && <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>• {data.interview.length} Interview</span>}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ color: '#94A3B8', fontSize: '1.2rem', transition: 'transform 0.2s' }} className="arrow-icon">
                                        <i className="fa-solid fa-angle-right" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {viewMode === 'detail' && (
                    <>
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
                            <div style={{ display: 'flex', gap: '0.5rem', background: '#F4F7FE', padding: '0.35rem', borderRadius: '12px' }}>
                                {[
                                    { id: 'resume', label: 'Resume Screening', icon: 'fa-file-magnifying-glass' },
                                    { id: 'assessment', label: 'AI Assessments', icon: 'fa-brain' },
                                    { id: 'interview', label: 'AI Interviews', icon: 'fa-microphone-lines' }
                                ].map(tab => (
                                    <button key={tab.id} onClick={() => handleTabChange(tab.id)} style={{
                                        background: activeTab === tab.id ? 'white' : 'transparent',
                                        border: 'none', padding: '0.65rem 1.3rem', borderRadius: '10px',
                                        fontWeight: '700', color: activeTab === tab.id ? '#4F46E5' : '#718096',
                                        cursor: 'pointer'
                                    }}>
                                        <i className={`fa-solid ${tab.icon}`} style={{ marginRight: '0.5rem' }} />
                                        {tab.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#9CA3AF' }}>FILTER:</span>
                            {[{ key: 'all', label: 'All' }, { key: 'pass', label: 'Pass ✓' }, { key: 'fail', label: 'Fail ✗' }].map(f => (
                                <button key={f.key} onClick={() => { setStatusFilter(f.key); setCurrentPage(1); }} style={{
                                    padding: '0.35rem 0.9rem', borderRadius: '20px', border: '1px solid',
                                    fontSize: '0.78rem', fontWeight: '700', cursor: 'pointer',
                                    borderColor: statusFilter === f.key ? '#4F46E5' : '#E5E7EB',
                                    background: statusFilter === f.key ? '#EEF2FF' : 'white',
                                    color: statusFilter === f.key ? '#4F46E5' : '#6B7280',
                                }}>{f.label}</button>
                            ))}
                            <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: '#9CA3AF' }}>{currentRows.length} results</span>
                        </div>

                        <div className="glass-table-card">
                            {loading ? (
                                <div style={{ padding: '6rem 2rem', textAlign: 'center' }}>
                                    <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', color: '#4F46E5' }} />
                                    Loading...
                                </div>
                            ) : (
                                <div style={{ overflowX: 'auto' }}>
                                    <table className="results-table">
                                        <thead>
                                            <tr>
                                                <th style={{ width: '60px', textAlign: 'center' }}>
                                                    <input type="checkbox" checked={allSelected} onChange={toggleSelectAll} />
                                                </th>
                                                <th>Candidate Info</th>
                                                <th>Result Data</th>
                                                <th>Date</th>
                                                <th>AI Status</th>
                                                <th style={{ textAlign: 'center' }}>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {currentRows.length === 0 && (
                                                <tr><td colSpan="6" style={{ padding: '4rem', textAlign: 'center' }}>No candidates found.</td></tr>
                                            )}
                                            {paginatedRows.map((r) => {
                                                const isSelected = selected.has(r._deleteKey);
                                                const isDeleting = deletingIds.has(r._deleteKey);
                                                return (
                                                    <tr key={r._deleteKey} className={isSelected ? 'selected' : ''}>
                                                        <td style={{ textAlign: 'center' }}>
                                                            <input type="checkbox" checked={isSelected} onChange={() => toggleSelect(r._deleteKey)} />
                                                        </td>
                                                        <td>
                                                            <div style={{ fontWeight: '800' }}>{r.full_name || r.candidate?.name}</div>
                                                            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{r.email || r.candidate?.email}</div>
                                                        </td>
                                                        <td>
                                                            {activeTab === 'resume' ? `${r.resume_score || 0}% Match` :
                                                                activeTab === 'assessment' ? `${Math.round((r.score / r.total) * 100)}% (${r.score}/${r.total})` :
                                                                    `${Math.round(r.score)}% Evaluation`}
                                                        </td>
                                                        <td>{new Date(r.created_at || r.submitted_at || r.completed_at).toLocaleDateString()}</td>
                                                        <td>
                                                            <span style={{ padding: '0.3rem 0.6rem', borderRadius: '6px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>
                                                                {getStatusLabel(r.status)}
                                                            </span>
                                                        </td>
                                                        <td style={{ textAlign: 'center' }}>
                                                            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                                                                {activeTab !== 'resume' && (
                                                                    <button onClick={() => activeTab === 'assessment' ? navigate(`/ai-assessments/${r.assessment?.id}?tab=submissions`) : setSummaryModal(r)} style={{ padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid #e2e8f0', background: 'white', cursor: 'pointer', fontSize: '0.8rem' }}>Review</button>
                                                                )}
                                                                <RowDeleteBtn item={r} isDeleting={isDeleting} onDelete={() => requestDelete([r])} />
                                                            </div>
                                                        </td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>

                                    {totalPages > 1 && (
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: 'white', borderTop: '1px solid #e2e8f0' }}>
                                            <span style={{ fontSize: '0.8rem' }}>Page {currentPage} of {totalPages}</span>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))} disabled={currentPage === 1}>Prev</button>
                                                <button onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))} disabled={currentPage === totalPages}>Next</button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

const RowDeleteBtn = ({ item, isDeleting, onDelete }) => (
    <button
        onClick={onDelete}
        disabled={isDeleting}
        style={{
            background: 'rgba(254, 226, 226, 0.6)', border: '1px solid #ef4444', color: '#ef4444',
            borderRadius: '8px', padding: '0.4rem 0.8rem', cursor: isDeleting ? 'not-allowed' : 'pointer', fontSize: '0.8rem'
        }}
    >
        {isDeleting ? '...' : 'Delete'}
    </button>
);

export default ResultsAI;