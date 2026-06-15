import os
import sys
import django

# Add the backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import CandidateSubmission, CandidateDetails, IdentityLink

# Locally define _get_filtered_warning_logs like candidate_assessment_views.py does at the top
def _get_filtered_warning_logs(warning_logs):
    if not isinstance(warning_logs, list):
        return []
    filtered = []
    for log in warning_logs:
        filtered.append(log)
    return filtered

import re

try:
    submission_id = 214
    sub_str = str(submission_id)
    
    sub_id = int(sub_str)
    s = CandidateSubmission.objects.select_related('invitation', 'invitation__assessment', 'invitation__integrity').get(id=sub_id)
    
    inv = s.invitation
    a = inv.assessment
    pan = inv.pan_number or getattr(inv, 'pan_number', None)
    phone = inv.phone or getattr(inv, 'phone', None)
    
    # Fetch latest candidate details
    latest_details = CandidateDetails.objects.filter(token=inv.token).first()
    if not latest_details and inv.email:
        latest_details = CandidateDetails.objects.filter(email=inv.email).first()
        
    original_identity_photo_url = None
    if latest_details:
        pan = latest_details.pan_number or pan
        phone = latest_details.phone or phone
        norm_pan = re.sub(r'[^A-Z0-9]', '', latest_details.pan_number.strip().upper()) if latest_details.pan_number else ""
        link = IdentityLink.objects.filter(pan_number=norm_pan).first()
        if not link and latest_details.email:
            link = IdentityLink.objects.filter(email=latest_details.email.strip().lower()).first()
        if link and link.snapshot_image:
            original_identity_photo_url = link.snapshot_image.url
            
    # Gather active deletions
    active_deletions = set()
    try:
        from api.models import DeletionRequest
        for dr in DeletionRequest.objects.filter(status='pending'):
            active_deletions.add(f"CandidateSubmission_{dr.object_id}")
            active_deletions.add(f"{dr.content_type}_{dr.object_id}")
    except Exception as e:
        print(f"Error gathering active deletions: {e}")

    data = {
        'submission_id': s.id,
        'invitation_id': inv.id,
        'submitted_at': s.submitted_at.isoformat() if s.submitted_at else None,
        'candidate': {
            'name': inv.name,
            'email': inv.email,
            'pan_number': pan,
            'phone': phone,
        },
        'assessment': {
            'id': a.id,
            'display_name': a.display_name,
            'name': a.name,
            'weightage_objective': a.weightage_objective,
            'weightage_coding': a.weightage_coding,
            'min_pass_percentage': a.min_pass_percentage,
        },
        'score': s.score,
        'total': s.total,
        'percentage': s.final_percentage if s.final_percentage is not None else s.percentage,
        
        'objective_score': s.objective_score,
        'objective_total': s.objective_total,
        'objective_percentage': s.objective_percentage,
        
        'coding_score': s.coding_score,
        'coding_total': s.coding_total,
        'coding_percentage': s.coding_percentage,
        'batch_id': inv.batch_id,
        'batch_name': inv.batch_name,

        'status': s.result,
        'termination_reason': (s.answers or {}).get('_termination', {}).get('reason') if isinstance(s.answers, dict) else None,
        'termination_detail': (s.answers or {}).get('_termination', {}).get('detail') if isinstance(s.answers, dict) else None,
        'qual_pending': False,
        'delete_requested': f"CandidateSubmission_{s.id}" in active_deletions,
        'answers': getattr(s, 'answers', {}),
        'integrity': {
            'integrity_score': getattr(inv.integrity, 'integrity_score', 100.0) if hasattr(inv, 'integrity') else 100.0,
            'warning_logs': _get_filtered_warning_logs(getattr(inv.integrity, 'warning_logs', [])) if hasattr(inv, 'integrity') else []
        },
        'activity_logs': list(inv.activity_logs) if isinstance(inv.activity_logs, list) else [],
        'regret_email_sent': s.regret_email_sent,
        'created_at': inv.created_at.isoformat() if inv.created_at else None,

        # Identity mismatch fields
        'identity_mismatch_detected': (latest_details.identity_mismatch_detected or latest_details.identity_mismatch) if latest_details else False,
        'identity_mismatch_reason': latest_details.identity_mismatch_reason if latest_details else None,
        'original_identity_photo_url': original_identity_photo_url,
        'candidate_photo_url': latest_details.snapshot if latest_details else None,
        'photo_update_approved': latest_details.photo_update_approved if latest_details else False,
        'photo_update_approved_by': latest_details.photo_update_approved_by if latest_details else None,
        'photo_update_approved_at': latest_details.photo_update_approved_at.isoformat() if (latest_details and latest_details.photo_update_approved_at) else None,
        'photo_update_reason': latest_details.photo_update_reason if latest_details else None,
        'previous_registered_face_url': latest_details.previous_registered_face_backup.url if (latest_details and latest_details.previous_registered_face_backup) else None,
        'photo_update_status': latest_details.photo_update_status if latest_details else 'none',
        'photo_update_admin_note': latest_details.photo_update_admin_note if latest_details else None,
        'deepface_distance': latest_details.deepface_distance if latest_details else None,
        'deepface_threshold': latest_details.deepface_threshold if latest_details else None,
        'deepface_verified': latest_details.deepface_verified if latest_details else None,
        'deepface_model': latest_details.deepface_model if latest_details else None,
        'deepface_detector': latest_details.deepface_detector if latest_details else None,
        'original_image_path': latest_details.original_image_path if latest_details else None,
        'captured_image_path': latest_details.captured_image_path if latest_details else None,
        'original_image_hash': latest_details.original_image_hash if latest_details else None,
        'captured_image_hash': latest_details.captured_image_hash if latest_details else None,
        'report_original_hash': latest_details.report_original_hash if latest_details else None,
        'report_captured_hash': latest_details.report_captured_hash if latest_details else None,
        'image_source_mismatch': latest_details.image_source_mismatch if latest_details else False,
    }
    print("SUCCESS: JSON serialized successfully!")
    print(f"identity_mismatch_detected: {data['identity_mismatch_detected']}")
    print(f"photo_update_status: {data['photo_update_status']}")
    print(f"photo_update_approved: {data['photo_update_approved']}")

except Exception as e:
    import traceback
    traceback.print_exc()
