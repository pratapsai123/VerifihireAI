import os
import django
import sys
import json

sys.path.append('c:/Users/D-IT/Desktop/finna1/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment

def get_counts(aid):
    a = Assessment.objects.get(id=aid)
    content = a.generated_content
    print(f"ID: {aid}, Type: {type(content)}")
    if isinstance(content, str):
        try:
            content = json.loads(content)
            print("Successfully parsed string.")
        except:
            print("Failed to parse string.")
    
    if isinstance(content, dict):
        mcqs = content.get('mcqs', [])
        coding = content.get('coding_challenges', []) or content.get('coding_tasks', [])
        print(f"Requested MCQ: {a.mcq_count}, Coding: {a.coding_count}")
        print(f"Generated MCQ: {len(mcqs)}, Coding: {len(coding)}")
    else:
        print("Content is not a dict after parsing.")

if __name__ == "__main__":
    get_counts(462)
    print("-" * 20)
    get_counts(1)
    print("-" * 20)
    get_counts(467)
