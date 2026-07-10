import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Assessment.css';
import { API_BASE_URL } from '../apiConfig';

function safeText(v) {
  return (v ?? '').toString();
}

function formatDate(iso) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: '2-digit' });
  } catch {
    return iso;
  }
}

function buildInviteLink(inviteToken) {
  if (!inviteToken) return '';
  // Candidate link should go to the frontend app route (you can implement the exam page later).
  return `${window.location.origin}/take-assessment/${inviteToken}`;
}

export default function Assessment() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const filtered = useMemo(() => {
    let list = items;

    // Search by Assessment Name/Role
    const q = search.trim().toLowerCase();
    if (q) {
      list = list.filter((a) => {
        const name = (a.display_name || a.name || '').toLowerCase();
        const role = (a.role || '').toLowerCase();
        return name.includes(q) || role.includes(q);
      });
    }

    return list;
  }, [items, search]);

  useEffect(() => {
    setPage(1);
  }, [search]);

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

  const load = useCallback(async () => {
    if (fromDate && toDate && new Date(fromDate) > new Date(toDate)) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (fromDate) params.start_date = fromDate;
      if (toDate) params.end_date = toDate;
      const resp = await axios.get(`${API_BASE_URL}/assessments/`, { params });
      setItems(resp.data?.results || []);
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to load assessments');
    } finally {
      setLoading(false);
    }
  }, [fromDate, toDate]);

  useEffect(() => {
    load();
  }, [load]);

  const copyToClipboard = async (text) => {
    const value = safeText(text);
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      alert('Invite link copied.');
    } catch {
      // Fallback for older browsers
      const el = document.createElement('textarea');
      el.value = value;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      alert('Invite link copied.');
    }
  };

  return (
    <div className="assessments-page">

      <div className="assessments-shell">
        <div className="assessments-header">
          <div>
            <div className="assessments-title">Assessments</div>
            <div className="assessments-subtitle">Manage your created assessments and share candidate invite links.</div>
          </div>
          <div className="assessments-actions" style={{ display: 'flex', gap: '8px' }}>
            <button 
              className="assessments-btn-back" 
              onClick={() => navigate('/dashboard')} 
              type="button"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 18 9 12 15 6" />
              </svg>
              Back
            </button>
            <button 
              className="assessments-btn-refresh" 
              onClick={load} 
              type="button"
              disabled={loading}
            >
              <svg 
                width="14" 
                height="14" 
                viewBox="0 0 24 24" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
                className={loading ? 'animate-spin' : ''}
              >
                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Refresh
            </button>
          </div>
        </div>

        <div className="assessments-toolbar" style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <input
            className="search-input"
            style={{ flex: 1, height: '40px' }}
            placeholder="Search by assessment name or role"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '14px', color: '#64748b' }}>From:</span>
            <input
              type="date"
              className="search-input"
              style={{ width: 'auto', height: '40px' }}
              max={toDate || "9999-12-31"}
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '14px', color: '#64748b' }}>To:</span>
            <input
              type="date"
              className="search-input"
              style={{ width: 'auto', height: '40px' }}
              min={fromDate}
              max="9999-12-31"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
            />
          </div>

          {fromDate && toDate && new Date(fromDate) > new Date(toDate) && (
            <div className="date-range-error-message" style={{
              background: '#fef2f2',
              border: '1px solid #fca5a5',
              borderRadius: '0.8rem',
              padding: '0.6rem 1rem',
              color: '#b91c1c',
              fontSize: '0.85rem',
              fontWeight: '600',
              marginTop: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              width: '100%'
            }}>
              ⚠️ From Date cannot be later than To Date.
            </div>
          )}
        </div>

        {loading ? (
          <div className="state-card">Loading assessments…</div>
        ) : error ? (
          <div className="state-card error">
            <div className="state-title">Couldn’t load assessments</div>
            <div className="state-text">{error}</div>
            <button className="btn-primary" onClick={load} type="button">Retry</button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="state-card">
            <div className="state-title">No assessments found</div>
            <div className="state-text">Create an assessment from the Review page, then it will appear here.</div>
          </div>
        ) : (
          <div className="table-card">
            <table className="assessments-table">
              <thead>
                <tr>
                  <th>Assessment / Role</th>
                  <th>Questions</th>
                  <th>Time</th>
                  <th>Invited</th>
                  <th>Submitted</th>
                  <th>Created</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((a) => {
                  const title = a.display_name || a.name || `Assessment #${a.id}`;
                  const roleText = (a.role || '').toString().trim();
                  const isManualPlaceholder = roleText.toLowerCase() === 'manual assessment';
                  const shouldShowRole = roleText && !isManualPlaceholder && roleText.toLowerCase() !== title.toString().trim().toLowerCase();
                  const inviteLink = buildInviteLink(a.invite_token);
                  return (
                    <tr key={a.id}>
                      <td>
                        <div className="cell-title">{title}</div>
                        {shouldShowRole && <div className="cell-sub">{a.role}</div>}
                      </td>
                      <td>{(a.total_questions || 0) + (a.coding_question_count || 0)}</td>
                      <td>{a.total_time ?? '-'}</td>
                      <td>{a.invited ?? 0}</td>
                      <td>{a.submitted ?? 0}</td>
                      <td>{formatDate(a.created_at)}</td>
                      <td style={{ textAlign: 'right' }}>
                        <div className="row-actions" style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                          <button
                            type="button"
                            className="btn-secondary"
                            onClick={() => navigate(`/view-assessment/${a.id}`)}
                            title="View assessment details"
                          >
                            View
                          </button>
                          <button
                            type="button"
                            className="btn-invite"
                            onClick={() => navigate(`/invite-candidates/${a.id}`)}
                            title={a.assessment_mode === 'single' && a.invited > 0 ? "Invitation already sent (Single Mode)" : "Invite candidates"}
                            disabled={a.assessment_mode === 'single' && a.invited > 0}
                            style={a.assessment_mode === 'single' && a.invited > 0 ? { opacity: 0.5, cursor: 'not-allowed' } : {}}
                          >
                            Invite
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
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



