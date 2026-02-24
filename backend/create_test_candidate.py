import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from ai_candidates.models import Candidate

# Create a test candidate if none exists
email = 'test_ui_modern@example.com'
if not Candidate.objects.filter(email=email).exists():
    c = Candidate.objects.create(
        full_name='UI Modernization Test',
        email=email,
        job_title='Frontend Specialist',
        job_description='Specialist in glassmorphism and modern UI design.'
    )
    print(c.id)
else:
    print(Candidate.objects.filter(email=email).first().id)
