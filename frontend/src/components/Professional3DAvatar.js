import React, { useEffect, useState, useRef } from 'react';

/**
 * Professional3DAvatar
 * A premium SVG AI interviewer with subtle, natural mouth animation.
 */
const Professional3DAvatar = ({ isSpeaking = false }) => {
    const [mouthOpen, setMouthOpen] = useState(0);
    const [blink, setBlink] = useState(false);
    const frameRef = useRef(0);

    useEffect(() => {
        let animationFrame;
        const animate = () => {
            frameRef.current += 1;

            // Lip Sync — smooth mouth open/close
            if (isSpeaking) {
                if (frameRef.current % 8 === 0) {
                    setMouthOpen(2 + Math.random() * 6); // 2–8px open range
                }
            } else {
                setMouthOpen(0);
            }

            // Blinking
            if (frameRef.current % 200 === 0) {
                setBlink(true);
                setTimeout(() => setBlink(false), 130);
            }

            animationFrame = requestAnimationFrame(animate);
        };
        animationFrame = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(animationFrame);
    }, [isSpeaking]);

    // Lip curve positions
    const lipY = 152;
    const lipGap = mouthOpen;

    return (
        <div style={{ position: 'relative', width: 260, height: 300, background: 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>

            {/* Ambient glow */}
            <div style={{
                position: 'absolute', width: '140%', height: '140%',
                background: 'radial-gradient(circle at center, rgba(99,102,241,0.12) 0%, transparent 70%)',
                animation: 'none', pointerEvents: 'none'
            }} />

            {/* Speaking pulse ring */}
            {isSpeaking && (
                <div style={{
                    position: 'absolute', inset: 10,
                    border: '2px solid rgba(99,102,241,0.6)',
                    borderRadius: '50%',
                    animation: 'pulse-ring 1.5s infinite',
                }} />
            )}

            <style>{`
                @keyframes pulse-ring {
                    0%   { transform: scale(0.92); opacity: 0.7; }
                    100% { transform: scale(1.15); opacity: 0; }
                }
            `}</style>

            <svg width="200" height="240" viewBox="0 0 200 240" fill="none" xmlns="http://www.w3.org/2000/svg"
                style={{ position: 'relative', zIndex: 2, filter: 'drop-shadow(0 8px 18px rgba(0,0,0,0.35))' }}>

                {/* Shoulders / jacket */}
                <path d="M15 240C15 195 58 175 100 175C142 175 185 195 185 240" fill="#1e1b4b" />
                {/* Shirt collar */}
                <path d="M86 178L100 200L114 178" fill="#f8fafc" />
                {/* Tie */}
                <path d="M97 178L100 200L103 178L101 174L99 174Z" fill="#4338ca" />

                {/* Neck */}
                <rect x="86" y="158" width="28" height="26" rx="7" fill="#e2b49a" />

                {/* Face */}
                <defs>
                    <radialGradient id="faceG" cx="45%" cy="40%" r="60%">
                        <stop offset="0%" stopColor="#f5cdb0" />
                        <stop offset="100%" stopColor="#d89a72" />
                    </radialGradient>
                </defs>
                <ellipse cx="100" cy="108" rx="56" ry="68" fill="url(#faceG)" />

                {/* Hair */}
                <path d="M44 98C44 57 70 38 100 38C130 38 156 57 156 98C156 108 151 128 141 138C146 108 141 76 100 76C59 76 54 108 59 138C49 128 44 108 44 98Z" fill="#2c1a10" />

                {/* Ears */}
                <ellipse cx="44" cy="112" rx="7" ry="11" fill="#d4956d" />
                <ellipse cx="156" cy="112" rx="7" ry="11" fill="#d4956d" />

                {/* Eyes */}
                <ellipse cx="75" cy="104" rx="13" ry={blink ? 1 : 9} fill="white" />
                <circle cx="75" cy="104" r={blink ? 0 : 5.5} fill="#1e293b" />
                <circle cx="77" cy="102" r={blink ? 0 : 1.8} fill="white" opacity="0.85" />

                <ellipse cx="125" cy="104" rx="13" ry={blink ? 1 : 9} fill="white" />
                <circle cx="125" cy="104" r={blink ? 0 : 5.5} fill="#1e293b" />
                <circle cx="127" cy="102" r={blink ? 0 : 1.8} fill="white" opacity="0.85" />

                {/* Eyebrows */}
                <path d="M62 89C67 84 86 84 91 89" stroke="#2c1a10" strokeWidth="2.2" strokeLinecap="round" fill="none" />
                <path d="M109 89C114 84 133 84 138 89" stroke="#2c1a10" strokeWidth="2.2" strokeLinecap="round" fill="none" />

                {/* Nose */}
                <path d="M97 126C100 121 103 121 103 133" stroke="#c08060" strokeWidth="1.4" strokeLinecap="round" fill="none" />
                <ellipse cx="95" cy="133" rx="4" ry="2.5" fill="#b87050" opacity="0.3" />
                <ellipse cx="105" cy="133" rx="4" ry="2.5" fill="#b87050" opacity="0.3" />

                {/* ── Mouth ── */}
                {/* Dark inner mouth — only visible when speaking */}
                {isSpeaking && lipGap > 1 && (
                    <ellipse cx="100" cy={lipY + lipGap / 2} rx="13" ry={lipGap / 2 + 1} fill="#3a1208" opacity="0.85" />
                )}

                {!isSpeaking && (
                    <>
                        {/* Upper lip — thin natural cupid's bow */}
                        <path
                            d={`M87 ${lipY} C91 ${lipY - 3} 95 ${lipY - 4} 100 ${lipY - 2} C105 ${lipY - 4} 109 ${lipY - 3} 113 ${lipY} C107 ${lipY - 1} 93 ${lipY - 1} 87 ${lipY}Z`}
                            fill="#c4836a"
                            opacity="0.95"
                        />

                        {/* Lower lip — natural pout */}
                        <path
                            d={`M87 ${lipY + 1} C91 ${lipY + 4} 109 ${lipY + 4} 113 ${lipY + 1} C107 ${lipY + 2} 93 ${lipY + 2} 87 ${lipY + 1}Z`}
                            fill="#b87560"
                            opacity="0.95"
                        />
                    </>
                )}



                {/* Cheek blush */}
                <circle cx="68" cy="135" r="9" fill="#f87171" opacity="0.09" />
                <circle cx="132" cy="135" r="9" fill="#f87171" opacity="0.09" />
            </svg>

            {/* Name badge */}
            <div style={{
                position: 'absolute', bottom: 12, left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(99,102,241,0.12)',
                backdropFilter: 'blur(8px)',
                padding: '3px 14px',
                borderRadius: '100px',
                border: '1px solid rgba(99,102,241,0.25)',
                color: '#94a3b8',
                fontSize: '10px', fontWeight: 700,
                letterSpacing: '0.8px',
                whiteSpace: 'nowrap',
                zIndex: 10
            }}>
                AI INTERVIEWER
            </div>
        </div>
    );
};

export default Professional3DAvatar;
