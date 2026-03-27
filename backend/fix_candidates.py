import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate
from api.models import UserProfile

cands = Candidate.objects.filter(user_profile__isnull=True, company__isnull=False)
fixed = 0
for c in cands:
    p = UserProfile.objects.filter(company=c.company).first()
    if p:
        c.user_profile = p
        c.save()
        fixed += 1

print(f"Fixed {fixed} existing candidates!")
