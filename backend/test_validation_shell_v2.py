import os
import django
import uuid
import asyncio
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import InterviewInvitation

async def test_validation_logic():
    print("--- STARTING VALIDATION LOGIC TEST ---")
    
    # 1. Test invalid token
    random_token = str(uuid.uuid4())
    invitation = await sync_to_async(lambda: InterviewInvitation.objects.filter(token=random_token).first())()
    print(f"Token {random_token} exists? {invitation is not None}")
    
    if invitation is None:
        print("PASS: Invalid token correctly not found.")
    else:
        print("FAIL: Invalid token found.")

    # 2. Test valid token
    first_inv = await sync_to_async(lambda: InterviewInvitation.objects.first())()
    if first_inv:
        token = str(first_inv.token)
        print(f"Testing valid token from DB: {token}")
        found = await sync_to_async(lambda: InterviewInvitation.objects.filter(token=token).first())()
        if found:
            print(f"PASS: Valid token correctly found. Status: {found.status}")
        else:
            print("FAIL: Valid token from DB not found via filter.")
    else:
        print("NOTE: No invitations found in DB to test valid token logic.")
    
    print("--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_validation_logic())
