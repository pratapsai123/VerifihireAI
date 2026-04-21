/**
 * DeepFace Proctoring — Test Dashboard JavaScript
 *
 * Handles:
 *  - Webcam capture for registration
 *  - Face registration API calls
 *  - Session start/stop via REST
 *  - WebSocket real-time monitoring
 *  - Live analytics visualization
 */

const API_BASE = '/api/v1';
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const WS_BASE = `${WS_PROTOCOL}${window.location.host}${API_BASE}`;

// ══════════════════════════════════════
// STATE
// ══════════════════════════════════════
const state = {
    regStream: null,
    regCaptured: false,
    regImageB64: null,

    sessionId: null,
    sessionActive: false,
    monitorStream: null,
    ws: null,
    frameCount: 0,
    startTime: null,
    timerInterval: null,
    fpsCounter: { frames: 0, lastTime: performance.now(), fps: 0 },
    alertCount: 0,
    sendInterval: null,
    awaitingFrameResult: false,
};

// ══════════════════════════════════════
// DOM ELEMENTS
// ══════════════════════════════════════
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// Server status
const serverDot = $('#serverDot');
const serverStatusText = $('#serverStatus');

// Registration
const regVideo = $('#regVideo');
const regCanvas = $('#regCanvas');
const regSnapshot = $('#regSnapshot');
const regOverlay = $('#regOverlay');
const btnStartRegCam = $('#btnStartRegCam');
const btnCaptureReg = $('#btnCaptureReg');
const btnRetakeReg = $('#btnRetakeReg');
const btnRegister = $('#btnRegister');
const personIdInput = $('#personIdInput');
const labelInput = $('#labelInput');
const regResult = $('#regResult');
const regResultIcon = $('#regResultIcon');
const regResultTitle = $('#regResultTitle');
const regResultMessage = $('#regResultMessage');
const regResultMeta = $('#regResultMeta');

// Monitoring
const sessionPersonId = $('#sessionPersonId');
const btnStartSession = $('#btnStartSession');
const btnStopSession = $('#btnStopSession');
const btnDownloadReport = $('#btnDownloadReport');
const monitorVideo = $('#monitorVideo');
const monitorCanvas = $('#monitorCanvas');
const monitorCtx = monitorCanvas.getContext('2d');
const videoHud = $('#videoHud');
const videoPlaceholder = $('#videoPlaceholder');
const hudSessionId = $('#hudSessionId');
const hudFrameCount = $('#hudFrameCount');
const hudFps = $('#hudFps');
const hudTimer = $('#hudTimer');

// Analytics
const engagementArc = $('#engagementArc');
const engagementValue = $('#engagementValue');
const violationBarFill = $('#violationBarFill');
const violationValue = $('#violationValue');
const facePresent = $('#facePresent');
const faceCount = $('#faceCount');
const faceVerified = $('#faceVerified');
const faceLiveness = $('#faceLiveness');
const yawIndicator = $('#yawIndicator');
const pitchIndicator = $('#pitchIndicator');
const yawValue = $('#yawValue');
const pitchValue = $('#pitchValue');

const alertCount = $('#alertCount');
const alertList = $('#alertList');

// ══════════════════════════════════════
// INITIALIZATION
// ══════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    checkServerHealth();
    initRegistration();
    initMonitoring();
});

// ── Server Health Check ──
async function checkServerHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        if (data.status === 'healthy') {
            serverDot.className = 'status-dot online';
            serverStatusText.textContent = 'Server Online';
        }
    } catch (e) {
        serverDot.className = 'status-dot offline';
        serverStatusText.textContent = 'Server Offline';
    }
}

// ══════════════════════════════════════
// REGISTRATION
// ══════════════════════════════════════
function initRegistration() {
    btnStartRegCam.addEventListener('click', startRegCamera);
    btnCaptureReg.addEventListener('click', captureRegPhoto);
    btnRetakeReg.addEventListener('click', retakeRegPhoto);
    btnRegister.addEventListener('click', registerFace);
    personIdInput.addEventListener('input', updateRegisterBtn);
}

