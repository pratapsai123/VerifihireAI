import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import { getToken } from '../utils/authStorage';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = ['#22c55e', '#f59e0b', '#6366f1', '#ef4444'];

export default function AiInterviewsOverview() {
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [expandedBatch, setExpandedBatch] = useState(null);
    const [search, setSearch] = useState('');
    const [resendingId, setResendingId] = useState(null);

    const handleResendInvite = async (candidateId, email) => {
        setResendingId(candidateId);
        try {
            await axios.post(`${API_BASE_URL}/ai-candidates/${candidateId}/resend-invite/`, {}, {
                headers: { Authorization: `Bearer ${getToken()}` }
            });
            alert(`Invite resent to ${email}`);
        } catch (err) {
            alert(err.response?.data?.error || 'Failed to resend invite.');
        } finally {
            setResendingId(null);
        }
    };

    useEffect(() => {
        const fetch = async () => {
            try {
                const resp = await axios.get(`${API_BASE_URL}/ai-candidates/interviews-overview/`, {
                    headers: { Authorization: `Bearer ${getToken()}` }
                });
                setData(resp.data);
            } catch (err) {
                console.error('Failed to load interviews overview:', err);
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, []);

    if (loading) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'Poppins' }}>
            <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', color: '#6366f1' }} />
        </div>
    );

    if (!data) return (
        <div style={{ textAlign: 'center', padding: '4rem', fontFamily: 'Poppins' }}>
            <p style={{ color: '#64748b' }}>Failed to load data.</p>
        </div>
    );

    const { summary, batches } = data;

    const pieData = [
        { name: 'Completed', value: summary.completed },
        { name: 'In Progress', value: summary.in_progress },
        { name: 'Pending', value: summary.pending },
    ].filter(d => d.value > 0);

    const scoreRanges = [
        { range: '0-20%', count: 0 },
        { range: '21-40%', count: 0 },
        { range: '41-60%', count: 0 },
        { range: '61-80%', count: 0 },
        { range: '81-100%', count: 0 },
    ];
    batches.forEach(b => b.candidates.forEach(c => {
        if (c.score_pct === null || c.score_pct === undefined) return;
        if (c.score_pct <= 20) scoreRanges[0].count++;
        else if (c.score_pct <= 40) scoreRanges[1].count++;
        else if (c.score_pct <= 60) scoreRanges[2].count++;
        else if (c.score_pct <= 80) scoreRanges[3].count++;
        else scoreRanges[4].count++;
    }));

    const filteredBatches = batches.filter(b =>
        b.batch_name.toLowerCase().includes(search.toLowerCase()) ||
        b.candidates.some(c => c.name.toLowerCase().includes(search.toLowerCase()) || c.email.toLowerCase().includes(search.toLowerCase()))
    );

    return (
        <div style={{ padding: '2rem 3rem', fontFamily: 'Poppins', maxWidth: '1200px', margin: '0 auto' }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
                <div>
                    <h1 style={{ fontSize: '1.8rem', fontWeight: '900', color: '#111827', margin: 0 }}>AI Interviews Dashboard</h1>
                    <p style={{ color: '#64748b', margin: '0.25rem 0 0', fontSize: '0.9rem' }}>All interview sessions and their progress</p>
                </div>
                <button onClick={() => navigate('/dashboard')} style={{ padding: '0.6rem 1.2rem', borderRadius: '10px', border: '1px solid #e2e8f0', background: 'white', cursor: 'pointer', fontWeight: '600', color: '#374151' }}>
                    ← Back
                </button>
            </div>

            {/* Stat Cards + Charts — Dark themed panel */}
            <div style={{
                background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
                borderRadius: '20px',
                padding: '1.5rem 2rem',
                marginBottom: '2rem',
                boxShadow: '0 10px 30px rgba(15, 12, 41, 0.3)',
                position: 'relative',
                overflow: 'hidden'
            }}>
                {/* Decorative orbs */}
                <div style={{ position: 'absolute', top: '-40px', right: '-40px', width: '200px', height: '200px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)', pointerEvents: 'none' }} />
                <div style={{ position: 'absolute', bottom: '-60px', left: '-30px', width: '250px', height: '250px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(168, 85, 247, 0.1) 0%, transparent 70%)', pointerEvents: 'none' }} />

                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.2rem', position: 'relative', zIndex: 1 }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#a78bfa', fontSize: '1rem' }}>
                        <i className="fa-solid fa-chart-pie" />
                    </div>
                    <h3 style={{ margin: 0, color: 'white', fontSize: '1.1rem', fontWeight: '800' }}>Interview Analytics</h3>
                    <span style={{ marginLeft: 'auto', fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', fontWeight: '600', background: 'rgba(255,255,255,0.08)', padding: '0.25rem 0.75rem', borderRadius: '20px' }}>
                        <i className="fa-solid fa-sparkles" style={{ marginRight: '4px' }} />OVERVIEW
                    </span>
                </div>

                {/* Stat Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.8rem', marginBottom: '1.2rem', position: 'relative', zIndex: 1 }}>
                    {[
                        { label: 'Total', value: summary.total, icon: 'fa-users', color: '#a78bfa' },
                        { label: 'Completed', value: summary.completed, icon: 'fa-circle-check', color: '#34d399' },
                        { label: 'In Progress', value: summary.in_progress, icon: 'fa-spinner', color: '#fbbf24' },
                        { label: 'Pending', value: summary.pending, icon: 'fa-clock', color: '#c084fc' },
                        { label: 'Avg Score', value: `${summary.avg_score}%`, icon: 'fa-chart-line', color: '#f472b6' },
                    ].map((stat, i) => (
                        <div key={i} style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', padding: '0.8rem', textAlign: 'center', border: '1px solid rgba(255,255,255,0.08)' }}>
                            <i className={`fa-solid ${stat.icon}`} style={{ fontSize: '1rem', color: stat.color, marginBottom: '0.3rem', display: 'block' }} />
                            <div style={{ fontSize: '1.4rem', fontWeight: '900', color: 'white' }}>{stat.value}</div>
                            <div style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.5)', fontWeight: '600', textTransform: 'uppercase' }}>{stat.label}</div>
                        </div>
                    ))}
                </div>

                {/* Charts */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', position: 'relative', zIndex: 1 }}>
                    <div style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '12px', padding: '1rem', border: '1px solid rgba(255,255,255,0.06)' }}>
                        <h4 style={{ fontSize: '0.75rem', fontWeight: '700', color: 'rgba(255,255,255,0.6)', marginBottom: '0.5rem', margin: '0 0 0.5rem' }}>Completion Status</h4>
                        <ResponsiveContainer width="100%" height={140}>
                            <PieChart>
                                <Pie data={pieData} cx="50%" cy="50%" innerRadius={35} outerRadius={55} dataKey="value" paddingAngle={3}>
                                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                </Pie>
                                <Tooltip contentStyle={{ background: '#1e1b4b', border: 'none', borderRadius: '8px', color: 'white', fontSize: '0.75rem' }} />
                            </PieChart>
                        </ResponsiveContainer>
                        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.8rem', marginTop: '0.3rem' }}>
                            {pieData.map((d, i) => (
                                <span key={i} style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.6)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: COLORS[i] }} />
                                    {d.name}
                                </span>
                            ))}
                        </div>
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '12px', padding: '1rem', border: '1px solid rgba(255,255,255,0.06)' }}>
                        <h4 style={{ fontSize: '0.75rem', fontWeight: '700', color: 'rgba(255,255,255,0.6)', marginBottom: '0.5rem', margin: '0 0 0.5rem' }}>Score Distribution</h4>
                        <ResponsiveContainer width="100%" height={140}>
                            <BarChart data={scoreRanges}>
                                <XAxis dataKey="range" tick={{ fontSize: 9, fill: 'rgba(255,255,255,0.5)' }} axisLine={false} tickLine={false} />
                                <YAxis allowDecimals={false} tick={{ fontSize: 9, fill: 'rgba(255,255,255,0.5)' }} axisLine={false} tickLine={false} />
                                <Tooltip contentStyle={{ background: '#1e1b4b', border: 'none', borderRadius: '8px', color: 'white', fontSize: '0.75rem' }} />
                                <Bar dataKey="count" fill="#a78bfa" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Search + Batch List */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#111827', margin: 0 }}>Interview Batches ({filteredBatches.length})</h2>
                <input
                    type="text"
                    placeholder="Search batches or candidates..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    style={{ padding: '0.6rem 1rem', borderRadius: '10px', border: '1px solid #e2e8f0', width: '280px', fontSize: '0.85rem', outline: 'none' }}
                />
            </div>

            {filteredBatches.length === 0 && (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>No batches found.</div>
            )}

            {filteredBatches.map((batch, idx) => {
                const isExpanded = expandedBatch === batch.batch_id;
                const completionPct = batch.total > 0 ? Math.round((batch.completed / batch.total) * 100) : 0;
                return (
                    <div key={batch.batch_id || idx} style={{ background: 'white', borderRadius: '16px', padding: '1.2rem 1.5rem', marginBottom: '1rem', boxShadow: '0 2px 12px rgba(0,0,0,0.03)', border: '1px solid #f1f5f9' }}>
                        <div
                            onClick={() => setExpandedBatch(isExpanded ? null : batch.batch_id)}
                            style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                        >
                            <div>
                                <div style={{ fontWeight: '800', fontSize: '1rem', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <i className="fa-solid fa-clipboard-list" style={{ color: '#6366f1' }} />
                                    {batch.batch_name}
                                </div>
                                <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '0.3rem' }}>
                                    Created: {batch.created_at} &nbsp;|&nbsp; Invited: {batch.total} &nbsp;|&nbsp; Completed: {batch.completed} &nbsp;|&nbsp; In Progress: {batch.in_progress}
                                </div>
                                {(batch.available_from || batch.available_until) && (
                                    <div style={{ fontSize: '0.72rem', color: '#8b5cf6', marginTop: '0.2rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <i className="fa-regular fa-clock" />
                                        {batch.available_from ? `Start: ${batch.available_from}` : ''}
                                        {batch.available_from && batch.available_until ? ' — ' : ''}
                                        {batch.available_until ? `End: ${batch.available_until}` : ''}
                                    </div>
                                )}
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <div style={{ width: '120px', height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{ width: `${completionPct}%`, height: '100%', background: completionPct === 100 ? '#22c55e' : '#6366f1', borderRadius: '4px', transition: 'width 0.3s' }} />
                                </div>
                                <span style={{ fontSize: '0.8rem', fontWeight: '700', color: completionPct === 100 ? '#22c55e' : '#6366f1' }}>{completionPct}%</span>
                                <i className={`fa-solid fa-chevron-${isExpanded ? 'up' : 'down'}`} style={{ color: '#94a3b8' }} />
                            </div>
                        </div>

                        {isExpanded && (
                            <div style={{ marginTop: '1rem', borderTop: '1px solid #f1f5f9', paddingTop: '1rem' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                                    <thead>
                                        <tr style={{ background: '#f8fafc' }}>
                                            <th style={{ padding: '0.6rem 1rem', textAlign: 'left', color: '#64748b', fontWeight: '700', fontSize: '0.75rem' }}>Name</th>
                                            <th style={{ padding: '0.6rem 1rem', textAlign: 'left', color: '#64748b', fontWeight: '700', fontSize: '0.75rem' }}>Email</th>
                                            <th style={{ padding: '0.6rem 1rem', textAlign: 'center', color: '#64748b', fontWeight: '700', fontSize: '0.75rem' }}>Status</th>
                                            <th style={{ padding: '0.6rem 1rem', textAlign: 'center', color: '#64748b', fontWeight: '700', fontSize: '0.75rem' }}>Score</th>
                                            <th style={{ padding: '0.6rem 1rem', textAlign: 'center', color: '#64748b', fontWeight: '700', fontSize: '0.75rem' }}>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {batch.candidates.map((c, ci) => (
                                            <tr key={ci} style={{ borderBottom: '1px solid #f8fafc' }}>
                                                <td style={{ padding: '0.6rem 1rem', fontWeight: '600', color: '#1e293b' }}>{c.name}</td>
                                                <td style={{ padding: '0.6rem 1rem', color: '#64748b' }}>{c.email}</td>
                                                <td style={{ padding: '0.6rem 1rem', textAlign: 'center' }}>
                                                    <span style={{
                                                        padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.72rem', fontWeight: '700',
                                                        background: c.status === 'Hired' || c.status === 'Interview Passed' ? '#dcfce7' :
                                                            c.status === 'Rejected' || c.status === 'Interview Failed' ? '#fee2e2' :
                                                            c.status_group === 'in_progress' ? '#fef3c7' : '#f1f5f9',
                                                        color: c.status === 'Hired' || c.status === 'Interview Passed' ? '#166534' :
                                                            c.status === 'Rejected' || c.status === 'Interview Failed' ? '#991b1b' :
                                                            c.status_group === 'in_progress' ? '#92400e' : '#475569'
                                                    }}>
                                                        {c.status}
                                                    </span>
                                                </td>
                                                <td style={{ padding: '0.6rem 1rem', textAlign: 'center', fontWeight: '700', color: '#6366f1' }}>
                                                    {c.score_pct !== null ? `${c.score_pct}%` : '—'}
                                                </td>
                                                <td style={{ padding: '0.6rem 1rem', textAlign: 'center' }}>
                                                    {c.status_group === 'pending' && (
                                                        <button
                                                            onClick={() => handleResendInvite(c.id, c.email)}
                                                            disabled={resendingId === c.id}
                                                            style={{
                                                                padding: '0.3rem 0.7rem', borderRadius: '6px', border: '1px solid #6366f1',
                                                                background: resendingId === c.id ? '#e2e8f0' : '#eef2ff',
                                                                color: '#4f46e5', fontSize: '0.7rem', fontWeight: '700',
                                                                cursor: resendingId === c.id ? 'not-allowed' : 'pointer',
                                                                display: 'inline-flex', alignItems: 'center', gap: '4px'
                                                            }}
                                                        >
                                                            <i className={`fa-solid ${resendingId === c.id ? 'fa-spinner fa-spin' : 'fa-paper-plane'}`} />
                                                            {resendingId === c.id ? 'Sending...' : 'Resend'}
                                                        </button>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
