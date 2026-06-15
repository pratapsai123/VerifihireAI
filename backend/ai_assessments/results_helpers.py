from ai_candidates.models import Candidate
from ai_assessments.models import AIAssessmentSubmission, AIAssessmentIntegrityScreenshot
import base64
import os

def _encode_image_field_to_b64(img_field):
    if not img_field or not getattr(img_field, 'name', None):
        return None
    try:
        if hasattr(img_field, 'path') and os.path.exists(img_field.path):
            with open(img_field.path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
                ext = img_field.path.split('.')[-1].lower()
                mime = "image/png" if ext == "png" else "image/jpeg"
                return f"data:{mime};base64,{b64}"
    except Exception:
        pass
    return None


def get_ai_assessment_results(scoped_ids, company_id, start_date, end_date, request, active_deletions, pending_qual_ai_ids=None, is_list=True, submission_id=None):
    from ai_assessments.views import _get_candidate_photo_url, _get_unified_identity_mismatch_fields
    if pending_qual_ai_ids is None:
        pending_qual_ai_ids = set()
        
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
    """
    Query and format AIAssessmentSubmission results for the results overview.
    Returns a list of dicts matching the unified results schema.
    """
    if submission_id:
        ai_qs = AIAssessmentSubmission.objects.filter(id=submission_id).select_related('assessment')
    elif scoped_ids is None:
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
        ai_qs = AIAssessmentSubmission.objects.filter(
            assessment__user_profile_id__in=scoped_ids,
            is_deleted=False
        ).select_related('assessment').order_by('-submitted_at')
    else:
        ai_qs = AIAssessmentSubmission.objects.none()

    if not submission_id:
        if start_date:
            ai_qs = ai_qs.filter(submitted_at__date__gte=start_date)
        if end_date:
            ai_qs = ai_qs.filter(submitted_at__date__lte=end_date)

    # Pre-fetch approved qualification requests for these submissions
    # so we know which ones were explicitly reviewed by admin/HR
    try:
        from api.models import QualificationRequest
        approved_ai_ids = set(
            QualificationRequest.objects.filter(
                content_type=QualificationRequest.CONTENT_AI,
                status=QualificationRequest.STATUS_APPROVED,
            ).values_list('ai_submission_id', flat=True)
        )
        # Convert to int set for comparison
        approved_ai_ids = {int(x) for x in approved_ai_ids if x and str(x).isdigit()}
    except Exception:
        approved_ai_ids = set()

    results = []
    for s in ai_qs[:5000]:
        a = s.assessment

        if is_list:
            screenshots_data = []
            pan_photo_url = None
            candidate_photo_url = None
            detected = getattr(s, 'identity_mismatch_detected', False)
            details = getattr(s, 'identity_mismatch_details', {})
            photo_approved = bool(details.get('photo_update_approved', False)) if isinstance(details, dict) else False
            photo_update_pending = bool(detected and not photo_approved)
            mismatch_fields = {
                "identity_mismatch_detected": detected,
                "original_identity_photo_url": None,
                "intruder_photo_url": None,
                "identity_mismatch_details": details,
                "photo_update_pending": photo_update_pending,
                "photo_update_approved": photo_approved,
                "pending_identity_photo_url": None,
                "master_photo_url": None,
                "is_assessment": True,
                "ai_candidate_pk": s.id,
            }
        else:
            from ai_assessments.models import AIAssessmentIntegrityScreenshot
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
                })
            pan_photo_url = _encode_image_field_to_b64(s.pan_photo) or (request.build_absolute_uri(s.pan_photo.url) if getattr(s, 'pan_photo', None) else None)
            candidate_photo_url = _get_candidate_photo_url(request, s) or clean_b64(s.original_identity_photo)
            mismatch_fields = _get_unified_identity_mismatch_fields(request, s)

        results.append(
            {
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
                'qual_pending': s.id in pending_qual_ai_ids,
                'was_approved': s.id in approved_ai_ids,
                'total_questions': getattr(s, 'total_questions', 0),
                'candidate_questions': getattr(s, 'candidate_questions', None) or getattr(a, 'generated_content', {}),
                'answers': getattr(s, 'answers', {}),
                'results_breakdown': getattr(s, 'results_breakdown', {}),
                'mcq_score': getattr(s, 'mcq_score', 0),
                'integrity': {
                    'integrity_score': getattr(s, 'integrity_score', 100.0),
                    'warning_logs': getattr(s, 'warning_logs', [])
                },
                'integrity_score': getattr(s, 'integrity_score', 100.0),
                'integrity_screenshots': screenshots_data,
                'is_resume_screening': False,
                'batch_id': s.batch_id,
                'batch_name': s.batch_name or (a.batch_name if hasattr(a, 'batch_name') else None),
                'is_fully_automatic': getattr(a, 'creation_type', 'manual') == 'automatic',
                'delete_requested': f"AIAssessmentSubmission_{s.id}" in active_deletions,
                'phone': getattr(s, 'phone', None),
                'pan_number': getattr(s, 'pan_number', None),
                'pan_photo': pan_photo_url,
                'pan_verified': getattr(s, 'pan_verified', False),
                'candidate_photo_url': candidate_photo_url,
                **mismatch_fields
            }
        )

    return results


