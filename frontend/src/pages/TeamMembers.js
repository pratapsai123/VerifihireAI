import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';

function safeParseUser() {
  const raw = localStorage.getItem('user');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export default function TeamMembers() {
  const me = safeParseUser();
  const myEmail = (me?.email || '').toLowerCase();
  const myRole = (me?.role || '').toLowerCase();

  const canAccess = useMemo(() => {
    return ['company_admin', 'hr_manager', 'application_admin'].includes(myRole);
  }, [myRole]);

  const canInvite = useMemo(() => {
    return myRole === 'company_admin' || myRole === 'hr_manager';
  }, [myRole]);

  const [tab, setTab] = useState(canInvite ? 'invite' : 'overview'); // invite | overview
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState({ scope: '', members: [], invitations: [] });

  // Filters (useful especially for application_admin who sees all companies)
  const [q, setQ] = useState('');
  const [companyFilter, setCompanyFilter] = useState(''); // company name or ''
  const [invStatusFilter, setInvStatusFilter] = useState(''); // pending/accepted/cancelled/expired or ''
  const [invRoleFilter, setInvRoleFilter] = useState(''); // hr/hr_manager or ''
  const [memberRoleFilter, setMemberRoleFilter] = useState(''); // company_admin/hr_manager/hr/... or ''

  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('hr');
  const [inviting, setInviting] = useState(false);
  const [inviteResult, setInviteResult] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});

  const [memberPage, setMemberPage] = useState(1);
  const [invitePage, setInvitePage] = useState(1);

  useEffect(() => {
    setMemberPage(1);
    setInvitePage(1);
  }, [q, companyFilter, invStatusFilter, invRoleFilter, memberRoleFilter]);

  // Helper: build the JWT Authorization header from localStorage
  const authHeader = () => {
    const token = localStorage.getItem('accessToken');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get(`${API_BASE_URL}/users/team-members/`, {
        headers: authHeader(),
      });
      setData(res.data);
    } catch (e) {
      setError(e?.response?.data?.error || 'Failed to load team members.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!canAccess) return;
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canAccess]);

  useEffect(() => {
    // If role changes (or page loaded as application_admin), default to overview
    if (!canInvite) setTab('overview');
  }, [canInvite]);

  const handleInvite = async (e) => {
    e.preventDefault();
    setInviteResult(null);
    setFieldErrors({});
    setError('');
    if (!canInvite) {
      setError('You are not allowed to send invitations.');
      return;
    }
    if (!inviteEmail.trim()) {
      setFieldErrors(prev => ({ ...prev, email: 'Email is required.' }));
      return;
    }
    setInviting(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/users/invite/`, {
        inviter_email: myEmail,
        email: inviteEmail.trim(),
        role: inviteRole,
      });
      setInviteResult(res.data);
      setInviteEmail('');
      await load();
      setTab('overview');
    } catch (e2) {
      if (e2.response) {
        const errorData = e2.response.data;
        if (errorData.email) {
          setFieldErrors(prev => ({ ...prev, email: errorData.email[0] }));
        } else if (errorData.role) {
          setFieldErrors(prev => ({ ...prev, role: errorData.role[0] }));
        } else {
          setError(errorData.error || 'Failed to create invitation.');
        }
      } else {
        setError('Unable to connect to server.');
      }
    } finally {
      setInviting(false);
    }
  };

  const handleCancelInvite = async (token) => {
    setError('');
    try {
      await axios.post(
        `${API_BASE_URL}/users/invite/${token}/cancel/`,
        {},
        { headers: authHeader() }
      );
      await load();
    } catch (e) {
      setError(e?.response?.data?.error || 'Failed to cancel invitation.');
    }
  };

  const handleResendInvite = async (token) => {
    setError('');
    setInviteResult(null);
    try {
      const res = await axios.post(
        `${API_BASE_URL}/users/invite/${token}/resend/`,
        {},
        { headers: authHeader() }
      );
      setInviteResult(res.data);
      await load();
    } catch (e) {
      setError(e?.response?.data?.error || 'Failed to resend invitation.');
    }
  };

  const companyOptions = useMemo(() => {
    const set = new Set();
    (data.invitations || []).forEach((i) => {
      if (i?.company) set.add(String(i.company));
    });
    (data.members || []).forEach((m) => {
      if (m?.company) set.add(String(m.company));
      else if (m?.organization_name) set.add(String(m.organization_name));
    });
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [data.invitations, data.members]);

  const query = (q || '').trim().toLowerCase();

  const filteredInvitations = useMemo(() => {
    const list = Array.isArray(data.invitations) ? data.invitations : [];
    return list.filter((inv) => {
      if (companyFilter && String(inv.company || '') !== companyFilter) return false;
      if (invStatusFilter && String(inv.status || '') !== invStatusFilter) return false;
      if (invRoleFilter && String(inv.role || '') !== invRoleFilter) return false;
      if (query) {
        const hay = [
          inv.email,
          inv.role,
          inv.company,
          inv.status,
          inv.invited_by,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        if (!hay.includes(query)) return false;
      }
      return true;
    });
  }, [data.invitations, companyFilter, invStatusFilter, invRoleFilter, query]);

  const filteredMembers = useMemo(() => {
    const list = Array.isArray(data.members) ? data.members : [];
    return list.filter((m) => {
      const companyName = m.company || m.organization_name || '';
      if (companyFilter && String(companyName) !== companyFilter) return false;
      if (memberRoleFilter && String(m.role || '') !== memberRoleFilter) return false;
      if (query) {
        const name = [m.first_name, m.last_name].filter(Boolean).join(' ');
        const hay = [name, m.email, m.role, companyName].filter(Boolean).join(' ').toLowerCase();
        if (!hay.includes(query)) return false;
      }
      return true;
    });
  }, [data.members, companyFilter, memberRoleFilter, query]);

  // Pagination Logic
  const itemsPerPage = 10;

  const indexOfLastMember = memberPage * itemsPerPage;
  const indexOfFirstMember = indexOfLastMember - itemsPerPage;
  const paginatedMembers = filteredMembers.slice(indexOfFirstMember, indexOfLastMember);
  const totalMemberPages = Math.ceil(filteredMembers.length / itemsPerPage);

  const indexOfLastInvite = invitePage * itemsPerPage;
  const indexOfFirstInvite = indexOfLastInvite - itemsPerPage;
  const paginatedInvites = filteredInvitations.slice(indexOfFirstInvite, indexOfLastInvite);
  const totalInvitePages = Math.ceil(filteredInvitations.length / itemsPerPage);

  return (
    <div className="dashboard-container">
      <Header />
      <div
        className="page-container"
        style={{
          maxWidth: '100%',
          width: '100%',
          margin: '1rem auto',
          padding: '0 0.75rem',
        }}
      >
        <h2 style={{ marginTop: 12 }}>Team Members</h2>

        {!canAccess && (
          <div className="auth-error-message" style={{ marginTop: 16 }}>
            You don’t have permission to view this page.
          </div>
        )}

        {canAccess && (
          <>
            <div style={{ display: 'flex', gap: 12, marginTop: 16, flexWrap: 'wrap' }}>
              {canInvite ? (
                <button
                  type="button"
                  className="btn btn-blue"
                  onClick={() => setTab('invite')}
                  style={{ opacity: tab === 'invite' ? 1 : 0.7 }}
                >
                  Invite
                </button>
              ) : null}
              <button
                type="button"
                className="btn btn-blue"
                onClick={() => setTab('overview')}
                style={{ opacity: tab === 'overview' ? 1 : 0.7 }}
              >
                Invited & Members
              </button>
            </div>

            {error && <div className="auth-error-message" style={{ marginTop: 16 }}>{error}</div>}

            {loading && <div style={{ marginTop: 16 }}>Loading...</div>}

            {!loading && tab === 'overview' && (
              <div style={{ marginTop: 16, background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e5e7eb' }}>
                <h3 style={{ marginBottom: 12 }}>Search & Filters</h3>
                {/* 4-part layout (no horizontal scroll). Wraps naturally on small screens. */}
                <div
                  style={{
                    display: 'grid',
                    gap: 12,
                    // Make Search a bit smaller and Invitations wider (better readability)
                    gridTemplateColumns: data.scope === 'all' ? '1.6fr 1fr 1.4fr 1fr' : '1.4fr 1fr',
                    alignItems: 'start',
                  }}
                >
                  {data.scope === 'all' ? (
                    <>
                      {/* Part 1: Search (Application Admin only) */}
                      <div style={{ display: 'grid', gap: 6 }}>
                        <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 600 }}>Search</div>
                        <input
                          className="auth-input"
                          placeholder="Email, name, company, role, status"
                          value={q}
                          onChange={(e) => setQ(e.target.value)}
                          style={{ width: '100%' }}
                        />
                      </div>

                      {/* Part 2: Company (Application Admin only) */}
                      <div style={{ display: 'grid', gap: 6 }}>
                        <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 600 }}>Company</div>
                        <select className="auth-input" value={companyFilter} onChange={(e) => setCompanyFilter(e.target.value)}>
                          <option value="">All Companies</option>
                          {companyOptions.map((c) => (
                            <option key={c} value={c}>{c}</option>
                          ))}
                        </select>
                      </div>
                    </>
                  ) : null}

                  {/* Part 4: Member filter */}
                  <div style={{ display: 'grid', gap: 6 }}>
                    <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 600 }}>Members</div>
                    <select className="auth-input" value={memberRoleFilter} onChange={(e) => setMemberRoleFilter(e.target.value)}>
                      <option value="">All Member Roles</option>
                      <option value="company_admin">company_admin</option>
                      <option value="hr_manager">hr_manager</option>
                      <option value="hr">hr</option>
                      <option value="interviewer">interviewer</option>
                      <option value="candidate">candidate</option>
                      {data.scope === 'all' ? <option value="application_admin">application_admin</option> : null}
                    </select>
                  </div>

                  {/* Part 3: Invitation filters (combined control) */}
                  <div style={{ display: 'grid', gap: 6 }}>
                    <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 600 }}>Invitations</div>
                    {/* Make this look like ONE control (single border) for better visibility */}
                    <div
                      style={{
                        border: '1px solid #cbd5e1',
                        borderRadius: 12,
                        overflow: 'hidden',
                        background: '#fff',
                        display: 'flex',
                        alignItems: 'stretch',
                        width: '100%',
                        minWidth: 360,
                      }}
                    >
                      <select
                        value={invStatusFilter}
                        onChange={(e) => setInvStatusFilter(e.target.value)}
                        style={{
                          width: '50%',
                          padding: '12px 14px',
                          border: 'none',
                          outline: 'none',
                          background: 'transparent',
                          fontSize: 16,
                          minHeight: 48,
                        }}
                      >
                        <option value="">All Invite Status</option>
                        <option value="pending">pending</option>
                        <option value="accepted">accepted</option>
                        <option value="cancelled">cancelled</option>
                        <option value="expired">expired</option>
                      </select>
                      <div style={{ width: 1, background: '#e5e7eb' }} />
                      <select
                        value={invRoleFilter}
                        onChange={(e) => setInvRoleFilter(e.target.value)}
                        style={{
                          width: '50%',
                          padding: '12px 14px',
                          border: 'none',
                          outline: 'none',
                          background: 'transparent',
                          fontSize: 16,
                          minHeight: 48,
                        }}
                      >
                        <option value="">All Invite Roles</option>
                        <option value="hr">hr</option>
                        <option value="hr_manager">hr_manager</option>
                        <option value="interviewer">interviewer</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div style={{ marginTop: 10, fontSize: 12, color: '#6b7280' }}>
                  Showing <strong>{filteredInvitations.length}</strong> invites and <strong>{filteredMembers.length}</strong> members.
                </div>
              </div>
            )}

            {!loading && tab === 'invite' && canInvite && (
              <div style={{ marginTop: 16, background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e5e7eb' }}>
                <h3 style={{ marginBottom: 12 }}>Invite a Team Member</h3>
                <div style={{ fontSize: 13, color: '#374151', marginBottom: 12 }}>
                  Company Admin can invite <strong>HR Manager</strong>, <strong>HR</strong> and <strong>Interviewer</strong>. HR Manager can invite <strong>HR</strong> and <strong>Interviewer</strong>.
                </div>
                <form onSubmit={handleInvite} style={{ display: 'grid', gap: 12, maxWidth: 520 }}>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <input
                      className="auth-input"
                      placeholder="Invitee Email"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      disabled={inviting}
                      style={{ marginBottom: 0 }}
                    />
                    {fieldErrors.email && (
                      <div className="field-error-text" style={{ marginTop: '0.2rem', marginBottom: '0.5rem' }}>{fieldErrors.email}</div>
                    )}
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <select
                      className="auth-input"
                      value={inviteRole}
                      onChange={(e) => setInviteRole(e.target.value)}
                      disabled={inviting}
                      style={{ marginBottom: 0 }}
                    >
                      <option value="hr">HR</option>
                      <option value="hr_manager">HR Manager</option>
                      <option value="interviewer">Interviewer</option>
                    </select>
                    {fieldErrors.role && (
                      <div className="field-error-text" style={{ marginTop: '0.2rem', marginBottom: '0.5rem' }}>{fieldErrors.role}</div>
                    )}
                  </div>
                  <button type="submit" className="auth-primary-btn" disabled={inviting}>
                    {inviting ? 'Inviting...' : 'Send Invite'}
                  </button>
                </form>

                {inviteResult && (
                  <div style={{ marginTop: 16, fontSize: 13 }}>
                    <div><strong>Invite Created</strong></div>
                    <div>email_sent: {String(inviteResult.email_sent)}</div>
                    {inviteResult.activation_link ? (
                      <div style={{ marginTop: 8 }}>
                        <div><strong>Activation Link (dev fallback)</strong></div>
                        <div style={{ wordBreak: 'break-all' }}>{inviteResult.activation_link}</div>
                      </div>
                    ) : null}
                    {inviteResult.temp_password ? (
                      <div style={{ marginTop: 8 }}>
                        <div><strong>Temp Password (dev fallback)</strong></div>
                        <div style={{ wordBreak: 'break-all' }}>{inviteResult.temp_password}</div>
                      </div>
                    ) : null}
                  </div>
                )}
              </div>
            )}

            {!loading && tab === 'overview' && (
              <div style={{ marginTop: 16, display: 'grid', gap: 16 }}>
                <div style={{ background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e5e7eb' }}>
                  <h3 style={{ marginBottom: 12 }}>Active Team Members</h3>
                  {filteredMembers?.length ? (
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Name</th>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Email</th>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Role</th>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Company</th>
                          </tr>
                        </thead>
                        <tbody>
                          {paginatedMembers.map((m) => (
                            <tr key={m.id}>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>
                                {[m.first_name, m.last_name].filter(Boolean).join(' ') || '-'}
                              </td>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{m.email}</td>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{m.role}</td>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{m.company || m.organization_name || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>

                      {/* Member Pagination Controls */}
                      {totalMemberPages > 1 && (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', borderTop: '1px solid #e5e7eb' }}>
                          <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                            Showing {indexOfFirstMember + 1} to {Math.min(indexOfLastMember, filteredMembers.length)} of {filteredMembers.length}
                          </span>
                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button
                              onClick={() => setMemberPage(prev => Math.max(prev - 1, 1))}
                              disabled={memberPage === 1}
                              style={{ padding: '0.4rem 0.8rem', background: memberPage === 1 ? '#f9fafb' : 'white', border: '1px solid #e5e7eb', borderRadius: '6px', cursor: memberPage === 1 ? 'not-allowed' : 'pointer', color: memberPage === 1 ? '#9ca3af' : '#4b5563', fontSize: '0.8rem', fontWeight: '500' }}
                            >
                              Previous
                            </button>
                            <div style={{ display: 'flex', alignItems: 'center', padding: '0 0.5rem', fontSize: '0.8rem', color: '#4b5563', fontWeight: '600' }}>
                              Page {memberPage} of {totalMemberPages}
                            </div>
                            <button
                              onClick={() => setMemberPage(prev => Math.min(prev + 1, totalMemberPages))}
                              disabled={memberPage === totalMemberPages}
                              style={{ padding: '0.4rem 0.8rem', background: memberPage === totalMemberPages ? '#f9fafb' : 'white', border: '1px solid #e5e7eb', borderRadius: '6px', cursor: memberPage === totalMemberPages ? 'not-allowed' : 'pointer', color: memberPage === totalMemberPages ? '#9ca3af' : '#4b5563', fontSize: '0.8rem', fontWeight: '500' }}
                            >
                              Next
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div style={{ fontSize: 13, color: '#6b7280' }}>No team members found.</div>
                  )}
                </div>

                <div style={{ background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e5e7eb' }}>
                  <h3 style={{ marginBottom: 12 }}>Pending / Sent Invitations</h3>
                  {filteredInvitations?.length ? (
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                        <thead>
                          <tr>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Email</th>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Role</th>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Company</th>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Status</th>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Invited By</th>
                            <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Expires</th>
                            {canInvite ? (
                              <th style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid #e5e7eb' }}>Actions</th>
                            ) : null}
                          </tr>
                        </thead>
                        <tbody>
                          {paginatedInvites.map((inv) => (
                            <tr key={inv.id}>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{inv.email}</td>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{inv.role}</td>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{inv.company}</td>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{inv.status}</td>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{inv.invited_by || '-'}</td>
                              <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{inv.expires_at || '-'}</td>
                              {canInvite ? (
                                <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>
                                  <div style={{ display: 'flex', gap: 10, flexWrap: 'nowrap', alignItems: 'center' }}>
                                    <button
                                      type="button"
                                      disabled={inv.status !== 'pending'}
                                      onClick={() => handleResendInvite(inv.token)}
                                      title="Resend"
                                      aria-label="Resend invitation"
                                      style={{
                                        width: 38,
                                        height: 38,
                                        borderRadius: 10,
                                        border: '1px solid #2563eb',
                                        background: inv.status !== 'pending' ? '#e5e7eb' : '#3b82f6',
                                        color: '#fff',
                                        cursor: inv.status !== 'pending' ? 'not-allowed' : 'pointer',
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        opacity: inv.status !== 'pending' ? 0.6 : 1,
                                      }}
                                    >
                                      {/* Reload icon */}
                                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                                        <path
                                          d="M20 12a8 8 0 10-2.343 5.657"
                                          stroke="currentColor"
                                          strokeWidth="2"
                                          strokeLinecap="round"
                                          strokeLinejoin="round"
                                        />
                                        <path
                                          d="M20 12v-6m0 6h-6"
                                          stroke="currentColor"
                                          strokeWidth="2"
                                          strokeLinecap="round"
                                          strokeLinejoin="round"
                                        />
                                      </svg>
                                    </button>
                                    <button
                                      type="button"
                                      disabled={inv.status !== 'pending'}
                                      onClick={() => handleCancelInvite(inv.token)}
                                      title="Cancel"
                                      aria-label="Cancel invitation"
                                      style={{
                                        width: 38,
                                        height: 38,
                                        borderRadius: 10,
                                        border: '1px solid #dc2626',
                                        background: inv.status !== 'pending' ? '#e5e7eb' : '#ef4444',
                                        color: '#fff',
                                        cursor: inv.status !== 'pending' ? 'not-allowed' : 'pointer',
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        opacity: inv.status !== 'pending' ? 0.6 : 1,
                                      }}
                                    >
                                      {/* X icon */}
                                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                                        <path
                                          d="M18 6L6 18M6 6l12 12"
                                          stroke="currentColor"
                                          strokeWidth="2.4"
                                          strokeLinecap="round"
                                          strokeLinejoin="round"
                                        />
                                      </svg>
                                    </button>
                                  </div>
                                </td>
                              ) : null}
                            </tr>
                          ))}
                        </tbody>
                      </table>

                      {/* Invite Pagination Controls */}
                      {totalInvitePages > 1 && (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', borderTop: '1px solid #e5e7eb' }}>
                          <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                            Showing {indexOfFirstInvite + 1} to {Math.min(indexOfLastInvite, filteredInvitations.length)} of {filteredInvitations.length}
                          </span>
                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button
                              onClick={() => setInvitePage(prev => Math.max(prev - 1, 1))}
                              disabled={invitePage === 1}
                              style={{ padding: '0.4rem 0.8rem', background: invitePage === 1 ? '#f9fafb' : 'white', border: '1px solid #e5e7eb', borderRadius: '6px', cursor: invitePage === 1 ? 'not-allowed' : 'pointer', color: invitePage === 1 ? '#9ca3af' : '#4b5563', fontSize: '0.8rem', fontWeight: '500' }}
                            >
                              Previous
                            </button>
                            <div style={{ display: 'flex', alignItems: 'center', padding: '0 0.5rem', fontSize: '0.8rem', color: '#4b5563', fontWeight: '600' }}>
                              Page {invitePage} of {totalInvitePages}
                            </div>
                            <button
                              onClick={() => setInvitePage(prev => Math.min(prev + 1, totalInvitePages))}
                              disabled={invitePage === totalInvitePages}
                              style={{ padding: '0.4rem 0.8rem', background: invitePage === totalInvitePages ? '#f9fafb' : 'white', border: '1px solid #e5e7eb', borderRadius: '6px', cursor: invitePage === totalInvitePages ? 'not-allowed' : 'pointer', color: invitePage === totalInvitePages ? '#9ca3af' : '#4b5563', fontSize: '0.8rem', fontWeight: '500' }}
                            >
                              Next
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div style={{ fontSize: 13, color: '#6b7280' }}>No invitations found.</div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}



