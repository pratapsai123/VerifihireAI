import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment, AIAssessmentSubmission

print("--- AI Assessments ---")
# Use a filter that doesn't rely on company to see everything
for a in Assessment.objects.order_by('-created_at')[:20]:
    sub_count = AIAssessmentSubmission.objects.filter(assessment=a).count()
    print(f"ID: {a.id}, Skills: {a.required_skills}, Created: {a.created_at}, Submissions: {sub_count}")

print("\n--- Recent Submissions ---")
for s in AIAssessmentSubmission.objects.order_by('-submitted_at')[:20]:
    print(f"ID: {s.id}, Candidate: {s.candidate_name}, Email: {s.candidate_email}, Assessment ID: {s.assessment_id}, Submitted: {s.submitted_at}")
