import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.test import Client
from ai_candidates.models import Candidate, InterviewIntegrity
from api.models import Company

def run_tests():
    print("--- Starting AI Interview On-Hold Logic Tests ---")
    
    # 1. Setup a dummy company
    company, _ = Company.objects.get_or_create(name="Test Company")

    client = Client()

    def create_candidate(name, public_token, score, total_questions, threshold, integrity_score):
        # Create candidate
        c = Candidate.objects.create(
            full_name=name,
            email=f"{public_token}@test.com",
            public_token=public_token,
            company=company,
            score=score,
            total_questions=total_questions,
            interview_pass_threshold=threshold,
            status='Interview'
        )
        # Set integrity score
        InterviewIntegrity.objects.create(
            candidate=c,
            integrity_score=integrity_score
        )
        return c

    import uuid

    # ---------------------------------------------------------
    # TEST CASE 1: ON-HOLD
    # Raw Score: 80% (Passes 50% threshold)
    # Integrity Score: 60% (Penalty = 40%)
    # Final Score: 80 - 40 = 40% (Fails 50% threshold)
    # Expected Status: On-Hold
    # ---------------------------------------------------------
    print("\n[Test Case 1]: On-Hold Logic (Passed Raw, Failed Integrity Penalty)")
    token1 = str(uuid.uuid4())
    c1 = create_candidate("Test OnHold", token1, score=80, total_questions=10, threshold=50, integrity_score=60.0)
    
    response1 = client.patch(f'/api/ai-candidates/public/{c1.public_token}/status/', 
                             data={'status': 'Completed'}, content_type='application/json')
    
    c1.refresh_from_db()
    print(f"API Response: {response1.status_code}")
    print(f"Resulting Status: {c1.status}")
    if c1.status == 'On-Hold':
        print("✅ PASS")
    else:
        print("❌ FAIL")


    # ---------------------------------------------------------
    # TEST CASE 2: REJECTED
    # Raw Score: 40% (Fails 50% threshold)
    # Integrity Score: 100% (Penalty = 0%)
    # Final Score: 40 - 0 = 40% (Fails 50% threshold)
    # Expected Status: Rejected
    # ---------------------------------------------------------
    print("\n[Test Case 2]: Rejected Logic (Failed Raw Score)")
    token2 = str(uuid.uuid4())
    c2 = create_candidate("Test Rejected", token2, score=40, total_questions=10, threshold=50, integrity_score=100.0)
    
    response2 = client.patch(f'/api/ai-candidates/public/{c2.public_token}/status/', 
                             data={'status': 'Completed'}, content_type='application/json')
    
    c2.refresh_from_db()
    print(f"API Response: {response2.status_code}")
    print(f"Resulting Status: {c2.status}")
    if c2.status == 'Rejected':
        print("✅ PASS")
    else:
        print("❌ FAIL")


    # ---------------------------------------------------------
    # TEST CASE 3: HIRED
    # Raw Score: 90% (Passes 50% threshold)
    # Integrity Score: 90% (Penalty = 10%)
    # Final Score: 90 - 10 = 80% (Passes 50% threshold)
    # Expected Status: Hired
    # ---------------------------------------------------------
    print("\n[Test Case 3]: Hired Logic (Passed Raw, Passed Final Score)")
    token3 = str(uuid.uuid4())
    c3 = create_candidate("Test Hired", token3, score=90, total_questions=10, threshold=50, integrity_score=90.0)
    
    response3 = client.patch(f'/api/ai-candidates/public/{c3.public_token}/status/', 
                             data={'status': 'Completed'}, content_type='application/json')
    
    c3.refresh_from_db()
    print(f"API Response: {response3.status_code}")
    print(f"Resulting Status: {c3.status}")
    if c3.status == 'Hired':
        print("✅ PASS")
    else:
        print("❌ FAIL")


    print("\n--- Cleaning up test data ---")
    c1.delete()
    c2.delete()
    c3.delete()
    print("Cleanup finished.")


if __name__ == "__main__":
    run_tests()
