import React, { useEffect, useState, useRef } from 'react';

/**
 * Professional3DAvatar (Indu)
 * A premium, aesthetic AI interviewer with a professional Indian female persona.
 * Includes smooth lip-sync, randomized blinking, and ambient "breathing" movement.
 */
const Professional3DAvatar = ({ isSpeaking = false }) => {
    const [mouthOpen, setMouthOpen] = useState(0);
    const [blink, setBlink] = useState(false);
    const [ambientOffset, setAmbientOffset] = useState(0);
    const frameRef = useRef(0);

    useEffect(() => {
        let animationFrame;
        const animate = () => {
            frameRef.current += 1;

            // 1. Ambient Breathing / Sway (very subtle)
            const sway = Math.sin(frameRef.current * 0.02) * 1.5;
            setAmbientOffset(sway);

            // 2. Lip Sync - smooth multi-segment movement
            if (isSpeaking) {
                if (frameRef.current % 6 === 0) {
                    // Randomized realistic mouth opening
                    setMouthOpen(1.5 + Math.random() * 5.5);
                }
            } else {
                // Return to neutral closed state
                setMouthOpen(prev => Math.max(0, prev - 0.4));
            }

            // 3. Natural Blinking
            if (frameRef.current % 240 === 0) {
                setBlink(true);
                setTimeout(() => setBlink(false), 140);
            }

            animationFrame = requestAnimationFrame(animate);
        };
        animationFrame = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(animationFrame);
    }, [isSpeaking]);

    // Dimensions/Styles
    const headYBase = 105;
    const mouthY = headYBase + 38;

    return (
        <div className="avatar-wrapper" style={{
            position: 'relative',
            width: 280,
            height: 320,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            filter: 'drop-shadow(0 15px 30px rgba(0,0,0,0.15))'
        }}>
            {/* Soft Ambient Background Glow */}
            <div style={{
                position: 'absolute', width: '130%', height: '130%',
                background: 'radial-gradient(circle at center, rgba(139, 92, 246, 0.08) 0%, transparent 65%)',
                pointerEvents: 'none',
                transform: `translateY(${ambientOffset * 0.5}px)`
            }} />

            <svg width="260" height="300" viewBox="0 0 200 240" fill="none" xmlns="http://www.w3.org/2000/svg"
                style={{
                    transform: `translateY(${ambientOffset}px)`,
                    transition: 'transform 0.1s linear'
                }}>

                {/* ── Clothing (Professional Formal) ── */}
                {/* Navy Blue Blazer */}
                <path d="M20 240C20 190 60 178 100 178C140 178 180 190 180 240H20Z" fill="#1e1b4b" />
                {/* Shirt Collar (White) */}
                <path d="M78 178L100 205L122 178C110 182 90 182 78 178Z" fill="#f8fafc" />
                {/* Lapel details */}
                <path d="M48 185C60 180 85 180 95 200L100 220" stroke="#2e2e60" strokeWidth="1" opacity="0.6" />
                <path d="M152 185C140 180 115 180 105 200L100 220" stroke="#2e2e60" strokeWidth="1" opacity="0.6" />

                {/* ── Neck ── */}
                <rect x="88" y="160" width="24" height="24" rx="8" fill="#d4956d" />
                <path d="M88 172C92 175 108 175 112 172" stroke="#b87a55" strokeWidth="0.5" opacity="0.4" />

                {/* ── Face ── */}
                <defs>
                    <linearGradient id="induSkin" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#efc1a0" />
                        <stop offset="100%" stopColor="#d8966b" />
                    </linearGradient>
                    <filter id="beautyBloom">
                        <feGaussianBlur in="SourceGraphic" stdDeviation="0.8" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>
                {/* Refined Oval Head Shape */}
                <ellipse cx="100" cy={headYBase} rx="54" ry="68" fill="url(#induSkin)" filter="url(#beautyBloom)" />

                {/* ── Hair (Professional Polished) ── */}
                {/* Dark brown polished hair with highlights */}
                <path d="M46 95C46 50 70 34 100 34C130 34 154 50 154 95C154 115 148 135 138 145C148 115 145 75 100 75C55 75 52 115 62 145C52 135 46 115 46 95Z" fill="#1c0d06" />
                {/* Subtle highlight sheen */}
                <path d="M70 45C85 40 115 40 130 45" stroke="#3d2114" strokeWidth="3" opacity="0.2" strokeLinecap="round" />

                {/* ── Features ── */}
                {/* Eyes (Refined) */}
                <g opacity={blink ? 0 : 1}>
                    <ellipse cx="76" cy="104" rx="12" ry="8" fill="white" />
                    <circle cx="76" cy="104" r="5" fill="#311c10" />
                    <circle cx="78.5" cy="102" r="1.5" fill="white" opacity="0.8" />

                    <ellipse cx="124" cy="104" rx="12" ry="8" fill="white" />
                    <circle cx="124" cy="104" r="5" fill="#311c10" />
                    <circle cx="126.5" cy="102" r="1.5" fill="white" opacity="0.8" />
                </g>
                {/* Blink Line */}
                {blink && (
                    <>
                        <path d="M64 104C70 106 82 106 88 104" stroke="#4a2c1a" strokeWidth="1.5" strokeLinecap="round" />
                        <path d="M112 104C118 106 130 106 136 104" stroke="#4a2c1a" strokeWidth="1.5" strokeLinecap="round" />
                    </>
                )}

                {/* Eyebrows (Elegant) */}
                <path d="M63 90C68 85 82 85 88 89" stroke="#1c0d06" strokeWidth="2.5" strokeLinecap="round" fill="none" opacity="0.85" />
                <path d="M112 89C118 85 132 85 137 90" stroke="#1c0d06" strokeWidth="2.5" strokeLinecap="round" fill="none" opacity="0.85" />

                {/* Eyelashes (Subtle Beauty touch) */}
                <path d="M63 100L60 98" stroke="#000" strokeWidth="0.8" opacity="0.4" />
                <path d="M137 100L140 98" stroke="#000" strokeWidth="0.8" opacity="0.4" />

                {/* Nose (Soft) */}
                <path d="M97 125C100 120 102 120 103 135" stroke="#b87a55" strokeWidth="1.2" strokeLinecap="round" opacity="0.6" />

                {/* ── Lips & Mouth ── */}
                {/* Lip color (Muted professional mauve/rose) */}
                {isSpeaking ? (
                    <g>
                        {/* Upper Lip */}
                        <path d={`M88 ${mouthY} C92 ${mouthY - 2.5} 108 ${mouthY - 2.5} 112 ${mouthY}`} fill="#a45d4e" />
                        {/* Inner Mouth Gap */}
                        <ellipse cx="100" cy={mouthY + mouthOpen / 2} rx="12" ry={mouthOpen / 2 + 0.5} fill="#3d140c" />
                        {/* Teeth (hint) */}
                        {mouthOpen > 3 && <rect x="91" y={mouthY + 1} width="18" height="2" rx="1" fill="#f8fafc" opacity="0.8" />}
                        {/* Lower Lip */}
                        <path d={`M88 ${mouthY + mouthOpen} C92 ${mouthY + mouthOpen + 4} 108 ${mouthY + mouthOpen + 4} 112 ${mouthY + mouthOpen}`} fill="#945348" />
                    </g>
                ) : (
                    <g>
                        <path d={`M88 ${mouthY} C92 ${mouthY - 3} 96 ${mouthY - 3} 100 ${mouthY - 1.5} C104 ${mouthY - 3} 108 ${mouthY - 3} 112 ${mouthY}`} fill="#a45d4e" />
                        <path d={`M88 ${mouthY + 0.6} C92 ${mouthY + 4.5} 108 ${mouthY + 4.5} 112 ${mouthY + 0.6}`} fill="#945348" />
                        <line x1="88.5" y1={mouthY + 0.5} x2="111.5" y2={mouthY + 0.5} stroke="#7a3a2d" strokeWidth="0.5" opacity="0.5" />
                    </g>
                )}

                {/* Cheek Glow (Professional blush) */}
                <circle cx="70" cy="132" r="10" fill="#f87171" opacity="0.10" />
                <circle cx="130" cy="132" r="10" fill="#f87171" opacity="0.10" />

            </svg>

            {/* Premium Glassmorphism Name Badge */}
            <div style={{
                position: 'absolute', bottom: 15, left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(12px)',
                padding: '4px 18px',
                borderRadius: '100px',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                boxShadow: '0 4px 15px rgba(0,0,0,0.08)',
                color: '#1e293b',
                fontSize: '11px', fontWeight: 800,
                letterSpacing: '1px',
                whiteSpace: 'nowrap',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
            }}>
                <div style={{ width: 6, height: 6, borderRadius: '50%', background: isSpeaking ? '#a855f7' : '#94a3b8', animation: isSpeaking ? 'glow 1s infinite alternate' : 'none' }} />
                INDU • AI RECRUITER
            </div>

            <style>{`
                @keyframes glow {
                    from { box-shadow: 0 0 0px #a855f7; }
                    to { box-shadow: 0 0 10px #a855f7; }
                }
                .avatar-wrapper:hover {
                    filter: drop-shadow(0 20px 40px rgba(0,0,0,0.22));
                }
            `}</style>
        </div>
    );
};

export default Professional3DAvatar;
