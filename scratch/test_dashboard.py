import os
import sys
import django

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from api.views.dashboard_views import dashboard_summary_view

User = get_user_model()
user = User.objects.first()  # Retrieve a user to run the authenticated request
print("Testing with User:", user.email if user else "None")

if user:
    from rest_framework.test import APIRequestFactory, force_authenticate
    
    factory = APIRequestFactory()
    request = factory.get('/api/dashboard/summary/')
    force_authenticate(request, user=user)
    
    response = dashboard_summary_view(request)
    print("Response Status Code:", response.status_code)
    if response.status_code == 200:
        data = response.data
        print("\n--- Summary Statistics ---")
        for key, val in data['stats'].items():
            print(f"{key}: {val}")
        
        print("\n--- Recent Candidates ---")
        for idx, cand in enumerate(data['recentCandidates']):
            print(f"{idx}: {cand['candidate']['name']} ({cand['candidate']['email']}) -> Status: {cand['status']}, Date: {cand['submitted_at']}")
            
        print("\n--- Trends (Total) Sample ---")
        for trend in data['trendsTotal']:
            print(trend)
            
        print("\n--- Success Rate Sample ---")
        print(data['successRate'])
    else:
        print("Error:", response.data)
else:
    print("No user found in the database.")
