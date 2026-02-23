import React, { useEffect, useState, useRef } from 'react';

/**
 * Professional3DAvatar (Indu) - Ultra Premium Edition
 * Features:
 * 1. Pseudo-3D Parallax: Distinct movement layers for head, hair, and torso.
 * 2. Advanced Aesthetics: Refined almond eye shapes, lashes, and polished formal wear.
 * 3. Dynamic Lighting: Rim lights, soft drop shadows, and beauty filters.
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

            // 1. Ambient Movement Layer (Slower breathing/sway)
            const sway = Math.sin(frameRef.current * 0.02) * 1.5;
            setAmbientOffset(sway);

            // 2. Lip Sync - smooth randomized shape interpolation
            if (isSpeaking) {
                if (frameRef.current % 5 === 0) {
                    setMouthOpen(2 + Math.random() * 6);
                }
            } else {
                setMouthOpen(prev => Math.max(0, prev - 0.5));
            }

            // 3. Natural Blinking
            if (frameRef.current % 220 === 0) {
                setBlink(true);
                setTimeout(() => setBlink(false), 120);
            }

            animationFrame = requestAnimationFrame(animate);
        };
        animationFrame = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(animationFrame);
    }, [isSpeaking]);

    // Parallax Factor (simulate depth)
    const pxTorso = ambientOffset * 0.3;
    const pxHead = ambientOffset * 1.0;
    const pxHair = ambientOffset * 1.2;
    const pxEyes = ambientOffset * 1.1;

    return (
        <div style={{ position: 'relative', width: 280, height: 320, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>

            {/* 3D Depth Field Effect */}
            <div style={{
                position: 'absolute', width: '130%', height: '130%',
                background: 'radial-gradient(circle at center, rgba(139, 92, 246, 0.08) 0%, transparent 70%)',
                pointerEvents: 'none'
            }} />

            <svg width="260" height="300" viewBox="0 0 200 240" fill="none" xmlns="http://www.w3.org/2000/svg"
                style={{ filter: 'drop-shadow(0 15px 30px rgba(0,0,0,0.18))' }}>

                {/* ── Torso Layer (Slow Parallax) ── */}
                <g style={{ transform: `translateY(${pxTorso}px)`, transition: 'transform 0.1s linear' }}>
                    {/* Premium Navy Blazer */}
                    <path d="M15 240C15 185 55 174 100 174C145 174 185 185 185 240H15Z" fill="#1e1b4b" />
                    {/* Rim Light on Shoulders */}
                    <path d="M15 240C15 185 55 174 100 174" stroke="rgba(255,255,255,0.06)" strokeWidth="2" opacity="0.6" fill="none" />
                    {/* White Formal Shirt */}
                    <path d="M80 174L100 202L120 174C110 178 90 178 80 174Z" fill="#f8fafc" />
                </g>

                {/* ── Neck ── */}
                <rect x="88" y="160" width="24" height="24" rx="8" fill="#d4956d"
                    style={{ transform: `translateY(${pxHead * 0.8}px)`, transition: 'transform 0.1s linear' }} />

                {/* ── Head & Face Layer (Main Parallax) ── */}
                <g style={{ transform: `translateY(${pxHead}px)`, transition: 'transform 0.1s linear' }}>
                    <defs>
                        <linearGradient id="induSkin" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor="#f2cbb2" />
                            <stop offset="100%" stopColor="#d59771" />
                        </linearGradient>
                        <filter id="beautyBloom">
                            <feGaussianBlur in="SourceGraphic" stdDeviation="0.6" />
                        </filter>
                        <radialGradient id="eyeShadow">
                            <stop offset="0%" stopColor="rgba(0,0,0,0.15)" />
                            <stop offset="100%" stopColor="transparent" />
                        </radialGradient>
                    </defs>
                    {/* Softer, more aesthetic Oval Face Shape */}
                    <path d="M50 100C50 64 72 40 100 40C128 40 150 64 150 100C150 142 124 176 100 176C76 176 50 142 50 100Z" fill="url(#induSkin)" filter="url(#beautyBloom)" />

                    {/* ── Eyes (Almond Shape - Reduced Intensity) ── */}
                    <g style={{ transform: `translateY(${pxEyes - pxHead}px)` }}>
                        {!blink ? (
                            <g>
                                {/* Shadow under brow for depth */}
                                <ellipse cx="77" cy="100" rx="14" ry="6" fill="url(#eyeShadow)" opacity="0.3" />
                                <ellipse cx="123" cy="100" rx="14" ry="6" fill="url(#eyeShadow)" opacity="0.3" />

                                <path d="M64 104C67 100 87 100 90 104C87 109 67 109 64 104Z" fill="white" />
                                <circle cx="77" cy="104" r="5" fill="#311c10" />
                                <circle cx="79" cy="102.5" r="1.5" fill="white" opacity="0.8" />

                                <path d="M110 104C113 100 133 100 136 104C133 109 113 109 110 104Z" fill="white" />
                                <circle cx="123" cy="104" r="5" fill="#311c10" />
                                <circle cx="125" cy="102.5" r="1.5" fill="white" opacity="0.8" />
                            </g>
                        ) : (
                            <g>
                                <path d="M64 104L90 104" stroke="#4a2c1a" strokeWidth="1.2" strokeLinecap="round" />
                                <path d="M110 104L136 104" stroke="#4a2c1a" strokeWidth="1.2" strokeLinecap="round" />
                            </g>
                        )}
                    </g>

                    {/* Feature Detail: Fine Brows */}
                    <path d="M66 94C70 90 82 90 88 93" stroke="#1c0d06" strokeWidth="1.8" strokeLinecap="round" fill="none" opacity="0.6" />
                    <path d="M112 93C118 90 130 90 134 94" stroke="#1c0d06" strokeWidth="1.8" strokeLinecap="round" fill="none" opacity="0.6" />

                    {/* Soft Nose & Blush */}
                    <path d="M100 128C101 125 102 125 102 136" stroke="#b07050" strokeWidth="1" strokeLinecap="round" opacity="0.3" />
                    <circle cx="72" cy="138" r="10" fill="#f87171" opacity="0.06" />
                    <circle cx="128" cy="138" r="10" fill="#f87171" opacity="0.06" />

                    {/* ── Mouth ── */}
                    <g>
                        {isSpeaking ? (
                            <>
                                <path d="M90 152C94 150 106 150 110 152" stroke="#a45d4e" strokeWidth="2.5" strokeLinecap="round" />
                                <ellipse cx="100" cy={152 + mouthOpen / 2} rx="10" ry={mouthOpen / 2 + 0.5} fill="#3d140c" />
                                <path d={`M90 ${152 + mouthOpen} C94 ${152 + mouthOpen + 4} 106 ${152 + mouthOpen + 4} 110 ${152 + mouthOpen}`} fill="#945348" />
                            </>
                        ) : (
                            <g>
                                <path d="M90 152C94 149 106 149 110 152" fill="#a45d4e" />
                                <path d="M90 152.6C94 156 106 156 110 152.6" fill="#945348" />
                            </g>
                        )}
                    </g>
                </g>

                {/* ── Hair Layer (Front Parallax) ── */}
                <g style={{ transform: `translateY(${pxHair}px)`, transition: 'transform 0.1s linear' }}>
                    <path d="M42 100C42 45 65 32 100 32C135 32 158 45 158 100C158 125 152 152 142 165C154 125 148 74 100 74C52 74 46 125 58 165C48 152 42 125 42 100Z" fill="#1b0a03" />
                    <path d="M60 52C80 44 120 44 140 52" stroke="#3d2114" strokeWidth="4" opacity="0.3" strokeLinecap="round" fill="none" />
                </g>
            </svg>

            {/* Premium Indicator Badge */}
            <div style={{
                position: 'absolute', bottom: 15, left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(15, 23, 42, 0.75)',
                backdropFilter: 'blur(12px)',
                padding: '5px 20px',
                borderRadius: '100px',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                color: '#e2e8f0',
                fontSize: '11px', fontWeight: 800,
                letterSpacing: '1.2px',
                whiteSpace: 'nowrap',
                display: 'flex', alignItems: 'center', gap: '8px',
                boxShadow: '0 8px 20px rgba(0,0,0,0.2)'
            }}>
                <div style={{
                    width: 7, height: 7, borderRadius: '50%',
                    background: isSpeaking ? '#a855f7' : '#475569',
                    boxShadow: isSpeaking ? '0 0 10px #a855f7' : 'none',
                    animation: isSpeaking ? 'pulse-glow 1s infinite alternate' : 'none'
                }} />
                INDU • AI RECRUITER
            </div>

            <style>{`
                @keyframes pulse-glow {
                    from { opacity: 0.6; transform: scale(0.9); }
                    to { opacity: 1; transform: scale(1.2); }
                }
            `}</style>
        </div>
    );
};

export default Professional3DAvatar;
