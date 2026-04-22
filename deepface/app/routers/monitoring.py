"""
Monitoring Router — Real-time WebSocket Frame Analysis

WebSocket endpoint: /ws/monitor/{session_id}

Each service call is individually wrapped in try/except so that
a failure in one service doesn't prevent others from running.
"""

import asyncio
import json
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time

import numpy as np

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models import database as db
from app.services import session_manager
from app.services.engagement import compute_engagement_score
from app.services.face_verification import verify_face_realtime
from app.utils.constants import ViolationType
from app.utils.image_utils import crop_face_region, decode_base64_image, resize_image

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Real-time Monitoring"])

# Dedicated thread pool for CPU-heavy frame processing (face detection, verification, etc.)
_frame_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="deepface-frame")


@router.websocket("/ws/monitor/{session_id}")
async def monitor_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()

    session = session_manager.get_active_session(session_id)
    if not session:
        await websocket.send_json({
            "error": True,
            "message": f"No active session found: {session_id}",
        })
        await websocket.close(code=4004)
        return

    logger.info(f"WebSocket connected for session: {session_id}")

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": True, "message": "Invalid JSON"})
                continue

            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            frame_b64 = message.get("frame")
            if not frame_b64:
                continue

            try:
                frame = decode_base64_image(frame_b64)
                frame = resize_image(frame, max_width=480, max_height=360)
            except Exception as e:
                await websocket.send_json({"error": True, "message": f"Image decode error: {e}"})
                continue

            # Process frame — fully crash-proof
            try:
                result = await _process_frame(session, frame)
            except Exception as e:
                logger.error(f"Frame processing error: {e}\n{traceback.format_exc()}")
                result = {
                    "frame_number": session.frame_count,
                    "error": True,
                    "message": f"Processing error: {str(e)}",
                }

            await websocket.send_json(_json_safe(result))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}\n{traceback.format_exc()}")
        try:
            await websocket.close(code=4000)
        except Exception:
            pass


