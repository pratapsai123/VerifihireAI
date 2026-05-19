import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/LiveInterviewList.css';
import { API_BASE_URL } from '../apiConfig';

function fmtSchedule(startIso, endIso) {
  if (!startIso) return null;
  try {
    const start = new Date(startIso);
    const fmtDate = (d) => d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    const fmtTime = (d) => {
      const h = d.getHours(), m = d.getMinutes(), ampm = h >= 12 ? 'PM' : 'AM';
      return `${String(h % 12 || 12).padStart(2, '0')}:${String(m).padStart(2, '0')} ${ampm}`;
    };
    if (endIso) {
      const end = new Date(endIso);
      return { date: fmtDate(start), time: `${fmtTime(start)} – ${fmtTime(end)}` };
    }
    return { date: fmtDate(start), time: fmtTime(start) };
  } catch {
    return null;
  }
}

function getInitials(name) {
  if (!name) return '?';
  const parts = name.trim().split(' ');
  return parts.length >= 2
    ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    : name[0].toUpperCase();
}

export default function LiveInterviewList() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const [userProfile, setUserProfile] = useState(null);

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [profileResp, invResp] = await Promise.all([
        axios.get(`${API_BASE_URL}/profile/`).catch(() => ({ data: null })),
        axios.get(`${API_BASE_URL}/interviews/invitations/`)
      ]);
      setUserProfile(profileResp.data);
      setItems(invResp.data?.results || []);
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to load interview candidates');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    window.scrollTo({ top: 0, behavior: 'auto' });
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

  useEffect(() => { setPage(1); }, [search]);

  const stats = useMemo(() => ({
    total: items.length,
    invited: items.filter(i => i.status === 'sent').length,
    accepted: items.filter(i => i.status === 'accepted').length,
    completed: items.filter(i => i.status === 'completed' || i.status === 'submitted').length,
  }), [items]);

  const totalPages = useMemo(() => Math.max(1, Math.ceil(filtered.length / pageSize)), [filtered.length]);
  const currentPage = Math.min(page, totalPages);
  const pageItems = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filtered.slice(start, start + pageSize);
  }, [filtered, currentPage]);

  const pageButtons = useMemo(() => {
    const maxButtons = 5;
    const half = Math.floor(maxButtons / 2);
    let start = Math.max(1, currentPage - half);
    let end = Math.min(totalPages, start + maxButtons - 1);
    start = Math.max(1, end - maxButtons + 1);
    const nums = [];
    for (let i = start; i <= end; i += 1) nums.push(i);
    return nums;
  }, [currentPage, totalPages]);

  const getStatusMeta = (status) => {
    switch (status) {
      case 'sent': return { label: 'Invited', cls: 'pill-blue' };
      case 'accepted': return { label: 'Accepted', cls: 'pill-green' };
      case 'completed': return { label: 'Completed', cls: 'pill-teal' };
      case 'submitted': return { label: 'Submitted', cls: 'pill-teal' };
      case 'failed': return { label: 'Failed', cls: 'pill-red' };
      case 'draft': return { label: 'Draft', cls: 'pill-gray' };
      default: return { label: status || 'Pending', cls: 'pill-gray' };
    }
  };

  const renderStars = (rating) => {
    const r = parseFloat(rating || 0);
    if (r <= 0) return <span className="lil-dash">–</span>;
    return (
      <div className="lil-stars">
        {[1, 2, 3, 4, 5].map(s => (
          <span key={s} className={`lil-star ${s <= Math.round(r) ? 'filled' : ''}`}>★</span>
        ))}
        <span className="lil-score">{r.toFixed(1)}</span>
      </div>
    );
  };

  const handleStartInterview = (token) => {
    window.open(`/live-interview-interviewer?token=${token}`, '_blank');
  };

  return (
    <div className="lil-page">
      <div className="lil-shell">

        {/* ── Header ── */}
        <div className="lil-header">
          <div className="lil-header-left">
            <div className="lil-icon-wrap">
              {/* Video / live interview icon */}
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="23 7 16 12 23 17 23 7" />
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
              </svg>
            </div>
            <div>
              <h1 className="lil-title">Live Interview Candidates</h1>
              <p className="lil-sub">Manage and join scheduled live interview sessions</p>
            </div>
          </div>
          <div className="lil-header-actions">
            <button className="lil-btn-back" type="button" onClick={() => navigate('/dashboard')}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 18 9 12 15 6" />
              </svg>
              Back
            </button>
            <button className="lil-btn-refresh" type="button" onClick={load}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 4 23 10 17 10" />
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
              </svg>
              Refresh
            </button>
          </div>
        </div>

        {/* ── Stats bar ── */}
        <div className="lil-stats-bar">
          <div className="lil-stat">
            <span className="lil-stat-val">{stats.total}</span>
            <span className="lil-stat-lbl">Total</span>
          </div>
          <div className="lil-stat-div" />
          <div className="lil-stat">
            <span className="lil-stat-val blue">{stats.invited}</span>
            <span className="lil-stat-lbl">Invited</span>
          </div>
          <div className="lil-stat-div" />
          <div className="lil-stat">
            <span className="lil-stat-val green">{stats.accepted}</span>
            <span className="lil-stat-lbl">Accepted</span>
          </div>
          <div className="lil-stat-div" />
          <div className="lil-stat">
            <span className="lil-stat-val teal">{stats.completed}</span>
            <span className="lil-stat-lbl">Completed</span>
          </div>
        </div>

        {/* ── Search ── */}
        <div className="lil-toolbar">
          <div className="lil-search-wrap">
            <svg className="lil-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              className="lil-search"
              placeholder="Search by name, email or interview…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && (
              <button className="lil-search-clear" type="button" onClick={() => setSearch('')}>✕</button>
            )}
          </div>
        </div>

        {/* ── Content ── */}
        {loading ? (
          <div className="lil-state-card">
            <div className="lil-spinner" />
            <p>Loading interview candidates…</p>
          </div>
        ) : error ? (
          <div className="lil-state-card lil-state-error">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <p className="lil-state-title">Could not load candidates</p>
            <p className="lil-state-sub">{error}</p>
            <button className="lil-btn-refresh" type="button" onClick={load}>Retry</button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="lil-state-card">
            <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="23 7 16 12 23 17 23 7" />
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
            </svg>
            <p className="lil-state-title">{search ? 'No results found' : 'No interviews yet'}</p>
            <p className="lil-state-sub">{search ? 'Try a different search term.' : 'Invite candidates to get started.'}</p>
          </div>
        ) : (
          <div className="lil-table-card">
            <table className="lil-table">
              <thead>
                <tr>
                  <th className="col-candidate">Candidate</th>
                  <th className="col-interviewer">Interviewer</th>
                  <th className="col-interview">Interview</th>
                  <th className="col-status">Status</th>
                  <th className="col-rating">Rating</th>
                  <th className="col-schedule">Schedule</th>
                  <th className="col-action">Action</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((inv) => {
                  const { label, cls } = getStatusMeta(inv.status);
                  const sched = fmtSchedule(inv.start_time, inv.end_time);
                  const isDone = inv.status === 'completed' || inv.status === 'submitted';
                  const isFailed = inv.status === 'failed';
                  
                  let canStart = false;
                  const userEmail = userProfile?.email?.toLowerCase();
                  if (userEmail) {
                    if (inv.interviewer_email?.toLowerCase() === userEmail) {
                      canStart = true;
                    } else if (inv.participants && inv.participants.some(p => p.email?.toLowerCase() === userEmail)) {
                      canStart = true;
                    }
                  }
                  
                  return (
                    <tr key={inv.id} className="lil-row">
                      <td className="col-candidate">
                        <div className="lil-person">
                          <div className="lil-avatar">{getInitials(inv.name)}</div>
                          <div>
                            <div className="lil-name">{inv.name || '–'}</div>
                            <div className="lil-email">{inv.email || '–'}</div>
                            {inv.phone && <div className="lil-phone">{inv.phone}</div>}
                          </div>
                        </div>
                      </td>
                      <td className="col-interviewer">
                        <div className="lil-person">
                          <div className="lil-avatar lil-avatar-teal">{getInitials(inv.interviewer_name)}</div>
                          <div>
                            <div className="lil-name">{inv.interviewer_name || '–'}</div>
                            <div className="lil-email">{inv.interviewer_email || '–'}</div>
                          </div>
                        </div>
                      </td>
                      <td className="col-interview">
                        <span className="lil-interview-name">{inv.interview?.name || '–'}</span>
                      </td>
                      <td className="col-status">
                        <span className={`lil-pill ${cls}`}>{label}</span>
                      </td>
                      <td className="col-rating">
                        {inv.feedbacks && inv.feedbacks.length > 0 ? (
                          <div className="lil-rating-cell">
                            {renderStars(
                              inv.feedbacks.reduce((sum, f) => sum + (f.interviewer_average_rating || f.interviewer_rating || 0), 0) / 
                              (inv.feedbacks.filter(f => f.interviewer_average_rating || f.interviewer_rating).length || 1)
                            )}
                            <button
                              className="lil-view-btn"
                              onClick={() => navigate('/feedback-details', { state: { inv } })}
                            >
                              View
                            </button>
                          </div>
                        ) : renderStars(0)}
                      </td>
                      <td className="col-schedule">
                        {sched ? (
                          <div className="lil-schedule">
                            <span className="lil-sched-date">{sched.date}</span>
                            <span className="lil-sched-time">{sched.time}</span>
                          </div>
                        ) : <span className="lil-dash">–</span>}
                      </td>
                      <td className="col-action">
                        {isDone ? (
                          <span className="lil-done-badge">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="20 6 9 17 4 12" />
                            </svg>
                            Done
                          </span>
                        ) : (
                          <button
                            className="lil-join-btn"
                            type="button"
                            onClick={() => handleStartInterview(inv.token)}
                            disabled={isFailed || !canStart}
                            title={!canStart ? "You are not assigned as an interviewer or panel member for this interview" : ""}
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                              <polygon points="5 3 19 12 5 21 5 3" />
                            </svg>
                            Start
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {/* ── Pagination ── */}
            <div className="lil-pager">
              <div className="lil-pager-info">
                Showing <strong>{filtered.length === 0 ? 0 : (currentPage - 1) * pageSize + 1}</strong>–<strong>{Math.min(currentPage * pageSize, filtered.length)}</strong> of <strong>{filtered.length}</strong>
              </div>
              <div className="lil-pager-btns">
                <button className="lil-pg-btn" type="button" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={currentPage <= 1}>‹</button>
                {pageButtons[0] > 1 && <>
                  <button className={`lil-pg-num ${currentPage === 1 ? 'active' : ''}`} type="button" onClick={() => setPage(1)}>1</button>
                  {pageButtons[0] > 2 && <span className="lil-pg-dots">…</span>}
                </>}
                {pageButtons.map(n => (
                  <button key={n} className={`lil-pg-num ${currentPage === n ? 'active' : ''}`} type="button" onClick={() => setPage(n)}>{n}</button>
                ))}
                {pageButtons[pageButtons.length - 1] < totalPages && <>
                  {pageButtons[pageButtons.length - 1] < totalPages - 1 && <span className="lil-pg-dots">…</span>}
                  <button className={`lil-pg-num ${currentPage === totalPages ? 'active' : ''}`} type="button" onClick={() => setPage(totalPages)}>{totalPages}</button>
                </>}
                <button className="lil-pg-btn" type="button" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={currentPage >= totalPages}>›</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
