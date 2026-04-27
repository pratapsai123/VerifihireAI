import os
import sys
import django

# Add current directory to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate

try:
    c = Candidate.objects.get(id=489)
    print(f"CANDIDATE_FOUND: {c.full_name}")
    print(f"STATUS: {c.status}")
    print(f"LINK_OPENED: {c.link_opened_at}")
except Exception as e:
    print(f"ERROR: {e}")
