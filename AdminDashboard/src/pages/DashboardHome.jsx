import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend,
    BarChart, Bar
} from 'recharts';

/* ──────────────────────── helpers ──────────────────────── */

function getDaysAgo(n) {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() - n);
    return d;
}

function formatShortDate(date) {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function buildTrendData(companies, users, days = 30) {
    const data = [];
    for (let i = days - 1; i >= 0; i--) {
        const dayStart = getDaysAgo(i);
        const dayEnd = getDaysAgo(i - 1);
        const label = formatShortDate(dayStart);
        const orgs = companies.filter(c => {
            const d = new Date(c.created_at);
            return d >= dayStart && d < dayEnd;
        }).length;
        const usrs = users.filter(u => {
            const d = new Date(u.registered_at);
            return d >= dayStart && d < dayEnd;
        }).length;
        data.push({ date: label, Organizations: orgs, Users: usrs });
    }
    return data;
}

function buildApprovalData(companies) {
    const pending = companies.filter(c => c.approval_status === 'pending').length;
    const approved = companies.filter(c => c.approval_status === 'approved').length;
    const rejected = companies.filter(c => c.approval_status === 'rejected').length;
    return [
        { name: 'Approved', value: approved, color: '#05CD99' },
        { name: 'Pending', value: pending, color: '#FFB547' },
        { name: 'Rejected', value: rejected, color: '#EE5D50' },
    ].filter(d => d.value > 0);
}

function buildRoleData(users) {
    const roleMap = {};
    users.forEach(u => {
        const role = u.role || 'unknown';
        const label = role.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        roleMap[label] = (roleMap[label] || 0) + 1;
    });
    return Object.entries(roleMap)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count);
}

function buildTopOrgs(companies) {
    return [...companies]
        .sort((a, b) => (b.user_count || 0) - (a.user_count || 0))
        .slice(0, 6)
        .map(c => ({ name: c.name.length > 14 ? c.name.slice(0, 14) + '…' : c.name, users: c.user_count || 0 }));
}

const ROLE_COLORS = ['#4F46E5', '#7C3AED', '#2563EB', '#0891B2', '#059669', '#D97706', '#DC2626', '#6366F1'];

/* ──────────────────────── AnimatedNumber ──────────────────────── */

function AnimatedNumber({ value, duration = 1200 }) {
    const [display, setDisplay] = useState(0);
    const ref = useRef();
    useEffect(() => {
        const start = 0;
        const end = value;
        const startTime = performance.now();
        function animate(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            setDisplay(Math.round(start + (end - start) * eased));
            if (progress < 1) ref.current = requestAnimationFrame(animate);
        }
        ref.current = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(ref.current);
    }, [value, duration]);
    return <>{display}</>;
}

/* ──────────────────────── StatCard ──────────────────────── */

function StatCard({ title, value, icon, color, subtitle, onClick }) {
    const [hovered, setHovered] = useState(false);
    return (
        <div
            onClick={onClick}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            style={{
                background: '#fff', borderRadius: '20px', padding: '24px',
                boxShadow: hovered ? '0 16px 32px rgba(112, 144, 176, 0.18)' : '0 10px 20px rgba(112, 144, 176, 0.08)',
                display: 'flex', flexDirection: 'column', gap: '12px',
                border: '1px solid #f0f3f8', flex: 1, minWidth: '200px',
                cursor: onClick ? 'pointer' : 'default',
                transform: hovered ? 'translateY(-4px)' : 'translateY(0)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
        >
            <div style={{
                width: 52, height: 52, borderRadius: '16px',
                background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.4rem', color: color,
                transition: 'transform 0.3s ease',
                transform: hovered ? 'scale(1.1)' : 'scale(1)',
            }}>{icon}</div>
            <div>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-main)', lineHeight: 1.1, letterSpacing: '-1px' }}>
                    <AnimatedNumber value={value} />
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 700, marginTop: 6, textTransform: 'uppercase', letterSpacing: '0.8px' }}>{title}</div>
                {subtitle && <div style={{ fontSize: '0.7rem', color: color, fontWeight: 600, marginTop: 2 }}>{subtitle}</div>}
            </div>
        </div>
    );
}

