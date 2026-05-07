"""
Registration Router — Face Registration & Verification API

Endpoints:
  POST /register        — Register a face
  POST /verify          — One-shot verification
  GET  /registered/{id} — Check registration status
  DELETE /registered/{id} — Remove registration
"""

import logging

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

from app.models.schemas import (
    FaceRegisterRequest,
    FaceRegisterResponse,
    FaceVerifyRequest,
    FaceVerifyResponse,
)
from app.services.face_registration import (
    delete_registration,
    is_registered,
    register_face,
)
from app.services.face_verification import verify_face

router = APIRouter(prefix="/registration", tags=["Face Registration"])


@router.post("/register", response_model=FaceRegisterResponse)
async def register_face_endpoint(request: FaceRegisterRequest):
    """Register a face for a person using ArcFace (high accuracy)."""
    logger.info(f"Registering face for person_id: {request.person_id}")
    result = register_face(
        person_id=request.person_id,
        image_base64=request.image_base64,
        label=request.label,
        overwrite=request.overwrite,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return FaceRegisterResponse(
        success=result["success"],
        person_id=result["person_id"],
        message=result["message"],
        face_quality_score=result.get("face_quality_score"),
        embedding_count=result.get("embedding_count", 0),
        embedding_hash=result.get("embedding_hash"),
    )


@router.post("/verify", response_model=FaceVerifyResponse)
async def verify_face_endpoint(request: FaceVerifyRequest):
    """One-shot face verification against registered embeddings."""
    result = verify_face(
        person_id=request.person_id,
        image_base64=request.image_base64,
        model=request.model,
    )

    return FaceVerifyResponse(**result)


@router.get("/registered/{person_id}")
async def check_registration(person_id: str):
    """Check if a person has registered face data."""
    registered = is_registered(person_id)
    return {
        "person_id": person_id,
        "registered": registered,
    }


@router.get("/registered/{person_id}/photo")
async def get_registered_photo(person_id: str):
    """Serve the registered face photo as a JPEG image."""
    from fastapi.responses import FileResponse
    from app.config import REGISTERED_FACES_DIR

    person_id = person_id.strip().lower()
    person_dir = REGISTERED_FACES_DIR / person_id

    if not person_dir.exists():
        raise HTTPException(status_code=404, detail="Person not registered")

    # Look for any jpg file in the person's directory
    for img_file in person_dir.glob("*.jpg"):
        return FileResponse(str(img_file), media_type="image/jpeg")

    raise HTTPException(status_code=404, detail="No photo found for this person")


@router.delete("/registered/{person_id}")
async def remove_registration(person_id: str):
    """Delete all registered face data for a person."""
    deleted = delete_registration(person_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"person_id": person_id, "deleted": True}
