import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import UserProfile, StudentPrepSession
from django.contrib.auth.models import User

def test_student_registration():
    print("\n" + "="*60)
    print("TEST 1: Student Registration Model Check")
    print("="*60)

    email = "practice_student@gmail.com"
    # Cleanup first
    User.objects.filter(email=email).delete()
    UserProfile.objects.filter(email=email).delete()

    user = User.objects.create_user(
        username=email,
        email=email,
        password="studentpassword123",
        first_name="Prep",
        last_name="Student"
    )

    profile = UserProfile.objects.create(
        first_name="Prep",
        last_name="Student",
        email=email,
        role=UserProfile.ROLE_STUDENT,
        organization_name='Student Prep',
        company=None,
        user=user,
        is_approved=True
    )

    print("SUCCESS: Created student user and profile successfully.")
    print(f"  Role is: {profile.role}")
    print(f"  Approved is: {profile.is_approved}")

    # Cleanup
    user.delete()
    return True

def test_prep_session_creation():
    print("\n" + "="*60)
    print("TEST 2: Student Prep Session Model Check")
    print("="*60)

    # Create prep session
    session = StudentPrepSession.objects.create(
        full_name="Prep Student",
        email="practice_student@gmail.com",
        phone="1234567890",
        target_role="Full Stack Engineer",
        experience_level="Entry Level",
        status="Scheduled"
    )

    print("SUCCESS: Created student prep session successfully.")
    print(f"  Session ID (Public Token): {session.id}")
    print(f"  Target Role: {session.target_role}")

    # Verify we can fetch it
    fetched = StudentPrepSession.objects.get(pk=session.id)
    if fetched.full_name == "Prep Student":
        print("SUCCESS: Verified session retrieval by ID")
    else:
        print("FAIL: Failed session retrieval")
        session.delete()
        return False

    session.delete()
    return True

def main():
    results = []
    results.append(("Student Registration Model", test_student_registration()))
    results.append(("Prep Session Creation Model", test_prep_session_creation()))

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{status}: {name}")

if __name__ == "__main__":
    main()
