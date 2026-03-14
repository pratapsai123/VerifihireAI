# Shared imports and utility functions used across all view modules.
# Every views/*.py file should import from here using:
#   from ._imports import *

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db import models, close_old_connections
from django.db.utils import OperationalError
from django.core.mail import EmailMultiAlternatives
from django.core.files.base import ContentFile
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from ai_candidates.models import Candidate
from ai_assessments.models import AIAssessmentSubmission

from ..models import (
    UserProfile,
    EmailOTP,
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
    JobRole,
    CandidateIntegrity,
    IntegrityScreenshot,
    DeletionRequest,
)
from ..ocr_utils import extract_text_from_image
from ..report_utils import generate_candidate_report

import re
import os
import random
import json
import io
import base64
import PyPDF2
import requests
from docx import Document
from typing import Optional
from datetime import timedelta

EXECUTOR_BASE_URL = os.environ.get("EXECUTOR_BASE_URL", "http://localhost:4000").rstrip("/")


# ---------------------------------------------------------------------------
# Shared utility functions
# ---------------------------------------------------------------------------

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


def _free_email_domains() -> set:
    default = {
        'gmail.com', 'googlemail.com',
        'yahoo.com', 'yahoo.in',
        'outlook.com', 'hotmail.com', 'live.com', 'icloud.com',
        'aol.com', 'proton.me', 'protonmail.com', 'zoho.com',
    }
    configured = getattr(settings, 'FREE_EMAIL_DOMAINS', None)
    if not configured:
        return default
    try:
        return {d.strip().lower() for d in configured if str(d).strip()}
    except Exception:
        return default


def _generate_temp_password(length: int = 12) -> str:
    length = max(10, int(length))
    rng = random.SystemRandom()
    lowers = "abcdefghjkmnpqrstuvwxyz"
    uppers = lowers.upper()
    digits = "23456789"
    specials = "!@#$%^&*_-+"
    required = [rng.choice(lowers), rng.choice(uppers), rng.choice(digits), rng.choice(specials)]
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
    """Best-effort retry wrapper for flaky DB connections."""
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
    raise last_err


# ---------------------------------------------------------------------------
# Hierarchical RBAC scope helper
# ---------------------------------------------------------------------------

def get_scoped_user_ids(user_profile) -> list:
    """
    Returns a list of UserProfile IDs that `user_profile` is allowed to
    query data for, based on the reporting hierarchy:

      - application_admin : all users across all companies (returns None)
      - company_admin     : self + all HR Managers where manager=self 
                            + all HRs where manager is one of those HRMs
      - hr_manager        : self + all HR users where manager=self
      - hr                : self only
      - (anything else)   : self only (safe fallback)

    Uses the 'manager' field for stable hierarchy.
    """
    if user_profile is None:
        return []

    role = (user_profile.role or '').strip().lower()

    if role == UserProfile.ROLE_APPLICATION_ADMIN:
        return None  

    if role == UserProfile.ROLE_HR:
        return [user_profile.id]

    if role == UserProfile.ROLE_HR_MANAGER:
        reporting_hr_ids = list(
            UserProfile.objects.filter(
                manager=user_profile,
                role=UserProfile.ROLE_HR
            ).values_list('id', flat=True)
        )
        return [user_profile.id] + reporting_hr_ids

    if role == UserProfile.ROLE_COMPANY_ADMIN:
        hrm_ids = list(
            UserProfile.objects.filter(
                manager=user_profile,
                role=UserProfile.ROLE_HR_MANAGER,
            ).values_list('id', flat=True)
        )
        hr_ids = list(
            UserProfile.objects.filter(
                manager_id__in=hrm_ids,
                role=UserProfile.ROLE_HR,
            ).values_list('id', flat=True)
        ) if hrm_ids else []
        
        direct_hr_ids = list(
            UserProfile.objects.filter(
                manager=user_profile,
                role=UserProfile.ROLE_HR,
            ).values_list('id', flat=True)
        )

        return [user_profile.id] + hrm_ids + hr_ids + direct_hr_ids

    return [user_profile.id]


# ---------------------------------------------------------------------------
# Deletion Workflow Helper
# ---------------------------------------------------------------------------

def notify_approver_deletion_request(req):
    """
    Sends an email alert to the approver when a new deletion request is filed.
    """
    if not req.approver or not req.approver.email:
        return

    subject = f"Action Required: Deletion Request from {req.requester.first_name}"
    message = (
        f"Hello {req.approver.first_name},\n\n"
        f"A new deletion request has been submitted and requires your approval.\n\n"
        f"Requester: {req.requester.first_name} {req.requester.last_name} ({req.requester.role.replace('_', ' ').title()})\n"
        f"Item to Delete: {req.object_repr}\n"
        f"Type: {req.content_type}\n"
        f"Reason: {req.reason}\n\n"
        f"Please log in to the VerifiHire portal to Approve or Reject this request.\n\n"
        f"Regards,\n"
        f"VerifiHire System"
    )
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[req.approver.email],
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send deletion alert email: {e}")


def handle_deletion_request(user_profile, company, content_type, object_id, object_repr, reason):
    """
    Standardizes the logic for blocking direct deletion and creating DeletionRequest.
    Follows hierarchy rules.
    """
    is_app_admin = _is_application_admin_email(user_profile.email)
    role = user_profile.role

    if is_app_admin:
        return None, False

    if role == UserProfile.ROLE_COMPANY_ADMIN:
        req = DeletionRequest.objects.create(
            requester=user_profile,
            approver=user_profile,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            reason=reason or 'Internal Admin Cleanup',
            status=DeletionRequest.STATUS_APPROVED,
            actioned_at=timezone.now()
        )
        from .workflow_views import _perform_actual_deletion
        _perform_actual_deletion(req)
        return Response({'message': f'{content_type} deleted successfully (Audit logged).'}, status=status.HTTP_200_OK), True

    if role in {UserProfile.ROLE_HR_MANAGER, UserProfile.ROLE_HR}:
        if role == UserProfile.ROLE_HR:
            allowed_approver_roles = {UserProfile.ROLE_HR_MANAGER, UserProfile.ROLE_COMPANY_ADMIN}
        else:
            allowed_approver_roles = {UserProfile.ROLE_COMPANY_ADMIN}

        # Reporting hierarchy check
        approver = user_profile.manager
        if not approver or approver.company != company or approver.role not in allowed_approver_roles:
            approver = UserProfile.objects.filter(
                company=company, 
                role__in=allowed_approver_roles
            ).exclude(id=user_profile.id).first()

        if not approver:
            return Response({
                'error': f'No suitable {", ".join(allowed_approver_roles).replace("_", " ")} found in your company to approve this deletion request.'
            }, status=status.HTTP_400_BAD_REQUEST), True

        exists = DeletionRequest.objects.filter(
            requester=user_profile,
            content_type=content_type,
            object_id=object_id,
            status=DeletionRequest.STATUS_PENDING
        ).exists()
        
        if exists:
            return Response({'message': 'A deletion request for this item is already pending approval.'}, status=status.HTTP_200_OK), True
        
        req = DeletionRequest.objects.create(
            requester=user_profile,
            approver=approver,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            reason=reason or 'Administrative Cleanup',
            status=DeletionRequest.STATUS_PENDING
        )
        notify_approver_deletion_request(req)
        return Response({
            'message': f'A deletion request for "{object_repr}" has been sent to your {approver.role.replace("_", " ")} for approval.'
        }, status=status.HTTP_201_CREATED), True

    return None, False
