import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserProfile, EmailOTP
from rest_framework.test import APIRequestFactory
from api.views.auth_views import reset_password_view
from django.utils import timezone
from datetime import timedelta

def test_password_reuse():
    print("Testing password reuse prevention...")
    
    email = "test_reuse@example.com"
    password = "InitialPassword123!"
    
    # 1. Create or get user
    user, created = User.objects.get_or_create(username=email, email=email)
    user.set_password(password)
    user.save()
    
    user_profile, _ = UserProfile.objects.get_or_create(email=email, user=user)
    user_profile.is_approved = True
    user_profile.save()
    
    # 2. Create a verified OTP
    EmailOTP.objects.filter(email=email).delete()
    otp = "123456"
    EmailOTP.objects.create(email=email, otp=otp, is_verified=True, created_at=timezone.now())
    
    factory = APIRequestFactory()
    
    # 3. Try to reset to the SAME password
    print(f"Attempting to reset password to the current one: {password}")
    request = factory.post('/api/reset-password/', {
        'email': email,
        'otp': otp,
        'new_password': password,
        'confirm_password': password
    }, format='json')
    
    response = reset_password_view(request)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Data: {response.data}")
    
    if response.status_code == 400 and response.data.get('error') == 'This password has already been used. Please choose a new password.':
        print("SUCCESS: Password reuse was blocked as expected.")
    else:
        print("FAILURE: Password reuse was NOT blocked correctly.")
        return False
        
    # 4. Try to reset to a DIFFERENT password
    new_password = "NewPassword456!"
    print(f"Attempting to reset password to a new one: {new_password}")
    
    # Need a new OTP or reuse existing one (if logic allows)
    # The view doesn't clear the OTP on failure, so we can probably reuse it if it's the most recent verified one
    request = factory.post('/api/reset-password/', {
        'email': email,
        'otp': otp,
        'new_password': new_password,
        'confirm_password': new_password
    }, format='json')
    
    response = reset_password_view(request)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Data: {response.data}")
    
    if response.status_code == 200:
        print("SUCCESS: Password reset allowed for a new password.")
    else:
        print("FAILURE: Password reset failed for a new password.")
        return False
        
    # Cleanup
    user_profile.delete()
    user.delete()
    EmailOTP.objects.filter(email=email).delete()
    
    return True

if __name__ == "__main__":
    success = test_password_reuse()
    sys.exit(0 if success else 1)
