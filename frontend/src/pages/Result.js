import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Download, Trash2, TableProperties, UserCheck, UserX, Loader2 } from 'lucide-react';
import Header from '../components/Header';
import '../styles/Result.css';
import { API_BASE_URL } from '../apiConfig';

function fmtPercent(v) {
    const n = Number(v);
    if (Number.isNaN(n)) return '0%';
    return `${n.toFixed(1)}%`;
}

function hasValue(v) {
    return v !== null && v !== undefined && String(v).trim() !== '';
}

function getStatusMeta(status, r = {}) {
    const isZero = Number(r.percentage || 0) === 0 && (status === 'rejected' || status === 'hold' || status === 'HOLD');

    if (status === 'terminated') {
        return {
            label: 'Terminated',
            className: 'bad',
            subtitle: r.termination_detail || r.termination_reason || '',
            isTerminated: true,
        };
    }
    if (status === 'selected' || status === 'COMPLETED') {
        return { label: 'Qualified', className: 'ok' };
    }
    if (status === 'rejected' || isZero) {
        return { label: 'Not Qualified', className: 'bad' };
    }
    if (status === 'hold' || status === 'HOLD') {
        return { label: 'Hold', className: 'warning' };
    }
    if (status === 'sent') {
        return { label: 'Sent', className: 'info' };
    }
    if (status === 'not_attempted') {
        return { label: 'Not Attempted', className: 'neutral' };
    }
    if (status === 'pending') {
        return { label: 'Pending', className: 'neutral' };
    }
    return { label: status || '-', className: 'neutral' };
}

function getSortValue(row, key) {
    if (key === 'candidate') return (row.candidate?.name || '').toLowerCase();
    if (key === 'details') return (row.assessment?.display_name || row.assessment?.name || '').toLowerCase();
    if (key === 'sent') return row.created_at ? new Date(row.created_at).getTime() : 0;
    if (key === 'submitted') return row.submitted_at ? new Date(row.submitted_at).getTime() : 0;
    if (key === 'objective') return Number(row.objective_percentage) || 0;
    if (key === 'coding') return Number(row.coding_percentage) || 0;
    if (key === 'final') return Number(row.percentage) || 0;
    if (key === 'integrity') return Number(row.integrity?.integrity_score) || 0;
    if (key === 'status') return (row.status || '').toLowerCase();
    return '';
}

