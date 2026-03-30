import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate
from ai_assessments.models import AIAssessmentSubmission
from api.models import CandidateSubmission, JobRole

with open("out_test_db.txt", "w") as f:
    f.write(f"Candidates: {Candidate.objects.count()}\n")
    f.write(f"AIAssessments: {AIAssessmentSubmission.objects.count()}\n")
    f.write(f"CandidateSubmissions: {CandidateSubmission.objects.count()}\n")
    f.write(f"JobRoles: {JobRole.objects.count()}\n\n")

    f.write("Candidate Job Titles and Statuses:\n")
    for c in Candidate.objects.all()[:10]:
        f.write(f"ID: {c.id}, Job Title: {c.job_title}, Status: {c.status}, is_deleted: {getattr(c, 'is_deleted', None)}\n")
