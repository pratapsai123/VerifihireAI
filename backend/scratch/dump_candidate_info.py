import os
import django
import sys

sys.path.append('c:\\HireAi\\VerifiHireAI\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import CandidateDetails, CandidateInvitation, CandidateSubmission, IdentityLink, FaceUpdateRequest

print("=== ALL IDENTITY LINKS FOR PANs ===")
for l in IdentityLink.objects.filter(pan_number__in=['ADBPE8898A', 'EPYPG5617E']):
    print(f"ID: {l.id}, Email: {l.email}, PAN: {l.pan_number}")
    print(f"  Snapshot Image: {l.snapshot_image}")

print("\n=== FACE UPDATE REQUESTS FOR EMAIL ===")
reqs = FaceUpdateRequest.objects.filter(candidate_details__email__iexact='kavyasuma.ganjala@iit.org.in')
for r in reqs:
    print(f"ID: {r.id}, Status: {r.status}, CandidateDetails ID: {r.candidate_details_id}")