async function startRegCamera() {
    try {
        state.regStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480, facingMode: 'user' }
        });
        regVideo.srcObject = state.regStream;
        regVideo.style.display = 'block';
        regSnapshot.style.display = 'none';
        regOverlay.style.display = 'flex';
        btnCaptureReg.disabled = true;  // Disabled until face is inside oval
        btnStartRegCam.textContent = 'Camera Active';
        btnStartRegCam.disabled = true;

        // Start live face-in-oval detection
        _startFaceGuideCheck();
    } catch (e) {
        alert('Could not access camera: ' + e.message);
    }
}

// ── Live Face-in-Oval Detection ──
function _startFaceGuideCheck() {
    const ovalEl = document.querySelector('.face-guide ellipse');
    const guideText = document.getElementById('regGuideText');

    // Check if browser supports FaceDetector (Chrome 70+)
    if (!('FaceDetector' in window)) {
        // Fallback: just enable the button and skip live detection
        btnCaptureReg.disabled = false;
        if (guideText) guideText.textContent = 'Position your face within the oval';
        return;
    }

    const detector = new FaceDetector({ fastMode: true, maxDetectedFaces: 3 });

    state._faceGuideInterval = setInterval(async () => {
        if (!regVideo.videoWidth || regVideo.style.display === 'none') return;

        try {
            const faces = await detector.detect(regVideo);

            // Oval zone in video pixel coordinates
            const vw = regVideo.videoWidth;
            const vh = regVideo.videoHeight;
            const ovalCx = vw * 0.50;
            const ovalCy = vh * 0.46;
            const ovalRx = vw * 0.35;
            const ovalRy = vh * 0.36;

            let faceInOval = false;

            for (const face of faces) {
                // Face center
                const fcx = face.boundingBox.x + face.boundingBox.width / 2;
                const fcy = face.boundingBox.y + face.boundingBox.height / 2;

                // Check if face center is inside the ellipse
                const dx = (fcx - ovalCx) / ovalRx;
                const dy = (fcy - ovalCy) / ovalRy;
                if (dx * dx + dy * dy <= 1.0) {
                    faceInOval = true;
                    break;
                }
            }

            if (faceInOval) {
                // Face is inside oval → GREEN, enable capture
                if (ovalEl) ovalEl.setAttribute('stroke', 'rgba(60,227,106,0.8)');
                btnCaptureReg.disabled = false;
                if (guideText) guideText.textContent = '✓ Face detected — ready to capture';
            } else {
                // No face in oval → RED, disable capture
                if (ovalEl) ovalEl.setAttribute('stroke', 'rgba(239,68,68,0.8)');
                btnCaptureReg.disabled = true;
                if (faces.length > 0) {
                    if (guideText) guideText.textContent = '⚠ Move your face inside the oval';
                } else {
                    if (guideText) guideText.textContent = '⚠ No face detected — look at the camera';
                }
            }
        } catch (e) {
            // FaceDetector error — just enable the button as fallback
            btnCaptureReg.disabled = false;
        }
    }, 400);
}

function _stopFaceGuideCheck() {
    if (state._faceGuideInterval) {
        clearInterval(state._faceGuideInterval);
        state._faceGuideInterval = null;
    }
}

function captureRegPhoto() {
    _stopFaceGuideCheck();

    const vw = regVideo.videoWidth;
    const vh = regVideo.videoHeight;

    // The oval guide is centered at (50%, 46%) with rx=35%, ry=36% of the preview.
    // Crop a rectangle that tightly bounds this oval from the raw video feed.
    const cropW = Math.round(vw * 0.70);   // 2 * 35% = 70% of width
    const cropH = Math.round(vh * 0.72);   // 2 * 36% = 72% of height
    const cropX = Math.round((vw - cropW) / 2);         // centered horizontally
    const cropY = Math.round(vh * 0.46 - cropH / 2);    // centered on 46% vertical

    regCanvas.width = cropW;
    regCanvas.height = cropH;
    const ctx = regCanvas.getContext('2d');
    // Draw only the oval-bounded region from the video
    ctx.drawImage(regVideo, cropX, cropY, cropW, cropH, 0, 0, cropW, cropH);

    const dataUrl = regCanvas.toDataURL('image/jpeg', 0.85);
    state.regImageB64 = dataUrl.split(',')[1];
    state.regCaptured = true;

    regSnapshot.src = dataUrl;
    regSnapshot.style.display = 'block';
    regVideo.style.display = 'none';
    regOverlay.style.display = 'none';

    btnCaptureReg.style.display = 'none';
    btnRetakeReg.style.display = 'inline-flex';

    updateRegisterBtn();
}

