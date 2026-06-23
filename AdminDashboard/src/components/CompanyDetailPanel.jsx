import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

const STATUS_COLORS = {
    pending: { bg: 'rgba(255, 181, 71, 0.12)', text: '#FFB547', border: 'rgba(255, 181, 71, 0.2)' },
    approved: { bg: 'rgba(5, 205, 153, 0.12)', text: '#05CD99', border: 'rgba(5, 205, 153, 0.2)' },
    rejected: { bg: 'rgba(238, 93, 80, 0.12)', text: '#EE5D50', border: 'rgba(238, 93, 80, 0.2)' },
};

function StatusBadge({ status }) {
    const st = typeof status === 'boolean' ? (status ? 'approved' : 'pending') : status;
    const c = STATUS_COLORS[st] || { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
    const label = typeof status === 'boolean' ? (status ? 'Approved' : 'Pending') : status;
    return (
        <span style={{
            padding: '4px 12px', borderRadius: 999, fontSize: '0.65rem', fontWeight: 800,
            letterSpacing: '0.05em', background: c.bg, color: c.text,
            border: `1px solid ${c.border}`, textTransform: 'uppercase',
        }}>{label}</span>
    );
}

function TimelineItem({ icon, title, subtitle, time, color, isLast }) {
    return (
        <div style={{ display: 'flex', gap: 14, position: 'relative' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{
                    width: 36, height: 36, borderRadius: '10px',
                    background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1rem', flexShrink: 0, zIndex: 1,
                }}>{icon}</div>
                {!isLast && <div style={{ width: 2, flex: 1, background: '#f0f3f8', marginTop: 4 }} />}
            </div>
            <div style={{ paddingBottom: isLast ? 0 : 20, flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-main)' }}>{title}</div>
                {subtitle && <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 500, marginTop: 2 }}>{subtitle}</div>}
                {time && <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 600, marginTop: 4 }}>{time}</div>}
            </div>
        </div>
    );
}

