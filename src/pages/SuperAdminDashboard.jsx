import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

const STATUS_TABS = [
    { key: 'pending_users', label: 'User Access', icon: '👤' },
    { key: 'pending_companies', label: 'Company Requests', icon: '🏢' },
    { key: 'all_users', label: 'Users List', icon: '📋' },
    { key: 'all_companies', label: 'Organization Index', icon: '🏢' },
];

const STATUS_COLORS = {
    pending: { bg: 'rgba(255, 181, 71, 0.12)', text: '#FFB547', border: 'rgba(255, 181, 71, 0.2)' },
    approved: { bg: 'rgba(5, 205, 153, 0.12)', text: '#05CD99', border: 'rgba(5, 205, 153, 0.2)' },
    rejected: { bg: 'rgba(238, 93, 80, 0.12)', text: '#EE5D50', border: 'rgba(238, 93, 80, 0.2)' },
};

function StatusBadge({ status }) {
    const c = STATUS_COLORS[status] || { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
    return (
        <span style={{
            padding: '4px 12px',
            borderRadius: '999px',
            fontSize: '0.7rem',
            fontWeight: 700,
            letterSpacing: '0.03em',
            background: c.bg,
            color: c.text,
            border: `1px solid ${c.border}`,
            textTransform: 'uppercase',
        }}>{status}</span>
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
            padding: '16px 24px', borderRadius: 16,
            background: type === 'success' ? '#05CD99' : '#EE5D50',
            color: '#fff', fontWeight: 600, fontSize: '0.85rem',
            boxShadow: '0 12px 30px rgba(0,0,0,0.15)',
            display: 'flex', alignItems: 'center', gap: 12,
            animation: 'slideIn 0.3s ease',
        }}>
            <span>{type === 'success' ? '✅' : '❌'}</span>
            {message}
        </div>
    );
}

function UserRequestCard({ user, onApprove, actionLoading }) {
    const isLoading = actionLoading === `user-${user.id}`;
    return (
        <div style={{
            background: '#fff', borderRadius: 20, padding: '20px',
            display: 'flex', alignItems: 'center', gap: '20px',
            boxShadow: '0 4px 15px rgba(112, 144, 176, 0.08)',
            animation: 'slideIn 0.4s ease-out'
        }}>
            <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: 'linear-gradient(135deg, #4318FF, #5E37FF)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: '#fff', fontWeight: 800, fontSize: '1.2rem'
            }}>{(user.first_name || 'U').charAt(0)}</div>

            <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                    <span style={{ fontWeight: 700, fontSize: '1rem', color: '#2B3674' }}>{user.first_name} {user.last_name}</span>
                    <StatusBadge status={user.is_approved ? 'approved' : 'pending'} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '4px 20px' }}>
                    <div style={{ fontSize: '0.8rem', color: '#707EAE', fontWeight: 500 }}>🏢 {user.organization_name}</div>
                    <div style={{ fontSize: '0.8rem', color: '#707EAE', fontWeight: 500 }}>✉️ {user.email}</div>
                </div>
            </div>

            {!user.is_approved && (
                <button
                    disabled={isLoading}
                    onClick={() => onApprove(user.id)}
                    style={{
                        padding: '10px 24px', borderRadius: 12, border: 'none',
                        background: '#4318FF', color: '#fff', fontWeight: 700,
                        cursor: isLoading ? 'wait' : 'pointer', fontSize: '0.8rem'
                    }}
                >{isLoading ? '...' : 'Approve'}</button>
            )}
        </div>
    );
}

function CompanyRequestCard({ company, onApprove, onReject, actionLoading }) {
    const isLoading = actionLoading === `comp-${company.id}`;
    return (
        <div style={{
            background: '#fff', borderRadius: 20, padding: '20px',
            display: 'flex', alignItems: 'center', gap: '20px',
            boxShadow: '0 4px 15px rgba(112, 144, 176, 0.08)',
            animation: 'slideIn 0.4s ease-out'
        }}>
            <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: 'linear-gradient(135deg, #05CD99, #00BFA6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: '#fff', fontWeight: 800, fontSize: '1.2rem'
            }}>{company.name.charAt(0).toUpperCase()}</div>

            <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                    <span style={{ fontWeight: 700, fontSize: '1rem', color: '#2B3674' }}>{company.name}</span>
                    <StatusBadge status={company.approval_status} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '4px 20px' }}>
                    <div style={{ fontSize: '0.8rem', color: '#707EAE', fontWeight: 500 }}>🌐 {company.domain || 'No domain'}</div>
                    <div style={{ fontSize: '0.8rem', color: '#707EAE', fontWeight: 500 }}>✉️ {company.primary_admin?.email}</div>
                </div>
            </div>

            {company.approval_status === 'pending' && (
                <div style={{ display: 'flex', gap: 10 }}>
                    <button
                        disabled={isLoading}
                        onClick={() => onApprove(company.id)}
                        style={{
                            padding: '10px 20px', borderRadius: 12, border: 'none',
                            background: '#05CD99', color: '#fff', fontWeight: 700,
                            cursor: isLoading ? 'wait' : 'pointer', fontSize: '0.8rem'
                        }}
                    >Approve</button>
                    <button
                        disabled={isLoading}
                        onClick={() => {
                            const reason = prompt('Reject reason?');
                            if (reason) onReject(company.id, reason);
                        }}
                        style={{
                            padding: '10px 20px', borderRadius: 12, border: '1px solid #EE5D50',
                            background: 'transparent', color: '#EE5D50', fontWeight: 700,
                            cursor: isLoading ? 'wait' : 'pointer', fontSize: '0.8rem'
                        }}
                    >Reject</button>
                </div>
            )}
        </div>
    );
}

