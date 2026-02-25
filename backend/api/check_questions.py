
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Question
from django.db.models import Count

topics = Question.objects.values('topic').annotate(count=Count('id')).order_by('topic')
print(f"Total topics: {len(topics)}")
for t in topics:
    print(f"{t['topic']}: {t['count']}")

# Also check for assessment names
assessments = Question.objects.values('assessment').annotate(count=Count('id')).order_by('assessment')
print(f"\nTotal assessments: {len(assessments)}")
for a in assessments:
    print(f"{a['assessment']}: {a['count']}")
