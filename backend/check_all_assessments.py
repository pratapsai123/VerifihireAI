import os
import django
import sys

sys.path.append('c:/Users/D-IT/Desktop/finna1/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment

def check_all_assessments():
    assessments = Assessment.objects.all().order_by('-id')
    print(f"Total Assessments: {len(assessments)}")
    for a in assessments:
        has_content = "YES" if a.generated_content else "NO"
        print(f"ID: {a.id}, Status: {a.status}, Content: {has_content}, Skills: {a.required_skills}")
        if a.generated_content:
            mcqs = a.generated_content.get('mcqs', [])
            coding = a.generated_content.get('coding_challenges', []) or a.generated_content.get('coding_tasks', [])
            print(f"  MCQs: {len(mcqs)}, Coding: {len(coding)}")

if __name__ == "__main__":
    check_all_assessments()