function retakeRegPhoto() {
    state.regCaptured = false;
    state.regImageB64 = null;

    regSnapshot.style.display = 'none';
    regVideo.style.display = 'block';
    regOverlay.style.display = 'flex';

    btnCaptureReg.style.display = 'inline-flex';
    btnRetakeReg.style.display = 'none';

    // Restart live face guide check
    _startFaceGuideCheck();

    updateRegisterBtn();
}

function updateRegisterBtn() {
    btnRegister.disabled = !(state.regCaptured && personIdInput.value.trim());
}

async function registerFace() {
    const personId = personIdInput.value.trim();
    if (!personId || !state.regImageB64) return;

    btnRegister.disabled = true;
    btnRegister.textContent = 'Registering...';

    try {
        const res = await fetch(`${API_BASE}/registration/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                person_id: personId,
                image_base64: state.regImageB64,
                label: labelInput.value.trim() || null,
            }),
        });

        const data = await res.json();
        showRegResult(data);

        // Auto-fill session person ID
        sessionPersonId.value = personId;

    } catch (e) {
        showRegResult({
            success: false,
            message: 'Network error: ' + e.message,
        });
    }

    btnRegister.disabled = false;
    btnRegister.textContent = 'Register Face';
}

function showRegResult(data) {
    regResult.style.display = 'flex';

    if (data.success) {
        regResultIcon.className = 'result-icon success';
        regResultIcon.textContent = '✓';
        regResultTitle.textContent = 'Registration Successful';
    } else {
        regResultIcon.className = 'result-icon error';
        regResultIcon.textContent = '✗';
        regResultTitle.textContent = 'Registration Failed';
    }

    regResultMessage.textContent = data.message || '';
    regResultMeta.innerHTML = '';

    if (data.face_quality_score != null) {
        regResultMeta.innerHTML += `<span>Quality: ${data.face_quality_score}</span>`;
    }
    if (data.embedding_count != null) {
        regResultMeta.innerHTML += `<span>Embeddings: ${data.embedding_count}</span>`;
    }
}

// ══════════════════════════════════════
// MONITORING SESSION
// ══════════════════════════════════════
function initMonitoring() {
    btnStartSession.addEventListener('click', startSession);
    btnStopSession.addEventListener('click', stopSession);
    btnDownloadReport.addEventListener('click', downloadReport);
}

async function startSession() {
    const personId = sessionPersonId.value.trim();
    if (!personId) {
        alert('Please enter a Person ID');
        return;
    }

    btnStartSession.disabled = true;
    btnStartSession.innerHTML = '<span class="loading-shimmer" style="width:60px;height:16px;display:inline-block;border-radius:4px;"></span> Starting...';

    try {
        // Start camera
        state.monitorStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480, facingMode: 'user' }
        });
        monitorVideo.srcObject = state.monitorStream;

        // Create session via API
        const res = await fetch(`${API_BASE}/session/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ person_id: personId }),
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || 'Failed to start session');
        }

        state.sessionId = data.session_id;
        state.sessionActive = true;
        state.startTime = Date.now();
        state.frameCount = 0;
        state.alertCount = 0;

        // Update UI
        videoPlaceholder.style.display = 'none';
        videoHud.style.display = 'block';
        hudSessionId.textContent = state.sessionId.substring(0, 8) + '...';
        alertList.innerHTML = '<div class="alert-empty">Monitoring active. Waiting for events...</div>';
        alertCount.textContent = '0';

        btnStartSession.style.display = 'none';
        btnStopSession.style.display = 'inline-flex';

        // Start timer
        state.timerInterval = setInterval(updateTimer, 1000);

        // Start WebSocket
        connectWebSocket();

        // Virtual camera warning
        if (data.virtual_camera_warning) {
            addAlert('WARNING', 'virtual_camera_detected', 'Virtual camera software detected!');
        }

    } catch (e) {
        alert('Error starting session: ' + e.message);
        if (state.monitorStream) {
            state.monitorStream.getTracks().forEach(t => t.stop());
        }
    }

    btnStartSession.disabled = false;
    btnStartSession.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> Start Session`;
}

function connectWebSocket() {
    const wsUrl = `${WS_BASE}/ws/monitor/${state.sessionId}`;
    state.ws = new WebSocket(wsUrl);

    state.ws.onopen = () => {
        console.log('WebSocket connected');
        state.awaitingFrameResult = false;
        // Start sending frames
        state.sendInterval = setInterval(sendFrame, 200); // ~5 FPS to server
    };

    state.ws.onmessage = (event) => {
        try {
            state.awaitingFrameResult = false;
            const result = JSON.parse(event.data);
            if (result.error) {
                console.error('Server error:', result.message);
                return;
            }
            updateAnalytics(result);
        } catch (e) {
            console.error('Parse error:', e);
        }
    };

    state.ws.onclose = () => {
        console.log('WebSocket closed');
        state.awaitingFrameResult = false;
        clearInterval(state.sendInterval);
    };

    state.ws.onerror = (e) => {
        state.awaitingFrameResult = false;
        console.error('WebSocket error:', e);
    };
}

function sendFrame() {
    if (!state.ws || state.ws.readyState !== WebSocket.OPEN) return;
    if (!monitorVideo.videoWidth) return;
    if (state.awaitingFrameResult) return;

    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext('2d');

    // Apply brightness and contrast enhancement before sending to backend
    // This makes face detection, iris tracking, and verification much more
    // accurate in low-light and dim webcam conditions.
    ctx.filter = 'brightness(1.15) contrast(1.2)';
    ctx.drawImage(monitorVideo, 0, 0, 640, 480);
    ctx.filter = 'none';

    const dataUrl = canvas.toDataURL('image/jpeg', 0.75);
    const b64 = dataUrl.split(',')[1];

    state.awaitingFrameResult = true;
    state.ws.send(JSON.stringify({ frame: b64 }));

    // FPS counting
    state.fpsCounter.frames++;
    const now = performance.now();
    const elapsed = now - state.fpsCounter.lastTime;
    if (elapsed >= 1000) {
        state.fpsCounter.fps = Math.round(state.fpsCounter.frames * 1000 / elapsed);
        state.fpsCounter.frames = 0;
        state.fpsCounter.lastTime = now;
        hudFps.textContent = `${state.fpsCounter.fps} FPS`;
    }
}

async function stopSession() {
    state.sessionActive = false;
    state.awaitingFrameResult = false;
    clearInterval(state.sendInterval);
    clearInterval(state.timerInterval);

    // Close WebSocket
    if (state.ws) {
        state.ws.close();
        state.ws = null;
    }

    // Stop camera
    if (state.monitorStream) {
        state.monitorStream.getTracks().forEach(t => t.stop());
        state.monitorStream = null;
    }

    // End session via API
    try {
        await fetch(`${API_BASE}/session/${state.sessionId}/end`, { method: 'POST' });
    } catch (e) {
        console.error('Error ending session:', e);
    }

    // Update UI
    btnStopSession.style.display = 'none';
    btnStartSession.style.display = 'inline-flex';
    btnDownloadReport.style.display = 'inline-flex';
    videoHud.style.display = 'none';
    if (monitorCtx) {
        monitorCtx.clearRect(0, 0, monitorCanvas.width, monitorCanvas.height);
    }
    videoPlaceholder.style.display = 'flex';
    videoPlaceholder.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p>Session completed. Download the report below.</p>
    `;
}