/* ──────────────────────── ChartCard ──────────────────────── */

function ChartCard({ title, subtitle, children, style }) {
    return (
        <div style={{
            background: '#fff', borderRadius: '24px', padding: '24px',
            boxShadow: '0 10px 20px rgba(112, 144, 176, 0.05)',
            border: '1px solid #f0f3f8',
            ...style,
        }}>
            <div style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>{title}</h3>
                {subtitle && <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: '4px 0 0', fontWeight: 500 }}>{subtitle}</p>}
            </div>
            {children}
        </div>
    );
}

/* ──────────────────────── Custom Tooltip ──────────────────────── */

function CustomTooltip({ active, payload, label }) {
    if (!active || !payload?.length) return null;
    return (
        <div style={{
            background: 'rgba(43, 54, 116, 0.95)', backdropFilter: 'blur(8px)',
            borderRadius: 12, padding: '12px 16px', border: 'none',
            boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
        }}>
            <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.7rem', fontWeight: 600, marginBottom: 6 }}>{label}</div>
            {payload.map((entry, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: entry.color }} />
                    <span style={{ color: '#fff', fontSize: '0.78rem', fontWeight: 600 }}>{entry.name}: {entry.value}</span>
                </div>
            ))}
        </div>
    );
}

function PieTooltip({ active, payload }) {
    if (!active || !payload?.length) return null;
    const d = payload[0];
    return (
        <div style={{
            background: 'rgba(43, 54, 116, 0.95)', backdropFilter: 'blur(8px)',
            borderRadius: 12, padding: '12px 16px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: d.payload.color }} />
                <span style={{ color: '#fff', fontSize: '0.8rem', fontWeight: 700 }}>{d.name}: {d.value}</span>
            </div>
        </div>
    );
}

/* ──────────────────────── Custom Legend ──────────────────────── */

function CustomPieLegend({ payload }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, paddingLeft: 8 }}>
            {payload.map((entry, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 12, height: 12, borderRadius: 4, background: entry.color, flexShrink: 0 }} />
                    <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}>{entry.value}</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: entry.color, marginLeft: 'auto' }}>{entry.payload.value}</span>
                </div>
            ))}
        </div>
    );
}

/* ──────────────────────── DashboardHome ──────────────────────── */

