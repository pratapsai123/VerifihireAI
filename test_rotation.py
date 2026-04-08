import os
import sys
import django

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_assessments.ai_logic import GroqKeyManager
from django.conf import settings

# Force a second key for testing
settings.GROQ_API_KEYS.append('gsk_MOCK_SECOND_KEY_FOR_TESTING')

print(f"Keys in settings: {len(settings.GROQ_API_KEYS)}")
print(f"Initial Key: {GroqKeyManager.get_current_key()}")

GroqKeyManager.rotate_key()
print(f"After 1st Rotate: {GroqKeyManager.get_current_key()}")

GroqKeyManager.rotate_key()
print(f"After 2nd Rotate (should loop back): {GroqKeyManager.get_current_key()}")
