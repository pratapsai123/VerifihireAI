import os
import django
import uuid

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import InterviewInvitation, CandidateInvitation

tokens = ["d101107a-2bac-4123-8721-866e20cb0ff8", "eea9546a-d97d-495c-86a9-0f650958c44a"]

print("--- Database Token Inspection ---")

for t_str in tokens:
    try:
        u = uuid.UUID(t_str)
        print(f"\nChecking token: {t_str}")
        
        # Check InterviewInvitation
        ii = InterviewInvitation.objects.filter(token=u).first()
        if ii:
            print(f"  [InterviewInvitation] FOUND! ID: {ii.id}, Email: {ii.email}, Interview: {ii.interview_id}, Status: {ii.status}")
        else:
            print(f"  [InterviewInvitation] Not found.")
            
        # Check CandidateInvitation
        ci = CandidateInvitation.objects.filter(token=u).first()
        if ci:
            print(f"  [CandidateInvitation] FOUND! ID: {ci.id}, Email: {ci.email}, Status: {ci.status}")
        else:
            print(f"  [CandidateInvitation] Not found.")
            
    except Exception as e:
        print(f"  Error processing {t_str}: {e}")

print("\n--- Summary of Recent Interview Invitations ---")
recent_ii = InterviewInvitation.objects.all().order_by('-created_at')[:5]
for inv in recent_ii:
    print(f"ID: {inv.id}, Email: {inv.email}, Token: {inv.token}, Status: {inv.status}")

print("\n--- Summary of Recent Candidate Invitations ---")
recent_ci = CandidateInvitation.objects.all().order_by('-created_at')[:5]
for inv in recent_ci:
    print(f"ID: {inv.id}, Email: {inv.email}, Token: {inv.token}")
