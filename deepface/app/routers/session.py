"""
Session Router — Session Management API

Endpoints:
  POST /session/start            — Start a monitoring session
  GET  /session/{id}             — Get session status
  POST /session/{id}/end         — End a session
  GET  /session/{id}/violations  — Get violations for a session
"""

import logging

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

from app.models.schemas import (
    SessionStartRequest,
    SessionStartResponse,
    SessionStatusResponse,
    ViolationListResponse,
)
from app.services import session_manager
from app.services.face_verification import verify_face
from app.models import database as db

router = APIRouter(prefix="/session", tags=["Session Management"])


@router.post("/start")
async def start_session(request: SessionStartRequest):
    """Start a new monitoring session with initial ArcFace verification."""
    logger.info(f"Session start request for person_id: {request.person_id}")
    try:
        result = await session_manager.start_session(
            person_id=request.person_id,
            session_id=request.session_id,
            config=request.config,
            camera_device=request.camera_device_name,
        )

        if result.get("status") == "already_active":
            raise HTTPException(status_code=409, detail=result["message"])
            
        if result.get("status") == "not_registered":
            raise HTTPException(status_code=403, detail=result["message"])

        # Serialize datetime to ISO string for JSON
        started_at = result.get("started_at")
        if hasattr(started_at, "isoformat"):
            started_at = started_at.isoformat()

        return {
            "session_id": result["session_id"],
            "person_id": result["person_id"],
            "status": result["status"],
            "started_at": started_at,
            "message": result["message"],
            "virtual_camera_warning": result.get("virtual_camera_warning", False),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session start failed: {str(e)}")


@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get session status and metrics."""
    session = await session_manager.get_session_status(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Compute verification success rate
    attempts = session.get("verification_attempts", 0)
    successes = session.get("verification_successes", 0)
    success_rate = (successes / attempts * 100) if attempts > 0 else 0.0

    # Get active session for live engagement
    active = session_manager.get_active_session(session_id)
    current_engagement = 0.0
    micro_score = session.get("micro_violation_score", 0.0)

    if active and active.engagement_scores:
        current_engagement = active.engagement_scores[-1]
        micro_score = active.violation_logger.compute_micro_violation_score()

    return {
        "session_id": session_id,
        "person_id": session.get("person_id"),
        "status": session.get("status"),
        "started_at": session.get("started_at"),
        "total_frames_analyzed": session.get("total_frames", 0),
        "total_violations": session.get("total_violations", 0),
        "current_engagement_score": round(current_engagement, 1),
        "micro_violation_score": round(micro_score, 2),
        "verification_success_rate": round(success_rate, 1),
    }


@router.post("/{session_id}/end")
async def end_session(session_id: str):
    """End a monitoring session and finalize data."""
    result = await session_manager.end_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "status": "completed",
        "message": "Session ended. Report is available.",
    }


@router.get("/{session_id}/violations")
async def get_violations(session_id: str):
    """Get all violations for a session."""
    violations = await db.get_violations(session_id)
    return {
        "session_id": session_id,
        "total": len(violations),
        "violations": violations,
    }
