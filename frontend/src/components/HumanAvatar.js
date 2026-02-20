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
    const breatheRef = useRef(0);          // subtle breathing animation

    const draw = useCallback((ctx, w, h) => {
        const cx = w / 2;
        const breathe = breatheRef.current * 2.5;
        ctx.clearRect(0, 0, w, h);

        // ── Configuration ──
        const skinBase = '#f3d2c1';
        const skinShadow = '#e0b0a0';
        const hairColor = '#0f172a';
        const suitColor = '#1e293b';

        const headW = 100;
        const headH = 140;
        const headTopY = h / 2 - 80 + breathe;
        const headCenterY = headTopY + headH / 2;

        // ── 1. Background ──
        const bg = ctx.createLinearGradient(0, 0, w, h);
        bg.addColorStop(0, '#ffffff');
        bg.addColorStop(1, '#f1f5f9');
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, w, h);

        // ── 2. Back Hair (Behind the head) ──
        ctx.fillStyle = hairColor;
        ctx.beginPath();
        ctx.ellipse(cx, headCenterY - 10, headW / 2 + 8, headH / 2 + 10, 0, 0, Math.PI * 2);
        ctx.fill();

        // ── 3. Shoulders & Suit ──
        const shoulderY = headCenterY + headH / 2 + 10;
        ctx.fillStyle = suitColor;
        ctx.beginPath();
        ctx.moveTo(cx - 130, h);
        ctx.bezierCurveTo(cx - 110, shoulderY + 20, cx - 70, shoulderY - 5, cx, shoulderY + 5);
        ctx.bezierCurveTo(cx + 70, shoulderY - 5, cx + 110, shoulderY + 20, cx + 130, h);
        ctx.closePath();
        ctx.fill();

        // Lapels
        ctx.fillStyle = '#334155';
        ctx.beginPath();
        ctx.moveTo(cx - 40, shoulderY + 10);
        ctx.lineTo(cx, shoulderY + 50);
        ctx.lineTo(cx + 40, shoulderY + 10);
        ctx.lineTo(cx, shoulderY + 20);
        ctx.closePath();
        ctx.fill();

        // Shirt
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(cx - 15, shoulderY + 10);
        ctx.lineTo(cx, shoulderY + 35);
        ctx.lineTo(cx + 15, shoulderY + 10);
        ctx.closePath();
        ctx.fill();

        // Tie
        ctx.fillStyle = '#4f46e5';
        ctx.beginPath();
        ctx.moveTo(cx - 5, shoulderY + 10);
        ctx.lineTo(cx, shoulderY + 25);
        ctx.lineTo(cx + 5, shoulderY + 10);
        ctx.lineTo(cx + 3, shoulderY + 45);
        ctx.lineTo(cx - 3, shoulderY + 45);
        ctx.closePath();
        ctx.fill();

        // ── 4. Neck ──
        ctx.fillStyle = skinShadow;
        ctx.beginPath();
        ctx.roundRect(cx - 22, headCenterY + headH / 2 - 20, 44, 45, 5);
        ctx.fill();

        // ── 5. Head Face (Skin) ──
        ctx.fillStyle = skinBase;
        ctx.beginPath();
        ctx.ellipse(cx, headCenterY, headW / 2, headH / 2, 0, 0, Math.PI * 2);
        ctx.fill();

        // Face Shadow/Shading
        const faceGrad = ctx.createRadialGradient(cx - 10, headCenterY - 30, 10, cx, headCenterY, headW / 2);
        faceGrad.addColorStop(0, 'rgba(255,255,255,0.25)');
        faceGrad.addColorStop(1, 'rgba(0,0,0,0.05)');
        ctx.fillStyle = faceGrad;
        ctx.fill();

        // ── 6. Front Hair (Sitting on the forehead) ──
        ctx.fillStyle = hairColor;
        // Top cap (overlaps the top edge of head)
        ctx.beginPath();
        ctx.ellipse(cx, headTopY + 20, headW / 2 + 6, 40, 0, Math.PI, Math.PI * 2);
        ctx.fill();
        // Fringe
        ctx.beginPath();
        ctx.moveTo(cx - headW / 2, headTopY + 20);
        ctx.quadraticCurveTo(cx, headTopY + 35, cx + headW / 2, headTopY + 20);
        ctx.quadraticCurveTo(cx, headTopY + 5, cx - headW / 2, headTopY + 20);
        ctx.fill();

        // ── 7. Facial Features ──
        const eyeY = headCenterY - 15;

        // Brows
        ctx.strokeStyle = '#2c1810';
        ctx.lineWidth = 3.5;
        ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(cx - 38, eyeY - 20); ctx.quadraticCurveTo(cx - 24, eyeY - 26, cx - 10, eyeY - 20); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(cx + 10, eyeY - 20); ctx.quadraticCurveTo(cx + 24, eyeY - 26, cx + 38, eyeY - 20); ctx.stroke();

        // Eyes
        const blink = blinkRef.current;
        const eyeH = 12 * (1 - blink);
        [-1, 1].forEach(side => {
            const ex = cx + side * 24;
            ctx.fillStyle = 'white';
            ctx.beginPath(); ctx.ellipse(ex, eyeY, 14, eyeH, 0, 0, Math.PI * 2); ctx.fill();
            if (eyeH > 2) {
                // Iris
                ctx.fillStyle = '#1e40af';
                ctx.beginPath(); ctx.arc(ex, eyeY, 7.5, 0, Math.PI * 2); ctx.fill();
                // Pupil
                ctx.fillStyle = '#000000';
                ctx.beginPath(); ctx.arc(ex, eyeY, 3.5, 0, Math.PI * 2); ctx.fill();
                // Sparkle
                ctx.fillStyle = 'white';
                ctx.beginPath(); ctx.arc(ex + 2, eyeY - 2, 2, 0, Math.PI * 2); ctx.fill();
            }
            // Lid line
            ctx.strokeStyle = 'rgba(0,0,0,0.5)';
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.ellipse(ex, eyeY, 14, eyeH, 0, Math.PI, Math.PI * 2); ctx.stroke();
        });

        // Nose
        const noseY = headCenterY + 15;
        ctx.strokeStyle = 'rgba(0,0,0,0.15)';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(cx, noseY);
        ctx.quadraticCurveTo(cx + 6, noseY + 18, cx, noseY + 22);
        ctx.stroke();

        // Mouth
        const mouthY = headCenterY + 50;
        const mouthOpen = mouthOpenRef.current;
        const mouthOpenPx = mouthOpen * 16;
        const lipW = 28;

        if (mouthOpen > 0.05) {
            ctx.fillStyle = '#4c0519';
            ctx.beginPath();
            ctx.roundRect(cx - lipW + 2, mouthY, (lipW - 2) * 2, mouthOpenPx, 4);
            ctx.fill();
        }

        // Lips
        ctx.fillStyle = '#d67161';
        ctx.beginPath();
        ctx.moveTo(cx - lipW, mouthY);
        ctx.bezierCurveTo(cx - lipW / 2, mouthY - 4, cx, mouthY - 4, cx, mouthY);
        ctx.bezierCurveTo(cx, mouthY - 4, cx + lipW / 2, mouthY - 4, cx + lipW, mouthY);
        ctx.quadraticCurveTo(cx, mouthY + 2, cx - lipW, mouthY);
        ctx.fill();

        ctx.fillStyle = '#ab3d33';
        ctx.beginPath();
        ctx.moveTo(cx - lipW, mouthY + mouthOpenPx);
        ctx.quadraticCurveTo(cx, mouthY + mouthOpenPx + 8, cx + lipW, mouthY + mouthOpenPx);
        ctx.quadraticCurveTo(cx, mouthY + mouthOpenPx + 2, cx - lipW, mouthY + mouthOpenPx);
        ctx.fill();

        // ── 8. Ring & Badge ──
        if (isSpeaking) {
            const pulse = 0.5 + 0.5 * Math.sin(timeRef.current * 0.1);
            ctx.strokeStyle = `rgba(79, 70, 229, ${0.4 + pulse * 0.4})`;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.ellipse(cx, headCenterY, headW / 2 + 15 + pulse * 5, headH / 2 + 10 + pulse * 3, 0, 0, Math.PI * 2);
            ctx.stroke();
        }

        const bW = 140; const bH = 30; const bY = h - 45;
        ctx.fillStyle = '#4f46e5';
        ctx.beginPath(); ctx.roundRect(cx - bW / 2, bY, bW, bH, 10); ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 12px Inter, sans-serif';
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText('AI INTERVIEWER', cx, bY + bH / 2);
    }, [isSpeaking]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        let frame = 0;
        const loop = () => {
            frame++;
            timeRef.current = frame;

            // ── Breathing ──
            breatheRef.current = Math.sin(frame * 0.05);

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