def _get_candidate_photo_url_for_candidate(request, candidate):
    """
    Returns the registered face URL for this candidate interview.
    Prioritizes checking the unified IdentityLink for this candidate's email.
    Otherwise prioritizes the candidate's PAN number folder if available.
    Otherwise checks public_token folder.
    Falls back to first non-empty webcam integrity screenshot if registration missing.
    """
    email = candidate.email.lower().strip() if candidate.email else None

    # Priority 0: DB-stored registered face (always the most recent verified photo for this specific assessment).
    if getattr(candidate, 'registered_face_b64', None):
        return f"data:image/jpeg;base64,{candidate.registered_face_b64}"
        
    db_photo = getattr(candidate, 'original_identity_photo', None)
    if db_photo and len(db_photo) > 1000:
        if not db_photo.startswith('data:image'):
            return f"data:image/jpeg;base64,{db_photo}"
        return db_photo

    # Priority 0.5: Historically accurate assessment-specific snapshot (Prevents later candidates with same PAN from overriding past exam photos)
    try:
        from pathlib import Path
        import base64
        deepface_data_dir = Path(__file__).resolve().parent.parent.parent / 'deepface' / 'data' / 'registered_faces'
        
        # Determine the token depending on if it's an AIAssessmentSubmission or AI Candidate
        token_str = None
        if hasattr(candidate, 'assessment') and getattr(candidate.assessment, 'share_token', None):
            token_str = str(candidate.assessment.share_token)
        elif getattr(candidate, 'public_token', None):
            token_str = str(candidate.public_token)
            
        if token_str:
            p_id = getattr(candidate, 'pan_number', '').lower().strip() or email or token_str
            # Support both manual assessments (assessments/<token>) and fully automated sessions (sessions/<token>)
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

    # Priority 1: Check unified IdentityLink
    if email:
        try:
            from api.models import IdentityLink
            identities = IdentityLink.objects.filter(email__iexact=email).order_by('-id')
            for identity in identities:
                if identity.snapshot_image and identity.snapshot_image.name:
                    return request.build_absolute_uri(identity.snapshot_image.url) if request else identity.snapshot_image.url
        except Exception:
            pass

    # Priority 2: Check deepface registered folders
    from pathlib import Path
    import os
    deepface_data_dir = Path(__file__).resolve().parent.parent.parent / 'deepface' / 'data' / 'registered_faces'

    # Try PAN
    if getattr(candidate, 'pan_number', None):
        pan_id = candidate.pan_number.lower().strip()
        pan_face_dir = deepface_data_dir / pan_id
        if pan_face_dir.exists() and any(pan_face_dir.glob('*.jpg')):
            url_path = f"/api/ai/registration/face/{pan_id}/"
            return request.build_absolute_uri(url_path) if request else url_path

    # Try public token
    if getattr(candidate, 'public_token', None):
        token_id = str(candidate.public_token).lower().strip()
        token_face_dir = deepface_data_dir / token_id
        if token_face_dir.exists() and any(token_face_dir.glob('*.jpg')):
            url_path = f"/api/ai/registration/face/{token_id}/"
            return request.build_absolute_uri(url_path) if request else url_path

    # Try email
    if email:
        email_face_dir = deepface_data_dir / email
        if email_face_dir.exists() and any(email_face_dir.glob('*.jpg')):
            url_path = f"/api/ai/registration/face/{email}/"
            return request.build_absolute_uri(url_path) if request else url_path

    # Fallback: first non-empty webcam screenshot from integrity logs
    try:
        logs = candidate.integrity_logs.filter(
            webcam_screenshot_base64__isnull=False
        ).exclude(
            event_type__icontains='face_not_detected'
        ).order_by('id')
        for log in logs:
            if len(log.webcam_screenshot_base64) > 1000:
                base64_str = log.webcam_screenshot_base64
                if not base64_str.startswith('data:image'):
                    return f"data:image/jpeg;base64,{base64_str}"
                return base64_str
    except Exception:
        pass

    return None


