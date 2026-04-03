import React from 'react';

function Header() {
    const user = (() => { try { return JSON.parse(localStorage.getItem('user') || '{}'); } catch { return {}; } })();

    const handleLogout = () => {
        localStorage.clear();
        window.location.href = '/login';
    };

    return (
        <header style={{
            height: 64,
            background: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(10px)',
            borderBottom: '1px solid #e9edf7',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 30px',
            position: 'sticky',
            top: 0,
            zIndex: 900,
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '30px' }}>
                <div style={{ position: 'relative' }}>
                    <span style={{
                        position: 'absolute',
                        left: 14,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        color: 'var(--text-secondary)',
                        fontSize: '0.9rem'
                    }}>🔍</span>
                    <input
                        type="text"
                        placeholder="Search dashboard..."
                        style={{
                            padding: '12px 16px 12px 42px',
                            borderRadius: '30px',
                            border: 'none',
                            background: '#F4F7FE',
                            fontSize: '0.85rem',
                            width: '350px',
                            outline: 'none',
                            color: 'var(--text-main)',
                            fontWeight: 500
                        }}
                    />
                </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-main)' }}>
                            {user.first_name || 'Admin'} {user.last_name || ''}
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Superadministrator</div>
                    </div>
                    <div style={{
                        width: 38,
                        height: 38,
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, var(--blue-accent), var(--blue-secondary))',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        boxShadow: '0 4px 8px rgba(79, 70, 229, 0.15)'
                    }}>
                        {(user.first_name || 'A').charAt(0)}
                    </div>
                </div>
                <button
                    onClick={handleLogout}
                    style={{
                        background: '#fff',
                        border: '1px solid #fee2e2',
                        padding: '10px 20px',
                        borderRadius: '12px',
                        fontSize: '0.8rem',
                        fontWeight: 700,
                        color: 'var(--status-error)',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        boxShadow: '0 2px 6px rgba(238, 93, 80, 0.05)'
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = '#fef2f2'; }}
                    onMouseLeave={e => { e.currentTarget.style.background = '#fff'; }}
                >
                    Logout
                </button>
            </div>
        </header>
    );
}

export default Header;
