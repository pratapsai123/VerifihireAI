from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db import models, close_old_connections
from django.db.utils import OperationalError
from ai_candidates.models import Candidate
from .models import (
    UserProfile,
    EmailOTP,
    Question,
    Question,
    CustomAssessment,
    Assessment,
    AssessmentQuestion,
    AssessmentCodingQuestion,
    CodingQuestion,
    Company,
    CandidateInvitation,
    CandidateSubmission,
    ApplicationAdmin,
    UserInvitation,
    CandidateDetails,
    CodingTestCase,
    Interview,
    InterviewInvitation,
    LiveInterviewFeedback,
)
from ai_assessments.models import AIAssessmentSubmission

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.dateparse import parse_datetime
import re
import os
from django.utils import timezone
from datetime import timedelta
import random
import re
import PyPDF2
import requests
from .ocr_utils import extract_text_from_image
from .report_utils import generate_candidate_report

EXECUTOR_BASE_URL = os.environ.get("EXECUTOR_BASE_URL", "http://localhost:4000").rstrip("/")
from docx import Document
import io
from typing import Optional
import json


def _otp_expiry_seconds() -> int:
    """Single source of truth for OTP validity duration used by API responses/messages."""
    try:
        return int(getattr(settings, 'EMAIL_OTP_EXPIRY_SECONDS', 120))
    except Exception:
        return 120


def _email_domain(email: str) -> str:
    email = (email or '').strip().lower()
    if '@' not in email:
        return ''
    return email.split('@', 1)[1].strip()


def _free_email_domains() -> set[str]:
    default = {
        'gmail.com',
        'googlemail.com',
        'yahoo.com',
        'yahoo.in',
        'outlook.com',
        'hotmail.com',
        'live.com',
        'icloud.com',
        'aol.com',
        'proton.me',
        'protonmail.com',
        'zoho.com',
    }
    configured = getattr(settings, 'FREE_EMAIL_DOMAINS', None)
    if not configured:
        return default
    try:
        return {d.strip().lower() for d in configured if str(d).strip()}
    except Exception:
        return default


def _generate_temp_password(length: int = 12) -> str:
    # Strong-ish temp password: at least one upper/lower/digit/special.
    length = max(10, int(length))
    rng = random.SystemRandom()
    lowers = "abcdefghjkmnpqrstuvwxyz"
    uppers = lowers.upper()
    digits = "23456789"
    specials = "!@#$%^&*_-+"
    required = [
        rng.choice(lowers),
        rng.choice(uppers),
        rng.choice(digits),
        rng.choice(specials),
    ]
    all_chars = lowers + uppers + digits + specials
    remaining = [rng.choice(all_chars) for _ in range(length - len(required))]
    pwd_list = required + remaining
    rng.shuffle(pwd_list)
    return "".join(pwd_list)


def _normalize_email(email: str) -> str:
    return (email or '').strip().lower()


def _is_application_admin_email(email: str) -> bool:
    email = _normalize_email(email)
    if not email:
        return False
    auth_user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
    if not auth_user:
        return False
    return ApplicationAdmin.objects.filter(user=auth_user).exists()


