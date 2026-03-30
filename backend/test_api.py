import os
import sys
import json
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import UserProfile
from api.views.candidate_assessment_views import results_overview_view
from rest_framework.test import APIRequestFactory, force_authenticate

User = get_user_model()
# Find a user with a profile (preferably company admin to see data)
user_profile = UserProfile.objects.filter(user__is_active=True).first()
if getattr(user_profile, 'company', None):
    # Try to find a company admin
    ca_profile = UserProfile.objects.filter(user__is_active=True, role='company_admin').first()
    if ca_profile:
        user_profile = ca_profile

user = user_profile.user

factory = APIRequestFactory()
request = factory.get('/api/results/')
force_authenticate(request, user=user)

response = results_overview_view(request)

with open("api_response.json", "w") as f:
    json.dump(response.data, f, indent=2)

print(f"Request made as user: {user.email}")
print(f"Company: {getattr(user_profile, 'company', None)}")
print(f"Role: {getattr(user_profile, 'role', None)}")
print(f"Response status: {response.status_code}")
print(f"Number of results: {len(response.data.get('results', []))}")
