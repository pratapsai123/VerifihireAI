import { useEffect, useState } from 'react';

/**
 * ImpersonationBanner – Dynamic Island style pill indicator.
 * Floats at the top-center of the screen without blocking the header.
 */
function ImpersonationBanner() {
    const [info, setInfo] = useState(null);

    useEffect(() => {
        const active = localStorage.getItem('impersonation_active') === 'true';
        if (active) {
            try {
                const company = JSON.parse(localStorage.getItem('impersonation_company') || '{}');
                setInfo(company);
            } catch {
                setInfo({});
            }
        }
    }, []);

    if (!info) return null;

    const handleExit = () => {
        const origToken = localStorage.getItem('superadmin_token');
        const origUser = localStorage.getItem('superadmin_user');

        localStorage.removeItem('impersonation_active');
        localStorage.removeItem('impersonation_company');
        localStorage.removeItem('superadmin_token');
        localStorage.removeItem('superadmin_user');

        if (origToken) localStorage.setItem('authToken', origToken);
        if (origUser) localStorage.setItem('user', origUser);

        window.location.href = '/superadmin';
    };

    return (
        <>
            <style>{`
                @keyframes islandExpand {
                    from { transform: translateX(-50%) scaleX(0.6); opacity: 0; }
                    to   { transform: translateX(-50%) scaleX(1);   opacity: 1; }
                }
                .impersonation-pill {
                    position: fixed;
                    top: 8px;
                    left: 50%;
                    transform: translateX(-50%);
                    z-index: 99999;
                    background: #0a0a0a;
                    color: #fff;
                    border-radius: 999px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 6px 14px;
                    font-size: 0.78rem;
                    font-weight: 600;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.45);
                    cursor: pointer;
                    transition: padding 0.3s ease, gap 0.3s ease, background 0.2s;
                    animation: islandExpand 0.35s cubic-bezier(0.34,1.56,0.64,1) forwards;
                    white-space: nowrap;
                    user-select: none;
                }
                .impersonation-pill:hover {
                    background: #1a1a2e;
                }
                .impersonation-pill .pill-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #a78bfa;
                    flex-shrink: 0;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.6; transform: scale(0.85); }
                }
                .impersonation-pill .pill-label {
                    color: #d4d4d4;
                    font-size: 0.72rem;
                }
                .impersonation-pill .pill-company {
                    color: #a78bfa;
                    font-weight: 700;
                }
                .impersonation-pill .pill-exit {
                    margin-left: 4px;
                    padding: 2px 10px;
                    border-radius: 999px;
                    background: rgba(167,139,250,0.18);
                    color: #a78bfa;
                    border: 1px solid rgba(167,139,250,0.35);
                    font-size: 0.72rem;
                    font-weight: 700;
                    cursor: pointer;
                    transition: background 0.2s, color 0.2s;
                    white-space: nowrap;
                }
                .impersonation-pill .pill-exit:hover {
                    background: #a78bfa;
                    color: #fff;
                }
            `}</style>

            <div
                className="impersonation-pill"
                title="Click Exit to return to admin panel"
            >
                <span className="pill-dot" />
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span className="pill-label">Viewing as</span>
                    <span className="pill-company">Superadmin</span>
                </span>
                <button
                    className="pill-exit"
                    onClick={e => { e.stopPropagation(); handleExit(); }}
                >
                    ← Exit
                </button>
            </div>
        </>
    );
}

export default ImpersonationBanner;
