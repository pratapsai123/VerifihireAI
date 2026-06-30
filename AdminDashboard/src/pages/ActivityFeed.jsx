import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

/* ──────────────────────── helpers ──────────────────────── */

function formatRelativeTime(ts) {
    const diff = Date.now() - new Date(ts).getTime();
    const secs = Math.floor(diff / 1000);
    if (secs < 60) return 'Just now';
    const mins = Math.floor(secs / 60);
    if (mins < 60) return `${mins} minute${mins > 1 ? 's' : ''} ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs} hour${hrs > 1 ? 's' : ''} ago`;
    const days = Math.floor(hrs / 24);
    if (days < 30) return `${days} day${days > 1 ? 's' : ''} ago`;
    return new Date(ts).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

const EVENT_TYPES = {
    registration: { icon: '📝', label: 'Registration', color: '#4F46E5', bg: 'rgba(79, 70, 229, 0.1)' },
    approved: { icon: '✅', label: 'Approved', color: '#05CD99', bg: 'rgba(5, 205, 153, 0.1)' },
    rejected: { icon: '❌', label: 'Rejected', color: '#EE5D50', bg: 'rgba(238, 93, 80, 0.1)' },
    pending: { icon: '⏳', label: 'Pending', color: '#FFB547', bg: 'rgba(255, 181, 71, 0.1)' },
    user_signup: { icon: '👤', label: 'User Signup', color: '#7C3AED', bg: 'rgba(124, 58, 237, 0.1)' },
    user_approved: { icon: '🟢', label: 'User Approved', color: '#059669', bg: 'rgba(5, 150, 105, 0.1)' },
};

function buildEvents(companies, users) {
    const events = [];

    companies.forEach(c => {
        // Registration event
        events.push({
            id: `comp-reg-${c.id}`,
            type: 'registration',
            title: `${c.name} registered`,
            subtitle: `Domain: ${c.domain || 'N/A'} · Admin: ${c.primary_admin?.email || 'N/A'}`,
            entity: 'company',
            entityName: c.name,
            timestamp: c.created_at,
        });

        // Approval/rejection event
        if (c.approval_status === 'approved' && c.approved_at) {
            events.push({
                id: `comp-app-${c.id}`,
                type: 'approved',
                title: `${c.name} was approved`,
                subtitle: `Organization granted platform access`,
                entity: 'company',
                entityName: c.name,
                timestamp: c.approved_at,
            });
        } else if (c.approval_status === 'rejected') {
            events.push({
                id: `comp-rej-${c.id}`,
                type: 'rejected',
                title: `${c.name} was rejected`,
                subtitle: c.rejected_reason || 'Registration denied by admin',
                entity: 'company',
                entityName: c.name,
                timestamp: c.updated_at || c.created_at,
            });
        }
    });

    users.forEach(u => {
        events.push({
            id: `user-reg-${u.id}`,
            type: 'user_signup',
            title: `${u.first_name} ${u.last_name} signed up`,
            subtitle: `${u.organization_name || 'No org'} · ${u.role?.replace(/_/g, ' ') || 'Unknown role'}`,
            entity: 'user',
            entityName: `${u.first_name} ${u.last_name}`,
            timestamp: u.registered_at || u.created_at,
        });

        if (u.is_approved) {
            events.push({
                id: `user-app-${u.id}`,
                type: 'user_approved',
                title: `${u.first_name} ${u.last_name} was approved`,
                subtitle: `${u.organization_name || 'No org'} · ${u.email}`,
                entity: 'user',
                entityName: `${u.first_name} ${u.last_name}`,
                timestamp: u.approved_at || u.registered_at || u.created_at,
            });
        }
    });

    // Sort by timestamp descending
    events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    return events;
}

/* ──────────────────────── TimelineEvent ──────────────────────── */

function TimelineEvent({ event, isLast }) {
    const et = EVENT_TYPES[event.type] || EVENT_TYPES.registration;
    const [hovered, setHovered] = useState(false);

    return (
        <div
            style={{
                display: 'flex', gap: 20, position: 'relative',
            }}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
        >
            {/* Timeline line + dot */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0 }}>
                <div style={{
                    width: 44, height: 44, borderRadius: 14,
                    background: hovered ? et.color : et.bg,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1.2rem', zIndex: 1,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    boxShadow: hovered ? `0 6px 20px ${et.color}40` : 'none',
                    transform: hovered ? 'scale(1.1)' : 'scale(1)',
                }}>
                    {et.icon}
                </div>
                {!isLast && <div style={{ width: 2, flex: 1, background: '#f0f3f8', marginTop: 4 }} />}
            </div>

            {/* Content */}
            <div style={{
                flex: 1, paddingBottom: isLast ? 0 : 32,
                background: hovered ? '#F8FAFC' : 'transparent',
                padding: '14px 18px', borderRadius: 16, marginTop: -6,
                transition: 'background 0.2s ease',
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6, flexWrap: 'wrap', gap: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontWeight: 700, fontSize: '0.92rem', color: '#2B3674' }}>{event.title}</span>
                        <span style={{
                            padding: '3px 10px', borderRadius: 999, fontSize: '0.6rem', fontWeight: 800,
                            background: et.bg, color: et.color, textTransform: 'uppercase', letterSpacing: '0.5px',
                        }}>{et.label}</span>
                    </div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#A3AED0', whiteSpace: 'nowrap' }}>
                        {formatRelativeTime(event.timestamp)}
                    </span>
                </div>
                <p style={{ margin: 0, fontSize: '0.8rem', color: '#707EAE', fontWeight: 500, lineHeight: 1.5 }}>
                    {event.subtitle}
                </p>
                <div style={{ fontSize: '0.7rem', color: '#A3AED0', fontWeight: 500, marginTop: 6 }}>
                    {new Date(event.timestamp).toLocaleString('en-US', {
                        weekday: 'short', month: 'short', day: 'numeric', year: 'numeric',
                        hour: 'numeric', minute: '2-digit'
                    })}
                </div>
            </div>
        </div>
    );
}

