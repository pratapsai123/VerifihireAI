import React from 'react';
import { NavLink } from 'react-router-dom';

const MENU_ITEMS = [
    {
        title: 'OVERVIEW',
        items: [
            { icon: '🏠', label: 'Dashboard', path: '/dashboard' },
        ]
    },
    {
        title: 'MANAGEMENT',
        items: [
            { icon: '📊', label: 'Approvals', path: '/' },
            { icon: '🏢', label: 'Companies', path: '/companies' },
        ]
    }
];

function Sidebar() {
    return (
        <aside style={{
            width: 280,
            background: 'var(--navy-primary)',
            color: '#fff',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '4px 0 20px rgba(0,0,0,0.15)',
            zIndex: 1000,
        }}>
            <div style={{
                padding: '32px 24px',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
            }}>
                <div style={{
                    width: 38,
                    height: 38,
                    borderRadius: '10px',
                    background: 'var(--blue-accent)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontWeight: 'bold',
                    fontSize: '20px',
                    boxShadow: '0 4px 10px rgba(79, 70, 229, 0.4)'
                }}>V</div>
                <div>
                    <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700, letterSpacing: '0.5px', color: '#fff' }}>VeriFiHire</h2>
                    <div style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.5)', fontWeight: 600, letterSpacing: '1px' }}>ADMIN PLATFORM</div>
                </div>
            </div>

            <nav style={{ padding: '10px 0', flex: 1 }}>
                {MENU_ITEMS.map((section, idx) => (
                    <div key={idx} style={{ marginBottom: '20px' }}>
                        <h3 style={{
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            padding: '0 30px',
                            marginBottom: '10px',
                            color: 'rgba(255,255,255,0.3)',
                            textTransform: 'uppercase',
                            letterSpacing: '1.5px'
                        }}>{section.title}</h3>
                        {section.items.map((item, i) => (
                            <NavLink
                                key={i}
                                to={item.path}
                                style={({ isActive }) => ({
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px',
                                    padding: '12px 30px',
                                    textDecoration: 'none',
                                    color: isActive ? '#fff' : 'rgba(255,255,255,0.6)',
                                    background: isActive ? 'linear-gradient(90deg, rgba(79,70,229,0.2) 0%, transparent 100%)' : 'transparent',
                                    borderLeft: isActive ? '4px solid var(--blue-accent)' : '4px solid transparent',
                                    transition: 'all 0.2s ease',
                                    fontSize: '0.85rem',
                                    fontWeight: isActive ? 600 : 500,
                                })}
                            >
                                <span style={{
                                    fontSize: '1.1rem',
                                    color: 'inherit',
                                    opacity: 0.8
                                }}>{item.icon}</span>
                                {item.label}
                            </NavLink>
                        ))}
                    </div>
                ))}
            </nav>

            <div style={{
                padding: '24px 30px',
                borderTop: '1px solid rgba(255,255,255,0.05)',
                fontSize: '0.75rem',
                color: 'rgba(255,255,255,0.3)',
                fontWeight: 500
            }}>
                &copy; 2026 VeriFiHire AI
                <div style={{ fontSize: '0.65rem', marginTop: 4 }}>Version 2.0.4 Premium</div>
            </div>
        </aside>
    );
}

export default Sidebar;
