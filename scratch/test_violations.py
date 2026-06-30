import os
import sys
import django
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import InterviewInvitation, InterviewViolation, Interview, Company
from api.serializers import InterviewViolationSerializer
from api.views.live_interview_views import get_interview_violations_by_id_view
from rest_framework.test import APIRequestFactory

def run_test():
    print("Starting verification of get_interview_violations_by_id_view...")
    
    # 1. Find or create an InterviewInvitation
    invite = InterviewInvitation.objects.first()
    if not invite:
        print("No InterviewInvitation found. Creating a temporary one for testing...")
        company = Company.objects.first()
        interview = Interview.objects.create(name="Test Interview", company=company)
        invite = InterviewInvitation.objects.create(
            interview=interview,
            name="Test Candidate",
            email="test_candidate@example.com",
            status="accepted"
        )
    else:
        print(f"Using existing InterviewInvitation ID: {invite.id}")

    # 2. Clear existing violations on this invitation to ensure controlled test case
    InterviewViolation.objects.filter(candidate=invite).delete()
    print("Cleared any existing violations for this candidate.")

    # 3. Create test violations: 1 HIGH, 2 MEDIUM, 1 LOW
    # High = 20, Medium = 10, Low = 5
    # Expected Risk Score = 20 + 20 + 5 = 45 -> Integrity Status: Suspicious
    print("Creating test violations...")
    v1 = InterviewViolation.objects.create(
        candidate=invite,
        violation_type="MULTIPLE_FACES",
        severity="HIGH",
        duration=0
    )
    v2 = InterviewViolation.objects.create(
        candidate=invite,
        violation_type="TAB_SWITCH",
        severity="MEDIUM",
        duration=15
    )
    v3 = InterviewViolation.objects.create(
        candidate=invite,
        violation_type="NO_FACE",
        severity="MEDIUM",
        duration=8
    )
    v4 = InterviewViolation.objects.create(
        candidate=invite,
        violation_type="LOOKING_AWAY",
        severity="LOW",
        duration=0
    )

    # 4. Trigger the view via APIRequestFactory
    factory = APIRequestFactory()
    request = factory.get(f'/api/interviews/{invite.id}/violations/')
    
    print("Invoking get_interview_violations_by_id_view view...")
    response = get_interview_violations_by_id_view(request, interview_id=invite.id)
    
    print(f"Response Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.data
    print("\n--- API Response Data ---")
    import json
    print(json.dumps(data, indent=2))
    print("-------------------------\n")

    # Verify counts and points
    assert data["total_violations"] == 4, f"Expected 4 violations, got {data['total_violations']}"
    assert data["high_count"] == 1, f"Expected 1 High, got {data['high_count']}"
    assert data["medium_count"] == 2, f"Expected 2 Medium, got {data['medium_count']}"
    assert data["low_count"] == 1, f"Expected 1 Low, got {data['low_count']}"
    
    # Risk score: 1*20 + 2*10 + 1*5 = 45
    assert data["risk_score"] == 45, f"Expected risk score 45, got {data['risk_score']}"
    assert data["integrity_status"] == "Suspicious", f"Expected integrity status 'Suspicious', got {data['integrity_status']}"
    
    # Verify violation_summary
    v_summary = data.get("violation_summary", {})
    assert v_summary.get("MULTIPLE_FACES") == 1
    assert v_summary.get("TAB_SWITCH") == 1
    assert v_summary.get("NO_FACE") == 1
    assert v_summary.get("LOOKING_AWAY") == 1
    print("violation_summary verified successfully!")

    print("Calculations and Response structure verified successfully!")

    # 5. Test another threshold: adding another HIGH violation to cross the 51+ threshold
    # 45 + 20 = 65 -> High Risk
    print("\nAdding one more HIGH violation to test 'High Risk' threshold...")
    InterviewViolation.objects.create(
        candidate=invite,
        violation_type="UNAUTHORIZED_DEVICE",
        severity="HIGH",
        duration=0
    )
    
    response = get_interview_violations_by_id_view(request, interview_id=invite.id)
    data = response.data
    print(f"New Risk Score: {data['risk_score']} (Expected: 65)")
    print(f"New Integrity Status: {data['integrity_status']} (Expected: High Risk)")
    
    assert data["risk_score"] == 65
    assert data["integrity_status"] == "High Risk"

    # Cleanup temporary violations
    InterviewViolation.objects.filter(candidate=invite).delete()
    print("Verification completed successfully and test data cleaned up!")

if __name__ == '__main__':
    run_test()
