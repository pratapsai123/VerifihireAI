import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import InterviewInvitation, UserProfile, Company
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from api.views.live_interview_views import draft_interview_invitations_view
from django.db import models

def test_draft_deletion():
    print("Testing draft invitation deletion fix...")
    
    # 1. Setup a test user and company
    email = "test_del_new@example.com"
    company_name = "Test Deletion Co"
    
    # Clean up any existing data from previous failed runs
    User.objects.filter(email=email).delete()
    Company.objects.filter(name=company_name).delete()
    
    company = Company.objects.create(name=company_name)
    user = User.objects.create(username=email, email=email)
    user_profile = UserProfile.objects.create(
        email=email, 
        user=user, 
        company=company,
        role=UserProfile.ROLE_HR_MANAGER,
        first_name="Test",
        last_name="User"
    )
    
    # 2. Create an orphan draft (interview=None)
    draft = InterviewInvitation.objects.create(
        name="Candidate One",
        email="cand1@example.com",
        status='draft',
        interview=None
    )
    draft_id = draft.id
    print(f"Created orphan draft ID: {draft_id}")
    
    factory = APIRequestFactory()
    
    # 3. Try to delete the draft
    print(f"Attempting to delete draft ID {draft_id}...")
    request = factory.delete(f'/api/interviews/draft-invites/{draft_id}/')
    request.user = user
    # Refresh user from DB to ensure 'profile' attribute is available via related_name
    user = User.objects.get(id=user.id)
    request.user = user
    
    request.data = {'reason': 'Testing fix'}
    
    response = draft_interview_invitations_view(request, draft_id=draft_id)
    
    print(f"Status Code: {response.status_code}")
    # print(f"Response Data: {response.data}")
    
    # Success conditions:
    # - 200: Successfully deleted (if user is Admin or hierarchy allows)
    # - 201: Deletion request created (if policy requires it)
    # - 400: Failed at specific workflow step (but draft was found!)
    
    success = False
    if response.status_code in [200, 201]:
        print("SUCCESS: Draft was found and deletion process handled.")
        success = True
    elif response.status_code == 400:
        error_msg = str(response.data.get('error', '')).lower()
        if "approver found" in error_msg:
             print("SUCCESS: Draft was found (no 404!), but failed at approver lookup (expected in this dummy setup).")
             success = True
        else:
             print(f"FAILURE: Unexpected 400 error: {response.data.get('error')}")
    else:
        print(f"FAILURE: Unexpected status code {response.status_code}. Data: {response.data}")
        
    # 4. Cleanup
    InterviewInvitation.objects.filter(id=draft_id).delete()
    user_profile.delete()
    user.delete()
    company.delete()
    
    return success

if __name__ == "__main__":
    success = test_draft_deletion()
    sys.exit(0 if success else 1)
