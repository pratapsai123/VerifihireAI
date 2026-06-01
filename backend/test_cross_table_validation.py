import os
import django
import sys
import base64
import re
import json
from io import BytesIO
from PIL import Image

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.test import Client
from django.utils import timezone
from django.core.files.base import ContentFile

from api.models import (
    Company, Assessment, CandidateInvitation, CandidateDetails, IdentityLink
)
from ai_assessments.models import (
    Assessment as AIAssessment, AIAssessmentSubmission
)
from ai_candidates.models import Candidate
from api.ocr_utils import (
    perform_cross_table_identity_validation, verify_two_faces_with_deepface
)

def get_real_face_b64(face_type='A'):
    if face_type == 'A':
        path = "media/identities/ADBPE8898A/canonical.jpg"
    else:
        path = "media/identities/XYZWV5678B/canonical.jpg"
    
    with open(path, "rb") as f:
        data = f.read()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()

email = "crosstabletest@verifihire.com"
pan_ok = "ABCDE1234F"
pan_bad = "XYZWV5678B"
pan_other = "GHIJK9012L"

def reset_db():
    CandidateInvitation.objects.filter(email__iexact=email).delete()
    CandidateDetails.objects.filter(email__iexact=email).delete()
    IdentityLink.objects.filter(email__iexact=email).delete()
    AIAssessmentSubmission.objects.filter(candidate_email__iexact=email).delete()
    Candidate.objects.filter(email__iexact=email).delete()

def create_baseline(pan1, pan2, pan3, face2_type, face3_type):
    reset_db()
    company, _ = Company.objects.get_or_create(name="Test Validation Company")
    assessment = Assessment.objects.create(
        name="Test Assessment",
        total_questions=10,
        total_time="01:00:00"
    )
    invitation = CandidateInvitation.objects.create(
        assessment=assessment,
        email=email,
        name="Test Candidate",
        pan_number=pan1
    )
    
    if pan2:
        CandidateDetails.objects.create(
            token=invitation.token,
            email=email,
            first_name="Test",
            last_name="Candidate",
            phone="9876543210",
            pan_number=pan2,
            snapshot=get_real_face_b64(face2_type),
            identity_mismatch_detected=False
        )
        
    if pan3:
        face3_bytes = base64.b64decode(get_real_face_b64(face3_type).split(',', 1)[1])
        face3_file = ContentFile(face3_bytes, name="details_face.jpg")
        IdentityLink.objects.create(
            email=email,
            pan_number=pan3,
            snapshot_image=face3_file
        )
        
    return invitation

