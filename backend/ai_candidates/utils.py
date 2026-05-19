from .models import PipelineLog
import logging

logger = logging.getLogger(__name__)

def log_automation_event(candidate, event_type, status, message, details=None, phase='GENERAL', batch_id=None):
    """
    Utility helper to create a PipelineLog entry for a candidate.
    """
    try:
        # Use provided batch_id or fallback to candidate's current batch_id
        effective_batch_id = batch_id or getattr(candidate, 'batch_id', None)
        
        PipelineLog.objects.create(
            candidate=candidate,
            event_type=event_type,
            status=status,
            phase=phase,
            batch_id=effective_batch_id,
            message=message,
            details=details or {}
        )
    except Exception as e:
        logger.error(f"Failed to create PipelineLog for candidate {candidate.id if candidate else 'unknown'}: {e}")


def _register_face_with_deepface(person_id, image_base64):
    """
    Push a base64-encoded face image to the DeepFace registration endpoint.

    This is used by the admin photo-approval flow (and legacy override paths)
    to overwrite the master face for a given person_id.

    Returns the parsed JSON response on success, or None on failure.
    """
    import requests
    from django.conf import settings

    # DEEPFACE_BASE_URL example: http://127.0.0.1:8500/api/v1
    base_url = getattr(settings, 'DEEPFACE_BASE_URL', None) or 'http://127.0.0.1:8500/api/v1'
    url = f"{base_url.rstrip('/')}/registration/register"

    person_id = str(person_id).strip().lower()
    payload = {
        'person_id': person_id,
        'image_base64': image_base64,
        'overwrite': True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        # Log the full response body so we can see exactly why DeepFace rejected.
        try:
            body = resp.json()
        except Exception:
            body = {'raw': resp.text[:500]}
        if resp.status_code >= 400:
            logger.error(
                f"[DeepFace] register({person_id}) HTTP {resp.status_code}: {body}"
            )
            return None
        logger.info(f"[DeepFace] register({person_id}) -> success={body.get('success')}")
        return body
    except Exception as e:
        logger.error(f"[DeepFace] register({person_id}) network/other error: {e}")
        return None


def _archive_session_photo(pan_number, public_token, image_b64, meta=None):
    """
    Archive a captured face photo under a per-session folder for audit.

    Layout (nested inside the DeepFace person folder):

      deepface/data/registered_faces/<pan>/
          face_0.jpg            — DeepFace master photo (volatile; overwritten on register)
          face_0.pkl            — DeepFace embedding (volatile)
          sessions/
              <token>/
                  face_0.jpg    — immutable per-interview snapshot
                  meta.json     — capture metadata (timestamp, mismatch flag, etc.)

    DeepFace's register-with-overwrite has been narrowed to only delete top-level
    files in the person folder, so the `sessions/` subtree is preserved across
    re-registrations and admin approvals.
    """
    import base64
    import json
    from pathlib import Path
    from django.conf import settings

    if not pan_number or not public_token or not image_b64:
        return None

    try:
        # Strip any data URL prefix
        if ',' in image_b64 and image_b64.startswith('data:'):
            image_b64 = image_b64.split(',', 1)[1]
        img_bytes = base64.b64decode(image_b64)
    except Exception as e:
        logger.error(f"[ArchivePhoto] Failed to decode image: {e}")
        return None

    pan_id = str(pan_number).strip().lower()
    token_id = str(public_token).strip().lower()

    # Resolve to deepface/data/registered_faces (sibling to the backend tree).
    deepface_root = Path(settings.BASE_DIR).resolve().parent / 'deepface' / 'data' / 'registered_faces'
    sessions_dir = deepface_root / pan_id / 'sessions' / token_id
    try:
        sessions_dir.mkdir(parents=True, exist_ok=True)
        img_path = sessions_dir / 'face_0.jpg'
        with open(img_path, 'wb') as f:
            f.write(img_bytes)
        if meta:
            try:
                with open(sessions_dir / 'meta.json', 'w', encoding='utf-8') as mf:
                    json.dump(meta, mf, indent=2, default=str)
            except Exception as meta_err:
                logger.warning(f"[ArchivePhoto] Could not write meta.json: {meta_err}")
        logger.info(f"[ArchivePhoto] Archived session photo to {img_path} ({len(img_bytes)} bytes)")
        return str(img_path)
    except Exception as e:
        logger.error(f"[ArchivePhoto] Failed to archive session photo: {e}")
        return None
