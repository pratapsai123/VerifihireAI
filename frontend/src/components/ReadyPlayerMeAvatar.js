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
                setPulse(0.8 + Math.random() * 0.4);
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
                    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="2.5" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                    <radialGradient id="coreGradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
                        <stop offset="0%" stopColor="#00f2ff" />
                        <stop offset="100%" stopColor="#0ea5e9" />
                    </radialGradient>
                </defs>

                {/* Outer Glass Ring 3 */}
                <circle cx="50" cy="50" r="45"
                    stroke="rgba(0, 242, 255, 0.05)"
                    strokeWidth="0.5"
                    fill="transparent"
                />

                {/* Outer Glass Ring 2 */}
                <circle cx="50" cy="50" r="35"
                    stroke="rgba(0, 242, 255, 0.1)"
                    strokeWidth="1"
                    fill="transparent"
                    className="rotating-ring-1"
                />

                {/* Outer Glass Ring 1 */}
                <circle cx="50" cy="50" r="28"
                    stroke="rgba(0, 242, 255, 0.08)"
                    strokeWidth="1.5"
                    className="rotating-ring-2"
                />

                {/* Speech Pulse Waves */}
                {isSpeaking && (
                    <>
                        <circle cx="50" cy="50" r="20" stroke="#00f2ff" strokeWidth="0.5" opacity="0.6">
                            <animate attributeName="r" from="20" to="48" dur="1.5s" repeatCount="indefinite" />
                            <animate attributeName="opacity" from="0.6" to="0" dur="1.5s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="50" cy="50" r="20" stroke="#00f2ff" strokeWidth="0.5" opacity="0.4">
                            <animate attributeName="r" from="20" to="40" dur="1s" begin="0.5s" repeatCount="indefinite" />
                            <animate attributeName="opacity" from="0.4" to="0" dur="1s" begin="0.5s" repeatCount="indefinite" />
                        </circle>
                    </>
                )}

                {/* Central AI Core */}
                <g style={{ transform: `scale(${pulse})`, transformOrigin: 'center', transition: 'transform 0.1s ease-out' }}>
                    <circle cx="50" cy="50" r="14" fill="url(#coreGradient)" filter="url(#glow)" />
                    {/* Inner Core Detail */}
                    <circle cx="50" cy="50" r="6" fill="#0f172a" opacity="0.4" />
                    <circle cx="50" cy="50" r="3" fill="white" opacity="0.8" />
                </g>

                {/* Scanning Lines */}
                <line x1="10" y1="50" x2="90" y2="50" stroke="rgba(0, 242, 255, 0.15)" strokeWidth="0.2" className="scanner-line" />
            </svg>

            {/* Glassmorphism Title Tag */}
            <div style={{
                position: 'absolute', bottom: 20, left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(15, 23, 42, 0.7)',
                backdropFilter: 'blur(10px)',
                padding: '6px 22px', borderRadius: '100px',
                border: '1px solid rgba(0, 242, 255, 0.3)',
                color: '#e2e8f0', fontSize: '10px', fontWeight: 900,
                letterSpacing: '2px', whiteSpace: 'nowrap',
                display: 'flex', alignItems: 'center', gap: '8px',
                boxShadow: '0 8px 32px rgba(0,0,0,0.4)', pointerEvents: 'none'
            }}>
                <div style={{
                    width: 6, height: 6, borderRadius: '50%',
                    background: isSpeaking ? '#00f2ff' : '#475569',
                    boxShadow: isSpeaking ? '0 0 12px #00f2ff' : 'none',
                    animation: isSpeaking ? 'pulse-core 0.8s infinite alternate' : 'none'
                }} />
                INDU • AI RECRUITER
            </div>

            <style>{`
                .rotating-ring-1 {
                    transform-origin: center;
                    animation: rotate 20s linear infinite;
                    stroke-dasharray: 40 10;
                }
                .rotating-ring-2 {
                    transform-origin: center;
                    animation: rotate-reverse 15s linear infinite;
                    stroke-dasharray: 5 15;
                }
                .scanner-line {
                    animation: scan 4s ease-in-out infinite;
                }
                @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
                @keyframes rotate-reverse { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }
                @keyframes scan { 
                    0% { transform: translateY(-30px); opacity: 0; }
                    50% { opacity: 1; }
                    100% { transform: translateY(30px); opacity: 0; }
                }
                @keyframes pulse-core {
                    from { transform: scale(0.9); opacity: 0.6; }
                    to { transform: scale(1.1); opacity: 1; }
                }
            `}</style>
        </div>
    );
};

export default ReadyPlayerMeAvatar;
