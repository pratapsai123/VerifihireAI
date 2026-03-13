import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

const STATUS_COLORS = {
    pending: { bg: 'rgba(255, 181, 71, 0.1)', text: '#FFB547', border: 'rgba(255, 181, 71, 0.15)' },
    approved: { bg: 'rgba(5, 205, 153, 0.1)', text: '#05CD99', border: 'rgba(5, 205, 153, 0.15)' },
    rejected: { bg: 'rgba(238, 93, 80, 0.1)', text: '#EE5D50', border: 'rgba(238, 93, 80, 0.15)' },
};

function StatusBadge({ status }) {
    const c = STATUS_COLORS[status] || { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
    return (
        <span style={{
            padding: '3px 10px',
            borderRadius: '8px',
            fontSize: '0.65rem',
            fontWeight: 800,
            letterSpacing: '0.05em',
            background: c.bg,
            color: c.text,
            border: `1px solid ${c.border}`,
            textTransform: 'uppercase',
        }}>
            {status}
        </span>
    );
}

function CompanyRow({ company }) {
    const admin = company.primary_admin;

    return (
        <div style={{
            background: 'var(--bg-white)',
            borderRadius: 16,
            padding: '20px 24px',
            display: 'flex',
            alignItems: 'center',
            gap: '24px',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            cursor: 'default',
            boxShadow: '0 4px 12px rgba(112, 144, 176, 0.05)',
            border: '1px solid transparent'
        }}
            onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'var(--blue-accent)';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 10px 20px rgba(112, 144, 176, 0.1)';
            }}
            onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'transparent';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(112, 144, 176, 0.05)';
            }}
        >
            <div style={{
                width: 52, height: 52, borderRadius: 14,
                background: company.approval_status === 'approved' ? 'rgba(5, 205, 153, 0.1)' : '#F4F7FE',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: company.approval_status === 'approved' ? 'var(--status-success)' : 'var(--text-main)',
                fontWeight: 800, fontSize: '1.25rem', flexShrink: 0,
                border: '1px solid rgba(0,0,0,0.03)'
            }}>
                {company.name.charAt(0).toUpperCase()}
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 4 }}>
                    <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)', letterSpacing: '-0.3px' }}>{company.name}</span>
                    <StatusBadge status={company.approval_status} />
                </div>
                <div style={{ display: 'flex', gap: 20, color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 500 }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ opacity: 0.7 }}>🌐</span> {company.domain || 'No domain'}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ opacity: 0.7 }}>✉️</span> {admin?.email || 'No email'}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ opacity: 0.7 }}>👥</span> {company.user_count || 0} employees</span>
                </div>
            </div>

            <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Member Since</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', marginTop: 2 }}>
                    {new Date(company.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                </div>
            </div>
        </div>
    );
}

function CompaniesPage() {
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    const fetchCompanies = useCallback(async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/superadmin/companies/`);
            setCompanies(res.data.companies || []);
        } catch (err) {
            console.error('Failed to load companies:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchCompanies();
    }, [fetchCompanies]);

    const filtered = companies.filter(c =>
        c.name.toLowerCase().includes(search.toLowerCase()) ||
        (c.primary_admin?.email || '').toLowerCase().includes(search.toLowerCase()) ||
        (c.domain || '').toLowerCase().includes(search.toLowerCase())
    );

    return (
        <>
            <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.5px' }}>
                        Enterprise Directory
                    </h1>
                    <p style={{ margin: '4px 0 0', color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 500 }}>
                        Viewing all registered <span style={{ color: 'var(--blue-accent)', fontWeight: 700 }}>{companies.length}</span> organizations on the platform.
                    </p>
                </div>

                <div style={{ position: 'relative' }}>
                    <span style={{
                        position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)',
                        fontSize: '0.9rem', color: 'var(--text-secondary)',
                    }}>🔍</span>
                    <input
                        type="text"
                        placeholder="Search workspace index..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        style={{
                            padding: '12px 16px 12px 42px',
                            borderRadius: '12px',
                            border: '1px solid #e9edf7',
                            fontSize: '0.85rem',
                            outline: 'none',
                            width: 320,
                            background: '#fff',
                            boxShadow: '0 4px 6px rgba(112, 144, 176, 0.05)',
                            color: 'var(--text-main)',
                            fontWeight: 500
                        }}
                    />
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '5rem', color: 'var(--text-secondary)' }}>
                    <div style={{
                        width: 44, height: 44, border: '4px solid #F4F7FE',
                        borderTop: '4px solid var(--blue-accent)', borderRadius: '50%',
                        margin: '0 auto 16px', animation: 'spin 1s linear infinite'
                    }} />
                    <span style={{ fontWeight: 600, fontSize: '0.9rem', letterSpacing: '0.5px' }}>INDEXING DIRECTORY...</span>
                </div>
            ) : filtered.length === 0 ? (
                <div style={{
                    textAlign: 'center', padding: '5rem',
                    background: '#fff', borderRadius: 30, border: 'none',
                    boxShadow: '0 20px 40px rgba(112, 144, 176, 0.08)',
                    color: 'var(--text-secondary)',
                }}>
                    <div style={{ fontSize: '4.5rem', marginBottom: 24, opacity: 0.5 }}>🏢</div>
                    <div style={{ fontWeight: 800, fontSize: '1.25rem', marginBottom: 10, color: 'var(--text-main)' }}>
                        No Registered Entities
                    </div>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
                    {filtered.map(company => (
                        <CompanyRow key={company.id} company={company} />
                    ))}
                </div>
            )}

            <style>{`
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            `}</style>
        </>
    );
}

export default CompaniesPage;
