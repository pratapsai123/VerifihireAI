import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()
from ai_candidates.models import Candidate

candidates = Candidate.objects.filter(full_name__icontains='Lavanya_Resume').order_by('-id')[:5]
for c in candidates:
    print(f"ID: {c.id}, Name: {c.full_name}, Status: {c.status}, Score: {c.resume_score}")
