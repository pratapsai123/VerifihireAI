import React, { useEffect, useState } from 'react';

/**
 * Professional2DBot - Ultra Premium Digital Edition
 * 
 * Replaces the 3D model with a high-end, animated 2D AI Core.
 * Features:
 * 1. Glassmorphism: Layered SVG rings with blur and transparency.
 * 2. Speech Reactivity: Dynamic pulse soundwaves and core intensity updates.
 * 3. Minimalist Aesthetic: Charcoal, slate, and glowing cyan color palette.
 */

const ReadyPlayerMeAvatar = ({ isSpeaking = false }) => {
    const [pulse, setPulse] = useState(1);

    useEffect(() => {
        if (isSpeaking) {
            const interval = setInterval(() => {
                setPulse(0.9 + Math.random() * 0.3);
            }, 80);
            return () => clearInterval(interval);
        } else {
            setPulse(1);
        }
    }, [isSpeaking]);

    return (
        <div style={{
            width: '100%',
            height: '320px',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            borderRadius: '12px',
            background: 'transparent'
        }}>
            <svg width="220" height="220" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="3.5" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                    <radialGradient id="neonCoreGradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                        <stop offset="0%" stopColor="#ff00ff" />
                        <stop offset="100%" stopColor="#9d00ff" />
                    </radialGradient>
                </defs>

                {/* Outer Neon Ring 3 */}
                <circle cx="50" cy="50" r="45"
                    stroke="rgba(255, 0, 255, 0.15)"
                    strokeWidth="0.5"
                    fill="transparent"
                />

                {/* Outer Rotating Neon Ring 2 */}
                <circle cx="50" cy="50" r="35"
                    stroke="rgba(0, 255, 239, 0.4)"
                    strokeWidth="1.2"
                    fill="transparent"
                    className="rotating-ring-1"
                    filter="url(#neonGlow)"
                />

                {/* Outer Rotating Neon Ring 1 */}
                <circle cx="50" cy="50" r="28"
                    stroke="rgba(255, 0, 255, 0.5)"
                    strokeWidth="1.8"
                    className="rotating-ring-2"
                    filter="url(#neonGlow)"
                />

                {/* Speech Pulse Waves - Neon Green/Cyan */}
                {isSpeaking && (
                    <>
                        <circle cx="50" cy="50" r="20" stroke="#00f2ff" strokeWidth="0.8" opacity="0.8">
                            <animate attributeName="r" from="20" to="48" dur="1s" repeatCount="indefinite" />
                            <animate attributeName="opacity" from="0.8" to="0" dur="1s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="50" cy="50" r="20" stroke="#ff00ff" strokeWidth="0.8" opacity="0.6">
                            <animate attributeName="r" from="20" to="42" dur="0.8s" begin="0.4s" repeatCount="indefinite" />
                            <animate attributeName="opacity" from="0.6" to="0" dur="0.8s" begin="0.4s" repeatCount="indefinite" />
                        </circle>
                    </>
                )}

                {/* Central Neon Core */}
                <g style={{ transform: `scale(${isSpeaking ? pulse : 1})`, transformOrigin: 'center', transition: 'transform 0.1s ease-out' }}>
                    <circle cx="50" cy="50" r="14" fill="url(#neonCoreGradient)" filter="url(#neonGlow)" />
                    {/* Inner Core Pulse */}
                    <circle cx="50" cy="50" r="5" fill="white" opacity="0.9" filter="url(#neonGlow)" />
                </g>

                {/* Scanning Laser Line */}
                <line x1="10" y1="50" x2="90" y2="50" stroke="#ff00ff" strokeWidth="0.4" className="scanner-line" filter="url(#neonGlow)" />
            </svg>

            {/* Neon Title Tag */}
            <div style={{
                position: 'absolute', bottom: 20, left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(20, 0, 30, 0.8)',
                backdropFilter: 'blur(12px)',
                padding: '6px 22px', borderRadius: '100px',
                border: '1px solid #ff00ff',
                color: '#ff00ff', fontSize: '10px', fontWeight: 900,
                letterSpacing: '2.5px', whiteSpace: 'nowrap',
                display: 'flex', alignItems: 'center', gap: '8px',
                boxShadow: '0 0 15px rgba(255, 0, 255, 0.5)', pointerEvents: 'none',
                textShadow: '0 0 8px #ff00ff'
            }}>
                <div style={{
                    width: 6, height: 6, borderRadius: '50%',
                    background: isSpeaking ? '#00f2ff' : '#475569',
                    boxShadow: isSpeaking ? '0 0 12px #00f2ff' : 'none',
                    animation: isSpeaking ? 'pulse-core 0.5s infinite alternate' : 'none'
                }} />
                INDU • NEON AI
            </div>

            <style>{`
                .rotating-ring-1 {
                    transform-origin: center;
                    animation: rotate 15s linear infinite;
                    stroke-dasharray: 30 20;
                }
                .rotating-ring-2 {
                    transform-origin: center;
                    animation: rotate-reverse 10s linear infinite;
                    stroke-dasharray: 10 15;
                }
                .scanner-line {
                    animation: scan 3s ease-in-out infinite;
                }
                @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
                @keyframes rotate-reverse { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }
                @keyframes scan { 
                    0% { transform: translateY(-35px); opacity: 0; }
                    50% { opacity: 1; }
                    100% { transform: translateY(35px); opacity: 0; }
                }
                @keyframes pulse-core {
                    from { transform: scale(0.85); opacity: 0.7; }
                    to { transform: scale(1.15); opacity: 1; }
                }
            `}</style>
        </div>
    );
};

export default ReadyPlayerMeAvatar;
