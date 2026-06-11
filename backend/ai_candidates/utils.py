from .models import PipelineLog
import logging
import re

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
    Push a base64-encoded face image to the DeepFace microservice.

    Delegates to the shared deepface_client.df_register so that all face
    registration across the backend goes through a single code path.

    Raises DeepFaceServiceError if the microservice is unreachable (hard-fail).
    Returns the parsed JSON response dict on success.
    """
    from api.deepface_client import df_register, DeepFaceServiceError  # noqa: F401
    return df_register(person_id, image_base64, overwrite=True)



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


def is_likely_code(text: str) -> bool:
    if not text:
        return False
    code_indicators = [
        r'\bdef\s+\w+\s*\(',      # Python def
        r'\bclass\s+\w+',          # Python/Java/JS class
        r'\bimport\s+\w+',         # Python/JS import
        r'^\s*return\b',           # Return statement
        r'#\s*include',            # C/C++ include
        r'std::',                  # C++ std
        r'public\s+static\s+void\s+main', # Java main
        r'System\.out\.print',     # Java print
        r'console\.log\s*\(',      # JS log
        r'const\s+\w+\s*=',        # JS const
        r'let\s+\w+\s*=',          # JS let
        r'function\s+\w+\s*\(',    # JS function
    ]
    # Check if any line has curly braces or semicolon or indicator pattern
    if '{' in text or '}' in text or ';' in text:
        return True
        
    lines = text.split('\n')
    indented_lines = sum(1 for line in lines if line.startswith('    ') or line.startswith('\t'))
    if len(lines) > 2 and indented_lines > 0:
        return True
        
    for pattern in code_indicators:
        if re.search(pattern, text, re.MULTILINE):
            return True
    return False


def clean_repetitive_text(text: str) -> str:
    """
    Clean up mechanical transcript repetitions where cumulative speech-to-text
    sends progressive overlapping segments.
    """
    if not text:
        return text
        
    if "[Candidate remained silent/skipped]" in text:
        return text
        
    if is_likely_code(text):
        return text

    # Normalise whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split by potential sentence/clause/phrase boundaries
    pattern = r'(?<=[,.!?])\s+|(?=\b(?:and|since|because|but|hello|my name is)\b)'
    segments = re.split(pattern, text, flags=re.IGNORECASE)
    
    cleaned_segments = []
    for s in segments:
        s_clean = s.strip()
        if s_clean:
            cleaned_segments.append(s_clean)
            
    def normalize_str(s):
        return re.sub(r'[^a-z0-9]', '', s.lower())
        
    final_segments = []
    for i, seg in enumerate(cleaned_segments):
        norm_seg = normalize_str(seg)
        # Skip very short segments to avoid discarding actual single letters/words
        if len(norm_seg) <= 2:
            final_segments.append(seg)
            continue
            
        subsumed = False
        for j in range(i + 1, len(cleaned_segments)):
            later_seg = cleaned_segments[j]
            norm_later = normalize_str(later_seg)
            if norm_seg in norm_later:
                subsumed = True
                break
        if not subsumed:
            final_segments.append(seg)
            
    # Reconstruct the cleaned text
    cleaned_text = " ".join(final_segments)
    cleaned_text = re.sub(r'\s+([,.!?])', r'\1', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text
