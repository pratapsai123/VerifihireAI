import os
import django
import sys
import json

sys.path.append('c:/Users/D-IT/Desktop/finna1/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment

def debug_assessment(aid):
    try:
        a = Assessment.objects.get(id=aid)
        print(f"ID: {a.id}")
        content = a.generated_content
        print(f"Type: {type(content)}")
        if isinstance(content, str):
            print("Content is a STRING. Attempting to parse...")
            try:
                content = json.loads(content)
                print("Successfully parsed string to JSON.")
            except Exception as e:
                print(f"Failed to parse string: {e}")
        
        if isinstance(content, dict):
            print(f"Keys: {list(content.keys())}")
            mcqs = content.get('mcqs', [])
            coding = content.get('coding_challenges', []) or content.get('coding_tasks', [])
            print(f"MCQs count: {len(mcqs)}")
            print(f"Coding count: {len(coding)}")
            if mcqs:
                print(f"First MCQ: {mcqs[0].get('question')[:100]}...")
            if coding:
                # Check if it's a list of strings or list of dicts
                if len(coding) > 0:
                    print(f"First Coding item type: {type(coding[0])}")
                    if isinstance(coding[0], dict):
                        print(f"First Coding Title: {coding[0].get('title')}")
                    else:
                        print(f"First Coding Value: {coding[0]}")
        else:
            print(f"Content is not a dict: {content}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_assessment(int(sys.argv[1]))
    else:
        debug_assessment(467)