function downloadReport() {
    if (state.sessionId) {
        window.open(`${API_BASE}/reports/${state.sessionId}`, '_blank');
    }
}

function updateTimer() {
    if (!state.startTime) return;
    const elapsed = Math.floor((Date.now() - state.startTime) / 1000);
    const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const secs = (elapsed % 60).toString().padStart(2, '0');
    hudTimer.textContent = `${mins}:${secs}`;
}

// ══════════════════════════════════════
// ANALYTICS UPDATE
// ══════════════════════════════════════
function updateAnalytics(result) {
    state.frameCount = result.frame_number || state.frameCount + 1;
    hudFrameCount.textContent = state.frameCount;

    drawVideoOverlays(result);

    // ── Engagement Gauge ──
    const eng = result.engagement_score || 0;
    engagementValue.textContent = Math.round(eng);
    const offset = 157 - (eng / 100 * 157);
    engagementArc.style.strokeDashoffset = offset;
    if (eng >= 70) {
        engagementArc.style.stroke = '#22c55e';
    } else if (eng >= 40) {
        engagementArc.style.stroke = '#f59e0b';
    } else {
        engagementArc.style.stroke = '#ef4444';
    }

    // ── Micro-Violation Score ──
    const microScore = result.micro_violation_score || 0;
    violationValue.textContent = microScore.toFixed(1);
    const pct = Math.min(100, (microScore / 25) * 100);
    violationBarFill.style.width = `${pct}%`;

    // ── Face Status ──
    setBadge(facePresent, result.face_present, 'YES', 'NO');
    faceCount.textContent = result.face_count ?? '—';
    faceCount.className = 'status-badge' + (result.face_count === 1 ? ' ok' : result.face_count > 1 ? ' fail' : '');

    if (result.verification) {
        if (result.verification.verified === 'skipped') {
            // Head is turned — hide the badge completely
            faceVerified.style.display = 'none';
        } else {
            faceVerified.style.display = '';
            setBadge(faceVerified, result.verification.verified, 'YES', 'NO');
        }
    }
    if (result.liveness) {
        setBadge(faceLiveness, result.liveness.is_live, 'LIVE', 'FAIL');
    }

    // ── Head Pose ──
    if (result.head_pose) {
        const hp = result.head_pose;
        const yawPct = Math.max(0, Math.min(100, 50 + (hp.yaw / 60 * 50)));
        const pitchPct = Math.max(0, Math.min(100, 50 + (hp.pitch / 50 * 50)));

        yawIndicator.style.left = `${yawPct}%`;
        pitchIndicator.style.left = `${pitchPct}%`;

        yawValue.textContent = `${hp.yaw.toFixed(1)}°`;
        pitchValue.textContent = `${hp.pitch.toFixed(1)}°`;

        yawIndicator.className = 'pose-indicator' + (hp.yaw_exceeded ? ' fail' : '');
        pitchIndicator.className = 'pose-indicator' + (hp.pitch_exceeded ? ' fail' : '');
    }



    // ── Alerts ──
    if (result.alerts && result.alerts.length > 0) {
        result.alerts.forEach(a => {
            addAlert(a.severity, a.type, a.message);
        });
    }
}

