import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Download, Trash2, TableProperties } from 'lucide-react';
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

function getStatusMeta(status) {
    if (status === 'selected' || status === 'COMPLETED') {
        return { label: 'Qualified', className: 'ok' };
    }
    if (status === 'rejected') {
        return { label: 'Not Qualified', className: 'bad' };
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
                return r.status === statusFilter;
            });
        }

        return list;
    }, [overview, search, statusFilter]);

    const overviewMetrics = useMemo(() => {
        const total = filtered.length;
        const qualified = filtered.filter((r) => r.status === 'selected' || r.status === 'COMPLETED').length;
        const notQualified = filtered.filter((r) => r.status === 'rejected').length;
        const attempted = filtered.filter((r) => r.status !== 'not_attempted' && r.status !== 'sent').length;
        return { total, qualified, notQualified, attempted };
    }, [filtered]);

    const segmentedResults = useMemo(() => {
        if (segment === 'qualified') return filtered.filter((r) => r.status === 'selected' || r.status === 'COMPLETED');
        if (segment === 'not_qualified') return filtered.filter((r) => r.status === 'rejected');
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

            if (status === 'rejected') {
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

    const load = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);
        setError('');
        try {
            if (isOverview) {
                const params = {};
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

    // Auto-refresh when viewing logs to show "instant" updates
    useEffect(() => {
        if (!isOverview || !isShowingLogs || !quickViewRow) return;

        const pollTimer = setInterval(() => {
            load(true);
        }, 5000); // Poll every 5 seconds

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
                        <button className="btn-top-primary" type="button" onClick={load}>Refresh</button>
                        <button className="btn-top-secondary" type="button" onClick={() => navigate('/assessments')}>Back to Assessments</button>
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
                                        const statusMeta = getStatusMeta(r.status);
                                        return (
                                            <tr key={r.submission_id || `inv_${r.invitation_id}`}>
                                                <td>
                                                    <div className="cell-title">{r.candidate?.name || '-'}</div>
                                                    <div className="cell-sub">{r.candidate?.email || '-'}</div>
                                                </td>
                                                <td>{r.assessment?.display_name || r.assessment?.name || '-'}</td>
                                                <td>
                                                    <div className="cell-title">{r.submitted_at ? new Date(r.submitted_at).toLocaleDateString() : '-'}</div>
                                                    <div className="cell-sub">{r.submitted_at ? new Date(r.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</div>
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
                                                    <span className={`pill ${statusMeta.className}`}>
                                                        <span className="pill-dot" />
                                                        {statusMeta.label}
                                                    </span>
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
                                                                disabled={r.status === 'pending'}
                                                                style={{ 
                                                                    opacity: r.status === 'pending' ? 0.5 : 1,
                                                                    cursor: r.status === 'pending' ? 'not-allowed' : 'pointer'
                                                                }}
                                                                onClick={async () => {
                                                                    if (r.status === 'pending') return;
                                                                    const url = `${API_BASE_URL}/results/${r.submission_id}/report/`;
                                                                    try {
                                                                        const resp = await axios.get(url, { responseType: 'blob' });
                                                                        const blob = new Blob([resp.data], { type: 'application/pdf' });
                                                                        const durl = window.URL.createObjectURL(blob);
                                                                        const link = document.createElement('a');
                                                                        link.href = durl;
                                                                        link.setAttribute('download', `Report_${r.candidate?.name || r.submission_id}.pdf`);
                                                                        document.body.appendChild(link);
                                                                        link.click();
                                                                        link.remove();
                                                                        window.URL.revokeObjectURL(durl);
                                                                    } catch (err) {
                                                                        alert("Failed to download report.");
                                                                    }
                                                                }}
                                                            >
                                                                <Download size={18} />
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
                                {quickViewRow.activity_logs && quickViewRow.activity_logs.length > 0 ? (
                                    <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                                        {quickViewRow.activity_logs.map((log, i) => {
                                            const isBlocked = log.action?.toLowerCase().includes('blocked');
                                            const isPassed = log.action?.toLowerCase().includes('passed') || log.action?.toLowerCase().includes('submitted');
                                            const isViolation = log.action?.toLowerCase().includes('violation') || log.action?.toLowerCase().includes('alert');
                                            
                                            let icon = '🔵';
                                            let bgColor = '#f8fafc';
                                            let textColor = '#1e293b';
                                            let borderColor = '#e2e8f0';

                                            if (isBlocked || isViolation) {
                                                icon = '⚠️';
                                                bgColor = '#fef2f2';
                                                textColor = '#991b1b';
                                                borderColor = '#fecaca';
                                            } else if (isPassed) {
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
                                                    {log.details && (
                                                        <div style={{ 
                                                            fontSize: '13px', 
                                                            color: isBlocked || isViolation ? '#b91c1c' : '#475569', 
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
                                onClick={() => setIsShowingLogs(!isShowingLogs)}
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
        </div>
    );
}