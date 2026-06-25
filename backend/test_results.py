import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()
from api.views.candidate_assessment_views import get_ai_candidate_results
res = get_ai_candidate_results(None, None, None, None, set())
failed = [r for r in res if r['status'] == 'Resume Failed']
if failed:
    print(json.dumps(failed[0], indent=2))
else:
    print("No failed resumes found")
