import os
import django
import base64
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from api.views.candidate_assessment_views import save_all_candidate_details_view
from api.models import (
    CandidateSubmission, 
    CandidateInvitation, 
    CandidateDetails,
    IdentityLink
)

# 1. Load candidate 166 details (which has valid files on disk)
details_116 = CandidateDetails.objects.get(id=166)
inv_116 = details_116.invitation

print("Mismatched candidate info:")
print("  Name:", details_116.first_name, details_116.last_name)
print("  PAN:", details_116.pan_number)
print("  Email:", details_116.email)

# Prepare base64 webcam snapshot
snapshot_base64 = details_116.snapshot
if ',' not in snapshot_base64:
    snapshot_base64 = "data:image/jpeg;base64," + snapshot_base64

# Prepare PAN file
pan_file_field = details_116.pan_file
pan_file_field.seek(0)
pan_file_content = pan_file_field.read()
pan_file_field.seek(0)
pan_file = ContentFile(pan_file_content, name="pan_temp.jpg")

# 2. Delete any existing IdentityLink for this PAN to simulate first-time registration
norm_pan = "ADBPE8898A"
IdentityLink.objects.filter(pan_number=norm_pan).delete()
print(f"Deleted existing IdentityLinks for PAN {norm_pan} to simulate first registration.")

# 3. Create a new dummy invitation to test registration
test_inv = CandidateInvitation.objects.create(
    email="mismatch_test_user@example.com",
    name="Test User",
    assessment=inv_116.assessment,
    status="active"
)
print("Created temporary test invitation with token:", test_inv.token)

# 4. Mock the save_all_candidate_details_view POST request
factory = APIRequestFactory()
post_data = {
    'token': str(test_inv.token),
    'full_name': 'Test User Mismatch',
    'email': 'mismatch_test_user@example.com',
    'phone': '9999999999',
    'pan_number': norm_pan,
    'snapshot': snapshot_base64,
    'pan_file': pan_file
}

request = factory.post('/api/results/save-all-details/', post_data, format='multipart')

print("\nExecuting save_all_candidate_details_view...")
try:
    response = save_all_candidate_details_view(request)
    print("Response status:", response.status_code)
    print("Response data:", response.data)

    # 5. Check if details were saved and mismatch was flagged
    saved_details = CandidateDetails.objects.filter(invitation=test_inv).first()
    if saved_details:
        print("\nVerification Results:")
        print("  Saved PAN:", saved_details.pan_number)
        print("  Identity Mismatch Detected:", saved_details.identity_mismatch_detected)
        print("  Identity Mismatch (alternative field):", saved_details.identity_mismatch)
        print("  Face Match Score:", saved_details.face_match_score)
        print("  Mismatch Reason:", saved_details.identity_mismatch_reason)
    else:
        print("\nCandidate details were not saved!")
finally:
    # Cleanup
    test_inv.delete()
    print("\nTemporary test invitation deleted.")