function SuperAdminDashboard() {
    const [activeTab, setActiveTab] = useState('pending_users');
    const [users, setUsers] = useState([]);
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null);
    const [toast, setToast] = useState(null);
    const [search, setSearch] = useState('');

    const fetchData = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);
        try {
            const [usersRes, compRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/superadmin/users/`),
                axios.get(`${API_BASE_URL}/superadmin/companies/`)
            ]);
            setUsers(usersRes.data.users || []);
            setCompanies(compRes.data.companies || []);
        } catch (err) {
            setToast({ type: 'error', message: 'Failed to sync data.' });
        } finally {
            if (!silent) setLoading(false);
        }
    }, []);

    useEffect(() => { 
        fetchData(); 
        const interval = setInterval(() => fetchData(true), 30000); // Auto-update every 30s
        return () => clearInterval(interval);
    }, [fetchData]);

    const handleApproveUser = async (id) => {
        setActionLoading(`user-${id}`);
        try {
            await axios.post(`${API_BASE_URL}/superadmin/users/${id}/approve/`);
            setToast({ type: 'success', message: 'User approved.' });
            fetchData(true); // Silent update context
        } catch (err) { 
            setToast({ type: 'error', message: 'User approval failed.' }); 
        } finally { setActionLoading(null); }
    };

    const handleApproveCompany = async (id) => {
        setActionLoading(`comp-${id}`);
        try {
            await axios.post(`${API_BASE_URL}/superadmin/companies/${id}/approve/`);
            setToast({ type: 'success', message: 'Company approved.' });
            fetchData(true); // Silent update context
        } catch (err) { 
            setToast({ type: 'error', message: 'Company approval failed.' }); 
        } finally { setActionLoading(null); }
    };

    const handleRejectCompany = async (id, reason) => {
        setActionLoading(`comp-${id}`);
        try {
            await axios.post(`${API_BASE_URL}/superadmin/companies/${id}/reject/`, { reason });
            setToast({ type: 'success', message: 'Company rejected.' });
            fetchData(true); // Silent update context
        } catch (err) { 
            setToast({ type: 'error', message: 'Rejection failed.' }); 
        } finally { setActionLoading(null); }
    };

    const filteredUsers = users.filter(u => {
        const matchesSearch = (u.email || '').toLowerCase().includes(search.toLowerCase()) || (u.organization_name || '').toLowerCase().includes(search.toLowerCase());
        const matchesTab = (activeTab === 'pending_users' && !u.is_approved) || (activeTab === 'all_users');
        return matchesSearch && matchesTab;
    });

    const filteredCompanies = companies.filter(c => {
        const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase());
        const matchesTab = (activeTab === 'pending_companies' && c.approval_status === 'pending') || (activeTab === 'all_companies');
        return matchesSearch && matchesTab;
    });

    return (
        <>
            <style>{`@keyframes slideIn { from { transform: translateY(15px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }`}</style>
            
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ margin: 0, fontSize: '1.6rem', fontWeight: 800, color: '#2B3674' }}>Platform Approvals</h1>
                <p style={{ margin: '4px 0 0', color: '#707EAE', fontSize: '0.9rem', fontWeight: 500 }}>Process individual and organization access requests.</p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', background: '#fff', padding: 10, borderRadius: 16 }}>
                <div style={{ display: 'flex', gap: 4 }}>
                    {STATUS_TABS.map(tab => (
                        <button key={tab.key} onClick={() => setActiveTab(tab.key)} style={{
                            padding: '10px 18px', borderRadius: 12, border: 'none',
                            background: activeTab === tab.key ? '#4318FF' : 'transparent',
                            color: activeTab === tab.key ? '#fff' : '#707EAE',
                            fontWeight: 700, cursor: 'pointer', fontSize: '0.8rem', transition: 'all 0.2s'
                        }}>{tab.icon} {tab.label}</button>
                    ))}
                </div>
                <input
                    type="text" placeholder="Search requests..." value={search} onChange={e => setSearch(e.target.value)}
                    style={{ padding: '12px 18px', borderRadius: 12, border: '1px solid #f0f3f8', fontSize: '0.85rem', width: 260, background: '#F4F7FE', outline: 'none' }}
                />
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '4rem' }}>Synchronizing Directory...</div>
            ) : activeTab.includes('user') ? (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
                    {filteredUsers.length === 0 ? <p style={{ textAlign: 'center', padding: '4rem', color: '#A3AED0' }}>No users found.</p> : filteredUsers.map(u => (
                        <UserRequestCard key={u.id} user={u} onApprove={handleApproveUser} actionLoading={actionLoading} />
                    ))}
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
                    {filteredCompanies.length === 0 ? <p style={{ textAlign: 'center', padding: '4rem', color: '#A3AED0' }}>No companies found.</p> : filteredCompanies.map(c => (
                        <CompanyRequestCard key={c.id} company={c} onApprove={handleApproveCompany} onReject={handleRejectCompany} actionLoading={actionLoading} />
                    ))}
                </div>
            )}

            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
        </>
    );
}

export default SuperAdminDashboard;
