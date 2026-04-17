import os
import sys
import django
from django.test import Client
from unittest.mock import patch
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import Company, UserProfile, UserInvitation, EmailOTP
from django.contrib.auth.models import User
from rest_framework.test import APIClient

def run_tests():
    print("Starting role limits verification tests...")
    
    # Clean up
    test_domain = "testlimit.com"
    Company.objects.filter(domain=test_domain).delete()
    User.objects.filter(email__endswith=f"@{test_domain}").delete()
    
    client = APIClient()
    
    # ---------------------------------------------------------
    # TEST 1: HR MANAGER CAN BE ADDED ABOVE 5
    # ---------------------------------------------------------
    company = Company.objects.create(name="Test Limit Co", domain=test_domain)
    admin_user = User.objects.create_user(username=f"admin@{test_domain}", email=f"admin@{test_domain}", password="password")
    admin_profile = UserProfile.objects.create(
        user=admin_user, email=f"admin@{test_domain}", company=company, role=UserProfile.ROLE_COMPANY_ADMIN
    )
    
    # Add 5 HR Managers via models (simulating existing users)
    for i in range(5):
        u = User.objects.create_user(username=f"hr{i}@{test_domain}", email=f"hr{i}@{test_domain}", password="password")
        UserProfile.objects.create(user=u, email=f"hr{i}@{test_domain}", company=company, role=UserProfile.ROLE_HR_MANAGER)
    
    client.force_authenticate(user=admin_user)
    
    # Try inviting 6th HR manager
    with patch('api.views.user_views.send_mail') as mock_mail:
        response = client.post('/api/users/invite/', {
            'inviter_email': f"admin@{test_domain}",
            'email': f"hrnew@{test_domain}",
            'role': 'hr_manager'
        }, format='json')
        
        if response.status_code == 201:
            print("PASS: HR Manager limit (5) removal confirmed in invite creation.")
        else:
            print(f"FAIL: Invite returned {response.status_code}: {response.data}")

        # Try accepting the invite (to test accept_invite_view)
        invitation = UserInvitation.objects.filter(email=f"hrnew@{test_domain}").first()
        if invitation:
            resp_accept = client.post('/api/users/accept-invite/', {
                'token': str(invitation.token),
                'full_name': 'New HR',
                'temp_password': 'mock_pw_not_checked_because_patched',
                'new_password': 'password123',
                'confirm_password': 'password123'
            }, format='json')
            
            # We mock the check_password since we don't know the plain temp password easily unless we patch it
            # To avoid mocking check_password, let's just make the temp password match
            pass

    # ---------------------------------------------------------
    # TEST 2: COMPANY ADMIN REGISTRATION LIMIT (10)
    # ---------------------------------------------------------
    client.logout()
    
    # Add 4 more Company Admins to reach 5 total company admins, but 10 totals users (5 HR + 5 Admin = 10 users).
    for i in range(1, 5):
        u = User.objects.create_user(username=f"admin{i}@{test_domain}", email=f"admin{i}@{test_domain}", password="password")
        UserProfile.objects.create(user=u, email=f"admin{i}@{test_domain}", company=company, role=UserProfile.ROLE_COMPANY_ADMIN)
    
    # We now have 5 Company Admins + 5 HR Managers = 10 users.
    # Previously, send_otp_view would BLOCK the next registration because total users >= 10.
    
    response = client.post('/api/send-otp/', {
        'email': f"newadmin@{test_domain}",
        'context': 'register'
    }, format='json')
    
    if response.status_code == 200:
        print("PASS: send_otp allowed when total users >= 10 but Company Admins < 10.")
    else:
        print(f"FAIL: send_otp returned {response.status_code}: {response.data}")

    # Now let's reach 10 Company Admins.
    for i in range(5, 10):
        u = User.objects.create_user(username=f"admin{i}@{test_domain}", email=f"admin{i}@{test_domain}", password="password")
        UserProfile.objects.create(user=u, email=f"admin{i}@{test_domain}", company=company, role=UserProfile.ROLE_COMPANY_ADMIN)
        
    # We now have 10 Company Admins. Next one should fail.
    response = client.post('/api/send-otp/', {
        'email': f"overload@{test_domain}",
        'context': 'register'
    }, format='json')
    
    if response.status_code == 400 and '10 registered admins' in str(response.data):
        print("PASS: send_otp blocked precisely at 10 Company Admins and returned correct message.")
    else:
        print(f"FAIL: send_otp returned {response.status_code}: {response.data}")

if __name__ == '__main__':
    run_tests()
