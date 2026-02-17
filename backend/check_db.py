import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import AIAssessmentSubmission, Assessment

def check_db():
    print(f"Total AI Assessments: {Assessment.objects.count()}")
    print(f"Total AI Submissions: {AIAssessmentSubmission.objects.count()}")
    for s in AIAssessmentSubmission.objects.all():
        print(f"Submission: {s.candidate_name} ({s.candidate_email}) - Score: {s.score}/{s.total_questions}")

if __name__ == "__main__":
    check_db()