def _db_call_with_retry(fn, *, retries: int = 1):
    """
    Best-effort retry wrapper for flaky DB connections (e.g., Supabase in dev).
    Retries `retries` times after the first failure (so total attempts = retries + 1).
    """
    attempts = max(0, int(retries)) + 1
    last_err = None
    for attempt in range(attempts):
        try:
            return fn()
        except OperationalError as e:
            last_err = e
            close_old_connections()
            if attempt >= attempts - 1:
                raise
    # Should never reach here
    raise last_err


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Root endpoint that displays available API endpoints.
    """
    return Response({
        'message': 'FaceD Interview Backend API',
        'version': '1.0',
        'endpoints': {
            'register': '/api/register/',
            'login': '/api/login/',
            'admin': '/admin/',
        },
        'documentation': 'Use POST requests to /api/register/ and /api/login/'
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp_view(request):
    """
    Send OTP to email for verification.
    Expected request body:
    {
        "email": "user@company.com"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        context = request.data.get('context', '').strip().lower()
        
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return Response(
                {'error': 'Invalid email format.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists (only for registration flow)
        if context == 'register':
            if UserProfile.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Account with this email already exists. Please login.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Generate OTP
        otp = EmailOTP.generate_otp()
        expires_in = _otp_expiry_seconds()
        expires_minutes = max(1, int(round(expires_in / 60)))
        
        # Invalidate previous OTPs for this email
        EmailOTP.objects.filter(email=email, is_verified=False).update(is_verified=True)
        
        # Create new OTP
        email_otp = EmailOTP.objects.create(email=email, otp=otp)
        
        # Send email with OTP
        try:
            send_mail(
                subject='VeriFiHire - Email Verification OTP',
                message=f'Your OTP for email verification is: {otp}\n\nThis OTP is valid for {expires_minutes} minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            # If email sending fails, log the error but still save the OTP
            print(f"Email sending failed: {str(e)}")
            # Return OTP in response for development/testing purposes
            # In production, you may want to handle this differently
            return Response(
                {
                    'message': 'OTP generated. Email sending failed, but OTP is available below for testing.',
                    'otp': otp,  # For development/testing - remove in production
                    'email': email,
                    'expires_in': expires_in,
                    'email_sent': False,
                    'error': f'Email sending failed: {str(e)}'
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                'message': 'OTP sent to your email. Please check your inbox.',
                'email': email,
                'expires_in': expires_in
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        error_message = str(e)
        # Check if it's a database error (table doesn't exist)
        if 'no such table' in error_message.lower() or 'relation' in error_message.lower() or 'does not exist' in error_message.lower():
            error_message = 'Database table not found. Please run migrations: python manage.py makemigrations && python manage.py migrate'
        print(f"Error in send_otp_view: {error_message}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred: {error_message}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_view(request):
    """
    Verify OTP for email.
    Expected request body:
    {
        "email": "user@company.com",
        "otp": "123456"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        otp = request.data.get('otp', '').strip()
        
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not otp:
            return Response(
                {'error': 'OTP is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find the most recent unverified OTP for this email
        try:
            email_otp = EmailOTP.objects.filter(
                email=email,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not email_otp:
                return Response(
                    {'error': 'No OTP found for this email. Please request a new OTP.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if email_otp.is_expired():
                return Response(
                    {'error': 'OTP has expired. Please request a new OTP.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if email_otp.otp != otp:
                return Response(
                    {'error': 'Invalid OTP. Please try again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark OTP as verified
            email_otp.is_verified = True
            email_otp.save()
            
            return Response(
                {
                    'message': 'Email verified successfully!',
                    'verified': True
                },
                status=status.HTTP_200_OK
            )
            
        except EmailOTP.DoesNotExist:
            return Response(
                {'error': 'Invalid OTP or email.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Reset password after email OTP verification.
    Expected request body:
    {
        "email": "user@company.com",
        "otp": "123456",
        "new_password": "password123",
        "confirm_password": "password123"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        otp = request.data.get('otp', '').strip()
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            return Response({'error': 'OTP is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or not confirm_password:
            return Response({'error': 'New password and confirm password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({'error': 'Password must be at least 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        # Find the most recent verified OTP for this email
        email_otp = EmailOTP.objects.filter(email=email, is_verified=True).order_by('-created_at').first()
        if not email_otp:
            return Response({'error': 'Please verify OTP first.'}, status=status.HTTP_400_BAD_REQUEST)
        if email_otp.is_expired():
            return Response({'error': 'OTP has expired. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        if email_otp.otp != otp:
            return Response({'error': 'Invalid OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update user password (prefer Django auth user hashing)
        try:
            user_profile = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            user_profile = None

        if user_profile and user_profile.user:
            user_profile.user.set_password(new_password)
            user_profile.user.save()
            # Keep deprecated plaintext field cleared going forward
            if user_profile.password:
                user_profile.old_password = user_profile.password
                user_profile.password = None
                user_profile.save(update_fields=['old_password', 'password', 'updated_at'])
        elif user_profile:
            # Backward compatibility for profiles that aren't linked to auth.User yet.
            user_profile.old_password = user_profile.password
            user_profile.password = new_password
            user_profile.save(update_fields=['old_password', 'password', 'updated_at'])
        else:
            # Allow password reset for application admin accounts (no UserProfile)
            auth_user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
            if not auth_user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            auth_user.set_password(new_password)
            auth_user.save()

        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error in reset_password_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user with ALL signup form fields.
    Expected request body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "user@company.com",
        "business_email": "user@company.com",
        "role": "recruiter",
        "organization_name": "ABC Company",
        "password": "password123"
    }
    """
    try:
        # Get all fields from request
        full_name = request.data.get('full_name', '').strip()
        email = request.data.get('email', '').strip().lower() or request.data.get('business_email', '').strip().lower()
        organization_name = request.data.get('organization_name', '').strip()
        password = request.data.get('password', '')
        
        # Support legacy fields for backward compatibility
        if not full_name:
            first_name = request.data.get('first_name', '').strip()
            last_name = request.data.get('last_name', '').strip()
            if first_name:
                full_name = f"{first_name} {last_name}".strip()
        
        if not full_name and request.data.get('name'):
            full_name = request.data.get('name', '').strip()
        
        # Split full_name into first_name and last_name
        name_parts = full_name.split(' ', 1) if full_name else []
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Validation
        if not full_name or not first_name:
            return Response(
                {'error': 'Full name is required.', 'full_name': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not email:
            return Response(
                {'error': 'Business email is required.', 'email': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not organization_name:
            return Response(
                {'error': 'Organization name is required.', 'organization_name': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {'error': 'Password is required.', 'password': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters long.', 'password': ['Password must be at least 6 characters.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enforce business-domain signup for company registration (platform admin can be gmail, but is created separately)
        domain = _email_domain(email)
        if not domain:
            return Response({'error': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)
        if domain in _free_email_domains():
            return Response(
                {'error': 'Please use your company email (free email domains are not allowed for company registration).', 'email': ['Please use your company email.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if email already exists in UserProfile
        if UserProfile.objects.filter(email=email).exists():
            return Response(
                {'error': 'A user with this email already exists.', 'email': ['A user with this email already exists.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify that email has been verified via OTP
        verified_otp = EmailOTP.objects.filter(
            email=email,
            is_verified=True
        ).order_by('-created_at').first()
        
        if not verified_otp:
            return Response(
                {'error': 'Please verify your email first by entering the OTP.', 'email': ['Email verification required.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if OTP verification is recent (within 30 minutes)
        if timezone.now() > verified_otp.created_at + timedelta(minutes=30):
            return Response(
                {'error': 'Email verification has expired. Please verify your email again.', 'email': ['Email verification expired.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create/get company tenant (registration is ONLY allowed for the very first user of a company)
        company, company_created = Company.objects.get_or_create(name=organization_name)
        if company.domain and company.domain != domain:
            return Response(
                {'error': 'Email domain does not match this organization.', 'email': ['Email domain mismatch.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not company.domain:
            company.domain = domain
            company.save(update_fields=['domain'])

        if UserProfile.objects.filter(company=company).count() >= 5:
            return Response(
                {'error': 'This organization already has 5 registered admins. Please request an invitation from your Company Admin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Always create Django User for authentication (hashed password)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create user profile (role is assigned automatically per PDF: first user is COMPANY_ADMIN)
        user_profile = UserProfile.objects.create(
            first_name=first_name,
            last_name=last_name if last_name else None,
            email=email,
            password=None,  # deprecated field
            role=UserProfile.ROLE_COMPANY_ADMIN,
            organization_name=organization_name,
            company=company,
            user=user,
        )

        return Response(
            {
                'message': 'Account created successfully!',
                'user': {
                    'id': user_profile.id,
                    'first_name': user_profile.first_name,
                    'last_name': user_profile.last_name,
                    'email': user_profile.email,
                    'role': user_profile.role,
                    'organization_name': user_profile.organization_name,
                    'registration_timestamp': user_profile.registration_timestamp.isoformat(),
                }
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login a user - Step 1: Verify email and password, then send OTP.
    Expected request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        # Validation
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {'error': 'Password is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_profile = UserProfile.objects.filter(email=email).first()

        # Company users (UserProfile)
        if user_profile:
            if user_profile.user:
                if not user_profile.user.check_password(password):
                    return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # Backward compatibility: plaintext profile password (legacy)
                if user_profile.password != password:
                    return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
                # Best-effort migrate to hashed auth user on successful legacy login
                try:
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=user_profile.first_name or '',
                        last_name=user_profile.last_name or '',
                    )
                    user_profile.user = user
                    user_profile.old_password = user_profile.password
                    user_profile.password = None
                    user_profile.save(update_fields=['user', 'old_password', 'password', 'updated_at'])
                except Exception:
                    pass
        else:
            # Application Admin users (no UserProfile): must exist in ApplicationAdmin table
            auth_user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
            if not auth_user or not auth_user.check_password(password):
                return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
            if not ApplicationAdmin.objects.filter(user=auth_user).exists():
                return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate and send OTP for 2-step verification
        otp = EmailOTP.generate_otp()
        expires_in = _otp_expiry_seconds()
        expires_minutes = max(1, int(round(expires_in / 60)))
        
        # Invalidate previous OTPs for this email
        EmailOTP.objects.filter(email=email, is_verified=False).update(is_verified=True)
        
        # Create new OTP for login
        email_otp = EmailOTP.objects.create(email=email, otp=otp)
        
        # Send email with OTP
        try:
            send_mail(
                subject='VeriFiHire - Login Verification OTP',
                message=f'Your OTP for login verification is: {otp}\n\nThis OTP is valid for {expires_minutes} minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            # Return OTP in response for development/testing
            return Response(
                {
                    'message': 'Credentials verified. OTP generated. Check your email.',
                    'otp_required': True,
                    'otp': otp,  # Remove this in production
                    'email': email,
                    'expires_in': expires_in,
                    'email_sent': False
                },
                status=status.HTTP_200_OK
            )

        # Return response indicating OTP is required
        return Response(
            {
                'message': 'Credentials verified. OTP sent to your email. Please verify to complete login.',
                'otp_required': True,
                'email': email,
                'expires_in': expires_in
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        import traceback
        print(f"Error in login_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_login_otp_view(request):
    """
    Login a user - Step 2: Verify OTP and complete login.
    Expected request body:
    {
        "email": "user@example.com",
        "otp": "123456"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        otp = request.data.get('otp', '').strip()
        
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not otp:
            return Response(
                {'error': 'OTP is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find the most recent unverified OTP for this email
        try:
            email_otp = EmailOTP.objects.filter(
                email=email,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not email_otp:
                return Response(
                    {'error': 'No OTP found for this email. Please login again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if email_otp.is_expired():
                return Response(
                    {'error': 'OTP has expired. Please login again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if email_otp.otp != otp:
                return Response(
                    {'error': 'Invalid OTP. Please try again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark OTP as verified
            email_otp.is_verified = True
            email_otp.save()
            
            # Prefer user profile; fallback to application admin
            user_profile = UserProfile.objects.filter(email=email).first()
            app_admin = None
            if not user_profile:
                auth_user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
                if auth_user:
                    app_admin = ApplicationAdmin.objects.filter(user=auth_user).first()
                if not app_admin:
                    return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            # Return success response with user data and token
            return Response(
                {
                    'message': 'Login successful!',
                    'token': 'dummy-token-for-now',  # You can implement JWT here later
                    'user': {
                        'id': (user_profile.id if user_profile else app_admin.user_id),
                        'first_name': (user_profile.first_name if user_profile else (app_admin.user.first_name or '')),
                        'last_name': (user_profile.last_name if user_profile else (app_admin.user.last_name or '')),
                        'email': (user_profile.email if user_profile else (app_admin.user.email or app_admin.user.username)),
                        'role': (user_profile.role if user_profile else UserProfile.ROLE_APPLICATION_ADMIN),
                        'organization_name': (user_profile.organization_name if user_profile else None),
                        'registration_timestamp': (user_profile.registration_timestamp.isoformat() if user_profile else app_admin.created_at.isoformat()),
                    }
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        import traceback
        print(f"Error in verify_login_otp_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def invite_user_view(request):
    """
    Create an invitation for internal company roles (HR Manager / HR).

    Expected request body:
    {
      "inviter_email": "companyadmin@acme.com",
      "email": "hrmanager@acme.com",
      "role": "hr_manager" | "hr"
    }

    NOTE: This repo currently doesn't have JWT/session auth wired in.
    For now we authorize by checking inviter_email's role in UserProfile.
    """
    try:
        inviter_email = _normalize_email(request.data.get('inviter_email', ''))
        invitee_email = _normalize_email(request.data.get('email', ''))
        role = (request.data.get('role') or '').strip().lower()

        if not inviter_email:
            return Response({'error': 'inviter_email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Application Admin can view all data but cannot send invites (per requirement)
        if _is_application_admin_email(inviter_email):
            return Response({'error': 'Application Admin is not allowed to send invitations.'}, status=status.HTTP_403_FORBIDDEN)

        if not invitee_email:
            return Response({'error': 'email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if role not in {UserProfile.ROLE_HR_MANAGER, UserProfile.ROLE_HR}:
            return Response({'error': 'role must be hr_manager or hr.'}, status=status.HTTP_400_BAD_REQUEST)

        inviter = UserProfile.objects.filter(email=inviter_email).select_related('company').first()
        if not inviter or not inviter.company:
            return Response({'error': 'Invalid inviter.'}, status=status.HTTP_403_FORBIDDEN)

        if inviter.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER}:
            return Response({'error': 'You are not allowed to invite users.'}, status=status.HTTP_403_FORBIDDEN)

        if inviter.role == UserProfile.ROLE_HR_MANAGER and role != UserProfile.ROLE_HR:
            return Response({'error': 'HR Manager can only invite HR users.'}, status=status.HTTP_403_FORBIDDEN)

        company = inviter.company
        company_domain = (company.domain or '').strip().lower()
        if not company_domain:
            return Response({'error': 'Company domain is not configured.'}, status=status.HTTP_400_BAD_REQUEST)

        invitee_domain = _email_domain(invitee_email)
        if not invitee_domain:
            return Response({'error': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)
        if invitee_domain != company_domain:
            return Response({'error': 'Invitee email domain must match company domain.'}, status=status.HTTP_400_BAD_REQUEST)
        if invitee_domain in _free_email_domains():
            return Response({'error': 'Free email domains are not allowed for internal roles.'}, status=status.HTTP_400_BAD_REQUEST)

        # Already registered?
        if UserProfile.objects.filter(email=invitee_email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce max 5 HR_MANAGER per company
        if role == UserProfile.ROLE_HR_MANAGER and UserProfile.objects.filter(company=company, role=UserProfile.ROLE_HR_MANAGER).count() >= 5:
            return Response({'error': 'Maximum of 5 HR Managers allowed per company.'}, status=status.HTTP_409_CONFLICT)

        # Prevent multiple pending invites
        existing_pending = UserInvitation.objects.filter(company=company, email=invitee_email, status=UserInvitation.STATUS_PENDING).first()
        if existing_pending and not existing_pending.is_expired():
            return Response({'error': 'A pending invitation already exists for this email.'}, status=status.HTTP_409_CONFLICT)

        temp_password = _generate_temp_password(12)
        expires_at = timezone.now() + timedelta(hours=48)

        invitation = UserInvitation.objects.create(
            company=company,
            email=invitee_email,
            role=role,
            invited_by=inviter,
            temp_password_hash=make_password(temp_password),
            status=UserInvitation.STATUS_PENDING,
            expires_at=expires_at,
        )

        # Prefer explicit env, otherwise best-effort derive from incoming request host.
        frontend_base = (
            getattr(settings, 'FRONTEND_BASE_URL', None)
            or os.environ.get('FRONTEND_BASE_URL')
        )
        if not frontend_base:
            # request.build_absolute_uri('/') gives http(s)://host/; trim trailing slash
            frontend_base = request.build_absolute_uri('/').rstrip('/')
        if not frontend_base:
            frontend_base = 'https://verifyhire.duckdns.org'
        activation_link = f"{frontend_base.rstrip('/')}/accept-invite?token={invitation.token}"

        subject = f"{company.name} - Account Invitation"
        message = (
            f"You have been invited to VeriFiHire.\n\n"
            f"Company: {company.name}\n"
            f"Role: {role}\n\n"
            f"Activation link (one-time): {activation_link}\n"
            f"Temporary password: {temp_password}\n\n"
            f"This link expires in 48 hours."
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitee_email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as mail_err:
            invitation.status = UserInvitation.STATUS_PENDING
            invitation.save(update_fields=['status'])
            email_sent = False

        payload = {
            'message': 'Invitation created.',
            'email_sent': email_sent,
            'invitation': {
                'id': invitation.id,
                'email': invitation.email,
                'role': invitation.role,
                'company': company.name,
                'token': str(invitation.token),
                'expires_at': invitation.expires_at.isoformat() if invitation.expires_at else None,
            },
        }
        if not email_sent:
            # Dev fallback: return temp password if email fails (consistent with OTP endpoints)
            payload['temp_password'] = temp_password
            payload['activation_link'] = activation_link
        return Response(payload, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_invite_view(request, token):
    """
    Cancel a pending invitation.

    Body:
      { "requester_email": "..." }
    """
    try:
        requester_email = _normalize_email(request.data.get('requester_email', ''))
        if not requester_email:
            return Response({'error': 'requester_email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if _is_application_admin_email(requester_email):
            return Response({'error': 'Application Admin cannot cancel invitations.'}, status=status.HTTP_403_FORBIDDEN)

        requester = UserProfile.objects.filter(email=requester_email).select_related('company').first()
        if not requester or not requester.company:
            return Response({'error': 'Invalid requester.'}, status=status.HTTP_403_FORBIDDEN)
        if requester.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER}:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        inv = UserInvitation.objects.select_related('company').filter(token=token).first()
        if not inv:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
        if inv.company_id != requester.company_id:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        if inv.status != UserInvitation.STATUS_PENDING:
            return Response({'error': f'Invitation is {inv.status}.'}, status=status.HTTP_409_CONFLICT)

        inv.status = UserInvitation.STATUS_CANCELLED
        inv.save(update_fields=['status'])
        return Response({'message': 'Invitation cancelled.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_invite_view(request, token):
    """
    Resend a pending invitation. Regenerates the temporary password.

    Body:
      { "requester_email": "..." }
    """
    try:
        requester_email = _normalize_email(request.data.get('requester_email', ''))
        if not requester_email:
            return Response({'error': 'requester_email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if _is_application_admin_email(requester_email):
            return Response({'error': 'Application Admin cannot resend invitations.'}, status=status.HTTP_403_FORBIDDEN)

        requester = UserProfile.objects.filter(email=requester_email).select_related('company').first()
        if not requester or not requester.company:
            return Response({'error': 'Invalid requester.'}, status=status.HTTP_403_FORBIDDEN)
        if requester.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER}:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        inv = UserInvitation.objects.select_related('company').filter(token=token).first()
        if not inv:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
        if inv.company_id != requester.company_id:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        if inv.status != UserInvitation.STATUS_PENDING:
            return Response({'error': f'Invitation is {inv.status}.'}, status=status.HTTP_409_CONFLICT)

        # HR Manager can only manage HR invites
        if requester.role == UserProfile.ROLE_HR_MANAGER and inv.role != UserProfile.ROLE_HR:
            return Response({'error': 'HR Manager can only manage HR invitations.'}, status=status.HTTP_403_FORBIDDEN)

        # Refresh temp password + expiry window
        temp_password = _generate_temp_password(12)
        inv.temp_password_hash = make_password(temp_password)
        inv.expires_at = timezone.now() + timedelta(hours=48)
        inv.save(update_fields=['temp_password_hash', 'expires_at'])

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'https://verifyhire.duckdns.org'
        activation_link = f"{frontend_base.rstrip('/')}/accept-invite?token={inv.token}"

        subject = f"{inv.company.name} - Account Invitation (Resent)"
        message = (
            f"Your VeriFiHire invitation has been resent.\n\n"
            f"Company: {inv.company.name}\n"
            f"Role: {inv.role}\n\n"
            f"Activation link (one-time): {activation_link}\n"
            f"Temporary password: {temp_password}\n\n"
            f"This link expires in 48 hours."
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inv.email],
                fail_silently=False,
            )
            email_sent = True
        except Exception:
            email_sent = False

        payload = {
            'message': 'Invitation resent.',
            'email_sent': email_sent,
            'activation_link': activation_link if not email_sent else None,
            'temp_password': temp_password if not email_sent else None,
            'expires_at': inv.expires_at.isoformat() if inv.expires_at else None,
        }
        return Response(payload, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_invite_view(request, token):
    """
    Public: fetch invitation metadata for the accept-invite UI.
    """
    try:
        inv = UserInvitation.objects.select_related('company').filter(token=token).first()
        if not inv:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        if inv.status != UserInvitation.STATUS_PENDING:
            return Response({'error': f'Invitation is {inv.status}.'}, status=status.HTTP_409_CONFLICT)

        if inv.is_expired():
            inv.status = UserInvitation.STATUS_EXPIRED
            inv.save(update_fields=['status'])
            return Response({'error': 'Invitation has expired.'}, status=status.HTTP_410_GONE)

        return Response(
            {
                'email': inv.email,
                'role': inv.role,
                'company': inv.company.name,
                'expires_at': inv.expires_at.isoformat() if inv.expires_at else None,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def accept_invite_view(request):
    """
    Accept a user invitation and set password.

    Expected request body:
    {
      "token": "<uuid>",
      "full_name": "First Last",
      "temp_password": "....",
      "new_password": "....",
      "confirm_password": "...."
    }
    """
    try:
        token = (request.data.get('token') or '').strip()
        full_name = (request.data.get('full_name') or '').strip()
        temp_password = request.data.get('temp_password') or ''
        new_password = request.data.get('new_password') or ''
        confirm_password = request.data.get('confirm_password') or ''

        if not token:
            return Response({'error': 'token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not full_name:
            return Response({'error': 'full_name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not temp_password:
            return Response({'error': 'temp_password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or not confirm_password:
            return Response({'error': 'new_password and confirm_password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({'error': 'Password must be at least 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        inv = UserInvitation.objects.select_related('company').filter(token=token).first()
        if not inv:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
        if inv.status != UserInvitation.STATUS_PENDING:
            return Response({'error': f'Invitation is {inv.status}.'}, status=status.HTTP_409_CONFLICT)
        if inv.is_expired():
            inv.status = UserInvitation.STATUS_EXPIRED
            inv.save(update_fields=['status'])
            return Response({'error': 'Invitation has expired.'}, status=status.HTTP_410_GONE)

        if not check_password(temp_password, inv.temp_password_hash):
            return Response({'error': 'Invalid temporary password.'}, status=status.HTTP_400_BAD_REQUEST)

        email = _normalize_email(inv.email)
        if UserProfile.objects.filter(email=email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_409_CONFLICT)

        # Enforce max 5 HR_MANAGER per company
        if inv.role == UserProfile.ROLE_HR_MANAGER and UserProfile.objects.filter(company=inv.company, role=UserProfile.ROLE_HR_MANAGER).count() >= 5:
            return Response({'error': 'Maximum of 5 HR Managers allowed per company.'}, status=status.HTTP_409_CONFLICT)

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0].strip()
        last_name = name_parts[1].strip() if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=email,
            email=email,
            password=new_password,
            first_name=first_name,
            last_name=last_name,
        )

        profile = UserProfile.objects.create(
            first_name=first_name,
            last_name=last_name if last_name else None,
            email=email,
            password=None,  # deprecated
            role=inv.role,
            organization_name=inv.company.name,
            company=inv.company,
            user=user,
        )

        inv.status = UserInvitation.STATUS_ACCEPTED
        inv.accepted_at = timezone.now()
        inv.temp_password_hash = ''
        inv.save(update_fields=['status', 'accepted_at', 'temp_password_hash'])

        return Response(
            {
                'message': 'Invitation accepted. Account created successfully.',
                'user': {
                    'id': profile.id,
                    'email': profile.email,
                    'role': profile.role,
                    'organization_name': profile.organization_name,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def team_members_view(request):
    """
    List team members and invitation details.

    Since this repo doesn't have JWT/session auth wired in, the caller supplies:
      ?requester_email=...

    Access rules:
    - application_admin: can view all companies' users + invites
    - company_admin/hr_manager: can view only their company users + invites
    - hr/candidate/etc: forbidden
    """
    try:
        requester_email = _normalize_email(request.query_params.get('requester_email', ''))
        if not requester_email:
            return Response({'error': 'requester_email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        is_app_admin = _is_application_admin_email(requester_email)
        requester_profile = None
        if not is_app_admin:
            requester_profile = UserProfile.objects.filter(email=requester_email).select_related('company').first()
            if not requester_profile or not requester_profile.company:
                return Response({'error': 'Invalid requester.'}, status=status.HTTP_403_FORBIDDEN)
            if requester_profile.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER}:
                return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        if is_app_admin:
            members_qs = UserProfile.objects.select_related('company').order_by('company__name', 'email')
            invites_qs = UserInvitation.objects.select_related('company', 'invited_by').order_by('-created_at')
        else:
            company = requester_profile.company
            # Never include application admin in company-scoped member lists
            members_qs = (
                UserProfile.objects.filter(company=company)
                .exclude(role=UserProfile.ROLE_APPLICATION_ADMIN)
                .select_related('company')
                .order_by('email')
            )
            invites_qs = UserInvitation.objects.filter(company=company).select_related('company', 'invited_by').order_by('-created_at')

        members = []
        for u in members_qs:
            members.append({
                'id': u.id,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'email': u.email,
                'role': u.role,
                'organization_name': u.organization_name,
                'company': (u.company.name if u.company else None),
                'registration_timestamp': u.registration_timestamp.isoformat() if u.registration_timestamp else None,
            })

        invitations = []
        now = timezone.now()
        for inv in invites_qs:
            status_value = inv.status
            if status_value == UserInvitation.STATUS_PENDING and inv.expires_at and now > inv.expires_at:
                status_value = UserInvitation.STATUS_EXPIRED
            invitations.append({
                'id': inv.id,
                'email': inv.email,
                'role': inv.role,
                'company': inv.company.name,
                'status': status_value,
                'token': str(inv.token),
                'invited_by': inv.invited_by.email if inv.invited_by else None,
                'created_at': inv.created_at.isoformat() if inv.created_at else None,
                'expires_at': inv.expires_at.isoformat() if inv.expires_at else None,
                'accepted_at': inv.accepted_at.isoformat() if inv.accepted_at else None,
            })

        return Response(
            {
                'scope': 'all' if is_app_admin else 'company',
                'requester_email': requester_email,
                'members': members,
                'invitations': invitations,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def extract_skills_from_resume_view(request):
    """
    Extract skills from uploaded resume file.
    Expected request: multipart/form-data with 'resume' file field
    Supports: PDF, DOC, DOCX files
    """
    try:
        if 'resume' not in request.FILES:
            return Response(
                {'error': 'No resume file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resume_file = request.FILES['resume']
        file_name = resume_file.name.lower()
        
        # Validate file type
        if not (file_name.endswith('.pdf') or file_name.endswith('.doc') or file_name.endswith('.docx')):
            return Response(
                {'error': 'Invalid file type. Please upload PDF, DOC, or DOCX file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Read file content
        file_content = resume_file.read()
        
        # Extract text based on file type
        text = ""
        try:
            if file_name.endswith('.pdf'):
                # Extract text from PDF
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                for page in pdf_reader.pages:
                    text += page.extract_text() + " "
            elif file_name.endswith('.docx'):
                # Extract text from DOCX
                doc = Document(io.BytesIO(file_content))
                for paragraph in doc.paragraphs:
                    text += paragraph.text + " "
                # Also extract text from tables
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            text += cell.text + " "
            elif file_name.endswith('.doc'):
                # DOC files require additional libraries (python-docx doesn't support .doc)
                # For now, return an error or use a workaround
                return Response(
                    {'error': 'DOC files are not fully supported. Please convert to PDF or DOCX.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Error reading file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not text.strip():
            return Response(
                {'error': 'Could not extract text from the resume file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract skills from text
        # Common technical skills database
        common_skills = [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'C', 'Go', 'Rust', 'Swift', 'Kotlin',
            'PHP', 'Ruby', 'Perl', 'Scala', 'R', 'MATLAB', 'Dart', 'Lua', 'Shell', 'Bash',
            # Web Technologies
            'HTML', 'CSS', 'HTML5', 'CSS3', 'React', 'Angular', 'Vue', 'Vue.js', 'Node.js', 'Express',
            'Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot', 'ASP.NET', 'Laravel', 'Symfony',
            'jQuery', 'Bootstrap', 'Tailwind CSS', 'SASS', 'SCSS', 'Less',
            # Databases
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQLite', 'Cassandra',
            'DynamoDB', 'Elasticsearch', 'Neo4j', 'Firebase', 'MariaDB',
            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'CI/CD',
            'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Terraform', 'Ansible', 'Chef', 'Puppet',
            'Linux', 'Unix', 'Windows', 'Ubuntu', 'CentOS',
            # Mobile Development
            'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'Ionic',
            # Data Science & AI
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
            'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Jupyter', 'Data Analysis',
            # Other Technologies
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'DevOps',
            'Blockchain', 'Ethereum', 'Solidity', 'Web3',
            'GraphQL', 'gRPC', 'RabbitMQ', 'Kafka', 'Apache', 'Nginx',
            # Tools & Frameworks
            'Jira', 'Confluence', 'Slack', 'Trello', 'Asana', 'Postman', 'Swagger',
            'Webpack', 'Babel', 'ESLint', 'Prettier', 'Jest', 'Mocha', 'Cypress',
            'Selenium', 'Playwright', 'Pytest', 'Unit Testing', 'Integration Testing',
        ]
        
        # Normalize text for matching (case-insensitive)
        text_lower = text.lower()
        extracted_skills = []
        
        # Find skills in the text
        for skill in common_skills:
            # Check if skill appears in text (case-insensitive, whole word or as part of a phrase)
            skill_lower = skill.lower()
            # Match whole word or as part of common phrases
            if skill_lower in text_lower:
                # Avoid duplicates and very short matches
                if skill not in extracted_skills and len(skill) > 2:
                    extracted_skills.append(skill)
        
        # Sort skills alphabetically
        extracted_skills.sort()
        
        return Response(
            {
                'skills': extracted_skills,
                'count': len(extracted_skills),
                'message': f'Successfully extracted {len(extracted_skills)} skills from resume.'
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        print(f"Error in extract_skills_from_resume_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while extracting skills: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_questions_view(request):
    """
    Get questions based on topic, assessment, or skill filters.
    Query parameters:
    - topic: Filter by topic (skill name)
    - assessment: Filter by assessment name
    - question_type: Filter by type (MCQ, MSQ, TF)
    - difficulty: Filter by difficulty (easy, medium, hard)
    - limit: Limit number of results
    - visibility: Filter by visibility (default: GLOBAL)
    """
    try:
        topic = request.GET.get('topic', '').strip()
        assessment = request.GET.get('assessment', '').strip()
        question_type = request.GET.get('question_type', '').strip()
        difficulty = request.GET.get('difficulty', '').strip()
        limit = request.GET.get('limit', None)
        visibility = request.GET.get('visibility', 'GLOBAL').strip()
        
        # Start with all GLOBAL questions
        questions = Question.objects.filter(visibility='GLOBAL', company_id__isnull=True)
        
        # Apply filters
        if topic:
            questions = questions.filter(topic__icontains=topic)
        
        if assessment:
            questions = questions.filter(assessment__icontains=assessment)
        
        if question_type:
            questions = questions.filter(question_type=question_type.upper())
        
        if difficulty:
            questions = questions.filter(difficulty=difficulty.lower())
        
        # Apply limit
        if limit:
            try:
                limit = int(limit)
                questions = questions[:limit]
            except ValueError:
                pass
        
        # Serialize questions
        questions_list = []
        for q in questions:
            question_data = {
                'id': q.id,
                'assessment': q.assessment,
                'topic': q.topic,
                'question_type': q.question_type,
                'difficulty': q.difficulty,
                'question': q.question,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_answer': q.correct_answer,
                'correct_answers': q.correct_answers if q.correct_answers else [],
                'time_limit': q.time_limit,
                'created_at': q.created_at.isoformat() if q.created_at else None,
            }
            questions_list.append(question_data)
        
        return Response(
            {
                'count': len(questions_list),
                'results': questions_list,
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        print(f"Error in get_questions_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while fetching questions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _parse_mmss_to_seconds(value: Optional[str]) -> Optional[int]:
    """
    Parse a string like 'mm:ss' into seconds.
    Returns None if value is falsy or cannot be parsed.
    """
    if not value:
        return None
    try:
        text = str(value).strip()
        if not text:
            return None
        if ':' not in text:
            # allow plain seconds
            seconds = int(text)
            return max(0, seconds)
        mm, ss = text.split(':', 1)
        minutes = int(mm) if mm else 0
        seconds = int(ss) if ss else 0
        if seconds < 0:
            seconds = 0
        if seconds > 59:
            seconds = 59
        total = minutes * 60 + seconds
        # cap to 99:59 to match frontend mm:ss UI
        return min(total, 99 * 60 + 59)
    except Exception:
        return None


def _difficulty_from_experience_level(experience_level: Optional[str]) -> str:
    """
    Map frontend experience levels to Question.difficulty choices.
    """
    level = (experience_level or '').strip().lower()
    mapping = {
        'entry': 'easy',
        'mid': 'medium',
        'senior': 'hard',
        'expert': 'hard',
    }
    return mapping.get(level, 'easy')


def _create_question_from_payload(
    data: dict,
    *,
    preloaded_custom_assessment: Optional["CustomAssessment"] = None,
    preloaded_created_by: Optional["UserProfile"] = None,
    preloaded_company: Optional["Company"] = None,
) -> "Question":
    """
    Internal helper to create a Question from a payload dict.
    Raises ValueError for validation issues.
    """
    data = data or {}

    custom_assessment_id = data.get('custom_assessment_id', None)
    user_email = (data.get('user_email') or data.get('email') or '').strip().lower() or None
    org_name_from_client = (data.get('organization_name') or data.get('company_name') or '').strip() or None
    assessment = (data.get('assessment') or '').strip() or 'Manual'
    topic = (data.get('topic') or '').strip()
    question_type = (data.get('question_type') or '').strip().upper()
    question_text = (data.get('question') or '').strip()

    if not topic:
        topic = 'General'
        print(f"DEBUG: Missing topic in payload, defaulting to '{topic}'")

    if question_type not in ('MCQ', 'MSQ', 'TF'):
        # Try to infer or default
        question_type = 'MCQ'
        print(f"DEBUG: Invalid question_type in payload, defaulting to '{question_type}'")

    if not question_text:
        print("DEBUG: Missing question text in payload.")
        raise ValueError('question is required.')

    option_a = (data.get('option_a') or '').strip() or None
    option_b = (data.get('option_b') or '').strip() or None
    option_c = (data.get('option_c') or '').strip() or None
    option_d = (data.get('option_d') or '').strip() or None

    # For TF, default options are True/False if not provided
    if question_type == 'TF':
        option_a = option_a or 'True'
        option_b = option_b or 'False'

    if not option_a:
        option_a = 'Option A'
        print("DEBUG: Missing option_a, defaulting.")
    if not option_b:
        option_b = 'Option B'
        print("DEBUG: Missing option_b, defaulting.")

    difficulty = (data.get('difficulty') or '').strip().lower()
    if difficulty not in ('easy', 'medium', 'hard'):
        difficulty = _difficulty_from_experience_level(data.get('experience_level'))

    time_limit = data.get('time_limit', None)
    if time_limit is not None:
        try:
            time_limit = int(time_limit)
        except (TypeError, ValueError):
            time_limit = None
    if time_limit is None:
        time_limit = _parse_mmss_to_seconds(data.get('time_to_answer')) or 120

    correct_answer = (data.get('correct_answer') or '').strip().upper() or None
    correct_answers = data.get('correct_answers', None)
    if correct_answers is None:
        correct_answers = []
    if not isinstance(correct_answers, list):
        correct_answers = []
    correct_answers = [str(x).strip().upper() for x in correct_answers if str(x).strip()]

    if question_type == 'MCQ':
        if correct_answer not in ('A', 'B', 'C', 'D'):
            raise ValueError('correct_answer must be one of A, B, C, D for MCQ.')
        correct_answers = []
    elif question_type == 'TF':
        if correct_answer not in ('A', 'B'):
            raise ValueError('correct_answer must be A (True) or B (False) for TF.')
        correct_answers = []
        option_c = None
        option_d = None
    else:  # MSQ
        allowed = {'A', 'B', 'C', 'D'}
        correct_answers = [x for x in correct_answers if x in allowed]
        correct_answers = list(dict.fromkeys(correct_answers))  # unique preserve order
        if len(correct_answers) == 0:
            raise ValueError('correct_answers must be a non-empty array for MSQ.')
        correct_answer = None

    # Link manual questions to CustomAssessment (separate from company_id)
    custom_assessment = preloaded_custom_assessment
    if custom_assessment is None and custom_assessment_id is not None:
        try:
            caid = int(custom_assessment_id)
        except (TypeError, ValueError):
            raise ValueError('custom_assessment_id must be an integer.')
        try:
            custom_assessment = _db_call_with_retry(lambda: CustomAssessment.objects.get(id=caid), retries=1)
        except CustomAssessment.DoesNotExist:
            raise ValueError(
                f'Custom assessment ID {caid} was not found. Please go back to Review page and recreate the assessment.'
            )

    created_by = preloaded_created_by
    if created_by is None and user_email:
        try:
            created_by = UserProfile.objects.get(email=user_email)
        except UserProfile.DoesNotExist:
            created_by = None

    # company_id should represent the logged-in company, not the customAssessmentId.
    company_id = None
    visibility = 'GLOBAL'
    org_name = (created_by.organization_name if created_by else None) or org_name_from_client or None
    company = preloaded_company
    if org_name and company is None:
        company, _ = _db_call_with_retry(lambda: Company.objects.get_or_create(name=org_name), retries=1)
    if company:
        company_id = company.id
        visibility = 'COMPANY'

    q = _db_call_with_retry(
        lambda: Question.objects.create(
            created_by=created_by,
            organization_name_snapshot=(org_name or (created_by.organization_name if created_by else None)),
            custom_assessment=custom_assessment,
            company_id=company_id,
            visibility=visibility,
            assessment=assessment,
            topic=topic,
            question_type=question_type,
            difficulty=difficulty,
            question=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            correct_answers=correct_answers,
            time_limit=time_limit,
        ),
        retries=1,
    )
    return q


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_question_view(request):
    """
    Create a manual Question (MCQ/MSQ/TF) from the Manual Questions UI.

    Expected request body (JSON):
    {
      "custom_assessment_id": 123,              // optional, used to group "manual" questions
      "assessment": "React Developer",          // optional (defaults to "Manual")
      "topic": "React Hooks",                   // required
      "question_type": "MCQ" | "MSQ" | "TF",    // required
      "difficulty": "easy"|"medium"|"hard",     // optional
      "experience_level": "entry|mid|senior|expert", // optional alternative to difficulty
      "question": "....",                       // required
      "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...", // required for A/B, optional for C/D
      "correct_answer": "A",                    // required for MCQ/TF (TF: A=True, B=False)
      "correct_answers": ["A","C"],             // required for MSQ
      "time_limit": 90,                         // optional seconds
      "time_to_answer": "01:30"                 // optional mm:ss (alternative)
    }
    """
    try:
        data = request.data or {}
        try:
            print(f"Incoming payload for create_question_view: {data}")
            q = _create_question_from_payload(data)
            print(f"Successfully created question ID: {q.id} for custom_assessment_id: {data.get('custom_assessment_id')}")
        except ValueError as ve:
            print(f"Validation error in create_question_view: {str(ve)}")
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                'message': 'Question created successfully.',
                'id': q.id,
                'question': {
                    'id': q.id,
                    'company_name': (q.organization_name_snapshot or (q.created_by.organization_name if q.created_by else None)),
                    'assessment': q.assessment,
                    'topic': q.topic,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'question': q.question,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                    'correct_answer': q.correct_answer,
                    'correct_answers': q.correct_answers if q.correct_answers else [],
                    'time_limit': q.time_limit,
                    'created_at': q.created_at.isoformat() if q.created_at else None,
                },
            },
            status=status.HTTP_201_CREATED
        )

    except OperationalError:
        # DB unreachable (common when Supabase host/port blocked or VPN/internet down)
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while creating question. '
                    'Please check your internet/VPN and that the DB host/port (5432) is reachable, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in create_question_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while creating question: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_manual_questions_view(request):
    """
    Fetch manual questions created for a given custom_assessment_id.
    Query params:
    - custom_assessment_id: required
    """
    try:
        custom_assessment_id = request.GET.get('custom_assessment_id', None)
        if custom_assessment_id is None or str(custom_assessment_id).strip() == '':
            return Response({'error': 'custom_assessment_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            caid = int(custom_assessment_id)
        except (TypeError, ValueError):
            return Response({'error': 'custom_assessment_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = (
            Question.objects.filter(custom_assessment_id=caid)
            .select_related('created_by', 'custom_assessment')
            .order_by('created_at')
        )
        q_list = _db_call_with_retry(lambda: list(qs), retries=1)

        # Also fetch CodingQuestions for this custom_assessment_id
        coding_qs = CodingQuestion.objects.filter(custom_assessment_id=caid).order_by('created_at')
        coding_list = _db_call_with_retry(lambda: list(coding_qs), retries=1)

        results = []
        # Add regular questions
        for q in q_list:
            results.append(
                {
                    'id': q.id,
                    'company_name': (q.organization_name_snapshot or (q.created_by.organization_name if q.created_by else None)),
                    'assessment': q.assessment,
                    'topic': q.topic,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'question': q.question,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                    'correct_answer': q.correct_answer,
                    'correct_answers': q.correct_answers if q.correct_answers else [],
                    'time_limit': q.time_limit,
                    'created_at': q.created_at.isoformat() if q.created_at else None,
                }
            )

        # Add coding questions
        for cq in coding_list:
            results.append(
                {
                    'id': cq.id,
                    'company_name': cq.organization_name_snapshot,
                    'assessment': 'Coding Challenge',
                    'topic': 'Coding', # This ensures it groups under "Coding" or similar if needed
                    'question_type': 'CODING',
                    'difficulty': cq.difficulty,
                    'question': cq.title, # Title is the main identifier
                    'title': cq.title,
                    'description': cq.description,
                    'language': cq.language,
                    'languages': cq.languages,
                    'mode': cq.mode,
                    'starter_code': cq.starter_code,
                    'schema_sql': cq.schema_sql,
                    'database_engine': cq.database_engine,
                    'time_limit_ms': cq.time_limit_ms,
                    'memory_limit_mb': cq.memory_limit_mb,
                    'created_at': cq.created_at.isoformat() if cq.created_at else None,
                }
            )

        # Sort combined results by created_at
        results.sort(key=lambda x: x.get('created_at') or '', reverse=False)

        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)

    except OperationalError:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while fetching manual questions. '
                    'Please check your internet/VPN and DB connectivity, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in get_manual_questions_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while fetching manual questions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _extract_text_from_uploaded_file(uploaded_file) -> tuple[str, str]:
    """
    Return (text, filename). Supports PDF, DOCX, TXT.
    """
    filename = getattr(uploaded_file, 'name', 'upload').lower()
    content = uploaded_file.read()
    text = ""
    if filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            text += (page.extract_text() or '') + "\n"
    elif filename.endswith('.doc'):
        # Legacy .doc (binary) is not supported by python-docx; require DOCX.
        raise ValueError('DOC files are not supported. Please convert the Word file to .docx and upload again.')
    elif filename.endswith('.docx'):
        doc = Document(io.BytesIO(content))
        # Paragraphs (includes most body text, lists, etc.)
        for p in doc.paragraphs:
            text += (p.text or '') + "\n"
        # Tables (Word docs often store content inside tables; python-docx won't include these in paragraphs)
        try:
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        cell_text = (cell.text or '').strip()
                        if cell_text:
                            text += cell_text + "\n"
        except Exception:
            # If tables are malformed, still return paragraph text.
            pass
    else:
        # fallback: treat as UTF-8 text
        try:
            text = content.decode('utf-8', errors='ignore')
        except Exception:
            text = str(content)
    return text, filename


def _normalize_lines(text: str) -> list[str]:
    lines = (text or '').replace('\r\n', '\n').replace('\r', '\n').split('\n')
    return [ln.strip() for ln in lines if ln.strip()]


def _parse_question_blocks(lines: list[str]) -> list[list[str]]:
    """
    Split into blocks by Q markers; fallback to blank-line style already removed, so heuristic.
    """
    blocks: list[list[str]] = []
    current: list[str] = []
    started = False
    for ln in lines:
        # Start a new block if it looks like "Q1." or "1)" etc.
        if re.match(r'^(?:q(?:uestion)?\s*)?\d+[\).:\-]\s*', ln, re.IGNORECASE):
            started = True
            if current:
                blocks.append(current)
            current = [ln]
        else:
            # Ignore any preamble/header text before the first question marker
            if not started:
                continue
            current.append(ln)
    if current:
        blocks.append(current)
    # If it didn't split well (single huge block), try to split by "Answer:" occurrences
    if len(blocks) <= 1:
        blocks = []
        current = []
        for ln in lines:
            # Ignore any preamble/header text before the first question marker
            if not started and not re.match(r'^(?:q(?:uestion)?\s*)?\d+[\).:\-]\s*', ln, re.IGNORECASE):
                continue
            started = True
            current.append(ln)
            # Word/PDF extraction sometimes puts "Answer:" mid-line; treat that as a block terminator too.
            if re.search(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', ln, re.IGNORECASE):
                blocks.append(current)
                current = []
        if current:
            blocks.append(current)
    return [b for b in blocks if any(b)]


def _parse_single_block(block: list[str], defaults: dict) -> tuple[Optional[dict], list[str]]:
    """
    Parse one question block into our schema.
    Returns (question_dict or None, warnings)
    """
    warnings: list[str] = []
    text_lines = [ln.strip() for ln in block if ln.strip()]
    if not text_lines:
        return None, warnings

    raw = " ".join(text_lines)

    # Detect explicit type (only from explicit MCQ/MSQ/TF markers, not from words in a sentence)
    qtype = None
    for ln in text_lines[:3]:
        m = re.search(r'\b(MCQ|MSQ|TF)\b', ln, re.IGNORECASE)
        if m:
            qtype = m.group(1).upper()
            break

    # Parse options (allow optional leading bullets like "• A)" or "- A)")
    opt_re = re.compile(r'^[\s\-\*\u2022]*?(A|B|C|D)\s*[\).:\-]\s*(.+)$', re.IGNORECASE)
    options = {}
    for ln in text_lines:
        m = opt_re.match(ln)
        if m:
            options[m.group(1).upper()] = m.group(2).strip()

    # Parse answer line
    ans_line = None
    for ln in text_lines[::-1]:
        # "Answer:" may appear mid-line depending on extraction; detect anywhere in the line.
        if re.search(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', ln, re.IGNORECASE):
            ans_line = ln
            break
    correct_answer = None
    correct_answers: list[str] = []
    tf_answer_word = False
    if ans_line:
        # Extract the substring after the first "Answer:"/"Correct answer:" marker
        m = re.search(r'(?:answer|correct(?:\s*answer)?)\s*[:\-]\s*(.+)$', ans_line, re.IGNORECASE)
        val = (m.group(1).strip() if m else '').strip()
        # Normalize for TF words
        if re.match(r'^(true|false)\b', val, re.IGNORECASE):
            tf_answer_word = True
            correct_answer = 'A' if val.lower().startswith('true') else 'B'
        else:
            letters = re.findall(r'[ABCD]', val.upper())
            if letters:
                if len(set(letters)) > 1:
                    correct_answers = list(dict.fromkeys(letters))
                else:
                    correct_answer = letters[0]

    # If options weren't detected line-by-line, attempt to extract inline options from the full block text.
    # This handles PDFs where options are emitted on the same line like: "A) ... B) ... C) ... D) ..."
    if not options:
        raw_for_options = raw
        if ans_line:
            # Remove the answer line to avoid confusing option extraction in edge cases
            raw_for_options = raw_for_options.replace(ans_line, ' ')
        opt_marker = re.compile(r'\b([ABCD])\s*[\).:\-]\s*', re.IGNORECASE)
        matches = list(opt_marker.finditer(raw_for_options))
        if matches:
            for idx, m in enumerate(matches):
                key = m.group(1).upper()
                start = m.end()
                end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_for_options)
                value = raw_for_options[start:end].strip()
                # Trim any trailing "Answer:" text that might appear in the same chunk (often mid-line)
                value = re.split(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', value, maxsplit=1, flags=re.IGNORECASE)[0].strip()
                if value:
                    options[key] = value

    # Infer type if missing
    if not qtype:
        if tf_answer_word:
            qtype = 'TF'
        elif options.get('A', '').lower() in ('true', 'false') and options.get('B', '').lower() in ('true', 'false'):
            qtype = 'TF'
        elif correct_answers:
            qtype = 'MSQ'
        else:
            qtype = 'MCQ'

    # Parse question text: take first non-metadata line, strip Q prefix and type tokens.
    # If "Answer:" is on the SAME LINE as the question (common in DOCX), use the part before "Answer:".
    q_text = None
    for ln in text_lines:
        if opt_re.match(ln):
            continue
        if re.search(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', ln, re.IGNORECASE):
            # Example: "26. JVM is platform dependent. Answer: True"
            # Keep left side as the question text candidate.
            left = re.split(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', ln, maxsplit=1, flags=re.IGNORECASE)[0].strip()
            if not left:
                continue
            ln = left
        # Remove leading "Q1." etc
        cleaned = re.sub(r'^(?:q(?:uestion)?\s*)?\d+[\).:\-]\s*', '', ln, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r'\b(MCQ|MSQ|TF)\b', '', cleaned, flags=re.IGNORECASE).strip(' :-')
        if cleaned:
            q_text = cleaned
            break

    if not q_text:
        warnings.append('Could not detect question text.')
        return None, warnings

    # Ensure required options
    if qtype == 'TF':
        option_a = 'True'
        option_b = 'False'
        option_c = None
        option_d = None
        if correct_answer not in ('A', 'B'):
            warnings.append('TF question missing valid answer; defaulting to A.')
            correct_answer = 'A'
    else:
        option_a = options.get('A')
        option_b = options.get('B')
        option_c = options.get('C')
        option_d = options.get('D')
        if not option_a or not option_b:
            warnings.append('Missing option A or B.')
        if qtype == 'MCQ':
            if correct_answer not in ('A', 'B', 'C', 'D'):
                warnings.append('MCQ missing correct_answer.')
        else:  # MSQ
            if not correct_answers:
                warnings.append('MSQ missing correct_answers.')

    # Optional time parsing e.g. "Time: 01:30"
    time_to_answer = defaults.get('time_to_answer') or None
    for ln in text_lines:
        tm = re.match(r'^(?:time|time\s*limit)\s*[:\-]\s*(.+)$', ln, re.IGNORECASE)
        if tm:
            time_to_answer = tm.group(1).strip()
            break

    return (
        {
            'assessment': defaults.get('assessment') or 'Manual',
            'topic': defaults.get('topic') or '',
            'question_type': qtype,
            'question': q_text,
            'option_a': option_a,
            'option_b': option_b,
            'option_c': option_c,
            'option_d': option_d,
            'correct_answer': correct_answer,
            'correct_answers': correct_answers,
            'time_to_answer': time_to_answer,
        },
        warnings,
    )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def parse_questions_document_view(request):
    """
    Parse uploaded PDF/DOCX into question objects.
    multipart/form-data:
      - file: required
      - assessment: optional
      - topic: optional (default topic if PDF doesn't include)
      - experience_level: optional (not used in parsing; passed to save step)
    """
    try:
        if 'file' not in request.FILES:
            return Response({'error': 'file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']
        assessment = (request.data.get('assessment') or '').strip() or 'Manual'
        topic = (request.data.get('topic') or '').strip() or ''
        time_to_answer = (request.data.get('time_to_answer') or '').strip() or None

        try:
            text, filename = _extract_text_from_uploaded_file(uploaded_file)
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        lines = _normalize_lines(text)
        if not lines:
            return Response({'error': 'No text could be extracted from the document.'}, status=status.HTTP_400_BAD_REQUEST)

        blocks = _parse_question_blocks(lines)
        defaults = {'assessment': assessment, 'topic': topic, 'time_to_answer': time_to_answer}

        questions: list[dict] = []
        errors: list[str] = []
        for i, block in enumerate(blocks, start=1):
            q, warns = _parse_single_block(block, defaults)
            if q:
                questions.append(q)
                for w in warns:
                    errors.append(f"Q{i}: {w}")
            else:
                errors.append(f"Q{i}: Could not parse this block.")

        return Response({'filename': filename, 'count': len(questions), 'questions': questions, 'errors': errors}, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error in parse_questions_document_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while parsing: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_create_questions_view(request):
    """
    Bulk create questions in DB.
    JSON body:
    {
      "custom_assessment_id": 123,
      "user_email": "...",
      "organization_name": "...",
      "questions": [ {question payload compatible with create_question_view}, ... ]
    }
    """
    try:
        data = request.data or {}
        custom_assessment_id = data.get('custom_assessment_id', None)
        print(f"bulk_create_questions_view: custom_assessment_id={custom_assessment_id}")
        user_email = data.get('user_email', None)
        organization_name = data.get('organization_name', None)
        questions = data.get('questions', [])

        if not custom_assessment_id:
            return Response({'error': 'custom_assessment_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(questions, list) or len(questions) == 0:
            return Response({'error': 'questions must be a non-empty array.'}, status=status.HTTP_400_BAD_REQUEST)

        # Preload shared context to avoid N queries for each question
        try:
            caid = int(custom_assessment_id)
        except (TypeError, ValueError):
            return Response({'error': 'custom_assessment_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            custom_assessment = _db_call_with_retry(lambda: CustomAssessment.objects.get(id=caid), retries=1)
        except CustomAssessment.DoesNotExist:
            return Response(
                {'error': f'Custom assessment ID {caid} was not found. Please go back to Review page and recreate the assessment.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_by = None
        resolved_user_email = (user_email or '').strip().lower() or None
        if resolved_user_email:
            try:
                created_by = UserProfile.objects.get(email=resolved_user_email)
            except UserProfile.DoesNotExist:
                created_by = None

        company = None
        resolved_org = (organization_name or '').strip() or None
        if resolved_org:
            company, _ = Company.objects.get_or_create(name=resolved_org)

        created_ids = []
        errors = []

        for idx, q in enumerate(questions, start=1):
            try:
                payload = dict(q or {})
                payload['custom_assessment_id'] = custom_assessment_id
                if user_email:
                    payload['user_email'] = user_email
                if organization_name:
                    payload['organization_name'] = organization_name

                created = _create_question_from_payload(
                    payload,
                    preloaded_custom_assessment=custom_assessment,
                    preloaded_created_by=created_by,
                    preloaded_company=company,
                )
                created_ids.append(created.id)
            except Exception as e:
                import traceback
                error_msg = f"Q{idx}: {str(e)}"
                print(f"Error in bulk_create_questions_view during question {idx} creation: {error_msg}")
                # print(traceback.format_exc())
                errors.append(error_msg)

        return Response(
            {
                'created_count': len([x for x in created_ids if x]),
                'created_ids': [x for x in created_ids if x],
                'errors': errors,
            },
            status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_207_MULTI_STATUS
        )

    except OperationalError:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while bulk creating questions. '
                    'Please check your internet/VPN and DB connectivity, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in bulk_create_questions_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while bulk creating: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_questions_by_skills_view(request):
    """
    Get questions for multiple skills/topics.
    Query parameters:
    - skills: Comma-separated list of skills
    - limit_per_skill: Number of questions per skill (default: all available)
    - question_type: Filter by type (optional)
    - difficulty: Filter by difficulty (optional)
    """
    try:
        skills_param = request.GET.get('skills', '').strip()
        limit_per_skill = request.GET.get('limit_per_skill', None)
        question_type = request.GET.get('question_type', '').strip()
        difficulty = request.GET.get('difficulty', '').strip()
        
        if not skills_param:
            return Response(
                {'error': 'Skills parameter is required. Provide comma-separated list of skills.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        skills = [s.strip() for s in skills_param.split(',') if s.strip()]
        
        if not skills:
            return Response(
                {'error': 'No valid skills provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get questions for each skill
        questions_by_topic = {}
        total_count = 0
        
        for skill in skills:
            # Try exact match first, then case-insensitive contains
            questions = Question.objects.filter(
                visibility='GLOBAL',
                company_id__isnull=True
            ).filter(
                models.Q(topic__iexact=skill) | models.Q(topic__icontains=skill)
            )
            
            if question_type:
                questions = questions.filter(question_type=question_type.upper())
            
            if difficulty:
                questions = questions.filter(difficulty=difficulty.lower())
            
            # Order by created_at for consistent results
            questions = questions.order_by('created_at')
            
            if limit_per_skill:
                try:
                    limit = int(limit_per_skill)
                    questions = questions[:limit]
                except ValueError:
                    pass
            
            # Serialize questions
            questions_list = []
            for q in questions:
                question_data = {
                    'id': q.id,
                    'assessment': q.assessment,
                    'topic': q.topic,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'question': q.question,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                    'correct_answer': q.correct_answer,
                    'correct_answers': q.correct_answers if q.correct_answers else [],
                    'time_limit': q.time_limit,
                    'created_at': q.created_at.isoformat() if q.created_at else None,
                }
                questions_list.append(question_data)
            
            questions_by_topic[skill] = questions_list
            total_count += len(questions_list)
        
        return Response(
            {
                'count': total_count,
                'skills': skills,
                'questions_by_topic': questions_by_topic,
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        print(f"Error in get_questions_by_skills_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while fetching questions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_custom_assessment_view(request):
    """
    Create and store a CustomAssessment record with all configuration data
    coming from the CustomAssessment page on the frontend.

    Expected request body (JSON):
    {
        "user": {
            "first_name": "...",
            "last_name": "...",
            "email": "...",
            "organization_name": "..."
        },
        "assessment": {
            "role": "...",
            "sub_roles": [...],
            "custom_role": "...",
            "experience_level": "entry|mid|senior|expert",
            "number_of_questions": 10,
            "time": "01:20:00",
            "auto_time": "01:20:00",
            "weights": {
                "common": 70,
                "role": 15,
                "resume": 15
            },
            "question_distribution": { "Python": 3, "Django": 2 },
            "removed_skills": [...],
            "extracted_skills": [...],
            "suggested_skills": [...],
            "common_skills": [...],
            "resume_file_name": "candidate_resume.pdf"
        }
    }
    """
    try:
        user_data = request.data.get('user', {}) or {}
        assessment_data = request.data.get('assessment', {}) or {}

        # Basic required fields validation
        role = assessment_data.get('role', '').strip()
        number_of_questions = assessment_data.get('number_of_questions', None)
        time_value = assessment_data.get('time', '').strip()

        if not role:
            return Response(
                {'error': 'role is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            number_of_questions = int(number_of_questions)
        except (TypeError, ValueError):
            return Response(
                {'error': 'number_of_questions must be an integer.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if number_of_questions < 1:
            return Response(
                {'error': 'number_of_questions must be at least 1.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not time_value:
            return Response(
                {'error': 'time is required (HH:MM:SS).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find linked UserProfile if possible (by email)
        email = (user_data.get('email') or '').strip().lower() or None
        user_profile = None
        if email:
            try:
                user_profile = UserProfile.objects.get(email=email)
            except UserProfile.DoesNotExist:
                user_profile = None

        weights = assessment_data.get('weights', {}) or {}

        custom_assessment = _db_call_with_retry(
            lambda: CustomAssessment.objects.create(
                user_profile=user_profile,
                first_name=user_data.get('first_name') or None,
                last_name=user_data.get('last_name') or None,
                email=email,
                organization_name=user_data.get('organization_name') or None,
                role=role,
                sub_roles=assessment_data.get('sub_roles') or [],
                custom_role=assessment_data.get('custom_role') or None,
                experience_level=assessment_data.get('experience_level') or None,
                number_of_questions=number_of_questions,
                time=time_value,
                auto_time=assessment_data.get('auto_time') or None,
                weight_common=int(weights.get('common', 70)),
                weight_role=int(weights.get('role', 15)),
                weight_resume=int(weights.get('resume', 15)),
                extracted_skills=assessment_data.get('extracted_skills') or [],
                suggested_skills=assessment_data.get('suggested_skills') or [],
                common_skills=assessment_data.get('common_skills') or [],
                question_distribution=assessment_data.get('question_distribution') or {},
                removed_skills=assessment_data.get('removed_skills') or [],
                resume_file_name=assessment_data.get('resume_file_name') or None,
            ),
            retries=1,
        )

        return Response(
            {
                'message': 'Custom assessment created successfully.',
                'id': custom_assessment.id,
                'created_at': custom_assessment.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED
        )

    except OperationalError:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while creating custom assessment. '
                    'Please check your internet/VPN and DB connectivity, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in create_custom_assessment_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while creating custom assessment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_custom_assessment_view(request, custom_assessment_id: int):
    """
    Fetch a CustomAssessment by ID.
    Used by the frontend to validate a locally-stored draftCustomAssessmentId.
    """
    try:
        try:
            caid = int(custom_assessment_id)
        except (TypeError, ValueError):
            return Response({'error': 'custom_assessment_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ca = _db_call_with_retry(lambda: CustomAssessment.objects.get(id=caid), retries=1)
        except CustomAssessment.DoesNotExist:
            return Response({'error': f'CustomAssessment with id {caid} not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                'id': ca.id,
                'created_at': ca.created_at.isoformat() if ca.created_at else None,
                'updated_at': ca.updated_at.isoformat() if getattr(ca, 'updated_at', None) else None,
                'role': ca.role,
                'custom_role': ca.custom_role,
                'experience_level': ca.experience_level,
                'number_of_questions': ca.number_of_questions,
                'time': ca.time,
                'organization_name': ca.organization_name,
                'email': ca.email,
            },
            status=status.HTTP_200_OK
        )

    except OperationalError:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while fetching custom assessment. '
                    'Please check your internet/VPN and DB connectivity, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in get_custom_assessment_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while fetching custom assessment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def create_assessment_view(request):
    """
    Create an Assessment record and associated AssessmentQuestion rows
    from a previously saved CustomAssessment and the final question list.

    Expected request body (JSON):
    {
        "custom_assessment_id": 1,
        "question_ids": [1, 2, 3, ...],  // objective questions in display order
        "coding_question_ids": [10, 11], // optional coding questions (order preserved)
        "coding_allowed_languages": ["python","javascript"] // optional override (fallback to question.languages)
    }
    """
    try:
        # GET: list assessments (simple dashboard feed)
        if request.method == 'GET':
            qs = Assessment.objects.all().order_by('-created_at')

            # Date filtering
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            if start_date:
                qs = qs.filter(created_at__date__gte=start_date)
            if end_date:
                qs = qs.filter(created_at__date__lte=end_date)

            qs = qs[:500]
            results = []
            for a in qs:
                results.append(
                    {
                        'id': a.id,
                        'name': a.name,
                        'display_name': a.display_name,
                        'role': a.role,
                        'experience_level': a.experience_level,
                        'assessment_type': getattr(a, 'assessment_type', None),
                        'total_questions': a.total_questions,
                        'coding_question_count': getattr(a, 'coding_question_count', 0),
                        'total_time': a.total_time,
                        'total_candidates': getattr(a, 'total_candidates', 0),
                        'invited': getattr(a, 'invited', 0),
                        'submitted': getattr(a, 'submitted', 0),
                        'evaluated': getattr(a, 'evaluated', 0),
                        'shortlisted': getattr(a, 'shortlisted', 0),
                        'on_proctoring': getattr(a, 'on_proctoring', False),
                        'invite_token': str(getattr(a, 'invite_token', '')) if getattr(a, 'invite_token', None) else None,
                        'created_at': a.created_at.isoformat() if a.created_at else None,
                    }
                )
            return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)

        custom_assessment_id = request.data.get('custom_assessment_id', None)
        question_ids = request.data.get('question_ids', [])
        coding_question_ids = request.data.get('coding_question_ids', [])
        coding_allowed_languages = request.data.get('coding_allowed_languages', None)
        explicit_name = (request.data.get('name') or '').strip() or None
        explicit_display_name = (request.data.get('display_name') or '').strip() or None
        explicit_role = (request.data.get('role') or '').strip() or None
        explicit_experience_level = (request.data.get('experience_level') or '').strip() or None

        custom_assessment = None
        if custom_assessment_id:
            # DB connections to Supabase can be flaky in dev; retry once on OperationalError
            for attempt in range(2):
                try:
                    custom_assessment = CustomAssessment.objects.get(id=custom_assessment_id)
                    break
                except CustomAssessment.DoesNotExist:
                    return Response(
                        {'error': f'CustomAssessment with id {custom_assessment_id} not found.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                except OperationalError as e:
                    close_old_connections()
                    if attempt == 0:
                        continue
                    return Response(
                        {
                            'error': (
                                'Database connection failed while creating assessment. '
                                'Please check your internet/VPN or Supabase DB host, then try again.'
                            )
                        },
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )

        # IMPORTANT: This is the NEW validation that allows empty question_ids for coding-only assessments
        print(f"[NEW CODE CHECK] Received question_ids={question_ids}, coding_question_ids={coding_question_ids}")
        
        if not isinstance(question_ids, list):
            return Response(
                {'error': '[NEW CODE] question_ids must be an array (can be empty when coding_question_ids are provided).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Coding IDs (optional)
        # Supports [id, id, ...] OR [{id:1, difficulty:...}, ...]
        coding_seen = set()
        ordered_coding_ids = []
        coding_overrides = {} # map id -> dict of overrides

        if isinstance(coding_question_ids, list):
            for item in coding_question_ids:
                cqid_int = None
                overrides = {}
                if isinstance(item, (int, str)):
                    try:
                        cqid_int = int(item)
                    except (TypeError, ValueError):
                        continue
                elif isinstance(item, dict):
                    try:
                        cqid_int = int(item.get('id'))
                        if 'difficulty' in item:
                            overrides['difficulty'] = item['difficulty']
                        if 'time_limit_ms' in item:
                            overrides['time_limit_ms'] = int(item['time_limit_ms'])
                    except (TypeError, ValueError):
                        continue
                
                if cqid_int and cqid_int not in coding_seen:
                    coding_seen.add(cqid_int)
                    ordered_coding_ids.append(cqid_int)
                    if overrides:
                        coding_overrides[cqid_int] = overrides
        
        # Debug: log what we received
        print(f"[DEBUG] create_assessment: question_ids={question_ids}, coding_question_ids={coding_question_ids}, ordered_coding_ids={ordered_coding_ids}")

        # Ensure we use unique IDs while preserving order (objective)
        seen = set()
        ordered_unique_ids = []
        for qid in question_ids:
            try:
                qid_int = int(qid)
            except (TypeError, ValueError):
                continue
            if qid_int not in seen:
                seen.add(qid_int)
                ordered_unique_ids.append(qid_int)

        if not ordered_unique_ids and not ordered_coding_ids:
            return Response(
                {'error': 'Provide at least one objective or coding question ID.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch all referenced questions (objective)
        questions_qs = Question.objects.filter(id__in=ordered_unique_ids) if ordered_unique_ids else Question.objects.none()
        if ordered_unique_ids and questions_qs.count() != len(ordered_unique_ids):
            return Response(
                {'error': 'Some question IDs do not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        coding_qs = CodingQuestion.objects.filter(id__in=ordered_coding_ids, is_active=True) if ordered_coding_ids else []
        if ordered_coding_ids and len(coding_qs) != len(ordered_coding_ids):
            return Response(
                {'error': 'Some coding question IDs are invalid or inactive.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        def _seconds_to_hhmmss(seconds: int) -> str:
            seconds = max(0, int(seconds or 0))
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h:02d}:{m:02d}:{s:02d}"

        # Compute total time from actual question list (includes manual questions)
        total_time_seconds = 0
        for q in questions_qs:
            try:
                total_time_seconds += int(getattr(q, 'time_limit', None) or 120)
            except Exception:
                total_time_seconds += 120

        coding_total_seconds = 0
        for cq in coding_qs:
            try:
                # Use override time if provided, otherwise use original question time
                override = coding_overrides.get(cq.id, {})
                if 'time_limit_ms' in override:
                    coding_total_seconds += int(override['time_limit_ms']) // 1000
                else:
                    coding_total_seconds += int(getattr(cq, 'time_limit_ms', None) or 0) // 1000
            except Exception:
                pass
        total_time_seconds += coding_total_seconds

        # Debug: Log the total_time received from frontend vs. calculated
        received_total_time = request.data.get('total_time')
        calculated_total_time = _seconds_to_hhmmss(total_time_seconds)
        print(f"[DEBUG] create_assessment: received_total_time={received_total_time}, calculated_total_time={calculated_total_time}, coding_total_seconds={coding_total_seconds}")

        # New fields for split assessment
        # Use request.data and ensure defaults if None is passed
        objective_time_limit = request.data.get('objective_time_limit')
        coding_time_limit = request.data.get('coding_time_limit')
        
        has_objective_cutoff_val = request.data.get('has_objective_cutoff')
        has_objective_cutoff = bool(has_objective_cutoff_val) if has_objective_cutoff_val is not None else False
        
        min_objective_pass_percentage = float(request.data.get('min_objective_pass_percentage') or 0.0)
        weightage_objective = int(request.data.get('weightage_objective') or 0)
        weightage_coding = int(request.data.get('weightage_coding') or 100)

        # Create Assessment
        assessment = Assessment.objects.create(
            user_profile=custom_assessment.user_profile if custom_assessment else None,
            custom_assessment=custom_assessment,
            role=explicit_role or (custom_assessment.role if custom_assessment else None),
            experience_level=explicit_experience_level or (custom_assessment.experience_level if custom_assessment else None),
            total_questions=len(ordered_unique_ids),
            total_time=request.data.get('total_time') or _seconds_to_hhmmss(total_time_seconds),
            coding_total_time=_seconds_to_hhmmss(coding_total_seconds) if coding_total_seconds else None,
            coding_question_count=len(ordered_coding_ids),
            min_pass_percentage=float(request.data.get('min_pass_percentage') or 60.0),
            
            # Save new fields
            objective_time_limit=objective_time_limit,
            coding_time_limit=coding_time_limit,
            has_objective_cutoff=has_objective_cutoff,
            min_objective_pass_percentage=min_objective_pass_percentage,
            weightage_objective=weightage_objective,
            weightage_coding=weightage_coding,

            total_points=int(request.data.get('total_points') or 0),
            status='draft',
        )

        # Populate human-friendly name/display_name if missing
        try:
            base_name = (
                explicit_display_name
                or explicit_name
                or getattr(custom_assessment, 'custom_role', None)
                or getattr(custom_assessment, 'role', None)
                or 'Assessment'
            )
            if explicit_display_name:
                assessment.display_name = explicit_display_name
            if explicit_name:
                assessment.name = explicit_name
            if not getattr(assessment, 'display_name', None):
                assessment.display_name = base_name
            if not getattr(assessment, 'name', None):
                assessment.name = f"{base_name} - {assessment.id}"
            assessment.save(update_fields=['display_name', 'name'])
        except Exception:
            pass

        # Map ID -> Question for quick lookup
        questions_by_id = {q.id: q for q in questions_qs}

        # Create AssessmentQuestion entries in the same order,
        # copying a snapshot of all important question fields
        assessment_questions = []
        for index, qid in enumerate(ordered_unique_ids, start=1):
            q = questions_by_id.get(qid)
            if not q:
                continue
            
            # Debug: Print question data to verify it exists
            print(f"Question {q.id}: type={q.question_type}, difficulty={q.difficulty}, time_limit={q.time_limit}")
            
            # Copy all question details as snapshot (use getattr with defaults for safety)
            assessment_questions.append(
                AssessmentQuestion(
                    assessment=assessment,
                    question=q,
                    skill=getattr(q, 'topic', '') or '',
                    order=index,
                    question_type=getattr(q, 'question_type', '') or '',
                    difficulty=getattr(q, 'difficulty', '') or '',
                    time_limit=getattr(q, 'time_limit', None) or 120,
                    option_a=getattr(q, 'option_a', None) or '',
                    option_b=getattr(q, 'option_b', None) or '',
                    option_c=getattr(q, 'option_c', None) or '',
                    option_d=getattr(q, 'option_d', None) or '',
                    correct_answer=getattr(q, 'correct_answer', None) or '',
                    correct_answers=getattr(q, 'correct_answers', None) or [],
                )
            )

        AssessmentQuestion.objects.bulk_create(assessment_questions)

        # Coding snapshots (ordered after objective block, but preserve provided order)
        if ordered_coding_ids:
            coding_by_id = {cq.id: cq for cq in coding_qs}
            coding_allowed = []
            if isinstance(coding_allowed_languages, list):
                coding_allowed = [str(v).strip().lower() for v in coding_allowed_languages if str(v).strip()]
            coding_snapshots = []
            order_offset = len(assessment_questions) + 1
            for idx, cqid in enumerate(ordered_coding_ids, start=0):
                cq = coding_by_id.get(cqid)
                if not cq:
                    continue
                langs = [str(v).strip().lower() for v in (cq.languages or []) if str(v).strip()]
                # Intersection logic: Only show languages that are BOTH in the assessment global list AND supported by this question.
                # If assessment global list is empty, show all question-supported languages.
                if coding_allowed:
                    allowed = [l for l in langs if l in coding_allowed]
                    if not allowed and langs:
                         # Fallback to the first supported language of the question if intersection is empty
                         # (prevents an empty dropdown being replaced by 'everything')
                         allowed = [langs[0]]
                    elif not allowed and getattr(cq, 'language', None):
                         allowed = [str(cq.language).lower()]
                else:
                    allowed = langs or ([str(cq.language).lower()] if getattr(cq, 'language', None) else [])
                ov = coding_overrides.get(cqid, {})
                # Use override if present, else fallback to question default
                t_limit = ov.get('time_limit_ms') if 'time_limit_ms' in ov else int(getattr(cq, 'time_limit_ms', None) or 0)
                diff = ov.get('difficulty') if 'difficulty' in ov else getattr(cq, 'difficulty', '')

                coding_snapshots.append(
                    AssessmentCodingQuestion(
                        assessment=assessment,
                        coding_question=cq,
                        order=order_offset + idx,
                        title=getattr(cq, 'title', '') or '',
                        description=getattr(cq, 'description', '') or '',
                        languages=langs,
                        allowed_languages=allowed,
                        mode=getattr(cq, 'mode', None) or '',
                        starter_code=getattr(cq, 'starter_code', None) or '',
                        template_code=getattr(cq, 'template_code', None) or '',
                        difficulty=diff,
                        time_limit_ms=t_limit,
                        memory_limit_mb=int(getattr(cq, 'memory_limit_mb', None) or 256),
                    )
                )
            AssessmentCodingQuestion.objects.bulk_create(coding_snapshots)

        return Response(
            {
                'message': 'Assessment created successfully.',
                'assessment_id': assessment.id,
                'total_questions': assessment.total_questions,
                'total_time': assessment.total_time,
                'coding_question_count': assessment.coding_question_count,
                'coding_total_time': assessment.coding_total_time,
                'invite_token': str(getattr(assessment, 'invite_token', '')) if getattr(assessment, 'invite_token', None) else None,
            },
            status=status.HTTP_201_CREATED
        )

    except OperationalError as e:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while creating assessment. '
                    'Please check your internet/VPN or Supabase DB host, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in create_assessment_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while creating assessment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_assessment_public_view(request, token):
    """
    Public (candidate) fetch by invite_token.
    Returns assessment metadata + question list (without correct answers).
    """
    try:
        try:
            assessment = Assessment.objects.get(invite_token=token)
        except Assessment.DoesNotExist:
            return Response({'error': 'Assessment not found.'}, status=status.HTTP_404_NOT_FOUND)

        aq_qs = (
            AssessmentQuestion.objects.filter(assessment=assessment)
            .select_related('question')
            .order_by('order')
        )
        acq_qs = (
            AssessmentCodingQuestion.objects.filter(assessment=assessment)
            .select_related('coding_question')
            .order_by('order')
        )
        questions = []
        for aq in aq_qs:
            questions.append(
                {
                    'id': aq.id,
                    'order': aq.order,
                    'skill': aq.skill,
                    'question_type': aq.question_type,
                    'difficulty': aq.difficulty,
                    'time_limit': aq.time_limit,
                    'question': aq.question.question if aq.question else None,
                    'option_a': aq.option_a,
                    'option_b': aq.option_b,
                    'option_c': aq.option_c,
                    'option_d': aq.option_d,
                }
            )

        acq_qs = (
            AssessmentCodingQuestion.objects.filter(assessment=assessment)
            .select_related('coding_question')
            .order_by('order')
        )
        coding_questions = []
        for acq in acq_qs:
            cq = acq.coding_question
            coding_questions.append(
                {
                    'id': acq.id,
                    'coding_question_id': cq.id if cq else None,
                    'order': acq.order,
                    'title': acq.title,
                    'description': acq.description,
                    'languages': acq.languages or [],
                    'allowed_languages': acq.allowed_languages or [],
                    'mode': acq.mode,
                    'starter_code': acq.starter_code,
                    'template_code': acq.template_code,
                    'time_limit_ms': acq.time_limit_ms,
                    'memory_limit_mb': acq.memory_limit_mb,
                }
            )

        return Response(
            {
                'assessment': {
                    'id': assessment.id,
                    'name': assessment.name,
                    'display_name': assessment.display_name,
                    'role': assessment.role,
                    'experience_level': assessment.experience_level,
                    'total_questions': assessment.total_questions,
                    'total_time': assessment.total_time,
                    'coding_total_time': assessment.coding_total_time,
                    'coding_question_count': assessment.coding_question_count,
                    'invite_token': str(assessment.invite_token) if assessment.invite_token else None,
                },
                'questions': questions,
                'coding_questions': coding_questions,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in get_assessment_public_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching assessment: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def get_assessment_detail_view(request, assessment_id: int):
    """
    Fetch or update a single assessment by numeric ID.
    """
    try:
        try:
            a = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            return Response({'error': 'Assessment not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PATCH':
            data = request.data
            if 'name' in data: a.name = data['name']
            if 'display_name' in data: a.display_name = data['display_name']
            if 'role' in data: a.role = data['role']
            if 'experience_level' in data: a.experience_level = data['experience_level']
            if 'min_pass_percentage' in data: 
                try:
                    a.min_pass_percentage = float(data['min_pass_percentage'])
                except ValueError:
                    pass
            if 'total_time' in data: a.total_time = data['total_time']
            a.save()
            return Response({'ok': True, 'message': 'Assessment updated successfully.'})

        return Response(
            {
                'id': a.id,
                'name': a.name,
                'display_name': a.display_name,
                'role': a.role,
                'experience_level': a.experience_level,
                'total_questions': a.total_questions,
                'total_time': a.total_time,
                'invite_token': str(a.invite_token) if getattr(a, 'invite_token', None) else None,
                'created_at': a.created_at.isoformat() if a.created_at else None,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in get_assessment_detail_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching assessment: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _is_valid_pan(pan: str) -> bool:
    if not pan:
        return True
    return bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan.strip().upper()))


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_invitations_and_send_email_view(request, assessment_id: int):
    """
    Create candidate invitation(s) for an assessment and send email(s) immediately.

    Body:
    {
      "candidates": [
        {
          "name":"...",
          "email":"...",
          "pan_number":"...",
          "phone":"...",
          "start_time": "...iso...",
          "end_time":"...iso...",
          "time_zone":"...",
          "start_grace_minutes": 30
        },
        ...
      ]
    }
    """
    try:
        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            return Response({'error': 'Assessment not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data or {}
        candidates = data.get('candidates', [])
        if not isinstance(candidates, list) or len(candidates) == 0:
            return Response({'error': 'candidates must be a non-empty array.'}, status=status.HTTP_400_BAD_REQUEST)

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'https://verifyhire.duckdns.org'

        results = []
        sent_count = 0
        fail_count = 0

        for idx, c in enumerate(candidates, start=1):
            payload = dict(c or {})
            name = (payload.get('name') or '').strip()
            email = (payload.get('email') or '').strip().lower()
            pan_number = (payload.get('pan_number') or payload.get('pan') or '').strip().upper() or None
            phone = (payload.get('phone') or '').strip() or None
            start_time_raw = (payload.get('start_time') or '').strip() or None
            end_time_raw = (payload.get('end_time') or '').strip() or None
            time_zone = (payload.get('time_zone') or '').strip() or None
            start_grace_minutes_raw = payload.get('start_grace_minutes', None)

            if not name:
                return Response({'error': f'Candidate #{idx}: name is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if not email:
                return Response({'error': f'Candidate #{idx}: email is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if pan_number and not _is_valid_pan(pan_number):
                return Response({'error': f'Candidate #{idx}: pan_number is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

            start_time = parse_datetime(start_time_raw) if start_time_raw else None
            end_time = parse_datetime(end_time_raw) if end_time_raw else None
            try:
                start_grace_minutes = int(start_grace_minutes_raw) if start_grace_minutes_raw is not None else 0
            except Exception:
                start_grace_minutes = 0
            start_grace_minutes = max(0, start_grace_minutes)

            invitation = CandidateInvitation.objects.create(
                assessment=assessment,
                name=name,
                email=email,
                pan_number=pan_number,
                phone=phone,
                start_time=start_time,
                end_time=end_time,
                time_zone=time_zone,
                start_grace_minutes=start_grace_minutes,
                status='draft',
            )

            start_link = f"{frontend_base.rstrip('/')}/take-assessment/{invitation.token}"
            subject = f"{assessment.display_name or assessment.name or 'Assessment'} - Invitation"

            # Read validity mode from payload
            validity_mode = (payload.get('validity_mode') or '').strip() or 'exact_window'

            # Convert UTC times to candidate's local timezone for display
            display_tz = time_zone or ''
            local_start = start_time
            local_end = end_time
            try:
                from zoneinfo import ZoneInfo
                if time_zone and start_time:
                    local_start = start_time.astimezone(ZoneInfo(time_zone))
                if time_zone and end_time:
                    local_end = end_time.astimezone(ZoneInfo(time_zone))
            except Exception:
                pass

            # Build schedule blocks based on validity mode
            if validity_mode == 'exact_window':
                # Show: Date, Start Time, End Time, Time Zone
                display_date = local_start.strftime('%B %d, %Y') if local_start else ''
                display_start_time = local_start.strftime('%I:%M %p') if local_start else ''
                display_end_time = local_end.strftime('%I:%M %p') if local_end else ''

                schedule_text = ''
                if display_date:
                    schedule_text = (
                        "Assessment Schedule:\n"
                        f"  Date: {display_date}\n"
                        f"  Start Time: {display_start_time}\n"
                    )
                    if display_end_time:
                        schedule_text += f"  End Time: {display_end_time}\n"
                    if display_tz:
                        schedule_text += f"  Time Zone: {display_tz}\n"
                    schedule_text += "\n"

                schedule_html = ''
                if display_date:
                    schedule_html = '<table style="border-collapse:collapse;margin:16px 0;">'
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 Date</td>'
                        f'<td style="padding:6px 0;">{display_date}</td>'
                        '</tr>'
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 Start Time</td>'
                        f'<td style="padding:6px 0;">{display_start_time}</td>'
                        '</tr>'
                    )
                    if display_end_time:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 End Time</td>'
                            f'<td style="padding:6px 0;">{display_end_time}</td>'
                            '</tr>'
                        )
                    if display_tz:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🌐 Time Zone</td>'
                            f'<td style="padding:6px 0;">{display_tz}</td>'
                            '</tr>'
                        )
                    schedule_html += '</table>'

            else:
                # date_anytime or one_week: Show Start Date, End Date, Available 12:00 AM to 11:59 PM
                display_start_date = local_start.strftime('%B %d, %Y') if local_start else ''
                display_end_date = local_end.strftime('%B %d, %Y') if local_end else ''

                schedule_text = ''
                if display_start_date:
                    schedule_text = (
                        "Assessment Schedule:\n"
                        f"  Start Date: {display_start_date}\n"
                    )
                    if display_end_date and display_end_date != display_start_date:
                        schedule_text += f"  End Date: {display_end_date}\n"
                    schedule_text += "  Available: 12:00 AM to 11:59 PM\n"
                    if display_tz:
                        schedule_text += f"  Time Zone: {display_tz}\n"
                    schedule_text += "\n"

                schedule_html = ''
                if display_start_date:
                    schedule_html = '<table style="border-collapse:collapse;margin:16px 0;">'
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 Start Date</td>'
                        f'<td style="padding:6px 0;">{display_start_date}</td>'
                        '</tr>'
                    )
                    if display_end_date and display_end_date != display_start_date:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 End Date</td>'
                            f'<td style="padding:6px 0;">{display_end_date}</td>'
                            '</tr>'
                        )
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 Available</td>'
                        '<td style="padding:6px 0;">12:00 AM to 11:59 PM</td>'
                        '</tr>'
                    )
                    if display_tz:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🌐 Time Zone</td>'
                            f'<td style="padding:6px 0;">{display_tz}</td>'
                            '</tr>'
                        )
                    schedule_html += '</table>'

            text_body = (
                f"Hi {name},\n\n"
                f"You have been invited to take an assessment.\n\n"
                f"Assessment: {assessment.display_name or assessment.name or 'Assessment'}\n\n"
                f"{schedule_text}"
                f"Start link: {start_link}\n\n"
                "Good luck!"
            )

            html_body = f"""
                <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #111; max-width: 600px;">
                  <p>Hi <strong>{name}</strong>,</p>
                  <p>You have been invited to take an assessment.</p>
                  <p><strong>Assessment:</strong> {assessment.display_name or assessment.name or 'Assessment'}</p>
                  {schedule_html}
                  <p style="margin: 24px 0;">
                    <a href="{start_link}" target="_blank"
                       style="background:#2563eb;color:#fff;padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:700;display:inline-block;">
                      Start Assessment
                    </a>
                  </p>
                  <p style="font-size:12px;color:#475569;">If the button doesn't work, copy this link: <br/>{start_link}</p>
                  <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;" />
                  <p style="font-size:12px;color:#94a3b8;">This is an automated message from VerifiHire AI. Please do not reply to this email.</p>
                </div>
            """

            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    to=[email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                invitation.status = 'sent'
                invitation.last_error = None
                invitation.save(update_fields=['status', 'last_error', 'updated_at'])
                sent_count += 1
            except Exception as mail_err:
                invitation.status = 'failed'
                invitation.last_error = str(mail_err)
                invitation.save(update_fields=['status', 'last_error', 'updated_at'])
                fail_count += 1

            results.append(
                {
                    'id': invitation.id,
                    'name': invitation.name,
                    'email': invitation.email,
                    'pan_number': invitation.pan_number,
                    'phone': invitation.phone,
                    'token': str(invitation.token),
                    'status': invitation.status,
                    'start_link': start_link,
                    'error': invitation.last_error,
                }
            )

        # Update simple invited counter
        try:
            assessment.invited = int(getattr(assessment, 'invited', 0) or 0) + sent_count
            assessment.total_candidates = max(int(getattr(assessment, 'total_candidates', 0) or 0), int(getattr(assessment, 'invited', 0) or 0))
            assessment.save(update_fields=['invited', 'total_candidates'])
        except Exception:
            pass

        return Response(
            {
                'message': 'Invitations processed.',
                'sent': sent_count,
                'failed': fail_count,
                'results': results,
            },
            status=status.HTTP_200_OK if fail_count == 0 else status.HTTP_207_MULTI_STATUS
        )
    except Exception as e:
        import traceback
        print(f"Error in create_invitations_and_send_email_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while sending invitations: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_invitation_public_view(request, token):
    """
    Public endpoint for candidates: fetch assessment + questions using a CandidateInvitation token.
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Single-use: if already submitted, block further access
        if inv.status == 'submitted':
            return Response({'error': 'Your exam has been completed.'}, status=status.HTTP_409_CONFLICT)

        assessment = inv.assessment

        def _hhmmss_to_seconds(value: str) -> int:
            try:
                parts = [int(x) for x in (value or '').split(':')]
                if len(parts) == 2:
                    h, m = 0, parts[0]
                    s = parts[1]
                elif len(parts) == 3:
                    h, m, s = parts
                else:
                    return 0
                return max(0, h * 3600 + m * 60 + s)
            except Exception:
                return 0

        def _make_aware_if_needed(dt):
            if not dt:
                return None
            try:
                return timezone.make_aware(dt, timezone.get_current_timezone()) if timezone.is_naive(dt) else dt
            except Exception:
                return dt

        start_time = _make_aware_if_needed(getattr(inv, 'start_time', None))
        end_time = _make_aware_if_needed(getattr(inv, 'end_time', None))
        try:
            grace_minutes = int(getattr(inv, 'start_grace_minutes', 0) or 0)
        except Exception:
            grace_minutes = 0
        grace_minutes = max(0, grace_minutes)

        # Start-time window enforcement:
        # - If NOT started yet: candidate can open only between [start_time, start_time + grace]
        # - If already started: do NOT block on grace (allows reconnect/refresh)
        now = timezone.now()
        if inv.started_at is None:
            # Build schedule info for error responses
            _tz = getattr(inv, 'time_zone', None) or ''
            _schedule_info = {}
            try:
                from zoneinfo import ZoneInfo
                _local_start = start_time.astimezone(ZoneInfo(_tz)) if _tz and start_time else start_time
                _local_end = end_time.astimezone(ZoneInfo(_tz)) if _tz and end_time else end_time
            except Exception:
                _local_start = start_time
                _local_end = end_time
            if _local_start:
                _schedule_info['start_date'] = _local_start.strftime('%B %d, %Y')
                _schedule_info['start_time_display'] = _local_start.strftime('%I:%M %p')
            if _local_end:
                _schedule_info['end_date'] = _local_end.strftime('%B %d, %Y')
                _schedule_info['end_time_display'] = _local_end.strftime('%I:%M %p')
            if _tz:
                _schedule_info['time_zone'] = _tz

            if start_time and now < start_time:
                return Response({'error': 'This exam has not started yet.', 'schedule': _schedule_info}, status=status.HTTP_403_FORBIDDEN)
            if start_time and grace_minutes > 0 and now > (start_time + timedelta(minutes=grace_minutes)):
                return Response({'error': 'The start window for this exam has expired.', 'schedule': _schedule_info}, status=status.HTTP_410_GONE)
            if end_time and now >= end_time:
                return Response({'error': 'This assessment link has expired.', 'schedule': _schedule_info}, status=status.HTTP_410_GONE)

        # Start timer on first access (persisted). Also cap by the scheduled end_time if provided.
        now = timezone.now()
        duration_seconds = _hhmmss_to_seconds(getattr(assessment, 'total_time', '') or '')
        if duration_seconds <= 0:
            duration_seconds = 0

        newly_started = False
        if inv.started_at is None:
            newly_started = True
            inv.started_at = now
            expires_at = now + timedelta(seconds=duration_seconds) if duration_seconds else None
            if end_time:
                expires_at = min(expires_at, end_time) if expires_at else end_time
            inv.expires_at = expires_at
        else:
            # Ensure existing expires_at is capped by end_time (in case schedule was set after start)
            if end_time:
                if inv.expires_at and inv.expires_at > end_time:
                    inv.expires_at = end_time
                elif inv.expires_at is None:
                    inv.expires_at = end_time

        # If expired, block access
        if inv.expires_at and now >= inv.expires_at:
            return Response({'error': 'This assessment link has expired.'}, status=status.HTTP_410_GONE)

        aq_qs = (
            AssessmentQuestion.objects.filter(assessment=assessment)
            .select_related('question')
            .order_by('order')
        )

        # Shuffle questions + options ONCE per invitation (persisted)
        aq_list = list(aq_qs)
        aq_by_id = {aq.id: aq for aq in aq_list}

        if not inv.question_order:
            ids = [aq.id for aq in aq_list]
            random.shuffle(ids)
            inv.question_order = ids

        if not isinstance(inv.option_map, dict) or not inv.option_map:
            inv.option_map = {}

        def _build_shuffled_options(aq: AssessmentQuestion):
            qtype = (aq.question_type or '').strip().upper()
            # TF defaults
            if qtype == 'TF' and not any([aq.option_a, aq.option_b, aq.option_c, aq.option_d]):
                base = [('A', 'True'), ('B', 'False')]
            else:
                base = []
                if aq.option_a: base.append(('A', aq.option_a))
                if aq.option_b: base.append(('B', aq.option_b))
                if aq.option_c: base.append(('C', aq.option_c))
                if aq.option_d: base.append(('D', aq.option_d))

            if not base:
                return [], {}

            shuffled = base[:]
            random.shuffle(shuffled)
            new_labels = ['A', 'B', 'C', 'D'][: len(shuffled)]
            mapping = {}
            options = []
            for new_label, (orig_label, text) in zip(new_labels, shuffled):
                mapping[new_label] = orig_label
                options.append({'key': new_label, 'text': text})
            return options, mapping

        questions = []
        changed = False
        for qid in inv.question_order:
            aq = aq_by_id.get(int(qid)) if qid is not None else None
            if not aq:
                continue

            key = str(aq.id)
            mapping = inv.option_map.get(key) if isinstance(inv.option_map, dict) else None
            if not mapping:
                options, mapping = _build_shuffled_options(aq)
                inv.option_map[key] = mapping
                changed = True
            else:
                # build options in the stored shuffled order (A..D)
                options = []
                for new_label in ['A', 'B', 'C', 'D']:
                    orig_label = mapping.get(new_label)
                    if not orig_label:
                        continue
                    text = getattr(aq, f"option_{orig_label.lower()}", None)
                    if text is None and (aq.question_type or '').strip().upper() == 'TF':
                        text = 'True' if orig_label == 'A' else 'False' if orig_label == 'B' else None
                    if text:
                        options.append({'key': new_label, 'text': text})

            questions.append(
                {
                    'id': aq.id,
                    'order': aq.order,
                    'skill': aq.skill,
                    'question_type': aq.question_type,
                    'difficulty': aq.difficulty,
                    'time_limit': aq.time_limit,
                    'question': aq.question.question if aq.question else None,
                    'options': options,
                }
            )

        # Coding questions (no shuffle; keep order)
        acq_qs = (
            AssessmentCodingQuestion.objects.filter(assessment=assessment)
            .select_related('coding_question')
            .order_by('order')
        )
        coding_questions = []
        for acq in acq_qs:
            cq = acq.coding_question
            coding_questions.append(
                {
                    'id': acq.id,
                    'coding_question_id': cq.id if cq else None,
                    'order': acq.order,
                    'title': acq.title,
                    'description': acq.description,
                    'languages': acq.languages or [],
                    'allowed_languages': acq.allowed_languages or [],
                    'mode': acq.mode,
                    'starter_code': acq.starter_code,
                    'template_code': acq.template_code,
                    'time_limit_ms': acq.time_limit_ms,
                    'memory_limit_mb': acq.memory_limit_mb,
                }
            )

        if changed or newly_started:
            inv.save(update_fields=['started_at', 'expires_at', 'question_order', 'option_map', 'updated_at'])

        # Fetch existing partial submission
        submission = getattr(inv, 'submission', None)
        submitted_coding_ids = []
        coding_answers = {}
        if submission and submission.answers:
            for k, v in submission.answers.items():
                if k.startswith('acq_'):
                    try:
                        qid_str = k.split('_', 1)[1]
                        submitted_coding_ids.append(int(qid_str))
                        if isinstance(v, dict):
                            coding_answers[qid_str] = {
                                'code': v.get('submitted_code'),
                                'language': v.get('language')
                            }
                    except:
                        pass

        return Response(
            {
                'invitation': {
                    'id': inv.id,
                    'name': inv.name,
                    'email': inv.email,
                    'pan_number': inv.pan_number,
                    'phone': inv.phone,
                    'token': str(inv.token),
                    'started_at': inv.started_at.isoformat() if inv.started_at else None,
                    'expires_at': inv.expires_at.isoformat() if inv.expires_at else None,
                    'status': inv.status,
                },
                'assessment': {
                    'id': assessment.id,
                    'name': assessment.name,
                    'display_name': assessment.display_name,
                    'role': assessment.role,
                    'experience_level': assessment.experience_level,
                    'total_questions': assessment.total_questions,
                    'total_time': assessment.total_time,
                    'coding_total_time': assessment.coding_total_time,
                    'coding_question_count': assessment.coding_question_count,
                    'objective_time_limit': assessment.objective_time_limit,
                    'coding_time_limit': assessment.coding_time_limit,
                    'has_objective_cutoff': assessment.has_objective_cutoff,
                    'min_objective_pass_percentage': assessment.min_objective_pass_percentage,
                    'weightage_objective': assessment.weightage_objective,
                    'weightage_coding': assessment.weightage_coding,
                },
                'questions': questions,
                'coding_questions': coding_questions,
                'submitted_coding_ids': submitted_coding_ids,
                'coding_answers': coding_answers,
                'remaining_seconds': int((inv.expires_at - now).total_seconds()) if inv.expires_at else None,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in get_invitation_public_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching invitation: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_invitation_answers_view(request, token):
    """
    Candidate submits answers for an invitation token.

    Body:
    {
      "answers": { "<assessment_question_id>": "A" | ["A","C"] }
    }
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Single-use: cannot submit twice
        if inv.status == 'submitted':
            return Response({'error': 'Your exam has been completed.'}, status=status.HTTP_409_CONFLICT)

        # Enforce expiry on submit as well (prevents submitting after time window)
        now = timezone.now()
        try:
            end_time = getattr(inv, 'end_time', None)
            end_time = timezone.make_aware(end_time, timezone.get_current_timezone()) if end_time and timezone.is_naive(end_time) else end_time
        except Exception:
            end_time = getattr(inv, 'end_time', None)

        # If not started yet, don't accept submit
        if inv.started_at is None:
            return Response({'error': 'Exam has not been started.'}, status=status.HTTP_403_FORBIDDEN)

        # Cap by expires_at (with grace) and/or scheduled end_time
        # Allow 2 minutes grace for auto-submit delays / network skew
        if inv.expires_at and now > (inv.expires_at + timedelta(minutes=2)):
            return Response({'error': 'Time is over. Submission is closed.'}, status=status.HTTP_410_GONE)
        if end_time and now >= end_time:
            # Hard stop for scheduled end time
            return Response({'error': 'Time is over. Submission is closed.'}, status=status.HTTP_410_GONE)

        data = request.data or {}
        answers = data.get('answers', None)
        if not isinstance(answers, dict) or len(answers.keys()) == 0:
            return Response({'error': 'answers must be a non-empty object.'}, status=status.HTTP_400_BAD_REQUEST)

        assessment = inv.assessment
        valid_aq_ids = set(
            AssessmentQuestion.objects.filter(assessment=assessment).values_list('id', flat=True)
        )
        # Filter to only valid question ids
        cleaned = {}
        for k, v in (answers or {}).items():
            try:
                aqid = int(k)
            except Exception:
                continue
            if aqid not in valid_aq_ids:
                continue
            cleaned[str(aqid)] = v

        if not cleaned:
            return Response({'error': 'No valid answers provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Auto evaluate
        PASS_PERCENT = int(os.environ.get('PASS_PERCENT', '60') or 60)

        aq_qs = AssessmentQuestion.objects.filter(assessment=assessment).select_related('question').order_by('order')
        total = aq_qs.count()
        score = 0

        def _norm_choice(v):
            if v is None:
                return ''
            return str(v).strip().upper()

        for aq in aq_qs:
            qid = str(aq.id)
            submitted = cleaned.get(qid, None)
            qtype = (aq.question_type or '').strip().upper()

            # Map submitted labels back to original labels if options were shuffled
            mapping = None
            try:
                mapping = (inv.option_map or {}).get(str(aq.id), None)
            except Exception:
                mapping = None

            if qtype == 'MSQ':
                submitted_list = submitted if isinstance(submitted, list) else []
                raw = [_norm_choice(x) for x in submitted_list if _norm_choice(x)]
                if mapping and isinstance(mapping, dict):
                    raw = [mapping.get(x, x) for x in raw]  # newLabel -> origLabel
                submitted_set = sorted(raw)
                correct_set = sorted([_norm_choice(x) for x in (aq.correct_answers or []) if _norm_choice(x)])
                if submitted_set and submitted_set == correct_set:
                    score += 1
            else:
                submitted_choice = _norm_choice(submitted)
                if mapping and isinstance(mapping, dict):
                    submitted_choice = _norm_choice(mapping.get(submitted_choice, submitted_choice))
                correct_choice = _norm_choice(aq.correct_answer)
                if submitted_choice and correct_choice and submitted_choice == correct_choice:
                    score += 1

        # Calculate Objective Score
        percentage = (float(score) / float(total) * 100.0) if total > 0 else 0.0
        
        # We need to fetch existing coding scores if any (for combined result)
        # But since this is a fresh get_or_create or update, we should check existing fields
        # However, `submission` object is created/fetched below. Let's do it after get_or_create.

        submission, created = CandidateSubmission.objects.get_or_create(
            invitation=inv,
        )
        
        # Store Objective Scores
        submission.objective_score = score
        submission.objective_total = total
        submission.objective_percentage = percentage
        submission.answers = cleaned

        # Combine with Coding Scores (preserve existing coding score if present)
        # coding_score defaults to 0 if not set
        
        # Weighted Scoring Logic
        # FIX: Check for None explicitly because 0 is a valid weight!
        w_obj = assessment.weightage_objective if assessment.weightage_objective is not None else 50
        w_cod = assessment.weightage_coding if assessment.weightage_coding is not None else 50
        
        # Normalize weights to ensure they sum to 100 (just in case)
        if w_obj + w_cod == 0:
            w_obj = 50
            w_cod = 50
            
        # Determine if we should use weights or simple average/sum
        # If it's a mixed assessment (both obj and coding exist), use weights.
        # If only objective, weight is effectively 100% objective.
        # If only coding, weight is effectively 100% coding.
        
        has_coding = assessment.coding_question_count > 0
        has_objective = assessment.total_questions > assessment.coding_question_count # Approximation
        
        # If strict "mixed" type isn't explicitly stored, infer from counts
        # (Note: total_questions includes objective questions only in some legacy logic, but usually total = obj + cod)
        # Let's trust the weights provided by the creator.
        
        obj_term = (submission.objective_percentage * w_obj)
        cod_term = (submission.coding_percentage * w_cod)
        
        # Special case: if one section doesn't exist, we might want to normalize to 100% based on the other?
        # BUT the requirement says "mixed, object-only, coding-only formulas".
        # Mixed: (obj * w_obj + cod * w_cod) / 100.
        # If obj-only: w_obj=100, w_cod=0.
        # If cod-only: w_obj=0, w_cod=100.
        # So the formula (obj% * w_obj + cod% * w_cod) / 100 works for all if weights are set correctly.
        
        final_percent = (obj_term + cod_term) / 100.0
            
        submission.score = submission.objective_score + submission.coding_score
        submission.total = submission.objective_total + submission.coding_total
        submission.percentage = round(final_percent)
        submission.final_percentage = final_percent
        
        min_pass = (inv.assessment.min_pass_percentage or 60.0)
        submission.is_qualified = submission.percentage >= min_pass
        submission.result = 'selected' if submission.is_qualified else 'rejected'
        
        submission.save(update_fields=[
            'answers', 
            'objective_score', 'objective_total', 'objective_percentage',
            'score', 'total', 'percentage', 'final_percentage', 
            'is_qualified', 'result'
        ])
        
        # Update assessment counters (best-effort)
        try:
            if created:
                assessment.submitted = int(getattr(assessment, 'submitted', 0) or 0) + 1
                assessment.evaluated = int(getattr(assessment, 'evaluated', 0) or 0) + 1
                if submission.result == 'selected':
                    assessment.shortlisted = int(getattr(assessment, 'shortlisted', 0) or 0) + 1
                assessment.save(update_fields=['submitted', 'evaluated', 'shortlisted'])
        except Exception:
            pass

        # Only mark as submitted if there are no coding questions
        # If coding questions exist, the frontend will call /coding/finalize/ next, which handles the final status.
        from api.models import AssessmentCodingQuestion
        has_coding = AssessmentCodingQuestion.objects.filter(assessment=assessment).exists()
        
        if not has_coding:
            inv.status = 'submitted'
            inv.save(update_fields=['status'])

        return Response(
            {
                'message': 'Submitted successfully.',
                'submission_id': submission.id,
                'score': submission.score,
                'total': submission.total,
                'percentage': submission.percentage,
                'result': submission.result,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in submit_invitation_answers_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while submitting: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _update_submission_scoring_logic(submission):
    """
    Recalculates coding score and updates submission fields based on stored answers.
    Doesn't save the submission object (caller should save).
    """
    inv = submission.invitation
    # Fetch all coding questions for this assessment
    from api.models import AssessmentCodingQuestion
    acqs = AssessmentCodingQuestion.objects.filter(assessment=inv.assessment)
    
    total_possible_points = 0
    candidate_total_points = 0
    
    submission_answers = submission.answers or {}
    
    difficulty_map = {
        'easy': 1,
        'medium': 2,
        'hard': 3
    }

    for acq in acqs:
        # 1. Calculate Total Possible for this question
        diff_key = (acq.difficulty or 'medium').lower()
        multiplier = difficulty_map.get(diff_key, 2)
        total_possible_points += (100 * multiplier)
        
        # 2. Calculate Candidate Score for this question
        ans_key = f"acq_{acq.id}"
        ans_data = submission_answers.get(ans_key)
        
        if ans_data:
            passed = int(ans_data.get('passed_count', 0))
            total_tests = int(ans_data.get('total_tests', 0))
            
            if total_tests > 0:
                base_score_ratio = passed / total_tests
                weighted_score = (base_score_ratio * 100) * multiplier
                candidate_total_points += weighted_score

    # 3. Final Percentage
    if total_possible_points > 0:
        coding_percentage = (candidate_total_points / total_possible_points) * 100
    else:
        coding_percentage = 0.0
    
    # 4. Update coding fields
    submission.coding_score = int(candidate_total_points)
    submission.coding_total = int(total_possible_points)
    submission.coding_percentage = coding_percentage

    # 5. Combine with Objective (if any)
    # Objective score is already stored in fields (or 0 if none)
    assessment = inv.assessment
    
    # Weighted Scoring Logic
    w_obj = assessment.weightage_objective if assessment.weightage_objective is not None else 50
    w_cod = assessment.weightage_coding if assessment.weightage_coding is not None else 50
    
    if w_obj + w_cod == 0:
        w_obj = 50
        w_cod = 50

    # Calculate final percentage using weights
    obj_term = (submission.objective_percentage * w_obj)
    cod_term = (submission.coding_percentage * w_cod)
    
    final_percentage = (obj_term + cod_term) / 100.0

    final_percentage_rounded = round(final_percentage)
    
    # 6. Update aggregate fields
    submission.score = submission.objective_score + submission.coding_score
    submission.total = submission.objective_total + submission.coding_total
    submission.percentage = final_percentage_rounded
    submission.final_percentage = final_percentage
    
    min_pass = getattr(inv.assessment, 'min_pass_percentage', 60.0) or 60.0
    submission.is_qualified = final_percentage_rounded >= min_pass
    submission.result = 'selected' if submission.is_qualified else 'rejected'


def _acq_allowed_languages(acq):
    allowed = []
    try:
        if isinstance(getattr(acq, 'allowed_languages', None), list):
            allowed = [str(v).strip().lower() for v in (acq.allowed_languages or []) if str(v).strip()]
    except Exception:
        allowed = []
    if allowed:
        return allowed
    langs = []
    try:
        if isinstance(getattr(acq, 'languages', None), list):
            langs = [str(v).strip().lower() for v in (acq.languages or []) if str(v).strip()]
    except Exception:
        langs = []
    if langs:
        return langs
    try:
        if getattr(acq.coding_question, 'language', None):
            return [str(acq.coding_question.language).strip().lower()]
    except Exception:
        pass
    return []


def _acq_merge_code(acq, user_code: str) -> str:
    """Return user code as-is for full program mode."""
    return "" if user_code is None else str(user_code)


def _evaluate_coding_question(acq, code, lang):
    """Helper to merge code, fetch test cases, and call executor for an ACQ."""
    from api.models import CodingTestCase
    exec_lang = lang or (acq.allowed_languages[0] if acq.allowed_languages else (acq.languages[0] if acq.languages else 'python3'))
    merged_code = _acq_merge_code(acq, code)

    schema_sql = None
    database_engine = None
    tcs = []
    if acq.coding_question:
        if exec_lang == 'sql':
            schema_sql = acq.coding_question.schema_sql
            database_engine = acq.coding_question.database_engine
        
        tcs_objs = CodingTestCase.objects.filter(question_id=acq.coding_question.id).order_by("id")
        for tc in tcs_objs:
            tcs.append({
                "id": tc.id,
                "stdin": tc.stdin or "",
                "expected_stdout": tc.expected_stdout or "",
            })

    result = _call_executor(
        language=exec_lang,
        source_code=merged_code,
        stdin="",
        time_limit_ms=getattr(acq, 'time_limit_ms', 3000),
        memory_mb=getattr(acq, 'memory_limit_mb', 256),
        schema_sql=schema_sql,
        database_engine=database_engine,
        testcases=tcs,
    )
    return result


def _call_executor(language: str, source_code: str, stdin: str, time_limit_ms: int, memory_mb: int, schema_sql: str = None, database_engine: str = None, testcases: list = None) -> dict:
    payload = {
        "language": language,
        "source_code": source_code,
        "stdin": stdin or "",
        "time_limit_ms": max(500, int(time_limit_ms or 3000)),
        "memory_mb": max(32, int(memory_mb or 256)),
        "schema_sql": schema_sql,
        "database_engine": database_engine,
        "testcases": testcases,
    }
    try:
        resp = requests.post(
            f"{EXECUTOR_BASE_URL}/execute",
            json=payload,
            timeout=max(5, int(payload["time_limit_ms"] / 1000) + 45),
        )
    except requests.RequestException as e:
        return {"ok": False, "error": f"Executor request failed: {str(e)}"}
    try:
        data = resp.json()
    except Exception:
        data = {"ok": False, "error": f"Non-JSON response from executor (status {resp.status_code})"}
    if resp.status_code >= 400 or not data.get("ok"):
        return {"ok": False, "error": data.get("error") or f"Executor error (status {resp.status_code})"}
    return data


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def invitation_coding_run_view(request, token):
    """
    Lightweight run for coding question inside an assessment invitation.
    Body:
    {
      "acq_id": <AssessmentCodingQuestion id>,
      "code": "...",
      "language": "python"
    }
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        acq_id = request.data.get('acq_id')
        code = request.data.get('code', '')
        lang = (request.data.get('language') or '').strip().lower()

        if not acq_id:
            return Response({'error': 'acq_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            acq = AssessmentCodingQuestion.objects.select_related('coding_question', 'assessment').get(id=int(acq_id))
        except AssessmentCodingQuestion.DoesNotExist:
            return Response({'error': 'Coding question not found.'}, status=status.HTTP_404_NOT_FOUND)

        if acq.assessment_id != inv.assessment_id:
            return Response({'error': 'Coding question does not belong to this assessment.'}, status=status.HTTP_403_FORBIDDEN)

        allowed_langs = _acq_allowed_languages(acq)
        if allowed_langs and lang and lang not in allowed_langs:
            return Response({'error': f'Language not allowed. Allowed: {", ".join(allowed_langs)}'}, status=status.HTTP_400_BAD_REQUEST)
        exec_lang = lang or (allowed_langs[0] if allowed_langs else None)
        if not exec_lang:
            return Response({'error': 'language is required.'}, status=status.HTTP_400_BAD_REQUEST)

        merged_code = _acq_merge_code(acq, code)

        # Prepare SQL specific params from the linked CodingQuestion
        schema_sql = None
        database_engine = None
        tcs = []
        
        if acq.coding_question:
            if exec_lang == 'sql':
                schema_sql = acq.coding_question.schema_sql
                database_engine = acq.coding_question.database_engine
            
            # Fetch visible test cases for validation
            tcs_objs = CodingTestCase.objects.filter(question_id=acq.coding_question.id, is_hidden=False).order_by("id")
            for tc in tcs_objs:
                tcs.append({
                    "id": tc.id,
                    "stdin": tc.stdin or "",
                    "expected_stdout": tc.expected_stdout or "",
                })

        result = _call_executor(
            language=exec_lang,
            source_code=merged_code,
            stdin="",
            time_limit_ms=getattr(acq, 'time_limit_ms', 3000),
            memory_mb=getattr(acq, 'memory_limit_mb', 256),
            schema_sql=schema_sql,
            database_engine=database_engine,
            testcases=tcs,
        )
        status_code = status.HTTP_200_OK if result.get('ok') else status.HTTP_400_BAD_REQUEST
        return Response(result, status=status_code)
    except Exception as e:
        import traceback
        print(f"Error in invitation_coding_run_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while running code: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def invitation_coding_submit_view(request, token):
    """
    Submit (final) for a coding question inside an assessment invitation.
    Currently returns executor result; persistence/scoring is not implemented.
    Body:
    {
      "acq_id": <AssessmentCodingQuestion id>,
      "code": "...",
      "language": "python"
    }
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        acq_id = request.data.get('acq_id')
        code = request.data.get('code', '')
        lang = (request.data.get('language') or '').strip().lower()

        if not acq_id:
            return Response({'error': 'acq_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            acq = AssessmentCodingQuestion.objects.select_related('coding_question', 'assessment').get(id=int(acq_id))
        except AssessmentCodingQuestion.DoesNotExist:
            return Response({'error': 'Coding question not found.'}, status=status.HTTP_404_NOT_FOUND)

        if acq.assessment_id != inv.assessment_id:
            return Response({'error': 'Coding question does not belong to this assessment.'}, status=status.HTTP_403_FORBIDDEN)

        allowed_langs = _acq_allowed_languages(acq)
        if allowed_langs and lang and lang not in allowed_langs:
            return Response({'error': f'Language not allowed. Allowed: {", ".join(allowed_langs)}'}, status=status.HTTP_400_BAD_REQUEST)
        exec_lang = lang or (allowed_langs[0] if allowed_langs else None)
        if not exec_lang:
            return Response({'error': 'language is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Use helper for evaluation
        result = _evaluate_coding_question(acq, code, lang)

        if inv.status == 'submitted':
            return Response({'error': 'Your exam has been completed.'}, status=status.HTTP_409_CONFLICT)

        # Check if this specific question was already submitted
        submission = getattr(inv, 'submission', None)
        if submission and submission.answers and f"acq_{acq.id}" in submission.answers:
             return Response({'error': 'This question has already been submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        # Persistence logic
        if result.get("ok"):
            # Create or update CandidateSubmission
            submission, created = CandidateSubmission.objects.get_or_create(
                invitation=inv,
                defaults={
                    "answers": {},
                    "score": 0,
                    "total": 0,
                    "percentage": 0,
                    "final_percentage": 0.0,
                    "is_qualified": False,
                    "result": "selected",
                },
            )
            
            # Update answers for this question
            passed_count = result.get("passed_count", 0)
            total_tests_exec = result.get("total_tests", 0)
            
            answers = submission.answers or {}
            question_key = f"acq_{acq.id}"
            answers[question_key] = {
                "acq_id": acq.id,
                "question_id": acq.coding_question_id,
                "submitted_code": code,
                "language": exec_lang,
                "passed_count": passed_count,
                "total_tests": total_tests_exec,
                "difficulty": acq.difficulty or 'medium', 
                "submitted_at": timezone.now().isoformat(),
            }
            submission.answers = answers
            
            # Recalculate score live so recruiters see progress
            _update_submission_scoring_logic(submission)
            submission.save()

            try:
                assessment = inv.assessment
                if created:
                    assessment.submitted = int(getattr(assessment, 'submitted', 0) or 0) + 1
                    assessment.evaluated = int(getattr(assessment, 'evaluated', 0) or 0) + 1
                    assessment.shortlisted = int(getattr(assessment, 'shortlisted', 0) or 0) + 1
                    assessment.save(update_fields=['submitted', 'evaluated', 'shortlisted'])
            except Exception:
                pass
            result["submission_id"] = submission.id

        status_code = status.HTTP_200_OK if result.get('ok') else status.HTTP_400_BAD_REQUEST
        return Response(result, status=status_code)
    except Exception as e:
        import traceback
        print(f"Error in invitation_coding_submit_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while submitting code: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def invitation_coding_finalize_view(request, token):
    """
    Finalize a coding-only invitation by creating a CandidateSubmission so that
    the result/rating page can be shown. Does nothing if an MCQ submission already exists.
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        # If already submitted, return success idempotently
        if inv.status in ('submitted', 'expired'):
             submission = getattr(inv, 'submission', None)
             if submission:
                 return Response({'ok': True, 'submission_id': submission.id}, status=status.HTTP_200_OK)

        # Ensure assessment has zero non-coding questions; otherwise enforce normal submit
        # Ensure assessment has zero non-coding questions; otherwise enforce normal submit
        # FIX: Allow mixed assessments (which have both). Only block if it's purely MCQ and somehow hit this endpoint?
        # Actually, if it has coding questions, we MUST allow this endpoint.
        # So we only block if has_mcq AND NOT has_coding.
        has_mcq = AssessmentQuestion.objects.filter(assessment=inv.assessment).exists()
        has_coding = AssessmentCodingQuestion.objects.filter(assessment=inv.assessment).exists()
        
        if has_mcq and not has_coding:
            return Response({'error': 'This assessment requires question answers submission.'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        try:
            end_time = getattr(inv, 'end_time', None)
            end_time = timezone.make_aware(end_time, timezone.get_current_timezone()) if end_time and timezone.is_naive(end_time) else end_time
        except Exception:
            end_time = getattr(inv, 'end_time', None)

        if inv.started_at is None:
            return Response({'error': 'Exam has not been started.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Allow 2 minutes grace period for auto-submit delays / network skew
        if inv.expires_at and now > (inv.expires_at + timedelta(minutes=2)):
            return Response({'error': 'Time is over. Submission is closed.'}, status=status.HTTP_410_GONE)
        if end_time and now >= end_time:
            return Response({'error': 'Time is over. Submission is closed.'}, status=status.HTTP_410_GONE)

        # Get or create submission (it might exist from per-question submits)
        submission, created = CandidateSubmission.objects.get_or_create(
            invitation=inv,
            defaults={
                "answers": {},
                "score": 0,
                "total": 0,
                "percentage": 0,
                "final_percentage": 0.0,
                "is_qualified": False,
                "result": "selected",
            },
        )
        
        # --- NEW: Process code_map if provided ---
        code_map = request.data.get('code_map', {})
        if code_map:
            submission_answers = submission.answers or {}
            changed = False
            for acq_id_str, info in code_map.items():
                ans_key = f"acq_{acq_id_str}"
                # If question not evaluated yet, do it now
                if ans_key not in submission_answers:
                    try:
                        acq = AssessmentCodingQuestion.objects.get(id=int(acq_id_str), assessment=inv.assessment)
                        code = info.get('code', '')
                        lang = info.get('language', '')
                        
                        # Only evaluate if code is not empty/placeholder
                        if code.strip() and not code.strip().startswith('// Your code here'):
                            print(f"[DEBUG] Evaluating ACQ {acq.id} (Lang: {lang})")
                            res = _evaluate_coding_question(acq, code, lang)
                            print(f"[DEBUG] Result for ACQ {acq.id}: {res}")

                            
                            # Always save the submission attempt, even if evaluation failed
                            submission_answers[ans_key] = {
                                "acq_id": acq.id,
                                "question_id": acq.coding_question_id,
                                "submitted_code": code,
                                "language": lang or (acq.allowed_languages[0] if acq.allowed_languages else 'python3'),
                                "passed_count": res.get("passed_count", 0) if res.get('ok') else 0,
                                "total_tests": res.get("total_tests", 0) if res.get('ok') else 0,
                                "difficulty": acq.difficulty or 'medium', 
                                "submitted_at": timezone.now().isoformat(),
                                "execution_error": res.get("error") if not res.get('ok') else None
                            }
                            changed = True
                    except Exception as e:
                        print(f"Error auto-evaluating {acq_id_str}: {str(e)}")
            
            if changed:
                submission.answers = submission_answers
                submission.save(update_fields=['answers'])

        # Use helper for scoring
        _update_submission_scoring_logic(submission)
        submission.save()

        is_qualified = submission.is_qualified

        try:
            assessment = inv.assessment
            # Increment counters only if not already counted? Evaluation logic is idempotent here largely
            assessment.submitted = int(getattr(assessment, 'submitted', 0) or 0) + 1
            assessment.evaluated = int(getattr(assessment, 'evaluated', 0) or 0) + 1
            if is_qualified:
                assessment.shortlisted = int(getattr(assessment, 'shortlisted', 0) or 0) + 1
            assessment.save(update_fields=['submitted', 'evaluated', 'shortlisted'])
        except Exception:
            pass
        
        # Mark invitation as submitted
        inv.status = 'submitted' # CodingInvite.STATUS_SUBMITTED
        inv.save(update_fields=['status'])

        return Response({'ok': True, 'submission_id': submission.id}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in invitation_coding_finalize_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while finalizing coding submission: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_invitation_result_view(request, token):
    """
    Fetch computed result for an invitation token (after submit).
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        submission = getattr(inv, 'submission', None)
        if not submission:
            return Response({'error': 'No submission found for this invitation.'}, status=status.HTTP_404_NOT_FOUND)

        a = inv.assessment
        return Response(
            {
                'invitation': {
                    'id': inv.id,
                    'name': inv.name,
                    'email': inv.email,
                    'token': str(inv.token),
                },
                'assessment': {
                    'id': a.id,
                    'name': a.name,
                    'display_name': a.display_name,
                    'total_questions': a.total_questions,
                    'total_time': a.total_time,
                },
                'result': {
                    'score': submission.score,
                    'total': submission.total,
                    'percentage': submission.percentage,
                    'final_percentage': submission.final_percentage,
                    
                    'objective_score': submission.objective_score,
                    'objective_total': submission.objective_total,
                    'objective_percentage': submission.objective_percentage,
                    
                    'coding_score': submission.coding_score,
                    'coding_total': submission.coding_total,
                    'coding_percentage': submission.coding_percentage,
                    
                    'weightage_objective': a.weightage_objective,
                    'weightage_coding': a.weightage_coding,

                    'status': submission.result,
                    'is_qualified': submission.is_qualified,
                    'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                    'rating': getattr(submission, 'rating', None),
                    'feedback': getattr(submission, 'feedback', None),
                },
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in get_invitation_result_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching result: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def results_overview_view(request):
    """
    Recruiter overview: list recent results (submissions).
    """
    try:
        qs = CandidateSubmission.objects.select_related('invitation', 'invitation__assessment').order_by('-submitted_at')

        # Date filtering
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date:
            qs = qs.filter(submitted_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(submitted_at__date__lte=end_date)
        
        # Similar logic for AI assessments — exclude ONGOING (not yet submitted)
        ai_qs = AIAssessmentSubmission.objects.select_related('assessment').exclude(status='ONGOING').order_by('-submitted_at')
        
        if start_date:
            ai_qs = ai_qs.filter(submitted_at__date__gte=start_date)
        if end_date:
            ai_qs = ai_qs.filter(submitted_at__date__lte=end_date)

        # Combine and limit
        results = []
        for s in qs[:400]:
            inv = s.invitation
            a = inv.assessment
            results.append(
                {
                    'submission_id': s.id,
                    'submitted_at': s.submitted_at.isoformat() if s.submitted_at else None,
                    'candidate': {
                        'name': inv.name,
                        'email': inv.email,
                    },
                    'assessment': {
                        'id': a.id,
                        'display_name': a.display_name,
                        'name': a.name,
                        'weightage_objective': a.weightage_objective,
                        'weightage_coding': a.weightage_coding,
                    },
                    'score': s.score,
                    'total': s.total,
                    'percentage': s.final_percentage if s.final_percentage is not None else s.percentage,
                    
                    'objective_score': s.objective_score,
                    'objective_total': s.objective_total,
                    'objective_percentage': s.objective_percentage,
                    
                    'coding_score': s.coding_score,
                    'coding_total': s.coding_total,
                    'coding_percentage': s.coding_percentage,

                    'status': s.result,
                }
            )

        # Re-sort combined results by submitted_at
        results.sort(key=lambda x: str(x['submitted_at'] or ''), reverse=True)

        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in results_overview_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching results: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CandidateSubmissionDeleteView(generics.DestroyAPIView):
    queryset = CandidateSubmission.objects.all()
    # serializer_class not strictly required for DestroyAPIView
    permission_classes = [AllowAny] # Or IsAuthenticated depending on requirements, kept open for now matching results view


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_rating_view(request, token):
    """
    Candidate submits rating/feedback after submission.
    Body: { "rating": 1-5, "feedback": "optional" }
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        submission = getattr(inv, 'submission', None)
        if not submission:
            return Response({'error': 'No submission found for this invitation.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data or {}
        rating = data.get('rating', None)
        feedback = (data.get('feedback') or '').strip() or None

        # Prevent multiple ratings for the same submission
        if submission.rating is not None:
            return Response({'error': 'Rating already submitted for this invitation.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating_int = int(rating)
        except Exception:
            return Response({'error': 'rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        if rating_int < 1 or rating_int > 5:
            return Response({'error': 'rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        submission.rating = rating_int
        submission.feedback = feedback
        submission.save(update_fields=['rating', 'feedback'])

        return Response({'message': 'Thanks for your feedback.'}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in submit_rating_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while saving rating: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def candidates_overview_view(request):
    """
    Recruiter overview: list invited candidates and their status.
    Query params:
      - assessment_id: optional
    """
    try:
        assessment_id = request.GET.get('assessment_id', None)
        qs = CandidateInvitation.objects.select_related('assessment').order_by('-created_at')

        # Date filtering
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)

        if assessment_id:
            try:
                qs = qs.filter(assessment_id=int(assessment_id))
            except Exception:
                return Response({'error': 'assessment_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = qs[:500]
        results = []
        for inv in qs:
            sub = getattr(inv, 'submission', None)
            results.append(
                {
                    'id': inv.id,
                    'name': inv.name,
                    'email': inv.email,
                    'pan_number': inv.pan_number,
                    'phone': inv.phone,
                    'status': inv.status,
                    'token': str(inv.token),
                    'created_at': inv.created_at.isoformat() if inv.created_at else None,
                    'started_at': inv.started_at.isoformat() if getattr(inv, 'started_at', None) else None,
                    'expires_at': inv.expires_at.isoformat() if getattr(inv, 'expires_at', None) else None,
                    'submitted_at': sub.submitted_at.isoformat() if sub and sub.submitted_at else None,
                    'submission_id': sub.id if sub else None,
                    'rating': getattr(sub, 'rating', None) if sub else None,
                    'score': sub.score if sub else 0,
                    'total_score': sub.total if sub else 0,
                    'final_percentage': sub.final_percentage if sub else 0,
                    'result': sub.result if sub else None,
                    'is_qualified': sub.is_qualified if sub else False,
                    'assessment': {
                        'id': inv.assessment_id,
                        'display_name': inv.assessment.display_name,
                        'name': inv.assessment.name,
                    } if inv.assessment_id else None,
                }
            )

        # Merge results from Resume Matcher (ai_candidates) if no assessment filter is applied
        if not assessment_id:
            try:
                ai_qs = Candidate.objects.all().order_by('-submission_date')
                if start_date:
                    ai_qs = ai_qs.filter(submission_date__date__gte=start_date)
                if end_date:
                    ai_qs = ai_qs.filter(submission_date__date__lte=end_date)
                
                ai_cands = ai_qs[:50]

                for cand in ai_cands:
                    results.append({
                        'id': cand.id,
                        'name': cand.full_name,
                        'email': cand.email,
                        'pan_number': None,
                        'phone': None,
                        'status': cand.status,
                        'token': None,
                        'created_at': cand.submission_date.isoformat() if cand.submission_date else None,
                        'started_at': cand.submission_date.isoformat() if cand.submission_date else None,
                        'expires_at': None,
                        'submitted_at': None,
                        'submission_id': None,
                        'rating': None,
                        'score': 0,
                        'total_score': 0,
                        'final_percentage': 0,
                        'result': None,
                        'is_qualified': False,
                        'assessment': {
                            'id': 0,
                            'display_name': cand.job_title,
                            'name': cand.job_title,
                        }
                    })
                
                # Re-sort combined results by created_at date
                def get_date(item):
                    return item.get('created_at') or ''
                results.sort(key=get_date, reverse=True)
            except Exception as e:
                print(f"Error merging ai_candidates: {e}")

        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in candidates_overview_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching candidates: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def backfill_assessment_questions_view(request):
    """
    Backfill existing AssessmentQuestion records with data from their linked Question records.
    This is useful if AssessmentQuestion records were created before the snapshot fields were added.
    
    Expected request body (JSON):
    {
        "assessment_id": 1  // Optional: backfill only this assessment, or omit to backfill all
    }
    """
    try:
        assessment_id = request.data.get('assessment_id', None)
        
        # Get AssessmentQuestion records that need backfilling
        if assessment_id:
            aq_records = AssessmentQuestion.objects.filter(
                assessment_id=assessment_id
            ).select_related('question')
        else:
            # Backfill all records with NULL question_type
            aq_records = AssessmentQuestion.objects.filter(
                question_type__isnull=True
            ).select_related('question')
        
        updated_count = 0
        for aq in aq_records:
            q = aq.question
            if not q:
                continue
            
            # Update all fields from the linked Question
            aq.question_type = getattr(q, 'question_type', '') or ''
            aq.difficulty = getattr(q, 'difficulty', '') or ''
            aq.time_limit = getattr(q, 'time_limit', None) or 120
            aq.option_a = getattr(q, 'option_a', None) or ''
            aq.option_b = getattr(q, 'option_b', None) or ''
            aq.option_c = getattr(q, 'option_c', None) or ''
            aq.option_d = getattr(q, 'option_d', None) or ''
            aq.correct_answer = getattr(q, 'correct_answer', None) or ''
            aq.correct_answers = getattr(q, 'correct_answers', None) or []
            aq.skill = getattr(q, 'topic', '') or aq.skill or ''
            
            aq.save()
            updated_count += 1
        
        return Response(
            {
                'message': f'Successfully backfilled {updated_count} AssessmentQuestion records.',
                'updated_count': updated_count,
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        print(f"Error in backfill_assessment_questions_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while backfilling: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_objective_section(request, token):
    """
    Submits and grades ONLY the objective section.
    Used for split assessments where objective performance gates the coding section.
    Does NOT mark the invitation as 'submitted' unless it fails the cutoff.
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        if inv.status == 'submitted':
            return Response({'error': 'Assessment already submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get answers: { "question_id": "A" ... }
        answers = request.data.get('answers', {})
        
        # Calculate Objective Score
        assessment = inv.assessment
        
        aq_qs = AssessmentQuestion.objects.filter(assessment=assessment)
        total_obj_questions = 0
        score = 0
        
        def _norm(v): return str(v).strip().upper() if v else ''
        
        for aq in aq_qs:
            qid_str = str(aq.id)
            if qid_str not in answers:
                total_obj_questions += 1
                continue
            
            total_obj_questions += 1
            user_val = answers[qid_str]
            
            # De-shuffle
            mapping = (inv.option_map or {}).get(qid_str)
            if mapping:
                if isinstance(user_val, list):
                   user_val = [mapping.get(x, x) for x in user_val]
                else:
                   user_val = mapping.get(user_val, user_val)
            
            # Grade
            qtype = (aq.question_type or '').strip().upper()
            if qtype == 'MSQ':
                u_list = sorted([_norm(x) for x in (user_val if isinstance(user_val, list) else [])])
                c_list = sorted([_norm(x) for x in (aq.correct_answers or [])])
                if u_list == c_list:
                    score += 1
            else:
                if _norm(user_val) == _norm(aq.correct_answer):
                    score += 1
                    
        percentage = (score / total_obj_questions * 100.0) if total_obj_questions > 0 else 0.0
        
        # Save to Submission
        submission, created = CandidateSubmission.objects.get_or_create(invitation=inv)
        submission.objective_score = score
        submission.objective_total = total_obj_questions
        submission.objective_percentage = round(percentage, 2)
        submission.answers = answers # Store current state
        submission.save()
        
        # Check Cutoff
        passed = True
        next_stage = 'coding'
        message = "Objective section completed."
        
        if assessment.has_objective_cutoff:
            cutoff = assessment.min_objective_pass_percentage
            if percentage < cutoff:
                passed = False
                message = "You did not meet the minimum requirement for the objective section."
                next_stage = 'finish'
                # Mark as submitted/failed immediately
                inv.status = 'submitted'
                inv.save()
                
                # Update final result
                submission.result = 'rejected'
                submission.is_qualified = False
                
                # Recalculate final percentage using existing logic
                _update_submission_scoring_logic(submission)
                submission.save()
            else:
                passed = True
                message = "Objective cutoff passed. Proceeding to coding section."
                next_stage = 'coding'
                # Even if passed, update scoring so partial results are correct
                _update_submission_scoring_logic(submission)
                submission.save()
        else:
            # If no cutoff, still update scoring for partial results
            _update_submission_scoring_logic(submission)
            submission.save()
        
        # Reload to get updated fields from _update_submission_scoring_logic
        submission.refresh_from_db()

        return Response({
            'success': True,
            'passed': passed,
            'score': score,
            'total': total_obj_questions,
            'percentage': percentage,
            'final_percentage': submission.final_percentage,
            'next_stage': next_stage,
            'message': message
        })

    except Exception as e:
        import traceback
        print(f"Error in submit_objective_section: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def save_candidate_details_view(request):
    """
    Save candidate details before starting the assessment.
    Expected payload:
    {
        "token": "uuid-string",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "pan_number": "ABCDE1234F",
        "pan_file": <file>,
        "snapshot": "base64-encoded-image-string"
    }
    """
    try:
        token = request.data.get('token')
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate token exists in CandidateInvitation
        try:
            invitation = CandidateInvitation.objects.get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Extract data
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        email = request.data.get('email', '').strip()
        phone = request.data.get('phone', '').strip()
        pan_number = request.data.get('pan_number', '').strip().upper()
        snapshot = request.data.get('snapshot', '').strip()
        pan_file = request.FILES.get('pan_file')

        # Validation
        if not all([first_name, last_name, email, phone, pan_number, snapshot]):
            return Response(
                {'error': 'All fields are required: first_name, last_name, email, phone, pan_number, snapshot'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate PAN format (5 letters, 4 digits, 1 letter)
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
            return Response(
                {'error': 'Invalid PAN number format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return Response(
                {'error': 'Invalid email format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate phone (10 digits)
        if not re.match(r'^[0-9]{10}$', phone):
            return Response(
                {'error': 'Invalid phone number format (must be 10 digits)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create or update candidate details
        candidate_details, created = CandidateDetails.objects.update_or_create(
            token=token,
            email=email,
            defaults={
                'invitation': invitation,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'pan_number': pan_number,
                'snapshot': snapshot,
                'pan_file': pan_file,
            }
        )

        return Response({
            'success': True,
            'message': 'Candidate details saved successfully',
            'id': candidate_details.id,
            'created': created,
            'created_at': candidate_details.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Failed to save candidate details: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def get_candidate_details_view(request, token):
    """
    Get candidate details for a given token.
    """
    try:
        candidate_details = CandidateDetails.objects.get(token=token)
        
        return Response({
            'success': True,
            'data': {
                'id': candidate_details.id,
                'first_name': candidate_details.first_name,
                'last_name': candidate_details.last_name,
                'email': candidate_details.email,
                'phone': candidate_details.phone,
                'pan_number': candidate_details.pan_number,
                'pan_file': candidate_details.pan_file.url if candidate_details.pan_file else None,
                'snapshot': candidate_details.snapshot,
                'created_at': candidate_details.created_at.isoformat(),
                'updated_at': candidate_details.updated_at.isoformat(),
            }
        }, status=status.HTTP_200_OK)

    except CandidateDetails.DoesNotExist:
        return Response(
            {'error': 'Candidate details not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve candidate details: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['POST'])
@permission_classes([AllowAny])
def create_interview_invitations_and_send_email_view(request):
    """
    Create interview invitation(s) and send email(s) immediately.
    
    This endpoint creates interview invitations without requiring an existing Interview object.
    If needed, it creates a default Interview record.

    Body:
    {
      "candidates": [
        {
          "name":"...",
          "email":"...",
          "pan_number":"...",
          "phone":"...",
          "start_time": "...iso...",
          "end_time":"...iso...",
          "time_zone":"...",
          "start_grace_minutes": 30
        },
        ...
      ],
      "interview_name": "Optional interview name" (defaults to "Interview")
    }
    """
    try:
        data = request.data or {}
        candidates = data.get('candidates', [])
        interview_name = data.get('interview_name', 'Interview').strip() or 'Interview'
        
        if not isinstance(candidates, list) or len(candidates) == 0:
            return Response({'error': 'candidates must be a non-empty array.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create a default interview (or create one per batch)
        # For simplicity, we'll create one interview per batch of invites
        interview = Interview.objects.create(
            name=interview_name,
            description=f'Interview created on {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
        )

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'https://verifyhire.duckdns.org'

        results = []
        sent_count = 0
        fail_count = 0

        for idx, c in enumerate(candidates, start=1):
            payload = dict(c or {})
            name = (payload.get('name') or '').strip()
            email = (payload.get('email') or '').strip().lower()
            pan_number = (payload.get('pan_number') or payload.get('pan') or '').strip().upper() or None
            phone = (payload.get('phone') or '').strip() or None
            start_time_raw = (payload.get('start_time') or '').strip() or None
            end_time_raw = (payload.get('end_time') or '').strip() or None
            time_zone = (payload.get('time_zone') or '').strip() or None
            start_grace_minutes_raw = payload.get('start_grace_minutes', None)

            if not name:
                return Response({'error': f'Candidate #{idx}: name is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if not email:
                return Response({'error': f'Candidate #{idx}: email is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if pan_number and not _is_valid_pan(pan_number):
                return Response({'error': f'Candidate #{idx}: pan_number is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

            start_time = parse_datetime(start_time_raw) if start_time_raw else None
            end_time = parse_datetime(end_time_raw) if end_time_raw else None
            try:
                start_grace_minutes = int(start_grace_minutes_raw) if start_grace_minutes_raw is not None else 0
            except Exception:
                start_grace_minutes = 0
            start_grace_minutes = max(0, start_grace_minutes)

            invitation = InterviewInvitation.objects.create(
                interview=interview,
                name=name,
                email=email,
                pan_number=pan_number,
                phone=phone,
                start_time=start_time,
                end_time=end_time,
                time_zone=time_zone,
                start_grace_minutes=start_grace_minutes,
                status='draft',
            )

            # Read validity mode from payload
            validity_mode = (payload.get('validity_mode') or '').strip() or 'exact_window'

            # Convert UTC times to candidate's local timezone for display
            display_tz = time_zone or ''
            local_start = start_time
            local_end = end_time
            try:
                from zoneinfo import ZoneInfo
                if time_zone and start_time:
                    local_start = start_time.astimezone(ZoneInfo(time_zone))
                if time_zone and end_time:
                    local_end = end_time.astimezone(ZoneInfo(time_zone))
            except Exception:
                pass

            interview_link = f"{frontend_base.rstrip('/')}/live-interview?token={invitation.token}"
            subject = f"Interview Invitation - {interview_name}"

            # Build schedule blocks based on validity mode
            if validity_mode == 'exact_window':
                display_date = local_start.strftime('%B %d, %Y') if local_start else ''
                display_start_time = local_start.strftime('%I:%M %p') if local_start else ''
                display_end_time = local_end.strftime('%I:%M %p') if local_end else ''

                schedule_text = ''
                if display_date:
                    schedule_text = (
                        f"Date: {display_date}\n"
                        f"Start Time: {display_start_time}\n"
                    )
                    if display_end_time:
                        schedule_text += f"End Time: {display_end_time}\n"
                    if display_tz:
                        schedule_text += f"Time Zone: {display_tz}\n"

                schedule_html = ''
                if display_date:
                    schedule_html = '<table style="border-collapse:collapse;width:100%;">'
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 Date</td>'
                        f'<td style="padding:6px 0;">{display_date}</td>'
                        '</tr>'
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 Start Time</td>'
                        f'<td style="padding:6px 0;">{display_start_time}</td>'
                        '</tr>'
                    )
                    if display_end_time:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 End Time</td>'
                            f'<td style="padding:6px 0;">{display_end_time}</td>'
                            '</tr>'
                        )
                    if display_tz:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🌐 Time Zone</td>'
                            f'<td style="padding:6px 0;">{display_tz}</td>'
                            '</tr>'
                        )
                    schedule_html += '</table>'
            else:
                display_start_date = local_start.strftime('%B %d, %Y') if local_start else ''
                display_end_date = local_end.strftime('%B %d, %Y') if local_end else ''

                schedule_text = ''
                if display_start_date:
                    schedule_text = f"Start Date: {display_start_date}\n"
                    if display_end_date and display_end_date != display_start_date:
                        schedule_text += f"End Date: {display_end_date}\n"
                    schedule_text += "Available: 12:00 AM to 11:59 PM\n"
                    if display_tz:
                        schedule_text += f"Time Zone: {display_tz}\n"

                schedule_html = ''
                if display_start_date:
                    schedule_html = '<table style="border-collapse:collapse;width:100%;">'
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 Start Date</td>'
                        f'<td style="padding:6px 0;">{display_start_date}</td>'
                        '</tr>'
                    )
                    if display_end_date and display_end_date != display_start_date:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 End Date</td>'
                            f'<td style="padding:6px 0;">{display_end_date}</td>'
                            '</tr>'
                        )
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 Available</td>'
                        '<td style="padding:6px 0;">12:00 AM to 11:59 PM</td>'
                        '</tr>'
                    )
                    if display_tz:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🌐 Time Zone</td>'
                            f'<td style="padding:6px 0;">{display_tz}</td>'
                            '</tr>'
                        )
                    schedule_html += '</table>'

            text_body = (
                f"Hi {name},\n\n"
                f"You have been invited to participate in a live interview.\n\n"
                f"Interview: {interview_name}\n"
            )
            if schedule_text:
                text_body += f"\n{schedule_text}"
            text_body += (
                f"\nJoin Interview Link: {interview_link}\n\n"
                "Please join the interview at the scheduled time.\n\n"
                "Best regards,\n"
                "VerifiHireAI Team"
            )

            html_body = f"""
                <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #111; max-width: 600px;">
                  <h2 style="color: #2563eb;">Interview Invitation</h2>
                  <p>Hi <strong>{name}</strong>,</p>
                  <p>You have been invited to participate in a live interview.</p>
                  
                  <div style="background: #f8fafc; padding: 16px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 8px 0;"><strong>Interview:</strong> {interview_name}</p>
                    {schedule_html}
                  </div>
                  
                  <p style="margin: 24px 0;">
                    <a href="{interview_link}" target="_blank"
                       style="background:#2563eb;color:#fff;padding:14px 24px;border-radius:10px;text-decoration:none;font-weight:700;display:inline-block;">
                      Join Interview
                    </a>
                  </p>
                  
                  <p style="font-size:12px;color:#475569;margin-top:24px;">
                    If the button doesn't work, copy this link:<br/>
                    <a href="{interview_link}" style="color:#2563eb;word-break:break-all;">{interview_link}</a>
                  </p>
                  
                  <p style="margin-top:24px;color:#64748b;font-size:14px;">
                    Best regards,<br/>
                    <strong>VerifiHireAI Team</strong>
                  </p>
                </div>
            """

            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    to=[email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                invitation.status = 'sent'
                invitation.last_error = None
                invitation.save(update_fields=['status', 'last_error', 'updated_at'])
                sent_count += 1
            except Exception as mail_err:
                invitation.status = 'failed'
                invitation.last_error = str(mail_err)
                invitation.save(update_fields=['status', 'last_error', 'updated_at'])
                fail_count += 1

            results.append(
                {
                    'id': invitation.id,
                    'name': invitation.name,
                    'email': invitation.email,
                    'pan_number': invitation.pan_number,
                    'phone': invitation.phone,
                    'token': str(invitation.token),
                    'status': invitation.status,
                    'interview_link': interview_link,
                    'error': invitation.last_error,
                }
            )

        return Response(
            {
                'message': 'Interview invitations processed.',
                'sent': sent_count,
                'failed': fail_count,
                'results': results,
            },
            status=status.HTTP_200_OK if fail_count == 0 else status.HTTP_207_MULTI_STATUS
        )
    except Exception as e:
        import traceback
        print(f"Error in create_interview_invitations_and_send_email_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while sending invitations: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def interview_invitations_overview_view(request):
    """
    Overview: list interview invitations and their status.
    Query params:
      - interview_id: optional filter by interview
    """
    try:
        interview_id = request.GET.get('interview_id', None)
        qs = InterviewInvitation.objects.select_related('interview').order_by('-created_at')
        if interview_id:
            try:
                qs = qs.filter(interview_id=int(interview_id))
            except Exception:
                return Response({'error': 'interview_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = qs[:500]
        results = []
        for inv in qs:
            feedback = getattr(inv, 'feedback', None)
            results.append(
                {
                    'id': inv.id,
                    'name': inv.name,
                    'email': inv.email,
                    'pan_number': inv.pan_number,
                    'phone': inv.phone,
                    'status': inv.status,
                    'token': str(inv.token),
                    'start_time': inv.start_time.isoformat() if inv.start_time else None,
                    'end_time': inv.end_time.isoformat() if inv.end_time else None,
                    'time_zone': inv.time_zone,
                    'start_grace_minutes': inv.start_grace_minutes,
                    'created_at': inv.created_at.isoformat() if inv.created_at else None,
                    'updated_at': inv.updated_at.isoformat() if inv.updated_at else None,
                    'interview': {
                        'id': inv.interview_id,
                        'name': inv.interview.name if inv.interview else None,
                        'description': inv.interview.description if inv.interview else None,
                    } if inv.interview_id else None,
                    'feedback': {
                        'interviewer_feedback': feedback.interviewer_feedback,
                        'interviewer_rating': feedback.interviewer_rating,
                        'interviewer_technical_rating': feedback.interviewer_technical_rating,
                        'interviewer_communication_rating': feedback.interviewer_communication_rating,
                        'interviewer_team_fit_rating': feedback.interviewer_team_fit_rating,
                        'interviewer_average_rating': feedback.interviewer_average_rating,
                        'candidate_feedback': feedback.candidate_feedback,
                        'candidate_rating': feedback.candidate_rating,
                        'updated_at': feedback.updated_at.isoformat() if feedback.updated_at else None,
                    } if feedback else None
                }
            )

        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in interview_invitations_overview_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching interview invitations: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_interview_invitation_by_token_view(request, token):
    """
    Get interview invitation details by token.
    """
    try:
        try:
            invitation = InterviewInvitation.objects.select_related('interview').get(token=token)
        except InterviewInvitation.DoesNotExist:
            return Response({'error': 'Interview invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'id': invitation.id,
            'name': invitation.name,
            'email': invitation.email,
            'pan_number': invitation.pan_number,
            'phone': invitation.phone,
            'status': invitation.status,
            'token': str(invitation.token),
            'start_time': invitation.start_time.isoformat() if invitation.start_time else None,
            'end_time': invitation.end_time.isoformat() if invitation.end_time else None,
            'time_zone': invitation.time_zone,
            'start_grace_minutes': invitation.start_grace_minutes,
            'created_at': invitation.created_at.isoformat() if invitation.created_at else None,
            'interview': {
                'id': invitation.interview_id,
                'name': invitation.interview.name if invitation.interview else None,
                'description': invitation.interview.description if invitation.interview else None,
            } if invitation.interview_id else None,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in get_interview_invitation_by_token_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_rating_view(request, token):
    """
    Candidate submits rating/feedback after submission.
    Body: { "rating": 1-5, "feedback": "optional" }
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        submission = getattr(inv, 'submission', None)
        if not submission:
            return Response({'error': 'No submission found for this invitation.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data or {}
        rating = data.get('rating', None)
        feedback = (data.get('feedback') or '').strip() or None

        # Prevent multiple ratings for the same submission
        if submission.rating is not None:
            return Response({'error': 'Rating already submitted for this invitation.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating_int = int(rating)
        except Exception:
            return Response({'error': 'rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        if rating_int < 1 or rating_int > 5:
            return Response({'error': 'rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        submission.rating = rating_int
        submission.feedback = feedback
        submission.save(update_fields=['rating', 'feedback'])

        return Response({'message': 'Thanks for your feedback.'}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in submit_rating_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while saving rating: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def backfill_assessment_questions_view(request):
    """
    Backfill existing AssessmentQuestion records with data from their linked Question records.
    This is useful if AssessmentQuestion records were created before the snapshot fields were added.
    
    Expected request body (JSON):
    {
        "assessment_id": 1  // Optional: backfill only this assessment, or omit to backfill all
    }
    """
    try:
        assessment_id = request.data.get('assessment_id', None)
        
        # Get AssessmentQuestion records that need backfilling
        if assessment_id:
            aq_records = AssessmentQuestion.objects.filter(
                assessment_id=assessment_id
            ).select_related('question')
        else:
            # Backfill all records with NULL question_type
            aq_records = AssessmentQuestion.objects.filter(
                question_type__isnull=True
            ).select_related('question')
        
        updated_count = 0
        for aq in aq_records:
            q = aq.question
            if not q:
                continue
            
            # Update all fields from the linked Question
            aq.question_type = getattr(q, 'question_type', '') or ''
            aq.difficulty = getattr(q, 'difficulty', '') or ''
            aq.time_limit = getattr(q, 'time_limit', None) or 120
            aq.option_a = getattr(q, 'option_a', None) or ''
            aq.option_b = getattr(q, 'option_b', None) or ''
            aq.option_c = getattr(q, 'option_c', None) or ''
            aq.option_d = getattr(q, 'option_d', None) or ''
            aq.correct_answer = getattr(q, 'correct_answer', None) or ''
            aq.correct_answers = getattr(q, 'correct_answers', None) or []
            aq.skill = getattr(q, 'topic', '') or aq.skill or ''
            
            aq.save()
            updated_count += 1
        
        return Response(
            {
                'message': f'Successfully backfilled {updated_count} AssessmentQuestion records.',
                'updated_count': updated_count,
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        print(f"Error in backfill_assessment_questions_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while backfilling: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def save_candidate_details_view(request):
    """
    Save candidate details before starting the assessment.
    Expected payload:
    {
        "token": "uuid-string",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "pan_number": "ABCDE1234F",
        "pan_file": <file>,
        "snapshot": "base64-encoded-image-string"
    }
    """
    try:
        token = request.data.get('token')
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate token exists in CandidateInvitation
        try:
            invitation = CandidateInvitation.objects.get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Extract data
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        email = request.data.get('email', '').strip()
        phone = request.data.get('phone', '').strip()
        pan_number = request.data.get('pan_number', '').strip().upper()
        snapshot = request.data.get('snapshot', '').strip()
        pan_file = request.FILES.get('pan_file')

        # Validation
        if not all([first_name, last_name, email, phone, pan_number, snapshot]):
            return Response(
                {'error': 'All fields are required: first_name, last_name, email, phone, pan_number, snapshot'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate PAN format (5 letters, 4 digits, 1 letter)
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
            return Response(
                {'error': 'Invalid PAN number format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return Response(
                {'error': 'Invalid email format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate phone (10 digits)
        if not re.match(r'^[0-9]{10}$', phone):
            return Response(
                {'error': 'Invalid phone number format (must be 10 digits)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create or update candidate details
        candidate_details, created = CandidateDetails.objects.update_or_create(
            token=token,
            email=email,
            defaults={
                'invitation': invitation,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'pan_number': pan_number,
                'snapshot': snapshot,
                'pan_file': pan_file,
            }
        )

        return Response({
            'success': True,
            'message': 'Candidate details saved successfully',
            'id': candidate_details.id,
            'created': created,
            'created_at': candidate_details.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Failed to save candidate details: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def get_candidate_details_view(request, token):
    """
    Get candidate details for a given token.
    """
    try:
        candidate_details = CandidateDetails.objects.get(token=token)
        
        return Response({
            'success': True,
            'data': {
                'id': candidate_details.id,
                'first_name': candidate_details.first_name,
                'last_name': candidate_details.last_name,
                'email': candidate_details.email,
                'phone': candidate_details.phone,
                'pan_number': candidate_details.pan_number,
                'pan_file': candidate_details.pan_file.url if candidate_details.pan_file else None,
                'snapshot': candidate_details.snapshot,
                'created_at': candidate_details.created_at.isoformat(),
                'updated_at': candidate_details.updated_at.isoformat(),
            }
        }, status=status.HTTP_200_OK)

    except CandidateDetails.DoesNotExist:
        return Response(
            {'error': 'Candidate details not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve candidate details: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_pan_backend_view(request):
    """
    Verify PAN number against uploaded image using backend OCR (pytesseract).
    Expected request body:
    - pan_number: string
    - pan_file: file (image)
    """
    try:
        data = request.data
        pan_number = data.get('pan_number', '').strip().upper()
        # Handle file upload properly
        pan_file = request.FILES.get('pan_file')

        if not pan_number:
            return Response({'error': 'PAN number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not pan_file:
            return Response({'error': 'PAN file is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Basic validation of PAN format
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
             return Response({'error': 'Invalid PAN number format'}, status=status.HTTP_400_BAD_REQUEST)

        # Check file type
        if not pan_file.content_type.startswith('image/'):
            return Response({'error': 'File must be an image for OCR verification'}, status=status.HTTP_400_BAD_REQUEST)

        # Perform OCR
        extracted_text, success = extract_text_from_image(pan_file)

        # Clean extracted text for comparison
        clean_extracted = re.sub(r'[^A-Z0-9]', '', extracted_text.upper())

        if success:
             # Strict check: Extracted PAN must match Input PAN
             extracted_clean = extracted_text.replace(" ", "").upper()
             if pan_number == extracted_clean:
                 return Response({
                    'success': True, 
                    'verified': True, 
                    'message': 'PAN verification successful',
                    'extracted_pan': extracted_text
                }, status=status.HTTP_200_OK)

        # Fallback: Check if input PAN exists anywhere in the full extracted text (fuzzy match)
        if pan_number in clean_extracted:
             return Response({
                'success': True, 
                'verified': True, 
                'message': 'PAN verified (fuzzy match)',
                'extracted_pan': pan_number
            }, status=status.HTTP_200_OK)

        return Response({
            'success': True, 
            'verified': False, 
            'message': 'PAN verification failed. Extracted text did not match.',
            'debug_info': clean_extracted[:100]
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Backend PAN Verification Error: {e}")
        return Response({
            'error': f'Verification processing failed: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def download_candidate_report_view(request, submission_id: int):
    """
    Download a comprehensive PDF report for a candidate submission.
    Includes: personal info, results, PAN card, objective answers, coding answers.
    """
    try:
        response = generate_candidate_report(submission_id)
        if response is None:
            return Response(
                {'error': 'Submission not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return response
    except Exception as e:
        import traceback
        print(f"Error in download_candidate_report_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'Failed to generate report: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_interview_feedback(request):
    """
    Submit feedback after a live interview.
    Handles both candidate and interviewer feedback.
    payload: {
        "token": "uuid",
        "feedback": "text",
        "rating": int (1-5),
        "role": "interviewer" | "candidate" (optional, default candidate)
    }
    """
    import uuid
    print(f"DEBUG: submit_interview_feedback called. Data: {request.data}")
    
    token = request.data.get('token')
    feedback_text = request.data.get('feedback')
    rating = request.data.get('rating')  # Legacy/Overall
    tech_rating = request.data.get('technical_rating')
    comm_rating = request.data.get('communication_rating')
    fit_rating = request.data.get('team_fit_rating')
    role = request.data.get('role', 'candidate')

    if not token or not feedback_text:
        return Response({'error': 'Token and feedback are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate UUID
        try:
            uuid_token = uuid.UUID(str(token))
        except ValueError:
             print(f"DEBUG: Invalid token format: {token}")
             return Response({'error': 'Invalid token format.'}, status=status.HTTP_400_BAD_REQUEST)

        # Try finding invitation by token
        invitation = InterviewInvitation.objects.filter(token=uuid_token).first()
        
        if not invitation:
            print(f"DEBUG: No invitation found for token: {token}")
            return Response({'error': 'Invalid token.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if feedback object exists
        from .models import LiveInterviewFeedback
        feedback_obj, created = LiveInterviewFeedback.objects.get_or_create(invitation=invitation)
        print(f"DEBUG: Feedback object {'created' if created else 'found'}: {feedback_obj}")

        if role == 'interviewer':
            feedback_obj.interviewer_feedback = feedback_text
            
            # Save individual ratings
            try:
                if rating: feedback_obj.interviewer_rating = int(rating)
                if tech_rating: feedback_obj.interviewer_technical_rating = int(tech_rating)
                if comm_rating: feedback_obj.interviewer_communication_rating = int(comm_rating)
                if fit_rating: feedback_obj.interviewer_team_fit_rating = int(fit_rating)
                
                # Calculate average if all three are present
                ratings_list = []
                if tech_rating: ratings_list.append(int(tech_rating))
                if comm_rating: ratings_list.append(int(comm_rating))
                if fit_rating: ratings_list.append(int(fit_rating))
                
                if ratings_list:
                    feedback_obj.interviewer_average_rating = sum(ratings_list) / len(ratings_list)
            except (ValueError, TypeError):
                pass
        else:
            # Default to candidate
            feedback_obj.candidate_feedback = feedback_text
            if rating:
                try:
                    feedback_obj.candidate_rating = int(rating)
                except ValueError:
                    pass
        
        feedback_obj.save()
        print(f"DEBUG: Feedback saved successfully for role: {role}")

        # Mark the invitation as completed when the interviewer submits feedback
        if role == 'interviewer':
            invitation.status = 'completed'
            invitation.save(update_fields=['status', 'updated_at'])
            print(f"DEBUG: Invitation {invitation.id} status updated to 'completed'")

        return Response({'success': True, 'message': 'Feedback submitted successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error submitting feedback: {e}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
