import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';
import {
  RefreshCw, AlertTriangle, CheckCircle2, Loader2, X,
  ClipboardList, Target, Mail, Brain, User, Users,
  ArrowRightLeft, UserPlus, Search, Filter, ChevronLeft,
  ChevronRight, Send, XCircle, Shield, Building2, Clock,
  UserCheck, UserX, RotateCcw, Code, Video, Trash2, History, FileText,
} from 'lucide-react';
import { getToken } from '../utils/authStorage';

function safeParseUser() {
  const raw = localStorage.getItem('user');
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

function Avatar({ name, size = 40 }) {
  const initials = (name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444'];
  const color = colors[(name || '').charCodeAt(0) % colors.length];
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%', background: color,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: '#fff', fontWeight: 700, fontSize: size * 0.38, flexShrink: 0,
    }}>{initials}</div>
  );
}

const ROLE_LABELS = {
  company_admin: 'Company Admin',
  hr_manager: 'HR Manager',
  hr: 'HR',
  interviewer: 'Interviewer',
  candidate: 'Candidate',
};

function StatPill({ label, value, Icon }) {
  const hasData = value > 0;
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px',
      background: hasData ? '#fef3c7' : '#f9fafb',
      border: `1px solid ${hasData ? '#fcd34d' : '#e5e7eb'}`,
      borderRadius: 10, flex: '1 1 calc(50% - 6px)', minWidth: 120,
    }}>
      <Icon size={15} color={hasData ? '#92400e' : '#9ca3af'} strokeWidth={2} />
      <div>
        <div style={{ fontSize: 11, color: '#6b7280', fontWeight: 500 }}>{label}</div>
        <div style={{ fontSize: 15, fontWeight: 700, color: hasData ? '#92400e' : '#374151' }}>{value}</div>
      </div>
    </div>
  );
}

