import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append(r'c:\Users\D-IT\Desktop\verifirehire\VerifiHireAI\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment, AIAssessmentSubmission
from ai_assessments.views import SaveAssessmentProgressView, CreateSubmissionView
from rest_framework.test import APIRequestFactory

def test_progress():
    factory = APIRequestFactory()
    
    # Create a dummy assessment
    assessment = Assessment.objects.create(
        job_description="Test JD",
        required_skills="Python",
        generated_content={"mcqs": [], "coding_challenges": []}
    )
    
    # Create a dummy submission
    submission = AIAssessmentSubmission.objects.create(
        assessment=assessment,
        candidate_name="Test Candidate",
        candidate_email="progress@example.com",
        status='ONGOING'
    )
    
    # 1. Test Saving Progress
    save_view = SaveAssessmentProgressView.as_view()
    progress_data = {
        "answers": {"mcq_0": "A"},
        "current_question_index": 1,
        "codingResults": {"0": {"passed": 2, "total": 2}}
    }
    
    request = factory.post(f'/api/ai/submission/{submission.id}/progress/', progress_data, format='json')
    response = save_view(request, pk=submission.id)
    
    print(f"Save Status: {response.status_code}")
    
    # 2. Test Restoration (CreateSubmissionView reconnect logic)
    create_view = CreateSubmissionView.as_view()
    reconnect_data = {
        "share_token": str(assessment.share_token),
        "candidate_name": "Test Candidate",
        "candidate_email": "progress@example.com"
    }
    
    request = factory.post('/api/ai/submit/create/', reconnect_data, format='json')
    response = create_view(request)
    
    print(f"Restore Status: {response.status_code}")
    print(f"Restored codingResults: {response.data.get('codingResults')}")
    
    if response.data.get('codingResults') == progress_data['codingResults']:
        print("✅ Progress Persistence Test Passed!")
    else:
        print(f"❌ Progress Persistence Test Failed! Expected {progress_data['codingResults']}, got {response.data.get('codingResults')}")

if __name__ == "__main__":
    test_progress()
