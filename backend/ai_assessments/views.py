import os
import uuid
import json
import random
import logging
import traceback
import copy
from datetime import datetime, timedelta
from ai_assessments.llm_client import create_llm_client, LLMKeyManager, get_default_model
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db import models
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

import io
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, PageBreak, HRFlowable, XPreformatted
)
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse

import uuid
from .models import Assessment, AIAssessmentSubmission, AIAssessmentIntegrityScreenshot
from ai_candidates.models import Candidate
from ai_candidates.views import extract_json
from .ai_logic import (
    _normalize_difficulty_label,
    _normalize_generated_pool,
    _mcq_difficulty_counts,
    _rebalance_mcq_difficulties,
    _repair_pool_shortfall,
    _generate_execution_verified_coding_pool,
    _generate_mcq_pool_ai_only,
    pick_random_subset,
    _expert_assessment_refiner,
    _validate_mcq_structure,
    GroqKeyManager
)

import traceback
import base64
from django.core.files.base import ContentFile
from api.models import UserProfile, DeletionRequest
from api._imports import _is_application_admin_email, handle_deletion_request
from api.utils.batch_utils import generate_batch_id, generate_batch_name
import requests
from api._imports import DEEPFACE_BASE_URL

from django.http import FileResponse, Http404

class ServeDeepFaceFaceView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    """
    Serve the registered face photo — uses IDENTICAL logic to the PDF report.
    PDF reads: deepface/data/registered_faces/{email}_{token}/face_0.jpg
    This view does the same, so result page and PDF always show the same photo.
    """
    def get(self, request, person_id):
        import logging
        logger = logging.getLogger(__name__)
        from pathlib import Path

        deepface_data_dir = Path(__file__).resolve().parent.parent.parent / 'deepface' / 'data' / 'registered_faces'
        person_face_dir = deepface_data_dir / person_id

        # Check if this person_id belongs to a fully automated assessment
        is_automatic = False
        try:
            from ai_assessments.models import AIAssessmentSubmission
            from django.db.models import Q
            if '/assessments/' in person_id:
                token = person_id.split('/assessments/')[-1]
                sub = AIAssessmentSubmission.objects.filter(assessment__share_token=token).first()
                if sub and sub.assessment and sub.assessment.creation_type == 'automatic':
                    is_automatic = True
            else:
                # Direct check by PAN or email token
                sub = AIAssessmentSubmission.objects.filter(
                    Q(pan_number__iexact=person_id) | 
                    Q(candidate_email__iexact=person_id.split('_')[0] if '_' in person_id else person_id)
                ).first()
                if sub and sub.assessment and sub.assessment.creation_type == 'automatic':
                    is_automatic = True
        except Exception as auto_err:
            logger.warning(f"Error checking is_automatic for ServeDeepFaceFaceView: {auto_err}")

        # For fully automated assessments, prioritize fetching via the DeepFace microservice API
        if is_automatic:
            try:
                from api._imports import DEEPFACE_BASE_URL
                import requests
                from django.http import HttpResponse
                
                df_url = f"{DEEPFACE_BASE_URL}/registration/registered/{person_id}/photo"
                resp = requests.get(df_url, timeout=5)
                if resp.status_code == 200:
                    logger.info(f"Serving registered face via DeepFace API for automatic assessment: {person_id}")
                    return HttpResponse(resp.content, content_type='image/jpeg')
            except Exception as e:
                logger.warning(f"ServeDeepFaceFaceView: DeepFace API proxy failed for {person_id}: {e}")

        # ── EXACT SAME LOGIC AS PDF (Manual Fallback / Legacy) ─────────────────
        target_file = None

        # Step 1: Check primary folder (email_token)
        if person_face_dir.exists():
            for name in ['face_0.jpg', 'registration_snapshot.jpg']:
                if (person_face_dir / name).exists():
                    target_file = person_face_dir / name
                    break
            if not target_file:
                jpgs = list(person_face_dir.glob('*.jpg'))
                if jpgs:
                    target_file = jpgs[0]

        # Step 2: Legacy email-only folder (strip token suffix)
        if not target_file and '_' in person_id:
            email_only = person_id.rsplit('_', 1)[0]
            legacy_dir = deepface_data_dir / email_only
            if legacy_dir.exists():
                for name in ['face_0.jpg', 'registration_snapshot.jpg']:
                    if (legacy_dir / name).exists():
                        target_file = legacy_dir / name
                        break
                if not target_file:
                    jpgs = list(legacy_dir.glob('*.jpg'))
                    if jpgs:
                        target_file = jpgs[0]

        # Step 3: IdentityLink DB (same as PDF final fallback)
        if not target_file:
            try:
                from api.models import IdentityLink
                from django.db.models import Q
                if '_' in person_id:
                    email_key = person_id.split('_')[0]
                    identity = IdentityLink.objects.filter(email__iexact=email_key).order_by('-updated_at').first()
                else:
                    identity = IdentityLink.objects.filter(
                        Q(pan_number__iexact=person_id) | Q(email__iexact=person_id)
                    ).order_by('-updated_at').first()
                if identity and identity.snapshot_image and identity.snapshot_image.name:
                    import os
                    if os.path.exists(identity.snapshot_image.path):
                        target_file = Path(identity.snapshot_image.path)
            except Exception as e:
                logger.warning(f"IdentityLink lookup failed for {person_id}: {e}")

        # ── SERVE THE FILE ───────────────────────────────────────────────────
        if target_file and target_file.exists():
            logger.info(f"Serving registered face: {target_file}")
            return FileResponse(open(target_file, 'rb'), content_type='image/jpeg')

        logger.warning(f"No registered face found for: {person_id}")
        raise Http404("No registered face found")

def _get_candidate_photo_url(request, submission):
    """
    Returns the registered face URL for this specific assessment only.
    Prioritizes checking the local registered face folder (on disk) first.
    Otherwise checks the unified IdentityLink for this candidate's email.
    Falls back to first non-empty webcam integrity screenshot if registration missing.
    """
    email = submission.candidate_email.lower().strip() if submission.candidate_email else None
    is_automatic = getattr(submission.assessment, 'creation_type', 'manual') == 'automatic' if getattr(submission, 'assessment', None) else False

    # Priority 0: DB-stored registered face (always the most recent verified photo for this specific assessment).
    db_photo = getattr(submission, 'original_identity_photo', None)
    if db_photo and len(db_photo) > 1000:
        if not db_photo.startswith('data:image'):
            return f"data:image/jpeg;base64,{db_photo}"
        return db_photo

    from pathlib import Path
    deepface_data_dir = Path(__file__).resolve().parent.parent.parent / 'deepface' / 'data' / 'registered_faces'

    # Priority 0.5: Historically accurate assessment-specific snapshot (Prevents later candidates with same PAN from overriding past exam photos)
    try:
        import base64
        token_str = str(submission.assessment.share_token) if getattr(submission, 'assessment', None) else None
        if token_str:
            p_id = getattr(submission, 'pan_number', '').lower().strip() or email or token_str
            for subfolder in ['standard_assessment', 'assessments', 'sessions']:
                session_dir = deepface_data_dir / p_id / subfolder / token_str
                for filename in ['registration_snapshot.jpg', 'face_0.jpg']:
                    target_snap_file = session_dir / filename
                    if target_snap_file.exists():
                        with open(target_snap_file, 'rb') as f:
                            return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"
                            
            # VM / Docker Deployment Fallback: Fetch from microservice over HTTP if not found on local disk
            try:
                from api._imports import DEEPFACE_BASE_URL
                import requests
                for subfolder in ['standard_assessment', 'assessments', 'sessions']:
                    resp = requests.get(f"{DEEPFACE_BASE_URL}/registration/registered/{p_id}/{subfolder}/{token_str}/photo", timeout=5)
                    if resp.status_code == 200:
                        return f"data:image/jpeg;base64,{base64.b64encode(resp.content).decode('utf-8')}"
            except Exception:
                pass
    except Exception:
        pass

    # Check via DeepFace API for fully automated assessments
    if is_automatic:
        try:
            from api._imports import DEEPFACE_BASE_URL
            import requests
            
            def _api_registered(pid):
                try:
                    resp = requests.get(f"{DEEPFACE_BASE_URL}/registration/registered/{pid}", timeout=2)
                    return resp.status_code == 200 and resp.json().get('registered', False)
                except Exception:
                    return False
                    
            if getattr(submission, 'pan_number', None):
                pan_id = submission.pan_number.lower().strip()
                if _api_registered(pan_id):
                    url_path = f"/api/ai/registration/face/{pan_id}/"
                    return request.build_absolute_uri(url_path) if request else url_path
                    
            if email:
                token = str(submission.assessment.share_token) if submission.assessment else None
                person_id = f"{email}_{token}" if token else email
                if _api_registered(person_id):
                    url_path = f"/api/ai/registration/face/{person_id}/"
                    return request.build_absolute_uri(url_path) if request else url_path
                    
                if token and _api_registered(email):
                    url_path = f"/api/ai/registration/face/{email}/"
                    return request.build_absolute_uri(url_path) if request else url_path
        except Exception as api_err:
            logger.warning(f"Error checking registration via API in _get_candidate_photo_url: {api_err}")

    from pathlib import Path
    deepface_data_dir = Path(__file__).resolve().parent.parent.parent / 'deepface' / 'data' / 'registered_faces'

    # Priority 1: Check if lowercased PAN number folder exists and has face images on disk (Manual / Fallback)
    if getattr(submission, 'pan_number', None):
        pan_id = submission.pan_number.lower().strip()
        pan_face_dir = deepface_data_dir / pan_id
        if pan_face_dir.exists() and any(pan_face_dir.rglob('*.jpg')):
            url_path = f"/api/ai/registration/face/{pan_id}/"
            return request.build_absolute_uri(url_path) if request else url_path

    # Priority 2: Check email_token folder on disk (Manual / Fallback)
    if email:
        token = str(submission.assessment.share_token) if submission.assessment else None
        person_id = f"{email}_{token}" if token else email
        person_face_dir = deepface_data_dir / person_id
        if person_face_dir.exists() and any(person_face_dir.rglob('*.jpg')):
            url_path = f"/api/ai/registration/face/{person_id}/"
            return request.build_absolute_uri(url_path) if request else url_path
            
        # Priority 3: Check plain email folder on disk (Manual / Fallback)
        if token:
            email_face_dir = deepface_data_dir / email
            if email_face_dir.exists() and any(email_face_dir.rglob('*.jpg')):
                url_path = f"/api/ai/registration/face/{email}/"
                return request.build_absolute_uri(url_path) if request else url_path

    # Priority 4: Check unified IdentityLink for registered face snapshot
    try:
        from api.models import IdentityLink
        import re
        pan = getattr(submission, 'pan_number', None)
        identity = None
        
        if pan:
            norm_pan = re.sub(r'[^A-Z0-9]', '', pan.strip().upper())
            if norm_pan:
                identity = IdentityLink.objects.filter(pan_number__iexact=norm_pan).order_by('-updated_at').first()
                
        if not identity and email:
            identity = IdentityLink.objects.filter(email__iexact=email).order_by('-updated_at').first()
            
        if identity and identity.snapshot_image and identity.snapshot_image.name:
            return request.build_absolute_uri(identity.snapshot_image.url) if request else identity.snapshot_image.url
    except Exception as e:
        logger.warning(f"Error checking IdentityLink in _get_candidate_photo_url: {e}")

    # Fallback: first non-empty webcam integrity screenshot (> 10KB = real face frame)
    try:
        from ai_assessments.models import AIAssessmentIntegrityScreenshot
        import os as _os
        snaps = AIAssessmentIntegrityScreenshot.objects.filter(
            submission=submission,
            webcam_screenshot__isnull=False
        ).exclude(
            event_type__icontains='face_not_detected'
        ).order_by('timestamp')
        for snap in snaps:
            if snap.webcam_screenshot and snap.webcam_screenshot.name:
                if _os.path.exists(snap.webcam_screenshot.path):
                    if _os.path.getsize(snap.webcam_screenshot.path) > 10000:
                        return request.build_absolute_uri(snap.webcam_screenshot.url)
    except Exception:
        pass

    # No photo found — return None so frontend shows placeholder
    return None

def _get_unified_identity_mismatch_fields(request, submission):
    """
    Returns unified identity mismatch fields for an assessment submission.
    If the submission itself doesn't have a mismatch, but the associated voice
    interview Candidate does, it bubbles up the Candidate's mismatch info.
    """
    def clean_b64(b64_str):
        if not b64_str:
            return None
        b64_str = b64_str.strip()
        if b64_str.startswith('identity_overrides/'):
            try:
                from django.conf import settings
                from pathlib import Path
                import base64
                file_path = Path(settings.MEDIA_ROOT) / b64_str
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        b64 = base64.b64encode(f.read()).decode('utf-8')
                        ext = b64_str.split('.')[-1].lower()
                        mime = "image/png" if ext == "png" else "image/jpeg"
                        return f"data:{mime};base64,{b64}"
            except Exception:
                pass
            return None
        if not b64_str.startswith('data:image'):
            return f"data:image/jpeg;base64,{b64_str}"
        return b64_str

    detected = getattr(submission, 'identity_mismatch_detected', False)
    has_severe = detected
    has_soft = False
    
    if not detected:
        from ai_assessments.models import AIAssessmentIntegrityScreenshot
        has_severe = AIAssessmentIntegrityScreenshot.objects.filter(
            submission=submission,
            event_type__in=["face_mismatch_on_reentry", "face_mismatch_override"]
        ).exists()
        
        has_soft = AIAssessmentIntegrityScreenshot.objects.filter(
            submission=submission,
            event_type__icontains="mismatch"
        ).exists()
    
    # Box 1 ("Registered Face" / "Original Candidate") must show the ROOT master face,
    # NOT the assessment-specific subfolder (which contains the intruder's face).
    orig_url = None
    pan_id = submission.pan_number.lower().strip() if getattr(submission, 'pan_number', None) else None
    
    try:
        from pathlib import Path
        import base64 as b64_mod
        deepface_data_dir = Path(__file__).resolve().parent.parent.parent / 'deepface' / 'data' / 'registered_faces'
        if pan_id:
            master_dir = deepface_data_dir / pan_id
            for fname in ['face_0.jpg', 'registration_snapshot.jpg']:
                master_file = master_dir / fname
                if master_file.exists():
                    with open(master_file, 'rb') as f:
                        orig_url = f"data:image/jpeg;base64,{b64_mod.b64encode(f.read()).decode('utf-8')}"
                    break
    except Exception:
        pass
        
    # VM / Docker Deployment Fallback: Fetch from microservice over HTTP if not found on local disk
    if not orig_url and pan_id:
        try:
            from api._imports import DEEPFACE_BASE_URL
            import requests
            import base64 as b64_mod
            resp = requests.get(f"{DEEPFACE_BASE_URL}/registration/registered/{pan_id}/photo", timeout=5)
            if resp.status_code == 200:
                orig_url = f"data:image/jpeg;base64,{b64_mod.b64encode(resp.content).decode('utf-8')}"
        except Exception:
            pass

    if not orig_url:
        orig_url = clean_b64(submission.original_identity_photo)
    
    # Fetch Box 2 ("Intruder Photo" / "Person During Assessment")
    # Priority 1: The assessment-specific folder in DeepFace
    # Priority 2: DeepFace microservice HTTP API
    # Priority 3: The database intruder_photo field
    df_intruder_url = None
    try:
        from pathlib import Path
        from django.conf import settings
        import base64
        deepface_data_dir = Path(settings.BASE_DIR).parent / 'deepface' / 'data' / 'registered_faces'
        p_id = submission.pan_number.lower().strip() if getattr(submission, 'pan_number', None) else f"{submission.candidate_email.lower().strip()}_{submission.assessment.share_token}"
        
        # Check both standard_assessment and assessments
        session_dir = deepface_data_dir / p_id / 'standard_assessment' / str(submission.assessment.share_token)
        if not session_dir.exists():
            session_dir = deepface_data_dir / p_id / 'assessments' / str(submission.assessment.share_token)
        
        target_snap_file = None
        for candidate_name in ['registration_snapshot.jpg', 'face_0.jpg']:
            possible = session_dir / candidate_name
            if possible.exists():
                target_snap_file = possible
                break
                
        if not target_snap_file and session_dir.exists():
            for jpg_file in session_dir.glob('*.jpg'):
                target_snap_file = jpg_file
                break
        
        if target_snap_file and target_snap_file.exists():
            with open(target_snap_file, 'rb') as f:
                df_intruder_url = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    except Exception:
        pass

    intruder_url = df_intruder_url
    
    is_automatic = getattr(submission.assessment, 'creation_type', 'manual') == 'automatic' if getattr(submission, 'assessment', None) else False
    if not intruder_url and is_automatic:
        try:
            from api._imports import DEEPFACE_BASE_URL
            import requests
            import base64
            p_id = submission.pan_number.lower().strip() if getattr(submission, 'pan_number', None) else f"{submission.candidate_email.lower().strip()}_{submission.assessment.share_token}"
            df_url = f"{DEEPFACE_BASE_URL}/registration/registered/{p_id}/standard_assessment/{submission.assessment.share_token}/photo"
            resp = requests.get(df_url, timeout=5)
            if resp.status_code == 200:
                intruder_url = f"data:image/jpeg;base64,{base64.b64encode(resp.content).decode('utf-8')}"
        except Exception as e:
            logger.warning(f"Failed to fetch assessment photo from DeepFace API: {e}")

    if not intruder_url:
        intruder_url = clean_b64(getattr(submission, 'intruder_photo', None))

    if not intruder_url and detected:
        try:
            from ai_assessments.models import AIAssessmentIntegrityScreenshot
            snap = AIAssessmentIntegrityScreenshot.objects.filter(
                submission=submission,
                event_type__icontains="mismatch"
            ).order_by('id').first()
            if snap:
                photo_field = snap.webcam_screenshot or snap.screenshot
                if photo_field:
                    try:
                        import base64 as b64_mod
                        with open(photo_field.path, 'rb') as f:
                            intruder_url = f"data:image/jpeg;base64,{b64_mod.b64encode(f.read()).decode('utf-8')}"
                    except Exception:
                        intruder_url = request.build_absolute_uri(photo_field.url) if request else photo_field.url
        except Exception:
            pass
        
    details = getattr(submission, 'identity_mismatch_details', {})

    if not detected and submission.candidate_email:
        try:
            # If the photo was explicitly approved for this assessment, do NOT bubble up the mismatch from Candidate
            is_approved = details.get('photo_update_approved', False) if isinstance(details, dict) else False
            if not is_approved:
                from ai_candidates.models import Candidate
                from ai_assessments.results_helpers import _get_candidate_intruder_photo_url
                cand = Candidate.objects.filter(email__iexact=submission.candidate_email).order_by('-id').first()
                if cand and getattr(cand, 'identity_mismatch_detected', False):
                    detected = True
                    details = getattr(cand, 'identity_mismatch_details', {})
                if getattr(cand, 'original_identity_photo', None):
                    try:
                        orig_url = request.build_absolute_uri(cand.original_identity_photo.url)
                    except Exception:
                        pass
                
                intr_url = _get_candidate_intruder_photo_url(cand)
                if intr_url:
                    intruder_url = intr_url
        except Exception as e:
            pass

    # For fresh PAN cards (first-ever submission with that PAN), skip photo_update_pending
    # because there is no prior registered face to "update" from.
    is_fresh_pan = False
    try:
        pan = (getattr(submission, 'pan_number', '') or '').strip()
        if pan:
            from django.db.models import Min
            earliest_id = AIAssessmentSubmission.objects.filter(
                pan_number__iexact=pan
            ).aggregate(first_id=Min('id'))['first_id']
            is_fresh_pan = (earliest_id == submission.id)
    except Exception:
        pass

    # Hide the red alert triangle for fresh PAN cards ONLY if it's a soft mismatch.
    # If they actually swapped faces during their first exam, still flag it!
    if is_fresh_pan:
        detected = has_severe
    else:
        detected = has_severe or has_soft

    return {
        "identity_mismatch_detected": detected,
        "original_identity_photo_url": orig_url,
        "intruder_photo_url": intruder_url,
        "identity_mismatch_details": details,
        "photo_update_pending": bool(detected and intruder_url and not is_fresh_pan),
        "photo_update_approved": bool(details.get('photo_update_approved', False)) if isinstance(details, dict) else False,
        "pending_identity_photo_url": intruder_url,
        "master_photo_url": orig_url,
        "is_assessment": True,
        "ai_candidate_pk": submission.id,
    }

