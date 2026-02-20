import React, { useEffect, useRef, useCallback } from 'react';

// Polyfill for CanvasRenderingContext2D.roundRect (not in all browsers)
if (typeof CanvasRenderingContext2D !== 'undefined' && !CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r = 0) {
        const rad = Math.min(r, Math.min(w, h) / 2);
        this.beginPath();
        this.moveTo(x + rad, y);
        this.lineTo(x + w - rad, y);
        this.quadraticCurveTo(x + w, y, x + w, y + rad);
        this.lineTo(x + w, y + h - rad);
        this.quadraticCurveTo(x + w, y + h, x + w - rad, y + h);
        this.lineTo(x + rad, y + h);
        this.quadraticCurveTo(x, y + h, x, y + h - rad);
        this.lineTo(x, y + rad);
        this.quadraticCurveTo(x, y, x + rad, y);
        this.closePath();
    };
}

/**
 * HumanAvatar — a Canvas-rendered professional human face
 * that animates its mouth (lip-sync) while isSpeaking === true.
 */
const HumanAvatar = ({ isSpeaking = false, width = 280, height = 320 }) => {
    const canvasRef = useRef(null);
    const animFrameRef = useRef(null);
    const mouthOpenRef = useRef(0);        // 0 = closed, 1 = fully open
    const targetMouthRef = useRef(0);
    const timeRef = useRef(0);
    const blinkRef = useRef(0);            // 0=open eye, 1=closed
    const blinkTimerRef = useRef(0);
    const blinkStateRef = useRef(0);       // 0=open, 1=closing, 2=closed, 3=opening

    const draw = useCallback((ctx, w, h) => {
        const cx = w / 2;
        ctx.clearRect(0, 0, w, h);

        // ── Background gradient ──
        const bg = ctx.createLinearGradient(0, 0, 0, h);
        bg.addColorStop(0, '#e8f0fe');
        bg.addColorStop(1, '#c7d7fc');
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, w, h);

        // ── Shoulders ──
        ctx.fillStyle = '#1a3a6b';
        ctx.beginPath();
        ctx.moveTo(cx - 90, h);
        ctx.bezierCurveTo(cx - 90, h - 60, cx - 50, h - 80, cx, h - 85);
        ctx.bezierCurveTo(cx + 50, h - 80, cx + 90, h - 60, cx + 90, h);
        ctx.closePath();
        ctx.fill();

        // Shirt collar white
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(cx - 18, h - 82);
        ctx.lineTo(cx, h - 60);
        ctx.lineTo(cx + 18, h - 82);
        ctx.closePath();
        ctx.fill();

        // Tie
        ctx.fillStyle = '#1a5276';
        ctx.beginPath();
        ctx.moveTo(cx - 8, h - 82);
        ctx.lineTo(cx, h - 60);
        ctx.lineTo(cx + 8, h - 82);
        ctx.lineTo(cx + 5, h - 88);
        ctx.lineTo(cx - 5, h - 88);
        ctx.closePath();
        ctx.fill();

        // ── Neck ──
        const skinLight = '#f0c27f';
        const skinMid = '#e8a96e';
        const skinDark = '#c68642';

        ctx.fillStyle = skinMid;
        ctx.beginPath();
        ctx.roundRect(cx - 18, h - 130, 36, 50, 8);
        ctx.fill();

        // ── Head ──
        const headY = h - 270;
        const headH = 155;
        const headW = 110;
        ctx.fillStyle = skinLight;
        ctx.beginPath();
        ctx.ellipse(cx, headY + headH / 2, headW / 2, headH / 2, 0, 0, Math.PI * 2);
        ctx.fill();

        // Head shadow / depth
        const headGrad = ctx.createRadialGradient(cx - 15, headY + 40, 10, cx, headY + headH / 2, headW / 2);
        headGrad.addColorStop(0, 'rgba(255,255,255,0.18)');
        headGrad.addColorStop(1, 'rgba(180,100,40,0.12)');
        ctx.fillStyle = headGrad;
        ctx.beginPath();
        ctx.ellipse(cx, headY + headH / 2, headW / 2, headH / 2, 0, 0, Math.PI * 2);
        ctx.fill();

        // ── Hair ──
        ctx.fillStyle = '#2c1810';
        ctx.beginPath();
        ctx.ellipse(cx, headY + 5, headW / 2, 38, 0, Math.PI, Math.PI * 2);
        ctx.fill();
        // Side hair left
        ctx.beginPath();
        ctx.ellipse(cx - headW / 2 + 10, headY + 55, 14, 30, -0.3, 0, Math.PI * 2);
        ctx.fill();
        // Side hair right
        ctx.beginPath();
        ctx.ellipse(cx + headW / 2 - 10, headY + 55, 14, 30, 0.3, 0, Math.PI * 2);
        ctx.fill();

        // ── Ears ──
        ctx.fillStyle = skinMid;
        ctx.beginPath();
        ctx.ellipse(cx - headW / 2 + 2, headY + 80, 10, 15, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(cx + headW / 2 - 2, headY + 80, 10, 15, 0, 0, Math.PI * 2);
        ctx.fill();

        // ── Eyebrows ──
        const eyeY = headY + 65;
        ctx.strokeStyle = '#3d1f0a';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        // Left brow
        ctx.beginPath();
        ctx.moveTo(cx - 38, eyeY - 20);
        ctx.quadraticCurveTo(cx - 22, eyeY - 26, cx - 8, eyeY - 20);
        ctx.stroke();
        // Right brow
        ctx.beginPath();
        ctx.moveTo(cx + 8, eyeY - 20);
        ctx.quadraticCurveTo(cx + 22, eyeY - 26, cx + 38, eyeY - 20);
        ctx.stroke();

        // ── Eyes ──
        const blink = blinkRef.current;
        const eyeOpenH = 11;
        const eyeH = eyeOpenH * (1 - blink);

        // Eye whites
        [-1, 1].forEach(side => {
            const ex = cx + side * 23;
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.ellipse(ex, eyeY, 14, eyeH, 0, 0, Math.PI * 2);
            ctx.fill();
            // Iris
            if (eyeH > 3) {
                ctx.fillStyle = '#3d5a80';
                ctx.beginPath();
                ctx.ellipse(ex, eyeY, 8, Math.min(8, eyeH), 0, 0, Math.PI * 2);
                ctx.fill();
                // Pupil
                ctx.fillStyle = '#111';
                ctx.beginPath();
                ctx.ellipse(ex, eyeY, 4, Math.min(4, eyeH - 2), 0, 0, Math.PI * 2);
                ctx.fill();
                // Highlight
                ctx.fillStyle = 'rgba(255,255,255,0.7)';
                ctx.beginPath();
                ctx.ellipse(ex + 2, eyeY - 2, 2, 2, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            // Eyelid (upper)
            ctx.strokeStyle = skinDark;
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.ellipse(ex, eyeY, 14, eyeH, 0, Math.PI, Math.PI * 2);
            ctx.stroke();
        });

        // ── Nose ──
        const noseY = headY + 95;
        ctx.strokeStyle = skinDark;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(cx, noseY);
        ctx.quadraticCurveTo(cx + 8, noseY + 22, cx, noseY + 26);
        ctx.stroke();
        // Nostrils
        ctx.fillStyle = 'rgba(140,80,30,0.3)';
        ctx.beginPath();
        ctx.ellipse(cx - 9, noseY + 26, 6, 4, -0.4, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(cx + 9, noseY + 26, 6, 4, 0.4, 0, Math.PI * 2);
        ctx.fill();

        // ── Mouth / Lip-sync ──
        const mouthY = headY + 120;
        const mouthOpen = mouthOpenRef.current;       // 0..1
        const mouthOpenPx = mouthOpen * 16;           // max gap = 16px

        const lipW = 26;

        // Lower lip / chin background first
        ctx.fillStyle = skinMid;
        ctx.fillRect(cx - lipW - 4, mouthY, (lipW + 4) * 2, mouthOpenPx + 8);

        // Teeth (only when open)
        if (mouthOpen > 0.1) {
            ctx.fillStyle = '#f8f8f8';
            ctx.beginPath();
            ctx.roundRect(cx - lipW + 2, mouthY + 2, (lipW - 2) * 2, mouthOpenPx * 0.55, 3);
            ctx.fill();
            // Lower teeth
            ctx.fillStyle = '#eeeeee';
            ctx.beginPath();
            ctx.roundRect(cx - lipW + 4, mouthY + mouthOpenPx * 0.55 - 2, (lipW - 4) * 2, mouthOpenPx * 0.4, 3);
            ctx.fill();
            // Inside mouth (dark)
            ctx.fillStyle = 'rgba(80,20,10,0.6)';
            ctx.beginPath();
            ctx.roundRect(cx - lipW + 2, mouthY + 2, (lipW - 2) * 2, mouthOpenPx - 2, 3);
            ctx.fill();
        }

        // Upper lip
        ctx.fillStyle = '#c0705a';
        ctx.beginPath();
        ctx.moveTo(cx - lipW, mouthY + 2);
        ctx.bezierCurveTo(cx - lipW / 2, mouthY - 6, cx, mouthY - 4, cx, mouthY);
        ctx.bezierCurveTo(cx, mouthY - 4, cx + lipW / 2, mouthY - 6, cx + lipW, mouthY + 2);
        ctx.quadraticCurveTo(cx, mouthY + 3, cx - lipW, mouthY + 2);
        ctx.fill();

        // Lower lip
        ctx.fillStyle = '#b86050';
        ctx.beginPath();
        ctx.moveTo(cx - lipW, mouthY + mouthOpenPx);
        ctx.quadraticCurveTo(cx, mouthY + mouthOpenPx + 10, cx + lipW, mouthY + mouthOpenPx);
        ctx.quadraticCurveTo(cx, mouthY + mouthOpenPx + 4, cx - lipW, mouthY + mouthOpenPx);
        ctx.fill();

        // Lip line crease
        ctx.strokeStyle = 'rgba(120,40,30,0.5)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(cx - lipW, mouthY + 2);
        ctx.quadraticCurveTo(cx, mouthY + mouthOpenPx / 2 + 2 + mouthOpen * 2, cx + lipW, mouthY + 2);
        ctx.stroke();

        // Subtle cheek
        ctx.fillStyle = 'rgba(230,140,100,0.12)';
        ctx.beginPath();
        ctx.ellipse(cx - 35, headY + 100, 18, 12, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(cx + 35, headY + 100, 18, 12, 0, 0, Math.PI * 2);
        ctx.fill();

        // ── Speaking indicator ring ──
        if (isSpeaking) {
            const pulse = 0.5 + 0.5 * Math.sin(timeRef.current * 0.08);
            ctx.strokeStyle = `rgba(102,126,234,${0.5 + pulse * 0.4})`;
            ctx.lineWidth = 3 + pulse * 2;
            ctx.beginPath();
            ctx.ellipse(cx, headY + headH / 2, headW / 2 + 10 + pulse * 5, headH / 2 + 6 + pulse * 3, 0, 0, Math.PI * 2);
            ctx.stroke();
        }

        // Name badge at bottom
        ctx.fillStyle = 'rgba(26,58,107,0.85)';
        ctx.beginPath();
        ctx.roundRect(cx - 60, h - 30, 120, 22, 8);
        ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 11px Poppins, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('AI Interviewer', cx, h - 14);
    }, [isSpeaking]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        let frame = 0;
        const loop = () => {
            frame++;
            timeRef.current = frame;

            // ── Lip animation ──
            if (isSpeaking) {
                // Randomly pick new mouth target every ~12 frames (≈5× per sec at 60fps)
                if (frame % 10 === 0) {
                    // Vary between wide open, half, and nearly closed
                    const shapes = [0, 0.1, 0.25, 0.5, 0.75, 1, 0.6, 0.3, 0];
                    targetMouthRef.current = shapes[Math.floor(Math.random() * shapes.length)];
                }
            } else {
                targetMouthRef.current = 0;
            }
            // Smooth interpolation toward target
            mouthOpenRef.current += (targetMouthRef.current - mouthOpenRef.current) * 0.35;

            // ── Blink logic ──
            blinkTimerRef.current++;
            if (blinkStateRef.current === 0 && blinkTimerRef.current > 120 + Math.random() * 80) {
                blinkStateRef.current = 1; blinkTimerRef.current = 0;
            }
            if (blinkStateRef.current === 1) {
                blinkRef.current = Math.min(1, blinkRef.current + 0.25);
                if (blinkRef.current >= 1) blinkStateRef.current = 2;
            }
            if (blinkStateRef.current === 2) {
                blinkRef.current = Math.max(0, blinkRef.current - 0.25);
                if (blinkRef.current <= 0) { blinkStateRef.current = 0; blinkTimerRef.current = 0; }
            }

            draw(ctx, canvas.width, canvas.height);
            animFrameRef.current = requestAnimationFrame(loop);
        };

        animFrameRef.current = requestAnimationFrame(loop);
        return () => cancelAnimationFrame(animFrameRef.current);
    }, [isSpeaking, draw]);

    return (
        <canvas
            ref={canvasRef}
            width={width}
            height={height}
            style={{ borderRadius: 20, display: 'block', boxShadow: '0 8px 32px rgba(0,0,0,0.15)' }}
        />
    );
};

export default HumanAvatar;
