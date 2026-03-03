import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import InterviewInvitation

print("--- Interview Invitations ---")
invites = InterviewInvitation.objects.all().order_by('-created_at')[:20]
for inv in invites:
    print(f"ID: {inv.id}, Email: {inv.email}, Token: {inv.token}, Status: {inv.status}, Interview ID: {inv.interview_id}")

print("\n--- Searching for specific tokens from logs ---")
tokens = ['d101107a-2bac-4123-8721-866e20cb0ff8', 'eea9546a-d97d-495c-86a9-0f650958c44a']
for t_str in tokens:
    try:
        t_uuid = uuid.UUID(t_str)
        inv = InterviewInvitation.objects.filter(token=t_uuid).first()
        if inv:
            print(f"Token {t_str} FOUND: ID={inv.id}, Email={inv.email}, Interview={inv.interview_id}")
        else:
            print(f"Token {t_str} NOT FOUND")
    except Exception as e:
        print(f"Error searching for {t_str}: {e}")
