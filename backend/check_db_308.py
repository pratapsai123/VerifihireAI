import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.db import connection

def check_id(pk):
    with connection.cursor() as cursor:
        print(f"--- Checking ID {pk} ---")
        
        # Check Candidate
        cursor.execute("SELECT id, full_name, email, is_deleted FROM ai_candidates_candidate WHERE id = %s", [pk])
        candidate = cursor.fetchone()
        print(f"Candidate table: {candidate}")
        
        # Check AIAssessmentSubmission
        cursor.execute("SELECT id, candidate_name, candidate_email, is_deleted FROM ai_assessment_submission WHERE id = %s", [pk])
        submission = cursor.fetchone()
        print(f"AIAssessmentSubmission table: {submission}")
        
        # Check Assessment
        cursor.execute("SELECT id, required_skills, share_token FROM ai_assessments_assessment WHERE id = %s", [pk])
        assessment = cursor.fetchone()
        print(f"Assessment table: {assessment}")

if __name__ == "__main__":
    check_id(308)
