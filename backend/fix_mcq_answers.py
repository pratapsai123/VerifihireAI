import os
import django
import sys

# Add the current directory to sys.path so we can import django settings
sys.path.append(os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.models import Assessment, AIAssessmentSubmission
from ai_assessments.ai_logic import _normalize_generated_pool
from django.db import transaction

def repair_data():
    with transaction.atomic():
        print("Starting data repair for Assessments...")
        assessments = Assessment.objects.select_for_update().all()
        a_count = 0
        for a in assessments:
            if a.generated_content:
                # Before normalization, try to ensure it's a dict if stored as string
                import json
                old_content = a.generated_content
                if isinstance(old_content, str):
                    try:
                        old_content = json.loads(old_content)
                    except: pass
                
                new_content = _normalize_generated_pool(old_content)
                
                # Check for meaningful changes (deep comparison)
                if json.dumps(old_content, sort_keys=True) != json.dumps(new_content, sort_keys=True):
                    a.generated_content = new_content
                    a.save(update_fields=['generated_content'])
                    print(f"  [FIXED] Assessment ID: {a.id} ({a.required_skills})")
                    a_count += 1
        
        print(f"Finished Assessments. Repaired: {a_count}")

        print("\nStarting data repair for Submissions...")
        submissions = AIAssessmentSubmission.objects.select_for_update().all()
        s_count = 0
        for s in submissions:
            if s.candidate_questions:
                import json
                old_questions = s.candidate_questions
                if isinstance(old_questions, str):
                    try:
                        old_questions = json.loads(old_questions)
                    except: pass
                
                new_questions = _normalize_generated_pool(old_questions)
                
                if json.dumps(old_questions, sort_keys=True) != json.dumps(new_questions, sort_keys=True):
                    s.candidate_questions = new_questions
                    s.save(update_fields=['candidate_questions'])
                    print(f"  [FIXED] Submission ID: {s.id} for {s.candidate_email}")
                    s_count += 1
        
        print(f"Finished Submissions. Repaired: {s_count}")

if __name__ == "__main__":
    try:
        repair_data()
        print("\n✅ Repair process completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during repair: {e}")
        import traceback
        traceback.print_exc()
