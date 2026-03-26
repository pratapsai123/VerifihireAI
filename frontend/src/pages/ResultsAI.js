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
    
    // Auth context
    const me = (() => {
        try { return JSON.parse(localStorage.getItem('user') || '{}'); } 
        catch { return {}; }
    })();
    const myRole = (me?.role || '').toLowerCase();
    const canDelete = myRole === 'application_admin' || (myRole !== 'company_admin'); 
    // Note: HR can still see it (maybe they request deletion), 
    // but the user specifically said "Admin" can't delete.

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
    const [summaryModal, setSummaryModal] = useState(null); // Candidate object for interview
    const [viewedSubmission, setViewedSubmission] = useState(null); // Submission object for assessment

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
                        candidate_questions: sub.candidate_questions || assessment.generated_content,
                        answers: sub.answers || {},
                        submitted_at: sub.submitted_at,
                        total_possible: sub.results_breakdown?.total_possible || sub.total_points || 0
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
                const name = (role || 'Other').trim();
                // Create group if it doesn't exist (previously it only used predefined Job Roles)
                if (!groups[name]) {
                    groups[name] = { resume: [], assessment: [], interview: [], total: 0 };
                }
                groups[name][type].push(item);
                groups[name].total += 1;
            };

            allCandidates.forEach(c => {
                if (c.total_questions > 0) addToGroup(c.job_title, c, 'interview');
                else addToGroup(c.job_title, c, 'resume');
            });

            sorted.forEach(s => {
                const roleName = s.assessment.role || s.assessment.display_name || s.assessment.name || 'General Assessment';
                addToGroup(roleName, s, 'assessment');
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
        const sid = searchParams.get('subId');
        if (sid) {
            const numSid = parseInt(sid);
            // Search in all assessments across roles if needed, or just current role
            const sub = aiAssessments.find(a => a.id === numSid || a.submission_id === `ai_${sid}`);
            if (sub && sub !== viewedSubmission) {
                setViewedSubmission(sub);
            }
        } else if (viewedSubmission) {
            setViewedSubmission(null);
        }
    }, [searchParams, aiAssessments, viewedSubmission]);

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
        if (s === 'extraction failed') return { background: '#FFF5F5', color: '#EE5D50' };
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

    const performDelete = async (items, reason) => {
        const ids = new Set(items.map(i => i._deleteKey));
        setDeletingIds(prev => new Set([...prev, ...ids]));

        let successCount = 0;
        let failCount = 0;
        let requestMessage = '';

        await Promise.all(items.map(async (item) => {
            try {
                let resp;
                if (item._type === 'candidate') {
                    resp = await axios.delete(`${API_BASE_URL}/ai-candidates/${item.id}/`, { data: { reason } });
                    successCount++;
                } else if (item._type === 'ai_assessment') {
                    const subId = item.submission_id.replace('ai_', '');
                    resp = await axios.delete(`${API_BASE_URL}/ai/submission/${subId}/`, { data: { reason } });
                    successCount++;
                }
                if (resp?.data?.message && !requestMessage) requestMessage = resp.data.message;
            } catch (err) {
                console.error('Delete failed for', item._deleteKey, err);
                failCount++;
            }
        }));

        const deletedCandidateIds = new Set(items.filter(i => i._type === 'candidate').map(i => i.id));
        const deletedAssessmentKeys = new Set(items.filter(i => i._type === 'ai_assessment').map(i => i.submission_id));

        // Only remove from UI if it was actually deleted (not just requested)
        setDeletingIds(prev => { const s = new Set(prev); ids.forEach(k => s.delete(k)); return s; });

        if (requestMessage) {
            showToast('info', requestMessage);
        } else if (successCount > 0 && failCount === 0) {
            setResumeResults(prev => prev.filter(r => !deletedCandidateIds.has(r.id)));
            setAiInterviews(prev => prev.filter(r => !deletedCandidateIds.has(r.id)));
            setAiAssessments(prev => prev.filter(r => !deletedAssessmentKeys.has(r.submission_id)));
            setSelected(prev => { const s = new Set(prev); ids.forEach(k => s.delete(k)); return s; });
            showToast('success', `${successCount} result${successCount > 1 ? 's' : ''} deleted.`);
        } else if (failCount > 0) {
            showToast('error', `${failCount} deletion(s) failed.`);
        }
    };

    const confirmAndDelete = async (reason) => {
        if (!confirmDelete) return;
        const items = confirmDelete.items;
        setConfirmDelete(null);
        await performDelete(items, reason);
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
                            {confirmDelete.items.length > 1 ? `Delete ${confirmDelete.items.length} Results` : 'Delete Result'}?
                        </h2>
                        <p style={{ color: '#475569', marginBottom: '1.25rem', lineHeight: '1.6', fontSize: '0.95rem' }}>
                            {confirmDelete.items.length === 1
                                ? <>This will initiate a deletion request for <strong>{confirmDelete.items[0].full_name || confirmDelete.items[0].candidate?.name || 'this candidate'}</strong>.</>
                                : <>This will initiate a deletion request for <strong>{confirmDelete.items.length} selected results</strong>.</>}
                        </p>
                        
                        <div style={{ marginBottom: '1.5rem', textAlign: 'left' }}>
                            <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#64748b', display: 'block', marginBottom: '0.5rem' }}>Reason for Deletion (Required)</label>
                            <textarea 
                                id="delete-reason-input"
                                style={{ width: '100%', borderRadius: '8px', border: '1px solid #e2e8f0', padding: '0.75rem', fontSize: '0.9rem', minHeight: '80px', fontFamily: 'inherit' }}
                                placeholder="Please provide a valid reason..."
                                required
                            />
                        </div>

                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                            <button onClick={cancelDelete} style={{ padding: '0.7rem 1.5rem', border: '1px solid #cbd5e1', borderRadius: '12px', background: 'white', cursor: 'pointer', fontWeight: '700' }}>Cancel</button>
                            <button 
                                onClick={() => {
                                    const reason = document.getElementById('delete-reason-input')?.value;
                                    if (!reason || reason.trim().length < 5) {
                                        alert("Please provide a meaningful reason (at least 5 characters).");
                                        return;
                                    }
                                    confirmAndDelete(reason);
                                }} 
                                style={{ padding: '0.7rem 1.5rem', border: 'none', borderRadius: '12px', background: '#EF4444', color: 'white', cursor: 'pointer', fontWeight: '700' }}
                            >
                                Submit Request
                            </button>
                        </div>
                    </div>
                </div>
            )}


            {viewedSubmission && (
                <div className="glass-modal-overlay" style={{ zIndex: 10000, background: 'rgba(27, 37, 75, 0.4)', backdropFilter: 'blur(8px)' }}>
                    <div className="glass-modal-content" style={{ 
                        width: '95%', maxWidth: '1200px', height: '90vh', 
                        display: 'flex', flexDirection: 'column', padding: 0,
                        background: '#F4F7FE', borderRadius: '30px'
                    }}>
                        {/* Modal Header */}
                        <div style={{ 
                            padding: '1.5rem 2.5rem', background: 'white', borderBottom: '1px solid #E2E8F0',
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            borderTopLeftRadius: '30px', borderTopRightRadius: '30px'
                        }}>
                            <div>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: '900', color: '#1B254B', margin: 0 }}>
                                    {viewedSubmission.candidate_name} <span style={{ color: '#707EAE', fontWeight: '400', fontSize: '1.1rem' }}>Review</span>
                                </h2>
                                <p style={{ fontSize: '0.9rem', color: '#A3AED0', margin: '0.25rem 0 0', fontWeight: '600' }}>
                                    Assessment: <span style={{ color: '#4318FF' }}>{viewedSubmission.assessment_name}</span>
                                    <span style={{ margin: '0 0.75rem', color: '#CBD5E1' }}>|</span>
                                    Submitted {new Date(viewedSubmission.submitted_at).toLocaleString()}
                                </p>
                            </div>
                            <button 
                                onClick={() => {
                                    const newParams = new URLSearchParams(searchParams);
                                    newParams.delete('subId');
                                    setSearchParams(newParams);
                                }}
                                style={{ 
                                    background: '#F4F7FE', border: 'none', borderRadius: '50%', 
                                    width: '44px', height: '44px', cursor: 'pointer',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    color: '#4318FF', transition: 'all 0.2s', boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
                                }}
                            >
                                <i className="fa-solid fa-xmark" style={{ fontSize: '1.25rem' }} />
                            </button>
                        </div>

                        {/* Modal Body */}
                        <div style={{ flex: 1, overflowY: 'auto', padding: '2.5rem' }}>
                            <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
                                
                                {/* 3-Card Summary (Matching AiAssessmentDetail.js) */}
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2.5rem' }}>
                                    {/* MCQ Card */}
                                    <div style={{ background: 'white', padding: '1.5rem', borderRadius: '25px', textAlign: 'center', boxShadow: '0 10px 30px rgba(0,0,0,0.03)', border: '1px solid #E0E5F2' }}>
                                        <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>MCQ Score</div>
                                        <div style={{ fontSize: '2.5rem', fontWeight: '800', color: '#4318FF' }}>
                                            {viewedSubmission.results_breakdown?.mcq?.total > 0
                                                ? Math.round((viewedSubmission.mcq_score / viewedSubmission.results_breakdown.mcq.total) * 100)
                                                : 0}%
                                        </div>
                                        <div style={{ color: '#1B254B', fontWeight: '600', fontSize: '0.9rem' }}>
                                            {viewedSubmission.mcq_score / 20} / {viewedSubmission.candidate_questions?.mcqs?.length || 0} Correct
                                        </div>
                                    </div>

                                    {/* Coding Card */}
                                    <div style={{ background: 'white', padding: '1.5rem', borderRadius: '25px', textAlign: 'center', boxShadow: '0 10px 30px rgba(0,0,0,0.03)', border: '1px solid #E0E5F2' }}>
                                        <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Coding Score</div>
                                        <div style={{ fontSize: '2.5rem', fontWeight: '800', color: '#4318FF' }}>
                                            {viewedSubmission.results_breakdown?.coding?.total > 0
                                                ? Math.round((viewedSubmission.coding_score / viewedSubmission.results_breakdown.coding.total) * 100)
                                                : 0}%
                                        </div>
                                        <div style={{ color: '#1B254B', fontWeight: '600', fontSize: '0.9rem' }}>
                                            {viewedSubmission.coding_score} / {viewedSubmission.results_breakdown?.coding?.total || 0} pts
                                        </div>
                                    </div>

                                    {/* Integrity Card */}
                                    <div style={{ background: 'white', padding: '1.5rem', borderRadius: '25px', textAlign: 'center', boxShadow: '0 10px 30px rgba(0,0,0,0.03)', border: '1px solid #E0E5F2' }}>
                                        <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Integrity</div>
                                        <div style={{ fontSize: '2.5rem', fontWeight: '800', color: (viewedSubmission.integrity_score || 0) >= 70 ? '#05CD99' : '#EE5D50' }}>
                                            {viewedSubmission.integrity_score || 0}%
                                        </div>
                                        <div style={{ color: (viewedSubmission.integrity_score || 0) >= 70 ? '#05CD99' : '#EE5D50', fontWeight: '800', textTransform: 'uppercase', fontSize: '0.8rem' }}>
                                            {(viewedSubmission.integrity_score || 0) >= 70 ? '✓ Reliable' : '⚠ Suspicious'}
                                        </div>
                                    </div>
                                </div>

                                {/* Overall Result Banner */}
                                <div style={{ 
                                    background: viewedSubmission.status === 'selected' ? '#E6FBF5' : '#FFF5F5', 
                                    padding: '1.5rem', borderRadius: '25px', textAlign: 'center', marginBottom: '3rem',
                                    border: `1px solid ${viewedSubmission.status === 'selected' ? '#05CD99' : '#EE5D50'}`
                                }}>
                                    <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.3rem' }}>Overall Result</div>
                                    <div style={{ fontSize: '2.5rem', fontWeight: '800', color: viewedSubmission.status === 'selected' ? '#05CD99' : '#EE5D50' }}>{viewedSubmission.percentage}%</div>
                                    <div style={{ color: '#1B254B', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '1px' }}>{viewedSubmission.status}</div>
                                </div>

                                {/* Answer Verification (MCQs) */}
                                <h4 style={{ color: '#1B254B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <i className="fa-solid fa-list-check" style={{ color: '#4318FF' }}></i> MCQ Answer Verification
                                </h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '4rem' }}>
                                    {viewedSubmission.candidate_questions?.mcqs?.map((q, i) => {
                                        const candAns = viewedSubmission.answers[`mcq_${i}`];
                                        const isCorrect = candAns === q.answer;
                                        return (
                                            <div key={i} style={{ 
                                                padding: '2rem', borderRadius: '30px', 
                                                border: '1px solid #E0E5F2', background: 'white', 
                                                boxShadow: '0 10px 30px rgba(0,0,0,0.02)' 
                                            }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                                                    <div style={{ flex: 1 }}>
                                                        <span style={{ fontSize: '0.75rem', fontWeight: '800', color: '#707EAE', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Question {i + 1}</span>
                                                        <p style={{ fontWeight: '700', color: '#1B254B', fontSize: '1.1rem', margin: '0.5rem 0 0', lineHeight: 1.5 }}>{q.question}</p>
                                                    </div>
                                                    <div style={{ 
                                                        padding: '0.5rem 1rem', borderRadius: '12px', 
                                                        background: isCorrect ? '#E6FBF5' : '#FFF5F5', 
                                                        color: isCorrect ? '#05CD99' : '#EE5D50', 
                                                        fontWeight: '800', fontSize: '0.75rem', 
                                                        display: 'flex', alignItems: 'center', gap: '6px',
                                                        border: `1px solid ${isCorrect ? '#05CD9944' : '#EE5D5044'}`
                                                    }}>
                                                        <i className={`fa-solid ${isCorrect ? 'fa-circle-check' : 'fa-circle-xmark'}`}></i>
                                                        {isCorrect ? 'CORRECT' : 'INCORRECT'}
                                                    </div>
                                                </div>

                                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                                    {q.options.map((opt, oi) => {
                                                        const isSelected = opt === candAns;
                                                        const isAnswer = opt === q.answer;

                                                        let bg = 'white';
                                                        let border = '1px solid #E0E5F2';
                                                        let color = '#1B254B';
                                                        let icon = null;

                                                        if (isAnswer) {
                                                            bg = '#E6FBF5';
                                                            border = '2px solid #05CD99';
                                                            color = '#05CD99';
                                                            icon = <i className="fa-solid fa-check-circle" style={{ marginLeft: 'auto' }}></i>;
                                                        } else if (isSelected && !isCorrect) {
                                                            bg = '#FFF5F5';
                                                            border = '2px solid #EE5D50';
                                                            color = '#EE5D50';
                                                            icon = <i className="fa-solid fa-circle-xmark" style={{ marginLeft: 'auto' }}></i>;
                                                        }

                                                        return (
                                                            <div key={oi} style={{
                                                                padding: '1rem 1.25rem', background: bg, borderRadius: '16px', border,
                                                                color: color, fontWeight: (isAnswer || isSelected) ? '700' : '500',
                                                                fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '10px'
                                                            }}>
                                                                <span style={{ opacity: 0.5, fontSize: '0.8rem', flexShrink: 0 }}>{String.fromCharCode(65 + oi)}.</span>
                                                                <span style={{ flex: 1 }}>{opt}</span>
                                                                {icon}
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                                
                                                {!isCorrect && (
                                                    <div style={{ 
                                                        marginTop: '1.25rem', padding: '1rem 1.5rem', 
                                                        background: 'linear-gradient(135deg, #E6FBF5, #D1F7ED)', 
                                                        borderRadius: '16px', display: 'flex', alignItems: 'center', gap: '12px',
                                                        border: '1px solid #05CD9933'
                                                    }}>
                                                        <i className="fa-solid fa-circle-check" style={{ color: '#05CD99', fontSize: '1.2rem' }} />
                                                        <div>
                                                            <div style={{ fontSize: '0.7rem', fontWeight: '800', color: '#05CD99', textTransform: 'uppercase' }}>Correct Solution</div>
                                                            <div style={{ fontWeight: '700', color: '#1B254B', fontSize: '0.95rem' }}>{q.answer}</div>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>

                                {/* Coding Challenges */}
                                {viewedSubmission.candidate_questions?.coding_challenges?.length > 0 && (
                                    <div style={{ marginBottom: '4rem' }}>
                                        <h4 style={{ color: '#1B254B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <i className="fa-solid fa-code" style={{ color: '#4318FF' }}></i> Coding Verification
                                        </h4>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
                                            {viewedSubmission.candidate_questions.coding_challenges.map((c, i) => {
                                                const candCode = viewedSubmission.answers[`coding_${i}`];
                                                const res = viewedSubmission.results_breakdown?.coding_results?.[c.id] || {};
                                                return (
                                                    <div key={i} style={{ background: 'white', borderRadius: '30px', padding: '2rem', border: '1px solid #E0E5F2', boxShadow: '0 10px 30px rgba(0,0,0,0.02)' }}>
                                                        <div style={{ marginBottom: '2rem' }}>
                                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                                                <div>
                                                                    <h5 style={{ color: '#1B254B', fontSize: '1.2rem', fontWeight: '800', margin: '0 0 0.5rem 0' }}>{c.title}</h5>
                                                                    <p style={{ color: '#707EAE', fontSize: '0.95rem', lineHeight: '1.5', margin: 0 }}>{c.problem_statement}</p>
                                                                </div>
                                                                <div style={{ textAlign: 'right', background: '#F4F7FE', padding: '0.5rem 1rem', borderRadius: '12px' }}>
                                                                    <div style={{ fontSize: '0.7rem', fontWeight: '800', color: '#A3AED0', textTransform: 'uppercase' }}>Passed Tests</div>
                                                                    <div style={{ fontSize: '1.2rem', fontWeight: '900', color: res.pass_count === res.total_count ? '#05CD99' : '#F59E0B' }}>
                                                                        {res.pass_count || 0}/{res.total_count || 10}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div style={{ position: 'relative' }}>
                                                            <div style={{
                                                                position: 'absolute', top: '-14px', left: '24px',
                                                                background: '#4318FF', color: 'white', padding: '4px 14px',
                                                                borderRadius: '8px', fontSize: '0.75rem', fontWeight: '800', zIndex: 1
                                                            }}>CANDIDATE SUBMISSION</div>
                                                            <div style={{
                                                                background: '#1B254B', borderRadius: '20px',
                                                                padding: '2.5rem 2rem 2rem', boxShadow: '0 15px 35px rgba(0,0,0,0.1)'
                                                            }}>
                                                                <pre style={{
                                                                    margin: 0, color: '#05CD99',
                                                                    fontFamily: "'Fira Code', 'Courier New', monospace",
                                                                    fontSize: '0.95rem', lineHeight: '1.6', whiteSpace: 'pre-wrap'
                                                                }}>
                                                                    {candCode || '// No code submitted'}
                                                                </pre>
                                                            </div>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}

                                {/* Integrity Violations */}
                                {viewedSubmission.integrity_screenshots?.length > 0 && (
                                    <div style={{ marginTop: '4rem' }}>
                                        <h4 style={{ color: '#1B254B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <i className="fa-solid fa-shield-halved" style={{ color: '#EE5D50' }}></i> Integrity Violations Log
                                        </h4>
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
                                            {viewedSubmission.integrity_screenshots.map((snap, sIdx) => (
                                                <div key={sIdx} style={{ background: 'white', borderRadius: '20px', padding: '12px', border: '1px solid #E0E5F2', textAlign: 'center' }}>
                                                    <div style={{ 
                                                        width: '100%', height: '160px', background: '#F4F7FE', 
                                                        borderRadius: '15px', overflow: 'hidden', marginBottom: '10px', 
                                                        position: 'relative', border: '1px solid #E0E5F2'
                                                    }}>
                                                        <img 
                                                            src={snap.screenshot_url || snap.webcam_screenshot_url} 
                                                            alt={snap.event_type}
                                                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                            onError={(e) => { e.target.src = 'https://placehold.co/400x300?text=No+Image'; }}
                                                        />
                                                        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: 'rgba(27, 37, 75, 0.8)', color: 'white', fontSize: '0.65rem', padding: '6px', fontWeight: '700' }}>
                                                            {snap.event_type.replace(/_/g, ' ').toUpperCase()}
                                                        </div>
                                                    </div>
                                                    <div style={{ color: '#A3AED0', fontSize: '0.75rem', fontWeight: '700' }}>
                                                        {new Date(snap.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div style={{ 
                            padding: '1.5rem 2.5rem', background: 'white', borderTop: '1px solid #E2E8F0',
                            textAlign: 'right', borderBottomLeftRadius: '30px', borderBottomRightRadius: '30px'
                        }}>
                            <button 
                                onClick={() => {
                                    const newParams = new URLSearchParams(searchParams);
                                    newParams.delete('subId');
                                    setSearchParams(newParams);
                                }}
                                style={{ 
                                    padding: '0.8rem 2.5rem', background: '#4318FF', color: 'white', 
                                    border: 'none', borderRadius: '15px', fontWeight: '800', cursor: 'pointer',
                                    boxShadow: '0 10px 20px rgba(67, 24, 255, 0.2)', fontSize: '0.95rem'
                                }}
                            >
                                Finished Review
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {summaryModal && (
                <div className="glass-modal-overlay" style={{ zIndex: 10000, background: 'rgba(27, 37, 75, 0.4)', backdropFilter: 'blur(8px)' }}>
                    <div className="glass-modal-content" style={{ 
                        width: '95%', maxWidth: '900px', height: '85vh', 
                        display: 'flex', flexDirection: 'column', padding: 0,
                        background: '#F4F7FE', borderRadius: '30px'
                    }}>
                        <div style={{ 
                            padding: '1.5rem 2.5rem', background: 'white', borderBottom: '1px solid #E2E8F0',
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            borderTopLeftRadius: '30px', borderTopRightRadius: '30px'
                        }}>
                            <div>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: '900', color: '#1B254B', margin: 0 }}>
                                    {summaryModal.full_name || summaryModal.candidate?.name} <span style={{ color: '#707EAE', fontWeight: '400', fontSize: '1.1rem' }}>Interview Transcript</span>
                                </h2>
                                <p style={{ fontSize: '0.9rem', color: '#A3AED0', margin: '0.25rem 0 0', fontWeight: '600' }}>
                                    Role: <span style={{ color: '#4318FF' }}>{summaryModal.job_title || 'General'}</span>
                                    <span style={{ margin: '0 0.75rem', color: '#CBD5E1' }}>|</span>
                                    {summaryModal.interview_summary?.length || 0} Questions Answered
                                </p>
                            </div>
                            <button 
                                onClick={() => setSummaryModal(null)}
                                style={{ 
                                    background: '#F4F7FE', border: 'none', borderRadius: '50%', 
                                    width: '44px', height: '44px', cursor: 'pointer',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    color: '#4318FF', transition: 'all 0.2s', boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
                                }}
                            >
                                <i className="fa-solid fa-xmark" style={{ fontSize: '1.25rem' }} />
                            </button>
                        </div>
                        
                        <div style={{ flex: 1, overflowY: 'auto', padding: '2.5rem' }}>
                            <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                                {(!summaryModal.interview_summary || summaryModal.interview_summary.length === 0) ? (
                                    <div style={{ textAlign: 'center', color: '#A3AED0', padding: '3rem' }}>
                                        <i className="fa-solid fa-microphone-slash" style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.5 }}></i>
                                        <p style={{ fontWeight: '700', fontSize: '1.1rem' }}>No conversational data recorded.</p>
                                    </div>
                                ) : (
                                    summaryModal.interview_summary.map((turn, i) => (
                                        <div key={i} style={{ 
                                            background: 'white', borderRadius: '24px', padding: '2rem', 
                                            boxShadow: '0 10px 30px rgba(0,0,0,0.03)', border: '1px solid #E0E5F2',
                                            position: 'relative', overflow: 'hidden'
                                        }}>
                                            {/* Score Badge */}
                                            <div style={{
                                                position: 'absolute', top: '1.5rem', right: '1rem',
                                                background: (turn.score || 0) >= 7 ? '#E6FBF5' : (turn.score || 0) >= 4 ? '#FFFBEB' : '#FFF5F5',
                                                color: (turn.score || 0) >= 7 ? '#05CD99' : (turn.score || 0) >= 4 ? '#F59E0B' : '#EE5D50',
                                                padding: '0.4rem 1rem', borderRadius: '12px', fontSize: '0.9rem', fontWeight: '900',
                                                border: `1px solid ${(turn.score || 0) >= 7 ? '#05CD9944' : (turn.score || 0) >= 4 ? '#F59E0B44' : '#EE5D5044'}`
                                            }}>
                                                Marks: {turn.score || 0}/10
                                            </div>

                                            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', paddingRight: '120px' }}>
                                                <div style={{ 
                                                    width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg, #4F46E5, #4338CA)', 
                                                    color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                                                    boxShadow: '0 4px 10px rgba(79, 70, 229, 0.3)'
                                                }}>
                                                    <i className="fa-solid fa-robot"></i>
                                                </div>
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ fontSize: '0.8rem', fontWeight: '800', color: '#4318FF', textTransform: 'uppercase', marginBottom: '0.25rem' }}>AI Interviewer</div>
                                                    <p style={{ margin: 0, fontWeight: '700', color: '#1B254B', fontSize: '1.05rem', lineHeight: '1.6' }}>{turn.question}</p>
                                                </div>
                                            </div>
                                            
                                            <div style={{ display: 'flex', gap: '1rem', padding: '1.5rem', background: '#F8FAFC', borderRadius: '16px', border: '1px solid #E2E8F0', marginBottom: '1rem' }}>
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ fontSize: '0.8rem', fontWeight: '800', color: '#64748B', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Candidate Response</div>
                                                    <p style={{ margin: 0, fontWeight: '500', color: '#334155', fontSize: '1rem', lineHeight: '1.7' }}>
                                                        {turn.answer ? `"${turn.answer}"` : <span style={{ fontStyle: 'italic', color: '#94A3B8' }}>[No answer provided]</span>}
                                                    </p>
                                                </div>
                                            </div>

                                            {turn.reason && (
                                                <div style={{ padding: '1rem 1.5rem', background: '#F1F5F9', borderRadius: '12px', borderLeft: '4px solid #4318FF' }}>
                                                    <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#4318FF', textTransform: 'uppercase', marginBottom: '0.3rem' }}>AI Justification</div>
                                                    <p style={{ margin: 0, fontSize: '0.9rem', color: '#475569', fontWeight: '600', lineHeight: '1.5' }}>{turn.reason}</p>
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}

                                {/* Total Calculation Summary */}
                                {summaryModal.interview_summary && summaryModal.interview_summary.length > 0 && (
                                    <div style={{ 
                                        background: 'linear-gradient(135deg, #4F46E5, #4338CA)', 
                                        borderRadius: '24px', padding: '2.5rem', color: 'white',
                                        textAlign: 'center', boxShadow: '0 20px 40px rgba(67, 24, 255, 0.2)',
                                        marginTop: '1rem', marginBottom: '2rem'
                                    }}>
                                        <h3 style={{ margin: '0 0 1.5rem 0', fontSize: '1.4rem', fontWeight: '800', opacity: 0.9 }}>Interview Performance Summary</h3>
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                                            <div>
                                                <div style={{ fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', opacity: 0.7, marginBottom: '0.5rem' }}>Total Marks Obtained</div>
                                                <div style={{ fontSize: '2.5rem', fontWeight: '900' }}>{summaryModal.score} <span style={{ fontSize: '1.2rem', opacity: 0.6 }}>/ {summaryModal.interview_summary.length * 10}</span></div>
                                            </div>
                                            <div>
                                                <div style={{ fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', opacity: 0.7, marginBottom: '0.5rem' }}>Overall Percentage</div>
                                                <div style={{ fontSize: '2.5rem', fontWeight: '900' }}>
                                                    {Math.round((summaryModal.score / (summaryModal.interview_summary.length * 10)) * 100)}%
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
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
                        <div style={{ marginTop: '1.5rem' }}>
                            <button onClick={handleBackToOverview} style={{ 
                                background: 'none', border: 'none', padding: '0', 
                                cursor: 'pointer', fontWeight: '800', color: '#4F46E5', 
                                display: 'flex', alignItems: 'center', gap: '0.5rem',
                                marginBottom: '1.5rem', fontSize: '1rem'
                            }}>
                                <i className="fa-solid fa-arrow-left" /> Back to Archive
                            </button>
                            
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem' }}>
                                <div>
                                    <h1 style={{ fontSize: '3.5rem', fontWeight: '900', color: '#111827', margin: 0, textTransform: 'lowercase' }}>
                                        {selectedRole} <span style={{ color: '#94A3B8', fontWeight: '400', fontSize: '1.8rem' }}>Assessment Results</span>
                                    </h1>
                                    <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', fontWeight: '700', color: '#4F46E5' }}>
                                            <i className="fa-solid fa-calendar-plus" />
                                            <span style={{ color: '#94A3B8' }}>Available From:</span>
                                            <span>
                                                {paginatedRows[0]?.available_from ? new Date(paginatedRows[0].available_from).toLocaleString() : 'N/A'}
                                            </span>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', fontWeight: '700', color: '#E11D48' }}>
                                            <i className="fa-solid fa-calendar-xmark" />
                                            <span style={{ color: '#94A3B8' }}>Available Until:</span>
                                            <span>
                                                {paginatedRows[0]?.available_until ? new Date(paginatedRows[0].available_until).toLocaleString() : 'N/A'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div style={{ 
                                    background: 'white', padding: '1.5rem 2.5rem', borderRadius: '24px', 
                                    boxShadow: '0 4px 20px rgba(0,0,0,0.05)', textAlign: 'center',
                                    border: '1px solid #F1F5F9'
                                }}>
                                    <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Submissions</div>
                                    <div style={{ fontSize: '2.5rem', fontWeight: '900', color: '#4F46E5' }}>{currentRows.length}</div>
                                </div>
                            </div>
                        </div>
                    )}
                </header>

                {viewMode === 'overview' && (
                    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                        <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <div style={{ width: '4px', height: '24px', background: '#4F46E5', borderRadius: '2px' }} />
                            <h2 style={{ fontSize: '1.4rem', fontWeight: '800', margin: 0, color: '#1E293B' }}>Candidate Performance</h2>
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
                                                    {activeTab === 'assessment' && (
                                                        <input type="checkbox" checked={allSelected} onChange={toggleSelectAll} />
                                                    )}
                                                </th>
                                                <th>Candidate Info</th>
                                                <th>Result Data</th>
                                                <th>Date</th>
                                                <th>AI Status</th>
                                                {(activeTab === 'assessment' || activeTab === 'interview') && <th>Action</th>}
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
                                                            {activeTab === 'assessment' && (
                                                                <input type="checkbox" checked={isSelected} onChange={() => toggleSelect(r._deleteKey)} />
                                                            )}
                                                        </td>
                                                        <td>
                                                            <div style={{ fontWeight: '800', color: (r.full_name === 'Extraction Failed' || r.candidate?.name === 'Extraction Failed') ? '#EE5D50' : 'inherit' }}>
                                                                {r.full_name || r.candidate?.name || 'Extraction Failed'}
                                                            </div>
                                                            <div style={{ fontSize: '0.8rem', color: (r.email === 'Extraction Failed' || r.candidate?.email === 'Extraction Failed') ? '#EE5D50' : '#64748b' }}>
                                                                {r.email || r.candidate?.email || 'Extraction Failed'}
                                                            </div>
                                                        </td>
                                                        <td>
                                                            {activeTab === 'resume' ? `${r.resume_score || 0}% Match` :
                                                                activeTab === 'assessment' ? `${r.percentage ?? 0}% (${r.score || 0}/${r.total_possible || r.total || r.total_questions || 0})` :
                                                                    `${r.score != null ? Math.round(r.score) : 0}% Evaluation`}
                                                        </td>
                                                        <td>
                                                            <div style={{ fontWeight: '500', color: '#1E293B' }}>
                                                                {new Date(r.created_at || r.submitted_at || r.completed_at).toLocaleDateString()}
                                                            </div>
                                                            <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '0.2rem' }}>
                                                                {new Date(r.created_at || r.submitted_at || r.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                            </div>
                                                        </td>
                                                        <td>
                                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'space-between' }}>
                                                                <span style={{ padding: '0.3rem 0.6rem', borderRadius: '6px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>
                                                                    {getStatusLabel(r.status)}
                                                                </span>
                                                                {activeTab === 'assessment' && (
                                                                    <button 
                                                                        onClick={(e) => { e.stopPropagation(); requestDelete([r]); }}
                                                                        style={{ background: 'none', border: 'none', color: '#EE5D50', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center', transition: 'all 0.2s', opacity: 0.6 }}
                                                                        title="Delete Result"
                                                                    >
                                                                        <i className="fa-solid fa-trash-can" style={{ fontSize: '0.9rem' }}></i>
                                                                    </button>
                                                                )}
                                                            </div>
                                                        </td>
                                                        {(activeTab === 'assessment' || activeTab === 'interview') && (
                                                            <td>
                                                                {activeTab === 'assessment' ? (
                                                                    <button 
                                                                        onClick={(e) => { e.stopPropagation(); setSearchParams({ ...Object.fromEntries(searchParams), subId: r.id || r.candidate_id }); }}
                                                                        className="view-details-btn"
                                                                        style={{ 
                                                                            padding: '0.6rem 1.4rem', borderRadius: '12px', border: 'none',
                                                                            background: 'linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)',
                                                                            color: 'white', fontWeight: '700', fontSize: '0.85rem',
                                                                            cursor: 'pointer', boxShadow: '0 4px 12px rgba(79, 70, 229, 0.25)',
                                                                            transition: 'all 0.2s'
                                                                        }}
                                                                    >
                                                                        View Details
                                                                    </button>
                                                                ) : (
                                                                    <button 
                                                                        onClick={(e) => { e.stopPropagation(); setSummaryModal(r); }}
                                                                        className="view-details-btn"
                                                                        style={{ 
                                                                            padding: '0.6rem 1.4rem', borderRadius: '12px', border: 'none',
                                                                            background: 'linear-gradient(135deg, #05CD99 0%, #04b082 100%)',
                                                                            color: 'white', fontWeight: '700', fontSize: '0.85rem',
                                                                            cursor: 'pointer', boxShadow: '0 4px 12px rgba(5, 205, 153, 0.25)',
                                                                            transition: 'all 0.2s'
                                                                        }}
                                                                    >
                                                                        Transcript
                                                                    </button>
                                                                )}
                                                            </td>
                                                        )}
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