function CompanyDetailPanel({ company, onClose, onApprove, onReject, actionLoading }) {
    const [companyUsers, setCompanyUsers] = useState([]);
    const [loadingUsers, setLoadingUsers] = useState(true);

    useEffect(() => {
        if (!company) return;
        setLoadingUsers(true);
        axios.get(`${API_BASE_URL}/superadmin/users/`)
            .then(res => {
                const users = (res.data.users || []).filter(
                    u => u.company_id === company.id || u.organization_name === company.name
                );
                setCompanyUsers(users);
            })
            .catch(() => setCompanyUsers([]))
            .finally(() => setLoadingUsers(false));
    }, [company]);

    if (!company) return null;

    const isLoading = actionLoading === `comp-${company.id}`;
    const admin = company.primary_admin;

    // Count user roles
    const companyAdminsCount = loadingUsers ? '...' : companyUsers.filter(u => u.role === 'company_admin').length;
    const hrManagersCount = loadingUsers ? '...' : companyUsers.filter(u => u.role === 'hr_manager').length;
    const hrsCount = loadingUsers ? '...' : companyUsers.filter(u => u.role === 'hr').length;
    const interviewersCount = loadingUsers ? '...' : companyUsers.filter(u => u.role === 'interviewer').length;

    // Build timeline
    const timeline = [];
    timeline.push({
        icon: '📝', title: 'Company Registered',
        subtitle: `${company.name} was registered on the platform`,
        time: new Date(company.created_at).toLocaleString(),
        color: '#4F46E5',
    });
    if (company.approval_status === 'approved' && company.approved_at) {
        timeline.push({
            icon: '✅', title: 'Approved',
            subtitle: 'Company registration was approved by platform admin',
            time: new Date(company.approved_at).toLocaleString(),
            color: '#05CD99',
        });
    } else if (company.approval_status === 'rejected') {
        timeline.push({
            icon: '❌', title: 'Rejected',
            subtitle: company.rejected_reason || 'Company registration was rejected',
            time: null,
            color: '#EE5D50',
        });
    } else if (company.approval_status === 'pending') {
        timeline.push({
            icon: '⏳', title: 'Pending Approval',
            subtitle: 'Awaiting platform admin review',
            time: null,
            color: '#FFB547',
        });
    }

    return (
        <>
            {/* Backdrop */}
            <div
                onClick={onClose}
                style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(10, 25, 47, 0.5)', backdropFilter: 'blur(4px)',
                    zIndex: 2000, animation: 'fadeIn 0.3s ease',
                }}
            />

            {/* Panel */}
            <div style={{
                position: 'fixed', top: 0, right: 0, bottom: 0,
                width: '520px', maxWidth: '90vw',
                background: '#fff', zIndex: 2001,
                boxShadow: '-20px 0 60px rgba(0,0,0,0.15)',
                display: 'flex', flexDirection: 'column',
                animation: 'slideInRight 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
                overflowY: 'auto',
            }}>
                {/* Header */}
                <div style={{
                    padding: '24px 28px', borderBottom: '1px solid #f0f3f8',
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    position: 'sticky', top: 0, background: '#fff', zIndex: 1,
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                        <div style={{
                            width: 48, height: 48, borderRadius: 14,
                            background: company.approval_status === 'approved'
                                ? 'linear-gradient(135deg, #05CD99, #00BFA6)'
                                : 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            color: '#fff', fontWeight: 800, fontSize: '1.3rem',
                        }}>{company.name.charAt(0).toUpperCase()}</div>
                        <div>
                            <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>{company.name}</h2>
                            <StatusBadge status={company.approval_status} />
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            width: 36, height: 36, borderRadius: 10, border: '1px solid #f0f3f8',
                            background: '#F4F7FE', cursor: 'pointer',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: '1.1rem', color: 'var(--text-secondary)',
                            transition: 'all 0.2s ease',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.background = '#EE5D50'; e.currentTarget.style.color = '#fff'; }}
                        onMouseLeave={e => { e.currentTarget.style.background = '#F4F7FE'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
                    >✕</button>
                </div>

                {/* Content */}
                <div style={{ padding: '24px 28px', flex: 1 }}>
                    {/* Info Grid */}
                    <div style={{
                        display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 28,
                    }}>
                        <div style={{ background: '#F4F7FE', borderRadius: 14, padding: '16px' }}>
                            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 6 }}>Domain</div>
                            <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)' }}>🌐 {company.domain || 'Not set'}</div>
                        </div>
                        <div style={{ background: '#F4F7FE', borderRadius: 14, padding: '16px' }}>
                            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 6 }}>Total Users</div>
                            <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)' }}>👥 {company.user_count || 0} employees</div>
                        </div>
                        <div style={{ background: '#F4F7FE', borderRadius: 14, padding: '16px' }}>
                            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 6 }}>Registered</div>
                            <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)' }}>📅 {new Date(company.created_at).toLocaleDateString()}</div>
                        </div>
                        <div style={{ background: '#F4F7FE', borderRadius: 14, padding: '16px' }}>
                            <div style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 6 }}>Admin Contact</div>
                            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', wordBreak: 'break-all' }}>✉️ {admin?.email || 'N/A'}</div>
                        </div>
                    </div>

                    {/* Team Composition / Role Breakdown */}
                    <div style={{
                        background: '#fff',
                        borderRadius: 16,
                        padding: '20px',
                        border: '1px solid #f0f3f8',
                        boxShadow: '0 4px 20px rgba(112, 144, 176, 0.05)',
                        marginBottom: 28
                    }}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: 14
                        }}>
                            <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#4F46E5', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                Team Composition
                            </span>
                            {!loadingUsers && (
                                <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                                    Total: {companyUsers.length}
                                </span>
                            )}
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
                            <div style={{ textAlign: 'center', background: '#F4F7FE', padding: '12px 6px', borderRadius: 12, border: '1px solid rgba(0,0,0,0.01)' }}>
                                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#2B3674' }}>{companyAdminsCount}</div>
                                <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#707EAE', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.2px' }}>Admins</div>
                            </div>
                            <div style={{ textAlign: 'center', background: '#F4F7FE', padding: '12px 6px', borderRadius: 12, border: '1px solid rgba(0,0,0,0.01)' }}>
                                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#2B3674' }}>{hrManagersCount}</div>
                                <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#707EAE', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.2px' }}>HR Managers</div>
                            </div>
                            <div style={{ textAlign: 'center', background: '#F4F7FE', padding: '12px 6px', borderRadius: 12, border: '1px solid rgba(0,0,0,0.01)' }}>
                                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#2B3674' }}>{hrsCount}</div>
                                <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#707EAE', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.2px' }}>HRs</div>
                            </div>
                            <div style={{ textAlign: 'center', background: '#F4F7FE', padding: '12px 6px', borderRadius: 12, border: '1px solid rgba(0,0,0,0.01)' }}>
                                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#2B3674' }}>{interviewersCount}</div>
                                <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#707EAE', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.2px' }}>Interviewers</div>
                            </div>
                        </div>
                    </div>

                    {/* Approval Timeline */}
                    <div style={{ marginBottom: 28 }}>
                        <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: 16, color: 'var(--text-main)' }}>Approval Timeline</h3>
                        <div style={{ paddingLeft: 4 }}>
                            {timeline.map((item, i) => (
                                <TimelineItem key={i} {...item} isLast={i === timeline.length - 1} />
                            ))}
                        </div>
                    </div>

                    {/* Company Users */}
                    <div style={{ marginBottom: 28 }}>
                        <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: 16, color: 'var(--text-main)' }}>
                            Company Users {!loadingUsers && <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>({companyUsers.length})</span>}
                        </h3>
                        {loadingUsers ? (
                            <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Loading users...</div>
                        ) : companyUsers.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.8rem', background: '#F4F7FE', borderRadius: 14 }}>No users found for this company</div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                {companyUsers.map(user => (
                                    <div key={user.id} style={{
                                        display: 'flex', alignItems: 'center', gap: 12,
                                        padding: '12px 14px', borderRadius: 14, background: '#F4F7FE',
                                        transition: 'all 0.2s ease',
                                    }}
                                        onMouseEnter={e => e.currentTarget.style.background = '#EBF0FE'}
                                        onMouseLeave={e => e.currentTarget.style.background = '#F4F7FE'}
                                    >
                                        <div style={{
                                            width: 36, height: 36, borderRadius: 10,
                                            background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            color: '#fff', fontWeight: 700, fontSize: '0.8rem', flexShrink: 0,
                                        }}>{(user.first_name || 'U').charAt(0)}</div>
                                        <div style={{ flex: 1, minWidth: 0 }}>
                                            <div style={{ fontWeight: 700, fontSize: '0.82rem', color: 'var(--text-main)' }}>{user.first_name} {user.last_name}</div>
                                            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user.email}</div>
                                            {user.manager_name && (
                                                <div style={{ fontSize: '0.68rem', color: '#4F46E5', fontWeight: 600, marginTop: 2, display: 'flex', alignItems: 'center', gap: 4 }}>
                                                    <span>↳</span> Reports to: {user.manager_name}
                                                </div>
                                            )}
                                        </div>
                                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4, flexShrink: 0 }}>
                                            <span style={{
                                                padding: '2px 8px', borderRadius: 999, fontSize: '0.6rem', fontWeight: 700,
                                                background: 'rgba(79, 70, 229, 0.1)', color: '#4F46E5', textTransform: 'uppercase',
                                            }}>{user.role?.replace(/_/g, ' ')}</span>
                                            <StatusBadge status={user.is_approved} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Action Buttons */}
                {(company.approval_status === 'pending' && onApprove && onReject) && (
                    <div style={{
                        padding: '20px 28px', borderTop: '1px solid #f0f3f8',
                        display: 'flex', gap: 12,
                        position: 'sticky', bottom: 0, background: '#fff',
                    }}>
                        <button
                            disabled={isLoading}
                            onClick={() => onApprove(company.id)}
                            style={{
                                flex: 1, padding: '14px 20px', borderRadius: 14, border: 'none',
                                background: 'linear-gradient(135deg, #05CD99, #00BFA6)',
                                color: '#fff', fontWeight: 700, fontSize: '0.85rem',
                                cursor: isLoading ? 'wait' : 'pointer',
                                boxShadow: '0 4px 12px rgba(5, 205, 153, 0.3)',
                                transition: 'all 0.2s ease',
                                opacity: isLoading ? 0.6 : 1,
                            }}
                        >✅ Approve Company</button>
                        <button
                            disabled={isLoading}
                            onClick={() => {
                                const reason = prompt('Reject reason?');
                                if (reason) onReject(company.id, reason);
                            }}
                            style={{
                                flex: 1, padding: '14px 20px', borderRadius: 14,
                                border: '2px solid #EE5D50', background: 'transparent',
                                color: '#EE5D50', fontWeight: 700, fontSize: '0.85rem',
                                cursor: isLoading ? 'wait' : 'pointer',
                                transition: 'all 0.2s ease',
                                opacity: isLoading ? 0.6 : 1,
                            }}
                        >❌ Reject</button>
                    </div>
                )}
            </div>

            <style>{`
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
            `}</style>
        </>
    );
}

export default CompanyDetailPanel;
