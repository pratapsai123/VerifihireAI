import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import InterviewInvitation, CandidateInvitation, CandidateDetails

email = 'saipratap65@gmail.com'
print(f"--- Records for {email} ---")

print("\n[InterviewInvitation]")
for i in InterviewInvitation.objects.filter(email=email):
    print(f"  ID: {i.id}, Token: {i.token}, Status: {i.status}, Created: {i.created_at}")

print("\n[CandidateInvitation]")
for i in CandidateInvitation.objects.filter(email=email):
    print(f"  ID: {i.id}, Token: {i.token}, Status: {i.status}, Created: {i.created_at}")

print("\n[CandidateDetails]")
for i in CandidateDetails.objects.filter(email=email):
    print(f"  ID: {i.id}, Token: {i.token}, Created: {i.created_at}")

print("\n--- Listing ALL InterviewInvitations (just in case email differs) ---")
for i in InterviewInvitation.objects.all().order_by('-created_at'):
    print(f"  ID: {i.id}, Email: {i.email}, Token: {i.token}")
