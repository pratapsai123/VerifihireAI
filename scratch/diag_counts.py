import os
import sys
import django

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate
from django.db.models import Count

print("--- Candidate Status Stats ---")
stats = Candidate.objects.values('status').annotate(count=Count('id')).order_by('-count')
for s in stats:
    print(f"Status: '{s['status']}', Count: {s['count']}")

print("\n--- Total Candidates ---")
print(Candidate.objects.count())

from ai_assessments.models import AIAssessmentSubmission
print("\n--- AI Assessment Submission Stats ---")
ai_stats = AIAssessmentSubmission.objects.values('status').annotate(count=Count('id')).order_by('-count')
for s in ai_stats:
    print(f"Status: '{s['status']}', Count: {s['count']}")

from api.models import CandidateSubmission
print("\n--- Candidate Submission Stats ---")
cs_stats = CandidateSubmission.objects.count()
print(f"Total CandidateSubmissions: {cs_stats}")
