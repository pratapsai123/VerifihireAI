import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()
from api.views.candidate_assessment_views import get_ai_candidate_results
res = get_ai_candidate_results(None, None, None, None, set())
failed = [r for r in res if r['status'] == 'Resume Failed']
print("Failed count:", len(failed))
for f in failed:
    if f.get('is_ai_interview') or f.get('interview_summary') or f.get('score', 0) > 0:
        print(f"Candidate {f['candidate_name']} has is_ai_interview={f.get('is_ai_interview')}")
