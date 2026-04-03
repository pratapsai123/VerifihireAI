import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

function StatCard({ title, value, icon, color }) {
    return (
        <div style={{
            background: '#fff', borderRadius: '20px', padding: '20px',
            boxShadow: '0 10px 20px rgba(112, 144, 176, 0.08)',
            display: 'flex', flexDirection: 'column', gap: '10px',
            border: '1px solid #f0f3f8', flex: 1, minWidth: '220px'
        }}>
            <div style={{
                width: 48, height: 48, borderRadius: '14px',
                background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.2rem', color: color
            }}>{icon}</div>
            <div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-main)', lineHeight: 1.2 }}>{value}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{title}</div>
            </div>
        </div>
    );
}

function DashboardHome() {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        totalCompanies: 0,
        pendingUserRequests: 0,
        approvedEntities: 0,
        totalPlatformUsers: 0,
        recentSignups: []
    });
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [orgFilter, setOrgFilter] = useState('');

    const fetchDashboardData = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);
        try {
            const [compRes, userRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/superadmin/companies/`),
                axios.get(`${API_BASE_URL}/superadmin/users/`)
            ]);

            const allCompanies = compRes.data.companies || [];
            const allUsers = userRes.data.users || [];
            setCompanies(allCompanies);

            const filteredCompanies = orgFilter ? allCompanies.filter(c => c.name === orgFilter) : allCompanies;
            const filteredUsers = orgFilter ? allUsers.filter(u => u.organization_name === orgFilter) : allUsers;

            setStats({
                totalCompanies: allCompanies.length,
                pendingCompanies: allCompanies.filter(c => c.approval_status === 'pending').length,
                approvedEntities: allCompanies.filter(c => c.approval_status === 'approved').length,
                totalPlatformUsers: filteredUsers.length,
                recentSignups: filteredUsers.slice(0, 5)
            });
        } catch (err) {
            console.error('Failed to fetch dashboard stats:', err);
        } finally {
            if (!silent) setLoading(false);
        }
    }, [orgFilter]);

    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(() => fetchDashboardData(true), 30000);
        return () => clearInterval(interval);
    }, [fetchDashboardData]);

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '5rem', color: 'var(--text-secondary)' }}>
                <div style={{
                    width: 44, height: 44, border: '4px solid #F4F7FE',
                    borderTop: '4px solid var(--blue-accent)', borderRadius: '50%',
                    margin: '0 auto 16px', animation: 'spin 1s linear infinite'
                }} />
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>LOADING PLATFORM DATA...</span>
            </div>
        );
    }

    return (
        <div style={{ animation: 'slideIn 0.5s ease-out' }}>
            <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.5px' }}>
                        System Overview
                    </h1>
                    <p style={{ margin: '4px 0 0', color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 500 }}>
                        Welcome back, Administrator. Real-time platform metrics for <span style={{ color: 'var(--blue-accent)', fontWeight: 700 }}>VeriFiHire</span>.
                    </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 12, background: '#fff', padding: '8px 16px', borderRadius: 12, border: '1px solid #e9edf7' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Organization:</span>
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

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '2rem' }}>
                <StatCard title="Total Organizations" value={stats.totalCompanies} icon="🏢" color="var(--blue-accent)" />
                <StatCard title="Approved Entities" value={stats.approvedEntities} icon="✅" color="var(--status-success)" />
                <StatCard title="Platform Employees" value={stats.totalPlatformUsers} icon="👥" color="#f6ad55" />
                <StatCard title="Pending Approvals" value={stats.pendingCompanies} icon="⏳" color="var(--status-warning)" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px' }}>
                <div style={{ background: '#fff', borderRadius: '24px', padding: '24px', boxShadow: '0 10px 20px rgba(112, 144, 176, 0.05)', border: '1px solid #f0f3f8' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Latest Registered Users</h3>
                        <button onClick={() => navigate('/companies')} style={{ background: 'transparent', border: 'none', color: 'var(--blue-accent)', fontWeight: 700, fontSize: '0.8rem', cursor: 'pointer' }}>Manage Companies</button>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {stats.recentSignups.map(user => (
                            <div key={user.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f8fafc' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                    <div style={{ width: 40, height: 40, borderRadius: '10px', background: '#F4F7FE', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, color: 'var(--text-main)' }}>{(user.first_name || 'U').charAt(0)}</div>
                                    <div>
                                        <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{user.first_name} {user.last_name}</div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{user.organization_name}</div>
                                    </div>
                                </div>
                                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                                    {new Date(user.registered_at).toLocaleDateString()}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
                    <div style={{ background: 'linear-gradient(135deg, var(--blue-accent), var(--blue-secondary))', borderRadius: '24px', padding: '24px', color: '#fff' }}>
                        <h3 style={{ color: '#fff', fontSize: '1rem', marginBottom: '0.5rem' }}>Platform Access</h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1rem' }}>
                            <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#05CD99', boxShadow: '0 0 10px #05CD99' }}></div>
                            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>System Live</span>
                        </div>
                        <p style={{ fontSize: '0.75rem', opacity: 0.8, lineHeight: 1.6, marginBottom: '0px' }}>VeriFiHire Superadmin panel is connected to the production background screening engine.</p>
                    </div>
                    <div style={{ background: '#fff', borderRadius: '24px', padding: '24px', boxShadow: '0 10px 20px rgba(112, 144, 176, 0.05)', border: '1px solid #f0f3f8' }}>
                        <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '1.2rem' }}>Queue Status</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.8rem', color: stats.pendingCompanies > 0 ? 'var(--status-warning)' : 'var(--status-success)', fontWeight: 600 }}>
                                <span>{stats.pendingCompanies > 0 ? `⚠️ ${stats.pendingCompanies} organizations awaiting approval` : '✅ All organizations verified'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <style>{`
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            `}</style>
        </div>
    );
}

export default DashboardHome;
