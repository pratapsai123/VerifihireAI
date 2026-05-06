import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from ai_candidates.models import Candidate
from django.db.models import Count

# Find duplicate PAN numbers
duplicates = Candidate.objects.values('pan_number').annotate(count=Count('id')).filter(count__gt=1, pan_number__isnull=False)

print(f"Found {duplicates.count()} duplicate PAN numbers")

for dup in duplicates:
    pan = dup['pan_number']
    candidates = Candidate.objects.filter(pan_number=pan).order_by('created_at')
    print(f"\nPAN {pan}: {candidates.count()} candidates")
    
    # Keep the first one, clear PAN for others
    first = candidates.first()
    print(f"  Keeping: {first.full_name} (created: {first.created_at})")
    
    for candidate in candidates[1:]:
        print(f"  Clearing PAN for: {candidate.full_name} (created: {candidate.created_at})")
        candidate.pan_number = None
        candidate.save(update_fields=['pan_number'])

print("\nDuplicate PAN cleanup complete!")
