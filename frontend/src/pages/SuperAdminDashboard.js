import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

const STATUS_TABS = [
    { key: 'all', label: 'All Companies', icon: '🏢' },
    { key: 'pending', label: 'Pending', icon: '⏳' },
    { key: 'approved', label: 'Approved', icon: '✅' },
    { key: 'rejected', label: 'Rejected', icon: '❌' },
];

const STATUS_COLORS = {
    pending: { bg: '#fef3c7', text: '#92400e', border: '#fbbf24' },
    approved: { bg: '#d1fae5', text: '#065f46', border: '#34d399' },
    rejected: { bg: '#fee2e2', text: '#991b1b', border: '#f87171' },
};

function StatusBadge({ status }) {
    const c = STATUS_COLORS[status] || { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
    return (
        <span style={{
            padding: '3px 12px',
            borderRadius: '999px',
            fontSize: '0.75rem',
            fontWeight: 700,
            letterSpacing: '0.03em',
            background: c.bg,
            color: c.text,
            border: `1px solid ${c.border}`,
            textTransform: 'capitalize',
        }}>
            {status}
        </span>
    );
}

function Toast({ message, type, onClose }) {
    useEffect(() => {
        const t = setTimeout(onClose, 4000);
        return () => clearTimeout(t);
    }, [onClose]);
    return (
        <div style={{
            position: 'fixed', bottom: 30, right: 30, zIndex: 9999,
            padding: '14px 22px',
            borderRadius: 12,
            background: type === 'success' ? '#065f46' : '#991b1b',
            color: '#fff',
            fontWeight: 600,
            fontSize: '0.9rem',
            boxShadow: '0 8px 30px rgba(0,0,0,0.25)',
            display: 'flex', alignItems: 'center', gap: 10,
            animation: 'slideIn 0.3s ease',
        }}>
            <span>{type === 'success' ? '✅' : '❌'}</span>
            {message}
        </div>
    );
}

function RejectModal({ company, onConfirm, onCancel }) {
    const [reason, setReason] = useState('');
    return (
        <div style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)',
            zIndex: 8000, display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
            <div style={{
                background: '#fff', borderRadius: 16, padding: '2rem',
                width: '100%', maxWidth: 480, boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
            }}>
                <h3 style={{ margin: '0 0 0.5rem', color: '#991b1b' }}>Reject Company</h3>
                <p style={{ color: '#6b7280', marginBottom: '1rem', fontSize: '0.9rem' }}>
                    You are about to reject <strong>{company.name}</strong>. An email will be sent to the company admin.
                </p>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: 6, fontSize: '0.85rem' }}>
                    Reason (optional)
                </label>
                <textarea
                    value={reason}
                    onChange={e => setReason(e.target.value)}
                    placeholder="e.g. Invalid business domain, duplicate registration, etc."
                    rows={3}
                    style={{
                        width: '100%', padding: '10px 12px', borderRadius: 8,
                        border: '1px solid #d1d5db', fontSize: '0.9rem', resize: 'vertical',
                        outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box',
                    }}
                />
                <div style={{ display: 'flex', gap: 12, marginTop: '1.25rem', justifyContent: 'flex-end' }}>
                    <button onClick={onCancel} style={{
                        padding: '9px 20px', borderRadius: 8, border: '1px solid #d1d5db',
                        background: '#f9fafb', fontWeight: 600, cursor: 'pointer', fontSize: '0.9rem',
                    }}>Cancel</button>
                    <button onClick={() => onConfirm(reason)} style={{
                        padding: '9px 20px', borderRadius: 8, border: 'none',
                        background: '#dc2626', color: '#fff', fontWeight: 600, cursor: 'pointer', fontSize: '0.9rem',
                    }}>Reject Company</button>
                </div>
            </div>
        </div>
    );
}

