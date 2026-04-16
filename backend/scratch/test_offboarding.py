import os
import sys
import django
import json

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import (
    UserProfile, Assessment, CustomAssessment, CandidateInvitation,
    JobRole, Question, UserInvitation, Interview, InterviewInvitation,
    OwnershipTransferLog
)
from api.views.hr_offboarding_views import _preview_counts

def test_preview():
    print("Testing _preview_counts...")
    # Get a random active user who has some data
    user = UserProfile.objects.filter(is_active=True).first()
    if not user:
        print("No user found.")
        return

    counts = _preview_counts(user)
    print(f"User: {user.email}")
    print(json.dumps(counts, indent=2))
    
    # Check for new fields
    expected_keys = [
        "assessments", "custom_assessments", "candidate_invitations",
        "job_roles", "questions", "user_invitations", "interviews",
        "interview_invitations", "subordinates", "deletion_requests",
        "interview_slots", "interviewer_availability", "coding_questions",
        "coding_invites"
    ]
    for key in expected_keys:
        if key not in counts:
            print(f"MISSING KEY: {key}")
        else:
            print(f"Verified key: {key} = {counts[key]}")

if __name__ == "__main__":
    test_preview()
