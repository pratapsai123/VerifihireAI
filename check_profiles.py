import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate
from django.db.models import Count

print("--- Candidate Profile Stats ---")
profiles = Candidate.objects.values('user_profile_id').annotate(count=Count('id'))
for p in profiles:
    print(f"Profile ID: {p['user_profile_id']}, Count: {p['count']}")

from api.models import UserProfile
print("\n--- Current Admin Profile ---")
admins = UserProfile.objects.filter(role='company_admin')
for a in admins:
    print(f"ID: {a.id}, Email: {a.email}, Company: {a.company_id}")
