
import os
import django
import sys

# Add the current directory to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import Question
from django.db.models import Count

print("--- Question Counts by Topic and Visibility ---")
topics = Question.objects.values('topic', 'visibility').annotate(count=Count('id')).order_by('topic')
for t in topics:
    print(f"Topic: {t['topic']}, Visibility: {t['visibility']}, Count: {t['count']}")

print("\n--- Question Counts by Assessment ---")
assessments = Question.objects.values('assessment').annotate(count=Count('id')).order_by('assessment')
for a in assessments:
    print(f"Assessment: {a['assessment']}, Count: {a['count']}")

total = Question.objects.count()
print(f"\nTotal Questions in DB: {total}")
