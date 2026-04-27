import os
import django
from django.forms.models import model_to_dict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate

try:
    c = Candidate.objects.get(id=489)
    print(model_to_dict(c))
except Exception as e:
    print(f"Error: {e}")
