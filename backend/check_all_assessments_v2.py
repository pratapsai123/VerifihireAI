import os
import django
import sys
import json

sys.path.append('c:/Users/D-IT/Desktop/finna1/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment

def check_all_assessments():
    assessments = Assessment.objects.all().order_by('-id')
    print(f"Total Assessments: {len(assessments)}")
    for a in assessments:
        content_val = a.generated_content
        content_type = type(content_val)
        is_empty_dict = (content_val == {})
        is_none = (content_val is None)
        
        print(f"ID: {a.id}, Status: {a.status}, Type: {content_type}, IsNone: {is_none}, IsEmptyDict: {is_empty_dict}")
        if content_val and isinstance(content_val, dict):
            mcqs = content_val.get('mcqs', [])
            coding = content_val.get('coding_challenges', []) or content_val.get('coding_tasks', [])
            print(f"  MCQs Count: {len(mcqs)}, Coding Count: {len(coding)}")

if __name__ == "__main__":
    check_all_assessments()