// ══════════════════════════════════════
// VIDEO OVERLAY — ALL-IN-ONE RENDERER
// ══════════════════════════════════════
function drawVideoOverlays(result) {
    if (!monitorCtx) return;

    const sourceW = Number(result.frame_width) || 640;
    const sourceH = Number(result.frame_height) || 480;

    const renderW = monitorVideo.clientWidth || sourceW;
    const renderH = monitorVideo.clientHeight || sourceH;

    if (monitorCanvas.width !== renderW || monitorCanvas.height !== renderH) {
        monitorCanvas.width = renderW;
        monitorCanvas.height = renderH;
    }

    const W = monitorCanvas.width;
    const H = monitorCanvas.height;
    const scaleX = W / sourceW;
    const scaleY = H / sourceH;

    monitorCtx.clearRect(0, 0, W, H);

    // ── 1. FACE DETECTION STATUS OVERLAY ──
    const facePresent = result.face_present;
    const faceCountVal = result.face_count || 0;

    if (!facePresent || faceCountVal === 0) {
        // NO FACE — full-screen red warning
        _drawFullScreenWarning('⚠ NO FACE DETECTED', 'Please position your face in front of the camera', '#ef4444', 0.25);
    } else if (faceCountVal > 1) {
        // MULTI FACE — full-screen orange warning
        _drawFullScreenWarning(
            `⚠ ${faceCountVal} FACES DETECTED`,
            'Only one person should be visible during proctoring',
            '#f59e0b', 0.22
        );
    }

    // ── 2. FACE BOUNDING BOXES ──
    if (Array.isArray(result.face_boxes) && result.face_boxes.length > 0) {
        const isVerified = result.verification && result.verification.verified === true;

        result.face_boxes.forEach((box, idx) => {
            if (!box) return;

            let rawX = box.x ?? box.xmin;
            let rawY = box.y ?? box.ymin;
            let rawW = box.width;
            let rawH = box.height;

            if (rawX == null || rawY == null || rawW == null || rawH == null) return;

            rawX = Number(rawX); rawY = Number(rawY);
            rawW = Number(rawW); rawH = Number(rawH);

            if (!Number.isFinite(rawX) || !Number.isFinite(rawY) || !Number.isFinite(rawW) || !Number.isFinite(rawH)) return;

            const looksNormalized = rawW <= 1.2 && rawH <= 1.2;
            const xPx = looksNormalized ? (rawX * sourceW) : rawX;
            const yPx = looksNormalized ? (rawY * sourceH) : rawY;
            const wPx = looksNormalized ? (rawW * sourceW) : rawW;
            const hPx = looksNormalized ? (rawH * sourceH) : rawH;

            const x = Math.max(0, xPx * scaleX);
            const y = Math.max(0, yPx * scaleY);
            const w = Math.max(0, wPx * scaleX);
            const h = Math.max(0, hPx * scaleY);

            if (w < 6 || h < 6) return;

            // Determine colors per face
            let boxColor, label;
            const verSkipped = result.verification && result.verification.verified === 'skipped';

            if (faceCountVal > 1) {
                boxColor = '#f59e0b';
                label = `FACE ${idx + 1}`;
            } else if (verSkipped) {
                // Head turned — orange box, no verified/not-matched label
                boxColor = '#f59e0b';
                label = '';
            } else if (isVerified) {
                boxColor = '#22c55e';
                label = '✓ VERIFIED';
            } else {
                boxColor = '#ef4444';
                label = '✗ NOT MATCHED';
            }

            // Draw fancy corner brackets instead of plain rect
            _drawFaceBrackets(x, y, w, h, boxColor);

            // Label tag above face (skip when label is empty, e.g. head turned)
            if (label) {
                monitorCtx.font = '700 13px Inter, sans-serif';
                monitorCtx.textBaseline = 'top';
                const textMetrics = monitorCtx.measureText(label);
                const textW = textMetrics.width + 16;
                const textH = 22;
                const textX = x + (w - textW) / 2;
                const textY = y > textH + 8 ? y - textH - 6 : y + h + 6;

                // Tag background with rounded corners
                monitorCtx.fillStyle = boxColor;
                _roundRect(textX, textY, textW, textH, 4);
                monitorCtx.fill();

                monitorCtx.fillStyle = '#ffffff';
                monitorCtx.fillText(label, textX + 8, textY + 4);
            }
        });
    }

    // ── 3. HEAD POSE DIRECTION HUD ──
    if (result.head_pose && facePresent) {
        const hp = result.head_pose;
        const yaw = hp.yaw || 0;
        const pitch = hp.pitch || 0;

        // Determine head direction text
        let headDir = 'FORWARD';
        const yawAbs = Math.abs(yaw);
        const pitchAbs = Math.abs(pitch);

        if (yawAbs > 15 || pitchAbs > 12) {
            const parts = [];
            if (pitch < -12) parts.push('UP');
            else if (pitch > 12) parts.push('DOWN');
            if (yaw < -15) parts.push('RIGHT');
            else if (yaw > 15) parts.push('LEFT');
            headDir = parts.length > 0 ? parts.join('-') : 'FORWARD';
        }

        const isExceeded = hp.yaw_exceeded || hp.pitch_exceeded;
        const headColor = isExceeded ? '#ef4444' : (headDir === 'FORWARD' ? '#22c55e' : '#f59e0b');

        // Draw head pose pill — bottom-left area
        const pillX = 14;
        const pillY = H - 80;
        _drawInfoPill(pillX, pillY,
            '🧭 HEAD', headDir,
            `Y:${yaw.toFixed(0)}° P:${pitch.toFixed(0)}°`,
            headColor, isExceeded
        );

        // Draw directional arrow in the center-bottom
        if (headDir !== 'FORWARD') {
            _drawDirectionArrow(W / 2, H - 30, yaw, pitch, headColor);
        }
    }
}
// ── HELPER: Full-screen warning overlay ──
function _drawFullScreenWarning(title, subtitle, color, alpha) {
    const W = monitorCanvas.width;
    const H = monitorCanvas.height;

    // Tinted overlay
    monitorCtx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
    monitorCtx.fillRect(0, 0, W, H);

    // Pulsing border
    const borderW = 4;
    monitorCtx.strokeStyle = color;
    monitorCtx.lineWidth = borderW;
    monitorCtx.setLineDash([12, 6]);
    monitorCtx.strokeRect(borderW, borderW, W - borderW * 2, H - borderW * 2);
    monitorCtx.setLineDash([]);

    // Warning icon circle
    const centerX = W / 2;
    const centerY = H / 2 - 20;
    monitorCtx.beginPath();
    monitorCtx.arc(centerX, centerY - 20, 30, 0, Math.PI * 2);
    monitorCtx.fillStyle = color + '33';
    monitorCtx.fill();
    monitorCtx.strokeStyle = color;
    monitorCtx.lineWidth = 2.5;
    monitorCtx.stroke();

    // Warning "!" inside circle
    monitorCtx.fillStyle = color;
    monitorCtx.font = '700 28px Inter, sans-serif';
    monitorCtx.textAlign = 'center';
    monitorCtx.textBaseline = 'middle';
    monitorCtx.fillText('!', centerX, centerY - 20);

    // Title text
    monitorCtx.font = '800 20px Inter, sans-serif';
    monitorCtx.fillStyle = color;
    monitorCtx.textAlign = 'center';
    monitorCtx.textBaseline = 'top';
    monitorCtx.fillText(title, centerX, centerY + 20);

    // Subtitle
    monitorCtx.font = '400 13px Inter, sans-serif';
    monitorCtx.fillStyle = 'rgba(255,255,255,0.7)';
    monitorCtx.fillText(subtitle, centerX, centerY + 48);

    // Reset alignment
    monitorCtx.textAlign = 'start';
    monitorCtx.textBaseline = 'alphabetic';
}

