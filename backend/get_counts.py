import os
import django
import sys

sys.path.append('c:/Users/D-IT/Desktop/finna1/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment

def get_counts(aid):
    a = Assessment.objects.get(id=aid)
    print(f"Requested MCQ: {a.mcq_count}, Coding: {a.coding_count}")
    print(f"Generated MCQ: {len(a.generated_content.get('mcqs', []))}, Coding: {len(a.generated_content.get('coding_challenges', []))}")

if __name__ == "__main__":
    get_counts(462)
