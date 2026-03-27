import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate
from django.db.models import Count

print("--- Candidate Company Stats ---")
companies = Candidate.objects.values('company_id').annotate(count=Count('id'))
for c in companies:
    print(f"Company ID: {c['company_id']}, Count: {c['count']}")

# Also check users/profiles to see what the current user's company is
from api.models import UserProfile
print("\n--- User Profile Stats ---")
profiles = UserProfile.objects.values('company_id', 'role').annotate(count=Count('id'))
for p in profiles:
    print(f"Company ID: {p['company_id']}, Role: {p['role']}, Count: {p['count']}")