function TransferModal({ member, onClose, onSuccess, authHeader }) {
  const [preview, setPreview] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(true);
  const [toUserId, setToUserId] = useState('');
  const [reason, setReason] = useState('');
  const [deactivateAfter, setDeactivateAfter] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/users/${member.id}/transfer-preview/`, { headers: authHeader() });
        setPreview(res.data);
        if (res.data?.eligible_replacements?.length) {
          setToUserId(String(res.data.eligible_replacements[0].id));
        }
      } catch (e) {
        setError(e?.response?.data?.error || 'Failed to load preview.');
      } finally {
        setLoadingPreview(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [member.id]);

  const handleTransfer = async () => {
    if (!toUserId) { setError('Please select a replacement.'); return; }
    setSubmitting(true); setError('');
    try {
      const res = await axios.post(
        `${API_BASE_URL}/users/${member.id}/transfer-ownership/`,
        { to_user_id: parseInt(toUserId, 10), transfer_reason: reason, deactivate_after: deactivateAfter },
        { headers: authHeader() }
      );
      setResult(res.data);
    } catch (e) {
      setError(e?.response?.data?.error || 'Transfer failed.');
    } finally { setSubmitting(false); }
  };

  const handleDeactivateOnly = async () => {
    if (!window.confirm(`Deactivate ${member.email} without transferring data?`)) return;
    setSubmitting(true); setError('');
    try {
      await axios.post(`${API_BASE_URL}/users/${member.id}/deactivate/`, { reason }, { headers: authHeader() });
      onSuccess();
    } catch (e) {
      setError(e?.response?.data?.error || 'Deactivation failed.');
    } finally { setSubmitting(false); }
  };

  const counts = preview?.ownership_counts || {};
  const replacements = preview?.eligible_replacements || [];
  const leavingName = preview?.user?.name || member.name || member.email;
  const leavingRole = ROLE_LABELS[preview?.user?.role || member.role] || member.role;
  const selectedReplacement = replacements.find(u => String(u.id) === String(toUserId));

  return (
    <div
      onClick={(e) => e.target === e.currentTarget && onClose()}
      style={{
        position: 'fixed', inset: 0, zIndex: 9999,
        background: 'rgba(15, 23, 42, 0.6)',
        backdropFilter: 'blur(4px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16,
      }}
    >
      <div style={{
        background: '#fff', borderRadius: 20, width: '100%', maxWidth: 540,
        maxHeight: '92vh', overflowY: 'auto',
        boxShadow: '0 25px 60px rgba(0,0,0,0.25)',
        animation: 'slideUp 0.2s ease',
      }}>
        {/* Header */}
        <div style={{
          padding: '20px 24px 16px', borderBottom: '1px solid #f1f5f9',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          position: 'sticky', top: 0, background: '#fff', borderRadius: '20px 20px 0 0', zIndex: 1,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: '#ede9fe', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ArrowRightLeft size={18} color="#7c3aed" strokeWidth={2.2} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 16, color: '#111827' }}>
                {result ? 'Transfer Complete' : 'Replace / Offboard Member'}
              </div>
              {!result && (
                <div style={{ fontSize: 12, color: '#6b7280', marginTop: 1 }}>
                  Ownership will be transferred to the selected member
                </div>
              )}
            </div>
          </div>
          <button onClick={onClose} style={{ border: 'none', background: '#f1f5f9', borderRadius: 8, width: 32, height: 32, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <X size={16} color="#6b7280" strokeWidth={2.2} />
          </button>
        </div>

        <div style={{ padding: '20px 24px 24px' }}>
          {error && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 10, padding: '10px 14px', marginBottom: 16, fontSize: 13, color: '#dc2626', display: 'flex', alignItems: 'center', gap: 8 }}>
              <AlertTriangle size={15} color="#dc2626" strokeWidth={2} style={{ flexShrink: 0 }} />
              {error}
            </div>
          )}

          {result ? (
            <div style={{ textAlign: 'center', padding: '12px 0 8px' }}>
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 12 }}>
                <CheckCircle2 size={52} color="#16a34a" strokeWidth={1.8} />
              </div>
              <div style={{ fontWeight: 700, fontSize: 18, color: '#111827', marginBottom: 6 }}>Transfer Successful</div>
              <div style={{ fontSize: 13, color: '#6b7280', marginBottom: 20 }}>All ownership records have been updated.</div>
              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 12, padding: 16, textAlign: 'left', marginBottom: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                  <span style={{ fontSize: 12, color: '#6b7280', width: 36, textAlign: 'right', flexShrink: 0 }}>From</span>
                  <div style={{ flex: 1, padding: '6px 10px', background: '#fef2f2', borderRadius: 8, fontSize: 13, color: '#374151', fontWeight: 500 }}>{result?.transferred_from?.email}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                  <span style={{ fontSize: 12, color: '#6b7280', width: 36, textAlign: 'right', flexShrink: 0 }}>To</span>
                  <div style={{ flex: 1, padding: '6px 10px', background: '#f0fdf4', borderRadius: 8, fontSize: 13, color: '#374151', fontWeight: 500 }}>{result?.transferred_to?.email}</div>
                </div>
                {result?.transfer_reason && (
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                    <span style={{ fontSize: 12, color: '#6b7280', width: 36, textAlign: 'right', flexShrink: 0, paddingTop: 3 }}>Note</span>
                    <div style={{ flex: 1, padding: '6px 10px', background: '#f8fafc', borderRadius: 8, fontSize: 13, color: '#374151' }}>{result.transfer_reason}</div>
                  </div>
                )}
              </div>
              <button onClick={onSuccess} style={{ width: '100%', padding: '12px 0', borderRadius: 10, border: 'none', background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)', color: '#fff', fontWeight: 600, fontSize: 14, cursor: 'pointer' }}>Done</button>
            </div>
          ) : loadingPreview ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#6b7280' }}>
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 10 }}>
                <Loader2 size={36} color="#a78bfa" strokeWidth={1.8} style={{ animation: 'spin 1s linear infinite' }} />
              </div>
              <div style={{ fontSize: 14 }}>Loading member details...</div>
            </div>
          ) : (
            <>
              {/* Leaving member card */}
              <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 14, padding: '14px 16px', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
                <Avatar name={leavingName} size={44} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, fontSize: 14, color: '#111827', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{leavingName}</div>
                  <div style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>{member.email}</div>
                </div>
                <div style={{ padding: '3px 10px', borderRadius: 20, background: '#fee2e2', fontSize: 11, fontWeight: 600, color: '#991b1b', whiteSpace: 'nowrap' }}>{leavingRole}</div>
              </div>

              {/* Data pills */}
              <div style={{ marginBottom: 18 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Full Data Ownership Transfer</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  <StatPill label="Assessments" value={counts.assessments} Icon={ClipboardList} />
                  <StatPill label="Custom Assessments" value={counts.custom_assessments} Icon={Target} />
                  <StatPill label="Invitations" value={counts.candidate_invitations} Icon={Mail} />
                  <StatPill label="Job Roles" value={counts.job_roles} Icon={Building2} />
                  <StatPill label="Questions" value={counts.questions} Icon={FileText} />
                  <StatPill label="Users Invited" value={counts.user_invitations} Icon={UserPlus} />
                  <StatPill label="Interviews" value={counts.interviews} Icon={Video} />
                  <StatPill label="Interview Requests" value={counts.interview_invitations} Icon={CheckCircle2} />
                  <StatPill label="Subordinates" value={counts.subordinates} Icon={Users} />
                  <StatPill label="Deletion Req." value={counts.deletion_requests} Icon={Trash2} />
                  <StatPill label="Calendar Slots" value={counts.interview_slots} Icon={Clock} />
                  <StatPill label="Availability" value={counts.interviewer_availability} Icon={Clock} />
                  <StatPill label="AI Assessments" value={counts.ai_assessments} Icon={Brain} />
                  <StatPill label="AI Candidates" value={counts.ai_candidates} Icon={User} />
                  <StatPill label="Coding Qs" value={counts.coding_questions} Icon={Code} />
                  <StatPill label="Coding Invites" value={counts.coding_invites} Icon={Mail} />
                </div>
              </div>

              {/* Replacement */}
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 8 }}>
                  Select Replacement <span style={{ color: '#ef4444' }}>*</span>
                </label>
                {replacements.length === 0 ? (
                  <div style={{ padding: '12px 14px', background: '#fef9c3', border: '1px solid #fde047', borderRadius: 10, fontSize: 13, color: '#854d0e', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <AlertTriangle size={14} color="#854d0e" strokeWidth={2} style={{ flexShrink: 0 }} />
                    No eligible replacements found with the same role ({leavingRole}).
                  </div>
                ) : (
                  <>
                    <div style={{ position: 'relative' }}>
                      <select
                        value={toUserId}
                        onChange={(e) => setToUserId(e.target.value)}
                        style={{ width: '100%', padding: '10px 36px 10px 14px', borderRadius: 10, border: '1.5px solid #e5e7eb', fontSize: 14, color: '#111827', background: '#fff', cursor: 'pointer', appearance: 'none', outline: 'none', boxSizing: 'border-box' }}
                        onFocus={e => (e.target.style.borderColor = '#6366f1')}
                        onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
                      >
                        <option value="">— Choose a replacement —</option>
                        {replacements.map((u) => (
                          <option key={u.id} value={u.id}>{u.name || u.email} ({ROLE_LABELS[u.role] || u.role})</option>
                        ))}
                      </select>
                      <span style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: '#9ca3af', fontSize: 14 }}>▾</span>
                    </div>
                    {selectedReplacement && (
                      <div style={{ marginTop: 8, padding: '8px 12px', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 10, display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Avatar name={selectedReplacement.name || selectedReplacement.email} size={28} />
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 600, color: '#166534' }}>{selectedReplacement.name || selectedReplacement.email}</div>
                          <div style={{ fontSize: 11, color: '#15803d' }}>{selectedReplacement.email}</div>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Reason */}
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 8 }}>
                  Reason <span style={{ fontSize: 12, color: '#9ca3af', fontWeight: 400 }}>(optional)</span>
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={2}
                  placeholder="e.g. Employee resigned, transferred to another department..."
                  style={{ width: '100%', padding: '10px 14px', borderRadius: 10, border: '1.5px solid #e5e7eb', fontSize: 13, color: '#111827', resize: 'vertical', outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box' }}
                  onFocus={e => (e.target.style.borderColor = '#6366f1')}
                  onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
                />
              </div>

              {/* Deactivate toggle */}
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20, cursor: 'pointer', userSelect: 'none' }}>
                <div onClick={() => setDeactivateAfter(v => !v)} style={{ width: 42, height: 24, borderRadius: 12, flexShrink: 0, background: deactivateAfter ? '#6366f1' : '#d1d5db', position: 'relative', transition: 'background 0.2s', cursor: 'pointer' }}>
                  <div style={{ position: 'absolute', top: 3, left: deactivateAfter ? 20 : 3, width: 18, height: 18, borderRadius: '50%', background: '#fff', transition: 'left 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)' }} />
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>Deactivate leaving member</div>
                  <div style={{ fontSize: 11, color: '#9ca3af' }}>Blocks login but preserves all historical data</div>
                </div>
              </label>

              {/* Action buttons */}
              <div style={{ display: 'flex', gap: 10 }}>
                <button
                  onClick={handleTransfer}
                  disabled={submitting || !toUserId || replacements.length === 0}
                  style={{ flex: 1, padding: '12px 0', borderRadius: 10, border: 'none', background: submitting || !toUserId ? '#c7d2fe' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)', color: '#fff', fontWeight: 600, fontSize: 14, cursor: submitting || !toUserId ? 'not-allowed' : 'pointer' }}
                >
                  {submitting
                    ? <><Loader2 size={15} strokeWidth={2.2} style={{ animation: 'spin 1s linear infinite', marginRight: 6, verticalAlign: 'middle' }} />Processing…</>
                    : <><RefreshCw size={15} strokeWidth={2.2} style={{ marginRight: 6, verticalAlign: 'middle' }} />Transfer & Replace</>
                  }
                </button>
                <button
                  onClick={handleDeactivateOnly}
                  disabled={submitting}
                  style={{ padding: '12px 16px', borderRadius: 10, border: '1.5px solid #fca5a5', background: '#fff', color: '#dc2626', fontWeight: 600, fontSize: 14, cursor: submitting ? 'not-allowed' : 'pointer', whiteSpace: 'nowrap' }}
                  onMouseEnter={e => (e.currentTarget.style.background = '#fef2f2')}
                  onMouseLeave={e => (e.currentTarget.style.background = '#fff')}
                >
                  Deactivate Only
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function TeamMembers() {
  const me = safeParseUser();
  const myEmail = (me?.email || '').toLowerCase();
  const myRole = (me?.role || '').toLowerCase();

  const canAccess = useMemo(() => ['company_admin', 'hr', 'hr_manager', 'application_admin'].includes(myRole), [myRole]);
  const canInvite = useMemo(() => myRole === 'company_admin' || myRole === 'hr_manager' || myRole === 'hr', [myRole]);

  const [tab, setTab] = useState(canInvite ? 'invite' : 'overview'); // overview, invite, history
  const [logs, setLogs] = useState([]);
  const [loadingLogs, setLoadingLogs] = useState(false);

  const loadLogs = async () => {
    setLoadingLogs(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/users/transfer-logs/`, { headers: authHeader() });
      setLogs(res.data.logs || []);
    } catch (e) {
      console.error('Failed to load transfer logs', e);
    } finally {
      setLoadingLogs(false);
    }
  };

  useEffect(() => {
    if (tab === 'history') loadLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState({ scope: '', members: [], invitations: [] });

  const [q, setQ] = useState('');
  const [companyFilter, setCompanyFilter] = useState('');
  const [invStatusFilter, setInvStatusFilter] = useState('');
  const [invRoleFilter, setInvRoleFilter] = useState('');
  const [memberRoleFilter, setMemberRoleFilter] = useState('');

  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('');
  const [inviting, setInviting] = useState(false);

  const availableRoles = useMemo(() => {
    if (myRole === 'company_admin' || myRole === 'application_admin') {
      return [{ value: 'hr_manager', label: 'HR Manager' }, { value: 'hr', label: 'HR' }, { value: 'interviewer', label: 'Interviewer' }];
    } else if (myRole === 'hr_manager') {
      return [{ value: 'hr', label: 'HR' }, { value: 'interviewer', label: 'Interviewer' }];
    } else if (myRole === 'hr') {
      return [{ value: 'interviewer', label: 'Interviewer' }];
    }
    return [];
  }, [myRole]);

  const [inviteResult, setInviteResult] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [memberPage, setMemberPage] = useState(1);
  const [invitePage, setInvitePage] = useState(1);
  const [offboardingMember, setOffboardingMember] = useState(null);

  const canOffboard = useMemo(() => myRole === 'company_admin' || myRole === 'hr_manager', [myRole]);

  const isOffboardable = (member) => {
    if (!canOffboard) return false;
    if (member.is_active === false) return false;
    return ['hr_manager', 'hr', 'interviewer'].includes(member.role) && member.email !== myEmail;
  };

  useEffect(() => { setMemberPage(1); setInvitePage(1); }, [q, companyFilter, invStatusFilter, invRoleFilter, memberRoleFilter]);

  const authHeader = () => {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const load = async () => {
    setLoading(true); setError('');
    try {
      const res = await axios.get(`${API_BASE_URL}/users/team-members/`, { headers: authHeader() });
      setData(res.data);
    } catch (e) {
      setError(e?.response?.data?.error || 'Failed to load team members.');
    } finally { setLoading(false); }
  };

  useEffect(() => {
    if (!canAccess) return;
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canAccess]);
  useEffect(() => { if (!canInvite) setTab('overview'); }, [canInvite]);

  const handleInvite = async (e) => {
    e.preventDefault();
    setInviteResult(null); setFieldErrors({}); setError('');
    if (!canInvite) { setError('You are not allowed to send invitations.'); return; }
    
    let hasError = false;
    const errors = {};
    if (!inviteEmail.trim()) {
      errors.email = 'Email is required.';
      hasError = true;
    }
    if (!inviteRole) {
      errors.role = 'Role is required.';
      hasError = true;
    }
    if (hasError) {
      setFieldErrors(errors);
      return;
    }
    
    setInviting(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/users/invite/`, { inviter_email: myEmail, email: inviteEmail.trim(), role: inviteRole });
      setInviteResult(res.data); setInviteEmail(''); setInviteRole('');
      await load(); setTab('overview');
    } catch (e2) {
      if (e2.response) {
        const d = e2.response.data;
        if (d.email) setFieldErrors(prev => ({ ...prev, email: d.email[0] }));
        else if (d.role) setFieldErrors(prev => ({ ...prev, role: d.role[0] }));
        else setError(d.error || 'Failed to create invitation.');
      } else { setError('Unable to connect to server.'); }
    } finally { setInviting(false); }
  };

  const handleCancelInvite = async (token) => {
    setError('');
    try { await axios.post(`${API_BASE_URL}/users/invite/${token}/cancel/`, {}, { headers: authHeader() }); await load(); }
    catch (e) { setError(e?.response?.data?.error || 'Failed to cancel invitation.'); }
  };

  const handleResendInvite = async (token) => {
    setError(''); setInviteResult(null);
    try {
      const res = await axios.post(`${API_BASE_URL}/users/invite/${token}/resend/`, {}, { headers: authHeader() });
      setInviteResult(res.data); await load();
    } catch (e) { setError(e?.response?.data?.error || 'Failed to resend invitation.'); }
  };

  const companyOptions = useMemo(() => {
    const set = new Set();
    (data.invitations || []).forEach(i => { if (i?.company) set.add(String(i.company)); });
    (data.members || []).forEach(m => { if (m?.company) set.add(String(m.company)); else if (m?.organization_name) set.add(String(m.organization_name)); });
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [data.invitations, data.members]);

  const query = (q || '').trim().toLowerCase();

  const filteredInvitations = useMemo(() => {
    const list = Array.isArray(data.invitations) ? data.invitations : [];
    return list.filter(inv => {
      if (companyFilter && String(inv.company || '') !== companyFilter) return false;
      if (invStatusFilter && String(inv.status || '') !== invStatusFilter) return false;
      if (invRoleFilter && String(inv.role || '') !== invRoleFilter) return false;
      if (query) {
        const hay = [inv.email, inv.role, inv.company, inv.status, inv.invited_by].filter(Boolean).join(' ').toLowerCase();
        if (!hay.includes(query)) return false;
      }
      return true;
    });
  }, [data.invitations, companyFilter, invStatusFilter, invRoleFilter, query]);

  const filteredMembers = useMemo(() => {
    const list = Array.isArray(data.members) ? data.members : [];
    return list.filter(m => {
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

  const itemsPerPage = 10;
  const indexOfLastMember   = memberPage * itemsPerPage;
  const indexOfFirstMember  = indexOfLastMember - itemsPerPage;
  const paginatedMembers    = filteredMembers.slice(indexOfFirstMember, indexOfLastMember);
  const totalMemberPages    = Math.ceil(filteredMembers.length / itemsPerPage);
  const indexOfLastInvite   = invitePage * itemsPerPage;
  const indexOfFirstInvite  = indexOfLastInvite - itemsPerPage;
  const paginatedInvites    = filteredInvitations.slice(indexOfFirstInvite, indexOfLastInvite);
  const totalInvitePages    = Math.ceil(filteredInvitations.length / itemsPerPage);

  // ── derived stats ──────────────────────────────────────────────────
  const totalMembers   = (data.members || []).length;
  const activeMembers  = (data.members || []).filter(m => m.is_active !== false).length;
  const deactivated    = totalMembers - activeMembers;
  const pendingInvites = (data.invitations || []).filter(i => i.status === 'pending').length;

  // ── sub-components ─────────────────────────────────────────────────
  const ROLE_BADGE = {
    company_admin:     { label: 'Company Admin', bg: '#ede9fe', color: '#6d28d9' },
    hr_manager:        { label: 'HR Manager',    bg: '#dbeafe', color: '#1d4ed8' },
    hr:                { label: 'HR',            bg: '#e0f2fe', color: '#0369a1' },
    interviewer:       { label: 'Interviewer',   bg: '#dcfce7', color: '#166534' },
    candidate:         { label: 'Candidate',     bg: '#fef9c3', color: '#854d0e' },
    application_admin: { label: 'App Admin',     bg: '#fce7f3', color: '#9d174d' },
  };
  const INV_STATUS_BADGE = {
    pending:   { label: 'Pending',   bg: '#fef9c3', color: '#854d0e', border: '#fde047' },
    accepted:  { label: 'Accepted',  bg: '#dcfce7', color: '#166534', border: '#86efac' },
    cancelled: { label: 'Cancelled', bg: '#f3f4f6', color: '#4b5563', border: '#d1d5db' },
    expired:   { label: 'Expired',   bg: '#fef2f2', color: '#dc2626', border: '#fca5a5' },
  };

  const RoleBadge = ({ role }) => {
    const cfg = ROLE_BADGE[role] || { label: role, bg: '#f3f4f6', color: '#374151' };
    return <span style={{ display: 'inline-block', padding: '3px 10px', borderRadius: 20, background: cfg.bg, color: cfg.color, fontSize: 11, fontWeight: 600, whiteSpace: 'nowrap' }}>{cfg.label}</span>;
  };

  const InvStatusBadge = ({ status }) => {
    const cfg = INV_STATUS_BADGE[status] || { label: status, bg: '#f3f4f6', color: '#4b5563', border: '#d1d5db' };
    return <span style={{ display: 'inline-block', padding: '3px 10px', borderRadius: 20, background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}`, fontSize: 11, fontWeight: 600, whiteSpace: 'nowrap' }}>{cfg.label}</span>;
  };

  const Pagination = ({ page, total, onChange }) => {
    if (total <= 1) return null;
    return (
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 20px', borderTop: '1px solid #f1f5f9' }}>
        <span style={{ fontSize: 12, color: '#6b7280' }}>Page <strong>{page}</strong> of <strong>{total}</strong></span>
        <div style={{ display: 'flex', gap: 6 }}>
          <button onClick={() => onChange(Math.max(page - 1, 1))} disabled={page === 1} style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '6px 12px', borderRadius: 8, border: '1px solid #e5e7eb', background: page === 1 ? '#f9fafb' : '#fff', color: page === 1 ? '#9ca3af' : '#374151', cursor: page === 1 ? 'not-allowed' : 'pointer', fontSize: 12, fontWeight: 500 }}>
            <ChevronLeft size={14} /> Prev
          </button>
          <button onClick={() => onChange(Math.min(page + 1, total))} disabled={page === total} style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '6px 12px', borderRadius: 8, border: '1px solid #e5e7eb', background: page === total ? '#f9fafb' : '#fff', color: page === total ? '#9ca3af' : '#374151', cursor: page === total ? 'not-allowed' : 'pointer', fontSize: 12, fontWeight: 500 }}>
            Next <ChevronRight size={14} />
          </button>
        </div>
      </div>
    );
  };

  const formatDate = (str) => {
    if (!str) return '—';
    try { return new Date(str).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }); }
    catch { return str; }
  };

  // ── render ──────────────────────────────────────────────────────────
  return (
    <div className="dashboard-container">
      <Header />
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '24px 20px 48px' }}>

        {/* Page header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16, marginBottom: 24 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800, color: '#111827', letterSpacing: '-0.02em' }}>Team Members</h1>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: '#6b7280' }}>Manage your organisation's HR team, invitations and offboarding</p>
          </div>
          {canInvite && (
            <button
              onClick={() => setTab(tab === 'invite' ? 'overview' : 'invite')}
              style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px', borderRadius: 10, border: 'none', background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)', color: '#fff', fontWeight: 600, fontSize: 13, cursor: 'pointer', boxShadow: '0 4px 12px rgba(99,102,241,0.3)' }}
            >
              {tab === 'invite' ? <Users size={16} strokeWidth={2.2} /> : <UserPlus size={16} strokeWidth={2.2} />}
              {tab === 'invite' ? 'Members & Invites' : 'Invite Member'}
            </button>
          )}
        </div>

        {!canAccess && (
          <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 12, padding: '14px 18px', color: '#dc2626', fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertTriangle size={16} /> You don't have permission to view this page.
          </div>
        )}

        {canAccess && (
          <>
            {/* Stats bar */}
            {!loading && (
              <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
                {[
                  { label: 'Total Members',   value: totalMembers,   Ic: Users,     bg: '#ede9fe', color: '#6d28d9' },
                  { label: 'Active',          value: activeMembers,  Ic: UserCheck, bg: '#dcfce7', color: '#166534' },
                  { label: 'Deactivated',     value: deactivated,    Ic: UserX,     bg: '#fef2f2', color: '#dc2626' },
                  { label: 'Pending Invites', value: pendingInvites, Ic: Clock,     bg: '#fef9c3', color: '#854d0e' },
                ].map(({ label, value, Ic, bg, color }) => (
                  <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 12, background: '#fff', border: '1px solid #f1f5f9', borderRadius: 14, padding: '14px 20px', flex: '1 1 160px', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
                    <div style={{ width: 40, height: 40, borderRadius: 10, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Ic size={18} color={color} strokeWidth={2} />
                    </div>
                    <div>
                      <div style={{ fontSize: 22, fontWeight: 800, color: '#111827', lineHeight: 1 }}>{value}</div>
                      <div style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>{label}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Left-side tabs */}
            <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 20 }}>
              {canInvite && (
                <button
                  onClick={() => setTab('invite')}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 8, minWidth: 170,
                    padding: '9px 14px', borderRadius: 10, cursor: 'pointer',
                    fontSize: 13, fontWeight: 600,
                    border: tab === 'invite' ? '1px solid #c7d2fe' : '1px solid #e5e7eb',
                    background: tab === 'invite' ? '#eef2ff' : '#fff',
                    color: tab === 'invite' ? '#4338ca' : '#4b5563',
                  }}
                >
                  <UserPlus size={14} /> Invite
                </button>
              )}
              <button
                onClick={() => setTab('overview')}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, minWidth: 170,
                  padding: '9px 14px', borderRadius: 10, cursor: 'pointer',
                  fontSize: 13, fontWeight: 600,
                  border: tab === 'overview' ? '1px solid #c7d2fe' : '1px solid #e5e7eb',
                  background: tab === 'overview' ? '#eef2ff' : '#fff',
                  color: tab === 'overview' ? '#4338ca' : '#4b5563',
                }}
              >
                <Users size={14} /> Members & Invites
              </button>
              <button
                onClick={() => setTab('history')}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, minWidth: 170,
                  padding: '9px 14px', borderRadius: 10, cursor: 'pointer',
                  fontSize: 13, fontWeight: 600,
                  border: tab === 'history' ? '1px solid #c7d2fe' : '1px solid #e5e7eb',
                  background: tab === 'history' ? '#eef2ff' : '#fff',
                  color: tab === 'history' ? '#4338ca' : '#4b5563',
                }}
              >
                <History size={14} /> Transfer History
              </button>
            </div>

            {/* Global error */}
            {error && (
              <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 10, padding: '12px 16px', marginBottom: 16, fontSize: 13, color: '#dc2626', display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertTriangle size={15} /> {error}
              </div>
            )}

            {/* Loading */}
            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, padding: '60px 0', color: '#6b7280', fontSize: 14 }}>
                <Loader2 size={22} color="#a78bfa" style={{ animation: 'spin 1s linear infinite' }} />
                Loading team data…
              </div>
            )}

            {/* ══ INVITE TAB ══ */}
            {!loading && tab === 'invite' && canInvite && (
              <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)', gap: 20, alignItems: 'start' }}>
                {/* Form */}
                <div style={{ background: '#fff', borderRadius: 16, border: '1px solid #e5e7eb', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
                  <div style={{ padding: '18px 24px 14px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 34, height: 34, borderRadius: 9, background: '#ede9fe', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <UserPlus size={16} color="#6d28d9" strokeWidth={2.2} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 15, color: '#111827' }}>Invite a Team Member</div>
                      <div style={{ fontSize: 12, color: '#6b7280' }}>An email invitation will be sent</div>
                    </div>
                  </div>
                  <div style={{ padding: '20px 24px' }}>
                    <div style={{ fontSize: 12, color: '#6b7280', background: '#f8fafc', borderRadius: 8, padding: '8px 12px', marginBottom: 18, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Shield size={12} color="#6b7280" />
                      You can invite: {availableRoles.map(r => r.label).join(', ')}
                    </div>
                    <form onSubmit={handleInvite} style={{ display: 'grid', gap: 14 }}>
                      <div>
                        <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 6 }}>Email Address <span style={{ color: '#ef4444' }}>*</span></label>
                        <div style={{ position: 'relative' }}>
                          <Mail size={15} color="#9ca3af" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                          <input type="email" placeholder="colleague@company.com" value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} disabled={inviting}
                            style={{ width: '100%', padding: '10px 12px 10px 36px', borderRadius: 10, border: `1.5px solid ${fieldErrors.email ? '#fca5a5' : '#e5e7eb'}`, fontSize: 13, outline: 'none', boxSizing: 'border-box', background: inviting ? '#f9fafb' : '#fff' }}
                          />
                        </div>
                        {fieldErrors.email && <div style={{ fontSize: 12, color: '#dc2626', marginTop: 4 }}>{fieldErrors.email}</div>}
                      </div>
                      <div>
                        <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 6 }}>Role</label>
                        <select value={inviteRole} onChange={e => setInviteRole(e.target.value)} disabled={inviting}
                          style={{ width: '100%', padding: '10px 12px', borderRadius: 10, border: `1.5px solid ${fieldErrors.role ? '#fca5a5' : '#e5e7eb'}`, fontSize: 13, outline: 'none', background: inviting ? '#f9fafb' : '#fff', cursor: 'pointer' }}
                        >
                          <option value="" disabled>Select the role</option>
                          {availableRoles.map(role => <option key={role.value} value={role.value}>{role.label}</option>)}
                        </select>
                        {fieldErrors.role && <div style={{ fontSize: 12, color: '#dc2626', marginTop: 4 }}>{fieldErrors.role}</div>}
                      </div>
                      <button type="submit" disabled={inviting} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: '11px 0', borderRadius: 10, border: 'none', background: inviting ? '#c7d2fe' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)', color: '#fff', fontWeight: 600, fontSize: 14, cursor: inviting ? 'not-allowed' : 'pointer' }}>
                        {inviting ? <><Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> Sending…</> : <><Send size={15} /> Send Invitation</>}
                      </button>
                    </form>
                  </div>
                </div>

                {/* Info / result */}
                <div style={{ background: '#fff', borderRadius: 16, border: '1px solid #e5e7eb', padding: '20px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
                  {inviteResult ? (
                    <>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                        <CheckCircle2 size={22} color="#16a34a" />
                        <span style={{ fontWeight: 700, fontSize: 15, color: '#111827' }}>Invitation Sent!</span>
                      </div>
                      <div style={{ fontSize: 13, color: '#374151', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 10, padding: '10px 14px', marginBottom: 10 }}>
                        Email sent: <strong>{String(inviteResult.email_sent)}</strong>
                      </div>
                      {inviteResult.activation_link && (
                        <div style={{ marginTop: 10 }}>
                          <div style={{ fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 4 }}>Activation Link (dev)</div>
                          <div style={{ fontSize: 11, wordBreak: 'break-all', color: '#6366f1', background: '#f5f3ff', padding: '8px 10px', borderRadius: 8 }}>{inviteResult.activation_link}</div>
                        </div>
                      )}
                      {inviteResult.temp_password && (
                        <div style={{ marginTop: 10 }}>
                          <div style={{ fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 4 }}>Temp Password (dev)</div>
                          <div style={{ fontSize: 12, fontFamily: 'monospace', background: '#fef9c3', padding: '8px 10px', borderRadius: 8 }}>{inviteResult.temp_password}</div>
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      <div style={{ fontWeight: 700, fontSize: 14, color: '#111827', marginBottom: 14 }}>How invitations work</div>
                      {[
                        { Ic: Send,           text: 'An email is sent to the invitee with a secure link' },
                        { Ic: UserCheck,      text: 'They register and their account is created under your hierarchy' },
                        { Ic: Shield,         text: 'Their role determines what data they can access' },
                        { Ic: ArrowRightLeft, text: 'You can replace or offboard them later from the Members table' },
                      ].map(({ Ic, text }, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, marginBottom: 12 }}>
                          <div style={{ width: 28, height: 28, borderRadius: 8, background: '#ede9fe', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                            <Ic size={14} color="#6d28d9" strokeWidth={2} />
                          </div>
                          <div style={{ fontSize: 13, color: '#374151', paddingTop: 4 }}>{text}</div>
                        </div>
                      ))}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* ══ HISTORY TAB ══ */}
            {!loading && tab === 'history' && (
              <div style={{ background: '#fff', borderRadius: 16, border: '1px solid #e5e7eb', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
                <div style={{ padding: '16px 20px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 32, height: 32, borderRadius: 8, background: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <History size={15} color="#64748b" strokeWidth={2.2} />
                  </div>
                  <span style={{ fontWeight: 700, fontSize: 15, color: '#111827' }}>Ownership Transfer History</span>
                </div>

                {loadingLogs ? (
                  <div style={{ padding: '40px 0', textAlign: 'center', color: '#6b7280' }}>
                    <Loader2 size={24} style={{ animation: 'spin 1s linear infinite', marginBottom: 8 }} />
                    <div style={{ fontSize: 13 }}>Loading history...</div>
                  </div>
                ) : logs.length === 0 ? (
                  <div style={{ padding: '60px 20px', textAlign: 'center' }}>
                    <div style={{ width: 48, height: 48, borderRadius: '50%', background: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px' }}>
                      <History size={24} color="#cbd5e1" />
                    </div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: '#374151' }}>No transfer history found</div>
                    <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>History of team member replacements will appear here</div>
                  </div>
                ) : (
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                      <thead>
                        <tr style={{ background: '#f8fafc' }}>
                          <th style={{ textAlign: 'left', padding: '10px 20px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Date</th>
                          <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Transferred From</th>
                          <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Transferred To</th>
                          <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Transferred By</th>
                          <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</th>
                          <th style={{ textAlign: 'left', padding: '10px 20px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Reason</th>
                        </tr>
                      </thead>
                      <tbody>
                        {logs.map(log => (
                          <tr key={log.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                            <td style={{ padding: '12px 20px', whiteSpace: 'nowrap' }}>
                              <div style={{ fontSize: 13, fontWeight: 600, color: '#111827' }}>{formatDate(log.transferred_at)}</div>
                              <div style={{ fontSize: 11, color: '#9ca3af' }}>{new Date(log.transferred_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                            </td>
                            <td style={{ padding: '12px 16px' }}>
                              <div style={{ fontSize: 13, color: '#374151', fontWeight: 500 }}>{log.from_name}</div>
                              <div style={{ fontSize: 11, color: '#6b7280' }}>{log.from_email}</div>
                            </td>
                            <td style={{ padding: '12px 16px' }}>
                              <div style={{ fontSize: 13, color: '#374151', fontWeight: 500 }}>{log.to_name}</div>
                              <div style={{ fontSize: 11, color: '#6b7280' }}>{log.to_email}</div>
                            </td>
                            <td style={{ padding: '12px 16px' }}>
                              <div style={{ fontSize: 12, color: '#6b7280' }}>{log.by_name}</div>
                            </td>
                            <td style={{ padding: '12px 16px' }}>
                              {log.also_deactivated && (
                                <span style={{ padding: '2px 8px', borderRadius: 4, background: '#fee2e2', color: '#991b1b', fontSize: 11, fontWeight: 600 }}>Deactivated</span>
                              )}
                            </td>
                            <td style={{ padding: '12px 20px', fontSize: 12, color: '#6b7280', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {log.transfer_reason || '—'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* ══ OVERVIEW TAB ══ */}
            {!loading && tab === 'overview' && (
              <div style={{ display: 'grid', gap: 20 }}>

                {/* Filter bar */}
                <div style={{ background: '#fff', borderRadius: 14, border: '1px solid #e5e7eb', padding: '14px 18px', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                    <Filter size={14} color="#6b7280" />
                    <span style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>Filter & Search</span>
                    {(q || companyFilter || memberRoleFilter || invStatusFilter || invRoleFilter) && (
                      <button onClick={() => { setQ(''); setCompanyFilter(''); setMemberRoleFilter(''); setInvStatusFilter(''); setInvRoleFilter(''); }}
                        style={{ marginLeft: 'auto', fontSize: 11, color: '#6366f1', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>
                        Clear all
                      </button>
                    )}
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                    <div style={{ position: 'relative', flex: '2 1 220px' }}>
                      <Search size={14} color="#9ca3af" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                      <input placeholder="Search name, email, role…" value={q} onChange={e => setQ(e.target.value)}
                        style={{ width: '100%', padding: '9px 12px 9px 32px', borderRadius: 9, border: '1.5px solid #e5e7eb', fontSize: 13, outline: 'none', boxSizing: 'border-box' }} />
                    </div>
                    {data.scope === 'all' && (
                      <div style={{ position: 'relative', flex: '1 1 160px' }}>
                        <Building2 size={14} color="#9ca3af" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                        <select value={companyFilter} onChange={e => setCompanyFilter(e.target.value)}
                          style={{ width: '100%', padding: '9px 12px 9px 32px', borderRadius: 9, border: '1.5px solid #e5e7eb', fontSize: 13, outline: 'none', cursor: 'pointer', boxSizing: 'border-box' }}>
                          <option value="">All Companies</option>
                          {companyOptions.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </div>
                    )}
                    <div style={{ position: 'relative', flex: '1 1 160px' }}>
                      <Shield size={14} color="#9ca3af" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                      <select value={memberRoleFilter} onChange={e => setMemberRoleFilter(e.target.value)}
                        style={{ width: '100%', padding: '9px 12px 9px 32px', borderRadius: 9, border: '1.5px solid #e5e7eb', fontSize: 13, outline: 'none', cursor: 'pointer', boxSizing: 'border-box' }}>
                        <option value="">All Roles</option>
                        <option value="company_admin">Company Admin</option>
                        <option value="hr_manager">HR Manager</option>
                        <option value="hr">HR</option>
                        <option value="interviewer">Interviewer</option>
                        {data.scope === 'all' && <option value="application_admin">App Admin</option>}
                      </select>
                    </div>
                    <div style={{ position: 'relative', flex: '1 1 150px' }}>
                      <Clock size={14} color="#9ca3af" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }} />
                      <select value={invStatusFilter} onChange={e => setInvStatusFilter(e.target.value)}
                        style={{ width: '100%', padding: '9px 12px 9px 32px', borderRadius: 9, border: '1.5px solid #e5e7eb', fontSize: 13, outline: 'none', cursor: 'pointer', boxSizing: 'border-box' }}>
                        <option value="">Invite Status</option>
                        <option value="pending">Pending</option>
                        <option value="accepted">Accepted</option>
                        <option value="cancelled">Cancelled</option>
                        <option value="expired">Expired</option>
                      </select>
                    </div>
                  </div>
                  <div style={{ marginTop: 10, fontSize: 12, color: '#6b7280' }}>
                    Found <strong>{filteredMembers.length}</strong> member{filteredMembers.length !== 1 ? 's' : ''} &amp; <strong>{filteredInvitations.length}</strong> invitation{filteredInvitations.length !== 1 ? 's' : ''}
                  </div>
                </div>

                {/* Members table */}
                <div style={{ background: '#fff', borderRadius: 16, border: '1px solid #e5e7eb', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
                  <div style={{ padding: '16px 20px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: '#ede9fe', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Users size={15} color="#6d28d9" strokeWidth={2.2} />
                    </div>
                    <span style={{ fontWeight: 700, fontSize: 15, color: '#111827' }}>Team Members</span>
                    <span style={{ fontSize: 12, color: '#6b7280', background: '#f3f4f6', padding: '2px 8px', borderRadius: 20 }}>{filteredMembers.length}</span>
                  </div>

                  {filteredMembers.length > 0 ? (
                    <>
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                          <thead>
                            <tr style={{ background: '#f8fafc' }}>
                              <th style={{ textAlign: 'left', padding: '10px 20px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>Member</th>
                              <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Role</th>
                              <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Company</th>
                              <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</th>
                              {canOffboard && <th style={{ textAlign: 'right', padding: '10px 20px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Action</th>}
                            </tr>
                          </thead>
                          <tbody>
                            {paginatedMembers.map(m => {
                              const fullName = [m.first_name, m.last_name].filter(Boolean).join(' ') || m.email;
                              const isDeactivated = m.is_active === false;
                              return (
                                <tr key={m.id}
                                  style={{ opacity: isDeactivated ? 0.6 : 1, background: isDeactivated ? '#fafafa' : '#fff', borderBottom: '1px solid #f3f4f6' }}
                                  onMouseEnter={e => { if (!isDeactivated) e.currentTarget.style.background = '#fafbff'; }}
                                  onMouseLeave={e => { e.currentTarget.style.background = isDeactivated ? '#fafafa' : '#fff'; }}
                                >
                                  <td style={{ padding: '12px 20px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                      <Avatar name={fullName} size={36} />
                                      <div>
                                        <div style={{ fontWeight: 600, color: '#111827', fontSize: 13 }}>{fullName}</div>
                                        <div style={{ fontSize: 11, color: '#6b7280', marginTop: 1 }}>{m.email}</div>
                                      </div>
                                    </div>
                                  </td>
                                  <td style={{ padding: '12px 16px' }}><RoleBadge role={m.role} /></td>
                                  <td style={{ padding: '12px 16px', fontSize: 12, color: '#374151' }}>{m.company || m.organization_name || '—'}</td>
                                  <td style={{ padding: '12px 16px' }}>
                                    {isDeactivated ? (
                                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 10px', borderRadius: 20, background: '#fef2f2', color: '#dc2626', fontSize: 11, fontWeight: 600, border: '1px solid #fca5a5' }}>
                                        <UserX size={11} /> Deactivated
                                      </span>
                                    ) : (
                                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 10px', borderRadius: 20, background: '#f0fdf4', color: '#16a34a', fontSize: 11, fontWeight: 600, border: '1px solid #86efac' }}>
                                        <UserCheck size={11} /> Active
                                      </span>
                                    )}
                                  </td>
                                  {canOffboard && (
                                    <td style={{ padding: '12px 20px', textAlign: 'right' }}>
                                      {isOffboardable(m) && (
                                        <button onClick={() => setOffboardingMember(m)}
                                          style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 8, border: '1px solid #fed7aa', background: '#fff7ed', color: '#c2410c', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}
                                          onMouseEnter={e => (e.currentTarget.style.background = '#ffedd5')}
                                          onMouseLeave={e => (e.currentTarget.style.background = '#fff7ed')}
                                        >
                                          <ArrowRightLeft size={13} strokeWidth={2.2} /> Replace
                                        </button>
                                      )}
                                    </td>
                                  )}
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                      <Pagination page={memberPage} total={totalMemberPages} onChange={setMemberPage} />
                    </>
                  ) : (
                    <div style={{ padding: '48px 20px', textAlign: 'center' }}>
                      <Users size={36} color="#e5e7eb" style={{ marginBottom: 10 }} />
                      <div style={{ fontSize: 14, fontWeight: 600, color: '#374151' }}>No members found</div>
                      <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>Try adjusting your filters</div>
                    </div>
                  )}
                </div>

                {/* Invitations table */}
                <div style={{ background: '#fff', borderRadius: 16, border: '1px solid #e5e7eb', overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
                  <div style={{ padding: '16px 20px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: '#dbeafe', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Mail size={15} color="#1d4ed8" strokeWidth={2.2} />
                    </div>
                    <span style={{ fontWeight: 700, fontSize: 15, color: '#111827' }}>Invitations</span>
                    <span style={{ fontSize: 12, color: '#6b7280', background: '#f3f4f6', padding: '2px 8px', borderRadius: 20 }}>{filteredInvitations.length}</span>
                  </div>

                  {filteredInvitations.length > 0 ? (
                    <>
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                          <thead>
                            <tr style={{ background: '#f8fafc' }}>
                              <th style={{ textAlign: 'left', padding: '10px 20px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Invitee</th>
                              <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Role</th>
                              {data.scope === 'all' && <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Company</th>}
                              <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</th>
                              <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Invited By</th>
                              <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Expires</th>
                              {canInvite && <th style={{ textAlign: 'right', padding: '10px 20px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Actions</th>}
                            </tr>
                          </thead>
                          <tbody>
                            {paginatedInvites.map(inv => (
                              <tr key={inv.id} style={{ borderBottom: '1px solid #f3f4f6' }}
                                onMouseEnter={e => (e.currentTarget.style.background = '#fafbff')}
                                onMouseLeave={e => (e.currentTarget.style.background = '#fff')}
                              >
                                <td style={{ padding: '12px 20px' }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                    <Avatar name={inv.email} size={32} />
                                    <span style={{ fontSize: 13, color: '#374151', fontWeight: 500 }}>{inv.email}</span>
                                  </div>
                                </td>
                                <td style={{ padding: '12px 16px' }}><RoleBadge role={inv.role} /></td>
                                {data.scope === 'all' && <td style={{ padding: '12px 16px', fontSize: 12, color: '#374151' }}>{inv.company || '—'}</td>}
                                <td style={{ padding: '12px 16px' }}><InvStatusBadge status={inv.status} /></td>
                                <td style={{ padding: '12px 16px', fontSize: 12, color: '#374151' }}>{inv.invited_by || '—'}</td>
                                <td style={{ padding: '12px 16px', fontSize: 12, color: '#6b7280' }}>{formatDate(inv.expires_at)}</td>
                                {canInvite && (
                                  <td style={{ padding: '12px 20px', textAlign: 'right' }}>
                                    <div style={{ display: 'inline-flex', gap: 6 }}>
                                      <button onClick={() => handleResendInvite(inv.token)} disabled={inv.status !== 'pending'} title="Resend invitation"
                                        style={{ width: 32, height: 32, borderRadius: 8, border: 'none', background: inv.status !== 'pending' ? '#f3f4f6' : '#dbeafe', color: inv.status !== 'pending' ? '#9ca3af' : '#1d4ed8', cursor: inv.status !== 'pending' ? 'not-allowed' : 'pointer', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <RotateCcw size={14} strokeWidth={2.2} />
                                      </button>
                                      <button onClick={() => handleCancelInvite(inv.token)} disabled={inv.status !== 'pending'} title="Cancel invitation"
                                        style={{ width: 32, height: 32, borderRadius: 8, border: 'none', background: inv.status !== 'pending' ? '#f3f4f6' : '#fef2f2', color: inv.status !== 'pending' ? '#9ca3af' : '#dc2626', cursor: inv.status !== 'pending' ? 'not-allowed' : 'pointer', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <XCircle size={14} strokeWidth={2.2} />
                                      </button>
                                    </div>
                                  </td>
                                )}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      <Pagination page={invitePage} total={totalInvitePages} onChange={setInvitePage} />
                    </>
                  ) : (
                    <div style={{ padding: '48px 20px', textAlign: 'center' }}>
                      <Mail size={36} color="#e5e7eb" style={{ marginBottom: 10 }} />
                      <div style={{ fontSize: 14, fontWeight: 600, color: '#374151' }}>No invitations found</div>
                      <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>Send an invite from the Invite tab</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {offboardingMember ? (
        <TransferModal
          member={offboardingMember}
          onClose={() => setOffboardingMember(null)}
          onSuccess={async () => { setOffboardingMember(null); await load(); }}
          authHeader={authHeader}
        />
      ) : null}
    </div>
  );
}
