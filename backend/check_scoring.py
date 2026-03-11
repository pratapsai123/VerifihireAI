import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append(r'c:\Users\D-IT\Desktop\verifirehire\VerifiHireAI\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment, AIAssessmentSubmission
from ai_assessments.views import SubmitAssessmentView
from rest_framework.test import APIRequestFactory
from django.utils import timezone

def test_scoring():
    factory = APIRequestFactory()
    view = SubmitAssessmentView.as_view()
    
    # Mock data
    gen_content = {
        "mcqs": [
            {"question": "Q1", "options": ["A", "B"], "correct_answer": "A"},
            {"question": "Q2", "options": ["X", "Y"], "answer": "X"}
        ],
        "coding_challenges": [
            {"title": "C1", "difficulty": "Easy", "test_cases": [{"input": "1", "output": "1"}]}
        ]
    }
    
    # Create a dummy assessment
    assessment = Assessment.objects.create(
        job_description="Test JD",
        required_skills="Python",
        generated_content=gen_content,
        pass_threshold=50
    )
    
    # Mock request data
    data = {
        "token": str(assessment.share_token),
        "name": "Test Candidate",
        "email": "test@example.com",
        "answers": {
            "mcq_0": "A", # Correct (uses correct_answer)
            "mcq_1": "X", # Correct (uses answer)
            "coding_0": "print(1)" # Dummy
        },
        "codingResults": {
            "0": {"passed": 1, "total": 1} # 100% pass
        }
    }
    
    request = factory.post('/api/ai/submit/', data, format='json')
    response = view(request)
    
    print(f"Status: {response.status_code}")
    print(f"Data: {response.data}")
    
    if response.status_code == 200:
        submission = AIAssessmentSubmission.objects.get(id=response.data['submission_id'])
        print(f"Submission Score: {submission.score}")
        print(f"Results Breakdown: {submission.results_breakdown}")
        
        # Possible points: 
        # MCQs: 20 * 2 = 40
        # Coding (Easy): 100
        # Total: 140
        # Candidate: 40 + 100 = 140 (100%)
        
        if submission.percentage == 100:
            print("✅ Scoring Test Passed!")
        else:
            print(f"❌ Scoring Test Failed! Expected 100%, got {submission.percentage}%")
    else:
        print("❌ View call failed!")

if __name__ == "__main__":
    test_scoring()
