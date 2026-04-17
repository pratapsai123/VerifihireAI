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

def test_deleted_draft_hidden():
    print("Testing visibility of deleted drafts...")
    
    # 1. Setup a test user and company
    email = "test_vis@example.com"
    company_name = "Test Visibility Co"
    
    User.objects.filter(email=email).delete()
    Company.objects.filter(name=company_name).delete()
    
    company = Company.objects.create(name=company_name)
    user = User.objects.create(username=email, email=email)
    UserProfile.objects.create(
        email=email, 
        user=user, 
        company=company,
        role=UserProfile.ROLE_HR_MANAGER
    )
    
    # 2. Create one active draft and one deleted draft
    active_draft = InterviewInvitation.objects.create(name="Active", email="active@ex.com", status='draft', is_deleted=False)
    deleted_draft = InterviewInvitation.objects.create(name="Deleted", email="deleted@ex.com", status='draft', is_deleted=True)
    
    factory = APIRequestFactory()
    
    # 3. Call GET endpoint
    request = factory.get('/api/interviews/draft-invites/')
    request.user = user
    # Ensure user.profile exists (related name)
    user = User.objects.get(id=user.id)
    request.user = user
    
    response = draft_interview_invitations_view(request)
    
    print(f"Status Code: {response.status_code}")
    results = response.data.get('results', [])
    print(f"Number of results returned: {len(results)}")
    
    found_active = any(d['id'] == active_draft.id for d in results)
    found_deleted = any(d['id'] == deleted_draft.id for d in results)
    
    print(f"Active draft found: {found_active}")
    print(f"Deleted draft found: {found_deleted}")
    
    success = found_active and not found_deleted
    
    if success:
        print("SUCCESS: Only active drafts were returned.")
    else:
        print("FAILURE: Incorrect filtering logic.")
        
    # 4. Cleanup
    active_draft.delete()
    deleted_draft.delete()
    User.objects.filter(email=email).delete()
    company.delete()
    
    return success

if __name__ == "__main__":
    success = test_deleted_draft_hidden()
    sys.exit(0 if success else 1)