function DashboardHome() {
    const navigate = useNavigate();
    const [companies, setCompanies] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [orgFilter, setOrgFilter] = useState('');
    const [chartOrgFilter, setChartOrgFilter] = useState('');

    const fetchData = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);
        try {
            const [compRes, userRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/superadmin/companies/`),
                axios.get(`${API_BASE_URL}/superadmin/users/`)
            ]);
            setCompanies(compRes.data.companies || []);
            setUsers(userRes.data.users || []);
        } catch (err) {
            console.error('Failed to fetch dashboard stats:', err);
        } finally {
            if (!silent) setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(() => fetchData(true), 30000);
        return () => clearInterval(interval);
    }, [fetchData]);

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '5rem', color: 'var(--text-secondary)' }}>
                <div style={{
                    width: 48, height: 48, border: '4px solid #F4F7FE',
                    borderTop: '4px solid var(--blue-accent)', borderRadius: '50%',
                    margin: '0 auto 16px', animation: 'spin 1s linear infinite'
                }} />
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>LOADING PLATFORM DATA...</span>
            </div>
        );
    }

    // Apply org filter
    const filteredUsers = orgFilter ? users.filter(u => u.organization_name === orgFilter) : users;
    const filteredCompanies = orgFilter ? companies.filter(c => c.name === orgFilter) : companies;

    // Derived stats
    const totalCompanies = companies.length;
    const approvedCompanies = companies.filter(c => c.approval_status === 'approved').length;
    const pendingCompanies = companies.filter(c => c.approval_status === 'pending').length;
    const totalUsers = filteredUsers.length;

    // Chart data
    const trendData = buildTrendData(filteredCompanies, filteredUsers);
    const approvalData = buildApprovalData(filteredCompanies);
    const roleData = buildRoleData(filteredUsers);
    const chartRoleData = buildRoleData(chartOrgFilter ? users.filter(u => u.organization_name === chartOrgFilter) : users);
    const topOrgs = buildTopOrgs(companies);
    const recentSignups = filteredUsers.slice(0, 5);

    return (
        <div style={{ animation: 'slideIn 0.5s ease-out' }}>
            {/* Header */}
            <div style={{ marginBottom: '1.8rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.5px' }}>
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

            {/* Stat Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '2rem' }}>
                <StatCard title="Total Organizations" value={totalCompanies} icon="🏢" color="var(--blue-accent)" subtitle={`${approvedCompanies} active`} onClick={() => navigate('/companies')} />
                <StatCard title="Approved Entities" value={approvedCompanies} icon="✅" color="var(--status-success)" />
                <StatCard title="Platform Users" value={totalUsers} icon="👥" color="#7C3AED" subtitle={`${roleData.length} roles`} />
                <StatCard title="Pending Approvals" value={pendingCompanies} icon="⏳" color="var(--status-warning)" subtitle={pendingCompanies > 0 ? 'Action required' : 'All clear'} onClick={() => navigate('/', { state: { activeTab: 'pending_companies' } })} />
            </div>

            {/* Row 1: Trend Chart + Approval Donut */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
                <ChartCard title="Registration Trends" subtitle="New signups over the last 30 days">
                    <ResponsiveContainer width="100%" height={260}>
                        <AreaChart data={trendData} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
                            <defs>
                                <linearGradient id="gradOrg" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#4F46E5" stopOpacity={0.25} />
                                    <stop offset="95%" stopColor="#4F46E5" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="gradUser" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#7C3AED" stopOpacity={0.25} />
                                    <stop offset="95%" stopColor="#7C3AED" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f3f8" />
                            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#A3AED0', fontWeight: 600 }} tickLine={false} axisLine={false} interval="preserveStartEnd" />
                            <YAxis tick={{ fontSize: 11, fill: '#A3AED0', fontWeight: 600 }} tickLine={false} axisLine={false} allowDecimals={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Area type="monotone" dataKey="Organizations" stroke="#4F46E5" strokeWidth={2.5} fill="url(#gradOrg)" dot={false} activeDot={{ r: 5, strokeWidth: 2 }} />
                            <Area type="monotone" dataKey="Users" stroke="#7C3AED" strokeWidth={2.5} fill="url(#gradUser)" dot={false} activeDot={{ r: 5, strokeWidth: 2 }} />
                        </AreaChart>
                    </ResponsiveContainer>
                    <div style={{ display: 'flex', gap: 24, justifyContent: 'center', marginTop: 12 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <div style={{ width: 12, height: 4, borderRadius: 2, background: '#4F46E5' }} />
                            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Organizations</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <div style={{ width: 12, height: 4, borderRadius: 2, background: '#7C3AED' }} />
                            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Users</span>
                        </div>
                    </div>
                </ChartCard>

                <ChartCard title="Approval Funnel" subtitle="Company approval status breakdown">
                    {approvalData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={260}>
                            <PieChart>
                                <Pie
                                    data={approvalData}
                                    cx="50%"
                                    cy="45%"
                                    innerRadius={55}
                                    outerRadius={85}
                                    paddingAngle={4}
                                    dataKey="value"
                                    cornerRadius={6}
                                    stroke="none"
                                >
                                    {approvalData.map((entry, index) => (
                                        <Cell key={index} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip content={<PieTooltip />} />
                                <Legend content={<CustomPieLegend />} verticalAlign="bottom" />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                            No company data yet
                        </div>
                    )}
                </ChartCard>
            </div>

            {/* Row 2: Role Distribution + Top Orgs */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                <div style={{
                    background: '#fff', borderRadius: '24px', padding: '24px',
                    boxShadow: '0 10px 20px rgba(112, 144, 176, 0.05)',
                    border: '1px solid #f0f3f8'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                        <div>
                            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>User Role Distribution</h3>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: '4px 0 0', fontWeight: 500 }}>
                                {chartOrgFilter ? `Breakdown for ${chartOrgFilter}` : 'Breakdown across all organizations'}
                            </p>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#F4F7FE', padding: '6px 12px', borderRadius: 10, border: '1px solid #e9edf7' }}>
                            <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Company:</span>
                            <select
                                value={chartOrgFilter}
                                onChange={(e) => setChartOrgFilter(e.target.value)}
                                style={{ border: 'none', outline: 'none', background: 'transparent', fontWeight: 700, color: 'var(--blue-accent)', fontSize: '0.75rem', cursor: 'pointer' }}
                            >
                                <option value="">All Organizations</option>
                                {companies.map(c => (
                                    <option key={c.id} value={c.name}>{c.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {chartRoleData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={240}>
                            <BarChart data={chartRoleData} layout="vertical" margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f3f8" horizontal={false} />
                                <XAxis type="number" tick={{ fontSize: 11, fill: '#A3AED0', fontWeight: 600 }} tickLine={false} axisLine={false} allowDecimals={false} />
                                <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: '#2B3674', fontWeight: 600 }} tickLine={false} axisLine={false} width={120} />
                                <Tooltip content={<CustomTooltip />} />
                                <Bar dataKey="count" name="Users" radius={[0, 6, 6, 0]} barSize={20}>
                                    {chartRoleData.map((_, i) => (
                                        <Cell key={i} fill={ROLE_COLORS[i % ROLE_COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ height: 240, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                            No user data found for this company
                        </div>
                    )}
                </div>

                <ChartCard title="Top Organizations" subtitle="By number of employees">
                    {topOrgs.length > 0 ? (
                        <ResponsiveContainer width="100%" height={240}>
                            <BarChart data={topOrgs} margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="gradBar" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#4F46E5" />
                                        <stop offset="100%" stopColor="#7C3AED" />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f3f8" />
                                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#A3AED0', fontWeight: 600 }} tickLine={false} axisLine={false} />
                                <YAxis tick={{ fontSize: 11, fill: '#A3AED0', fontWeight: 600 }} tickLine={false} axisLine={false} allowDecimals={false} />
                                <Tooltip content={<CustomTooltip />} />
                                <Bar dataKey="users" name="Employees" fill="url(#gradBar)" radius={[8, 8, 0, 0]} barSize={36} />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ height: 240, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                            No organization data yet
                        </div>
                    )}
                </ChartCard>
            </div>

            {/* Row 3: Recent Users + Status Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
                <ChartCard title="Latest Registered Users">
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: -40, marginBottom: 12 }}>
                        <button onClick={() => navigate('/', { state: { activeTab: 'all_users' } })} style={{ background: 'transparent', border: 'none', color: 'var(--blue-accent)', fontWeight: 700, fontSize: '0.78rem', cursor: 'pointer' }}>View All Users →</button>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        {recentSignups.length === 0 && (
                            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>No users registered yet</div>
                        )}
                        {recentSignups.map(user => (
                            <div key={user.id} style={{
                                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                padding: '14px 12px', borderRadius: 12,
                                transition: 'background 0.2s ease',
                            }}
                                onMouseEnter={e => e.currentTarget.style.background = '#F4F7FE'}
                                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                                    <div style={{
                                        width: 42, height: 42, borderRadius: '12px',
                                        background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontWeight: 700, color: '#fff', fontSize: '0.9rem'
                                    }}>
                                        {(user.first_name || 'U').charAt(0)}
                                    </div>
                                    <div>
                                        <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--text-main)' }}>{user.first_name} {user.last_name}</div>
                                        <div style={{ fontSize: '0.73rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{user.organization_name} · {user.role?.replace(/_/g, ' ')}</div>
                                    </div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                    <span style={{
                                        padding: '4px 10px', borderRadius: 999, fontSize: '0.65rem', fontWeight: 700,
                                        background: user.is_approved ? 'rgba(5, 205, 153, 0.12)' : 'rgba(255, 181, 71, 0.12)',
                                        color: user.is_approved ? '#05CD99' : '#FFB547',
                                        textTransform: 'uppercase',
                                    }}>{user.is_approved ? 'Approved' : 'Pending'}</span>
                                    <span style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                                        {new Date(user.registered_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </ChartCard>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    <div style={{
                        background: 'linear-gradient(135deg, var(--blue-accent), var(--blue-secondary))',
                        borderRadius: '24px', padding: '24px', color: '#fff',
                        position: 'relative', overflow: 'hidden',
                    }}>
                        {/* Decorative circle */}
                        <div style={{ position: 'absolute', top: -20, right: -20, width: 100, height: 100, borderRadius: '50%', background: 'rgba(255,255,255,0.08)' }} />
                        <div style={{ position: 'absolute', bottom: -30, right: 30, width: 80, height: 80, borderRadius: '50%', background: 'rgba(255,255,255,0.05)' }} />
                        <h3 style={{ color: '#fff', fontSize: '1rem', marginBottom: '0.6rem', position: 'relative' }}>Platform Status</h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1rem', position: 'relative' }}>
                            <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#05CD99', boxShadow: '0 0 10px #05CD99', animation: 'pulse 2s infinite' }} />
                            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>System Live</span>
                        </div>
                        <p style={{ fontSize: '0.75rem', opacity: 0.8, lineHeight: 1.6, marginBottom: '0px', position: 'relative' }}>
                            VeriFiHire Superadmin panel is connected to the production background screening engine.
                        </p>
                    </div>

                    <div style={{
                        background: '#fff', borderRadius: '24px', padding: '24px',
                        boxShadow: '0 10px 20px rgba(112, 144, 176, 0.05)',
                        border: '1px solid #f0f3f8'
                    }}>
                        <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '1.2rem' }}>Queue Status</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <div style={{
                                display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.8rem',
                                color: pendingCompanies > 0 ? 'var(--status-warning)' : 'var(--status-success)', fontWeight: 600
                            }}>
                                <span>{pendingCompanies > 0 ? `⚠️ ${pendingCompanies} organizations awaiting approval` : '✅ All organizations verified'}</span>
                            </div>
                            {users.filter(u => !u.is_approved).length > 0 && (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.8rem', color: 'var(--status-warning)', fontWeight: 600 }}>
                                    <span>⚠️ {users.filter(u => !u.is_approved).length} users pending approval</span>
                                </div>
                            )}
                        </div>
                    </div>

                    <button
                        onClick={() => navigate('/companies')}
                        style={{
                            background: '#fff', border: '1px solid #e9edf7', borderRadius: 16,
                            padding: '16px 20px', cursor: 'pointer',
                            display: 'flex', alignItems: 'center', gap: 12,
                            transition: 'all 0.2s ease',
                            boxShadow: '0 4px 12px rgba(112, 144, 176, 0.05)',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--blue-accent)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
                        onMouseLeave={e => { e.currentTarget.style.borderColor = '#e9edf7'; e.currentTarget.style.transform = 'translateY(0)'; }}
                    >
                        <span style={{ fontSize: '1.4rem' }}>🏢</span>
                        <div style={{ textAlign: 'left' }}>
                            <div style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-main)' }}>Manage Companies</div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 500 }}>View enterprise directory</div>
                        </div>
                        <span style={{ marginLeft: 'auto', color: 'var(--text-secondary)', fontSize: '1.1rem' }}>→</span>
                    </button>
                </div>
            </div>

            <style>{`
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
                @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
            `}</style>
        </div>
    );
}

export default DashboardHome;
