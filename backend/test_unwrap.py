import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.views import extract_json
import json
json_str = '{"test": {"mcqs": [{"q":"1"}], "coding_challenges": []}}'
res = extract_json(json_str)
print("Unwrapped Keys:", res.keys() if res else None)
