import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

const STATUS_TABS = [
    { key: 'pending', label: 'Pending Requests', icon: '⏳' },
    { key: 'approved', label: 'Approved Users', icon: '✅' },
    { key: 'all_companies', label: 'Company Overview', icon: '🏢' },
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
            background: type === 'success' ? 'var(--status-success)' : 'var(--status-error)',
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
    const isLoading = actionLoading === user.id;
    return (
        <div style={{
            background: '#fff', borderRadius: 20, padding: '20px',
            display: 'flex', alignItems: 'center', gap: '20px',
            boxShadow: '0 4px 15px rgba(112, 144, 176, 0.08)',
            animation: 'slideIn 0.4s ease-out', transition: 'transform 0.2s'
        }}
            onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
            onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
        >
            <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: 'linear-gradient(135deg, var(--blue-accent), var(--blue-secondary))',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: '#fff', fontWeight: 800, fontSize: '1.2rem',
                boxShadow: '0 4px 10px rgba(79, 70, 229, 0.2)'
            }}>{(user.first_name || 'U').charAt(0)}</div>

            <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                    <span style={{ fontWeight: 700, fontSize: '1rem' }}>{user.first_name} {user.last_name}</span>
                    <StatusBadge status={user.is_approved ? 'approved' : 'pending'} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '4px 20px' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                        🏢 {user.organization_name}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                        ✉️ {user.email}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                        📅 Registered {new Date(user.registered_at).toLocaleDateString()}
                    </div>
                </div>
            </div>

            {!user.is_approved && (
                <button
                    disabled={isLoading}
                    onClick={() => onApprove(user.id)}
                    style={{
                        padding: '10px 24px', borderRadius: 10, border: 'none',
                        background: isLoading ? '#e9edf7' : 'var(--blue-accent)',
                        color: '#fff', fontWeight: 700, cursor: isLoading ? 'wait' : 'pointer',
                        fontSize: '0.8rem'
                    }}
                >{isLoading ? '...' : 'Approve Access'}</button>
            )}
        </div>
    );
}

function SuperAdminDashboard() {
    const [activeTab, setActiveTab] = useState('pending');
    const [users, setUsers] = useState([]);
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null);
    const [toast, setToast] = useState(null);
    const [search, setSearch] = useState('');
    const [orgFilter, setOrgFilter] = useState('');

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const [usersRes, compRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/superadmin/users/`),
                axios.get(`${API_BASE_URL}/superadmin/companies/`)
            ]);
            setUsers(usersRes.data.users || []);
            setCompanies(compRes.data.companies || []);
        } catch (err) {
            const msg = err.response?.data?.error || err.response?.data?.message || 'Failed to synchronize data.';
            setToast({ type: 'error', message: msg });
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleApprove = async (id) => {
        setActionLoading(id);
        try {
            await axios.post(`${API_BASE_URL}/superadmin/users/${id}/approve/`);
            setToast({ type: 'success', message: 'User approved successfully.' });
            fetchData();
        } catch (err) {
            setToast({ type: 'error', message: 'Approval failed.' });
        } finally {
            setActionLoading(null);
        }
    };

    const filteredUsers = users.filter(u => {
        const matchesSearch = (u.first_name || '').toLowerCase().includes(search.toLowerCase()) ||
            (u.email || '').toLowerCase().includes(search.toLowerCase()) ||
            (u.organization_name || '').toLowerCase().includes(search.toLowerCase());
        const matchesTab = (activeTab === 'pending' && !u.is_approved) ||
            (activeTab === 'approved' && u.is_approved);
        const matchesOrg = !orgFilter || u.organization_name === orgFilter || String(u.company_id) === orgFilter;
        return matchesSearch && matchesTab && matchesOrg;
    });

    return (
        <>
            <style>{`
                @keyframes slideIn { from { transform: translateY(15px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            `}</style>

            <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800 }}>Registration Approvals</h1>
                    <p style={{ margin: '4px 0 0', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        Process individual access requests for the <span style={{ color: 'var(--blue-accent)', fontWeight: 700 }}>VeriFiHire</span> platform.
                    </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 12, background: '#fff', padding: '8px 16px', borderRadius: 12, border: '1px solid #e9edf7' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Filter by Org:</span>
                    <select
                        value={orgFilter}
                        onChange={(e) => setOrgFilter(e.target.value)}
                        style={{ border: 'none', outline: 'none', background: 'transparent', fontWeight: 700, color: 'var(--blue-accent)', fontSize: '0.8rem', cursor: 'pointer' }}
                    >
                        <option value="">All Organizations</option>
                        {companies.map(c => (
                            <option key={c.id} value={c.name}>{c.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '2.5rem' }}>
                <div style={{ background: '#fff', borderRadius: '20px', padding: '20px', border: '1px solid #f0f3f8', boxShadow: '0 4px 15px rgba(0,0,0,0.02)' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>Pending Users</div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 800 }}>{users.filter(u => !u.is_approved).length}</div>
                </div>
                <div style={{ background: '#fff', borderRadius: '20px', padding: '20px', border: '1px solid #f0f3f8', boxShadow: '0 4px 15px rgba(0,0,0,0.02)' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>Approved Entities</div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 800 }}>{companies.filter(c => c.approval_status === 'approved').length}</div>
                </div>
                <div style={{ background: '#fff', borderRadius: '20px', padding: '20px', border: '1px solid #f0f3f8', boxShadow: '0 4px 15px rgba(0,0,0,0.02)' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>Total Companies</div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 800 }}>{companies.length}</div>
                </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', background: '#fff', padding: 8, borderRadius: 16 }}>
                <div style={{ display: 'flex', gap: 6 }}>
                    {STATUS_TABS.map(tab => (
                        <button key={tab.key} onClick={() => setActiveTab(tab.key)} style={{
                            padding: '10px 20px', borderRadius: 10, border: 'none',
                            background: activeTab === tab.key ? 'var(--blue-accent)' : 'transparent',
                            color: activeTab === tab.key ? '#fff' : 'var(--text-secondary)',
                            fontWeight: 700, cursor: 'pointer', fontSize: '0.8rem', transition: 'all 0.2s'
                        }}>{tab.label}</button>
                    ))}
                </div>
                <input
                    type="text" placeholder="Search registration..." value={search} onChange={e => setSearch(e.target.value)}
                    style={{ padding: '10px 15px', borderRadius: 10, border: '1px solid #e9edf7', fontSize: '0.85rem', width: 240, background: '#F4F7FE' }}
                />
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '4rem' }}>Synchronizing...</div>
            ) : activeTab === 'all_companies' ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
                    {companies.map(c => (
                        <div key={c.id} style={{ background: '#fff', padding: 20, borderRadius: 20, boxShadow: '0 4px 15px rgba(0,0,0,0.05)', border: '1px solid #f0f3f8' }}>
                            <div style={{ fontWeight: 700, marginBottom: 4 }}>{c.name}</div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Status: <StatusBadge status={c.approval_status} /></div>
                        </div>
                    ))}
                </div>
            ) : filteredUsers.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '5rem', background: '#fff', borderRadius: 24, color: 'var(--text-secondary)' }}>
                    No pending {activeTab} user requests.
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
                    {filteredUsers.map(u => (
                        <UserRequestCard key={u.id} user={u} onApprove={handleApprove} actionLoading={actionLoading} />
                    ))}
                </div>
            )}

            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
        </>
    );
}

export default SuperAdminDashboard;
