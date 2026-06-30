import os
import django
import sys

# Add the project root to sys.path
sys.path.append('c:/Users/D-IT/Desktop/finna1/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment

def check_assessments():
    assessments = Assessment.objects.all().order_by('-id')[:5]
    for a in assessments:
        print(f"ID: {a.id}, Status: {a.status}, Skills: {a.required_skills}")
        print(f"Generated Content Type: {type(a.generated_content)}")
        if a.generated_content:
            mcqs = a.generated_content.get('mcqs', [])
            coding = a.generated_content.get('coding_challenges', []) or a.generated_content.get('coding_tasks', [])
            print(f"MCQs: {len(mcqs)}, Coding: {len(coding)}")
            # Print keys if any
            print(f"Keys: {list(a.generated_content.keys()) if isinstance(a.generated_content, dict) else 'Not a dict'}")
        else:
            print("Generated Content is NULL")
        print("-" * 20)

if __name__ == "__main__":
    check_assessments()
