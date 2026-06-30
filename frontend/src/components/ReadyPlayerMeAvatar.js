import React, { useEffect, useState } from 'react';

/**
 * JARVIS Visual Core - Stark Industries EXTREME BLUE EDITION
 * 
 * A high-intensity, multi-layered holographic core in neon blue.
 * Features:
 * 1. Electric Blue Bloom: Multi-layered stroke glow for a "cold" high-tech light feel.
 * 2. Data Fragments: Floating geometric 'UI bits' for a more complex HUD look.
 * 3. Transparent Backdrop: Removed the shadow for a cleaner integration.
 * 4. Technical Arcs: Fragmented HUD arcs with high-speed secondary movements in cyan.
 */

const ReadyPlayerMeAvatar = ({ isSpeaking = false }) => {
    const [pulse, setPulse] = useState(1);
    const [glitch, setGlitch] = useState(false);

    useEffect(() => {
        if (isSpeaking) {
            const interval = setInterval(() => {
                setPulse(0.9 + Math.random() * 0.3);
                if (Math.random() > 0.95) {
                    setGlitch(true);
                    setTimeout(() => setGlitch(false), 50);
                }
            }, 60);
            return () => clearInterval(interval);
        } else {
            setPulse(1);
        }
    }, [isSpeaking]);

    return (
        <div style={{
            width: '100%',
            height: '240px',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            borderRadius: '12px',
            background: 'transparent'
        }}>
            <svg width="200" height="200" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ zIndex: 1, filter: glitch ? 'hue-rotate(60deg) brightness(1.8)' : 'none' }}>
                <defs>
                    <filter id="blueBloom" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="1.5" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                    <filter id="extremeBlueBloom" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="3.5" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>

                    <radialGradient id="jarvisBlueCore" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stopColor="#fff" />
                        <stop offset="30%" stopColor="#00f2ff" />
                        <stop offset="60%" stopColor="#0066ff" />
                        <stop offset="100%" stopColor="#001133" />
                    </radialGradient>

                    <linearGradient id="blueSpikeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="transparent" />
                        <stop offset="50%" stopColor="#00f2ff" />
                        <stop offset="100%" stopColor="transparent" />
                    </linearGradient>
                </defs>

                {/* 1. LAYER: Fragmented Outer Arcs (The Stark HUD) */}
                <g className="rotate-slow">
                    <path d="M50 4 A46 46 0 0 1 96 50" stroke="#00f2ff" strokeWidth="0.5" opacity="0.3" strokeDasharray="2 10 5 15" />
                    <path d="M4 50 A46 46 0 0 1 50 96" stroke="#00d8ff" strokeWidth="0.5" opacity="0.3" strokeDasharray="1 20 2 5" />
                </g>
                <g className="rotate-fast-reverse">
                    <path d="M50 10 A40 40 0 0 0 10 50" stroke="#00f2ff" strokeWidth="1" opacity="0.5" strokeDasharray="25 100" filter="url(#blueBloom)" />
                    <path d="M10 50 A40 40 0 0 0 50 90" stroke="#00f2ff" strokeWidth="1" opacity="0.5" strokeDasharray="25 100" filter="url(#blueBloom)" />
                    <path d="M50 90 A40 40 0 0 0 90 50" stroke="#00f2ff" strokeWidth="1" opacity="0.5" strokeDasharray="25 100" filter="url(#blueBloom)" />
                    <path d="M90 50 A40 40 0 0 0 50 10" stroke="#00f2ff" strokeWidth="1" opacity="0.5" strokeDasharray="25 100" filter="url(#blueBloom)" />
                </g>

                {/* 2. LAYER: Floating Data Fragments */}
                {[...Array(8)].map((_, i) => (
                    <rect key={i} x="49.5" y="4" width="1" height="0.5" fill="#00f2ff" opacity="0.6" transform={`rotate(${i * 45}, 50, 50)`} className="flicker">
                        <animateTransform attributeName="transform" type="translate" from="0 0" to="0 -2" dur={`${1 + i * 0.2}s`} repeatCount="indefinite" additive="sum" />
                    </rect>
                ))}

                {/* 4. LAYER: Vocal Waveform Spectrum (Clean Cyan) */}
                <g>
                    {[...Array(48)].map((_, i) => (
                        <rect
                            key={i}
                            x="49.9"
                            y="28"
                            width="0.2"
                            height={isSpeaking ? (2 + Math.random() * 10) : 1.5}
                            fill="#00f2ff"
                            opacity={isSpeaking ? 0.8 : 0.15}
                            transform={`rotate(${i * 7.5}, 50, 50)`}
                            style={{ transition: 'height 0.1s ease', filter: 'url(#blueBloom)' }}
                        />
                    ))}
                </g>

                {/* 5. LAYER: Central Mechanic Hub */}
                <circle cx="50" cy="50" r="32" stroke="rgba(0, 242, 255, 0.1)" strokeWidth="0.5" fill="none" />
                <circle cx="50" cy="50" r="26" stroke="#00f2ff" strokeWidth="0.8" fill="none" strokeDasharray="5 15" className="rotate-medium" />
                <circle cx="50" cy="50" r="22" stroke="#00ccff" strokeWidth="1.5" fill="none" strokeDasharray="1 10" className="rotate-fast" />

                {/* 6. LAYER: Multi-Level Intense Blue Power Core */}
                <g style={{ transform: `scale(${isSpeaking ? pulse : 1})`, transformOrigin: 'center', transition: 'transform 0.1s ease-out' }}>
                    <circle cx="50" cy="50" r="14" fill="rgba(0, 242, 255, 0.05)" stroke="#00f2ff" strokeWidth="0.2" opacity="0.4" />
                    <circle cx="50" cy="50" r="10" fill="url(#jarvisBlueCore)" filter="url(#extremeBlueBloom)" className="flicker" />
                    <circle cx="50" cy="50" r="16" stroke="#00f2ff" strokeWidth="0.4" opacity="0.6" className="pulse-ring" />
                    <circle cx="50" cy="50" r="3" fill="white" filter="url(#blueBloom)" />
                </g>
            </svg>

            {/* Jarvis HUD Label - Blue Edition */}
            <div style={{
                position: 'absolute', bottom: 15, left: '50%',
                transform: 'translateX(-50%)',
                background: 'transparent',
                backdropFilter: 'none',
                padding: '2px 22px', borderRadius: '15px',
                border: '1px solid rgba(0, 242, 255, 0.4)',
                color: '#00f2ff', fontSize: '8px', fontWeight: 900,
                letterSpacing: '5px', whiteSpace: 'nowrap',
                display: 'flex', alignItems: 'center', gap: '8px',
                pointerEvents: 'none',
                textShadow: '0 0 10px rgba(0, 242, 255, 0.8)'
            }}>
                <div style={{
                    width: 4, height: 4,
                    background: isSpeaking ? '#fff' : '#003344',
                    boxShadow: isSpeaking ? '0 0 15px #00f2ff' : 'none',
                    animation: isSpeaking ? 'flicker 0.1s infinite' : 'none',
                    transform: 'rotate(45deg)',
                    border: '1px solid #00f2ff'
                }} />
                INDU
            </div>

            <style>{`
                .rotate-fast { transform-origin: center; animation: rotate 3s linear infinite; }
                .rotate-fast-reverse { transform-origin: center; animation: rotate-reverse 4s linear infinite; }
                .rotate-medium { transform-origin: center; animation: rotate 15s linear infinite; }
                .rotate-slow { transform-origin: center; animation: rotate 35s linear infinite; }
                .rotate-slow-reverse { transform-origin: center; animation: rotate-reverse 45s linear infinite; }
                
                .scanner-line { animation: scan 6s ease-in-out infinite; transform-origin: center; }
                .flicker { animation: flicker 2.5s infinite; }
                .pulse-ring { animation: pulse-ring 3s infinite ease-out; transform-origin: center; }
                
                @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
                @keyframes rotate-reverse { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }
                @keyframes scan { 
                    0% { transform: translateY(-28px); opacity: 0; }
                    50% { opacity: 0.8; }
                    100% { transform: translateY(28px); opacity: 0; }
                }
                @keyframes flicker {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    40% { opacity: 0.7; transform: scale(0.98); }
                    42% { opacity: 1; transform: scale(1.02); }
                    45% { opacity: 0.5; transform: scale(0.95); }
                }
                @keyframes pulse-ring {
                    0% { transform: scale(0.85); opacity: 0.8; }
                    100% { transform: scale(1.8); opacity: 0; }
                }
            `}</style>
        </div>
    );
};

export default ReadyPlayerMeAvatar;
