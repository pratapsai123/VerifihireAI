import os
import django
import sys
import json

sys.path.append('c:/Users/D-IT/Desktop/finna1/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment

def final_check(aid):
    a = Assessment.objects.get(id=aid)
    print(f"--- ID {aid} ---")
    print(f"Status: {a.status}")
    print(f"generated_content type: {type(a.generated_content)}")
    print(f"generated_content value: {repr(a.generated_content)[:500]}")

if __name__ == "__main__":
    for i in [467, 462, 1]:
        try:
            final_check(i)
        except Exception as e:
            print(f"Error checking {i}: {e}")