function CompanyCard({ company, onApprove, onReject, onImpersonate, actionLoading, impersonateLoading }) {
    const admin = company.primary_admin;
    const isLoading = actionLoading === company.id;
    const isImpersonating = impersonateLoading === company.id;
    const canImpersonate = company.approval_status === 'approved';

    return (
        <div style={{
            background: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: 14,
            padding: '1.25rem 1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '1.25rem',
            transition: 'box-shadow 0.2s',
            boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
        }}
            onMouseEnter={e => e.currentTarget.style.boxShadow = '0 4px 18px rgba(0,0,0,0.10)'}
            onMouseLeave={e => e.currentTarget.style.boxShadow = '0 1px 4px rgba(0,0,0,0.06)'}
        >
            {/* Company Avatar */}
            <div style={{
                width: 52, height: 52, borderRadius: 12,
                background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: '#fff', fontWeight: 700, fontSize: '1.4rem', flexShrink: 0,
            }}>
                {company.name.charAt(0).toUpperCase()}
            </div>

            {/* Company Info */}
            <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                    {/* Clickable company name triggers impersonation */}
                    <button
                        onClick={() => canImpersonate && onImpersonate(company)}
                        disabled={!canImpersonate || isImpersonating}
                        title={canImpersonate ? `View all data for ${company.name}` : 'Approve company first to view its data'}
                        style={{
                            background: 'none', border: 'none', padding: 0, margin: 0,
                            fontWeight: 700, fontSize: '1rem',
                            color: canImpersonate ? '#4f46e5' : '#111827',
                            cursor: canImpersonate && !isImpersonating ? 'pointer' : 'not-allowed',
                            textDecoration: canImpersonate ? 'underline' : 'none',
                            textDecorationStyle: 'dotted',
                            opacity: (!canImpersonate) ? 0.7 : 1,
                            display: 'flex', alignItems: 'center', gap: 5,
                        }}
                    >
                        {isImpersonating ? '⏳ Opening...' : company.name}
                        {canImpersonate && !isImpersonating && (
                            <span style={{ fontSize: '0.7rem', color: '#7c3aed', fontWeight: 900 }}>↗</span>
                        )}
                    </button>
                    <StatusBadge status={company.approval_status} />
                </div>
                {company.domain && (
                    <div style={{ fontSize: '0.8rem', color: '#6b7280', marginTop: 2 }}>🌐 {company.domain}</div>
                )}
                {admin && (
                    <div style={{ fontSize: '0.82rem', color: '#374151', marginTop: 4 }}>
                        <span style={{ fontWeight: 600 }}>👤 {admin.first_name} {admin.last_name}</span>
                        <span style={{ margin: '0 8px', color: '#d1d5db' }}>|</span>
                        <span>✉️ {admin.email}</span>
                    </div>
                )}
                <div style={{ display: 'flex', gap: 16, marginTop: 4, flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.78rem', color: '#9ca3af' }}>
                        📅 Registered: {new Date(company.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </span>
                    <span style={{ fontSize: '0.78rem', color: '#9ca3af' }}>
                        👥 {company.user_count} user{company.user_count !== 1 ? 's' : ''}
                    </span>
                    {company.approval_status === 'approved' && company.approved_at && (
                        <span style={{ fontSize: '0.78rem', color: '#059669' }}>
                            ✅ Approved: {new Date(company.approved_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                        </span>
                    )}
                    {company.approval_status === 'rejected' && company.rejected_reason && (
                        <span style={{ fontSize: '0.78rem', color: '#dc2626' }}>
                            Reason: {company.rejected_reason}
                        </span>
                    )}
                </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                {company.approval_status !== 'approved' && (
                    <button
                        disabled={isLoading}
                        onClick={() => onApprove(company)}
                        style={{
                            padding: '8px 18px', borderRadius: 8, border: 'none',
                            background: isLoading ? '#d1fae5' : 'linear-gradient(135deg, #059669, #10b981)',
                            color: '#fff', fontWeight: 700, cursor: isLoading ? 'wait' : 'pointer',
                            fontSize: '0.85rem', transition: 'opacity 0.2s',
                            opacity: isLoading ? 0.7 : 1,
                        }}
                    >
                        {isLoading ? '...' : '✅ Approve'}
                    </button>
                )}
                {company.approval_status !== 'rejected' && (
                    <button
                        disabled={isLoading}
                        onClick={() => onReject(company)}
                        style={{
                            padding: '8px 18px', borderRadius: 8,
                            border: '1px solid #fca5a5',
                            background: '#fff', color: '#dc2626',
                            fontWeight: 700, cursor: isLoading ? 'wait' : 'pointer',
                            fontSize: '0.85rem', transition: 'all 0.2s',
                            opacity: isLoading ? 0.7 : 1,
                        }}
                    >
                        ❌ Reject
                    </button>
                )}
            </div>
        </div>
    );
}

function SuperAdminDashboard() {
    const [activeTab, setActiveTab] = useState('pending');
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null);
    const [impersonateLoading, setImpersonateLoading] = useState(null);
    const [rejectTarget, setRejectTarget] = useState(null);
    const [toast, setToast] = useState(null);
    const [search, setSearch] = useState('');

    // Get current user info
    const user = (() => { try { return JSON.parse(localStorage.getItem('user') || '{}'); } catch { return {}; } })();

    const fetchCompanies = useCallback(async (tabStatus) => {
        setLoading(true);
        try {
            const params = tabStatus !== 'all' ? `?status=${tabStatus}` : '';
            const res = await axios.get(`${API_BASE_URL}/superadmin/companies/${params}`);
            setCompanies(res.data.companies || []);
        } catch (err) {
            setToast({ type: 'error', message: err.response?.data?.error || 'Failed to load companies.' });
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchCompanies(activeTab);
    }, [activeTab, fetchCompanies]);

    const handleApprove = async (company) => {
        setActionLoading(company.id);
        try {
            await axios.post(`${API_BASE_URL}/superadmin/companies/${company.id}/approve/`);
            setToast({ type: 'success', message: `"${company.name}" has been approved!` });
            fetchCompanies(activeTab);
        } catch (err) {
            setToast({ type: 'error', message: err.response?.data?.error || 'Failed to approve company.' });
        } finally {
            setActionLoading(null);
        }
    };

    const handleRejectConfirm = async (reason) => {
        if (!rejectTarget) return;
        const company = rejectTarget;
        setRejectTarget(null);
        setActionLoading(company.id);
        try {
            await axios.post(`${API_BASE_URL}/superadmin/companies/${company.id}/reject/`, { reason });
            setToast({ type: 'success', message: `"${company.name}" has been rejected.` });
            fetchCompanies(activeTab);
        } catch (err) {
            setToast({ type: 'error', message: err.response?.data?.error || 'Failed to reject company.' });
        } finally {
            setActionLoading(null);
        }
    };

    const handleLogout = () => {
        localStorage.clear();
        window.location.href = '/login';
    };

    const handleImpersonate = async (company) => {
        setImpersonateLoading(company.id);
        try {
            const res = await axios.post(`${API_BASE_URL}/superadmin/companies/${company.id}/impersonate/`);
            const { token, refresh, impersonated_user } = res.data;

            // Save superadmin's original session
            localStorage.setItem('superadmin_token', localStorage.getItem('authToken') || '');
            localStorage.setItem('superadmin_user', localStorage.getItem('user') || '{}');

            // Set impersonation flag and company info
            localStorage.setItem('impersonation_active', 'true');
            localStorage.setItem('impersonation_company', JSON.stringify({ id: company.id, name: company.name }));

            // Swap to company admin's token
            localStorage.setItem('authToken', token);
            if (refresh) localStorage.setItem('refreshToken', refresh);
            localStorage.setItem('user', JSON.stringify(impersonated_user));

            // Hard reload so ImpersonationBanner detects the flag immediately on mount
            window.location.href = '/dashboard';
        } catch (err) {
            setToast({ type: 'error', message: err.response?.data?.error || 'Failed to open company view.' });
            setImpersonateLoading(null);
        }
    };

    const filtered = companies.filter(c =>
        c.name.toLowerCase().includes(search.toLowerCase()) ||
        (c.primary_admin?.email || '').toLowerCase().includes(search.toLowerCase()) ||
        (c.domain || '').toLowerCase().includes(search.toLowerCase())
    );

    const tabCounts = {}; // we show counts from current fetched list only for the active tab
    STATUS_TABS.forEach(t => { tabCounts[t.key] = t.key === activeTab ? companies.length : '–'; });

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 50%, #f0fdf4 100%)',
            fontFamily: "'Inter', 'Segoe UI', sans-serif",
        }}>
            <style>{`
        @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: transparent; } ::-webkit-scrollbar-thumb { background: #c4b5fd; border-radius: 3px; }
      `}</style>

            {/* Header */}
            <header style={{
                background: 'rgba(255,255,255,0.9)',
                backdropFilter: 'blur(12px)',
                borderBottom: '1px solid #e9d5ff',
                padding: '0 2rem',
                height: 64,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                position: 'sticky',
                top: 0,
                zIndex: 100,
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    <div style={{
                        width: 36, height: 36, borderRadius: 10,
                        background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: '#fff', fontWeight: 800, fontSize: '1rem',
                    }}>V</div>
                    <div>
                        <div style={{ fontWeight: 800, fontSize: '1.05rem', color: '#1e1b4b' }}>VeriFiHire</div>
                        <div style={{ fontSize: '0.7rem', color: '#7c3aed', fontWeight: 600, letterSpacing: '0.04em' }}>PLATFORM ADMIN</div>
                    </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#1e1b4b' }}>
                            {user.first_name || 'Platform'} {user.last_name || 'Admin'}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#7c3aed' }}>Superadministrator</div>
                    </div>
                    <button onClick={handleLogout} style={{
                        padding: '7px 16px', borderRadius: 8,
                        border: '1px solid #e9d5ff', background: '#fff',
                        color: '#7c3aed', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem',
                    }}>Logout</button>
                </div>
            </header>

            {/* Main Content */}
            <main style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 1.5rem' }}>

                {/* Page Title */}
                <div style={{ marginBottom: '2rem' }}>
                    <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 800, color: '#1e1b4b' }}>
                        Company Approvals
                    </h1>
                    <p style={{ margin: '6px 0 0', color: '#6b7280', fontSize: '0.95rem' }}>
                        Review and manage company registration requests from the VeriFiHire platform.
                    </p>
                </div>

                {/* Tabs + Search */}
                <div style={{
                    display: 'flex', gap: 12, flexWrap: 'wrap',
                    alignItems: 'center', justifyContent: 'space-between',
                    marginBottom: '1.5rem',
                }}>
                    {/* Status Tabs */}
                    <div style={{
                        display: 'flex', gap: 6,
                        background: '#fff',
                        borderRadius: 10,
                        padding: 4,
                        border: '1px solid #e9d5ff',
                        boxShadow: '0 1px 4px rgba(124,58,237,0.08)',
                    }}>
                        {STATUS_TABS.map(tab => (
                            <button
                                key={tab.key}
                                onClick={() => { setActiveTab(tab.key); setSearch(''); }}
                                style={{
                                    padding: '7px 16px',
                                    borderRadius: 7,
                                    border: 'none',
                                    background: activeTab === tab.key
                                        ? 'linear-gradient(135deg, #7c3aed, #4f46e5)'
                                        : 'transparent',
                                    color: activeTab === tab.key ? '#fff' : '#6b7280',
                                    fontWeight: activeTab === tab.key ? 700 : 500,
                                    cursor: 'pointer',
                                    fontSize: '0.85rem',
                                    transition: 'all 0.2s',
                                    whiteSpace: 'nowrap',
                                }}
                            >
                                {tab.icon} {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Search */}
                    <div style={{ position: 'relative' }}>
                        <span style={{
                            position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
                            fontSize: '1rem', color: '#9ca3af',
                        }}>🔍</span>
                        <input
                            type="text"
                            placeholder="Search company or email..."
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            style={{
                                padding: '9px 14px 9px 36px',
                                borderRadius: 9,
                                border: '1px solid #e9d5ff',
                                fontSize: '0.9rem',
                                outline: 'none',
                                width: 250,
                                background: '#fff',
                            }}
                        />
                    </div>
                </div>

                {/* Stats Row */}
                <div style={{
                    display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: 12, marginBottom: '1.75rem',
                }}>
                    {[
                        { label: 'Showing', value: filtered.length, color: '#4f46e5' },
                        { label: 'Pending', value: companies.filter(c => c.approval_status === 'pending').length, color: '#d97706' },
                        { label: 'Approved', value: companies.filter(c => c.approval_status === 'approved').length, color: '#059669' },
                        { label: 'Rejected', value: companies.filter(c => c.approval_status === 'rejected').length, color: '#dc2626' },
                    ].map(s => (
                        <div key={s.label} style={{
                            background: '#fff', borderRadius: 12, padding: '1rem 1.25rem',
                            border: '1px solid #e5e7eb',
                            boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
                        }}>
                            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: s.color }}>{s.value}</div>
                            <div style={{ fontSize: '0.8rem', color: '#6b7280', marginTop: 2 }}>{s.label}</div>
                        </div>
                    ))}
                </div>

                {/* Company List */}
                {loading ? (
                    <div style={{ textAlign: 'center', padding: '4rem', color: '#9ca3af', fontSize: '1rem' }}>
                        <div style={{ fontSize: '2rem', marginBottom: 12 }}>⏳</div>
                        Loading companies...
                    </div>
                ) : filtered.length === 0 ? (
                    <div style={{
                        textAlign: 'center', padding: '4rem',
                        background: '#fff', borderRadius: 16, border: '1px solid #e5e7eb',
                        color: '#9ca3af',
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: 12 }}>
                            {activeTab === 'pending' ? '🎉' : '🔍'}
                        </div>
                        <div style={{ fontWeight: 600, fontSize: '1.1rem', marginBottom: 6, color: '#374151' }}>
                            {activeTab === 'pending' ? 'No pending approvals!' : 'No companies found'}
                        </div>
                        <div style={{ fontSize: '0.9rem' }}>
                            {activeTab === 'pending'
                                ? 'All company registrations have been reviewed.'
                                : 'Try adjusting your search or filter.'}
                        </div>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {filtered.map(company => (
                            <CompanyCard
                                key={company.id}
                                company={company}
                                onApprove={handleApprove}
                                onReject={setRejectTarget}
                                onImpersonate={handleImpersonate}
                                actionLoading={actionLoading}
                                impersonateLoading={impersonateLoading}
                            />
                        ))}
                    </div>
                )}
            </main>

            {/* Reject Modal */}
            {rejectTarget && (
                <RejectModal
                    company={rejectTarget}
                    onConfirm={handleRejectConfirm}
                    onCancel={() => setRejectTarget(null)}
                />
            )}

            {/* Toast */}
            {toast && (
                <Toast
                    message={toast.message}
                    type={toast.type}
                    onClose={() => setToast(null)}
                />
            )}
        </div>
    );
}

export default SuperAdminDashboard;