def _get_candidate_intruder_photo_url(candidate):
    """
    Extract the intruder's webcam base64 screenshot from mismatch event logs.
    """
    try:
        logs = candidate.integrity_logs.filter(
            event_type__in=['face_mismatch', 'verification_failed', 'face_mismatch_on_reentry'],
            webcam_screenshot_base64__isnull=False
        ).order_by('id')
        for log in logs:
            if len(log.webcam_screenshot_base64) > 1000:
                base64_str = log.webcam_screenshot_base64
                if not base64_str.startswith('data:image'):
                    return f"data:image/jpeg;base64,{base64_str}"
                return base64_str
        
        # Second fallback: any webcam snapshot containing mismatch
        logs = candidate.integrity_logs.filter(
            event_type__icontains='mismatch',
            webcam_screenshot_base64__isnull=False
        ).order_by('id')
        for log in logs:
            if len(log.webcam_screenshot_base64) > 1000:
                base64_str = log.webcam_screenshot_base64
                if not base64_str.startswith('data:image'):
                    return f"data:image/jpeg;base64,{base64_str}"
                return base64_str
    except Exception:
        pass
    return None


def get_ai_candidate_results(scoped_ids, company_id, start_date, end_date, active_deletions, pending_qual_ai_ids=None, request=None, is_list=True, candidate_id=None):
    if pending_qual_ai_ids is None:
        pending_qual_ai_ids = set()
    """
    Query and format AI Candidate (voice interview) results for the results overview.
    Returns a list of dicts matching the unified results schema.
    """
    if candidate_id:
        ai_cand_qs = Candidate.objects.filter(id=candidate_id).defer('resume_text', 'conversation_memory').prefetch_related('integrity', 'integrity_logs')
    elif scoped_ids is None:
        if company_id:
            ai_cand_qs = Candidate.objects.filter(
                company_id=company_id,
                is_deleted=False,
            ).defer('resume_text', 'conversation_memory').prefetch_related('integrity', 'integrity_logs').order_by('-submission_date')
        else:
            ai_cand_qs = Candidate.objects.filter(
                is_deleted=False,
                status__in=['Completed', 'Hired', 'Rejected', 'Resume Passed', 'Resume Failed', 'Extraction Failed']
            ).defer('resume_text', 'conversation_memory').prefetch_related('integrity', 'integrity_logs').order_by('-submission_date')
    elif scoped_ids:
        ai_cand_qs = Candidate.objects.filter(
            user_profile_id__in=scoped_ids,
            is_deleted=False,
        ).defer('resume_text', 'conversation_memory').prefetch_related('integrity', 'integrity_logs').order_by('-submission_date')
    else:
        ai_cand_qs = Candidate.objects.none()

    if not candidate_id:
        if start_date:
            ai_cand_qs = ai_cand_qs.filter(submission_date__gte=start_date)
        if end_date:
            ai_cand_qs = ai_cand_qs.filter(submission_date__lte=end_date)

    results = []
    for s in ai_cand_qs[:5000]:
        submitted_date_iso = s.completed_at.isoformat() if getattr(s, 'completed_at', None) else (s.created_at.isoformat() if getattr(s, 'created_at', None) else None)
        
        if is_list:
            integrity_logs = []
            pan_photo_url = None
            candidate_photo_url = None
            orig_identity_photo_url = None
            master_photo_url = None
            pending_identity_photo_url = None
            photo_update_pending = bool(s.identity_mismatch_detected and not getattr(s, 'photo_update_approved', False))
            intruder_photo_url = None
        else:
            integrity_logs = [
                {
                    'event_type': log.event_type,
                    'screenshot_base64': None,
                    'webcam_screenshot_base64': None,
                    'has_screenshot': bool(log.screenshot_base64),
                    'has_webcam_screenshot': bool(log.webcam_screenshot_base64),
                    'screenshot_id': log.id,
                    'timestamp': log.timestamp.isoformat() if log.timestamp else None
                } for log in s.integrity_logs.all()
            ]
            pan_photo_url = request.build_absolute_uri(s.pan_photo.url) if request and getattr(s, 'pan_photo', None) and getattr(s.pan_photo, 'url', None) else None
            candidate_photo_url = _get_candidate_photo_url_for_candidate(request, s)
            orig_identity_photo_url = (
                f"data:image/jpeg;base64,{s.registered_face_b64}"
                if getattr(s, 'registered_face_b64', None)
                else None
            )
            master_photo_url = (
                f"data:image/jpeg;base64,{s.master_face_b64}"
                if getattr(s, 'master_face_b64', None)
                else None
            )
            pending_identity_photo_url = (
                f"data:image/jpeg;base64,{s.pending_face_b64}"
                if getattr(s, 'pending_face_b64', None)
                else None
            )
            photo_update_pending = bool(getattr(s, 'pending_face_b64', None))
            intruder_photo_url = _get_candidate_intruder_photo_url(s)

        results.append(
            {
                'submission_id': f"aicand_{s.id}",
                'submitted_at': submitted_date_iso,
                'candidate_name': s.full_name,
                'candidate_email': s.email,
                'full_name': s.full_name,
                'email': s.email,
                'candidate': {
                    'name': s.full_name,
                    'email': s.email,
                },
                'assessment': {
                    'id': f"aicand_{s.id}",
                    'display_name': s.job_title or "AI Interview",
                    'name': s.job_title or "AI Interview",
                    'weightage_objective': 0,
                    'weightage_coding': 100,
                },
                'score': s.score,
                'total': 100,
                'status': s.status,
                'qual_pending': s.id in pending_qual_ai_ids,
                'is_ai_interview': bool(s.interview_summary or s.status in ['Interview Passed', 'Interview Failed', 'Completed', 'Hired', 'Rejected']),
                'is_ai_candidate': True,
                'is_resume_screening': True,
                'delete_requested': f"Candidate_{s.id}" in active_deletions,
                'interview_summary': s.interview_summary,
                'full_conversation': s.full_conversation,
                'total_questions': getattr(s, 'total_questions', 0),
                'resume_score': getattr(s, 'resume_score', 0),
                'is_fully_automatic': s.automation_settings.get('is_fully_automatic', False) if isinstance(s.automation_settings, dict) else False,
                'batch_id': s.batch_id,
                'batch_name': s.batch_name,
                'integrity': {
                    'integrity_score': getattr(s.integrity, 'integrity_score', 100.0) if hasattr(s, 'integrity') else 100.0,
                    'warning_logs': getattr(s.integrity, 'warning_logs', []) if hasattr(s, 'integrity') else []
                },
                'integrity_logs': integrity_logs,
                'phone': getattr(s, 'phone', None),
                'pan_number': getattr(s, 'pan_number', None),
                'pan_photo': pan_photo_url,
                'pan_verified': getattr(s, 'pan_verified', False),
                'identity_mismatch_detected': s.identity_mismatch_detected,
                'identity_mismatch_details': s.identity_mismatch_details,
                'candidate_photo_url': candidate_photo_url,
                'original_identity_photo_url': orig_identity_photo_url,
                'master_photo_url': master_photo_url,
                'pending_identity_photo_url': pending_identity_photo_url,
                'photo_update_pending': photo_update_pending,
                'photo_update_approved': getattr(s, 'photo_update_approved', False),
                'ai_candidate_pk': s.id,
                'intruder_photo_url': intruder_photo_url,
            }
        )

    return results