export default function Result() {
    const navigate = useNavigate();
    const location = useLocation();
    const { token } = useParams();

    const isOverview = !token;

    // Check if this was an auto-submit due to timeout
    const wasAutoSubmit = location.state?.autoSubmit === true;
    const [showTimeoutPopup, setShowTimeoutPopup] = useState(wasAutoSubmit);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const [overview, setOverview] = useState([]);
    const [candidateResult, setCandidateResult] = useState(null);
    const [rating, setRating] = useState(0);
    const [feedback, setFeedback] = useState('');
    const [savingRating, setSavingRating] = useState(false);
    const [ratingSaved, setRatingSaved] = useState(false);

    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [fromDate, setFromDate] = useState('');
    const [toDate, setToDate] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [segment, setSegment] = useState('all');
    const [sortConfig, setSortConfig] = useState({ key: 'submitted', direction: 'desc' });
    const [quickViewRow, setQuickViewRow] = useState(null);
    const [isShowingLogs, setIsShowingLogs] = useState(false);
    const [reviewPopup, setReviewPopup] = useState({ show: false, submissionId: null, status: '', candidateName: '' });
    const [downloadingIds, setDownloadingIds] = useState(new Set());
    const [qualReasonPopup, setQualReasonPopup] = useState({ show: false, submissionId: null, status: '', candidateName: '', reason: '', submitting: false });

    // Derive user role from localStorage
    const currentUser = (() => { try { return JSON.parse(localStorage.getItem('user') || '{}'); } catch { return {}; } })();
    const currentRole = (currentUser?.role || '').toLowerCase();
    const isAdmin = currentRole === 'company_admin' || currentRole === 'application_admin';

    useEffect(() => {
        if (isOverview) return;
        if (!ratingSaved) return;
        const timer = setTimeout(() => {
            try {
                window.close();
            } catch (err) {
                // ignore if close is blocked
            }
        }, 800);
        return () => clearTimeout(timer);
    }, [isOverview, ratingSaved]);

    const handleUpdateResult = (submission, newStatus) => {
        if (isAdmin) {
            // Admin: show the existing review-report popup (direct update after report review)
            setReviewPopup({
                show: true,
                submissionId: submission.submission_id,
                status: newStatus,
                candidateName: submission.candidate?.name || 'this candidate'
            });
        } else {
            // HR / HR Manager: show reason modal → creates a pending approval request
            setQualReasonPopup({
                show: true,
                submissionId: submission.submission_id,
                status: newStatus,
                candidateName: submission.candidate?.name || 'this candidate',
                reason: '',
                submitting: false
            });
        }
    };

    // Admin path: direct update (called from the review-report popup)
    const confirmUpdateResult = async () => {
        const { submissionId, status } = reviewPopup;
        try {
            const resp = await axios.post(`${API_BASE_URL}/results/${submissionId}/update-result/`, { result: status });
            if (resp.data?.pending) {
                alert(resp.data.message);
                setOverview(prev => prev.map(r => r.submission_id === submissionId ? { ...r, qual_pending: true } : r));
            } else {
                alert(resp.data.message || 'Status updated.');
                setOverview(prev => prev.map(r => r.submission_id === submissionId ? { ...r, status } : r));
            }
            setReviewPopup({ show: false, submissionId: null, status: '', candidateName: '' });
        } catch (err) {
            alert(err.response?.data?.error || 'Failed to update result.');
        }
    };

    // HR/HRM path: submit qualification request with reason
    const submitQualRequest = async () => {
        const { submissionId, status, reason } = qualReasonPopup;
        if (!reason.trim()) { alert('Please provide a reason for this qualification change.'); return; }
        setQualReasonPopup(prev => ({ ...prev, submitting: true }));
        try {
            const resp = await axios.post(`${API_BASE_URL}/results/${submissionId}/update-result/`, { result: status, reason: reason.trim() });
            alert(resp.data.message);
            // Mark the row as pending locally so user sees feedback immediately
            setOverview(prev => prev.map(r => r.submission_id === submissionId ? { ...r, qual_pending: true } : r));
            setQualReasonPopup({ show: false, submissionId: null, status: '', candidateName: '', reason: '', submitting: false });
        } catch (err) {
            alert(err.response?.data?.error || 'Failed to submit request.');
            setQualReasonPopup(prev => ({ ...prev, submitting: false }));
        }
    };

    const handleDownloadReport = async (submissionId, candidateName) => {
        if (downloadingIds.has(submissionId)) return;
        
        setDownloadingIds(prev => new Set(prev).add(submissionId));
        const url = `${API_BASE_URL}/results/${submissionId}/report/`;
        try {
            const resp = await axios.get(url, { responseType: 'blob' });
            const blob = new Blob([resp.data], { type: 'application/pdf' });
            const durl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = durl;
            link.setAttribute('download', `Report_${candidateName || submissionId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(durl);
        } catch (err) {
            alert("Failed to download report.");
        } finally {
            setDownloadingIds(prev => {
                const next = new Set(prev);
                next.delete(submissionId);
                return next;
            });
        }
    };

    const filtered = useMemo(() => {
        let list = overview;

        // Unified Search (Name/Email/Assessment)
        const q = search.trim().toLowerCase();
        if (q) {
            list = list.filter((r) => {
                const name = (r.candidate?.name || '').toLowerCase();
                const email = (r.candidate?.email || '').toLowerCase();
                const assess = (r.assessment?.display_name || r.assessment?.name || '').toLowerCase();
                return name.includes(q) || email.includes(q) || assess.includes(q);
            });
        }

        // Status Filter
        if (statusFilter) {
            list = list.filter((r) => {
                if (statusFilter === 'selected') {
                    return r.status === 'selected' || r.status === 'COMPLETED';
                }
                if (statusFilter === 'rejected') {
                    return r.status === 'rejected' || (Number(r.percentage || 0) === 0 && (r.status === 'hold' || r.status === 'HOLD'));
                }
                if (statusFilter === 'hold') {
                    return (r.status === 'hold' || r.status === 'HOLD') && Number(r.percentage || 0) !== 0;
                }
                return r.status === statusFilter;
            });
        }

        return list;
    }, [overview, search, statusFilter]);

    const overviewMetrics = useMemo(() => {
        const total = filtered.length;
        const qualified = filtered.filter((r) => r.status === 'selected' || r.status === 'COMPLETED').length;
        const notQualified = filtered.filter((r) => r.status === 'rejected' || (Number(r.percentage || 0) === 0 && (r.status === 'hold' || r.status === 'HOLD'))).length;
        const hold = filtered.filter((r) => (r.status === 'hold' || r.status === 'HOLD') && Number(r.percentage || 0) !== 0).length;
        const attempted = filtered.filter((r) => r.status !== 'not_attempted' && r.status !== 'sent').length;
        return { total, qualified, notQualified, hold, attempted };
    }, [filtered]);

    const segmentedResults = useMemo(() => {
        if (segment === 'qualified') return filtered.filter((r) => r.status === 'selected' || r.status === 'COMPLETED');
        if (segment === 'not_qualified') return filtered.filter((r) => r.status === 'rejected' || (Number(r.percentage || 0) === 0 && (r.status === 'hold' || r.status === 'HOLD')));
        if (segment === 'hold') return filtered.filter((r) => (r.status === 'hold' || r.status === 'HOLD') && Number(r.percentage || 0) !== 0);
        if (segment === 'not_attempted') return filtered.filter((r) => r.status === 'not_attempted');
        return filtered;
    }, [filtered, segment]);

    const analytics = useMemo(() => {
        const dataset = filtered;
        const explainability = [];

        dataset.forEach((r) => {
            const score = Number(r.percentage) || 0;
            const integrity = Number(r.integrity?.integrity_score) || 0;
            const status = r.status;

            if (status === 'rejected' || status === 'hold' || status === 'HOLD') {
                const reasons = [];
                if (score < 50) reasons.push('Low final score');
                if (integrity < 60) reasons.push('Integrity concerns');
                if ((Number(r.objective_percentage) || 0) < 45) reasons.push('Low objective performance');
                if ((Number(r.coding_percentage) || 0) < 45) reasons.push('Low coding performance');
                explainability.push({
                    id: r.submission_id || r.invitation_id,
                    reason: reasons.length > 0 ? reasons.join(', ') : 'Did not meet qualification threshold',
                });
            }
        });
        return { explainability };
    }, [filtered]);

    const sortedResults = useMemo(() => {
        const cloned = [...segmentedResults];
        cloned.sort((a, b) => {
            const av = getSortValue(a, sortConfig.key);
            const bv = getSortValue(b, sortConfig.key);
            if (av < bv) return sortConfig.direction === 'asc' ? -1 : 1;
            if (av > bv) return sortConfig.direction === 'asc' ? 1 : -1;
            return 0;
        });
        return cloned;
    }, [segmentedResults, sortConfig]);

    const pageSize = Number(rowsPerPage) || 10;
    const totalPages = Math.max(1, Math.ceil(sortedResults.length / pageSize));
    const paginatedResults = useMemo(() => {
        const start = (currentPage - 1) * pageSize;
        return sortedResults.slice(start, start + pageSize);
    }, [sortedResults, currentPage, pageSize]);

    const paginationPages = useMemo(() => {
        const pages = [];
        const start = Math.max(1, currentPage - 2);
        const end = Math.min(totalPages, start + 4);
        for (let p = start; p <= end; p += 1) pages.push(p);
        return pages;
    }, [currentPage, totalPages]);

    useEffect(() => {
        setCurrentPage(1);
    }, [search, statusFilter, fromDate, toDate, segment, rowsPerPage]);

    useEffect(() => {
        if (currentPage > totalPages) {
            setCurrentPage(totalPages);
        }
    }, [currentPage, totalPages]);

    const handleSort = (key) => {
        setSortConfig((prev) => {
            if (prev.key === key) {
                return { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
            }
            return { key, direction: 'asc' };
        });
    };

    const sortMarker = (key) => {
        if (sortConfig.key !== key) return '↕';
        return sortConfig.direction === 'asc' ? '↑' : '↓';
    };

    const fetchActivityLogsForRow = useCallback(async (row) => {
        if (!row?.invitation_id) return Array.isArray(row?.activity_logs) ? row.activity_logs : [];
        try {
            const resp = await axios.get(
                `${API_BASE_URL}/invitations/${row.invitation_id}/activity-logs/`,
                { params: { _t: Date.now() } }
            );
            return resp.data?.activity_logs || [];
        } catch (err) {
            console.warn('Failed to fetch activity logs:', err?.message);
            return Array.isArray(row?.activity_logs) ? row.activity_logs : [];
        }
    }, []);

    const handleToggleActivityLogs = async () => {
        if (isShowingLogs) {
            setIsShowingLogs(false);
            return;
        }
        if (quickViewRow?.invitation_id) {
            const logs = await fetchActivityLogsForRow(quickViewRow);
            setQuickViewRow((prev) => (prev ? { ...prev, activity_logs: logs } : prev));
        }
        setIsShowingLogs(true);
    };

    const load = useCallback(async (silentArg = false) => {
        const silent = silentArg === true;
        if (!silent) setLoading(true);
        setError('');
        try {
            if (isOverview) {
                const params = {
                    _t: Date.now() // Prevent caching
                };
                if (fromDate) params.start_date = fromDate;
                if (toDate) params.end_date = toDate;
                const resp = await axios.get(`${API_BASE_URL}/results/`, { params });
                // Filter out AI results — those belong in ResultsAI.js only
                const allResults = resp.data?.results || [];
                const manualOnly = allResults.filter(r => {
                    const sid = String(r.submission_id || '');
                    return !sid.startsWith('ai_') && !sid.startsWith('aicand_');
                });
                setOverview(manualOnly);
            } else {
                // Candidate view: validate submission exists but do NOT show score/selected/rejected.
                const resp = await axios.get(`${API_BASE_URL}/invitations/public/${token}/result/`);
                const data = resp.data || null;
                setCandidateResult(data);

                // If a rating already exists, lock the form and show the stored values.
                const existingRating = data?.result?.rating;
                if (existingRating) {
                    setRating(existingRating);
                    setFeedback(data?.result?.feedback || '');
                    setRatingSaved(true);
                }
            }
        } catch (e) {
            if (!silent) setError(e?.response?.data?.error || e?.message || 'Failed to load');
        } finally {
            if (!silent) setLoading(false);
        }
    }, [isOverview, token, fromDate, toDate]);

    const downloadCSV = () => {
        const data = filtered;
        if (data.length === 0) {
            alert("No data to download.");
            return;
        }

        const headers = ["name", "email", "pan_number", "phone"];
        const rows = data.map(r => [
            r.candidate?.name || "",
            r.candidate?.email || "",
            r.candidate?.pan_number || "",
            r.candidate?.phone || ""
        ]);

        const csvContent = [
            headers.join(","),
            ...rows.map(row => row.map(v => `"${String(v).replace(/"/g, '""')}"`).join(","))
        ].join("\n");

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "candidate_results.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    useEffect(() => {
        load();
    }, [load]);

    // Auto-refresh when viewing logs to show near-instant updates
    useEffect(() => {
        if (!isOverview || !isShowingLogs || !quickViewRow) return;

        const pollTimer = setInterval(() => {
            load(true);
        }, 2000); // Poll every 2 seconds for near-instant log display

        return () => clearInterval(pollTimer);
    }, [isOverview, isShowingLogs, quickViewRow, load]);

    // Sync quickViewRow with the latest data from overview when it refreshes
    useEffect(() => {
        if (!quickViewRow) return;
        const updatedRow = overview.find(r => 
            (r.invitation_id && r.invitation_id === quickViewRow.invitation_id) || 
            (r.id && r.id === quickViewRow.id)
        );
        if (updatedRow && JSON.stringify(updatedRow.activity_logs) !== JSON.stringify(quickViewRow.activity_logs)) {
            setQuickViewRow(updatedRow);
        }
    }, [overview, quickViewRow]);

    if (!isOverview) {
        return (
            <div className="result-page">
                {/* Timeout Auto-Submit Popup */}
                {showTimeoutPopup && (
                    <div className="timeout-popup-overlay">
                        <div className="timeout-popup">
                            <div className="timeout-popup-icon">⏰</div>
                            <div className="timeout-popup-title">Time's Up!</div>
                            <div className="timeout-popup-message">
                                Your assessment has been automatically submitted because the time limit was reached.
                                All your answers (including any unsubmitted coding questions) have been saved and submitted.
                            </div>
                            <button
                                className="timeout-popup-btn"
                                type="button"
                                onClick={() => setShowTimeoutPopup(false)}
                            >
                                OK, Got it
                            </button>
                        </div>
                    </div>
                )}
                <div className="result-shell">
                    {loading ? (
                        <div className="card">Loading result…</div>
                    ) : error ? (
                        <div className="card error">
                            <div className="title">Assessment not submitted</div>
                            <div className="sub">{error}</div>
                            <div style={{ marginTop: 12 }}>
                                <button className="btn-secondary" type="button" onClick={() => navigate(`/take-assessment/${token}`)}>
                                    Go to Assessment
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="card">
                            <div className="title">Thank you</div>
                            <div className="sub">
                                Your assessment has been submitted successfully.
                            </div>
                            <div className="sub" style={{ marginTop: 10 }}>
                                You can close this window now.
                            </div>

                            {/* Keep the assessment name visible, but hide pass/fail and score */}
                            <div className="badge ok" style={{ marginTop: 14 }}>
                                {candidateResult?.assessment?.display_name || candidateResult?.assessment?.name || 'Assessment'}
                            </div>

                            {/* Rating (optional) */}
                            <div className="rating-wrap">
                                <div className="rating-title">Rate your experience</div>
                                {ratingSaved && (
                                    <div className="sub" style={{ marginBottom: 8 }}>
                                        You already submitted your rating and feedback for this assessment.
                                    </div>
                                )}
                                <div className="stars" role="radiogroup" aria-label="Rating">
                                    {[1, 2, 3, 4, 5].map((n) => (
                                        <button
                                            key={n}
                                            type="button"
                                            className={`star ${rating >= n ? 'on' : ''}`}
                                            onClick={() => setRating(n)}
                                            disabled={savingRating || ratingSaved}
                                            aria-label={`${n} star`}
                                        >
                                            ★
                                        </button>
                                    ))}
                                </div>
                                <textarea
                                    className="feedback"
                                    placeholder="Optional feedback"
                                    value={feedback}
                                    onChange={(e) => setFeedback(e.target.value)}
                                    disabled={savingRating || ratingSaved}
                                />
                                <div className="rating-actions">
                                    <button
                                        className="btn-secondary"
                                        type="button"
                                        disabled={savingRating || ratingSaved || rating < 1}
                                        onClick={async () => {
                                            if (!token) return;
                                            if (rating < 1) return;
                                            setSavingRating(true);
                                            try {
                                                await axios.post(`${API_BASE_URL}/invitations/public/${token}/rating/`, {
                                                    rating,
                                                    feedback,
                                                });
                                                setRatingSaved(true);
                                            } catch (e) {
                                                alert(e?.response?.data?.error || e?.message || 'Failed to save rating');
                                            } finally {
                                                setSavingRating(false);
                                            }
                                        }}
                                    >
                                        {ratingSaved ? 'Thanks!' : (savingRating ? 'Saving…' : 'Submit Rating')}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // Recruiter overview
    return (
        <div className="result-page">
            <Header />
            <div className="result-shell">
                <div className="top">
                    <div>
                        <div className="title">Results Overview</div>
                        <div className="sub">Latest submitted assessments (auto-checked).</div>
                    </div>
                    <div className="top-actions">
                        <button className="btn-top-primary" type="button" onClick={() => load()}>Refresh</button>
                        <button className="btn-top-secondary" type="button" onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
                    </div>
                </div>

                <div className="toolbar">
                    <input
                        className="search search-input"
                        placeholder="Search by name / email / assessment"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                    <select
                        className="search search-select"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="">All Statuses</option>
                        <option value="sent">Sent</option>
                        <option value="selected">Qualified</option>
                        <option value="rejected">Not Qualified</option>
                        <option value="hold">Hold</option>
                        <option value="not_attempted">Not Attempted</option>
                    </select>
                    <div className="date-filter">
                        <span>From:</span>
                        <input
                            type="date"
                            className="search search-date"
                            value={fromDate}
                            onChange={(e) => setFromDate(e.target.value)}
                        />
                    </div>
                    <div className="date-filter">
                        <span>To:</span>
                        <input
                            type="date"
                            className="search search-date"
                            value={toDate}
                            onChange={(e) => setToDate(e.target.value)}
                        />
                    </div>
                    <button className="search" type="button" onClick={downloadCSV} title="Download CSV" style={{ display: 'flex', alignItems: 'center', gap: '4px', whiteSpace: 'nowrap', flexShrink: 0, cursor: 'pointer', fontWeight: '700', color: '#64748b' }}>
                        <Download size={14} /> .csv
                    </button>
                </div>

                <div className="metrics-grid">
                    <div className="metric-card">
                        <div className="metric-label">Total Results</div>
                        <div className="metric-value">{overviewMetrics.total}</div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-label">Qualified</div>
                        <div className="metric-value success">{overviewMetrics.qualified}</div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-label">Not Qualified</div>
                        <div className="metric-value danger">{overviewMetrics.notQualified}</div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-label">Hold</div>
                        <div className="metric-value" style={{ color: '#92400e' }}>{overviewMetrics.hold}</div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-label">Attempted</div>
                        <div className="metric-value">{overviewMetrics.attempted}</div>
                    </div>
                </div>



                {loading ? (
                    <div className="card skeleton-wrap">
                        <div className="skeleton-line w40"></div>
                        <div className="skeleton-line w65"></div>
                        <div className="skeleton-table">
                            {Array.from({ length: 6 }).map((_, idx) => (
                                <div key={idx} className="skeleton-row"></div>
                            ))}
                        </div>
                    </div>
                ) : error ? (
                    <div className="card error">
                        <div className="title">Couldn’t load results</div>
                        <div className="sub">{error}</div>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="card">No results found yet. Submit an assessment once and it will appear here.</div>
                ) : (
                    <>
                        <div className="table-card">
                            <table className="table">
                                <thead>
                                    <tr>
                                        <th onClick={() => handleSort('candidate')} className="sortable-th">Candidate {sortMarker('candidate')}</th>
                                        <th onClick={() => handleSort('details')} className="sortable-th">Details {sortMarker('details')}</th>
                                        <th onClick={() => handleSort('sent')} className="sortable-th">Sent {sortMarker('sent')}</th>
                                        <th onClick={() => handleSort('submitted')} className="sortable-th">Submitted {sortMarker('submitted')}</th>
                                        <th onClick={() => handleSort('objective')} className="sortable-th">Objective {sortMarker('objective')}</th>
                                        <th onClick={() => handleSort('coding')} className="sortable-th">Coding {sortMarker('coding')}</th>
                                        <th onClick={() => handleSort('final')} className="sortable-th">Final Score {sortMarker('final')}</th>
                                        <th onClick={() => handleSort('integrity')} className="sortable-th">Integrity Score {sortMarker('integrity')}</th>
                                        <th onClick={() => handleSort('status')} className="sortable-th">Status {sortMarker('status')}</th>
                                        <th className="center-col">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {paginatedResults.map((r) => {
                                        const statusMeta = getStatusMeta(r.status, r);
                                        return (
                                            <tr key={r.submission_id || `inv_${r.invitation_id}`}>
                                                <td>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                                        <div>
                                                            <div className="cell-title">{r.candidate?.name || '-'}</div>
                                                            <div className="cell-sub">{r.candidate?.email || '-'}</div>
                                                        </div>
                                                        {statusMeta.isTerminated ? (
                                                            <span title="Exam terminated" style={{ flexShrink: 0, width: 26, height: 26, borderRadius: '50%', background: '#dc2626', color: '#fff', fontWeight: 800, fontSize: '0.8rem', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', border: '2px solid #fecaca' }}>T</span>
                                                        ) : null}
                                                    </div>
                                                </td>
                                                <td>{r.assessment?.display_name || r.assessment?.name || '-'}</td>
                                                <td>
                                                    <div className="cell-title">{r.created_at ? new Date(r.created_at).toLocaleDateString() : '-'}</div>
                                                    <div className="cell-sub">{r.created_at ? new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</div>
                                                </td>
                                                <td>
                                                    <div className="cell-title">{(r.status === 'pending' || !r.submitted_at) ? '-' : new Date(r.submitted_at).toLocaleDateString()}</div>
                                                    <div className="cell-sub">{(r.status === 'pending' || !r.submitted_at) ? '' : new Date(r.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                                                </td>
                                                <td>
                                                    <div className="cell-title">{r.objective_score} / {r.objective_total}</div>
                                                    <div className="cell-sub">{fmtPercent(r.objective_percentage)}</div>
                                                    {r.assessment?.weightage_objective !== undefined && r.assessment.weightage_objective !== 50 && (
                                                        <div className="cell-sub" style={{ fontSize: '0.75em', color: '#6b7280' }}>Weight: {r.assessment.weightage_objective}%</div>
                                                    )}
                                                </td>
                                                <td>
                                                    <div className="cell-title">{r.coding_score} / {r.coding_total}</div>
                                                    <div className="cell-sub">{fmtPercent(r.coding_percentage)}</div>
                                                    {r.assessment?.weightage_coding !== undefined && r.assessment.weightage_coding !== 50 && (
                                                        <div className="cell-sub" style={{ fontSize: '0.75em', color: '#6b7280' }}>Weight: {r.assessment.weightage_coding}%</div>
                                                    )}
                                                </td>
                                                <td>
                                                    <div className="cell-title" style={{ fontWeight: 'bold' }}>{fmtPercent(r.percentage)}</div>
                                                    <div className="cell-sub">Weighted</div>
                                                    <div className="progress-track">
                                                        <div className="progress-fill" style={{ width: `${Math.max(0, Math.min(100, Number(r.percentage) || 0))}%` }} />
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="cell-title" style={{ fontWeight: 'bold' }}>
                                                        {r.integrity?.integrity_score !== undefined && r.integrity?.integrity_score !== null ? `${r.integrity.integrity_score}%` : '-'}
                                                    </div>
                                                    {r.integrity?.warning_logs?.length > 0 && (
                                                        <div className="cell-sub" style={{ color: '#ef4444' }}>
                                                            {r.integrity.warning_logs.length} Warnings
                                                        </div>
                                                    )}
                                                </td>
                                                <td>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                        <span className={`pill ${statusMeta.className}`} style={statusMeta.isTerminated ? { background: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca' } : undefined}>
                                                            <span className="pill-dot" />
                                                            {statusMeta.label}
                                                        </span>
                                                        {r.qual_pending && (
                                                            <span title="Qualification change pending admin approval" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.72rem', fontWeight: '700', background: '#fffbeb', color: '#d97706', border: '1px solid #fde68a', borderRadius: '999px', padding: '2px 8px' }}>
                                                                ⏳ Pending Approval
                                                            </span>
                                                        )}
                                                        {!r.qual_pending && (r.status === 'hold' || r.status === 'HOLD') && r.submission_id && (
                                                            <div className="status-actions" style={{ display: 'flex', gap: '4px' }}>
                                                                <button 
                                                                    onClick={() => handleUpdateResult(r, 'selected')}
                                                                    title="Mark as Qualified"
                                                                    style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#10b981', padding: 0 }}
                                                                >
                                                                    <UserCheck size={18} />
                                                                </button>
                                                                <button 
                                                                    onClick={() => handleUpdateResult(r, 'rejected')}
                                                                    title="Mark as Not Qualified"
                                                                    style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#ef4444', padding: 0 }}
                                                                >
                                                                    <UserX size={18} />
                                                                </button>
                                                            </div>
                                                        )}
                                                    </div>
                                                </td>
                                                <td className="center-col">
                                                    <div className="action-buttons">
                                                        <button
                                                            className="btn-report-dl"
                                                            title="Quick View"
                                                            onClick={() => setQuickViewRow(r)}
                                                        >
                                                            <TableProperties size={16} />
                                                        </button>
                                                        {r.submission_id ? (
                                                            <button
                                                                className="btn-report-dl"
                                                                title={r.status === 'pending' ? "Report unavailable while pending" : "Download Report"}
                                                                disabled={r.status === 'pending' || downloadingIds.has(r.submission_id)}
                                                                style={{ 
                                                                    opacity: (r.status === 'pending' || downloadingIds.has(r.submission_id)) ? 0.5 : 1,
                                                                    cursor: (r.status === 'pending' || downloadingIds.has(r.submission_id)) ? 'not-allowed' : 'pointer',
                                                                    transition: 'transform 0.1s ease',
                                                                }}
                                                                onMouseDown={(e) => {
                                                                    if (r.status !== 'pending' && !downloadingIds.has(r.submission_id)) {
                                                                        e.currentTarget.style.transform = 'scale(0.9)';
                                                                    }
                                                                }}
                                                                onMouseUp={(e) => {
                                                                    e.currentTarget.style.transform = 'scale(1)';
                                                                }}
                                                                onMouseLeave={(e) => {
                                                                    e.currentTarget.style.transform = 'scale(1)';
                                                                }}
                                                                onClick={() => {
                                                                    if (r.status === 'pending' || downloadingIds.has(r.submission_id)) return;
                                                                    handleDownloadReport(r.submission_id, r.candidate?.name);
                                                                }}
                                                            >
                                                                {downloadingIds.has(r.submission_id) ? (
                                                                    <Loader2 size={18} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                                                                ) : (
                                                                    <Download size={18} />
                                                                )}
                                                            </button>
                                                        ) : (
                                                            <div style={{ width: '31px' }}></div>
                                                        )}
                                                        {r.delete_requested ? (
                                                            <div className="delete-pending" title="Deletion Pending Approval">⏳</div>
                                                        ) : (
                                                            <button
                                                                className="btn-action-delete"
                                                                title={r.status === 'pending' ? "Cannot delete pending assessment" : (JSON.parse(localStorage.getItem('user'))?.role === 'company_admin' ? 'Delete' : 'Request Delete')}
                                                                disabled={r.status === 'pending'}
                                                                style={{ 
                                                                    opacity: r.status === 'pending' ? 0.5 : 1,
                                                                    cursor: r.status === 'pending' ? 'not-allowed' : 'pointer'
                                                                }}
                                                                onClick={async () => {
                                                                    if (r.status === 'pending') return;
                                                                    const role = JSON.parse(localStorage.getItem('user'))?.role;
                                                                    const isAdmin = role === 'company_admin' || role === 'application_admin';

                                                                    const delId = r.submission_id;
                                                                    if (!delId) {
                                                                        alert("Cannot delete a pending invitation from this view yet.");
                                                                        return;
                                                                    }

                                                                    const isAI = String(delId).startsWith('ai_');
                                                                    const realId = isAI ? String(delId).replace('ai_', '') : delId;
                                                                    const endpoint = isAI ? `${API_BASE_URL}/ai-assessments/submission/${realId}/` : `${API_BASE_URL}/submissions/${realId}/`;

                                                                    if (isAdmin) {
                                                                        if (window.confirm("CRITICAL: Once you delete, you cannot restore. Proceed?")) {
                                                                            try {
                                                                                await axios.delete(endpoint, {
                                                                                    data: { confirm_permanent_delete: true }
                                                                                });
                                                                                alert("Deleted successfully.");
                                                                                load();
                                                                            } catch (err) {
                                                                                console.error("Delete Error:", err.response || err);
                                                                                alert("Failed to delete. " + (err.response?.data?.error || err.message));
                                                                            }
                                                                        }
                                                                    } else {
                                                                        const reason = prompt("Enter reason for deletion request:");
                                                                        if (reason) {
                                                                            try {
                                                                                await axios.delete(endpoint, {
                                                                                    data: { reason }
                                                                                });
                                                                                alert("Deletion request sent.");
                                                                                load();
                                                                            } catch (err) {
                                                                                alert(err.response?.data?.error || "Failed to request deletion.");
                                                                            }
                                                                        }
                                                                    }
                                                                }}
                                                            >
                                                                <Trash2 size={18} />
                                                            </button>
                                                        )}
                                                    </div>
                                                </td>
                                            </tr>
                                        )
                                    })}
                                </tbody>
                            </table>
                        </div>
                        <div className="pagination-wrap">
                            <div className="pagination-summary">
                                Showing {sortedResults.length === 0 ? 0 : ((currentPage - 1) * pageSize) + 1}-
                                {Math.min(currentPage * pageSize, sortedResults.length)} of {sortedResults.length}
                            </div>
                            <div className="pagination-controls">
                                <select
                                    className="search pagination-size"
                                    value={rowsPerPage}
                                    onChange={(e) => setRowsPerPage(Number(e.target.value))}
                                >
                                    <option value={10}>10 / page</option>
                                    <option value={25}>25 / page</option>
                                    <option value={50}>50 / page</option>
                                </select>
                                <button
                                    type="button"
                                    className="pagination-btn"
                                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                                    disabled={currentPage === 1}
                                >
                                    Prev
                                </button>
                                {paginationPages.map((page) => (
                                    <button
                                        key={page}
                                        type="button"
                                        className={`pagination-btn ${currentPage === page ? 'active' : ''}`}
                                        onClick={() => setCurrentPage(page)}
                                    >
                                        {page}
                                    </button>
                                ))}
                                <button
                                    type="button"
                                    className="pagination-btn"
                                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                                    disabled={currentPage === totalPages}
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>

            {quickViewRow && (
                <div className="quickview-overlay" onClick={() => setQuickViewRow(null)}>
                    <div className="quickview-panel" onClick={(e) => e.stopPropagation()}>
                        <div className="quickview-head">
                            <h3>{isShowingLogs ? 'Activity Logs' : 'Candidate Data Details'}</h3>
                            <button type="button" className="quickview-close" onClick={() => { setQuickViewRow(null); setIsShowingLogs(false); }}>✕</button>
                        </div>
                        <div className="quickview-subhead">
                            <strong>{quickViewRow.candidate?.name || quickViewRow.full_name || 'Candidate'}</strong>
                            <span>{quickViewRow.candidate?.email || quickViewRow.email || 'No email'}</span>
                        </div>
                        
                        {isShowingLogs ? (
                            <div className="quickview-logs" style={{ padding: '0 24px', flex: 1, overflowY: 'auto' }}>
                                {quickViewRow.status === 'terminated' && (quickViewRow.termination_detail || quickViewRow.termination_reason) ? (
                                    <div style={{ marginBottom: 16, padding: '14px 16px', borderRadius: 8, background: '#fef2f2', border: '1px solid #fecaca' }}>
                                        <div style={{ fontWeight: 700, color: '#b91c1c', marginBottom: 6, fontSize: '0.9rem' }}>Exam terminated</div>
                                        <div style={{ color: '#991b1b', fontSize: '0.88rem', lineHeight: 1.45 }}>{quickViewRow.termination_detail || quickViewRow.termination_reason}</div>
                                    </div>
                                ) : null}

                                {quickViewRow.activity_logs && quickViewRow.activity_logs.length > 0 ? (
                                    <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                                        {[...quickViewRow.activity_logs].reverse().map((log, i) => {
                                            const isBlocked = log.action?.toLowerCase().includes('blocked');
                                            const isPassed = log.action?.toLowerCase().includes('passed') || log.action?.toLowerCase().includes('submitted');
                                            const isViolation = log.action?.toLowerCase().includes('violation') || log.action?.toLowerCase().includes('alert');
                                            const isTerminated = log.action?.toLowerCase().includes('terminated');
                                            const isTerminalClose = log.action?.toLowerCase().includes('terminal closed');
                                            const isUsb = log.action?.toLowerCase().includes('usb');
                                            const isStarted = log.action?.toLowerCase().includes('started') && !isTerminated;
                                            
                                            let icon = '🔵';
                                            let bgColor = '#f8fafc';
                                            let textColor = '#1e293b';
                                            let borderColor = '#e2e8f0';

                                            if (isTerminated) {
                                                icon = '🛑';
                                                bgColor = '#fef2f2';
                                                textColor = '#991b1b';
                                                borderColor = '#fecaca';
                                            } else if (isBlocked || isViolation) {
                                                icon = '⚠️';
                                                bgColor = '#fef2f2';
                                                textColor = '#991b1b';
                                                borderColor = '#fecaca';
                                            } else if (isTerminalClose || isUsb) {
                                                icon = '🔌';
                                                bgColor = '#fffbeb';
                                                textColor = '#92400e';
                                                borderColor = '#fde68a';
                                            } else if (isPassed || isStarted) {
                                                icon = '✅';
                                                bgColor = '#f0fdf4';
                                                textColor = '#166534';
                                                borderColor = '#bbf7d0';
                                            } else if (log.action === 'Opened Link') {
                                                icon = '🔗';
                                            }

                                            return (
                                                <li key={i} style={{ 
                                                    padding: '14px', 
                                                    marginBottom: '12px',
                                                    borderRadius: '8px',
                                                    background: bgColor,
                                                    border: `1px solid ${borderColor}`,
                                                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                                                }}>
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                                                        <span style={{ fontSize: '11px', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.025em' }}>
                                                            {new Date(log.timestamp).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                                                        </span>
                                                        <span style={{ fontSize: '16px' }}>{icon}</span>
                                                    </div>
                                                    <strong style={{ display: 'block', color: textColor, fontSize: '14px' }}>{log.action}</strong>
                                                    {log.termination_label ? (
                                                        <div style={{ fontSize: '12px', color: '#b91c1c', fontWeight: 600, marginTop: 4 }}>Reason: {log.termination_label}</div>
                                                    ) : null}
                                                    {log.details && (
                                                        <div style={{ 
                                                            fontSize: '13px', 
                                                            color: isTerminated || isBlocked || isViolation ? '#b91c1c' : '#475569', 
                                                            marginTop: '6px',
                                                            paddingTop: '6px',
                                                            borderTop: `1px dashed ${borderColor}`
                                                        }}>
                                                            {log.details}
                                                        </div>
                                                    )}
                                                </li>
                                            );
                                        })}
                                    </ul>
                                ) : (
                                    <div style={{ padding: '40px 0', color: '#64748b', textAlign: 'center' }}>
                                        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📋</div>
                                        <div style={{ fontWeight: '500' }}>No activity logs found for this candidate.</div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="quickview-grid">
                                {[
                                    { label: 'ID: Submission ID', value: quickViewRow.submission_id },
                                    { label: 'ID: Invitation ID', value: quickViewRow.invitation_id },
                                    { label: 'ID: Candidate ID', value: quickViewRow.candidate?.id || quickViewRow.candidate_id },
                                    { label: 'Workflow: Raw Status', value: quickViewRow.status },
                                    { label: 'Workflow: Delete Requested', value: quickViewRow.delete_requested ? 'Yes' : 'No' },
                                    { label: 'Workflow: Report Available', value: quickViewRow.submission_id ? 'Yes' : 'No' },
                                    { label: 'Scoring: Objective Weightage', value: hasValue(quickViewRow.assessment?.weightage_objective) ? `${quickViewRow.assessment.weightage_objective}%` : null },
                                    { label: 'Scoring: Coding Weightage', value: hasValue(quickViewRow.assessment?.weightage_coding) ? `${quickViewRow.assessment.weightage_coding}%` : null },
                                    { label: 'Scoring: Objective Marks Missing', value: hasValue(quickViewRow.objective_total) && hasValue(quickViewRow.objective_score) ? `${Math.max(0, Number(quickViewRow.objective_total) - Number(quickViewRow.objective_score))}` : null },
                                    { label: 'Scoring: Coding Marks Missing', value: hasValue(quickViewRow.coding_total) && hasValue(quickViewRow.coding_score) ? `${Math.max(0, Number(quickViewRow.coding_total) - Number(quickViewRow.coding_score))}` : null },
                                    { label: 'Integrity: Warnings Count', value: quickViewRow.integrity?.warning_logs?.length ? `${quickViewRow.integrity.warning_logs.length}` : '0' },
                                    {
                                        label: 'Integrity: Warning Types', value: Array.isArray(quickViewRow.integrity?.warning_logs) && quickViewRow.integrity.warning_logs.length > 0
                                            ? [...new Set(quickViewRow.integrity.warning_logs.map((w) => w?.event_type || w?.type).filter(Boolean))].join(', ')
                                            : null
                                    },
                                    { label: 'Meta: Created At', value: quickViewRow.created_at ? new Date(quickViewRow.created_at).toLocaleString() : null },
                                    { label: 'Meta: Updated At', value: quickViewRow.updated_at ? new Date(quickViewRow.updated_at).toLocaleString() : null },
                                ]
                                    .filter((item) => hasValue(item.value))
                                    .map((item) => (
                                        <div key={item.label}>
                                            <span>{item.label}</span>
                                            <strong>{item.value}</strong>
                                        </div>
                                    ))}
                            </div>
                        )}
                        <div className="quickview-footer" style={{ display: 'flex', justifyContent: 'space-between', padding: '16px 24px', borderTop: '1px solid #e2e8f0' }}>
                            <button 
                                type="button" 
                                className="quickview-close-btn" 
                                style={{ 
                                    background: '#eff6ff', 
                                    color: '#1d4ed8', 
                                    border: '1px solid #bfdbfe',
                                    fontWeight: '600',
                                    padding: '8px 16px',
                                    borderRadius: '6px'
                                }} 
                                onClick={handleToggleActivityLogs}
                            >
                                {isShowingLogs ? '📊 View Data Details' : '📋 View Activity Logs'}
                            </button>
                            <button 
                                type="button" 
                                className="quickview-close-btn" 
                                style={{ 
                                    background: '#fee2e2', 
                                    color: '#b91c1c', 
                                    border: '2px solid #ef4444',
                                    fontWeight: '700',
                                    padding: '8px 24px',
                                    borderRadius: '6px',
                                    textTransform: 'uppercase',
                                    fontSize: '13px'
                                }}
                                onClick={() => { setQuickViewRow(null); setIsShowingLogs(false); }}
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
            {reviewPopup.show && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
                    backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center',
                    alignItems: 'center', zIndex: 2000, backdropFilter: 'blur(4px)'
                }}>
                    <div style={{
                        backgroundColor: '#fff', padding: '32px', borderRadius: '16px',
                        maxWidth: '450px', width: '90%', textAlign: 'center', 
                        boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
                        border: '1px solid #e5e7eb'
                    }}>
                        <div style={{ 
                            width: '56px', height: '56px', backgroundColor: '#fef3c7', 
                            borderRadius: '50%', display: 'flex', alignItems: 'center', 
                            justifyContent: 'center', margin: '0 auto 20px', color: '#d97706'
                        }}>
                            <TableProperties size={28} />
                        </div>
                        <h3 style={{ marginBottom: '12px', color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>Review Candidate Report</h3>
                        <p style={{ marginBottom: '24px', color: '#4b5563', lineHeight: '1.6', fontSize: '0.95rem' }}>
                            Please review the candidate report before marking <strong>{reviewPopup.candidateName}</strong> as <strong>{reviewPopup.status === 'selected' ? 'Qualified' : 'Not Qualified'}</strong>.
                        </p>
                        
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            <button
                                onClick={() => handleDownloadReport(reviewPopup.submissionId, reviewPopup.candidateName)}
                                disabled={downloadingIds.has(reviewPopup.submissionId)}
                                style={{
                                    backgroundColor: downloadingIds.has(reviewPopup.submissionId) ? '#9ca3af' : '#4f46e5', 
                                    color: '#fff', border: 'none',
                                    padding: '14px', borderRadius: '10px', 
                                    cursor: downloadingIds.has(reviewPopup.submissionId) ? 'not-allowed' : 'pointer',
                                    fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                                    boxShadow: '0 4px 6px -1px rgba(79, 70, 229, 0.2)',
                                    transition: 'all 0.1s ease',
                                }}
                                onMouseDown={(e) => {
                                    if (!downloadingIds.has(reviewPopup.submissionId)) {
                                        e.currentTarget.style.transform = 'scale(0.96)';
                                    }
                                }}
                                onMouseUp={(e) => {
                                    e.currentTarget.style.transform = 'scale(1)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'scale(1)';
                                }}
                            >
                                {downloadingIds.has(reviewPopup.submissionId) ? (
                                    <>
                                        <Loader2 size={20} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} /> 
                                        Downloading...
                                    </>
                                ) : (
                                    <>
                                        <Download size={20} /> Download Report
                                    </>
                                )}
                            </button>
                            
                            <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
                                <button
                                    onClick={() => setReviewPopup({ ...reviewPopup, show: false })}
                                    style={{
                                        flex: 1, backgroundColor: '#fff', color: '#374151',
                                        border: '1px solid #d1d5db', padding: '12px', borderRadius: '10px', cursor: 'pointer', fontWeight: '600'
                                    }}
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={confirmUpdateResult}
                                    style={{
                                        flex: 1, backgroundColor: reviewPopup.status === 'selected' ? '#059669' : '#dc2626',
                                        color: '#fff', border: 'none', padding: '12px', borderRadius: '10px', cursor: 'pointer', fontWeight: '600',
                                        boxShadow: reviewPopup.status === 'selected' ? '0 4px 6px -1px rgba(5, 150, 105, 0.2)' : '0 4px 6px -1px rgba(220, 38, 38, 0.2)'
                                    }}
                                >
                                    Confirm Update
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* ── HR/HRM Qualification Request Reason Modal ─────────────── */}
            {qualReasonPopup.show && (
                <div style={{
                    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999
                }}>
                    <div style={{
                        background: '#fff', borderRadius: '18px', padding: '36px',
                        width: '100%', maxWidth: '460px', boxShadow: '0 25px 60px rgba(0,0,0,0.25)'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                            <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: '800', color: '#111827' }}>
                                Request Qualification Change
                            </h3>
                            <button onClick={() => setQualReasonPopup({ show: false, submissionId: null, status: '', candidateName: '', reason: '', submitting: false })}
                                style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.3rem', color: '#9ca3af' }}>✕</button>
                        </div>

                        <p style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '20px', lineHeight: 1.5 }}>
                            You are requesting to mark <strong style={{ color: '#111827' }}>{qualReasonPopup.candidateName}</strong> as{' '}
                            <strong style={{ color: qualReasonPopup.status === 'selected' ? '#059669' : '#dc2626' }}>
                                {qualReasonPopup.status === 'selected' ? '✅ Qualified' : '❌ Not Qualified'}
                            </strong>.
                            This requires admin approval. Please provide a reason below.
                        </p>

                        <div style={{ background: '#f9fafb', borderRadius: '10px', padding: '12px 16px', marginBottom: '12px', border: '1px solid #e5e7eb' }}>
                            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', color: '#374151', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                Reason <span style={{ color: '#ef4444' }}>*</span>
                            </label>
                            <textarea
                                value={qualReasonPopup.reason}
                                onChange={e => setQualReasonPopup(prev => ({ ...prev, reason: e.target.value }))}
                                placeholder="Explain why this candidate should be marked as Qualified / Not Qualified..."
                                rows={4}
                                style={{
                                    width: '100%', border: 'none', background: 'transparent', outline: 'none',
                                    resize: 'vertical', fontSize: '0.9rem', color: '#111827', fontFamily: 'inherit', boxSizing: 'border-box'
                                }}
                            />
                        </div>

                        <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
                            <button
                                onClick={() => setQualReasonPopup({ show: false, submissionId: null, status: '', candidateName: '', reason: '', submitting: false })}
                                style={{ flex: 1, background: '#fff', color: '#374151', border: '1px solid #d1d5db', padding: '12px', borderRadius: '10px', cursor: 'pointer', fontWeight: '600' }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={submitQualRequest}
                                disabled={qualReasonPopup.submitting || !qualReasonPopup.reason.trim()}
                                style={{
                                    flex: 1,
                                    background: qualReasonPopup.submitting || !qualReasonPopup.reason.trim()
                                        ? '#9ca3af'
                                        : (qualReasonPopup.status === 'selected' ? '#059669' : '#dc2626'),
                                    color: '#fff', border: 'none', padding: '12px', borderRadius: '10px',
                                    cursor: qualReasonPopup.submitting || !qualReasonPopup.reason.trim() ? 'not-allowed' : 'pointer',
                                    fontWeight: '700', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'
                                }}
                            >
                                {qualReasonPopup.submitting ? '⏳ Submitting...' : '📨 Submit for Approval'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