/* ──────────────────────── ActivityFeed ──────────────────────── */

function ActivityFeed() {
    const [companies, setCompanies] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [visibleCount, setVisibleCount] = useState(30);

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
            console.error('Failed to fetch activity data:', err);
        } finally {
            if (!silent) setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(() => fetchData(true), 30000);
        return () => clearInterval(interval);
    }, [fetchData]);

    const allEvents = buildEvents(companies, users);

    const filteredEvents = filter === 'all'
        ? allEvents
        : allEvents.filter(e => {
            if (filter === 'companies') return e.entity === 'company';
            if (filter === 'users') return e.entity === 'user';
            if (filter === 'approvals') return e.type === 'approved' || e.type === 'user_approved';
            if (filter === 'rejections') return e.type === 'rejected';
            return true;
        });

    const visibleEvents = filteredEvents.slice(0, visibleCount);

    const FILTER_TABS = [
        { key: 'all', label: 'All Events', icon: '📋' },
        { key: 'companies', label: 'Companies', icon: '🏢' },
        { key: 'users', label: 'Users', icon: '👤' },
        { key: 'approvals', label: 'Approvals', icon: '✅' },
        { key: 'rejections', label: 'Rejections', icon: '❌' },
    ];

    return (
        <div style={{ animation: 'slideIn 0.5s ease-out' }}>
            {/* Header */}
            <div style={{ marginBottom: '1.8rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '1.6rem', fontWeight: 800, color: '#2B3674', letterSpacing: '-0.5px' }}>
                        Activity Feed
                    </h1>
                    <p style={{ margin: '4px 0 0', color: '#707EAE', fontSize: '0.85rem', fontWeight: 500 }}>
                        Real-time timeline of all platform events —{' '}
                        <span style={{ color: '#4F46E5', fontWeight: 700 }}>{allEvents.length}</span> total events
                    </p>
                </div>
                <div style={{
                    background: '#fff', padding: '10px 16px', borderRadius: 14,
                    border: '1px solid #f0f3f8', fontSize: '0.8rem', fontWeight: 600,
                    color: '#707EAE',
                    boxShadow: '0 4px 12px rgba(112, 144, 176, 0.04)',
                }}>
                    🔄 Auto-refreshes every 30s
                </div>
            </div>

            {/* Filter Tabs */}
            <div style={{
                display: 'flex', gap: 6, marginBottom: '1.5rem',
                background: '#fff', padding: 8, borderRadius: 16,
                border: '1px solid #f0f3f8',
                boxShadow: '0 4px 12px rgba(112, 144, 176, 0.04)',
            }}>
                {FILTER_TABS.map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => { setFilter(tab.key); setVisibleCount(30); }}
                        style={{
                            padding: '10px 18px', borderRadius: 12, border: 'none',
                            background: filter === tab.key ? '#4F46E5' : 'transparent',
                            color: filter === tab.key ? '#fff' : '#707EAE',
                            fontWeight: 700, cursor: 'pointer', fontSize: '0.8rem',
                            transition: 'all 0.2s ease',
                            display: 'flex', alignItems: 'center', gap: 6,
                        }}
                    >
                        <span>{tab.icon}</span> {tab.label}
                        {filter === tab.key && (
                            <span style={{
                                background: 'rgba(255,255,255,0.2)', padding: '2px 8px',
                                borderRadius: 999, fontSize: '0.65rem', fontWeight: 800,
                            }}>{filteredEvents.length}</span>
                        )}
                    </button>
                ))}
            </div>

            {/* Timeline */}
            {loading ? (
                <div style={{ textAlign: 'center', padding: '5rem', color: '#A3AED0' }}>
                    <div style={{
                        width: 48, height: 48, border: '4px solid #F4F7FE',
                        borderTop: '4px solid #4F46E5', borderRadius: '50%',
                        margin: '0 auto 16px', animation: 'spin 1s linear infinite'
                    }} />
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Loading activity...</span>
                </div>
            ) : visibleEvents.length === 0 ? (
                <div style={{
                    textAlign: 'center', padding: '6rem', background: '#fff', borderRadius: 24,
                    boxShadow: '0 10px 30px rgba(112, 144, 176, 0.06)', color: '#A3AED0',
                }}>
                    <div style={{ fontSize: '4rem', marginBottom: 16 }}>📭</div>
                    <div style={{ fontWeight: 800, fontSize: '1.2rem', color: '#2B3674' }}>No Events Found</div>
                    <p style={{ fontSize: '0.85rem', marginTop: 8, color: '#707EAE' }}>
                        {filter !== 'all' ? 'Try a different filter' : 'Activity will appear here as the platform is used'}
                    </p>
                </div>
            ) : (
                <div style={{
                    background: '#fff', borderRadius: 24, padding: '28px',
                    boxShadow: '0 10px 30px rgba(112, 144, 176, 0.06)',
                    border: '1px solid #f0f3f8',
                }}>
                    {visibleEvents.map((event, i) => (
                        <TimelineEvent key={event.id} event={event} isLast={i === visibleEvents.length - 1} />
                    ))}

                    {visibleCount < filteredEvents.length && (
                        <div style={{ textAlign: 'center', paddingTop: 24 }}>
                            <button
                                onClick={() => setVisibleCount(prev => prev + 30)}
                                style={{
                                    padding: '12px 32px', borderRadius: 14, border: '1px solid #e9edf7',
                                    background: '#fff', color: '#4F46E5', fontWeight: 700,
                                    fontSize: '0.85rem', cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    boxShadow: '0 4px 12px rgba(79, 70, 229, 0.08)',
                                }}
                                onMouseEnter={e => { e.currentTarget.style.background = '#4F46E5'; e.currentTarget.style.color = '#fff'; }}
                                onMouseLeave={e => { e.currentTarget.style.background = '#fff'; e.currentTarget.style.color = '#4F46E5'; }}
                            >
                                Load More ({filteredEvents.length - visibleCount} remaining)
                            </button>
                        </div>
                    )}
                </div>
            )}

            <style>{`
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            `}</style>
        </div>
    );
}

export default ActivityFeed;
