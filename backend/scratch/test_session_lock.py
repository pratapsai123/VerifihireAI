import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VerifiHireAI_backend.settings")
django.setup()

from api.models import CandidateInvitation, Assessment
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

def run():
    client = APIClient()
    
    # 1. Create a mock assessment and invitation
    assessment = Assessment.objects.first()
    if not assessment:
        print("No assessment found in DB. Test assumes at least 1 config exists.")
        return
    
    inv = CandidateInvitation.objects.create(
        assessment=assessment,
        name="Jane Doe",
        email="jane.locktest@verifihire.com"
    )
    token = str(inv.token)
    print(f"Created Invitation Token: {token}")
    
    # Case 1: First browser checks the link without claiming
    print("\n[Case 1] Browser A checks link (check_only=1)")
    response = client.get(f'/api/invitations/public/{token}/?check_only=1', HTTP_X_SESSION_ID='SESSION_A')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("-> OK: Browser A successfully checked link.")

    # Case 2: Second browser simultaneously checks without claiming
    print("\n[Case 2] Browser B checks link before claim")
    response = client.get(f'/api/invitations/public/{token}/?check_only=1', HTTP_X_SESSION_ID='SESSION_B')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("-> OK: Browser B successfully checked link.")

    # Case 3: Browser A Claims the assessment by saving details
    print("\n[Case 3] Browser A saves details (claims the token)")
    dummy_file = SimpleUploadedFile("pan.jpg", b"file_content", content_type="image/jpeg")
    claim_data = {
        'token': token,
        'full_name': 'Jane Doe',
        'email': 'jane.locktest@verifihire.com',
        'phone': '1234567890',
        'pan_number': 'ABCDE1234F',
        'snapshot': 'base64str',
        'pan_file': dummy_file
    }
    
    response = client.post('/api/candidate-details/', claim_data, format='multipart', HTTP_X_SESSION_ID='SESSION_A')
    # Can be 200 or 201 depending on logic
    assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.data}"
    
    # Ensure it's locked
    inv.refresh_from_db()
    assert inv.claimed_session_id == 'SESSION_A', "Token was not claimed by SESSION_A!"
    print("-> OK: Token successfully locked to SESSION_A.")

    # Case 4: Browser A (same session) loads the assessment
    print("\n[Case 4] Browser A loads full assessment")
    response = client.get(f'/api/invitations/public/{token}/', HTTP_X_SESSION_ID='SESSION_A')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("-> OK: Browser A successfully loaded the assessment.")

    # Case 5: Browser B (different session) tries to load full assessment
    print("\n[Case 5] Browser B attempts to load full assessment")
    response = client.get(f'/api/invitations/public/{token}/', HTTP_X_SESSION_ID='SESSION_B')
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    assert 'already in use' in response.data['error']
    print(f"-> OK: Browser B blocked! Error: {response.data['error']}")
    
    # Case 6: Browser B tries to check only
    print("\n[Case 6] Browser B attempts to check_only")
    response = client.get(f'/api/invitations/public/{token}/?check_only=1', HTTP_X_SESSION_ID='SESSION_B')
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    assert 'already in use' in response.data['error']
    print(f"-> OK: Browser B check_only blocked! Error: {response.data['error']}")
    
    # Case 7: Browser B tries to override by submitting candidate details
    print("\n[Case 7] Browser B attempts to claim by saving details")
    dummy_file_b = SimpleUploadedFile("pan2.jpg", b"b_content", content_type="image/jpeg")
    claim_data_b = {
        'token': token,
        'full_name': 'Hacker',
        'email': 'hacker@verifihire.com',
        'phone': '0987654321',
        'pan_number': 'XYZ123',
        'snapshot': 'base64str2',
        'pan_file': dummy_file_b
    }
    response = client.post('/api/candidate-details/', claim_data_b, format='multipart', HTTP_X_SESSION_ID='SESSION_B')
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    assert 'already in use' in response.data['error']
    print(f"-> OK: Browser B detail-save blocked! Error: {response.data['error']}")
    
    print("\nALL LOCK TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run()
