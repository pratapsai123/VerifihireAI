import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from api.views.workflow_views import list_face_requests_view
from api.models import UserProfile

User = get_user_model()
admin_user = User.objects.filter(profile__role=UserProfile.ROLE_COMPANY_ADMIN).first()

if not admin_user:
    # If no company admin profile user, try any user
    admin_user = User.objects.first()

print("Using user:", admin_user.email if admin_user else "None")

factory = APIRequestFactory()
request = factory.get('/api/workflow/face-requests/')
if admin_user:
    force_authenticate(request, user=admin_user)

response = list_face_requests_view(request)
print("Response status:", response.status_code)

data = response.data
target_req = next((r for r in data if r['id'] == 19), None)

if target_req:
    print("Found Request 19 details:")
    print("  Candidate Name:", target_req['candidate_name'])
    print("  Candidate Email:", target_req['candidate_email'])
    print("  Integrity Details:")
    int_details = target_req['integrity_details']
    if int_details:
        for k, v in int_details.items():
            print(f"    {k}: {v}")
    else:
        print("    None")
    print("  Integrity Screenshots count:", len(target_req['integrity_screenshots']))
    for s in target_req['integrity_screenshots']:
        print(f"    - {s['event_type']} at {s['timestamp']}")
else:
    print("Request 19 not found in response!")

print("\n--------------------------------------------------")
print("Testing request_photo_update_view (email contents):")
from api.views.candidate_assessment_views import request_photo_update_view
# We can mock the post call
req_post = factory.post('/api/results/116/request-photo-update/', {'reason': 'Verify mismatch approved'})
if admin_user:
    force_authenticate(req_post, user=admin_user)

# To prevent actual email sending during test, we can mock send_mail
from unittest.mock import patch
with patch('django.core.mail.send_mail') as mock_send_mail:
    from api.models import CandidateDetails, CandidateSubmission
    sub = CandidateSubmission.objects.get(id=116)
    details = CandidateDetails.objects.filter(invitation=sub.invitation).order_by('id').last()
    old_status = details.photo_update_status
    old_snapshot = details.snapshot
    details.photo_update_status = 'none'
    details.snapshot = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
    details.save()
    try:
        resp = request_photo_update_view(req_post, 116)
        print("Response status:", resp.status_code)
        print("Response data:", resp.data)
        if mock_send_mail.called:
            kwargs = mock_send_mail.call_args[1]
            subject = kwargs.get('subject')
            message = kwargs.get('message')
            html_message = kwargs.get('html_message', '')
            print("\nEmail Subject:", subject)
            print("\nEmail Body (text):")
            print(message)
        else:
            print("Email was not sent!")
    finally:
        details.photo_update_status = old_status
        details.snapshot = old_snapshot
        details.save()

