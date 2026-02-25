import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import '../styles/Result.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

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
    const [activeTab, setActiveTab] = useState('assessment'); // 'assessment' or 'interview'

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
            list = list.filter((r) => r.status === statusFilter);
        }

        // Category (Tab) Filter
        list = list.filter((r) => {
            if (activeTab === 'interview') {
                return r.submission_id && r.submission_id.startsWith('interview_');
            } else {
                return r.submission_id && !r.submission_id.startsWith('interview_');
            }
        });

        return list;
    }, [overview, search, statusFilter, activeTab]);

    const load = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            if (isOverview) {
                const params = {};
                if (fromDate) params.start_date = fromDate;
                if (toDate) params.end_date = toDate;
                const resp = await axios.get(`${API_BASE_URL}/results/`, { params });
                const allResults = resp.data?.results || [];
                // Filter out AI assessments (they have their own results page)
                setOverview(allResults.filter(r => !r.submission_id?.startsWith('ai_')));
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

    useEffect(() => {
        load();
    }, [load]);

    const handleDelete = async (submissionId) => {
        if (!window.confirm("Are you sure you want to delete this interview record? This action cannot be undone.")) {
            return;
        }

        try {
            setLoading(true);
            // Extract ID from "interview_123"
            const dbId = submissionId.replace('interview_', '');
            await axios.delete(`${API_BASE_URL}/ai-candidates/${dbId}/`);
            // Refresh list
            await load();
        } catch (e) {
            console.error("Delete failed", e);
            setError(e?.response?.data?.error || "Failed to delete record");
            setLoading(false); // Only stop loading on error, success will reload
        }
    };

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

                <div className="tab-switcher" style={{ display: 'flex', gap: '20px', marginBottom: '20px', borderBottom: '2px solid #edf2f7', paddingBottom: '10px' }}>
                    <button
                        onClick={() => setActiveTab('assessment')}
                        style={{
                            background: 'none',
                            border: 'none',
                            fontSize: '1.1rem',
                            fontWeight: activeTab === 'assessment' ? 'bold' : 'normal',
                            color: activeTab === 'assessment' ? '#667eea' : '#718096',
                            borderBottom: activeTab === 'assessment' ? '2px solid #667eea' : 'none',
                            padding: '5px 15px',
                            cursor: 'pointer',
                            marginBottom: '-12px'
                        }}
                    >
                        AI Assessments
                    </button>
                    <button
                        onClick={() => setActiveTab('interview')}
                        style={{
                            background: 'none',
                            border: 'none',
                            fontSize: '1.1rem',
                            fontWeight: activeTab === 'interview' ? 'bold' : 'normal',
                            color: activeTab === 'interview' ? '#667eea' : '#718096',
                            borderBottom: activeTab === 'interview' ? '2px solid #667eea' : 'none',
                            padding: '5px 15px',
                            cursor: 'pointer',
                            marginBottom: '-12px'
                        }}
                    >
                        AI Interview
                    </button>
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
                        <option value="selected">Qualified</option>
                        <option value="rejected">Not Qualified</option>
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
                                    <th>Assessment</th>
                                    <th>Date</th>
                                    <th>Score</th>
                                    <th>Percentage</th>
                                    <th>Integrity</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map((r) => (
                                    <tr key={r.submission_id}>
                                        <td>
                                            <div className="cell-title">{r.candidate?.name || '-'}</div>
                                            <div className="cell-sub">{r.candidate?.email || '-'}</div>
                                        </td>
                                        <td>{r.assessment?.display_name || r.assessment?.name || '-'}</td>
                                        <td>
                                            <div className="cell-title">{r.submitted_at ? new Date(r.submitted_at).toLocaleDateString() : '-'}</div>
                                            <div className="cell-sub">{r.submitted_at ? new Date(r.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</div>
                                        </td>
                                        <td>{r.score} / {r.total}</td>
                                        <td>{fmtPercent(r.percentage)}</td>
                                        <td>
                                            {r.integrity !== undefined && r.integrity !== null ? (
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                    <div style={{
                                                        width: '8px', height: '8px', borderRadius: '50%',
                                                        backgroundColor: r.integrity >= 70 ? '#10b981' : '#ef4444'
                                                    }} />
                                                    <span style={{ fontWeight: '600', color: r.integrity >= 70 ? '#10b981' : '#ef4444' }}>
                                                        {r.integrity}%
                                                    </span>
                                                </div>
                                            ) : (
                                                <span style={{ color: '#9ca3af', fontSize: '0.85rem' }}>-</span>
                                            )}
                                        </td>
                                        <td>
                                            <span className={`pill ${r.status === 'selected' ? 'ok' : 'bad'}`}>
                                                {r.status === 'selected' ? 'Qualified' : 'Not Qualified'}
                                            </span>
                                        </td>
                                        <td>
                                            {r.submission_id && r.submission_id.startsWith('interview_') && (
                                                <button
                                                    className="btn-icon delete"
                                                    title="Delete Record"
                                                    onClick={(e) => { e.stopPropagation(); handleDelete(r.submission_id); }}
                                                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#e53e3e' }}
                                                >
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                        <polyline points="3 6 5 6 21 6"></polyline>
                                                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                                        <line x1="10" y1="11" x2="10" y2="17"></line>
                                                        <line x1="14" y1="11" x2="14" y2="17"></line>
                                                    </svg>
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



