import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Download, Trash2 } from 'lucide-react';
import Header from '../components/Header';
import '../styles/Result.css';
import { API_BASE_URL } from '../apiConfig';

function fmtPercent(v) {
    const n = Number(v);
    if (Number.isNaN(n)) return '0%';
    return `${n.toFixed(1)}%`;
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

    const load = useCallback(async () => {
        setLoading(true);
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
            setError(e?.response?.data?.error || e?.message || 'Failed to load');
        } finally {
            setLoading(false);
        }
    }, [isOverview, token, fromDate, toDate]);

    const downloadCSV = () => {
        if (!filtered || filtered.length === 0) {
            alert("No data available to download.");
            return;
        }

        // Format: name,email,pan_number,phone
        const headers = ["name", "email", "pan_number", "phone"];
        const rows = filtered.map(r => [
            r.candidate?.name || "",
            r.candidate?.email || "",
            r.candidate?.pan_number || "",
            r.candidate?.phone || ""
        ]);

        const csvString = [
            headers.join(","),
            ...rows.map(row => row.map(v => `"${String(v).replace(/"/g, '""')}"`).join(","))
        ].join("\n");

        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `results_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    useEffect(() => {
        load();
    }, [load]);

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
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button className="btn-secondary" type="button" onClick={load}>Refresh</button>
                        <button className="btn-secondary" type="button" onClick={() => navigate('/assessments')}>Back to Assessments</button>
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
                    <button className="btn-secondary" type="button" onClick={downloadCSV} title="Download CSV" style={{ display: 'flex', alignItems: 'center', gap: '6px', whiteSpace: 'nowrap', flexShrink: 0, height: '42px', padding: '0 1rem' }}>
                        <Download size={16} /> .csv
                    </button>
                </div>

                {loading ? (
                    <div className="card">Loading results…</div>
                ) : error ? (
                    <div className="card error">
                        <div className="title">Couldn’t load results</div>
                        <div className="sub">{error}</div>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="card">No results found yet. Submit an assessment once and it will appear here.</div>
                ) : (
                    <div className="table-card">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Candidate</th>
                                    <th>Details</th>
                                    <th>Submitted</th>
                                    <th>Objective</th>
                                    <th>Coding</th>
                                    <th>Final Score</th>
                                    <th>Integrity Score</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map((r) => (
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
                                            <span className={`pill ${r.status === 'selected' || r.status === 'COMPLETED' ? 'ok' : r.status === 'sent' ? 'info' : r.status === 'not_attempted' ? 'neutral' : 'bad'}`}>
                                                {r.status === 'selected' || r.status === 'COMPLETED' ? 'Qualified' : r.status === 'rejected' ? 'Not Qualified' : r.status === 'sent' ? 'Sent' : r.status === 'not_attempted' ? 'Not Attempted' : r.status}
                                            </span>
                                        </td>
                                        <td style={{ display: 'flex', gap: '8px' }}>
                                            {r.submission_id ? (
                                                <button
                                                    className="btn-report-dl"
                                                    title="Download Report"
                                                    onClick={async () => {
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
                                                <div style={{ width: '32px' }}></div>
                                            )}
                                            {r.delete_requested ? (
                                                <div 
                                                    style={{ 
                                                        display: 'flex', alignItems: 'center', justifyContent: 'center', 
                                                        width: '36px', height: '36px', background: '#fffbeb', 
                                                        borderRadius: '8px', border: '1px solid #fde68a', cursor: 'not-allowed'
                                                    }} 
                                                    title="Deletion Pending Approval"
                                                >
                                                    ⏳
                                                </div>
                                            ) : (
                                                <button
                                                    className="btn-action-delete"
                                                    title={JSON.parse(localStorage.getItem('user'))?.role === 'company_admin' ? 'Delete' : 'Request Delete'}
                                                onClick={async () => {
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
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}