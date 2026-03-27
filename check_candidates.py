import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate
from django.db.models import Count

print("--- Candidate Job Titles ---")
titles = Candidate.objects.values('job_title').annotate(count=Count('id')).order_by('-count')
for t in titles:
    print(f"Title: '{t['job_title']}', Count: {t['count']}")

print("\n--- Candidate Status Stats ---")
stats = Candidate.objects.values('status').annotate(count=Count('id')).order_by('-count')
for s in stats:
    print(f"Status: '{s['status']}', Count: {s['count']}")