// ── HELPER: Fancy corner brackets for face box ──
function _drawFaceBrackets(x, y, w, h, color) {
    const cornerLen = Math.min(20, w * 0.25, h * 0.25);
    monitorCtx.strokeStyle = color;
    monitorCtx.lineWidth = 3;
    monitorCtx.lineJoin = 'round';
    monitorCtx.lineCap = 'round';

    // Subtle full rect
    monitorCtx.globalAlpha = 0.25;
    monitorCtx.strokeRect(x, y, w, h);
    monitorCtx.globalAlpha = 1.0;

    // Top-left
    monitorCtx.beginPath();
    monitorCtx.moveTo(x, y + cornerLen);
    monitorCtx.lineTo(x, y);
    monitorCtx.lineTo(x + cornerLen, y);
    monitorCtx.stroke();

    // Top-right
    monitorCtx.beginPath();
    monitorCtx.moveTo(x + w - cornerLen, y);
    monitorCtx.lineTo(x + w, y);
    monitorCtx.lineTo(x + w, y + cornerLen);
    monitorCtx.stroke();

    // Bottom-left
    monitorCtx.beginPath();
    monitorCtx.moveTo(x, y + h - cornerLen);
    monitorCtx.lineTo(x, y + h);
    monitorCtx.lineTo(x + cornerLen, y + h);
    monitorCtx.stroke();

    // Bottom-right
    monitorCtx.beginPath();
    monitorCtx.moveTo(x + w - cornerLen, y + h);
    monitorCtx.lineTo(x + w, y + h);
    monitorCtx.lineTo(x + w, y + h - cornerLen);
    monitorCtx.stroke();

    // Glow effect
    monitorCtx.shadowColor = color;
    monitorCtx.shadowBlur = 8;
    monitorCtx.strokeStyle = color;
    monitorCtx.lineWidth = 1;
    monitorCtx.strokeRect(x, y, w, h);
    monitorCtx.shadowBlur = 0;
    monitorCtx.shadowColor = 'transparent';
}