def run_tests():
    print("--- Starting Production-Ready Strict Cross-Table Identity Validation Tests ---")
    
    # -------------------------------------------------------------------------
    # TEST CASE 1: All three tables contain the same PAN and same face.
    # Submitted PAN and face match. Expected Result: Assessment Allowed.
    # -------------------------------------------------------------------------
    print("\n[Test Case 1]: Perfect Match (Assessment Allowed)")
    create_baseline(pan_ok, pan_ok, pan_ok, 'A', 'A')
    has_mismatch, reasons = perform_cross_table_identity_validation(email, pan_ok, get_real_face_b64('A'))
    print(f"Mismatch: {has_mismatch}, Reasons: {reasons}")
    if not has_mismatch and len(reasons) == 0:
        print("PASS")
    else:
        print("FAIL")

    # -------------------------------------------------------------------------
    # TEST CASE 2: Table 1 PAN differs from Table 2 and Table 3.
    # Expected Result: Cross-table PAN mismatch flag.
    # -------------------------------------------------------------------------
    print("\n[Test Case 2]: Table 1 PAN Differs (Cross-table PAN mismatch)")
    create_baseline(pan_bad, pan_ok, pan_ok, 'A', 'A')
    has_mismatch, reasons = perform_cross_table_identity_validation(email, pan_ok, get_real_face_b64('A'))
    print(f"Mismatch: {has_mismatch}, Reasons: {reasons}")
    if has_mismatch and any("PAN Number Mismatch Across Verification Sources" in r for r in reasons):
        print("PASS")
    else:
        print("FAIL")

    # -------------------------------------------------------------------------
    # TEST CASE 3: Table 2 face differs from Table 1 and Table 3.
    # Expected Result: Cross-table face mismatch flag.
    # -------------------------------------------------------------------------
    print("\n[Test Case 3]: Table 2 Face Differs (Cross-table face mismatch)")
    create_baseline(pan_ok, pan_ok, pan_ok, 'B', 'A')
    has_mismatch, reasons = perform_cross_table_identity_validation(email, pan_ok, get_real_face_b64('A'))
    print(f"Mismatch: {has_mismatch}, Reasons: {reasons}")
    if has_mismatch and any("Candidate Face Mismatch Across Verification Sources" in r for r in reasons):
        print("PASS")
    else:
        print("FAIL")

    # -------------------------------------------------------------------------
    # TEST CASE 4: PAN and face mismatch across multiple tables.
    # Expected Result: Multiple mismatch reasons and assessment blocked.
    # -------------------------------------------------------------------------
    print("\n[Test Case 4]: Multiple Mismatch Across Tables (PAN & Face mismatch)")
    create_baseline(pan_bad, pan_ok, pan_other, 'B', 'A')
    has_mismatch, reasons = perform_cross_table_identity_validation(email, pan_ok, get_real_face_b64('A'))
    print(f"Mismatch: {has_mismatch}, Reasons: {reasons}")
    if has_mismatch and len(reasons) > 1:
        print("PASS")
    else:
        print("FAIL")

    # -------------------------------------------------------------------------
    # TEST CASE 5: Tables match but submitted PAN is different.
    # Expected Result: Submitted PAN mismatch flag.
    # -------------------------------------------------------------------------
    print("\n[Test Case 5]: Submitted PAN Mismatch")
    create_baseline(pan_ok, pan_ok, pan_ok, 'A', 'A')
    has_mismatch, reasons = perform_cross_table_identity_validation(email, pan_bad, get_real_face_b64('A'))
    print(f"Mismatch: {has_mismatch}, Reasons: {reasons}")
    if has_mismatch and any("Submitted PAN Does Not Match Verified Identity" in r for r in reasons):
        print("PASS")
    else:
        print("FAIL")

    # -------------------------------------------------------------------------
    # TEST CASE 6: Tables match but current webcam face is different.
    # Expected Result: Face verification mismatch flag.
    # -------------------------------------------------------------------------
    print("\n[Test Case 6]: Current Webcam Face Mismatch")
    create_baseline(pan_ok, pan_ok, pan_ok, 'A', 'A')
    has_mismatch, reasons = perform_cross_table_identity_validation(email, pan_ok, get_real_face_b64('B'))
    print(f"Mismatch: {has_mismatch}, Reasons: {reasons}")
    if has_mismatch and any("Current Face Does Not Match Verified Identity" in r for r in reasons):
        print("PASS")
    else:
        print("FAIL")

    # -------------------------------------------------------------------------
    # TEST CASE 7: Standard/Custom Assessment flow validation.
    # Verify 403 response and Hold status.
    # -------------------------------------------------------------------------
    print("\n[Test Case 7]: Custom/Standard save_all_candidate_details_view Integration")
    invitation = create_baseline(pan_ok, pan_ok, pan_ok, 'A', 'A')
    client = Client()
    post_data = {
        'token': str(invitation.token),
        'full_name': 'Test Candidate',
        'email': email,
        'phone': '9876543210',
        'pan_number': pan_bad,  # Trigger submitted PAN mismatch
        'snapshot': get_real_face_b64('A')
    }
    # Delete the newly created details record so we can test posting
    CandidateDetails.objects.filter(token=invitation.token).delete()
    
    response = client.post('/api/candidate-details/', data=post_data)
    print(f"API Response Code: {response.status_code}")
    
    details = CandidateDetails.objects.filter(token=invitation.token).first()
    if details:
        print(f"Details Mismatch Detected flag: {details.identity_mismatch_detected}")
        print(f"Details Photo Update Status: {details.photo_update_status}")
        
    if response.status_code == 403 and details and details.identity_mismatch_detected and details.photo_update_status == 'pending':
        print("PASS")
    else:
        print("FAIL")

    # -------------------------------------------------------------------------
    # TEST CASE 8: AI Assessment flow validation.
    # Verify 403 response and Hold status.
    # -------------------------------------------------------------------------
    print("\n[Test Case 8]: AI Assessment CreateSubmissionView Integration")
    create_baseline(pan_ok, pan_ok, pan_ok, 'A', 'A')
    ai_assessment = AIAssessment.objects.create(
        job_description="Test Job",
        required_skills="Python",
        total_points=100
    )
    ai_post_data = {
        'share_token': str(ai_assessment.share_token),
        'candidate_name': 'Test Candidate',
        'candidate_email': email,
        'phone': '9876543210',
        'pan_number': pan_bad,  # Trigger submitted PAN mismatch
        'snapshot': get_real_face_b64('A')
    }
    response_ai = client.post('/api/ai/submit/create/', data=ai_post_data)
    print(f"AI API Response Code: {response_ai.status_code}")
    
    submission = AIAssessmentSubmission.objects.filter(candidate_email=email).first()
    if submission:
        print(f"Submission Status: {submission.status}")
        print(f"Submission Mismatch Detected flag: {submission.identity_mismatch_detected}")
        
    if response_ai.status_code == 403 and submission and submission.status == 'hold' and submission.identity_mismatch_detected:
        print("PASS")
    else:
        print("FAIL")

    # -------------------------------------------------------------------------
    # TEST CASE 9: AI Interview flow validation.
    # Verify 403 response and Hold status.
    # -------------------------------------------------------------------------
    print("\n[Test Case 9]: AI Interview CandidateRegistrationUpdateView Integration")
    create_baseline(pan_ok, pan_ok, pan_ok, 'A', 'A')
    candidate_interview = Candidate.objects.create(
        full_name="Test Candidate",
        email=email,
        status="New"
    )
    interview_post_data = {
        'phone': '9876543210',
        'pan_number': pan_bad,  # Trigger submitted PAN mismatch
        'snapshot_b64': get_real_face_b64('A')
    }
    response_interview = client.post(
        f'/api/ai-candidates/public/{candidate_interview.public_token}/register/',
        data=interview_post_data
    )
    print(f"Interview API Response Code: {response_interview.status_code}")
    
    cand = Candidate.objects.filter(public_token=candidate_interview.public_token).first()
    if cand:
        print(f"Candidate Status: {cand.status}")
        print(f"Candidate Mismatch Detected flag: {cand.identity_mismatch_detected}")
        
    if response_interview.status_code == 403 and cand and cand.status == 'On-Hold' and cand.identity_mismatch_detected:
        print("PASS")
    else:
        print("FAIL")

    # Cleanup test data
    reset_db()

if __name__ == '__main__':
    run_tests()
