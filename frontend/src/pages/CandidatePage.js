import React, { useEffect, useMemo, useState, useCallback } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import '../styles/CandidatePage.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

function fmtDate(iso) {
    if (!iso) return '-';
    try {
        return new Date(iso).toLocaleString();
    } catch {
        return iso;
    }
}

export default function CandidatePage() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [items, setItems] = useState([]);
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [fromDate, setFromDate] = useState('');
    const [toDate, setToDate] = useState('');
    const [page, setPage] = useState(1);
    const pageSize = 10;

    const load = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const params = {};
            if (fromDate) params.start_date = fromDate;
            if (toDate) params.end_date = toDate;
            const resp = await axios.get(`${API_BASE_URL}/candidates/`, { params });
            setItems(resp.data?.results || []);
        } catch (e) {
            setError(e?.response?.data?.error || e?.message || 'Failed to load candidates');
        } finally {
            setLoading(false);
        }
    }, [fromDate, toDate]);

    useEffect(() => {
        load();
    }, [load]);

    const filtered = useMemo(() => {
        let list = items;

        // Unified Search (Name/Email/Assessment)
        const q = search.trim().toLowerCase();
        if (q) {
            list = list.filter((c) => {
                const name = (c.name || '').toLowerCase();
                const email = (c.email || '').toLowerCase();
                const assess = (c.assessment?.display_name || c.assessment?.name || '').toLowerCase();
                return name.includes(q) || email.includes(q) || assess.includes(q);
            });
        }

        // Filter by Status
        if (statusFilter) {
            list = list.filter((c) => {
                const isCompleted = !!c.submitted_at;
                const status = isCompleted ? 'completed' : (c.status || '').toLowerCase();
                return status === statusFilter.toLowerCase();
            });
        }

        return list;
    }, [items, search, statusFilter]);

    useEffect(() => {
        setPage(1);
    }, [search, statusFilter]);

    const totalPages = useMemo(() => Math.max(1, Math.ceil(filtered.length / pageSize)), [filtered.length]);
    const currentPage = Math.min(page, totalPages);
    const pageItems = useMemo(() => {
        const start = (currentPage - 1) * pageSize;
        return filtered.slice(start, start + pageSize);
    }, [filtered, currentPage]);

    const pageButtons = useMemo(() => {
        // show up to 5 numbers around current page
        const maxButtons = 5;
        const half = Math.floor(maxButtons / 2);
        let start = Math.max(1, currentPage - half);
        let end = Math.min(totalPages, start + maxButtons - 1);
        start = Math.max(1, end - maxButtons + 1);
        const nums = [];
        for (let i = start; i <= end; i += 1) nums.push(i);
        return nums;
    }, [currentPage, totalPages]);

    return (
        <div className="cand-page">
            <Header />
            <div className="cand-shell">
                <div className="cand-top">
                    <div>
                        <div className="cand-title">Candidates</div>
                        <div className="cand-sub">All candidates you invited </div>
                    </div>
                    <button className="btn-secondary" type="button" onClick={load}>Refresh</button>
                </div>

                <div className="cand-toolbar" style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                    <input
                        className="cand-search"
                        style={{ flex: '1 1 300px', height: '40px' }}
                        placeholder="Search by name / email / assessment"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                    <select
                        className="cand-search"
                        style={{ flex: '0 0 150px', height: '40px', padding: '0 12px', borderRadius: '8px', border: '1px solid #e5e7eb' }}
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="">All Statuses</option>
                        <option value="completed">Completed</option>
                        <option value="sent">Sent</option>
                    </select>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '14px', color: '#64748b' }}>From:</span>
                        <input
                            type="date"
                            className="cand-search"
                            style={{ width: 'auto', height: '40px' }}
                            value={fromDate}
                            onChange={(e) => setFromDate(e.target.value)}
                        />
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '14px', color: '#64748b' }}>To:</span>
                        <input
                            type="date"
                            className="cand-search"
                            style={{ width: 'auto', height: '40px' }}
                            value={toDate}
                            onChange={(e) => setToDate(e.target.value)}
                        />
                    </div>
                </div>

                {loading ? (
                    <div className="card">Loading…</div>
                ) : error ? (
                    <div className="card error">
                        <div className="cand-title">Couldn’t load candidates</div>
                        <div className="cand-sub">{error}</div>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="card">No candidates found.</div>
                ) : (
                    <div className="table-card">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Candidate</th>
                                    <th>Assessment</th>
                                    <th>Status</th>
                                    <th>Started</th>
                                    <th>Submitted</th>
                                    <th>Rating</th>
                                    <th>Report</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pageItems.map((c) => (
                                    <tr key={c.id}>
                                        <td>
                                            <div className="cell-title">{c.name || '-'}</div>
                                            <div className="cell-sub">{c.email || '-'}</div>
                                        </td>
                                        <td>{c.assessment?.display_name || c.assessment?.name || '-'}</td>
                                        <td>
                                            <span className={`pill ${c.submitted_at ? 'ok' : 'bad'}`}>
                                                {c.submitted_at ? 'Completed' : (c.status || 'Pending')}
                                            </span>
                                        </td>
                                        <td>{fmtDate(c.started_at)}</td>
                                        <td>{fmtDate(c.submitted_at)}</td>
                                        <td>{c.rating ?? '-'}</td>
                                        <td>
                                            {c.submission_id ? (
                                                <button
                                                    className="report-download-btn"
                                                    type="button"
                                                    title="Download full candidate report"
                                                    onClick={() => {
                                                        const url = `${API_BASE_URL}/results/${c.submission_id}/report/`;
                                                        window.open(url, '_blank');
                                                    }}
                                                >
                                                    ⬇ Download
                                                </button>
                                            ) : (
                                                <span className="cell-sub">-</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        <div className="pager">
                            <div className="pager-left">
                                Showing {(filtered.length === 0) ? 0 : ((currentPage - 1) * pageSize + 1)}-
                                {Math.min(currentPage * pageSize, filtered.length)} of {filtered.length}
                            </div>

                            <div className="pager-right">
                                <button
                                    className="pager-btn"
                                    type="button"
                                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                                    disabled={currentPage <= 1}
                                >
                                    ‹
                                </button>

                                {pageButtons[0] > 1 ? (
                                    <>
                                        <button className={`pager-num ${currentPage === 1 ? 'active' : ''}`} type="button" onClick={() => setPage(1)}>1</button>
                                        {pageButtons[0] > 2 ? <span className="pager-dots">…</span> : null}
                                    </>
                                ) : null}

                                {pageButtons.map((n) => (
                                    <button
                                        key={n}
                                        className={`pager-num ${currentPage === n ? 'active' : ''}`}
                                        type="button"
                                        onClick={() => setPage(n)}
                                    >
                                        {n}
                                    </button>
                                ))}

                                {pageButtons[pageButtons.length - 1] < totalPages ? (
                                    <>
                                        {pageButtons[pageButtons.length - 1] < totalPages - 1 ? <span className="pager-dots">…</span> : null}
                                        <button
                                            className={`pager-num ${currentPage === totalPages ? 'active' : ''}`}
                                            type="button"
                                            onClick={() => setPage(totalPages)}
                                        >
                                            {totalPages}
                                        </button>
                                    </>
                                ) : null}

                                <button
                                    className="pager-btn"
                                    type="button"
                                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                                    disabled={currentPage >= totalPages}
                                >
                                    ›
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}