async def _process_frame(session: session_manager.MonitoringSession, frame) -> dict:
    """
    Run all analysis services on a single frame.
    Each service is individually protected — failures produce defaults.
    """
    session.increment_frame()
    frame_num = session.frame_count
    config = session.config

    result = {
        "frame_number": frame_num,
        "timestamp": datetime.utcnow().isoformat(),
        "frame_width": int(frame.shape[1]) if frame is not None else 0,
        "frame_height": int(frame.shape[0]) if frame is not None else 0,
        "face_present": False,
        "face_count": 0,
        "face_boxes": [],
        "verification": {"verified": False, "confidence": 0.0, "model_used": "none", "low_confidence": False},
        "liveness": {"is_live": True, "texture_score": 0.0, "blink_detected": False, "motion_detected": False},
        "head_pose": {"yaw": 0.0, "pitch": 0.0, "yaw_exceeded": False, "pitch_exceeded": False},

        "engagement_score": 0.0,
        "micro_violation_score": 0.0,
        "alerts": [],
    }

    # ── 1. Face Detection ──
    try:
        detection = session.face_detector.detect(frame)
        result["face_present"] = detection.get("face_present", False)
        result["face_count"] = detection.get("face_count", 0)
        result["face_boxes"] = detection.get("bounding_boxes", []) or []
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        detection = {"face_present": False, "face_count": 0}

    if not result["face_present"]:
        session.last_verification = {
            "verified": False,
            "confidence": 0.0,
            "model_used": "no_face",
            "low_confidence": False,
        }
        # DO NOT update last_verification_ts here.
        # This ensures that as soon as a face reappears, the PeriodicVerifier
        # timers will have expired and an immediate re-verification fires.
        # Reset the verifier clocks so the next face-present frame triggers
        # an instant fresh check.
        session.periodic_verifier.last_sface_check = 0.0
        session.periodic_verifier.last_arcface_check = 0.0

        # Log no-face violation
        try:
            alert = session.alert_system.trigger(ViolationType.NO_FACE)
            if alert:
                result["alerts"].append(_safe_alert(alert))
                await session.violation_logger.log(ViolationType.NO_FACE)
        except Exception as e:
            logger.error(f"Alert/violation logging error: {e}")

        # Compute engagement (low since no face)
        try:
            eng = compute_engagement_score(face_present=False)
            result["engagement_score"] = eng.get("score", 0.0)
            session.engagement_scores.append(result["engagement_score"])
        except Exception as e:
            logger.error(f"Engagement error: {e}")

        result["micro_violation_score"] = _safe_micro_score(session)
        await _safe_update_db(session, result["engagement_score"])
        return result

    # Multiple faces — log alert but still verify the primary face
    if result["face_count"] > 1:
        try:
            alert = session.alert_system.trigger(ViolationType.MULTIPLE_FACES)
            if alert:
                result["alerts"].append(_safe_alert(alert))
                await session.violation_logger.log(
                    ViolationType.MULTIPLE_FACES,
                    details={"count": result["face_count"]},
                )
        except Exception as e:
            logger.error(f"Multiple faces alert error: {e}")

    # ── 2. Face Verification (runs for ANY frame with at least 1 face) ──
    # Always verify the PRIMARY face (largest bounding box, sorted first).
    # This ensures the registered user stays "verified" even when extra
    # faces appear in the background.
    if result["face_count"] >= 1:
        try:
            check_model = session.periodic_verifier.get_model_for_check()
            if check_model:
                verify_frame = frame
                # Use the primary tracked face region for identity verification.
                # face_boxes are sorted largest-first by the detector, so [0]
                # is always the main/closest face.
                try:
                    primary_box = (result.get("face_boxes") or [None])[0]
                    if primary_box:
                        bbox = (
                            int(primary_box.get("x", 0)),
                            int(primary_box.get("y", 0)),
                            int(primary_box.get("width", 0)),
                            int(primary_box.get("height", 0)),
                        )
                        cropped = crop_face_region(frame, bbox, padding=0.22)
                        if cropped is not None and cropped.size > 0:
                            verify_frame = cropped
                except Exception as crop_err:
                    logger.debug(f"Verification crop fallback to full frame: {crop_err}")

                vr = verify_face_realtime(session.person_id, verify_frame, model=check_model)
                result["verification"] = {
                    "verified": vr.get("verified", False),
                    "confidence": vr.get("confidence", 0.0),
                    "model_used": vr.get("model_used", check_model),
                    "low_confidence": vr.get("low_confidence", False),
                }
                session.last_verification = dict(result["verification"])
                session.last_verification_ts = time.time()
                session.periodic_verifier.mark_done(vr.get("model_used", check_model))

                try:
                    await db.increment_session_counters(
                        session.session_id,
                        verification_attempt=True,
                        verification_success=vr.get("verified", False),
                    )
                except Exception:
                    pass

                if not vr.get("verified", True):
                    # Reset verifier timers so the NEXT frame immediately
                    # re-checks. This way, when the correct face returns,
                    # it gets recognized on the very first frame — no delay.
                    session.periodic_verifier.last_sface_check = 0.0
                    session.periodic_verifier.last_arcface_check = 0.0

                    vtype = ViolationType.LOW_CONFIDENCE if vr.get("low_confidence") else ViolationType.VERIFICATION_FAILED
                    try:
                        alert = session.alert_system.trigger(vtype)
                        if alert:
                            result["alerts"].append(_safe_alert(alert))
                            await session.violation_logger.log(vtype, details={"confidence": vr.get("confidence")})
                    except Exception:
                        pass
            else:
                # No verification needed this frame — report last known decision.
                cached = dict(getattr(session, "last_verification", {
                    "verified": False,
                    "confidence": 0.0,
                    "model_used": "pending",
                    "low_confidence": False,
                }))
                cached["model_used"] = f"cached:{cached.get('model_used', 'unknown')}"
                result["verification"] = cached
        except Exception as e:
            logger.error(f"Verification error: {e}")

    # ── 3. Liveness Detection ──
    try:
        if config.enable_liveness:
            lr = session.liveness_detector.check(frame)
            result["liveness"] = {
                "is_live": lr.get("is_live", True),
                "texture_score": lr.get("texture_score", 0.0),
                "blink_detected": lr.get("blink_detected", False),
                "motion_detected": lr.get("motion_detected", False),
            }
            if not lr.get("is_live", True):
                try:
                    alert = session.alert_system.trigger(ViolationType.LIVENESS_FAILED)
                    if alert:
                        result["alerts"].append(_safe_alert(alert))
                        await session.violation_logger.log(ViolationType.LIVENESS_FAILED)
                except Exception:
                    pass
    except Exception as e:
        logger.error(f"Liveness error: {e}")

    # ── 4. Head Pose ──
    try:
        hp = session.head_pose_estimator.estimate(frame)
        result["head_pose"] = hp

        if hp.get("yaw_exceeded"):
            try:
                alert = session.alert_system.trigger(ViolationType.HEAD_YAW_EXCEEDED)
                if alert:
                    result["alerts"].append(_safe_alert(alert))
                    await session.violation_logger.log(ViolationType.HEAD_YAW_EXCEEDED, details={"yaw": hp["yaw"]})
            except Exception:
                pass

        if hp.get("pitch_exceeded"):
            try:
                alert = session.alert_system.trigger(ViolationType.HEAD_PITCH_EXCEEDED)
                if alert:
                    result["alerts"].append(_safe_alert(alert))
                    await session.violation_logger.log(ViolationType.HEAD_PITCH_EXCEEDED, details={"pitch": hp["pitch"]})
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Head pose error: {e}")

    # ── 4b. Pause verification when face is turned away ──
    # When the head is turned, face recognition is unreliable so we SKIP it
    # entirely — no "matched" or "not matched" is shown. Verification only
    # resumes when the candidate looks forward again.
    pose = result.get("head_pose", {})
    if pose.get("yaw_exceeded") or pose.get("pitch_exceeded"):
        result["verification"] = {
            "verified": "skipped",
            "confidence": 0.0,
            "model_used": "pose_exceeded",
            "low_confidence": False,
        }
        # Reset timers so the INSTANT they look forward, a fresh check fires.
        session.periodic_verifier.last_sface_check = 0.0
        session.periodic_verifier.last_arcface_check = 0.0


    # ── 6. Deepfake Detection (every 10th frame) ──
    try:
        if config.enable_deepfake and frame_num % 10 == 0:
            df = session.deepfake_detector.analyze(frame)
            if df.get("deepfake_suspected"):
                try:
                    alert = session.alert_system.trigger(ViolationType.DEEPFAKE_SUSPECTED)
                    if alert:
                        result["alerts"].append(_safe_alert(alert))
                        await session.violation_logger.log(ViolationType.DEEPFAKE_SUSPECTED, details=df)
                except Exception:
                    pass
    except Exception as e:
        logger.error(f"Deepfake detection error: {e}")

    # ── 7. Engagement Score ──
    try:
        eng = compute_engagement_score(
            face_present=result["face_present"],
            face_count=result["face_count"],

            head_pose_attentive=not (result["head_pose"].get("yaw_exceeded") or result["head_pose"].get("pitch_exceeded")),
            liveness_passed=result["liveness"].get("is_live", True),
            verification_passed=result["verification"].get("verified", True),
        )
        result["engagement_score"] = eng.get("score", 0.0)
        session.engagement_scores.append(result["engagement_score"])
    except Exception as e:
        logger.error(f"Engagement error: {e}")

    # ── 8. Micro-Violation Score ──
    result["micro_violation_score"] = _safe_micro_score(session)

    try:
        if session.violation_logger.is_critical():
            alert = session.alert_system.trigger(ViolationType.MICRO_VIOLATION_CRITICAL)
            if alert:
                result["alerts"].append(_safe_alert(alert))
    except Exception:
        pass

    # ── Update database ──
    await _safe_update_db(session, result.get("engagement_score", 0.0))

    # Log engagement snapshot every 10 frames
    if frame_num % 10 == 0:
        try:
            await db.log_engagement_snapshot(session.session_id, result["engagement_score"], None)
        except Exception:
            pass

    return result


def _safe_alert(alert) -> dict:
    """Convert an alert to a safe JSON dict."""
    try:
        if hasattr(alert, "model_dump"):
            d = alert.model_dump(mode="json")
            # Ensure timestamp is string
            if "timestamp" in d and not isinstance(d["timestamp"], str):
                d["timestamp"] = str(d["timestamp"])
            return d
        return {"severity": "WARNING", "type": "unknown", "message": str(alert)}
    except Exception:
        return {"severity": "WARNING", "type": "unknown", "message": "Alert serialization failed"}


def _safe_micro_score(session) -> float:
    try:
        return session.violation_logger.compute_micro_violation_score()
    except Exception:
        return 0.0


async def _safe_update_db(session, engagement_score: float):
    try:
        await db.increment_session_counters(
            session.session_id,
            frames=1,
            engagement_score=engagement_score,
        )
    except Exception:
        pass


def _json_safe(value):
    """Recursively convert numpy/scalar values to JSON-native Python types."""
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, datetime):
        return value.isoformat()

    return value
