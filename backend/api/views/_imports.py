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
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db import models, close_old_connections
from django.db.utils import OperationalError
from django.core.mail import EmailMultiAlternatives
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
)
from ..ocr_utils import extract_text_from_image
from ..report_utils import generate_candidate_report

import re
import os
import random
import json
import io
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
        'gmail.com', 'googlemail.com', 'yahoo.com', 'yahoo.in',
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
