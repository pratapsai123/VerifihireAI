"""
Session Manager Service

Manages monitoring session lifecycle: create, get, end.
Orchestrates all per-session service instances (detectors, trackers, etc.)

Updated to use new MediaPipe Tasks API class-based services.
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Optional

from app.models import database as db
from app.models.schemas import SessionConfig
from app.services.alert_system import AlertSystem
from app.services.deepfake_detection import DeepfakeDetector, check_virtual_camera
from app.services.face_detection import FaceDetectionService
from app.services.face_verification import PeriodicVerifier

from app.services.head_pose import HeadPoseService
from app.services.liveness_detection import LivenessDetectionService
from app.services.violation_logger import ViolationLogger
from app.services.face_registration import is_registered

logger = logging.getLogger(__name__)


class MonitoringSession:
    """
    A complete monitoring session with all service instances.
    One instance per active session.
    """

    def __init__(
        self,
        session_id: str,
        person_id: str,
        config: Optional[SessionConfig] = None,
    ):
        self.session_id = session_id
        self.person_id = person_id
        self.config = config or SessionConfig()
        self.started_at = datetime.utcnow()
        self.status = "active"
        self.frame_count = 0

        # Initialize per-session service instances (new Tasks API classes)
        self.face_detector = FaceDetectionService()
        self.liveness_detector = LivenessDetectionService()
        self.head_pose_estimator = HeadPoseService()

        self.deepfake_detector = DeepfakeDetector()
        self.alert_system = AlertSystem()
        self.violation_logger = ViolationLogger(session_id)
        self.periodic_verifier = PeriodicVerifier(person_id)

        # Persist last identity decision so cached frames don't default to verified.
        self.last_verification = {
            "verified": False,
            "confidence": 0.0,
            "model_used": "pending",
            "low_confidence": False,
        }
        self.last_verification_ts = time.time()

        # Engagement tracking
        self.engagement_scores = []

    def increment_frame(self):
        self.frame_count += 1

    def close(self):
        """Release all resources."""
        try:
            self.face_detector.close()
            self.head_pose_estimator.close()

            self.liveness_detector.close()
        except Exception:
            pass
        self.status = "completed"


# ──────────────────────────────────────────────
# SESSION REGISTRY (in-memory for active sessions)
# ──────────────────────────────────────────────
_active_sessions: Dict[str, MonitoringSession] = {}


async def start_session(
    person_id: str,
    session_id: Optional[str] = None,
    config: Optional[SessionConfig] = None,
    camera_device: Optional[str] = None,
) -> Dict:
    """
    Start a new monitoring session.

    Args:
        person_id: Registered person to monitor.
        session_id: Custom session ID (auto-generated if None).
        config: Session configuration overrides.
        camera_device: Client camera device name.

    Returns:
        Session start data.
    """
    sid = session_id or str(uuid.uuid4())

    # Check for existing active session
    if sid in _active_sessions:
        return {
            "session_id": sid,
            "status": "already_active",
            "message": "Session already exists and is active.",
        }

    # Ensure the person is registered before allowing a session
    if not is_registered(person_id):
        return {
            "session_id": sid,
            "status": "not_registered",
            "message": f"Candidate '{person_id}' has not registered a reference face. Registration required before starting a session.",
        }

    # Create database record
    await db.create_session(
        session_id=sid,
        person_id=person_id,
        config=config.model_dump() if config else None,
        camera_device=camera_device,
    )

    # Create in-memory session
    session = MonitoringSession(sid, person_id, config)
    _active_sessions[sid] = session

    # Check for virtual camera
    vc_result = check_virtual_camera(camera_device)

    logger.info(f"Session started: {sid} for person {person_id}")

    return {
        "session_id": sid,
        "person_id": person_id,
        "status": "active",
        "started_at": session.started_at,
        "message": "Monitoring session started.",
        "virtual_camera_warning": vc_result.get("virtual_camera_detected", False),
    }


def get_active_session(session_id: str) -> Optional[MonitoringSession]:
    """Get an active monitoring session by ID."""
    return _active_sessions.get(session_id)


async def end_session(session_id: str) -> Optional[Dict]:
    """
    End an active monitoring session.

    Returns:
        Final session data or None if not found.
    """
    session = _active_sessions.pop(session_id, None)

    if session:
        session.close()

        # Update database
        db_session = await db.end_session(session_id)

        # Update final micro-violation score
        final_score = session.violation_logger.compute_micro_violation_score()
        await db.update_micro_violation_score(session_id, final_score)

        logger.info(f"Session ended: {session_id}")

        return db_session

    # Try to end in database even if not in memory
    return await db.end_session(session_id)


async def get_session_status(session_id: str) -> Optional[Dict]:
    """Get session status from database."""
    return await db.get_session(session_id)


def get_all_active_sessions() -> Dict[str, str]:
    """Get all active session IDs and their person IDs."""
    return {sid: s.person_id for sid, s in _active_sessions.items()}