// ── HELPER: Rounded rect path ──
function _roundRect(x, y, w, h, r) {
    monitorCtx.beginPath();
    monitorCtx.moveTo(x + r, y);
    monitorCtx.lineTo(x + w - r, y);
    monitorCtx.quadraticCurveTo(x + w, y, x + w, y + r);
    monitorCtx.lineTo(x + w, y + h - r);
    monitorCtx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    monitorCtx.lineTo(x + r, y + h);
    monitorCtx.quadraticCurveTo(x, y + h, x, y + h - r);
    monitorCtx.lineTo(x, y + r);
    monitorCtx.quadraticCurveTo(x, y, x + r, y);
    monitorCtx.closePath();
}

// ── HELPER: Info pill (head pose HUD) ──
function _drawInfoPill(x, y, label, value, subText, color, isAlert) {
    const pillW = 176;
    const pillH = subText ? 58 : 46;

    // Background with glass effect
    monitorCtx.fillStyle = 'rgba(0, 0, 0, 0.65)';
    _roundRect(x, y, pillW, pillH, 8);
    monitorCtx.fill();

    // Border
    monitorCtx.strokeStyle = isAlert ? color : 'rgba(255,255,255,0.15)';
    monitorCtx.lineWidth = 1.5;
    _roundRect(x, y, pillW, pillH, 8);
    monitorCtx.stroke();

    // Left color accent bar
    monitorCtx.fillStyle = color;
    _roundRect(x, y, 4, pillH, 2);
    monitorCtx.fill();

    // Label
    monitorCtx.font = '600 10px Inter, sans-serif';
    monitorCtx.fillStyle = 'rgba(255,255,255,0.5)';
    monitorCtx.textBaseline = 'top';
    monitorCtx.textAlign = 'start';
    monitorCtx.fillText(label, x + 14, y + 8);

    // Value
    monitorCtx.font = '800 16px Inter, sans-serif';
    monitorCtx.fillStyle = color;
    monitorCtx.fillText(value, x + 14, y + 22);

    // Subtext
    if (subText) {
        monitorCtx.font = '400 10px Inter, sans-serif';
        monitorCtx.fillStyle = 'rgba(255,255,255,0.45)';
        monitorCtx.fillText(subText, x + 14, y + 42);
    }

    // Status dot
    monitorCtx.beginPath();
    monitorCtx.arc(x + pillW - 16, y + 14, 4, 0, Math.PI * 2);
    monitorCtx.fillStyle = color;
    monitorCtx.fill();

    // Reset
    monitorCtx.textAlign = 'start';
    monitorCtx.textBaseline = 'alphabetic';
}

