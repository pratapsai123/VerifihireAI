import google.generativeai as genai
import os

# Mock settings
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or "Put_Key_Here_If_Needed_But_Use_Env_Preferably"

# Check if we can import settings from django if needed, but standalone is better if we have the key.
# I'll rely on the one in settings.py if I can import it, or just hope the environment has it.
# Actually, let's try to load it from the django settings context to be safe.

import sys
import django
from django.conf import settings

sys.path.append('c:/Users/D-IT/Desktop/AIexam/VerifiHireAI/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

genai.configure(api_key=settings.GEMINI_API_KEY)

print("Listing Models:")
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)
