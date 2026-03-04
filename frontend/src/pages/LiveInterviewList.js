import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/LiveInterviewList.css';
import { API_BASE_URL } from '../apiConfig';

function fmtDate(iso) {
  if (!iso) return '-';
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function fmtDateOnly(iso) {
  if (!iso) return '-';
  try {
    return new Date(iso).toLocaleDateString();
  } catch {
    return iso;
  }
}

function fmtTime(iso) {
  if (!iso) return '-';
  try {
    return new Date(iso).toLocaleTimeString();
  } catch {
    return iso;
  }
}

export default function LiveInterviewList() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await axios.get(`${API_BASE_URL}/interviews/invitations/`);
      setItems(resp.data?.results || []);
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to load interview candidates');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return items;
    return items.filter((inv) => {
      const name = (inv.name || '').toLowerCase();
      const email = (inv.email || '').toLowerCase();
      const interviewName = (inv.interview?.name || '').toLowerCase();
      return name.includes(q) || email.includes(q) || interviewName.includes(q);
    });
  }, [items, search]);

  useEffect(() => {
    // reset page when search changes
    setPage(1);
  }, [search]);

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

  const getStatusClass = (status) => {
    switch (status) {
      case 'sent':
        return 'ok';
      case 'accepted':
        return 'ok';
      case 'completed':
        return 'ok';
      case 'submitted':
        return 'ok';
      case 'failed':
        return 'bad';
      default:
        return 'bad';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'draft':
        return 'Draft';
      case 'sent':
        return 'Invited';
      case 'accepted':
        return 'Accepted';
      case 'completed':
        return 'Completed';
      case 'submitted':
        return 'Submitted';
      case 'failed':
        return 'Failed';
      default:
        return status || 'Pending';
    }
  };

  const renderStars = (rating) => {
    const r = parseFloat(rating || 0);
    return (
      <div className="list-rating-stars">
        {[1, 2, 3, 4, 5].map((star) => (
          <i
            key={star}
            className={`${star <= Math.round(r) ? 'fas' : 'far'} fa-star`}
            style={{ color: star <= Math.round(r) ? '#f59e0b' : '#cbd5e1', fontSize: '12px', marginRight: '2px' }}
          ></i>
        ))}
        <span style={{ marginLeft: '4px', fontSize: '12px', fontWeight: 600, color: '#475569' }}>
          {r > 0 ? r.toFixed(1) : '-'}
        </span>
      </div>
    );
  };

  const handleStartInterview = (token) => {
    navigate(`/live-interview-interviewer?token=${token}`);
  };

  return (
    <div className="live-interview-list-page">
      <div className="live-interview-list-shell">
        <div className="live-interview-list-top">
          <div>
            <div className="live-interview-list-title">Live Interview Candidates</div>
            <div className="live-interview-list-sub">All candidates invited for live interviews</div>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn-secondary" type="button" onClick={() => navigate('/dashboard')}>
              Back
            </button>
            <button className="btn-secondary" type="button" onClick={load}>
              Refresh
            </button>
          </div>
        </div>

        <div className="live-interview-list-toolbar">
          <input
            className="live-interview-list-search"
            placeholder="Search by name / email / interview"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="card">Loading…</div>
        ) : error ? (
          <div className="card error">
            <div className="live-interview-list-title">Couldn't load interview candidates</div>
            <div className="live-interview-list-sub">{error}</div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="card">No interview candidates found.</div>
        ) : (
          <div className="table-card">
            <table className="table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Interviewer</th>
                  <th>Interview</th>
                  <th>Status</th>
                  <th>Rating</th>
                  <th>Scheduled Start</th>
                  <th>Scheduled End</th>
                  <th>Created</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((inv) => (
                  <tr key={inv.id}>
                    <td>
                      <div className="cell-title">{inv.name || '-'}</div>
                      <div className="cell-sub">{inv.email || '-'}</div>
                      {inv.phone && <div className="cell-sub" style={{ fontSize: '12px', color: '#64748b' }}>{inv.phone}</div>}
                    </td>
                    <td>
                      <div className="cell-title">{inv.interviewer_name || '-'}</div>
                      <div className="cell-sub">{inv.interviewer_email || '-'}</div>
                    </td>
                    <td>{inv.interview?.name || '-'}</td>
                    <td>
                      <span className={`pill ${getStatusClass(inv.status)}`}>
                        {getStatusLabel(inv.status)}
                      </span>
                    </td>
                    <td>
                      {inv.feedback ? (
                        <div>
                          {renderStars(inv.feedback.interviewer_average_rating || inv.feedback.interviewer_rating)}
                          <button
                            className="btn-secondary"
                            style={{ padding: '2px 8px', fontSize: '12px', marginTop: '4px' }}
                            onClick={() => navigate('/feedback-details', { state: { inv } })}
                          >
                            View Details
                          </button>
                        </div>
                      ) : (
                        <span style={{ color: '#94a3b8' }}>-</span>
                      )}
                    </td>
                    <td>
                      {inv.start_time ? (
                        <>
                          <div>{fmtDateOnly(inv.start_time)}</div>
                          <div className="cell-sub">{fmtTime(inv.start_time)}</div>
                        </>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>
                      {inv.end_time ? (
                        <>
                          <div>{fmtDateOnly(inv.end_time)}</div>
                          <div className="cell-sub">{fmtTime(inv.end_time)}</div>
                        </>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>{fmtDate(inv.created_at)}</td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className={inv.status === 'completed' || inv.status === 'submitted' ? 'btn-secondary' : 'btn-primary'}
                        type="button"
                        onClick={() => handleStartInterview(inv.token)}
                        disabled={inv.status === 'failed' || inv.status === 'completed' || inv.status === 'submitted'}
                      >
                        {inv.status === 'completed' || inv.status === 'submitted' ? 'Completed' : 'Start Interview'}
                      </button>
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