logger = logging.getLogger(__name__)
MAX_CODING_TASKS = 50

from api.views.job_role_views import ensure_role_exists

# Configure Groq
# groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
# if not groq_api_key:
#     raise ValueError("GROQ_API_KEY must be set in settings.py")
# LLM client is now created via create_llm_client() from llm_client.py


# Redundant helper removed. New version is at the top of the file.
        

class SubmitAssessmentView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        data = request.data
        token = data.get('token')
        name = data.get('name')
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '')
        pan_number = data.get('pan_number', '')
        pan_photo = request.FILES.get('pan_photo')
        pan_verified_raw = data.get('pan_verified', False)
        # Handle string 'true'/'false' from FormData
        if isinstance(pan_verified_raw, str):
            pan_verified = pan_verified_raw.lower() == 'true'
        else:
            pan_verified = bool(pan_verified_raw)
        # Parse JSON strings from FormData
        answers_raw = data.get('answers', '{}')
        coding_results_raw = data.get('coding_results', '{}')
        try:
            import json
            answers = json.loads(answers_raw) if isinstance(answers_raw, str) else answers_raw
            coding_results = json.loads(coding_results_raw) if isinstance(coding_results_raw, str) else coding_results_raw
        except json.JSONDecodeError:
            answers = {}
            coding_results = {}

        if not token or not name or not email:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assessment = Assessment.objects.get(share_token=token)
            
            # Absolute block against submitting multiple times
            if AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                submitted_at__isnull=False
            ).exists():
                return Response(
                    {"error": "You have already completed this assessment and cannot retake it."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            submission = AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                status='ONGOING'
            ).order_by('-id').first()

            if not submission:
                submission = AIAssessmentSubmission.objects.create(
                    assessment=assessment,
                    candidate_name=name,
                    candidate_email=email,
                    phone=phone,
                    pan_number=pan_number,
                    pan_photo=pan_photo,
                    pan_verified=pan_verified,
                    status='ONGOING',
                    batch_id=assessment.batch_id,
                    batch_name=assessment.batch_name
                )
            else:
                # If the candidate provided a real name to override an auto-generated one (like "Extraction Failed"), update it
                if name and submission.candidate_name != name:
                    submission.candidate_name = name
                    # Also update email if it was overridden
                    if email and submission.candidate_email != email:
                        submission.candidate_email = email
                # Update PAN details if provided
                if phone:
                    submission.phone = phone
                if pan_number:
                    submission.pan_number = pan_number
                if pan_photo:
                    submission.pan_photo = pan_photo
                submission.pan_verified = pan_verified

                # CROSS-UPDATE: Synchronize with the Candidate record if exists
                try:
                    candidate = Candidate.objects.filter(email__iexact=email).first()
                    if candidate:
                        if name and (candidate.full_name == "Extraction Failed" or candidate.full_name != name):
                            candidate.full_name = name
                            candidate.save(update_fields=['full_name'])
                except Exception as sync_err:
                    logger.warning(f"Failed to cross-update candidate {email}: {sync_err}")

            # Use candidate_questions (the subset) instead of the whole pool
            generated_content = submission.candidate_questions or assessment.generated_content or {}
            
            # Unwrap historic nested dictionaries from Llama-3.1
            if 'mcqs' not in generated_content and 'coding_challenges' not in generated_content:
                for key, val in generated_content.items():
                    if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                        generated_content = val
                        break

            generated_content = _normalize_generated_pool(generated_content)
            mcqs = generated_content.get('mcqs', [])
            coding_challenges = generated_content.get('coding_challenges', [])
            
            total_possible_points = 0
            candidate_total_points = 0
            
            # Difficulty weight multipliers (matches user requirement: Easy=1x, Medium=2x, Hard=3x)
            # Base points = 100 per question
            weight_map = {'Easy': 100, 'Medium': 200, 'Hard': 300}

            import re
            def clean_ans(s):
                if not s: return ""
                # Strip common choice prefixes like "a) ", "1. ", "Choice A: "
                return re.sub(r'^(?:choice\s+)?[a-z0-9][\.\)\:\s-]+\s*', '', s.lower()).strip()

            # 1. MCQ Scoring - 1 point each
            possible_mcq_points = 0
            candidate_mcq_points = 0
            for i, mcq in enumerate(mcqs):
                weight = 1  # 1 point per MCQ question
                possible_mcq_points += weight
                
                correct_ans = str(mcq.get('answer') or mcq.get('correct_answer') or '').strip()
                candidate_ans = str(answers.get(f'mcq_{i}') or '').strip()
                
                if correct_ans and clean_ans(candidate_ans) == clean_ans(correct_ans):
                    candidate_mcq_points += weight

            # 2. Coding Challenge Scoring - Weighted (100, 200, 300)
            possible_coding_points = 0
            candidate_coding_points = 0
            for i, challenge in enumerate(coding_challenges):
                difficulty = challenge.get('difficulty', 'Medium')
                weight = weight_map.get(difficulty, 200)
                possible_coding_points += weight
                
                res = coding_results.get(str(i))
                if res:
                    passed = res.get('passed', 0)
                    total_tc = res.get('total', 1) 
                    if total_tc > 0:
                        score_fraction = passed / total_tc
                        candidate_coding_points += (score_fraction * weight)

            # ---------------------------------------------------------
            # FINAL WEIGHTED SCORING (configurable MCQ% / Coding%)
            # Defaults to 40% MCQ / 60% Coding if not set
            # ---------------------------------------------------------
            mcq_w = (getattr(assessment, 'mcq_weight', 40) or 40) / 100
            coding_w = 1 - mcq_w

            # Calculate individual percentages
            mcq_percentage = (candidate_mcq_points / possible_mcq_points * 100) if possible_mcq_points > 0 else 0
            coding_percentage = (candidate_coding_points / possible_coding_points * 100) if possible_coding_points > 0 else 0
            
            # Aggregate based on weightage
            if possible_mcq_points > 0 and possible_coding_points > 0:
                percentage = round((mcq_percentage * mcq_w) + (coding_percentage * coding_w))
            elif possible_mcq_points > 0:
                # 100% MCQ if no coding challenges are present
                percentage = round(mcq_percentage)
            elif possible_coding_points > 0:
                # 100% Coding if no MCQs are present
                percentage = round(coding_percentage)
            else:
                percentage = 0

            # --- PASS/FAIL LOGIC ---
            # Only the configurable pass_threshold determines score-based pass/fail.
            # Integrity check (proctoring) AND identity verification are additional gates.
            INTEGRITY_HOLD_THRESHOLD = 50.0  # Below this = HOLD if score passed

            # CRITICAL: Re-read the LATEST integrity data from DB to avoid race condition.
            # The submission object was loaded at the start of this view, but integrity violations
            # may have been recorded by UpdateAssessmentIntegrityView AFTER we loaded it.
            fresh_data = AIAssessmentSubmission.objects.filter(pk=submission.pk).values(
                'integrity_score', 'identity_mismatch_detected'
            ).first()
            if fresh_data:
                submission.integrity_score = fresh_data['integrity_score']
                submission.identity_mismatch_detected = fresh_data['identity_mismatch_detected']

            passed_overall = percentage >= assessment.pass_threshold
            passed_integrity = submission.integrity_score >= INTEGRITY_HOLD_THRESHOLD
            has_identity_mismatch = getattr(submission, 'identity_mismatch_detected', False)
            try:
                from api.models import CandidateDetails
                details = CandidateDetails.objects.filter(token=submission.invitation.token).first()
                if details:
                    if details.identity_mismatch_detected or details.photo_update_status == 'pending':
                        has_identity_mismatch = True
            except Exception as e:
                logger.error(f"Error checking CandidateDetails in SubmitAssessment: {e}")

            # Selection Logic:
            # 1. Final Score < pass_threshold -> REJECTED
            # 2. Final Score >= pass_threshold + (Integrity < 50% OR Identity Mismatch) -> HOLD (manual review)
            # 3. Final Score >= pass_threshold + Integrity >= 50% + No Identity Mismatch -> SELECTED

            if not passed_overall:
                pass_status = 'rejected'
            elif not passed_integrity or has_identity_mismatch:
                pass_status = 'hold'  # Passed score but failed integrity/identity - needs admin review
            else:
                pass_status = 'selected'

            submission.answers = answers
            submission.mcq_score = round(mcq_percentage) # Store % for internal tracking
            submission.coding_score = round(coding_percentage) # Store % for internal tracking
            submission.score = percentage 
            submission.total_questions = len(mcqs) + len(coding_challenges)
            submission.percentage = percentage
            submission.status = pass_status
            submission.results_breakdown = {
                "mcq": {
                    "scored_points": round(candidate_mcq_points), 
                    "possible_points": possible_mcq_points,
                    "accuracy": f"{int(mcq_percentage)}%",
                    "weight": f"{round(mcq_w * 100)}%"
                },
                "coding": {
                    "scored_points": round(candidate_coding_points), 
                    "possible_points": possible_coding_points,
                    "accuracy": f"{int(coding_percentage)}%",
                    "weight": f"{round(coding_w * 100)}%"
                },
                "coding_results": coding_results,
                "weighted_final": f"{percentage}%"
            }
            submission.submitted_at = timezone.now()
            # Use update_fields to avoid overwriting integrity_score/monitoring data
            # that may be concurrently updated by UpdateAssessmentIntegrityView
            submission.save(update_fields=[
                'answers', 'mcq_score', 'coding_score', 'score',
                'total_questions', 'percentage', 'status',
                'results_breakdown', 'submitted_at',
                'integrity_score', 'identity_mismatch_detected',
            ])

            # POST-SAVE INTEGRITY CORRECTION:
            # Violations can arrive slightly after submit (race condition).
            # Wait briefly then re-read integrity and correct status if needed.
            import time as _time
            _time.sleep(0.5)
            final_integrity = AIAssessmentSubmission.objects.filter(pk=submission.pk).values('integrity_score', 'identity_mismatch_detected').first()
            if final_integrity:
                final_int_score = final_integrity['integrity_score'] or 100.0
                final_mismatch = final_integrity['identity_mismatch_detected']
                # If integrity dropped below threshold after we set status=selected, correct to hold
                if pass_status == 'selected' and (final_int_score < INTEGRITY_HOLD_THRESHOLD or final_mismatch):
                    AIAssessmentSubmission.objects.filter(pk=submission.pk).update(
                        status='hold',
                        integrity_score=final_int_score
                    )
                    pass_status = 'hold'
                    submission.status = 'hold'
                    submission.integrity_score = final_int_score
                    logger.warning(
                        f"SubmitAssessment: Status corrected to HOLD for submission {submission.pk} "
                        f"(integrity={final_int_score}%, mismatch={final_mismatch}) after post-save re-check."
                    )

            # CROSS-UPDATE: Synchronize with the Candidate record
            try:
                # Use iexact and prioritize the same batch if possible
                candidates = Candidate.objects.filter(email__iexact=email).order_by('-id')
                candidate = candidates.filter(batch_id=assessment.batch_id).first()

                if candidate:
                    logger.info(f"SubmitAssessment: Updating candidate {candidate.id} results for {email} (Submission ID={submission.id})")
                    candidate.score = percentage
                    
                    # Set correct status based on pass/fail/hold
                    if pass_status == 'selected':
                        candidate.status = 'Assessment Passed'
                        logger.info(f"SubmitAssessment: Candidate {email} PASSED assessment with {percentage}% - status updated to 'Assessment Passed'")
                    elif pass_status == 'hold':
                        candidate.status = 'Assessment On Hold'
                        logger.info(f"SubmitAssessment: Candidate {email} ON HOLD (integrity={submission.integrity_score}%, mismatch={getattr(submission, 'identity_mismatch_detected', False)}) - requires admin review")
                    else:
                        candidate.status = 'Assessment Failed'
                        logger.info(f"SubmitAssessment: Candidate {email} FAILED assessment with {percentage}% - status updated to 'Assessment Failed'")
                    
                    candidate.save(update_fields=['score', 'status'])
                    
                    # ── TRIGGER NEXT STAGE ──
                    # Only trigger interview pipeline for AUTOMATIC assessments.
                    # For MANUAL assessments, passing = qualified only — HR reviews and decides next step.
                    is_automatic = getattr(assessment, 'creation_type', 'manual') == 'automatic'
                    if pass_status == 'selected' and is_automatic:
                        logger.info(f"SubmitAssessment: Candidate {email} PASSED automatic assessment, triggering interview invitation for submission {submission.id}")
                        try:
                            from api.pipeline import process_assessment_passed
                            process_assessment_passed(submission.id)
                            logger.info(f"SubmitAssessment: Successfully triggered interview invitation for {email}")
                        except Exception as pipe_err:
                            logger.error(f"Pipeline Automation Error: Failed to trigger interview for {email}: {pipe_err}")
                            import traceback
                            logger.error(traceback.format_exc())
                    elif pass_status == 'selected' and not is_automatic:
                        logger.info(f"SubmitAssessment: Candidate {email} PASSED manual assessment — marked as qualified, no interview auto-sent.")
                    else:
                        logger.info(f"SubmitAssessment: Candidate {email} status={pass_status}, score={percentage}% — NOT triggering interview")

                else:
                    logger.info(f"SubmitAssessment: No matching Candidate record found for {email} to update results.")

                    # ── TRIGGER NEXT STAGE ──
                    # Only trigger interview pipeline for AUTOMATIC assessments.
                    # For MANUAL assessments, passing = qualified only — HR reviews and decides next step.
                    is_automatic = getattr(assessment, 'creation_type', 'manual') == 'automatic'
                    if pass_status == 'selected' and is_automatic:
                        logger.info(f"SubmitAssessment: Candidate {email} PASSED automatic assessment, triggering interview invitation for submission {submission.id}")
                        try:
                            from api.pipeline import process_assessment_passed
                            process_assessment_passed(submission.id)
                            logger.info(f"SubmitAssessment: Successfully triggered interview invitation for {email}")
                        except Exception as pipe_err:
                            logger.error(f"Pipeline Automation Error: Failed to trigger interview for {email}: {pipe_err}")
                            import traceback
                            logger.error(traceback.format_exc())
                    elif pass_status == 'selected' and not is_automatic:
                        logger.info(f"SubmitAssessment: Candidate {email} PASSED manual assessment — marked as qualified, no interview auto-sent.")
                    else:
                        logger.info(f"SubmitAssessment: Candidate {email} status={pass_status}, score={percentage}% — NOT triggering interview")

            except Exception as sync_err:
                logger.warning(f"Failed to cross-update candidate {email}: {sync_err}")

            response_data = {
                "message": "Assessment submitted successfully",
                "submission_id": submission.id,
                "final_score": percentage,
                "mcq_score": int(mcq_percentage),
                "coding_score": int(coding_percentage),
                "weightage": "40/60 (MCQ/Coding)",
                "status": pass_status,
                "display_percentage": f"{percentage}%"
            }
            response = Response(response_data, status=status.HTTP_200_OK)
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response

        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"SUMBISSION ERROR: {str(e)}\n{traceback.format_exc()}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CancelGenerationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            # sendBeacon might send raw text or JSON
            if request.content_type == 'text/plain':
                data = json.loads(request.body)
            else:
                data = request.data
            token = data.get('cancel_token') or data.get('token')
            if token:
                logger.warning(f"Frontend sent abort signal for generation token: {token}")
                cache.set(f"abort_{token}", True, timeout=300)
                return Response({"status": "aborted"})
            return Response({"error": "No token"}, status=400)
        except Exception as e:
            logger.error(f"Cancel error: {e}")
            return Response({"error": "Invalid format"}, status=400)

class GenerateAssessmentView(APIView):
    PRIMARY_MODEL = get_default_model()
    FALLBACK_MODEL = get_default_model()
    _fallback_until = 0

    def post(self, request):
        data = request.data
        job_description = data.get('job_description')
        required_skills = data.get('required_skills')
        experience_level = data.get('experience_level')  # NEW: Capture experience level
        cancel_token = data.get('cancel_token')
        
        # Robust Question Count Extraction
        # 1. MCQs: Priority to Granular (if they have non-zero sum) > Total count
        input_mcq_total = int(data.get('mcq_count', 0))
        input_easy = int(data.get('mcq_easy', 0))
        input_medium = int(data.get('mcq_medium', 0))
        input_hard = int(data.get('mcq_hard', 0))
        
        granular_sum = input_easy + input_medium + input_hard
        
        # Check if mcq_count or granular fields were explicitly provided
        mcq_count_provided = 'mcq_count' in data
        mcq_granular_provided = 'mcq_easy' in data or 'mcq_medium' in data or 'mcq_hard' in data
        
        if granular_sum > 0:
            mcq_count = granular_sum
            mcq_easy = input_easy
            mcq_medium = input_medium
            mcq_hard = input_hard
        elif input_mcq_total > 0:
            mcq_count = input_mcq_total
            mcq_easy = mcq_count // 2
            mcq_medium = (mcq_count * 3) // 10
            mcq_hard = max(0, mcq_count - mcq_easy - mcq_medium)
        elif mcq_count_provided and input_mcq_total == 0:
            # User explicitly set 0 MCQs via mcq_count field
            mcq_count = 0
            mcq_easy = 0
            mcq_medium = 0
            mcq_hard = 0
        elif mcq_granular_provided and granular_sum == 0:
            # User explicitly set 0 MCQs via all granular fields being 0
            mcq_count = 0
            mcq_easy = 0
            mcq_medium = 0
            mcq_hard = 0
        else:
            # Absolute default fallback (only when not explicitly provided)
            mcq_count = 10
            mcq_easy = 5
            mcq_medium = 3
            mcq_hard = 2

        # 2. Coding Challenges: Priority to Non-Empty coding_tasks > coding_count
        input_coding_count = int(data.get('coding_count', 0))
        input_coding_count = max(0, min(input_coding_count, MAX_CODING_TASKS))
        coding_tasks = data.get('coding_tasks', [])
        
        if isinstance(coding_tasks, str) and coding_tasks:
            try:
                coding_tasks = json.loads(coding_tasks)
            except:
                coding_tasks = []

        if isinstance(coding_tasks, list):
            coding_tasks = coding_tasks[:MAX_CODING_TASKS]

        if isinstance(coding_tasks, list) and len(coding_tasks) > 0:
            coding_count = len(coding_tasks)
        elif input_coding_count > 0:
            coding_count = input_coding_count
            coding_tasks = ['Medium'] * coding_count
        else:
            # Respect user's coding_count=0 - don't force a default
            coding_count = 0
            coding_tasks = []

        # Log for debugging
        logger.info(f"Generated Assessment Config: MCQs={mcq_count} ({mcq_easy}/{mcq_medium}/{mcq_hard}), Coding={coding_count} ({coding_tasks})")
        
        # Parse separate MCQ and Coding durations
        mcq_duration = int(data.get('mcq_duration', mcq_count))  # Default: 1 min per MCQ
        coding_duration = int(data.get('coding_duration', 30))    # Default: 30 min
        
        if mcq_count == 0:
            mcq_duration = 0
        if coding_count == 0:
            coding_duration = 0
            
        if coding_count > 0 and coding_duration <= 0:
            return Response({
                "error": "Invalid Duration",
                "message": "Coding Assessment Duration must be greater than 0 minutes."
            }, status=status.HTTP_400_BAD_REQUEST)

        if mcq_count > 0 and mcq_duration <= 0:
            return Response({
                "error": "Invalid Duration",
                "message": "MCQ Assessment Duration must be greater than 0 minutes."
            }, status=status.HTTP_400_BAD_REQUEST)

        duration = mcq_duration + coding_duration  # Total for backward compat
        total_possible_points = int(data.get('total_possible_points', 1000))

        if not job_description or not required_skills:
            return Response({
                "error": "Missing job_description or required_skills",
                "message": "Both fields are required to generate an assessment."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Date Validations
        from dateutil import parser
        from django.utils import timezone
        import datetime
        
        available_from_str = data.get('available_from')
        available_until_str = data.get('available_until')
        
        if available_from_str and available_until_str:
            try:
                av_from = parser.isoparse(available_from_str)
                av_until = parser.isoparse(available_until_str)
                now = timezone.now()
                
                # Allow a 5-minute grace period for network latency and processing time
                if av_from < now - datetime.timedelta(minutes=5):
                    return Response({
                        "error": "Invalid Timing", 
                        "message": "Assessment 'Available From' timing cannot be in the past."
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
                if av_until <= av_from:
                    return Response({
                        "error": "Invalid Timing", 
                        "message": "Assessment 'Available Until' must be strictly after 'Available From'."
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Date parsing error: {e}")
                return Response({
                    "error": "Invalid Date Format", 
                    "message": "Could not parse the provided dates."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Log experience level for debugging
        if experience_level:
            logger.info(f"Generating assessment for experience level: {experience_level}")

        if mcq_count == 0 and coding_count == 0:
            return Response({
                "error": "Assessment cannot be empty",
                "message": "Please select at least one MCQ question or one Coding task."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Auto-persist role if title is provided
            # required_skills often contains the role title in this app's context
            job_title = data.get('job_title') or data.get('role_title') or required_skills
            if job_title:
                ensure_role_exists(job_title, job_description, user=request.user)
            
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None

            # Read new flag
            same_questions_for_all = bool(data.get('same_questions_for_all', False))
            num_applicants = int(data.get('num_applicants', 0)) or 1

            # Case 1: Single candidate — generate exactly required count (1x)
            # Case 3: Same questions for all — generate exactly required count (1x)
            # Case 2: Multiple candidates, unique — generate num_applicants * required_count
            if num_applicants <= 1 or same_questions_for_all:
                pool_multiplier = 1
            else:
                pool_multiplier = num_applicants

            pool_easy = mcq_easy * pool_multiplier
            pool_medium = mcq_medium * pool_multiplier
            pool_hard = mcq_hard * pool_multiplier
            pool_mcq_total = pool_easy + pool_medium + pool_hard
            pool_coding_total = coding_count * pool_multiplier
            pool_coding_tasks = coding_tasks * pool_multiplier

            logger.info(f"Dispatching Assessment Generation (Case {'3' if same_questions_for_all else ('1' if num_applicants <= 1 else '2')}) for {num_applicants} applicants: Multiplier={pool_multiplier}")

            params_dict = {
                'job_description': job_description,
                'required_skills': required_skills,
                'experience_level': experience_level,
                'cancel_token': cancel_token,
                'mcq_count': mcq_count,
                'mcq_easy': mcq_easy,
                'mcq_medium': mcq_medium,
                'mcq_hard': mcq_hard,
                'coding_count': coding_count,
                'coding_tasks': coding_tasks,
                'mcq_duration': mcq_duration,
                'coding_duration': coding_duration,
                'duration': duration,
                'total_possible_points': total_possible_points,
                'num_applicants': num_applicants,
                'same_questions_for_all': same_questions_for_all,
                'mcq_weight': int(data.get('mcq_weight', 40)),
                'available_from': data.get('available_from'),
                'available_until': data.get('available_until'),
                'pass_threshold': max(10, int(data.get('pass_threshold', 60))),
                'user_profile_id': user_profile.id if user_profile else None,
                'company_id': company.id if company else None,
                'job_title': job_title,
                'pool_easy': pool_easy,
                'pool_medium': pool_medium,
                'pool_hard': pool_hard,
                'pool_mcq_total': pool_mcq_total,
                'pool_coding_total': pool_coding_total,
                'pool_coding_tasks': pool_coding_tasks
            }
            
            from ai_assessments.tasks import generate_assessment_task

            # Credit deduction: (0.5 per MCQ + 6 per coding) × num_applicants
            # If same_questions_for_all is True, don't multiply by applicants
            base_credit_cost = max(1, int((mcq_count * 0.5) + (coding_count * 6)))
            same_q_for_all = str(data.get('same_questions_for_all', 'false')).lower() == 'true'
            num_applicants = max(1, int(data.get('num_applicants', 1)))
            credit_cost = base_credit_cost if same_q_for_all else base_credit_cost * num_applicants

            user_profile = getattr(request.user, 'profile', None)
            if user_profile:
                if (user_profile.ai_credits or 0) < credit_cost:
                    return Response({
                        "error": f"Insufficient credits. You need {credit_cost} credits ({mcq_count} MCQs + {coding_count} Coding{'' if same_q_for_all else f' × {num_applicants} applicants'}) but have {user_profile.ai_credits or 0}. Please add credits from your wallet."
                    }, status=status.HTTP_402_PAYMENT_REQUIRED)
                user_profile.ai_credits = (user_profile.ai_credits or 0) - credit_cost
                user_profile.save(update_fields=['ai_credits'])
                from api.models import CreditTransaction
                CreditTransaction.objects.create(
                    user_profile=user_profile,
                    transaction_type=CreditTransaction.TYPE_USED,
                    amount=credit_cost,
                    balance_after=user_profile.ai_credits,
                    description=f"AI Assessment ({mcq_count} MCQs + {coding_count} Coding{'' if same_q_for_all else f' × {num_applicants}'})",
                )

            task = generate_assessment_task.delay(params_dict)
            
            return Response({
                "task_id": task.id,
                "status": "processing",
                "message": "Assessment generation started in the background"
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"ERROR starting GenerateAssessment task: {str(e)}\n{tb}")
            return Response({"error": str(e), "message": "Failed to start assessment generation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerationStatusView(APIView):
    """
    Check the status of an async assessment generation task.
    """
    def get(self, request, task_id):
        from celery.result import AsyncResult
        from django.core.cache import cache

        result = AsyncResult(task_id)
        progress_data = cache.get(f"gen_progress_{task_id}") or {}
        
        # Check if the task has a successful result
        if result.ready():
            if result.successful():
                task_result = result.get()
                if task_result.get('status') == 'completed':
                    return Response({
                        "status": "completed",
                        "assessment_id": task_result.get('assessment_id'),
                        "message": task_result.get('message'),
                        "progress": "Assessment generated successfully!"
                    })
                else:
                    return Response({
                        "status": "failed",
                        "error": task_result.get('error', 'Unknown error'),
                        "message": task_result.get('message', 'Generation failed.')
                    })
            else:
                return Response({
                    "status": "failed",
                    "error": str(result.result),
                    "message": "The generation task encountered a critical error."
                })

        # Task is still running or pending
        current_step = progress_data.get('step', 0)
        total_steps = progress_data.get('total_steps', 8)
        message = progress_data.get('message', "Initializing generation task...")

        return Response({
            "status": "processing",
            "progress": message,
            "step": current_step,
            "total_steps": total_steps
        })


def _register_face_with_deepface(person_id, snapshot_b64, overwrite=False):
    """
    Register/update a candidate's face in the DeepFace microservice.

    Delegates to the shared deepface_client.df_register so all face
    registration in the backend flows through a single code path.

    Raises DeepFaceServiceError if the microservice is unreachable (hard-fail).
    """
    from api.deepface_client import df_register
    return df_register(person_id, snapshot_b64, overwrite=overwrite)


def _verify_face_with_deepface_microservice(person_id, snapshot_b64):
    """
    Verify the candidate's face during re-entry via the DeepFace microservice.

    Delegates to the shared deepface_client.df_verify so all face verification
    in the backend flows through a single code path.

    Raises DeepFaceServiceError if the microservice is unreachable (hard-fail).
    """
    from api.deepface_client import df_verify
    result = df_verify(person_id, snapshot_b64)
    return result.get('verified', False)


class CreateSubmissionView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        token = request.data.get('share_token')
        name = request.data.get('candidate_name')
        email = request.data.get('candidate_email', '').strip().lower()
        snapshot = request.data.get('snapshot')
        phone = request.data.get('phone', '')
        pan_number = request.data.get('pan_number', '')
        pan_photo = request.FILES.get('pan_photo')
        pan_verified_raw = request.data.get('pan_verified', False)
        if isinstance(pan_verified_raw, str):
            pan_verified = pan_verified_raw.lower() == 'true'
        else:
            pan_verified = bool(pan_verified_raw)
            
        identity_mismatch_override_raw = request.data.get('identity_mismatch_override', False)
        if isinstance(identity_mismatch_override_raw, str):
            identity_mismatch_override = identity_mismatch_override_raw.lower() == 'true'
        else:
            identity_mismatch_override = bool(identity_mismatch_override_raw)

        if not all([token, name, email]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assessment = Assessment.objects.get(share_token=token)
            
            # Availability Guard
            now = timezone.now()
            if assessment.available_from and now < assessment.available_from:
                return Response({"error": "This assessment is not yet available."}, status=status.HTTP_400_BAD_REQUEST)
            if assessment.available_until and now > assessment.available_until:
                return Response({"error": "This assessment has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Prevent re-testing if already completed (case-insensitive check)
            if AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                submitted_at__isnull=False
            ).exists():
                return Response(
                    {"error": "You have already completed this assessment and cannot retake it."},
                    status=status.HTTP_400_BAD_REQUEST
                )



            # If an ONGOING session exists, reconnect the user instead of spawning a new one
            existing_submission = AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                status='ONGOING'
            ).order_by('-id').first()

            is_reconnect = bool(existing_submission)

            if not existing_submission:
                submission = AIAssessmentSubmission.objects.create(
                    assessment=assessment,
                    candidate_name=name,
                    candidate_email=email,
                    phone=phone,
                    pan_number=pan_number,
                    pan_photo=pan_photo,
                    pan_verified=pan_verified,
                    status='ONGOING',
                    batch_id=assessment.batch_id,
                    batch_name=assessment.batch_name,
                    current_phase='coding' if assessment.mcq_count == 0 else 'mcq'
                )
                

                # CROSS-UPDATE: Synchronize with the Candidate record if exists
                try:
                    # Use iexact and prioritize the same batch
                    candidates = Candidate.objects.filter(email__iexact=email).order_by('-id')
                    candidate = candidates.filter(batch_id=assessment.batch_id).first()
                    
                    # ONLY update the name if the candidate belongs to the SAME batch.
                    # Do not blindly fallback to candidates.first() for name updates, 
                    # as that mutates records from other pipelines.
                    if candidate:
                        logger.info(f"CreateSubmission: Reconciled candidate {candidate.id} for {email} in assessment {assessment.id}")
                        if name and (candidate.full_name == "Extraction Failed" or candidate.full_name != name):
                            candidate.full_name = name
                            candidate.save(update_fields=['full_name'])
                    else:
                        logger.info(f"CreateSubmission: No matching Candidate record found for {email} in batch {assessment.batch_id}")
                except Exception as sync_err:
                    logger.warning(f"Failed to cross-update candidate {email} on creation: {sync_err}")
            else:
                submission = existing_submission
                

            # --- DEEPFACE REGISTRATION & IDENTITY STORAGE ---
            if snapshot:
                # Prioritize lowercased PAN number as getDeepfacePersonId() in frontend
                if pan_number and pan_number.strip():
                    person_id = pan_number.lower().strip()
                elif getattr(submission, 'pan_number', None):
                    person_id = submission.pan_number.lower().strip()
                else:
                    person_id = f"{email}_{token}"
                
                # Double-check registration status directly from microservice for absolute security
                try:
                    check_url = f"{DEEPFACE_BASE_URL}/registration/registered/{person_id}"
                    check_resp = requests.get(check_url, timeout=5)
                    is_actually_registered = check_resp.status_code == 200 and check_resp.json().get('registered', False)
                except:
                    is_actually_registered = False

                is_first_registration = request.data.get('is_first_registration', 'false').lower() == 'true'

                if is_actually_registered and not is_first_registration:
                    logger.info(f"CreateSubmission: {person_id} is already registered in DeepFace. Verifying...")
                    # ALREADY REGISTERED -> Must Verify (Hard Block) or Override
                    is_verified = _verify_face_with_deepface_microservice(person_id, snapshot)
                    logger.info(f"CreateSubmission: Verification result for {person_id}: {is_verified}, Override: {identity_mismatch_override}")
                    
                    if not is_verified or identity_mismatch_override:
                        logger.warning(f"CreateSubmission: Mismatch detected or overridden for {person_id}")
                        import base64
                        from django.core.files.base import ContentFile

                        # Parse the intruder snapshot once
                        imgstr = snapshot
                        ext = 'jpg'
                        if ';' in snapshot and 'base64,' in snapshot:
                            header, imgstr = snapshot.split(';base64,')
                            ext = header.split('/')[-1]
                        img_data = base64.b64decode(imgstr)

                        # 1. Save intruder's face as a dedicated integrity screenshot
                        try:
                            integrity_snap = AIAssessmentIntegrityScreenshot(
                                submission=submission,
                                event_type="face_mismatch_on_reentry",
                            )
                            fname = f"ai_integrity_{submission.id}_mismatch_{int(timezone.now().timestamp())}.{ext}"
                            integrity_snap.screenshot.save(fname, ContentFile(img_data), save=True)
                            
                            # Deduct integrity score
                            submission.integrity_score = max(0, getattr(submission, 'integrity_score', 100) - 50)
                            submission.save(update_fields=['integrity_score'])
                        except Exception as e:
                            logger.error(f"Failed to save re-entry identity violation: {e}")

                        # 2. Save intruder's face to the dedicated intruder_photo field
                        #    (used by the result page as "ASSESSMENT FACE")
                        try:
                            submission.intruder_photo = snapshot
                        except Exception as e:
                            logger.error(f"Failed to save intruder photo: {e}")

                        # 3. FLAG: Identity mismatch detected but allow override
                        submission.identity_mismatch_detected = True
                        submission.identity_mismatch_details = {
                            'mismatch_at': timezone.now().isoformat(),
                            'person_id': person_id,
                            'mismatch_type': 'face_mismatch_on_reentry_override' if not identity_mismatch_override else 'face_mismatch_override'
                        }
                        
                        # 4. Capture the ORIGINAL registered face for comparison
                        #    Only save if not already captured (idempotent on reconnect)
                        if not submission.original_identity_photo:
                            try:
                                from pathlib import Path
                                from django.core.files import File
                                from django.conf import settings
                                deepface_data_dir = Path(settings.BASE_DIR).parent / 'deepface' / 'data' / 'registered_faces'
                                person_face_dir = deepface_data_dir / person_id
                                
                                target_file = None
                                for orig_name in ['face_0.jpg', 'registration_snapshot.jpg']:
                                    if (person_face_dir / orig_name).exists():
                                        target_file = person_face_dir / orig_name
                                        break
                                if not target_file:
                                    # Fallback: search recursively for any jpg
                                    for jpg_file in person_face_dir.rglob('*.jpg'):
                                        target_file = jpg_file
                                        break
                                
                                if target_file:
                                    with open(target_file, 'rb') as f:
                                        import base64
                                        b64 = base64.b64encode(f.read()).decode('utf-8')
                                        submission.original_identity_photo = f"data:image/jpeg;base64,{b64}"
                            except Exception as e:
                                logger.error(f"Failed to capture original identity photo for override: {e}")

                        # 5. Allow the candidate to proceed — do NOT re-register the new face.
                        #    The original face registration is preserved so the mismatch remains
                        #    detectable for the duration of the session.
                        submission.save()
                        logger.warning(
                            f"Identity mismatch flagged for AI Assessment submission {submission.id} ({email}). "
                            f"Original face preserved. Intruder photo saved."
                        )
                        # Continue flow...
                        pass
                else:
                    if identity_mismatch_override:
                        # Sometimes the deepface service might have been wiped, but they are overriding from frontend state
                        submission.identity_mismatch_detected = True
                        submission.identity_mismatch_details = {
                            'mismatch_at': timezone.now().isoformat(),
                            'person_id': person_id,
                            'mismatch_type': 'face_mismatch_override'
                        }
                        submission.save()
                        logger.warning(f"Identity mismatch override flagged for AI Assessment submission {submission.id} ({email}) without deepface conflict")

                # --- ALWAYS REGISTER THE SESSION-SCOPED DEEPFACE ANCHOR ---
                # This guarantees that the live proctoring websocket has an anchor face to verify against
                # for the duration of this specific assessment session.
                try:
                    _register_face_with_deepface(f"{person_id}/assessments/{token}", snapshot, overwrite=True)
                    logger.info(f"CreateSubmission: Session anchor registered for {person_id}/assessments/{token}")
                except Exception as e:
                    logger.error(f"Failed to register session deepface anchor: {e}")
                    
                # --- ALWAYS SAVE THE NEW SNAPSHOT ---
                # Save the registration snapshot to submission.original_identity_photo
                # so Box 2 on the report always shows the face captured at THIS exam start,
                # even if they are a returning candidate who passed verification.
                if not submission.original_identity_photo and not getattr(submission, 'identity_mismatch_detected', False):
                    try:
                        submission.original_identity_photo = snapshot
                        submission.save()
                    except Exception as e:
                        logger.error(f"Failed to save original_identity_photo at registration: {e}")

                # Store Identity Link for the report (always update to the freshest photo)
                try:
                    from api.models import IdentityLink
                    import base64
                    from django.core.files.base import ContentFile
                    
                    identity, created = IdentityLink.objects.get_or_create(
                        email=email,
                        pan_number=pan_number or 'UNKNOWN'
                    )
                    
                    if created or not identity.snapshot_image:
                        imgstr = snapshot
                        ext = 'jpg'
                        if ';' in snapshot and 'base64,' in snapshot:
                            header, imgstr = snapshot.split(';base64,')
                            ext = header.split('/')[-1]
                            
                        img_data = base64.b64decode(imgstr)
                        cname = f"ai_reg_{email.replace('@','_')}_{int(timezone.now().timestamp())}.{ext}"
                        identity.snapshot_image.save(cname, ContentFile(img_data), save=True)
                        if pan_photo:
                            identity.pan_image = pan_photo
                            identity.save()
                except Exception as e:
                    logger.error(f"Failed to save IdentityLink in AI assessment: {e}")

            # Only pick and lock questions if they haven't been locked yet
            if not submission.candidate_questions:
                # Unique MCQ Distribution:
                # Resolve this candidate's 0-based index within the batch so pick_random_subset
                # can assign a non-overlapping slice of the MCQ pool (partitioned mode).
                # For same_questions_for_all, candidate_index is not used (sampling mode).
                candidate_index = None
                if not assessment.same_questions_for_all:
                    try:
                        # Index = position of this candidate's submission among all ONGOING/submitted
                        # submissions for this assessment, ordered by creation time.
                        all_subs = list(
                            AIAssessmentSubmission.objects.filter(
                                assessment=assessment
                            ).order_by('id').values_list('id', flat=True)
                        )
                        if submission.id in all_subs:
                            candidate_index = all_subs.index(submission.id)
                        else:
                            candidate_index = len(all_subs)  # fallback: append to end
                    except Exception as idx_err:
                        logger.warning(f"Could not resolve candidate_index for {email}: {idx_err}")

                submission.candidate_questions = pick_random_subset(
                    assessment, assessment.generated_content,
                    seed=email,
                    candidate_index=candidate_index
                )
                submission.save(update_fields=['candidate_questions'])

             
            # Check if assessment has expired based on available_until
            now = timezone.now()
            if assessment.available_until and now > assessment.available_until:
                return Response({"error": "This assessment has expired and is no longer available."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate time left — phase-aware
            total_duration = assessment.duration_minutes * 60
            elapsed_since_start = (now - submission.started_at).total_seconds()
            
            if elapsed_since_start >= total_duration:
                return Response({"error": "Assessment time has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate individual phase time left
            # Use actual saved duration; fall back to 1 min per MCQ question if not set
            mcq_dur = assessment.mcq_duration_minutes if assessment.mcq_duration_minutes is not None else (assessment.mcq_count or 10)
            mcq_total = mcq_dur * 60
            coding_dur = assessment.coding_duration_minutes if assessment.coding_duration_minutes is not None else 30
            coding_total = coding_dur * 60
            
            mcq_left = max(0, mcq_total - submission.mcq_time_spent)
            coding_left = max(0, coding_total - submission.coding_time_spent)

            return Response({
                "submission_id": submission.id,
                "status": "success",
                "time_left": int(total_duration - elapsed_since_start), # total wall clock left
                "mcq_duration": mcq_total,
                "coding_duration": coding_total,
                "mcq_time_left": mcq_left,
                "coding_time_left": coding_left,
                "current_phase": submission.current_phase,
                "answers": submission.answers,
                "current_question_index": submission.current_question_index,
                "coding_results": (submission.results_breakdown or {}).get('coding_results', {}),
                "codeDrafts": (submission.results_breakdown or {}).get('code_drafts', {}),
                "candidate_questions": submission.candidate_questions
            }, status=status.HTTP_201_CREATED)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

class UpdateAssessmentIntegrityView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
            event_type = request.data.get('event_type')
            
            if event_type == 'tab_switch':
                submission.tab_switches += 1
            elif event_type == 'phone_detection':
                submission.phone_warnings += 1
            elif event_type in ['face_detection_lost', 'no_face_detection', 'no_face']:
                submission.face_warnings += 1
            elif event_type in ['multiface_detection', 'multiple_faces', 'multi_person']:
                submission.face_warnings += 1
            elif event_type in ['looking_away', 'head_yaw_exceeded', 'head_pitch_exceeded']:
                submission.face_warnings += 1
            elif event_type in ['face_mismatch', 'verification_failed', 'face_mismatch_on_reentry']:
                submission.face_warnings += 1
            elif event_type in ['fullscreen_exit', 'liveness_failed']:
                submission.face_warnings += 1
            
            # Simple metadata log
            submission.monitoring_logs.append({
                "event": event_type,
                "timestamp": timezone.now().isoformat()
            })
            
            # Grace Warning System Phase 2: Handle First 3 as Warnings
            is_warning = len(submission.warning_logs) < 3
            if is_warning:
                submission.warning_logs.append(event_type)

            # Calculate integrity score based on violations
            # Start at 100, deduct penalties for actual violations (after grace period)
            if not is_warning:
                # Define penalties for different violation types
                penalties = {
                    'tab_switch': 3,
                    'window_blur': 2,
                    'screen_stop': 2,
                    'phone_detection': 10,
                    'face_detection_lost': 5,
                    'no_face_detection': 5,
                    'no_face': 5,
                    'multiface_detection': 10,
                    'multiple_faces': 10,
                    'multi_person': 10,
                    'looking_away': 3,
                    'head_yaw_exceeded': 3,
                    'head_pitch_exceeded': 3,
                    'face_mismatch': 10,
                    'verification_failed': 10,
                    'fullscreen_exit': 10,
                    'liveness_failed': 8,
                    'face_mismatch_on_reentry': 20,
                }
                
                # Get penalty for this event (default to 5 if not specified)
                penalty = penalties.get(event_type, 5)
                
                # Apply penalty
                submission.integrity_score = max(0, submission.integrity_score - penalty)
            
            # Initialize integrity_score only if it has never been set (None).
            # Do NOT reset when score is 0 — that's a legitimate result after penalties!
            if submission.integrity_score is None:
                submission.integrity_score = 100.0
            
            # Handle Screenshot
            screenshot_b64 = request.data.get('screenshot')
            webcam_b64 = request.data.get('webcam_screenshot')
            
            if screenshot_b64 or webcam_b64:
                try:
                    integrity_snap = AIAssessmentIntegrityScreenshot(
                        submission=submission,
                        event_type=event_type,
                        timestamp=timezone.now()
                    )
                    
                    if screenshot_b64:
                        if ';' in screenshot_b64 and 'base64,' in screenshot_b64:
                            header, imgstr = screenshot_b64.split(';base64,')
                            ext = header.split('/')[-1]
                        else:
                            imgstr = screenshot_b64
                            ext = 'png'
                        
                        img_data = base64.b64decode(imgstr)
                        fname = f"ai_integrity_{submission.id}_{event_type}_{int(timezone.now().timestamp())}.{ext}"
                        integrity_snap.screenshot.save(fname, ContentFile(img_data), save=False)

                    if webcam_b64:
                        if ';' in webcam_b64 and 'base64,' in webcam_b64:
                            header, imgstr = webcam_b64.split(';base64,')
                            ext = header.split('/')[-1]
                        else:
                            imgstr = webcam_b64
                            ext = 'png'
                        
                        webcam_data = base64.b64decode(imgstr)
                        cname = f"ai_cam_{submission.id}_{event_type}_{int(timezone.now().timestamp())}.{ext}"
                        integrity_snap.webcam_screenshot.save(cname, ContentFile(webcam_data), save=False)

                    integrity_snap.save()

                    # If face_mismatch_on_reentry detected (explicit re-entry verification),
                    # flag identity mismatch. Regular face_mismatch/verification_failed from
                    # WebSocket monitoring are soft proctoring warnings (lighting, angle, threshold)
                    # and should NOT trigger the identity mismatch flag — that is handled by
                    # CreateSubmissionView when a genuinely different person uses someone's PAN.
                    if event_type == 'face_mismatch_on_reentry':
                        if not submission.intruder_photo and webcam_b64:
                            submission.intruder_photo = webcam_b64
                        
                        submission.identity_mismatch_detected = True
                        if not submission.identity_mismatch_details:
                            submission.identity_mismatch_details = {}
                        submission.identity_mismatch_details['mismatch_at'] = timezone.now().isoformat()
                        submission.identity_mismatch_details['mismatch_type'] = event_type

                except Exception as se:
                    logger.error(f"Failed to save AI integrity screenshot: {str(se)}")

            submission.save()
            
            return Response({
                "status": "success",
                "integrity_score": submission.integrity_score
            })
        except AIAssessmentSubmission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

class SaveAssessmentProgressView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
            if submission.submitted_at:
                return Response({"error": "Already submitted"}, status=status.HTTP_400_BAD_REQUEST)
            
            answers = request.data.get('answers')
            index = request.data.get('current_question_index')
            coding_results = request.data.get('coding_results')
            code_drafts = request.data.get('codeDrafts')
            
            if answers is not None:
                submission.answers = answers
            if index is not None:
                submission.current_question_index = index
            
            if not submission.results_breakdown:
                submission.results_breakdown = {}
                
            if coding_results is not None:
                submission.results_breakdown['coding_results'] = coding_results
            if code_drafts is not None:
                submission.results_breakdown['code_drafts'] = code_drafts

            # Update time tracking
            now = timezone.now()
            elapsed = int((now - submission.last_phase_switch).total_seconds())
            
            if submission.current_phase == 'mcq':
                submission.mcq_time_spent += elapsed
            else:
                submission.coding_time_spent += elapsed
            
            submission.last_phase_switch = now

            # Handle phase switch if requested
            new_phase = request.data.get('current_phase')
            if new_phase and new_phase in ['mcq', 'coding']:
                submission.current_phase = new_phase
            
            submission.save()
            return Response({
                "status": "progress saved",
                "mcq_time_spent": submission.mcq_time_spent,
                "coding_time_spent": submission.coding_time_spent,
                "current_phase": submission.current_phase
            })
        except AIAssessmentSubmission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

class AssessmentListView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            if not company:
                return Response([], status=status.HTTP_200_OK)

            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)

            if scoped_ids is None:
                # Application Admin: all in company, OR assessments with company=None that they created
                assessments = Assessment.objects.filter(
                    models.Q(company=company) | models.Q(company__isnull=True, user_profile=user_profile),
                    is_deleted=False
                ).exclude(status='FAILED').order_by('-created_at')
            else:
                # Scoped: only assessments created by users in this user's reporting hierarchy
                assessments = Assessment.objects.filter(
                    company=company, 
                    user_profile_id__in=scoped_ids, 
                    is_deleted=False
                ).exclude(status='FAILED').order_by('-created_at')

            data = []
            for assessment in assessments:
                count = AIAssessmentSubmission.objects.filter(assessment=assessment).count()
                completed_count = AIAssessmentSubmission.objects.filter(assessment=assessment, submitted_at__isnull=False).count()
                # Use available_until as expiry if present, else fallback to 7 days
                if assessment.available_until:
                    expiry_at = assessment.available_until
                else:
                    expiry_at = assessment.created_at + timedelta(days=7)

                data.append({
                    "id": assessment.id,
                    "job_description": assessment.job_description,
                    "required_skills": assessment.required_skills,
                    "mcq_count": assessment.mcq_count,
                    "coding_count": assessment.coding_count,
                    "duration_minutes": assessment.duration_minutes,
                    "mcq_duration_minutes": assessment.mcq_duration_minutes,
                    "coding_duration_minutes": assessment.coding_duration_minutes,
                    "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                    "expiry_at": expiry_at.strftime("%Y-%m-%d %H:%M"),
                    "generated_content": _normalize_generated_pool(assessment.generated_content or {}),
                    "status": assessment.status,
                    "batch_name": assessment.batch_name,
                    "creation_type": assessment.creation_type,
                    "max_candidates_allowed": assessment.max_candidates_allowed,
                    "share_token": str(assessment.share_token),
                    "candidate_count": count,
                    "completed_count": completed_count,
                    "invited_count": assessment.invited_count,
                    "num_applicants": assessment.num_applicants,
                    "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                    "available_until": assessment.available_until.isoformat() if assessment.available_until else None
                })
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AssessmentDetailView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)

            if scoped_ids is None:
                # Primary attempt: By ID and Company
                assessment = Assessment.objects.filter(pk=pk, company=company).first()
                # Fallback: By ID and Creator (handles legacy/admin assessments with company=None)
                if not assessment:
                    assessment = Assessment.objects.filter(pk=pk, user_profile=user_profile).first()
            else:
                assessment = Assessment.objects.filter(pk=pk, company=company, user_profile_id__in=scoped_ids).first()
            
            if not assessment:
                raise Assessment.DoesNotExist
                
            submissions = AIAssessmentSubmission.objects.filter(assessment=assessment).order_by('-submitted_at')
            
            def clean_b64(b64_str):
                if not b64_str:
                    return None
                b64_str = b64_str.strip()
                if b64_str.startswith('identity_overrides/'):
                    try:
                        from django.conf import settings
                        from pathlib import Path
                        import base64
                        file_path = Path(settings.MEDIA_ROOT) / b64_str
                        if file_path.exists():
                            with open(file_path, 'rb') as f:
                                b64 = base64.b64encode(f.read()).decode('utf-8')
                                ext = b64_str.split('.')[-1].lower()
                                mime = "image/png" if ext == "png" else "image/jpeg"
                                return f"data:{mime};base64,{b64}"
                    except Exception:
                        pass
                    return None
                if not b64_str.startswith('data:image'):
                    return f"data:image/jpeg;base64,{b64_str}"
                return b64_str

            submission_data = []
            for sub in submissions:
                integrity_snapshots = AIAssessmentIntegrityScreenshot.objects.filter(submission=sub).order_by('timestamp')
                screenshots_data = []
                for snap in integrity_snapshots:
                    screenshots_data.append({
                        "event_type": snap.event_type,
                        "timestamp": snap.timestamp.isoformat() if snap.timestamp else None,
                        "screenshot_url": request.build_absolute_uri(snap.screenshot.url) if snap.screenshot else None,
                        "webcam_screenshot_url": request.build_absolute_uri(snap.webcam_screenshot.url) if snap.webcam_screenshot else None,
                        "has_screenshot": bool(snap.screenshot),
                        "has_webcam_screenshot": bool(snap.webcam_screenshot),
                    })

                photo_url = _get_candidate_photo_url(request, sub)

                # Try to load registration_snapshot.jpg from assessments folder (via API first, then local disk)
                pending_photo_b64 = None
                is_automatic = getattr(assessment, 'creation_type', 'manual') == 'automatic'
                if is_automatic:
                    try:
                        p_id = sub.pan_number.lower().strip() if getattr(sub, 'pan_number', None) else f"{sub.candidate_email.lower().strip()}_{assessment.share_token}"
                        from api._imports import DEEPFACE_BASE_URL
                        import requests
                        import base64
                        
                        df_url = f"{DEEPFACE_BASE_URL}/registration/registered/{p_id}/assessments/{assessment.share_token}/photo"
                        resp = requests.get(df_url, timeout=5)
                        if resp.status_code == 200:
                            pending_photo_b64 = f"data:image/jpeg;base64,{base64.b64encode(resp.content).decode('utf-8')}"
                    except Exception:
                        pass

                if not pending_photo_b64:
                    try:
                        from pathlib import Path
                        from django.conf import settings
                        import base64
                        deepface_data_dir = Path(settings.BASE_DIR).parent / 'deepface' / 'data' / 'registered_faces'
                        p_id = sub.pan_number.lower().strip() if getattr(sub, 'pan_number', None) else f"{sub.candidate_email.lower().strip()}_{assessment.share_token}"
                        target_snap_file = deepface_data_dir / p_id / 'assessments' / str(assessment.share_token) / 'registration_snapshot.jpg'
                        if target_snap_file.exists():
                            with open(target_snap_file, 'rb') as f:
                                pending_photo_b64 = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"
                    except Exception:
                        pass

                # No fallback to intruder_photo to ensure we only get starting override snapshot

                submission_data.append({
                    "id": sub.id,
                    "submission_id": f"ai_{sub.id}",
                    "candidate_name": sub.candidate_name,
                    "candidate_email": sub.candidate_email,
                    "job_title": assessment.required_skills,
                    "role": assessment.required_skills,
                    "assessment_name": assessment.required_skills,
                    "score": sub.score,
                    "mcq_score": sub.mcq_score,
                    "coding_score": sub.coding_score,
                    "results_breakdown": sub.results_breakdown,
                    "percentage": sub.percentage,
                    "status": sub.status,
                    "final_status": sub.status,
                    "integrity_score": sub.integrity_score,
                    "submitted_at": timezone.localtime(sub.submitted_at).strftime("%Y-%m-%d %H:%M") if sub.submitted_at else None,
                    "candidate_questions": sub.candidate_questions,
                    "answers": sub.answers,
                    "integrity_screenshots": screenshots_data,
                    "is_resume_screening": False,
                    "candidate_photo_url": photo_url,
                    "pan_photo": request.build_absolute_uri(sub.pan_photo.url) if sub.pan_photo else None,
                    # Identity mismatch fields
                    "identity_mismatch_detected": getattr(sub, 'identity_mismatch_detected', False),
                    "original_identity_photo_url": clean_b64(sub.original_identity_photo),
                    "intruder_photo_url": pending_photo_b64,
                    "identity_mismatch_details": getattr(sub, 'identity_mismatch_details', {}),
                })


            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "role_title": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "mcq_duration_minutes": assessment.mcq_duration_minutes,
                "coding_duration_minutes": assessment.coding_duration_minutes,
                "difficulty_level": assessment.difficulty_level,
                "total_points": assessment.total_points,
                "pass_threshold": assessment.pass_threshold,
                "mcq_weight": getattr(assessment, 'mcq_weight', 40) or 40,
                "coding_weight": 100 - (getattr(assessment, 'mcq_weight', 40) or 40),
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M") if assessment.created_at else None,
                "generated_content": _normalize_generated_pool(assessment.generated_content or {}),
                "status": assessment.status,
                "batch_name": assessment.batch_name,
                "creation_type": assessment.creation_type,
                "share_token": str(assessment.share_token),
                "num_applicants": assessment.num_applicants,
                "max_candidates_allowed": assessment.max_candidates_allowed,
                "same_questions_for_all": assessment.same_questions_for_all,
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None,
                "submissions": submission_data,
                "assigned_interviewers": []
            }
            # Safely try to load assigned_interviewers
            try:
                data["assigned_interviewers"] = [
                    {"id": i.id, "name": i.user.get_full_name() or i.user.username, "email": i.user.email, "role": i.role}
                    for i in assessment.assigned_interviewers.all()
                ]
            except Exception:
                pass

            return Response(data, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)

            if scoped_ids is None:
                assessment = Assessment.objects.filter(pk=pk, company=company).first()
                if not assessment:
                    assessment = Assessment.objects.filter(pk=pk, user_profile=user_profile).first()
            else:
                assessment = Assessment.objects.filter(pk=pk, company=company, user_profile_id__in=scoped_ids).first()

            if not assessment:
                return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update fields
            if 'num_applicants' in request.data:
                assessment.num_applicants = request.data['num_applicants']
            # role_title is not in the model, we use required_skills
            if 'role_title' in request.data:
                assessment.required_skills = request.data['role_title']
            
            assessment.save()
            return Response({
                "message": "Assessment updated successfully",
                "num_applicants": assessment.num_applicants,
                "role_title": assessment.required_skills
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def pick_random_subset(self, assessment, pool):
        return pick_random_subset(assessment, pool)

class PublicAssessmentView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def get(self, request, token):
        try:
            with open('api_debug.txt', 'a') as f:
                f.write(f"\n[{timezone.now()}] PUBLIC ACCESS: Token='{token}'\n")
                f.write(f"Query Params: {request.query_params}\n")
                f.write(f"Host: {request.get_host()}\n")
        except Exception:
            pass

        try:
            assessment = Assessment.objects.get(share_token=token)
            gen_content = assessment.generated_content or {}
            
            # Robust extraction: Handle if it's a string or nested dict
            if isinstance(gen_content, str):
                import json
                try:
                    gen_content = json.loads(gen_content)
                except:
                    pass

            # Unwrap if it's a wrapper dict (like {"technical_assessment": {...}})
            if isinstance(gen_content, dict):
                # If it doesn't have the main keys but has a nested dict that does, unwrap it
                if 'mcqs' not in gen_content and 'coding_challenges' not in gen_content:
                    for val in gen_content.values():
                        if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                            gen_content = val
                            break
            # Second pass: if it's still a string (nested string), try one more parse
            if isinstance(gen_content, str):
                try:
                    gen_content = json.loads(gen_content)
                except:
                    pass

            # 1. Handle Candidate-Specific Randomized Content
            email_param = request.query_params.get('email', '').strip().lower()
            name_param = request.query_params.get('name', '').strip()
            
            gen_content = _normalize_generated_pool(gen_content)
            final_content = gen_content
            already_completed = False
            
            if email_param:
                from .models import AIAssessmentSubmission
                import random

                # Check for existing submission
                submission = AIAssessmentSubmission.objects.filter(
                    assessment=assessment,
                    candidate_email__iexact=email_param
                ).first()

                if submission:
                    already_completed = submission.submitted_at is not None
                    # If we already have locked-in questions, use them
                    if submission.candidate_questions:
                        final_content = submission.candidate_questions
                    else:
                        # Case 1 & 3 Bypass
                        if assessment.num_applicants <= 1 or assessment.same_questions_for_all:
                            final_content = _normalize_generated_pool(gen_content)
                        else:
                            # Use consistent index logic even in preview if submission exists
                            candidate_index = None
                            try:
                                all_subs = list(AIAssessmentSubmission.objects.filter(assessment=assessment).order_by('id').values_list('id', flat=True))
                                if submission.id in all_subs:
                                    candidate_index = all_subs.index(submission.id)
                            except: pass
                            final_content = pick_random_subset(assessment, gen_content, seed=email_param, candidate_index=candidate_index)
                            
                        submission.candidate_questions = final_content
                        submission.save(update_fields=['candidate_questions'])
                else:
                    # No submission yet, but we have an email. 
                    # Consistent set for the UI. Since there is no submission ID yet, 
                    # we use a fallback that will be reconciled when the submission is created.
                    if assessment.num_applicants <= 1 or assessment.same_questions_for_all:
                        final_content = _normalize_generated_pool(gen_content)
                    else:
                        final_content = pick_random_subset(assessment, gen_content, seed=email_param)


            # Prevent Answer Leakage: Strip MCQ answers from the public payload
            if isinstance(final_content, dict) and 'mcqs' in final_content:
                for mcq in final_content['mcqs']:
                    if isinstance(mcq, dict):
                        mcq.pop('answer', None)
                        mcq.pop('correct_answer', None)

            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "mcq_duration_minutes": assessment.mcq_duration_minutes,
                "coding_duration_minutes": assessment.coding_duration_minutes,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": final_content,
                "status": assessment.status,
                "already_completed": already_completed,
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None
            }
            response = Response(data, status=status.HTTP_200_OK)
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response
        except Assessment.DoesNotExist:
            logger.error(f"PublicAssessmentView: Assessment not found for token {token}")
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
             logger.error(f"PublicAssessmentView Error: {str(e)}\n{traceback.format_exc()}")
             return Response({"error": "Invalid token or data structure"}, status=status.HTTP_400_BAD_REQUEST)
class InviteAssessmentCandidatesView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def post(self, request):
        assessment_id = request.data.get('assessment_id')
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            assessment = Assessment.objects.get(pk=assessment_id, company=company)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

        invite_type = request.data.get('type')  # 'individual' or 'bulk'
        invited_candidates = []
        
        # Check if max candidates reached
        from .models import InvitedCandidate
        already_invited = InvitedCandidate.objects.filter(assessment=assessment).count()
        max_allowed = assessment.max_candidates_allowed
        
        import urllib.parse
        # Use frontend base URL from settings - Standardized to localhost for dev
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        base_link = f"{base_url}/take-ai-assessment/{assessment.share_token}"

        if invite_type == 'individual':
            name = request.data.get('name')
            email = request.data.get('email')
            if not name or not email:
                return Response({"error": "Name and Email are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if max reached
            if already_invited >= max_allowed:
                return Response({"error": f"Maximum {max_allowed} candidates allowed. Already invited {already_invited}."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already invited
            if InvitedCandidate.objects.filter(assessment=assessment, email=email).exists():
                return Response({"error": f"Candidate {email} already invited."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Append name and email
            encoded_name = urllib.parse.quote(name)
            encoded_email = urllib.parse.quote(email)
            link = f"{base_link}?name={encoded_name}&email={encoded_email}"
            
            # Save invited candidate
            InvitedCandidate.objects.create(assessment=assessment, name=name, email=email)
            
            # Increment invited count
            assessment.invited_count += 1
            assessment.save(update_fields=['invited_count'])
            
            invited_candidates.append({"name": name, "email": email, "link": link})
            
            # Send Email
            try:
                subject = f"Invite to AI Technical Assessment: {assessment.required_skills}"
                
                # Format availability dates in local time for consistency
                from django.utils import timezone
                if assessment.available_from:
                    local_start = timezone.localtime(assessment.available_from)
                    start_time = local_start.strftime('%B %d, %Y at %I:%M %p')
                else:
                    start_time = "Immediately"
                if assessment.available_until:
                    local_end = timezone.localtime(assessment.available_until)
                    end_time = local_end.strftime('%B %d, %Y at %I:%M %p')
                else:
                    end_time = "No fixed deadline"
                
                jd_preview = (assessment.job_description or '')[:200]
                
                # Plain text fallback
                message = f"Dear {name},\n\nYou have been invited to attempt an AI technical assessment for the role of {assessment.required_skills}.\n\nTiming Details:\n- Available From: {start_time}\n- Available Until: {end_time}\n- Duration: {assessment.duration_minutes} minutes\n\nPlease click the link below to start your assessment during the availability window:\n{link}\n\nBest of luck!"
                
                # HTML version
                html_message = f"""
                <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                    <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">Assessment Invitation</h1>
                    </div>
                    <div style="padding: 32px; background-color: white;">
                        <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{name}</strong>,</p>
                        <p style="line-height: 1.6; margin-bottom: 24px;">You have been invited to attempt an AI technical assessment for the role: <br/><strong>{assessment.required_skills}</strong></p>
                        
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                            <h3 style="margin-top: 0; color: #4318FF; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>
                            <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {start_time}</p>
                            <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {end_time}</p>
                            <p style="margin: 8px 0; font-size: 14px;"><strong>⏱️ Duration:</strong> {assessment.duration_minutes} minutes</p>
                        </div>
                        
                        <div style="text-align: center; margin: 32px 0;">
                            <a href="{link}" style="background-color: #4318FF; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(67, 24, 255, 0.2);">Start Assessment</a>
                        </div>
                        
                        <p style="font-size: 13px; color: #64748b; margin-top: 32px; border-top: 1px solid #f1f5f9; pt: 16px;">If the button above doesn't work, copy and paste this link into your browser:<br/>
                        <a href="{link}" style="color: #4318FF;">{link}</a></p>
                    </div>
                    <div style="background-color: #f1f5f9; padding: 16px; text-align: center; font-size: 12px; color: #94a3b8;">
                        &copy; 2026 VerifiHireAI. All rights reserved.
                    </div>
                </div>
                """
                
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False, html_message=html_message)
                logger.info(f"Individual invite sent to {email}")
            except Exception as e:
                import traceback
                logger.error(f"Email error for {email}: {str(e)}")
                logger.error(traceback.format_exc())
                return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        elif invite_type == 'bulk':
            file = request.FILES.get('file')
            if not file:
                return Response({"error": "File is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                import pandas as pd
                if file.name.lower().endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                df.columns = df.columns.str.lower().str.strip()
                if 'name' not in df.columns or 'email' not in df.columns:
                    return Response({"error": "File must have 'name' and 'email' columns"}, status=status.HTTP_400_BAD_REQUEST)

                # Check capacity
                max_allowed = assessment.max_candidates_allowed
                available_slots = max_allowed - already_invited
                num_to_invite = min(len(df), available_slots)
                
                if num_to_invite == 0:
                    return Response(
                        {"error": f"No available slots. Max {max_allowed} allowed, {already_invited} already invited."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                invitation_count = 0
                skipped_count = 0

                for idx, row in df.iterrows():
                    if invitation_count >= num_to_invite:
                        break
                        
                    name = str(row['name']).strip()
                    email = str(row['email']).strip()
                    
                    # Check if already invited
                    if InvitedCandidate.objects.filter(assessment=assessment, email=email).exists():
                        skipped_count += 1
                        continue
                    
                    encoded_name = urllib.parse.quote(name)
                    encoded_email = urllib.parse.quote(email)
                    link = f"{base_link}?name={encoded_name}&email={encoded_email}"
                    
                    # Save invited candidate
                    InvitedCandidate.objects.create(assessment=assessment, name=name, email=email)
                    invitation_count += 1
                    
                    invited_candidates.append({"name": name, "email": email, "link": link})
                    
                    try:
                        subject = f"Invite to AI Technical Assessment: {assessment.required_skills}"
                        
                        from django.utils import timezone
                        if assessment.available_from:
                            local_start = timezone.localtime(assessment.available_from)
                            start_time = local_start.strftime('%B %d, %Y at %I:%M %p')
                        else:
                            start_time = "Immediately"
                        if assessment.available_until:
                            local_end = timezone.localtime(assessment.available_until)
                            end_time = local_end.strftime('%B %d, %Y at %I:%M %p')
                        else:
                            end_time = "No fixed deadline"

                        message = f"Dear {name},\n\nYou have been invited to attempt an AI technical assessment for the role: {assessment.required_skills}.\n\nTiming Details:\n- Available From: {start_time}\n- Available Until: {end_time}\n- Duration: {assessment.duration_minutes} minutes\n\nLink: {link}\n\nGood luck!"
                        
                        html_message = f"""
                        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                            <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                                <h1 style="color: white; margin: 0; font-size: 24px;">Assessment Invitation</h1>
                            </div>
                            <div style="padding: 32px; background-color: white;">
                                <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{name}</strong>,</p>
                                <p style="line-height: 1.6; margin-bottom: 24px;">You have been invited to attempt an AI technical assessment for the role: <br/><strong>{assessment.required_skills}</strong></p>
                                
                                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                                    <h3 style="margin-top: 0; color: #4318FF; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>
                                    <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {start_time}</p>
                                    <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {end_time}</p>
                                    <p style="margin: 8px 0; font-size: 14px;"><strong>⏱️ Duration:</strong> {assessment.duration_minutes} minutes</p>
                                </div>
                                
                                <div style="text-align: center; margin: 32px 0;">
                                    <a href="{link}" style="background-color: #4318FF; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(67, 24, 255, 0.2);">Start Assessment</a>
                                </div>
                                
                                <p style="font-size: 13px; color: #64748b; margin-top: 32px; border-top: 1px solid #f1f5f9; pt: 16px;">If the button above doesn't work, copy and paste this link into your browser:<br/>
                                <a href="{link}" style="color: #4318FF;">{link}</a></p>
                            </div>
                            <div style="background-color: #f1f5f9; padding: 16px; text-align: center; font-size: 12px; color: #94a3b8;">
                                &copy; 2026 VerifiHireAI. All rights reserved.
                            </div>
                        </div>
                        """

                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False, html_message=html_message)
                        logger.info(f"Bulk invite sent to {email}")
                    except Exception as mail_err:
                        logger.error(f"Bulk email error for {email}: {mail_err}")
            except Exception as e:
                return Response({"error": f"Error parsing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update assessment invited count to match invited candidates count
        assessment.invited_count = InvitedCandidate.objects.filter(assessment=assessment).count()
        assessment.save(update_fields=['invited_count'])
        
        # Calculate remaining spots
        remaining_spots = max(0, assessment.max_candidates_allowed - assessment.invited_count)

        return Response({
            "message": f"Successfully invited {len(invited_candidates)} {'candidate' if len(invited_candidates) == 1 else 'candidates'}",
            "count": len(invited_candidates),
            "total_invited": assessment.invited_count,
            "max_allowed": assessment.max_candidates_allowed,
            "remaining_spots": remaining_spots
        }, status=status.HTTP_200_OK)

class ResendAssessmentInviteView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def post(self, request):
        assessment_id = request.data.get('assessment_id')
        email = request.data.get('email')
        
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            assessment = Assessment.objects.get(pk=assessment_id, company=company)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        from .models import InvitedCandidate
        candidate = InvitedCandidate.objects.filter(assessment=assessment, email=email).first()
        
        if not candidate:
            return Response({"error": "Candidate not found in invited list"}, status=status.HTTP_404_NOT_FOUND)

        import urllib.parse
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        base_link = f"{base_url}/take-ai-assessment/{assessment.share_token}"
        
        encoded_name = urllib.parse.quote(candidate.name)
        encoded_email = urllib.parse.quote(candidate.email)
        link = f"{base_link}?name={encoded_name}&email={encoded_email}"

        try:
            subject = f"Reminder: Invite to AI Technical Assessment - {assessment.required_skills}"
            
            from django.utils import timezone
            if assessment.available_from:
                local_start = timezone.localtime(assessment.available_from)
                start_time = local_start.strftime('%B %d, %Y at %I:%M %p')
            else:
                start_time = "Immediately"
            if assessment.available_until:
                local_end = timezone.localtime(assessment.available_until)
                end_time = local_end.strftime('%B %d, %Y at %I:%M %p')
            else:
                end_time = "No fixed deadline"
            
            message = f"Dear {candidate.name},\n\nThis is a reminder that you have been invited to attempt an AI technical assessment for the role of {assessment.required_skills}.\n\nTiming Details:\n- Available From: {start_time}\n- Available Until: {end_time}\n- Duration: {assessment.duration_minutes} minutes\n\nPlease click the link below to start your assessment during the availability window:\n{link}\n\nBest of luck!"
            
            html_message = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">Assessment Invitation Reminder</h1>
                </div>
                <div style="padding: 32px; background-color: white;">
                    <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{candidate.name}</strong>,</p>
                    <p style="line-height: 1.6; margin-bottom: 24px;">This is a reminder that you have been invited to attempt an AI technical assessment for the role: <br/><strong>{assessment.required_skills}</strong></p>
                    
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                        <h3 style="margin-top: 0; color: #4318FF; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>
                        <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {start_time}</p>
                        <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {end_time}</p>
                        <p style="margin: 8px 0; font-size: 14px;"><strong>⏱️ Duration:</strong> {assessment.duration_minutes} minutes</p>
                    </div>
                    
                    <div style="text-align: center; margin: 32px 0;">
                        <a href="{link}" style="background-color: #4318FF; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(67, 24, 255, 0.2);">Start Assessment</a>
                    </div>
                    
                    <p style="font-size: 13px; color: #64748b; margin-top: 32px; border-top: 1px solid #f1f5f9; pt: 16px;">If the button above doesn't work, copy and paste this link into your browser:<br/>
                    <a href="{link}" style="color: #4318FF;">{link}</a></p>
                </div>
                <div style="background-color: #f1f5f9; padding: 16px; text-align: center; font-size: 12px; color: #94a3b8;">
                    &copy; 2026 VerifiHireAI. All rights reserved.
                </div>
            </div>
            """
            
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [candidate.email], fail_silently=False, html_message=html_message)
            logger.info(f"Resent individual invite to {candidate.email}")
            
            return Response({"message": f"Successfully resent invitation to {candidate.email}"}, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            logger.error(f"Email error for {candidate.email}: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class GetInvitedCandidatesView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]
    
    def get(self, request, assessment_id):
        """Get list of invited candidates for an assessment"""
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            assessment = Assessment.objects.filter(pk=assessment_id, company=company).first()
            if not assessment:
                assessment = Assessment.objects.filter(pk=assessment_id, user_profile=user_profile).first()
            
            if not assessment:
                raise Assessment.DoesNotExist
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        from .models import InvitedCandidate
        invited_qs = InvitedCandidate.objects.filter(assessment=assessment).order_by('-invited_at')
        
        invited_list = []
        for cand in invited_qs:
            invited_list.append({
                "name": cand.name,
                "email": cand.email,
                "status": cand.status,
                "invited_at": cand.invited_at.strftime("%Y-%m-%d %H:%M") if cand.invited_at else None
            })
        
        # Calculate candidate points (Division based on num_applicants vs same_questions)
        divisor = max(1, assessment.num_applicants) if not assessment.same_questions_for_all else 1
        
        mcq_pool_size = assessment.mcq_count if hasattr(assessment, 'mcq_count') else 0
        coding_pool_size = assessment.coding_count if hasattr(assessment, 'coding_count') else 0
        
        candidate_mcq_count = mcq_pool_size // divisor
        candidate_coding_count = coding_pool_size // divisor
        
        # Scoring: 1 pt per MCQ + weighted coding (matching actual scoring engine)
        mcq_points = candidate_mcq_count * 1
        
        # Calculate coding points based on difficulty weights of challenges in the pool
        coding_points = 0
        generated_content = assessment.generated_content or {}
        coding_pool = generated_content.get('coding_challenges', [])
        weight_map = {'Easy': 100, 'Medium': 200, 'Hard': 300}
        
        for i in range(min(len(coding_pool), candidate_coding_count)):
            difficulty = coding_pool[i].get('difficulty', 'Medium')
            coding_points += weight_map.get(difficulty, 200)
            
        total_candidate_points = mcq_points + coding_points
        
        remaining_spots = max(0, assessment.max_candidates_allowed - invited_qs.count())
        
        return Response({
            "invited_candidates": invited_list,
            "total_invited": invited_qs.count(),
            "max_allowed": assessment.max_candidates_allowed,
            "remaining_spots": remaining_spots,
            "can_invite_more": remaining_spots > 0,
            "candidate_points": {
                "mcq_count": candidate_mcq_count,
                "mcq_points": mcq_points,
                "coding_count": candidate_coding_count,
                "coding_points": coding_points,
                "total_points": total_candidate_points
            }
        }, status=status.HTTP_200_OK)

import requests

from rest_framework.permissions import AllowAny

class ProxyCodeExecuteView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        try:
            language = request.data.get('language')
            files = request.data.get('files', [])
            stdin = request.data.get('stdin', '')
            # Coerce stdin to a string if it's a dict/list from JSON test cases
            if isinstance(stdin, (dict, list)):
                import json
                stdin = json.dumps(stdin)
            elif stdin is None or (isinstance(stdin, str) and stdin.strip().lower() in ["none", "null"]):
                stdin = ""
            else:
                stdin = str(stdin)
            code = files[0]['content'] if files else ''
            
            # Get executor URL from environment or fallback to localhost:4000
            executor_base_url = os.environ.get("EXECUTOR_BASE_URL", "http://localhost:4000").rstrip("/")
            
            # Prepare payload for internal executor
            payload = {
                "language": language,
                "source_code": code,
                "stdin": stdin,
                "time_limit_ms": 30000,
                "memory_mb": 2048,
            }

            # Special handling for SQL (default to sqlite for AI assessments)
            if language == 'sql':
                payload["database_engine"] = "sqlite"
                payload["stdin"] = "" # SQL executor shouldn't parse stdin as SQL if it's JSON

            # Call internal executor
            try:
                response = requests.post(f"{executor_base_url}/execute", json=payload, timeout=120)
                result = response.json()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"ProxyCodeExecuteView executor timeout/error: {str(e)}")
                return Response({
                    "run": {
                        "stdout": "",
                        "stderr": f"Execution Service Timeout: {str(e)}",
                        "code": 1,
                        "output": f"The code execution service (port 4000) Timed Out after 120s. Please restart the executor or simplify your code."
                    }
                }, status=status.HTTP_200_OK)

            if not result.get('ok'):
                return Response({
                    "run": {
                        "stdout": "",
                        "stderr": result.get('error', 'Executor Error'),
                        "code": 1,
                        "output": result.get('error', 'Executor Error')
                    }
                }, status=status.HTTP_200_OK)

            # Map executor response to the format expected by the frontend
            piston_response = {
                "run": {
                    "stdout": result.get('stdout', ''),
                    "stderr": result.get('stderr', ''),
                    "code": result.get('exit_code', 0),
                    "output": result.get('stdout', '') + result.get('stderr', '')
                }
            }

            return Response(piston_response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Code Execution Proxy Error: {str(e)}")
            return Response({
                "run": {
                    "stdout": "",
                    "stderr": f"Execution Error: {str(e)}",
                    "code": 1
                }
            }, status=status.HTTP_200_OK)

class AIAssessmentSubmissionDetailView(generics.RetrieveDestroyAPIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_profile = getattr(self.request.user, 'profile', None)
        company = user_profile.company if user_profile and user_profile.company else None
        if not company:
            return AIAssessmentSubmission.objects.none()
            
        from api._imports import get_scoped_user_ids
        scoped_ids = get_scoped_user_ids(user_profile)

        if scoped_ids is None:
            return AIAssessmentSubmission.objects.filter(assessment__company=company, is_deleted=False)
            
        return AIAssessmentSubmission.objects.filter(
            assessment__company=company, 
            assessment__user_profile_id__in=scoped_ids, 
            is_deleted=False
        )

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Get integrity snapshots
        integrity_snapshots = AIAssessmentIntegrityScreenshot.objects.filter(submission=instance).order_by('timestamp')
        screenshots_data = []
        for snap in integrity_snapshots:
            screenshots_data.append({
                "event_type": snap.event_type,
                "timestamp": snap.timestamp.isoformat() if snap.timestamp else None,
                "screenshot_url": request.build_absolute_uri(snap.screenshot.url) if snap.screenshot else None,
                "webcam_screenshot_url": request.build_absolute_uri(snap.webcam_screenshot.url) if snap.webcam_screenshot else None,
                "has_screenshot": bool(snap.screenshot),
                "has_webcam_screenshot": bool(snap.webcam_screenshot),
            })

        # Get candidate photo using unified helper
        photo_url = _get_candidate_photo_url(request, instance)

        # Prepare detailed response data
        data = {
            "id": instance.id,
            "submission_id": f"ai_{instance.id}",
            "candidate_name": instance.candidate_name,
            "candidate_email": instance.candidate_email,
            "job_title": instance.assessment.required_skills,
            "score": instance.score,
            "mcq_score": instance.mcq_score,
            "coding_score": instance.coding_score,
            "results_breakdown": instance.results_breakdown,
            "percentage": instance.percentage,
            "status": instance.status,
            "integrity_score": instance.integrity_score,
            "submitted_at": instance.submitted_at.isoformat() if instance.submitted_at else None,
            "candidate_questions": instance.candidate_questions,
            "answers": instance.answers,
            "integrity_screenshots": screenshots_data,
            "candidate_photo_url": photo_url,
            "pan_photo": request.build_absolute_uri(instance.pan_photo.url) if instance.pan_photo else None,
            "pan_number": instance.pan_number,
            "pan_verified": instance.pan_verified,
            "phone": instance.phone,
            "assessment": {
                "id": instance.assessment.id,
                "display_name": instance.assessment.required_skills,
                "name": instance.assessment.required_skills
            },
            # Identity mismatch fields
            **_get_unified_identity_mismatch_fields(request, instance),
        }
        return Response(data)

    def delete(self, request, *args, **kwargs):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.company:
            return super().destroy(request, *args, **kwargs)

        instance = self.get_object()
        
        # Use centralized helper to handle policy and workflow
        response, handled = handle_deletion_request(
            user_profile=user_profile,
            company=user_profile.company,
            content_type='AIAssessmentSubmission',
            object_id=instance.id,
            object_repr=f"AI Assessment Submission: {instance.candidate_name} ({instance.candidate_email})",
            reason=request.data.get('reason')
        )
        
        if handled:
            return response

        return self.destroy(request, *args, **kwargs)

class AIAssessmentAssignmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or user_profile.role not in ['company_admin', 'hr_manager', 'ROLE_COMPANY_ADMIN', 'ROLE_HR_MANAGER']:
            return Response({"error": "Unauthorized"}, status=403)
            
        try:
            assessment = Assessment.objects.get(pk=pk, company=user_profile.company)
            interviewer_ids = request.data.get('interviewer_ids', [])
            
            interviewers = UserProfile.objects.filter(id__in=interviewer_ids, company=user_profile.company)
            assessment.assigned_interviewers.set(interviewers)
            
            return Response({"message": "Interviewers assigned successfully"})
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=404)

class AIAssessmentAvailableInterviewersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.company:
            return Response({"error": "Unauthorized"}, status=403)
            
        # exclude candidates
        members = UserProfile.objects.filter(company=user_profile.company).exclude(role__in=['candidate', 'ROLE_CANDIDATE'])
        data = [
            {"id": m.id, "name": f"{m.first_name or ''} {m.last_name or ''}".strip() or m.email, "email": m.email, "role": m.role}
            for m in members
        ]
        return Response(data)

class AIAssessmentReportDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        temp_files_to_cleanup = []
        
        def _save_to_temp_file(content_or_b64, is_b64=False):
            import tempfile
            import base64
            import os
            # Create temp file
            suffix = ".jpg"
            f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            try:
                if is_b64:
                    # Clean up header if present
                    if ',' in content_or_b64 and content_or_b64.startswith('data:'):
                        content_or_b64 = content_or_b64.split(',', 1)[1]
                    data = base64.b64decode(content_or_b64)
                else:
                    data = content_or_b64
                f.write(data)
                f.close()
                return f.name
            except Exception as e:
                f.close()
                try:
                    os.unlink(f.name)
                except:
                    pass
                raise e

        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
            assessment = submission.assessment
            
            # RBAC: Ensure user belongs to the same company or is a superuser
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile or (user_profile.company != assessment.company and not request.user.is_superuser):
                return Response({'error': 'Unauthorized access to this assessment report.'}, status=status.HTTP_403_FORBIDDEN)

            # Generate PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )
            styles = getSampleStyleSheet()
            
            # Custom Styles for Premium Look
            styles.add(ParagraphStyle(
                'SubHeader',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor("#707EAE"),
                alignment=0,
                spaceAfter=12
            ))
            styles.add(ParagraphStyle(
                'CardLabel',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor("#A3AED0"),
                fontName='Helvetica-Bold',
                alignment=1,
                textTransform='uppercase'
            ))
            styles.add(ParagraphStyle(
                'CardValue',
                parent=styles['Normal'],
                fontSize=18,
                textColor=colors.HexColor("#4318FF"),
                fontName='Helvetica-Bold',
                alignment=1
            ))
            styles.add(ParagraphStyle(
                'CardSubValue',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-Bold',
                alignment=1
            ))
            styles.add(ParagraphStyle(
                'BannerLabel',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor("#A3AED0"),
                fontName='Helvetica-Bold',
                alignment=1,
                textTransform='uppercase'
            ))
            styles.add(ParagraphStyle(
                'BannerValue',
                parent=styles['Normal'],
                fontSize=28,
                textColor=colors.HexColor("#4318FF"),
                fontName='Helvetica-Bold',
                alignment=1
            ))
            styles.add(ParagraphStyle(
                'BannerStatus',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-Bold',
                alignment=1,
                textTransform='uppercase'
            ))
            styles.add(ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-Bold',
                spaceBefore=20,
                spaceAfter=15
            ))
            styles.add(ParagraphStyle(
                'QuestionHeader',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor("#707EAE"),
                fontName='Helvetica-Bold',
                textTransform='uppercase'
            ))
            styles.add(ParagraphStyle(
                'QuestionText',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-Bold',
                leading=14
            ))
            styles.add(ParagraphStyle(
                'BadgeCorrect',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor("#05CD99"),
                fontName='Helvetica-Bold',
                alignment=2
            ))
            styles.add(ParagraphStyle(
                'BadgeIncorrect',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor("#EE5D50"),
                fontName='Helvetica-Bold',
                alignment=2
            ))
            styles.add(ParagraphStyle(
                'SolutionBox',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor("#1B254B"),
                backColor=colors.HexColor("#E6FBF5"),
                borderPadding=10,
                borderWidth=0,
                borderRadius=10,
                fontName='Helvetica-Bold'
            ))
            styles.add(ParagraphStyle(
                'CodeTitle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.white,
                backColor=colors.HexColor("#4318FF"),
                borderPadding=5,
                borderRadius=5,
                fontName='Helvetica-Bold',
                alignment=0
            ))
            styles.add(ParagraphStyle(
                'RefCodeTitle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.white,
                backColor=colors.HexColor("#05CD99"),
                borderPadding=5,
                borderRadius=5,
                fontName='Helvetica-Bold',
                alignment=0
            ))
            styles.add(ParagraphStyle(
                'CodeContent',
                parent=styles['Code'],
                fontSize=8,
                textColor=colors.HexColor("#05CD99"),
                backColor=colors.HexColor("#1B254B"),
                borderPadding=15,
                borderRadius=15,
                fontName='Courier'
            ))
            styles.add(ParagraphStyle(
                'RefCodeContent',
                parent=styles['Code'],
                fontSize=8,
                textColor=colors.HexColor("#7EE787"),
                backColor=colors.HexColor("#0D1117"),
                borderPadding=15,
                borderRadius=15,
                fontName='Courier'
            ))

            elements = []

            # Calculate scores
            res_brk = submission.results_breakdown or {}
            mcq_scored = res_brk.get('mcq', {}).get('scored_points', 0)
            mcq_total = res_brk.get('mcq', {}).get('possible_points', submission.total_questions or 10)
            mcq_pct = round((mcq_scored / mcq_total * 100)) if mcq_total > 0 else 0
            
            coding_scored = res_brk.get('coding', {}).get('scored_points', 0)
            coding_total = res_brk.get('coding', {}).get('possible_points', 0)
            coding_pct = round((coding_scored / coding_total * 100)) if coding_total > 0 else 0

            integrity_score = submission.integrity_score
            integrity_label = "✓ Reliable" if integrity_score >= 50 else "⚠ Suspicious"
            integrity_color = colors.HexColor("#05CD99") if integrity_score >= 50 else colors.HexColor("#EE5D50")

            # Status display
            if submission.status == 'selected':
                status_display = "Assessment Passed"
                status_color = colors.HexColor("#05CD99")
            elif submission.status == 'hold':
                status_display = "On Hold \u2014 Pending Admin Review"
                status_color = colors.HexColor("#F59E0B")
            else:
                status_display = "Not Qualified"
                status_color = colors.HexColor("#EE5D50")

            # 1. Report Header - Interview Report Style
            elements.append(Paragraph("VerifiHireAI — Assessment Report", ParagraphStyle(
                'ReportHeader',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor("#4F46E5"),
                alignment=1,  # Center
                spaceAfter=6
            )))
            elements.append(Paragraph(f"Candidate: {submission.candidate_name}", ParagraphStyle(
                'CandidateSubHeader',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor("#1B254B"),
                alignment=1,
                spaceAfter=20
            )))

            # 2. Candidate Information Section
            elements.append(Paragraph("Candidate Information", ParagraphStyle(
                'SectionTitleItalic',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-BoldOblique',
                spaceAfter=10
            )))

            # Get candidate photo — prioritizing PAN, then exact assessment token folder
            candidate_img = None
            
            try:
                from pathlib import Path
                import os as _os
                deepface_data_dir = Path(__file__).resolve().parent.parent.parent / 'deepface' / 'data' / 'registered_faces'
                
                target_file = None
                is_automatic = getattr(assessment, 'creation_type', 'manual') == 'automatic'

                # --- STEP 0: MIRROR UI LOGIC ---
                # If there's an identity mismatch, the main candidate profile photo should be the intruder/assessment face (Box 2)
                if getattr(submission, 'identity_mismatch_detected', False):
                    if getattr(submission, 'intruder_photo', None):
                        try:
                            temp_intr = _save_to_temp_file(submission.intruder_photo, is_b64=True)
                            temp_files_to_cleanup.append(temp_intr)
                            target_file = Path(temp_intr)
                        except Exception as e:
                            logger.error(f"PDF Gen: Failed to save intruder_photo for Candidate Profile: {e}")
                            
                    if not target_file and is_automatic:
                        from api._imports import DEEPFACE_BASE_URL
                        import requests
                        token = str(assessment.share_token)
                        pan = getattr(submission, 'pan_number', None)
                        email = submission.candidate_email.lower().strip() if submission.candidate_email else None
                        person_id = pan.lower().strip() if pan else f"{email}_{token}"
                        df_url = f"{DEEPFACE_BASE_URL}/registration/registered/{person_id}/assessments/{token}/photo"
                        try:
                            resp = requests.get(df_url, timeout=5)
                            if resp.status_code == 200:
                                temp_path = _save_to_temp_file(resp.content, is_b64=False)
                                temp_files_to_cleanup.append(temp_path)
                                target_file = Path(temp_path)
                        except Exception as e:
                            logger.warning(f"PDF Gen: Failed to fetch Box 2 photo for Candidate Profile: {e}")

                # Step 1: Decode original_identity_photo if present on the submission (Box 1 fallback)
                if not target_file and getattr(submission, 'original_identity_photo', None):
                    try:
                        temp_orig = _save_to_temp_file(submission.original_identity_photo, is_b64=True)
                        temp_files_to_cleanup.append(temp_orig)
                        target_file = Path(temp_orig)
                    except Exception as e:
                        logger.error(f"PDF Gen: Failed to save original_identity_photo: {e}")

                # Step 2: Fetch via DeepFace API if automatic assessment
                if not target_file and is_automatic:
                    from api._imports import DEEPFACE_BASE_URL
                    import requests
                    
                    token = str(assessment.share_token)
                    email = submission.candidate_email.lower().strip() if submission.candidate_email else None
                    pan = getattr(submission, 'pan_number', None)
                    person_id = pan.lower().strip() if pan else f"{email}_{token}"
                    
                    urls_to_try = [
                        f"{DEEPFACE_BASE_URL}/registration/registered/{person_id}/assessments/{token}/photo",
                        f"{DEEPFACE_BASE_URL}/registration/registered/{person_id}/photo",
                    ]
                    if email:
                        urls_to_try.append(f"{DEEPFACE_BASE_URL}/registration/registered/{email}/photo")
                        
                    photo_bytes = None
                    for df_url in urls_to_try:
                        try:
                            resp = requests.get(df_url, timeout=5)
                            if resp.status_code == 200:
                                photo_bytes = resp.content
                                break
                        except Exception as e:
                            logger.warning(f"PDF Gen: DeepFace API proxy failed for URL {df_url}: {e}")
                            
                    if photo_bytes:
                        temp_path = _save_to_temp_file(photo_bytes, is_b64=False)
                        temp_files_to_cleanup.append(temp_path)
                        target_file = Path(temp_path)

                # Step 3: Check unified IdentityLink next
                if not target_file and submission.candidate_email:
                    try:
                        from api.models import IdentityLink
                        identities = IdentityLink.objects.filter(email__iexact=submission.candidate_email.lower().strip()).order_by('-id')
                        for identity in identities:
                            if identity.snapshot_image and identity.snapshot_image.name:
                                if _os.path.exists(identity.snapshot_image.path):
                                    target_file = Path(identity.snapshot_image.path)
                                    break
                    except Exception as e:
                        logger.warning(f"PDF IdentityLink check error: {e}")

                # Step 4: Prioritize PAN folder
                if not target_file and getattr(submission, 'pan_number', None):
                    pan_id = submission.pan_number.lower().strip()
                    pan_face_dir = deepface_data_dir / pan_id
                    if pan_face_dir.exists():
                        for name in ['face_0.jpg', 'registration_snapshot.jpg']:
                            if (pan_face_dir / name).exists():
                                target_file = pan_face_dir / name
                                break
                        if not target_file:
                            jpgs = list(pan_face_dir.glob('*.jpg'))
                            if jpgs:
                                target_file = jpgs[0]

                # Step 5: Fall back to exact email_token folder for this assessment only
                if not target_file:
                    person_id = f"{submission.candidate_email.lower().strip()}_{assessment.share_token}" if assessment.share_token else submission.candidate_email.lower().strip()
                    person_face_dir = deepface_data_dir / person_id
                    for name in ['face_0.jpg', 'registration_snapshot.jpg']:
                        if (person_face_dir / name).exists():
                            target_file = person_face_dir / name
                            break
                    if not target_file and person_face_dir.exists():
                        jpgs = list(person_face_dir.glob('*.jpg'))
                        if jpgs:
                            target_file = jpgs[0]

                # Step 6: First non-empty webcam integrity screenshot (> 10KB)
                if not target_file:
                    snaps = AIAssessmentIntegrityScreenshot.objects.filter(
                        submission=submission,
                        webcam_screenshot__isnull=False
                    ).exclude(event_type__icontains='face_not_detected').order_by('timestamp')
                    for snap in snaps:
                        if snap.webcam_screenshot and snap.webcam_screenshot.name:
                            if _os.path.exists(snap.webcam_screenshot.path):
                                if _os.path.getsize(snap.webcam_screenshot.path) > 10000:
                                    target_file = Path(snap.webcam_screenshot.path)
                                    break

                if target_file:
                    candidate_img = RLImage(str(target_file), width=1.4*inch, height=1.4*inch)

            except Exception as e:
                logger.error(f"PDF Photo error for candidate {submission.candidate_email}: {e}")

            # Info table data
            # Handle old submissions without PAN data
            if submission.pan_number:
                pan_verified_text = "Yes ✓" if submission.pan_verified else "No ✗"
            else:
                pan_verified_text = "N/A"
            # Identify mismatch details
            mismatch_data = _get_unified_identity_mismatch_fields(request, submission)
            identity_status = "Verified \u2713"
            ident_status_color = colors.HexColor("#16a34a") # Green
            
            if mismatch_data.get('identity_mismatch_detected', False):
                if mismatch_data.get('photo_update_approved', False):
                    identity_status = "MISMATCH (APPROVED & UPDATED) \u2713"
                    ident_status_color = colors.HexColor("#16a34a") # Green
                # Check rejection state by looking at the details dict directly
                elif isinstance(mismatch_data.get('identity_mismatch_details'), dict) and mismatch_data['identity_mismatch_details'].get('photo_update_status') == 'rejected':
                    identity_status = "MISMATCH (APPROVAL REJECTED) \u2717"
                    ident_status_color = colors.HexColor("#dc2626") # Red
                else:
                    identity_status = "MISMATCH DETECTED \u2717"
                    ident_status_color = colors.HexColor("#dc2626") # Red

            match_score_str = "100%"
            score_val = getattr(submission, 'face_match_score', None)
            if score_val is not None:
                if score_val <= 1.0:
                    match_score_str = f"{min(100.0, round(score_val * 100.0, 2))}%"
                else:
                    match_score_str = f"{min(100.0, round(score_val, 2))}%"
            elif mismatch_data.get('identity_mismatch_detected', False):
                match_score_str = "Mismatch \u2717"

            is_student = hasattr(request.user, 'profile') and request.user.profile.role == 'student'

            if is_student:
                info_data = [
                    ['Full Name', submission.candidate_name],
                    ['Email', submission.candidate_email or 'N/A'],
                    ['Phone', submission.phone or 'N/A'],
                ]
            else:
                info_data = [
                    ['Full Name', submission.candidate_name],
                    ['Email', submission.candidate_email or 'N/A'],
                    ['Phone', submission.phone or 'N/A'],
                    ['PAN Number', submission.pan_number or 'N/A'],
                    ['PAN Verified', pan_verified_text],
                    ['Identity Status', identity_status],
                    ['Face Match Score', match_score_str],
                ]
            
            mismatch_reason = getattr(submission, 'identity_mismatch_reason', None)
            if not is_student and mismatch_data.get('identity_mismatch_detected', False) and mismatch_reason:
                info_data.append(['Mismatch Reason', mismatch_reason])

            info_data.extend([
                ['Job Title', assessment.required_skills or 'N/A'],
                ['MCQ Score', f"{mcq_pct}% ({mcq_scored} / {mcq_total} Correct)"],
                ['Coding Score', f"{coding_pct}% ({coding_scored} / {coding_total} pts)"],
            ])

            if not is_student:
                info_data.append(['Integrity Score', f"{integrity_score}% {integrity_label}"])

            info_data.extend([
                ['Overall Result', f"{submission.percentage}%"],
                ['Status', status_display],
                ['Submission Date', submission.submitted_at.strftime('%B %d, %Y %I:%M %p') if submission.submitted_at else 'N/A'],
            ])

            # Style the info table
            info_table = Table(info_data, colWidths=[1.4*inch, 3.0*inch])
            
            # Find indices for dynamic styling
            integrity_idx = -1
            status_idx = -1
            overall_idx = -1
            identity_status_idx = -1
            mismatch_reason_idx = -1
            
            for i, row in enumerate(info_data):
                if row[0] == 'Integrity Score': integrity_idx = i
                elif row[0] == 'Status': status_idx = i
                elif row[0] == 'Overall Result': overall_idx = i
                elif row[0] == 'Identity Status': identity_status_idx = i
                elif row[0] == 'Mismatch Reason': mismatch_reason_idx = i

            base_styles = [
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8F9FF")),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (0,-1), 9),
                ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#64748b")),
                ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (1,0), (1,-1), 10),
                ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor("#1B254B")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (0,-1), 10),
                ('LEFTPADDING', (1,0), (1,-1), 10),
                ('TOPPADDING', (0,0), (-1,-1), 7),
                ('BOTTOMPADDING', (0,0), (-1,-1), 7),
                ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E0E5F2")),
            ]
            
            if integrity_idx != -1:
                base_styles.extend([
                    ('TEXTCOLOR', (1,integrity_idx), (1,integrity_idx), integrity_color),
                    ('FONTNAME', (1,integrity_idx), (1,integrity_idx), 'Helvetica-Bold')
                ])
            if status_idx != -1:
                base_styles.extend([
                    ('TEXTCOLOR', (1,status_idx), (1,status_idx), status_color),
                    ('FONTNAME', (1,status_idx), (1,status_idx), 'Helvetica-Bold')
                ])
            if overall_idx != -1:
                base_styles.extend([
                    ('TEXTCOLOR', (1,overall_idx), (1,overall_idx), status_color),
                    ('FONTNAME', (1,overall_idx), (1,overall_idx), 'Helvetica-Bold')
                ])
            if identity_status_idx != -1:
                base_styles.extend([
                    ('TEXTCOLOR', (1,identity_status_idx), (1,identity_status_idx), ident_status_color),
                    ('FONTNAME', (1,identity_status_idx), (1,identity_status_idx), 'Helvetica-Bold')
                ])
            if mismatch_reason_idx != -1:
                base_styles.extend([
                    ('TEXTCOLOR', (1,mismatch_reason_idx), (1,mismatch_reason_idx), colors.HexColor("#dc2626")),
                    ('FONTNAME', (1,mismatch_reason_idx), (1,mismatch_reason_idx), 'Helvetica-Bold')
                ])
                
            info_table.setStyle(TableStyle(base_styles))

            # Photo section - Stacking Candidate Photo and PAN Card
            photo_style = ParagraphStyle('PhotoLabel', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor("#707EAE"))
            photo_elements = []
            
            if candidate_img:
                photo_elements.append([candidate_img])
                photo_elements.append([Paragraph("Candidate Photo", photo_style)])
            if not photo_elements:
                no_photo_text = Paragraph("No photos<br/>available", ParagraphStyle('NoPhoto', parent=styles['Normal'], fontSize=9, alignment=1, textColor=colors.grey))
                photo_table = Table([[no_photo_text]], colWidths=[1.5*inch], rowHeights=[1.5*inch])
                photo_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F4F7FE")),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
            else:
                # Calculate row heights: images are 1.4/1.0 inch, labels are ~18pt, spacer is 10pt
                row_heights = []
                for row in photo_elements:
                    if isinstance(row[0], RLImage):
                        row_heights.append(row[0].drawHeight)
                    elif isinstance(row[0], Spacer):
                        row_heights.append(10)
                    else:
                        row_heights.append(18)
                        
                photo_table = Table(photo_elements, colWidths=[1.5*inch], rowHeights=row_heights)
                photo_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))

            # Combine photo + info in a bordered container
            page_width = A4[0] - 100  # Total usable width (50pt margins each side)
            if is_student:
                combined_table = Table([[info_table]], colWidths=[page_width])
                combined_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (0,0), 10),
                    ('RIGHTPADDING', (0,0), (0,0), 10),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                    # Outer border box
                    ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#D0D5E4")),
                    ('ROUNDEDCORNERS', [6, 6, 6, 6]),
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FCFCFF")),
                ]))
            else:
                combined_data = [[photo_table, info_table]]
                combined_table = Table(combined_data, colWidths=[1.8*inch, page_width - 1.8*inch])
                combined_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (0,0), 'CENTER'),
                    ('LEFTPADDING', (0,0), (0,0), 10),
                    ('RIGHTPADDING', (0,0), (0,0), 10),
                    ('LEFTPADDING', (1,0), (1,0), 5),
                    ('RIGHTPADDING', (1,0), (1,0), 5),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                    # Outer border box
                    ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#D0D5E4")),
                    ('ROUNDEDCORNERS', [6, 6, 6, 6]),
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FCFCFF")),
                    # Vertical divider between photo and info
                    ('LINEAFTER', (0,0), (0,-1), 0.5, colors.HexColor("#E0E5F2")),
                ]))
            elements.append(combined_table)

            elements.append(Spacer(1, 30))

            # 3.5 Identity Documents Section - PAN Card
            if not is_student and submission.pan_photo:
                elements.append(Paragraph("Identity Documents", styles['Heading3']))
                elements.append(Spacer(1, 10))
                
                try:
                    pan_img_path = submission.pan_photo.path
                    if _os.path.exists(pan_img_path):
                        pan_img_elem = RLImage(pan_img_path, width=3.0*inch, height=2.0*inch)
                        pan_caption = f"PAN Card: {submission.pan_number or 'N/A'} (Verified: {'Yes' if submission.pan_verified else 'No'})"
                        
                        pan_table = Table([
                            [pan_img_elem],
                            [Paragraph(pan_caption, ParagraphStyle('SmallStyle', parent=styles['Normal'], fontSize=9))]
                        ], colWidths=[3.0*inch])
                        pan_table.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ]))
                        elements.append(pan_table)
                    else:
                        elements.append(Paragraph("<i>PAN card image file not found on server.</i>", styles['Normal']))
                except Exception as pan_error:
                    elements.append(Paragraph(f"<i>Error loading PAN card image: {str(pan_error)}</i>", styles['Italic']))
                
                elements.append(Spacer(1, 25))

            # 4. MCQ Section
            generated_content = submission.candidate_questions or assessment.generated_content or {}
            if 'mcqs' not in generated_content and 'coding_challenges' not in generated_content:
                for val in generated_content.values():
                    if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                        generated_content = val
                        break
            
            mcqs = generated_content.get('mcqs', [])
            coding_challenges = generated_content.get('coding_challenges', [])
            answers = submission.answers or {}

            if mcqs:
                elements.append(Paragraph("MCQ Answer Verification", styles['SectionTitle']))
                page_width = A4[0] - 100  # Usable width

                for i, mcq in enumerate(mcqs):
                    q_text = mcq.get('question', 'N/A')
                    options = mcq.get('options', [])
                    correct_ans = str(mcq.get('answer') or mcq.get('correct_answer') or '').strip()
                    candidate_ans = str(answers.get(f'mcq_{i}') or '').strip()
                    is_correct = candidate_ans == correct_ans

                    # Question Header with Badge — full width
                    badge_text = "CORRECT" if is_correct else "INCORRECT"
                    badge_style = styles['BadgeCorrect'] if is_correct else styles['BadgeIncorrect']
                    q_header_table = Table(
                        [[Paragraph(f"QUESTION {i+1}", styles['QuestionHeader']), Paragraph(badge_text, badge_style)]],
                        colWidths=[page_width - 1.6*inch, 1.6*inch]
                    )
                    q_header_table.setStyle(TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('ALIGN', (1,0), (1,0), 'RIGHT'),
                    ]))
                    elements.append(q_header_table)
                    elements.append(Paragraph(q_text, styles['QuestionText']))
                    elements.append(Spacer(1, 8))

                    # Options — stacked vertically, each as a full-width bordered row
                    for oi, opt in enumerate(options):
                        is_selected = opt == candidate_ans
                        is_ans = opt == correct_ans
                        
                        bg = colors.white
                        border_color = colors.HexColor("#E0E5F2")
                        txt_color = colors.HexColor("#1B254B")
                        marker = ""
                        
                        if is_ans:
                            bg = colors.HexColor("#E6FBF5")
                            border_color = colors.HexColor("#05CD99")
                            txt_color = colors.HexColor("#05CD99")
                            marker = " (Correct Answer)"
                        elif is_selected and not is_correct:
                            bg = colors.HexColor("#FFF5F5")
                            border_color = colors.HexColor("#EE5D50")
                            txt_color = colors.HexColor("#EE5D50")
                            marker = " (Your Answer)"
                        elif is_selected and is_correct:
                            marker = " (Your Answer)"
                        
                        prefix = f"{chr(65+oi)}."
                        opt_para = Paragraph(
                            f"<b>{prefix}</b> {opt}<font color='#94A3B8'>{marker}</font>",
                            ParagraphStyle('OptStyle', parent=styles['Normal'], textColor=txt_color, fontSize=9, leading=13)
                        )
                        opt_table = Table([[opt_para]], colWidths=[page_width - 10])
                        opt_table.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,-1), bg),
                            ('BOX', (0,0), (-1,-1), 0.8, border_color),
                            ('LEFTPADDING', (0,0), (-1,-1), 10),
                            ('RIGHTPADDING', (0,0), (-1,-1), 10),
                            ('TOPPADDING', (0,0), (-1,-1), 6),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ]))
                        elements.append(opt_table)
                        elements.append(Spacer(1, 3))

                    # Correct Solution Box if incorrect
                    if not is_correct:
                        elements.append(Spacer(1, 6))
                        sol_box = Table(
                            [[Paragraph("CORRECT ANSWER:", styles['QuestionHeader']), Paragraph(correct_ans, styles['SolutionBox'])]],
                            colWidths=[1.5*inch, page_width - 1.5*inch]
                        )
                        sol_box.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E6FBF5")),
                            ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#05CD99")),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('LEFTPADDING', (0,0), (-1,-1), 10),
                            ('TOPPADDING', (0,0), (-1,-1), 6),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ]))
                        elements.append(sol_box)

                    elements.append(Spacer(1, 20))

            # 5. Coding Section
            if coding_challenges:
                elements.append(PageBreak())
                elements.append(Paragraph("Coding Verification", styles['SectionTitle']))
                coding_results = (submission.results_breakdown or {}).get('coding_results', {})

                for i, challenge in enumerate(coding_challenges):
                    title = challenge.get('title', 'N/A')
                    desc = challenge.get('problem_statement', challenge.get('description', 'N/A'))
                    student_code = answers.get(f'coding_{i}', '// No code submitted')
                    ref_solution = challenge.get('reference_solution', '')
                    
                    res = coding_results.get(str(i), {})
                    passed = res.get('passed', 0)
                    total_tc = res.get('total', challenge.get('test_cases', []).__len__() if isinstance(challenge.get('test_cases'), list) else 0)
                    
                    # Challenge Header
                    elements.append(Paragraph(title, styles['Heading3']))
                    elements.append(Paragraph(desc, styles['Normal']))
                    elements.append(Paragraph(f"<b>Passed Tests:</b> {passed} / {total_tc}", styles['Normal']))
                    elements.append(Spacer(1, 15))

                    # Candidate Submission
                    elements.append(Paragraph("CANDIDATE SUBMISSION", styles['CodeTitle']))
                    elements.append(XPreformatted(student_code, styles['CodeContent']))
                    elements.append(Spacer(1, 15))

                    # Reference Solution
                    if ref_solution:
                        elements.append(Paragraph("✓ REFERENCE SOLUTION (ANSWER KEY)", styles['RefCodeTitle']))
                        elements.append(XPreformatted(ref_solution, styles['RefCodeContent']))
                        elements.append(Spacer(1, 30))

            # 6. Integrity Violations Log
            if not is_student:
                elements.append(PageBreak())
                elements.append(Paragraph("Integrity Violations Log", styles['SectionTitle']))
                
                screenshots = submission.screenshots.all().order_by('timestamp')
                if screenshots.exists():
                    # Display in a grid-like fashion (4 images per row)
                    shots_list = list(screenshots)
                    img_grid = []
                    current_row = []
                    page_width = A4[0] - 100  # Usable width
                    col_w = page_width / 4
                    
                    for shot in shots_list:
                        img_path = None
                        if shot.webcam_screenshot: img_path = shot.webcam_screenshot.path
                        elif shot.screenshot: img_path = shot.screenshot.path
                        
                        try:
                            if img_path:
                                rl_img = RLImage(img_path, width=col_w - 12, height=(col_w - 12) * 0.75)
                                label = f"{shot.event_type.replace('_', ' ').title()} ({shot.timestamp.strftime('%I:%M:%S %p')})"
                                current_row.append([rl_img, Paragraph(label, ParagraphStyle('ShotLabel', parent=styles['Normal'], fontSize=7, alignment=1, textColor=colors.grey, leading=9))])
                            else:
                                current_row.append(Paragraph("No Image", styles['Normal']))
                        except:
                            current_row.append(Paragraph("Error Loading", styles['Normal']))

                        if len(current_row) == 4:
                            img_grid.append(current_row)
                            current_row = []

                    if current_row:
                        while len(current_row) < 4:
                            current_row.append("")
                        img_grid.append(current_row)

                    for grid_row in img_grid:
                        t = Table([grid_row], colWidths=[col_w] * 4)
                        t.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('LEFTPADDING', (0,0), (-1,-1), 3),
                            ('RIGHTPADDING', (0,0), (-1,-1), 3),
                            ('TOPPADDING', (0,0), (-1,-1), 5),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                        ]))
                        elements.append(t)
                else:
                    elements.append(Paragraph("No violations recorded. Candidate maintained full integrity.", styles['Italic']))

                # Identity Mismatch Section in PDF (placed below integrity screenshots)
                mismatch_fields = _get_unified_identity_mismatch_fields(request, submission) or {}
                is_mismatch_detected = mismatch_fields.get('identity_mismatch_detected', False)
                is_photo_approved = mismatch_fields.get('photo_update_approved', False)
                
                if is_mismatch_detected or is_photo_approved:
                    elements.append(Spacer(1, 15))
                    # Red alert box title
                    mismatch_title_style = ParagraphStyle(
                        'MismatchTitle',
                        parent=styles['Heading3'],
                        fontSize=11,
                        textColor=colors.HexColor("#EE5D50"),
                        fontName='Helvetica-Bold',
                        spaceAfter=6
                    )
                    elements.append(Paragraph("⚠ IDENTITY EVIDENCE — FACE COMPARISON MISMATCH", mismatch_title_style))
                    
                    desc_style = ParagraphStyle(
                        'MismatchDesc',
                        parent=styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor("#EE5D50"),
                        leading=13
                    )
                    elements.append(Paragraph(
                        "The candidate failed the automated facial verification check when starting the assessment. "
                        "They chose to 'Override & Continue', meaning the assessment was completed using a <b>different face</b> "
                        "than what was initially registered. Please compare the original face with the overriding face below.",
                        desc_style
                    ))
                    elements.append(Spacer(1, 10))
                    
                    # Side-by-side comparison table
                    comparison_photos = []
                    comparison_row = []
                    
                    import os as _os_local
                    orig_path = None
                    master_url = mismatch_fields.get('master_photo_url')
                    if master_url:
                        try:
                            temp_orig = _save_to_temp_file(master_url, is_b64=True)
                            temp_files_to_cleanup.append(temp_orig)
                            orig_path = temp_orig
                        except Exception as e:
                            logger.error(f"PDF Gen: Failed to write master mismatch temp file: {e}")
                            
                    intr_path = None
                    pending_url = mismatch_fields.get('pending_identity_photo_url')
                    if pending_url:
                        try:
                            temp_intr = _save_to_temp_file(pending_url, is_b64=True)
                            temp_files_to_cleanup.append(temp_intr)
                            intr_path = temp_intr
                        except Exception as e:
                            logger.error(f"PDF Gen: Failed to write pending intruder temp file: {e}")
                    
                    # Fall back to target_file if original_identity_photo not set on submission
                    if not orig_path and target_file:
                        orig_path = str(target_file)
                    
                    try:
                        if orig_path and _os_local.path.exists(orig_path):
                            comparison_row.append(RLImage(orig_path, width=1.6*inch, height=1.6*inch))
                        else:
                            comparison_row.append(Paragraph("No Registered Photo", styles['Normal']))
                    except Exception as e:
                        comparison_row.append(Paragraph(f"Error loading: {str(e)}", styles['Normal']))
                        
                    try:
                        if intr_path and _os_local.path.exists(intr_path):
                            comparison_row.append(RLImage(intr_path, width=1.6*inch, height=1.6*inch))
                        else:
                            comparison_row.append(Paragraph("No Overriding Photo", styles['Normal']))
                    except Exception as e:
                        comparison_row.append(Paragraph(f"Error loading: {str(e)}", styles['Normal']))
                        
                    comparison_photos.append(comparison_row)
                    
                    # Labels row
                    comparison_labels = [
                        Paragraph("<b>1. Registered Face</b>", ParagraphStyle('CompLabel1', parent=styles['Normal'], fontSize=9, alignment=1)),
                        Paragraph("<b>2. Assessment Overriding Face</b>", ParagraphStyle('CompLabel2', parent=styles['Normal'], fontSize=9, alignment=1))
                    ]
                    comparison_photos.append(comparison_labels)
                    
                    comp_table = Table(comparison_photos, colWidths=[page_width/2] * 2)
                    comp_table.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#EE5D50")),
                        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF5F5")),
                    ]))
                    elements.append(comp_table)

            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            # Prepare Response
            response = HttpResponse(buffer, content_type='application/pdf')
            safe_name = "".join([c for c in submission.candidate_name if c.isalnum() or c==' ']).rstrip().replace(' ', '_')
            filename = f"AI_Assessment_Report_{safe_name}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except AIAssessmentSubmission.DoesNotExist:
            return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generating PDF report for submission {pk}: {str(e)}", exc_info=True)
            return Response({'error': f"Critical failure: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            import os
            for temp_file in temp_files_to_cleanup:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to delete temp file {temp_file}: {cleanup_err}")

class AIAssessmentTimelineView(APIView):
    """
    Fetches the assessment activity logs for a specific submission.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
            # Permission check: ensure user belongs to same company
            user_profile = getattr(request.user, 'profile', None)
            if not self.request.user.is_superuser and (not user_profile or user_profile.company != submission.assessment.company):
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

            logs = []
            from django.utils import timezone as tz

            # 1. Guaranteed Assessment Registration/Creation log
            # For legacy assessments that might have no other logs
            created_time = getattr(submission.assessment, 'created_at', None) or submission.started_at or tz.now()
            logs.append({
                'id': 'ts_created_at',
                'event_type': 'ASSESSMENT_REGISTERED',
                'status': 'INFO',
                'phase': 'ASSESSMENT',
                'batch_id': getattr(submission, 'batch_id', None),
                'message': 'Candidate was registered for the AI Assessment.',
                'details': {},
                'timestamp': created_time.isoformat(),
                'timestamp_formatted': tz.localtime(created_time).strftime('%B %d, %Y at %I:%M %p'),
            })

            # 2. Key assessment timestamps
            if submission.started_at:
                local_opened = tz.localtime(submission.started_at)
                logs.append({
                    'id': 'ts_started_at',
                    'event_type': 'STARTED_ASSESSMENT',
                    'status': 'INFO',
                    'phase': 'ASSESSMENT',
                    'batch_id': getattr(submission, 'batch_id', None),
                    'message': 'Candidate started the assessment.',
                    'details': {},
                    'timestamp': submission.started_at.isoformat(),
                    'timestamp_formatted': local_opened.strftime('%B %d, %Y at %I:%M %p'),
                })

            if submission.submitted_at:
                local_submitted = tz.localtime(submission.submitted_at)
                logs.append({
                    'id': 'ts_submitted_at',
                    'event_type': 'SUBMITTED_ASSESSMENT',
                    'status': 'SUCCESS',
                    'phase': 'ASSESSMENT',
                    'batch_id': getattr(submission, 'batch_id', None),
                    'message': 'Candidate submitted the assessment.',
                    'details': {},
                    'timestamp': submission.submitted_at.isoformat(),
                    'timestamp_formatted': local_submitted.strftime('%B %d, %Y at %I:%M %p'),
                })

            # 2. Warning logs
            if isinstance(submission.warning_logs, list):
                for i, w_log in enumerate(submission.warning_logs):
                    if isinstance(w_log, dict):
                        try:
                            import dateutil.parser
                            dt = dateutil.parser.isoparse(w_log.get('time'))
                            local_dt = tz.localtime(dt)
                        except:
                            dt = submission.started_at
                            local_dt = tz.localtime(dt)
                        
                        logs.append({
                            'id': f'warning_{i}',
                            'event_type': w_log.get('type', 'WARNING'),
                            'status': 'FAILURE',
                            'phase': 'ASSESSMENT',
                            'batch_id': getattr(submission, 'batch_id', None),
                            'message': w_log.get('message', 'Warning triggered'),
                            'details': {},
                            'timestamp': dt.isoformat(),
                            'timestamp_formatted': local_dt.strftime('%B %d, %Y at %I:%M %p'),
                        })
                    else:
                        dt = submission.started_at
                        local_dt = tz.localtime(dt)
                        logs.append({
                            'id': f'warning_{i}',
                            'event_type': 'WARNING',
                            'status': 'FAILURE',
                            'phase': 'ASSESSMENT',
                            'batch_id': getattr(submission, 'batch_id', None),
                            'message': str(w_log),
                            'details': {},
                            'timestamp': dt.isoformat(),
                            'timestamp_formatted': local_dt.strftime('%B %d, %Y at %I:%M %p'),
                        })

            # 3. Integrity Screenshots
            logger = logging.getLogger(__name__)
            snapshots = AIAssessmentIntegrityScreenshot.objects.filter(submission=submission).order_by('timestamp')
            INLINE_LIMIT = 8
            for i, snap in enumerate(snapshots):
                local_dt = tz.localtime(snap.timestamp) if snap.timestamp else tz.localtime(submission.started_at)
                dt_iso = snap.timestamp.isoformat() if snap.timestamp else submission.started_at.isoformat()
                
                screenshot_base64 = None
                webcam_screenshot_base64 = None
                
                if i < INLINE_LIMIT:
                    if snap.screenshot:
                        try:
                            import base64
                            with snap.screenshot.open('rb') as f:
                                screenshot_base64 = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"
                        except Exception as e:
                            logger.error(f"Error encoding screenshot to base64 for snap {snap.id}: {e}")
                    
                    if snap.webcam_screenshot:
                        try:
                            import base64
                            with snap.webcam_screenshot.open('rb') as f:
                                webcam_screenshot_base64 = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"
                        except Exception as e:
                            logger.error(f"Error encoding webcam_screenshot to base64 for snap {snap.id}: {e}")

                logs.append({
                    'id': f'integrity_{snap.id}',
                    'event_type': snap.event_type.upper(),
                    'status': 'FAILURE' if 'failed' in snap.event_type or 'mismatch' in snap.event_type or 'warning' in snap.event_type or 'switches' in snap.event_type else 'INFO',
                    'phase': 'INTEGRITY',
                    'batch_id': getattr(submission, 'batch_id', None),
                    'message': f"Integrity Event: {snap.event_type.replace('_', ' ').title()}",
                    'details': {
                        'screenshot': request.build_absolute_uri(snap.screenshot.url) if snap.screenshot else (request.build_absolute_uri(snap.webcam_screenshot.url) if snap.webcam_screenshot else 'N/A')
                    },
                    'timestamp': dt_iso,
                    'timestamp_formatted': local_dt.strftime('%B %d, %Y at %I:%M %p'),
                    'has_screenshot': bool(snap.screenshot),
                    'has_webcam_screenshot': bool(snap.webcam_screenshot),
                    'screenshot_id': snap.id,
                    'screenshot_base64': screenshot_base64,
                    'webcam_screenshot_base64': webcam_screenshot_base64,
                })

            # Sort logs by timestamp
            logs.sort(key=lambda x: x['timestamp'])

            return Response(logs)
        except AIAssessmentSubmission.DoesNotExist:
            return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)

class AIAssessmentSubmissionListView(APIView):
    def get(self, request):
        candidate_email = request.query_params.get('candidate_email')
        batch_name = request.query_params.get('batch_name')
        batch_id = request.query_params.get('batch_id')
        submission_id = request.query_params.get('submission_id')
        
        if not candidate_email and not submission_id:
            return Response({"error": "candidate_email or submission_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        qs = AIAssessmentSubmission.objects.all()
        if candidate_email:
            qs = qs.filter(candidate_email__iexact=candidate_email)
        if batch_name:
            qs = qs.filter(batch_name=batch_name)
        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        if submission_id:
            qs = qs.filter(id=submission_id.replace('ai_', '') if str(submission_id).startswith('ai_') else submission_id)
            
        submissions = qs.order_by('-submitted_at')
        
        data = []
        from django.utils import timezone
        for sub in submissions:
            integrity_snapshots = AIAssessmentIntegrityScreenshot.objects.filter(submission=sub).order_by('timestamp')
            screenshots_data = []
            for snap in integrity_snapshots:
                screenshots_data.append({
                    "event_type": snap.event_type,
                    "timestamp": snap.timestamp.isoformat() if snap.timestamp else None,
                    "screenshot_url": request.build_absolute_uri(snap.screenshot.url) if snap.screenshot else None,
                    "webcam_screenshot_url": request.build_absolute_uri(snap.webcam_screenshot.url) if snap.webcam_screenshot else None,
                    "has_screenshot": bool(snap.screenshot),
                    "has_webcam_screenshot": bool(snap.webcam_screenshot),
                    "screenshot_id": snap.id,
                })

            photo_url = _get_candidate_photo_url(request, sub)

            data.append({
                "id": sub.id,
                "submission_id": f"ai_{sub.id}",
                "candidate_name": sub.candidate_name,
                "candidate_email": sub.candidate_email,
                "job_title": sub.assessment.required_skills,
                "role": sub.assessment.required_skills,
                "assessment_name": sub.assessment.required_skills,
                "score": sub.score,
                "mcq_score": sub.mcq_score,
                "coding_score": sub.coding_score,
                "results_breakdown": sub.results_breakdown,
                "percentage": sub.percentage,
                "status": sub.status,
                "final_status": sub.status,
                "integrity_score": sub.integrity_score,
                "submitted_at": timezone.localtime(sub.submitted_at).strftime("%Y-%m-%d %H:%M") if sub.submitted_at else None,
                "candidate_questions": sub.candidate_questions,
                "answers": sub.answers,
                "integrity_screenshots": screenshots_data,
                "is_resume_screening": False,
                "candidate_photo_url": photo_url,
                "pan_photo": request.build_absolute_uri(sub.pan_photo.url) if sub.pan_photo else None,
                "assessment": {
                    "id": sub.assessment.id,
                    "display_name": sub.assessment.required_skills,
                    "name": sub.assessment.required_skills
                },
                # Identity mismatch fields
                **_get_unified_identity_mismatch_fields(request, sub),
            })
        return Response({"results": data}, status=status.HTTP_200_OK)


class AIAssessmentResultsView(APIView):
    """
    AI Assessment results overview with PAN authentication fields.
    Separate endpoint to keep custom assessment logic untouched.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from api.utils.role_utils import get_scoped_user_ids
        
        user_profile = getattr(request.user, 'profile', None)
        company_id = user_profile.company_id if user_profile and user_profile.company else None
        scoped_ids = get_scoped_user_ids(user_profile) if user_profile else []
        
        # Query AI assessment submissions based on user role/scope
        if scoped_ids is None:
            # Application Admin: all results across ALL companies
            if company_id:
                ai_qs = AIAssessmentSubmission.objects.filter(
                    assessment__company_id=company_id,
                    is_deleted=False
                ).select_related('assessment').order_by('-submitted_at')
            else:
                ai_qs = AIAssessmentSubmission.objects.filter(
                    is_deleted=False
                ).select_related('assessment').order_by('-submitted_at')
        elif scoped_ids:
            # Role-scoped: results for assessments created by this user's hierarchy
            ai_qs = AIAssessmentSubmission.objects.filter(
                assessment__user_profile_id__in=scoped_ids,
                is_deleted=False
            ).select_related('assessment').order_by('-submitted_at')
        else:
            ai_qs = AIAssessmentSubmission.objects.none()
        
        # Date filtering
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date:
            ai_qs = ai_qs.filter(submitted_at__date__gte=start_date)
        if end_date:
            ai_qs = ai_qs.filter(submitted_at__date__lte=end_date)
        
        # Active deletions tracking
        active_deletions = set()
        try:
            from api.models import DeletionRequest
            for dr in DeletionRequest.objects.filter(status='pending'):
                active_deletions.add(f"AIAssessmentSubmission_{dr.object_id}")
        except Exception:
            pass
        
        results = []
        
        for s in ai_qs[:5000]:
            a = s.assessment
            
            # Fetch integrity screenshots for this submission
            integrity_snapshots = AIAssessmentIntegrityScreenshot.objects.filter(submission=s).order_by('timestamp')
            screenshots_data = []
            for snap in integrity_snapshots:
                screenshots_data.append({
                    "event_type": snap.event_type,
                    "timestamp": snap.timestamp.isoformat() if snap.timestamp else None,
                    "screenshot_url": request.build_absolute_uri(snap.screenshot.url) if snap.screenshot else None,
                    "webcam_screenshot_url": request.build_absolute_uri(snap.webcam_screenshot.url) if snap.webcam_screenshot else None,
                    "has_screenshot": bool(snap.screenshot),
                    "has_webcam_screenshot": bool(snap.webcam_screenshot),
                    "screenshot_id": snap.id,
                })
            
            results.append({
                'id': s.id,
                'submission_id': f"ai_{s.id}",
                'submitted_at': s.submitted_at.isoformat() if getattr(s, 'submitted_at', None) else (s.started_at.isoformat() if getattr(s, 'started_at', None) else None),
                'candidate_name': getattr(s, 'candidate_name', 'Unknown'),
                'candidate_email': getattr(s, 'candidate_email', 'Unknown'),
                'full_name': getattr(s, 'candidate_name', 'Unknown'),
                'email': getattr(s, 'candidate_email', 'Unknown'),
                'candidate': {
                    'name': getattr(s, 'candidate_name', 'Unknown'),
                    'email': getattr(s, 'candidate_email', 'Unknown'),
                },
                'assessment': {
                    'id': f"ai_{a.id}",
                    'display_name': getattr(a, 'required_skills', str(a.id)),
                    'name': getattr(a, 'required_skills', str(a.id)),
                    'weightage_objective': getattr(a, 'mcq_weight', 40) or 40,
                    'weightage_coding': 100 - (getattr(a, 'mcq_weight', 40) or 40),
                },
                'score': getattr(s, 'score', 0),
                'total': getattr(s, 'total_possible', 100),
                'percentage': getattr(s, 'percentage', 0),
                'objective_score': getattr(s, 'results_breakdown', {}).get('mcq', {}).get('scored_points', 0),
                'objective_total': getattr(s, 'results_breakdown', {}).get('mcq', {}).get('possible_points', 0),
                'objective_percentage': getattr(s, 'mcq_score', 0),
                'coding_score': getattr(s, 'results_breakdown', {}).get('coding', {}).get('scored_points', 0),
                'coding_total': getattr(s, 'results_breakdown', {}).get('coding', {}).get('possible_points', 0),
                'coding_percentage': getattr(s, 'coding_score', 0),
                'status': getattr(s, 'status', 'COMPLETED'),
                'total_questions': getattr(s, 'total_questions', 0),
                'candidate_questions': getattr(s, 'candidate_questions', None) or getattr(a, 'generated_content', {}),
                'answers': getattr(s, 'answers', {}),
                'results_breakdown': getattr(s, 'results_breakdown', {}),
                'mcq_score': getattr(s, 'mcq_score', 0),
                'integrity': {
                    'integrity_score': getattr(s, 'integrity_score', 100.0),
                    'warning_logs': getattr(s, 'warning_logs', [])
                },
                'integrity_screenshots': screenshots_data,
                'is_resume_screening': False,
                'batch_id': s.batch_id,
                'batch_name': s.batch_name or (a.batch_name if hasattr(a, 'batch_name') else None),
                'is_fully_automatic': getattr(a, 'creation_type', 'manual') == 'automatic',
                'delete_requested': f"AIAssessmentSubmission_{s.id}" in active_deletions,
                'candidate_photo_url': _get_candidate_photo_url(request, s),
                # PAN authentication fields
                'phone': getattr(s, 'phone', None),
                'pan_number': getattr(s, 'pan_number', None),
                'pan_photo': request.build_absolute_uri(s.pan_photo.url) if getattr(s, 'pan_photo', None) else None,
                'pan_verified': getattr(s, 'pan_verified', False),
                # Identity Override Fields
                'identity_mismatch_detected': getattr(s, 'identity_mismatch_detected', False),
                'original_identity_photo_url': getattr(s, 'original_identity_photo', None),
                'intruder_photo_url': getattr(s, 'intruder_photo', None),
                'identity_mismatch_details': getattr(s, 'identity_mismatch_details', {}),
                'photo_update_pending': bool(s.identity_mismatch_detected and s.intruder_photo),
                'photo_update_approved': bool(s.identity_mismatch_details.get('photo_update_approved', False)) if isinstance(s.identity_mismatch_details, dict) else False,
                'pending_identity_photo_url': s.intruder_photo if s.intruder_photo else None,
                'master_photo_url': s.original_identity_photo if s.original_identity_photo else None,
                'is_assessment': True,
                'ai_candidate_pk': s.id,
            })
        
        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)


class OverrideSubmissionStatusView(APIView):
    """
    HR manually approves or rejects a Hold candidate.
    PATCH /api/ai/submission/<pk>/override-status/
    Body: { "action": "approve" | "reject", "reason": "optional note" }
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
        except AIAssessmentSubmission.DoesNotExist:
            return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action', '').lower()
        reason = request.data.get('reason', 'HR manual review override')

        if action not in ('approve', 'reject'):
            return Response(
                {'error': 'Invalid action. Use "approve" or "reject".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if submission.status != 'hold':
            return Response(
                {'error': f'Submission is not on hold (current status: {submission.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if action == 'approve':
            submission.status = 'selected'
            submission.save(update_fields=['status'])
            logger.info(
                f"HR Override: Submission {pk} APPROVED by {request.user}. Reason: {reason}"
            )

            # Only trigger interview pipeline for AUTOMATIC assessments.
            # For MANUAL assessments, HR approval = qualified only — no interview link sent.
            is_automatic = getattr(submission.assessment, 'creation_type', 'manual') == 'automatic'
            if is_automatic:
                try:
                    from api.pipeline import process_assessment_passed
                    process_assessment_passed(submission.id)
                    logger.info(f"HR Override: Pipeline triggered for submission {pk}")
                except Exception as pipe_err:
                    logger.error(f"HR Override: Pipeline trigger failed for {pk}: {pipe_err}")
                message = 'Candidate approved. Interview invitation will be sent.'
            else:
                logger.info(f"HR Override: Manual assessment — candidate marked as selected, no interview link sent.")
                message = 'Candidate approved and marked as qualified.'

            return Response({
                'message': message,
                'status': 'selected',
                'submission_id': pk
            }, status=status.HTTP_200_OK)

        else:  # reject
            submission.status = 'rejected'
            submission.save(update_fields=['status'])
            logger.info(
                f"HR Override: Submission {pk} REJECTED by {request.user}. Reason: {reason}"
            )
            return Response({
                'message': 'Candidate rejected.',
                'status': 'rejected',
                'submission_id': pk
            }, status=status.HTTP_200_OK)


class ApproveAssessmentIdentityPhotoView(APIView):
    """
    POST /api/ai/submission/<pk>/approve-photo/
    Approves the overriding face mismatch photo for an AI Assessment submission:
      1. Pushes the intruder/mismatch photo to DeepFace as the new master face for this PAN / token.
      2. Promotes the intruder_photo to the original_identity_photo (updating the baseline).
      3. Clears the identity_mismatch_detected flag.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
        except AIAssessmentSubmission.DoesNotExist:
            return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)

        # Authorization: must belong to the same company
        user_profile = getattr(request.user, 'profile', None)
        if user_profile and user_profile.company and submission.assessment.company_id != user_profile.company_id:
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        mismatch_data = _get_unified_identity_mismatch_fields(request, submission)
        intruder_url = mismatch_data.get("intruder_photo_url")
        
        b64_str = None
        if intruder_url and intruder_url.startswith("data:image"):
            b64_str = intruder_url
            
        if not b64_str:
            # Fallback to the database webcam frame
            b64_str = getattr(submission, 'intruder_photo', None)
                
        if not b64_str:
            return Response(
                {'error': 'No mismatch/intruder photo to approve for this submission.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_automatic = getattr(submission.assessment, 'creation_type', 'manual') == 'automatic' if getattr(submission, 'assessment', None) else False

        # 1. Read intruder_photo and base64 encode it for DeepFace registration.
        # This will update the master face in DeepFace for BOTH manual and automated assessments.
        try:
            import base64
            b64_str = b64_str.strip()
            if b64_str.startswith('identity_overrides/'):
                from django.conf import settings
                from pathlib import Path
                file_path = Path(settings.MEDIA_ROOT) / b64_str
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        b64_data = base64.b64encode(f.read()).decode('utf-8')
                else:
                    raise FileNotFoundError(f"Legacy path {file_path} not found")
            else:
                if ',' in b64_str and b64_str.startswith('data:'):
                    b64_data = b64_str.split(',', 1)[1]
                else:
                    b64_data = b64_str
            
            # DeepFace registration: person_id is PAN Card if available, otherwise email_token
            pan = getattr(submission, 'pan_number', None)
            if pan and pan.strip():
                person_id = pan.lower().strip()
            else:
                email = submission.candidate_email.strip().lower()
                token = submission.assessment.share_token
                person_id = f"{email}_{token}"
            
            # Register with deepface — overwrite=True to replace the old face
            _register_face_with_deepface(person_id, b64_data, overwrite=True)
            logger.info(f"[ApproveAssessmentPhoto] DeepFace re-registered master profile for {person_id}")
            
            # Also update the assessment-specific snapshot so the UI immediately reflects the approved photo
            if getattr(submission, 'assessment', None) and getattr(submission.assessment, 'share_token', None):
                assessment_person_id = f"{person_id}/assessments/{submission.assessment.share_token}"
                try:
                    _register_face_with_deepface(assessment_person_id, b64_data, overwrite=True)
                    logger.info(f"[ApproveAssessmentPhoto] DeepFace re-registered assessment profile for {assessment_person_id}")
                except Exception as e:
                    logger.warning(f"[ApproveAssessmentPhoto] Failed to update assessment-specific DeepFace profile: {e}")
        except Exception as e:
            logger.exception(f"[ApproveAssessmentPhoto] Failed to push to DeepFace: {e}")
            return Response(
                {'error': f'Could not update DeepFace: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 2. Clear identity mismatch flags and optionally promote intruder_photo to original_identity_photo.
        try:
            submission.original_identity_photo = b64_data
            
            submission.identity_mismatch_detected = False
            
            details = submission.identity_mismatch_details or {}
            details['photo_approved_at'] = timezone.now().isoformat()
            details['photo_approved_by'] = request.user.email if hasattr(request.user, 'email') else str(request.user)
            details['photo_update_approved'] = True
            submission.identity_mismatch_details = details
            submission.save()
            
            # 3. Also update the unified IdentityLink so it cascades everywhere
            from api.models import IdentityLink
            from django.core.files.base import ContentFile
            email = submission.candidate_email.lower().strip() if submission.candidate_email else None
            if email:
                try:
                    identity = IdentityLink.objects.filter(email__iexact=email).order_by('-updated_at').first()
                    if identity:
                        image_data = base64.b64decode(b64_data)
                        identity.snapshot_image.save(f"approved_{submission.id}.jpg", ContentFile(image_data), save=False)
                        identity.save(update_fields=['snapshot_image', 'updated_at'])
                        logger.info(f"[ApproveAssessmentPhoto] Updated IdentityLink for {email}")
                except Exception as e:
                    logger.error(f"[ApproveAssessmentPhoto] Failed to update IdentityLink: {e}")

        except Exception as e:
            logger.exception(f"[ApproveAssessmentPhoto] Save error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                'success': True,
                'message': 'Assessment identity photo approved and updated successfully.',
                'submission_id': submission.id,
            },
            status=status.HTTP_200_OK,
        )