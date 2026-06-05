"""
Unified DeepFace Microservice Client
=====================================

Single source of truth for all face registration and verification across
the entire backend — Standard Assessment, AI Candidate, and AI Assessment.

All calls go to the DeepFace microservice (http://localhost:8500/api/v1).
person_id convention: pan_number.strip().lower() for root identity;
  <pan>/sessions/<token>   for per-interview proctoring anchors;
  <pan>/assessments/<token> for per-assessment proctoring anchors.

Hard-fail policy: If the microservice is unreachable, DeepFaceServiceError
is raised. Callers must handle it explicitly — no silent fallbacks.
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _get_base_url() -> str:
    """Resolve the DeepFace microservice base URL at call-time so it respects
    runtime env overrides without requiring a server restart."""
    try:
        from django.conf import settings
        url = getattr(settings, "DEEPFACE_BASE_URL", None)
        if url:
            return url.rstrip("/")
    except Exception:
        pass
    return os.environ.get("DEEPFACE_BASE_URL", "http://localhost:8500/api/v1").rstrip("/")


_TIMEOUT_REGISTER = 30   # seconds — registration extracts embeddings (slower)
_TIMEOUT_VERIFY   = 15   # seconds — verification is faster
_TIMEOUT_CHECK    = 5    # seconds — simple is_registered probe


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DeepFaceServiceError(Exception):
    """Raised when the DeepFace microservice is unreachable or returns an error."""
    pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def df_register(person_id: str, image_b64: str, overwrite: bool = False) -> dict:
    """
    Register a face with the DeepFace microservice.

    Args:
        person_id:   Unique identity key — always PAN.lower() for root identity,
                     or '<pan>/sessions/<token>' / '<pan>/assessments/<token>'
                     for proctoring session anchors.
        image_b64:   Base64-encoded JPEG/PNG image (with or without data-URL prefix).
        overwrite:   If True, replace any existing embedding for this person_id.

    Returns:
        dict with keys: success (bool), person_id, message, embedding_hash, etc.

    Raises:
        DeepFaceServiceError: if microservice is unreachable or returns HTTP >= 400.
    """
    person_id = str(person_id).strip().lower()

    # Strip data-URL prefix if present so the microservice receives raw base64.
    if isinstance(image_b64, str) and "," in image_b64 and image_b64.startswith("data:"):
        image_b64 = image_b64.split(",", 1)[1]

    url = f"{_get_base_url()}/registration/register"
    payload = {
        "person_id": person_id,
        "image_base64": image_b64,
        "overwrite": overwrite,
    }

    try:
        resp = requests.post(url, json=payload, timeout=_TIMEOUT_REGISTER)
    except requests.exceptions.ConnectionError as exc:
        logger.error("[DeepFace] register(%s) — microservice unreachable: %s", person_id, exc)
        raise DeepFaceServiceError(
            f"DeepFace microservice is unreachable at {_get_base_url()}. "
            "Ensure the service is running."
        ) from exc
    except requests.exceptions.Timeout as exc:
        logger.error("[DeepFace] register(%s) — request timed out", person_id)
        raise DeepFaceServiceError("DeepFace registration request timed out.") from exc

    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text[:500]}

    if resp.status_code >= 400:
        msg = body.get("detail") or body.get("message") or str(body)
        logger.error("[DeepFace] register(%s) HTTP %s: %s", person_id, resp.status_code, msg)
        raise DeepFaceServiceError(f"DeepFace registration failed for {person_id}: {msg}")

    logger.info(
        "[DeepFace] register(%s) → success=%s hash=%s",
        person_id,
        body.get("success"),
        str(body.get("embedding_hash", ""))[:16],
    )
    return body


def df_verify(person_id: str, image_b64: str, model: str = "ArcFace") -> dict:
    """
    Verify a face against the registered embedding for person_id.

    Args:
        person_id:  Identity key (PAN.lower() for root, session path for anchors).
        image_b64:  Base64-encoded webcam snapshot.
        model:      Recognition model ('ArcFace' or 'SFace').

    Returns:
        dict with keys: verified (bool), distance, threshold, model, detector,
                        person_id, message.

    Raises:
        DeepFaceServiceError: if microservice is unreachable or returns HTTP >= 400.
    """
    person_id = str(person_id).strip().lower()

    if isinstance(image_b64, str) and "," in image_b64 and image_b64.startswith("data:"):
        image_b64 = image_b64.split(",", 1)[1]

    url = f"{_get_base_url()}/registration/verify"
    payload = {
        "person_id": person_id,
        "image_base64": image_b64,
        "model": model,
    }

    try:
        resp = requests.post(url, json=payload, timeout=_TIMEOUT_VERIFY)
    except requests.exceptions.ConnectionError as exc:
        logger.error("[DeepFace] verify(%s) — microservice unreachable: %s", person_id, exc)
        raise DeepFaceServiceError(
            f"DeepFace microservice is unreachable at {_get_base_url()}. "
            "Ensure the service is running."
        ) from exc
    except requests.exceptions.Timeout as exc:
        logger.error("[DeepFace] verify(%s) — request timed out", person_id)
        raise DeepFaceServiceError("DeepFace verification request timed out.") from exc

    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text[:500]}

    if resp.status_code >= 400:
        msg = body.get("detail") or body.get("message") or str(body)
        logger.error("[DeepFace] verify(%s) HTTP %s: %s", person_id, resp.status_code, msg)
        raise DeepFaceServiceError(f"DeepFace verification failed for {person_id}: {msg}")

    logger.info(
        "[DeepFace] verify(%s) → verified=%s distance=%s",
        person_id,
        body.get("verified"),
        body.get("distance"),
    )
    return body


def df_is_registered(person_id: str) -> bool:
    """
    Check whether a face is already registered for person_id.

    Returns False (not True) if the microservice is unreachable, so callers
    can decide whether to proceed with registration or not.
    Raises DeepFaceServiceError only on hard connectivity failures if needed.

    This is a lightweight probe (no embedding computation).
    """
    person_id = str(person_id).strip().lower()
    url = f"{_get_base_url()}/registration/registered/{person_id}"

    try:
        resp = requests.get(url, timeout=_TIMEOUT_CHECK)
        if resp.status_code == 200:
            return resp.json().get("registered", False)
        return False
    except Exception as exc:
        logger.warning("[DeepFace] is_registered(%s) probe failed: %s", person_id, exc)
        raise DeepFaceServiceError(
            f"DeepFace microservice is unreachable at {_get_base_url()}."
        ) from exc


def df_get_photo_b64(person_id: str) -> str | None:
    """
    Fetch the registered face photo from the microservice and return as base64.
    Returns None if not found or microservice is down.
    """
    person_id = str(person_id).strip().lower()
    url = f"{_get_base_url()}/registration/registered/{person_id}/photo"
    try:
        import base64 as _b64
        resp = requests.get(url, timeout=_TIMEOUT_CHECK)
        if resp.status_code == 200 and resp.content:
            return _b64.b64encode(resp.content).decode("ascii")
    except Exception as exc:
        logger.warning("[DeepFace] get_photo(%s) failed: %s", person_id, exc)
    return None