// ── HELPER: Direction arrow for head pose ──
function _drawDirectionArrow(cx, cy, yaw, pitch, color) {
    const arrowLen = 18;
    // yaw: negative = looking right on screen, positive = looking left on screen
    // pitch: negative = looking up, positive = looking down
    const angle = Math.atan2(pitch, -yaw);

    monitorCtx.save();
    monitorCtx.translate(cx, cy);
    monitorCtx.rotate(angle);

    // Arrow shaft
    monitorCtx.strokeStyle = color;
    monitorCtx.lineWidth = 3;
    monitorCtx.lineCap = 'round';
    monitorCtx.beginPath();
    monitorCtx.moveTo(-arrowLen, 0);
    monitorCtx.lineTo(arrowLen, 0);
    monitorCtx.stroke();

    // Arrow head
    monitorCtx.fillStyle = color;
    monitorCtx.beginPath();
    monitorCtx.moveTo(arrowLen + 2, 0);
    monitorCtx.lineTo(arrowLen - 6, -6);
    monitorCtx.lineTo(arrowLen - 6, 6);
    monitorCtx.closePath();
    monitorCtx.fill();

    monitorCtx.restore();
}



function setBadge(el, condition, yesText, noText) {
    if (condition) {
        el.textContent = yesText;
        el.className = 'status-badge ok';
    } else {
        el.textContent = noText;
        el.className = 'status-badge fail';
    }
}

// ══════════════════════════════════════
// ALERT FEED
// ══════════════════════════════════════
function addAlert(severity, type, message) {
    state.alertCount++;
    alertCount.textContent = state.alertCount;

    // Remove empty state
    const empty = alertList.querySelector('.alert-empty');
    if (empty) empty.remove();

    const now = new Date().toLocaleTimeString();

    const el = document.createElement('div');
    el.className = `alert-item severity-${severity}`;
    el.innerHTML = `
        <span class="alert-severity-tag ${severity}">${severity}</span>
        <span class="alert-message">${message}</span>
        <span class="alert-time">${now}</span>
    `;

    alertList.prepend(el);

    // Keep max 50 alerts in UI
    while (alertList.children.length > 50) {
        alertList.removeChild(alertList.lastChild);
    }
}
