import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate

try:
    c = Candidate.objects.get(id=489)
    print(f"Found candidate: {c.full_name}")
    print(f"Status: {c.status}")
    print(f"Link opened at: {c.link_opened_at}")
except Exception as e:
    print(f"Error: {e}")
