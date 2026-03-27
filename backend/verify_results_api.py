import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.views.candidate_assessment_views import results_overview_view
from rest_framework.test import APIRequestFactory, force_authenticate
from api.models import UserProfile
from django.contrib.auth.models import User

factory = APIRequestFactory()
request = factory.get('/api/results/')

# Find a user to authenticate
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.first()

if user:
    force_authenticate(request, user=user)
    response = results_overview_view(request)
    if response.status_code == 200:
        results = response.data.get('results', [])
        print(f"Found {len(results)} results.")
        for res in results:
            sid = res.get('submission_id', '')
            if sid.startswith('ai_'):
                print(f"Checking AI Result {sid}:")
                fields = ['answers', 'candidate_questions', 'results_breakdown', 'integrity_screenshots', 'mcq_score', 'coding_score']
                for f in fields:
                    if f in res:
                        print(f"  [OK] {f} present")
                    else:
                        print(f"  [MISSING] {f}")
                break
    else:
        print(f"Error: {response.status_code} - {response.data}")
else:
    print("No user found for authentication.")
