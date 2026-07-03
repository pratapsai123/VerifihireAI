import io

import PyPDF2

import fitz  # PyMuPDF

from ai_assessments.llm_client import create_llm_client, LLMKeyManager, get_default_model

import os

import json

import numpy as np

from PIL import Image

from datetime import datetime, timedelta

from django.utils import timezone
from django.db import IntegrityError

from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import status, generics

from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Candidate, InterviewIntegrity, InterviewIntegrityLog, PipelineLog
from .utils import clean_repetitive_text
from .serializers import CandidateSerializer, PipelineLogSerializer

from django.utils.dateparse import parse_datetime

from django.utils import timezone

import time

import re

import logging

import uuid
from api.utils.batch_utils import generate_batch_id, generate_batch_name
import requests
from api.ocr_utils import _get_reader
from django.conf import settings
from django.core.mail import send_mail
import pandas as pd

# Setup Logger
logger = logging.getLogger(__name__)
MAX_CODING_TASKS = 50
TOTAL_INTERVIEW_QUESTIONS = 14
from api.views.job_role_views import ensure_role_exists

from api.models import UserProfile

from api._imports import _is_application_admin_email, handle_deletion_request



import uuid

from .tasks import process_resume_batch_task

# Import extract_json if needed or just keep local one if already there. 

# Looking at views.py it is usually defined at top.

# LLM client is now created via create_llm_client() from llm_client.py



def extract_json(text):

    if not text:

        return None

        

    def _unwrap_payload(data):

        # If it's a dict and doesn't have the expected keys at root, but has a nested dict that DOES

        if isinstance(data, dict):

            if 'mcqs' not in data and 'coding_challenges' not in data:

                # Look for a single nested wrapper dict

                for key, val in data.items():

                    if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):

                        return val

        return data



    def _clean_json_str(s):

        # 1. Remove trailing commas in lists/objects before ] or }

        s = re.sub(r',\s*([\]\}])', r'\1', s)

        

        # 2. Fix truncation: count braces and append missing ones

        open_b = s.count('{')

        close_b = s.count('}')

        if open_b > close_b:

            s += '}' * (open_b - close_b)

            

        open_sq = s.count('[')

        close_sq = s.count(']')

        if open_sq > close_sq:

            s += ']' * (open_sq - close_sq)

            

        return s



    try:

        # Priority 1: Markdown code block

        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)

        if match:

            json_str = _clean_json_str(match.group(1))

            return _unwrap_payload(json.loads(json_str, strict=False))

        

        # Priority 2: Bare braces

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:

            json_str = _clean_json_str(match.group(0))

            return _unwrap_payload(json.loads(json_str, strict=False))

        

        # Priority 3: Raw string

        json_str = _clean_json_str(text.strip())

        return _unwrap_payload(json.loads(json_str, strict=False))

    except Exception as e:

        logger.error(f"JSON Extraction Failed: {e}")

        # Final fallback: just return None

        return None



class AssemblyAITokenView(APIView):
    """
    Returns a short-lived session identifier for AssemblyAI WebSocket connection.
    Requires a valid candidate token to prevent abuse.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        # Require a candidate token to prevent unauthenticated abuse
        candidate_token = request.query_params.get('token') or request.query_params.get('candidate_token')
        if not candidate_token:
            return Response({'error': 'candidate token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate the token belongs to an active candidate
        try:
            _resolve_public_candidate(candidate_token)
        except Candidate.DoesNotExist:
            return Response({'error': 'Invalid candidate token'}, status=status.HTTP_403_FORBIDDEN)

        api_key = getattr(settings, 'ASSEMBLYAI_API_KEY', None)
        if not api_key:
            return Response({'error': 'ASSEMBLYAI_API_KEY is missing from configuration.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the key (AssemblyAI v3 WebSocket accepts it directly as token param)
        return Response({'token': api_key})



class BulkInviteView(APIView):

    from rest_framework.permissions import IsAuthenticated

    permission_classes = [IsAuthenticated]



    def post(self, request):

        file = request.FILES.get('file')

        job_description = request.data.get('job_description')

        available_from = request.data.get('available_from')

        available_until = request.data.get('available_until')

        

        # Parse ISO strings into datetime objects

        if isinstance(available_from, str) and available_from:

            available_from = parse_datetime(available_from)

        if isinstance(available_until, str) and available_until:

            available_until = parse_datetime(available_until)

            

        batch_interview_time = request.data.get('interview_time') # Keep for legacy/compat

        experience_level = request.data.get('experience_level', '').strip() or None

        interview_pass_threshold = request.data.get('interview_pass_threshold', 50)
        interview_duration_minutes = request.data.get('interview_duration_minutes', 60)

        try:

            interview_pass_threshold = int(interview_pass_threshold)

        except:

            interview_pass_threshold = 50

        try:
            interview_duration_minutes = int(interview_duration_minutes)
        except:
            interview_duration_minutes = 60



        

        if not file or not job_description:
            return Response({"error": "File and Job Description are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not experience_level:
            return Response({"error": "Experience level is required"}, status=status.HTTP_400_BAD_REQUEST)

            

        try:

            batch_id = generate_batch_id()

            job_title_for_batch = request.data.get('job_title') or request.data.get('role_title') or "Interview"

            batch_name = generate_batch_name(job_title_for_batch)

            

            logger.info(f"Processing bulk invite file: {file.name}, Batch Time: {batch_interview_time}")

            if file.name.lower().endswith('.csv'):

                df = pd.read_csv(file)

            elif file.name.lower().endswith(('.xls', '.xlsx')):

                df = pd.read_excel(file)

            else:

                return Response({"error": "Unsupported file format. Use CSV or Excel."}, status=status.HTTP_400_BAD_REQUEST)

            

            df.columns = df.columns.str.lower().str.strip()

            logger.info(f"File columns: {list(df.columns)}")

            

            required_cols = ['name', 'email']

            if not all(col in df.columns for col in required_cols):

                return Response({"error": f"File must contain columns: {', '.join(required_cols)}. Found: {', '.join(df.columns)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate date ordering: available_until must be after available_from
            if available_from and available_until and available_until <= available_from:
                return Response({"error": "Available Until must be after Available From."}, status=status.HTTP_400_BAD_REQUEST)

            # Deduplicate emails within the uploaded file
            df['email'] = df['email'].str.strip().str.lower()
            df = df.drop_duplicates(subset='email', keep='first')

            # Deduplicate: within this CSV AND within this batch
            # (prevents same email twice in CSV, and also re-adding someone already in this batch)
            seen_emails_in_csv = set()
            existing_in_batch = set(
                Candidate.objects.filter(
                    batch_id=batch_id,
                    email__in=df['email'].tolist(),
                    is_deleted=False,
                ).values_list('email', flat=True)
            )

            skipped_duplicates = []

            invited_candidates = []

            

            for _, row in df.iterrows():

                name = str(row['name']).strip()

                email = str(row['email']).strip().lower()

                # Skip if duplicate within this CSV or already in this batch
                if email in seen_emails_in_csv or email in existing_in_batch:
                    skipped_duplicates.append(email)
                    continue
                seen_emails_in_csv.add(email)

                # Auto-persist role if title is provided

                job_title = request.data.get('job_title') or request.data.get('role_title')

                if job_title:

                    ensure_role_exists(job_title, job_description, user=request.user)



                user_profile = getattr(request.user, 'profile', None)

                company = user_profile.company if user_profile else None



                candidate = Candidate.objects.create(

                    full_name=name,

                    email=email,

                    job_title=job_title or "Applicant",

                    interview_time=batch_interview_time,

                    available_from=available_from if available_from else None,

                    available_until=available_until if available_until else None,

                    job_description=job_description,

                    experience_level=experience_level,

                    status='Invited',

                    company=company,

                    user_profile=user_profile,

                    created_by=user_profile,

                    batch_id=batch_id,

                    batch_name=batch_name,

                    interview_pass_threshold=interview_pass_threshold,

                    automation_settings={'interview_duration_minutes': interview_duration_minutes},

                )

                frontend_base = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')

                link = f"{frontend_base}/interview-start/{candidate.public_token}"

                

                # Format time info for email

                time_range_info = ""

                if candidate.available_from and candidate.available_until:

                    try:

                        # Ensure we convert to local time safely even if naive (though should be aware)

                        start_dt = candidate.available_from

                        end_dt = candidate.available_until

                        

                        if timezone.is_naive(start_dt):

                            start_dt = timezone.make_aware(start_dt)

                        if timezone.is_naive(end_dt):

                            end_dt = timezone.make_aware(end_dt)

                            

                        from_local = start_dt.astimezone(timezone.get_current_timezone())

                        until_local = end_dt.astimezone(timezone.get_current_timezone())

                        time_range_info = f"\n\nYour interview window is from {from_local.strftime('%d %b %Y, %I:%M %p')} to {until_local.strftime('%d %b %Y, %I:%M %p')}."

                    except Exception as tz_err:

                        logger.warning(f"Timezone conversion failed for candidate {candidate.id}: {tz_err}")

                        time_range_info = f"\n\nYour interview is scheduled for {batch_interview_time}." if batch_interview_time else ""

                elif batch_interview_time:

                    time_range_info = f"\n\nYour interview is scheduled for {batch_interview_time}."



                invited_candidates.append({

                    "id": candidate.id, "name": name, "email": email, "link": link, "time": batch_interview_time

                })

                

                try:
                    logger.info(f"=== STARTING EMAIL SEND for {email} ===")
                    subject = "Invite to VerifiHireAI Interview Session"

                    

                    # Format availability dates for email (converted to local time)

                    from_str = "Immediately"

                    if candidate.available_from:

                        local_from = timezone.localtime(candidate.available_from)

                        from_str = local_from.strftime('%B %d, %Y at %I:%M %p')

                        

                    until_str = "No fixed deadline"

                    if candidate.available_until:

                        local_until = timezone.localtime(candidate.available_until)

                        until_str = local_until.strftime('%B %d, %Y at %I:%M %p')

                    

                    time_info = f"\n\nYour interview is scheduled to start at {batch_interview_time}." if batch_interview_time else ""

                    message = f"Dear {name},\n\nYou have been invited to complete an AI-powered video interview.{time_info}\n\nTiming Details:\n- Available From: {from_str}\n- Available Until: {until_str}\n\nPlease click the link below to verify your details and start your session:\n{link}"

                    

                    html_message = f"""

                    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">

                        <div style="background-color: #6366F1; padding: 24px; text-align: center;">

                            <h1 style="color: white; margin: 0; font-size: 24px;">Interview Invitation</h1>

                        </div>

                        <div style="padding: 32px; background-color: white;">

                            <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{name}</strong>,</p>

                            <p style="line-height: 1.6; margin-bottom: 24px;">You have been invited to attempt an AI-powered video interview session.</p>

                            

                            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">

                                <h3 style="margin-top: 0; color: #6366F1; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>

                                <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {from_str}</p>

                                <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {until_str}</p>

                                {f'<p style="margin: 8px 0; font-size: 14px;"><strong>⏱️ Scheduled Time:</strong> {batch_interview_time}</p>' if batch_interview_time else ''}

                            </div>

                            

                            <div style="text-align: center; margin: 32px 0;">

                                <a href="{link}" style="background-color: #6366F1; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2);">Start Interview Session</a>

                            </div>

                            

                            <p style="font-size: 13px; color: #64748b; margin-top: 32px; border-top: 1px solid #f1f5f9; padding-top: 16px;">If the button above doesn't work, copy and paste this link into your browser:<br/>

                            <a href="{link}" style="color: #6366F1;">{link}</a></p>

                        </div>

                        <div style="background-color: #f1f5f9; padding: 16px; text-align: center; font-size: 12px; color: #94a3b8;">

                            &copy; 2026 VerifiHireAI. All rights reserved.

                        </div>

                    </div>

                    """

                    
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False, html_message=html_message)
                    logger.info(f"=== EMAIL SENT SUCCESSFULLY to {email} ===")
                except Exception as mail_error:
                    import traceback
                    error_msg = f"Failed to send email to {email}: {str(mail_error)}"

                    logger.error(error_msg)
                    logger.error(f"SMTP Error Details: {traceback.format_exc()}")
                    logger.error(f"Email Settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, TLS={settings.EMAIL_USE_TLS}, USER={settings.EMAIL_HOST_USER}")
                    # Temporary file logging for debugging

                    with open('email_errors.log', 'a') as f:

                        f.write(f"{timezone.now()} - {error_msg}\n")
                        f.write(f"{timezone.now()} - SMTP Settings: {settings.EMAIL_HOST}:{settings.EMAIL_PORT} (TLS:{settings.EMAIL_USE_TLS})\n")
                        f.write(f"{timezone.now()} - Traceback: {traceback.format_exc()}\n\n")
                

            msg = f"Successfully invited {len(invited_candidates)} {'candidate' if len(invited_candidates) == 1 else 'candidates'}."
            if skipped_duplicates:
                msg += f" Skipped {len(skipped_duplicates)} duplicate(s) already having active interviews."

            return Response({
                "message": msg,
                "candidates": invited_candidates,
                "skipped_duplicates": skipped_duplicates,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:

            logger.error(f"Error in BulkInviteView: {str(e)}", exc_info=True)

            return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ResumeMatchView(APIView):

    from rest_framework.permissions import AllowAny

    permission_classes = [AllowAny]



    def post(self, request):

        resume_files = request.FILES.getlist('resume')

        candidate_id = request.data.get('candidate_id')

        

        # 🔒 SECURITY LOCK: Only allow unauthenticated access for individual candidate interview starts.

        # Bulk uploads MUST be authenticated to ensure proper ownership.

        if not candidate_id and not request.user.is_authenticated:

            return Response({"error": "Authentication required for bulk upload operations."}, status=status.HTTP_401_UNAUTHORIZED)



        job_description = request.data.get('job_description')
        experience_level = request.data.get('experience_level', '').strip() or None
        
        # NOTE: experience_level is only required for the bulk upload flow.
        # For single-candidate start (candidate_id provided) it is optional.

        threshold = request.data.get('threshold', 70)

        # Date Validations for Fully Automated Page
        from dateutil import parser
        from django.utils import timezone
        import datetime
        
        now = timezone.now()
        def validate_date_pair(from_str, until_str, prefix):
            if from_str and until_str:
                try:
                    av_from = parser.isoparse(from_str)
                    av_until = parser.isoparse(until_str)
                    if av_from < now - datetime.timedelta(minutes=5):
                        return f"{prefix} 'Available From' timing cannot be in the past."
                    if av_until <= av_from:
                        return f"{prefix} 'Available Until' must be strictly after 'Available From'."
                except Exception:
                    return f"Invalid Date Format for {prefix}."
            return None

        # Validate both sets of dates
        err = validate_date_pair(request.data.get('assessment_available_from'), request.data.get('assessment_available_until'), "Assessment")
        if err:
            return Response({"error": "Invalid Timing", "message": err}, status=status.HTTP_400_BAD_REQUEST)
            
        err = validate_date_pair(request.data.get('interview_available_from'), request.data.get('interview_available_until'), "Interview")
        if err:
            return Response({"error": "Invalid Timing", "message": err}, status=status.HTTP_400_BAD_REQUEST)

        # Validate MCQ / Coding Counts
        try:
            mcq_count = int(request.data.get('mcq_count', 10))
            coding_count = int(request.data.get('coding_count', 1))
        except (ValueError, TypeError):
            mcq_count = 10
            coding_count = 1
            
        if mcq_count == 0 and coding_count == 0:
            return Response({
                "error": "Assessment cannot be empty",
                "message": "Please provide at least one MCQ question or one Coding task for the assessment. They cannot both be 0."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate MCQ / Coding Durations
        try:
            mcq_duration = int(request.data.get('mcq_duration', 10))
            coding_duration = int(request.data.get('coding_duration', 30))
        except (ValueError, TypeError):
            mcq_duration = 10
            coding_duration = 30

        if coding_count > 0 and coding_duration <= 0:
            return Response({
                "error": "Invalid Duration",
                "message": "Coding Assessment Duration must be greater than 0 minutes."
            }, status=status.HTTP_400_BAD_REQUEST)

        if mcq_count > 0 and mcq_duration <= 0:
            return Response({
                "error": "Invalid Duration",
                "message": "MCQ Assessment Duration must be greater than 0 minutes."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            threshold = int(threshold)
            if threshold <= 0:
                return Response({"error": "Invalid Threshold", "message": "Sensitivity Threshold must be greater than 0%."}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            threshold = 70



        # Single candidate "Start Interview" Flow

        if candidate_id:

            try:

                candidate = Candidate.objects.get(id=candidate_id)

            except Candidate.DoesNotExist:

                return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)



            if not job_description:

                job_description = candidate.job_description or "General requirements and responsibilities for this role."



            if resume_files:

                candidate.resume = resume_files[0]

            # skip_scoring mode: Just extract resume text for adaptive questioning context
            skip_scoring = request.data.get('skip_scoring', 'false').lower() == 'true'

            if skip_scoring:
                # Only extract text from resume — no AI scoring, no pass/fail
                candidate.status = 'Interview'
                candidate.save()
                
                if candidate.resume and not candidate.resume_text:
                    from .tasks import extract_resume_text_task
                    # Run synchronously for immediate availability
                    try:
                        extract_resume_text_task(candidate.id)
                    except Exception as e:
                        logger.warning(f"Resume extraction failed (non-blocking): {e}")
                
                return Response({
                    "status": "ready",
                    "message": "Resume processed. Interview ready to start."
                }, status=status.HTTP_200_OK)

            elif not candidate.resume:

                return Response({"error": "Candidate has no resume uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            

            # Ensure candidate has a company/profile link if missing (e.g. from public link)

            # but don't overwrite if it already has one.

            if not candidate.user_profile and request.user.is_authenticated:

                candidate.user_profile = getattr(request.user, 'profile', None)

                if not candidate.company and candidate.user_profile:

                    candidate.company = candidate.user_profile.company

            # Auto-persist role to global JobRole if title is provided
            if candidate.job_title and job_description and request.user.is_authenticated:
                ensure_role_exists(candidate.job_title, job_description, user=request.user)



            batch_id = generate_batch_id()

            batch_name = generate_batch_name(candidate.job_title or job_description[:20])

            candidate.batch_id = batch_id

            candidate.batch_name = batch_name

            candidate.status = 'New'

            candidate.save()



            # Execute synchronously for immediate UI feedback

            try:

                process_resume_batch_task(

                    batch_id=batch_id,

                    job_description=job_description,

                    threshold=threshold,

                    is_fully_automatic=False, 

                    automation_settings={}

                )

                

                candidate.refresh_from_db()

                if not candidate.interview_questions:

                    return Response({"error": "Failed to generate interview questions. The AI may have been unable to parse the resume."}, status=status.HTTP_400_BAD_REQUEST)

                    

                return Response({

                    "interview_questions": candidate.interview_questions

                }, status=status.HTTP_200_OK)

            except Exception as e:

                logger.error(f"Synchronous processing failed: {e}")

                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        # Bulk Upload Flow (100% Asynchronous)

        # experience_level is required for bulk upload
        if not experience_level:
            return Response({"error": "Experience level is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not job_description:

            job_description = "General requirements and responsibilities for this role."



        if not resume_files:

            return Response({"error": "No resumes uploaded"}, status=status.HTTP_400_BAD_REQUEST)



        results = []

        batch_id = generate_batch_id()

        batch_name = "Bulk Screening" # Placeholder, will update per job title if available

        first_job_title = request.data.get('job_title') or request.data.get('role_title')

        if first_job_title:

            batch_name = generate_batch_name(first_job_title)

        

        try:

            is_auto = False
            raw_is_auto = request.data.get('is_fully_automatic')
            if raw_is_auto:
                if isinstance(raw_is_auto, str): is_auto = raw_is_auto.lower() == 'true'
                else: is_auto = bool(raw_is_auto)

            if not is_auto:
                from .models import StandaloneResumeScreening
                from .tasks import process_standalone_resume_screening_task

                # Auto-persist role if custom title/JD is provided
                if first_job_title and request.user.is_authenticated:
                    ensure_role_exists(first_job_title, job_description, user=request.user)
                for resume_file in resume_files:
                    user_profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None
                    company = user_profile.company if user_profile else None
                    candidate_name = getattr(resume_file, 'name', 'Candidate').replace('.pdf', '')
                    
                    new_standalone = StandaloneResumeScreening.objects.create(
                        full_name=candidate_name,
                        email="pending@example.com",
                        resume=resume_file,
                        job_description=job_description,
                        status='New',
                        company=company,
                        user_profile=user_profile,
                        created_by=user_profile,
                        batch_id=batch_id,
                        batch_name=batch_name
                    )
                    results.append({"id": new_standalone.id, "name": candidate_name, "status": "Queued"})
                    process_standalone_resume_screening_task.delay(new_standalone.id, threshold=threshold)
                    
                return Response({
                    "message": "Files successfully uploaded for manual screening.",
                    "results": results,
                    "batch_id": batch_id,
                    "total": len(resume_files)
                }, status=status.HTTP_201_CREATED)

            # INSTANT SAVE: Create Candidate records without waiting for OCR (Automatic Mode)
            for resume_file in resume_files:

                job_title = request.data.get('job_title') or request.data.get('role_title')

                if job_title and request.user.is_authenticated:

                    ensure_role_exists(job_title, job_description, user=request.user)

                user_profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None

                company = user_profile.company if user_profile else None

                candidate_name = getattr(resume_file, 'name', 'Candidate').replace('.pdf', '')

                # Create the candidate record

                new_candidate = Candidate.objects.create(

                    full_name=candidate_name,

                    email="pending@example.com",

                    job_title=job_title or "Applicant",

                    resume=resume_file, 

                    resume_text=None,   

                    status='New',

                    job_description=job_description,

                    company=company,

                    user_profile=user_profile,

                    batch_id=batch_id,

                    batch_name=batch_name,

                    experience_level=experience_level

                )

                results.append({"id": new_candidate.id, "name": candidate_name, "status": "Queued"})

            # 2. Trigger processing as a background task

            same_q = False

            raw_same_q = request.data.get('same_questions_for_all')

            if raw_same_q:

                if isinstance(raw_same_q, str): same_q = raw_same_q.lower() == 'true'

                else: same_q = bool(raw_same_q)



            try:
                pass_threshold = int(request.data.get('pass_threshold', 60))
                interview_pass_threshold = int(request.data.get('interview_pass_threshold', 50))
                if pass_threshold <= 0 or interview_pass_threshold <= 0:
                    return Response({"error": "Invalid Threshold", "message": "Pass thresholds must be greater than 0%."}, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                pass_threshold = 60
                interview_pass_threshold = 50

            automation_settings = {

                'difficulty': request.data.get('difficulty', 'Medium'),

                'duration': int(request.data.get('duration', 60)),

                'mcq_count': int(request.data.get('mcq_count', 10)),
                'coding_count': int(request.data.get('coding_count', 1)),
                'mcq_duration': request.data.get('mcq_duration'),
                'coding_duration': request.data.get('coding_duration'),
                'pass_threshold': pass_threshold,

                'interview_pass_threshold': interview_pass_threshold,

                'mcq_weight': int(request.data.get('mcq_weight', 40)),

                'same_questions_for_all': same_q,

                'assessment_available_from': request.data.get('assessment_available_from'),

                'assessment_available_until': request.data.get('assessment_available_until'),

                'interview_available_from': request.data.get('interview_available_from'),

                'interview_available_until': request.data.get('interview_available_until'),

                'coding_tasks': request.data.get('coding_tasks'), # JSON string of difficulties

                'is_fully_automatic': is_auto  # PERSIST FLAG FOR DOWNSTREAM SIGNALS

            }



            process_resume_batch_task.delay(

                batch_id=batch_id,

                job_description=job_description,

                threshold=threshold,

                is_fully_automatic=is_auto,

                automation_settings=automation_settings

            )



            return Response({

                "batch_id": batch_id, 

                "total": len(results),

                "message": f"Successfully queued {len(results)} resumes for processing."

            }, status=status.HTTP_202_ACCEPTED)



        except Exception as e:

            logger.error(f"ERROR in ResumeMatchView: {str(e)}")

            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class BatchProgressView(APIView):

    """View to check the progress of a resume processing batch."""

    from rest_framework.permissions import IsAuthenticated

    permission_classes = [IsAuthenticated]



    def get(self, request, batch_id):

        candidates = Candidate.objects.filter(batch_id=batch_id)

        if not candidates.exists():
            standalone = StandaloneResumeScreening.objects.filter(batch_id=batch_id)
            if not standalone.exists():
                return Response({"error": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)
            
            processed_qs = standalone.exclude(status='New')
            processed = processed_qs.count()
            total = standalone.count()

            results = []
            for c in processed_qs:
                results.append({
                    "candidate_id": c.id,
                    "candidate_name": c.full_name,
                    "candidate_email": c.email,
                    "match_percentage": c.resume_score,
                    "is_eligible": (c.status == 'Resume Passed'),
                    "status": c.status,
                    "file_name": c.full_name if not c.resume else os.path.basename(c.resume.name),
                    "extraction_failed": (c.status == 'Extraction Failed'),
                    "summary": c.resume_summary or "Match calculated in background." if c.status != 'Extraction Failed' else f"Extraction failed for {c.full_name}."
                })

            return Response({
                "batch_id": batch_id,
                "total": total,
                "processed": processed,
                "is_complete": (processed == total),
                "results": results
            }, status=status.HTTP_200_OK)


        processed_qs = candidates.exclude(status='New')

        processed = processed_qs.count()

        total = candidates.count()

        

        results = []

        for c in processed_qs:

            results.append({

                "candidate_id": c.id,

                "candidate_name": c.full_name,

                "candidate_email": c.email,

                "match_percentage": c.resume_score,

                "is_eligible": (c.status == 'Resume Passed'),

                "status": c.status,

                "file_name": c.full_name if not c.resume else os.path.basename(c.resume.name),

                "extraction_failed": (c.status == 'Extraction Failed'),

                "summary": c.resume_summary or "Match calculated in background." if c.status != 'Extraction Failed' else f"Extraction failed for {c.full_name}."

            })



        return Response({

            "batch_id": batch_id,

            "total": total,

            "processed": processed,

            "is_complete": (processed == total),

            "results": results

        }, status=status.HTTP_200_OK)



class RetryFailedExtractionsView(APIView):

    """Retry extraction for specific failed candidates using their stored resume_text."""

    from rest_framework.permissions import IsAuthenticated

    permission_classes = [IsAuthenticated]



    def post(self, request):

        candidate_ids = request.data.get('candidate_ids', [])

        job_description = request.data.get('job_description', '')

        threshold = request.data.get('threshold', 70)

        try:

            threshold = int(threshold)

        except:

            threshold = 70



        if not candidate_ids:

            return Response({"error": "No candidate IDs provided."}, status=status.HTTP_400_BAD_REQUEST)



        # Fix: Use Key Rotation list

        api_keys = getattr(settings, 'GROQ_API_KEYS', [])

        if not api_keys:

            single_key = getattr(settings, 'GROQ_API_KEY', None)

            api_keys = [single_key] if single_key else []



        if not api_keys:

            return Response({"error": "No API keys configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        print(f"\n🔄 RETRYING EXTRACTION: {len(candidate_ids)} candidates")

        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")



        results = []

        for cid in candidate_ids:

            try:

                candidate = Candidate.objects.get(id=cid)

                print(f"📄 Retrying: {candidate.full_name or 'Unknown'}")



                # Skip already-screened candidates

                if candidate.status == 'Resume Passed' and candidate.full_name != 'Extraction Failed':

                    print("   ℹ️ Already screened — skipping.")

                    results.append({

                        "candidate_id": candidate.id,

                        "candidate_name": candidate.full_name,

                        "candidate_email": candidate.email,

                        "match_percentage": candidate.resume_score,

                        "is_eligible": candidate.resume_score >= threshold,

                        "summary": "Already screened — skipped retry.",

                        "extraction_failed": False,

                        "file_name": candidate.full_name,

                        "already_screened": True

                    })

                    continue



                resume_text = candidate.resume_text

                if not resume_text or len(resume_text.strip()) < 50:

                    print("   ❌ No readable resume text found.")

                    results.append({

                        "candidate_id": candidate.id,

                        "candidate_name": None,

                        "file_name": candidate.full_name or "Unknown",

                        "extraction_failed": True,

                        "is_eligible": False,

                        "match_percentage": 0,

                        "summary": f"No readable resume text stored for this candidate.",

                        "error": "No resume text available for retry."

                    })

                    continue



                jd = job_description or candidate.job_description or "General requirements and responsibilities."



                prompt = f"""
                Act as an expert technical recruiter and interviewer. Analyze the match between the following resume and job description.
                
                RESUME:
                {resume_text}
                
                JOB DESCRIPTION:
                {jd}
                
                SCORING RULES (Strict & Objective):
                1. Start with a BASE SCORE of 100%.
                2. For every CORE SKILL or TECHNOLOGY mentioned in the JD that is MISSING from the resume, SUBTRACT 15-20 points.
                3. If the candidate has NO relevant industry experience for the role, the final score must be below 20%.
                4. If the resume and JD are a 100% match, return 100%.
                5. Be brutally honest. Do not "inflate" the score, but do not drop to 0% unless there is zero relevance.
                
                Please provide:
                1. The candidate's full name. Look at the very top of the document. If missing, return "Extraction Failed".
                2. The candidate's contact email. Look for email patterns. If missing, return "Extraction Failed".
                3. A match percentage (0-100).
                4. A brief 2-3 sentence summary of the fit. Explicitly mention any critical missing skills.
                5. A list of 7 interview questions (5 technical/behavioral questions + 2 coding-specific challenges or deep-dives) based on their resume and the JD.
                
                CRITICAL: You MUST extract the name and email if they are present in ANY form. Do not be overly strict with formatting.
                
                Format the output strictly as a raw JSON object with these keys: "candidate_name", "candidate_email", "match_percentage", "summary", "interview_questions".
                """



                # Retry with Groq client (handles key rotation and backoff internally)
                from ai_assessments.llm_client import call_groq_with_backoff, get_groq_model
                match_result = None
                
                try:
                    print(f"   🤖 Calling Groq ({get_groq_model()})... ", end="", flush=True)
                    match_result = call_groq_with_backoff(
                        prompt=prompt,
                        is_json=True,
                        max_tokens=4096,
                        temperature=0.0,
                    )
                    if match_result:
                        print("✅ Success!")
                    else:
                        print("❌ Empty response")
                except Exception as llm_err:
                    print(f"❌ LLM Error: {llm_err}")
                    logger.error(f"LLM retry failed for candidate {cid}: {llm_err}")



                

                if match_result:

                    extracted_name = match_result.get('candidate_name') or match_result.get('full_name') or match_result.get('name') or "Extraction Failed"

                    extracted_email = match_result.get('candidate_email') or match_result.get('email') or match_result.get('email_address') or "Extraction Failed"

                    

                    # Only overwrite identity if it's missing or a placeholder.

                    # This prevents valid recruiter-entered data from being replaced by AI extraction errors.

                    is_placeholder_email = not candidate.email or any(p in candidate.email.lower() for p in ['pending', 'extraction', 'unknown'])

                    is_placeholder_name = not candidate.full_name or any(p in candidate.full_name.lower() for p in ['extraction', 'unknown', 'pending'])



                    if is_placeholder_name and extracted_name != "Extraction Failed":

                        candidate.full_name = extracted_name

                    

                    if is_placeholder_email and extracted_email != "Extraction Failed":

                        candidate.email = extracted_email

                    

                    percentage = match_result.get('match_percentage', 0)

                    try:

                        num_percentage = int(float(percentage))

                    except:

                        num_percentage = 0

                    
                    # For AI interviews (non-fully-automatic with interview_duration_minutes),
                    # resume is only for question generation — don't score.
                    # Resume screening and fully-automatic always get scored.
                    is_auto = getattr(candidate, 'automation_settings', None)
                    is_fully_auto = isinstance(is_auto, dict) and is_auto.get('is_fully_automatic', False)
                    is_ai_interview_only = (
                        not is_fully_auto
                        and isinstance(is_auto, dict)
                        and 'interview_duration_minutes' in is_auto
                    )

                    if is_ai_interview_only:
                        candidate.resume_summary = match_result.get('summary', '')
                    else:
                        candidate.resume_score = num_percentage
                        candidate.resume_summary = match_result.get('summary', 'No summary provided by AI.')
                        is_eligible = (num_percentage >= threshold)
                        candidate.status = 'Resume Passed' if is_eligible else 'Resume Failed'

                    if match_result.get('interview_questions'):

                        candidate.interview_questions = match_result['interview_questions']

                        

                    candidate.save()

                    

                    match_result['candidate_id'] = candidate.id

                    match_result['file_name'] = candidate.full_name

                    match_result['is_eligible'] = is_eligible

                    match_result['status'] = candidate.status

                    match_result['extraction_failed'] = (extracted_name == 'Extraction Failed' and extracted_email == 'Extraction Failed')

                    results.append(match_result)

                else:

                    results.append({

                        "candidate_id": candidate.id,

                        "file_name": candidate.full_name or "Unknown",

                        "extraction_failed": True,

                        "is_eligible": False,

                        "match_percentage": 0,

                        "summary": "Extraction Failed after retry (Quota or AI Error)."

                    })



            except Exception as e:

                logger.error(f"Error retrying candidate {cid}: {e}")

                results.append({"candidate_id": cid, "error": str(e), "extraction_failed": True})



        return Response(results, status=status.HTTP_200_OK)



class CandidateListCreateView(generics.ListCreateAPIView):

    from rest_framework.permissions import IsAuthenticated

    permission_classes = [IsAuthenticated]

    serializer_class = CandidateSerializer



    def get_queryset(self):

        user_profile = getattr(self.request.user, 'profile', None)

        if not user_profile or not user_profile.company:

            return Candidate.objects.none()

        

        from api._imports import get_scoped_user_ids

        scoped_ids = get_scoped_user_ids(user_profile)

        

        if scoped_ids is None:

            # Application Admin: all in company

            return Candidate.objects.filter(company=user_profile.company, is_deleted=False).order_by('-created_at')

        

        # Scoped: only candidates created by users in this user's reporting hierarchy

        return Candidate.objects.filter(

            company=user_profile.company,

            user_profile_id__in=scoped_ids,

            is_deleted=False

        ).order_by('-created_at')



    def perform_create(self, serializer):

        user_profile = getattr(self.request.user, 'profile', None)

        company = user_profile.company if user_profile else None

        candidate = serializer.save(company=company, user_profile=user_profile)

        # Auto-persist role to global JobRole if title and description are provided
        if candidate.job_title and candidate.job_description and self.request.user.is_authenticated:
            ensure_role_exists(candidate.job_title, candidate.job_description, user=self.request.user)



INTERVIEW_LINK_TTL_MINUTES = 60 # Back to 60 minutes as requested





def _resolve_public_candidate(public_token):

    """

    Backward compatible resolver for public interview links.

    Supports both new UUID public_token and legacy numeric candidate id links.

    """

    token_str = str(public_token).strip()

    # New format: UUID token

    try:

        parsed = uuid.UUID(token_str)

        return Candidate.objects.get(public_token=parsed, is_deleted=False)

    except Exception:

        pass



    # Legacy format: integer candidate id

    if token_str.isdigit():

        return Candidate.objects.get(pk=int(token_str), is_deleted=False)



    raise Candidate.DoesNotExist()



class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CandidateSerializer

    permission_classes = [AllowAny]



    def get_queryset(self):

        if self.request.user.is_authenticated:

            user_profile = getattr(self.request.user, 'profile', None)

            if not user_profile or not user_profile.company:

                return Candidate.objects.none()



            from api._imports import get_scoped_user_ids

            scoped_ids = get_scoped_user_ids(user_profile)



            if scoped_ids is None:

                return Candidate.objects.filter(company=user_profile.company, is_deleted=False)



            return Candidate.objects.filter(

                company=user_profile.company,

                user_profile_id__in=scoped_ids,

                is_deleted=False

            )

        # Allow unauthenticated GET requests (required for candidates starting interviews)

        return Candidate.objects.filter(is_deleted=False)



    def destroy(self, request, *args, **kwargs):

        user = request.user

        if not user.is_authenticated:

            return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

            

        user_profile = getattr(user, 'profile', None)

        if not user_profile or not user_profile.company:

            return super().destroy(request, *args, **kwargs)



        instance = self.get_object()

        

        # Determine if this was an interview or just a resume screening based on progress

        is_interview = instance.completed_at is not None or (isinstance(instance.interview_summary, list) and len(instance.interview_summary) > 0)

        prefix = "AI Interview Session" if is_interview else "Resume Screening Result"

        

        # Use centralized helper to handle policy and workflow

        response, handled = handle_deletion_request(

            user_profile=user_profile,

            company=user_profile.company,

            content_type='Candidate',

            object_id=instance.id,

            object_repr=f"{prefix}: {instance.full_name} ({instance.email})",

            reason=request.data.get('reason')

        )

        

        if handled:

            return response



        return super().destroy(request, *args, **kwargs)





    def get(self, request, *args, **kwargs):

        try:

            candidate = self.get_object()
            now = timezone.now()



            # Prevent retaking if already completed or if they failed screening

            if candidate.status in ['Completed', 'Hired', 'Rejected'] or candidate.completed_at:

                return Response(

                    {'error': 'You have already completed this interview session and cannot retake it.', 'link_expired': True},

                    status=status.HTTP_403_FORBIDDEN

                )

            





            # First access — stamp the time

            if not candidate.link_opened_at:

                candidate.link_opened_at = now
                candidate.save(update_fields=['link_opened_at'])

            else:

                # Check if link has expired

                elapsed = now - candidate.link_opened_at

                if elapsed.total_seconds() > INTERVIEW_LINK_TTL_MINUTES * 60:

                    return Response(

                        {'error': 'Interview link has expired.', 'link_expired': True},

                        status=status.HTTP_403_FORBIDDEN

                    )



            response = self.retrieve(request, *args, **kwargs)

            response["Cache-Control"] = "no-cache, no-store, must-revalidate"

            response["Pragma"] = "no-cache"

            response["Expires"] = "0"

            return response

        except Exception as e:

            logger.error(f"Error in CandidateDetailView.get: {str(e)}", exc_info=True)

            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class CandidatePublicDetailView(generics.RetrieveAPIView):

    serializer_class = CandidateSerializer

    permission_classes = [AllowAny]

    authentication_classes = []

    def get_object(self):

        return _resolve_public_candidate(self.kwargs.get('public_token'))



    def get(self, request, *args, **kwargs):

        candidate = self.get_object()

        now = timezone.now()

        # Only block if interview is truly completed (has completed_at and status is final)
        if candidate.completed_at and candidate.status in ['Completed', 'Hired', 'Rejected']:
            return Response(

                {'error': 'You have already completed this interview session and cannot retake it.', 'link_expired': True},

                status=status.HTTP_403_FORBIDDEN

            )









        if candidate.link_opened_at:

            elapsed = now - candidate.link_opened_at

            if elapsed.total_seconds() > INTERVIEW_LINK_TTL_MINUTES * 60:

                return Response(

                    {'error': 'Interview link has expired.', 'link_expired': True},

                    status=status.HTTP_403_FORBIDDEN

                )



        response = self.retrieve(request, *args, **kwargs)

        # FIX: Include server_time so frontend can sync timer against
        # the server clock instead of relying on the client's local clock.
        # This prevents candidates from gaining extra time by changing
        # their system clock.
        if isinstance(response.data, dict):
            response.data['server_time'] = now.isoformat()

        response["Cache-Control"] = "no-cache, no-store, must-revalidate"

        response["Pragma"] = "no-cache"

        response["Expires"] = "0"

        return response





class CandidateStatusUpdateView(APIView):

    permission_classes = [AllowAny]

    authentication_classes = []

    def patch(self, request, pk):

        try:

            user_profile = getattr(request.user, 'profile', None)

            company = user_profile.company if user_profile and user_profile.company else None

            

            # If recruiter, filter by company and hierarchy scope. If candidate (not auth), AllowAny might be needed?

            # Existing code didn't have permission_classes, so it was public.

            # We'll allow status updates if either recruiter from same company or AllowAny (for backward compat)

            if request.user.is_authenticated and company:
                from api._imports import get_scoped_user_ids
                scoped_ids = get_scoped_user_ids(user_profile)
                if scoped_ids is not None:
                    candidate = Candidate.objects.get(pk=pk, company=company, user_profile_id__in=scoped_ids)
                else:
                    candidate = Candidate.objects.get(pk=pk, company=company)

            else:

                candidate = Candidate.objects.get(pk=pk)

            

            new_status = request.data.get('status')

            if new_status in dict(Candidate.STATUS_CHOICES):

                # Security hardening: unauthenticated candidate link flow should only be

                # able to mark itself Completed (not Hired/Rejected/etc.).

                if not request.user.is_authenticated and new_status != 'Completed':

                    return Response({'error': 'Unauthenticated status updates are restricted.'}, status=status.HTTP_403_FORBIDDEN)

                candidate.status = new_status

                if new_status in ['Completed', 'Hired', 'Rejected', 'Resume Failed']:

                    candidate.resume_text = None

                if new_status == 'Completed':

                    candidate.completed_at = timezone.now()

                candidate.save()

                response = Response({'status': 'success', 'new_status': candidate.status})

                response["Cache-Control"] = "no-cache, no-store, must-revalidate"

                response["Pragma"] = "no-cache"

                response["Expires"] = "0"

                return response

            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        except Candidate.DoesNotExist:

            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)





class CandidatePublicStatusUpdateView(APIView):

    permission_classes = [AllowAny]

    authentication_classes = []


    # Support POST as well (for navigator.sendBeacon fallback which only supports POST)
    def post(self, request, public_token):
        return self.patch(request, public_token)

    def patch(self, request, public_token):

        try:

            candidate = _resolve_public_candidate(public_token)

            new_status = request.data.get('status')

            if new_status in ('Interview', 'Interviewing'):
                candidate.status = new_status
                # Stamp link_opened_at here — this is the true interview start moment.
                # The 1-hour timer is calculated from this timestamp on the frontend.
                # Only set it if not already set (handles resume/refresh cases).
                now = timezone.now()
                update_fields = ['status']
                if not candidate.link_opened_at:
                    candidate.link_opened_at = now
                    update_fields.append('link_opened_at')
                    from .utils import log_automation_event
                    log_automation_event(
                        candidate,
                        'STATUS_CHANGE',
                        'SUCCESS',
                        f"AI Interview timer started. Candidate began the interview session.",
                        phase='INTERVIEW'
                    )
                candidate.save(update_fields=update_fields)
                return Response({
                    'message': f'Interview status updated to {new_status}.',
                    'link_opened_at': candidate.link_opened_at.isoformat() if candidate.link_opened_at else None,
                }, status=status.HTTP_200_OK)

            if new_status not in dict(Candidate.STATUS_CHOICES):

                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

            if new_status != 'Completed':

                return Response({'error': 'Only completion status is allowed for public links.'}, status=status.HTTP_403_FORBIDDEN)

            # Security: Only allow completion if the interview was actually started
            if not candidate.link_opened_at:
                return Response({'error': 'Interview was never started.'}, status=status.HTTP_403_FORBIDDEN)

            # Refresh from DB to get the latest score (in case last ProcessAnswer is still saving)
            candidate.refresh_from_db()

            # Save the full conversation transcript if provided by the frontend
            chat_history = request.data.get('chat_history')
            if chat_history and isinstance(chat_history, list):
                candidate.full_conversation = chat_history



            # Calculate final score percentage.
            # For student/practice interviews, score against the chosen question_count.
            # For company-created interviews, always use the default 14 questions (140 points max).
            _is_practice_interview = (
                isinstance(candidate.automation_settings, dict)
                and candidate.automation_settings.get('is_practice', False)
            )
            if _is_practice_interview:
                custom_qc = candidate.automation_settings.get('question_count', TOTAL_INTERVIEW_QUESTIONS)
                if isinstance(custom_qc, int) and 5 <= custom_qc <= 20:
                    total_possible = custom_qc * 10
                else:
                    total_possible = TOTAL_INTERVIEW_QUESTIONS * 10
            else:
                # Company interviews: always against full 14 questions (140 points max)
                # Unanswered questions count as 0, preventing gaming by exiting early
                total_possible = TOTAL_INTERVIEW_QUESTIONS * 10  # Always 140
            score_percentage = (candidate.score / total_possible) * 100 if total_possible > 0 else 0
            # Calculate final score percentage using the model's single source of truth
            score_percentage = candidate.score_percentage

            # Get integrity score
            integrity_obj = getattr(candidate, 'integrity', None)
            integrity_score = integrity_obj.integrity_score if integrity_obj else 100.0

            # Determine pass/fail based on threshold
            # New logic: No penalty on raw score. On-Hold if passed but integrity < 75%
            threshold = candidate.interview_pass_threshold if candidate.interview_pass_threshold is not None else 50
            INTEGRITY_THRESHOLD = 75.0

            if score_percentage >= threshold and integrity_score >= INTEGRITY_THRESHOLD:
                # Passed interview AND good integrity
                candidate.status = 'Hired'
            elif score_percentage >= threshold and integrity_score < INTEGRITY_THRESHOLD:
                # Passed interview BUT suspicious behavior — needs manual review
                candidate.status = 'On-Hold'
            else:
                # Failed on answers alone
                candidate.status = 'Rejected'



            candidate.completed_at = timezone.now()

            candidate.resume_text = None

            candidate.save()



            # Log interview completion

            from .utils import log_automation_event

            log_automation_event(

                candidate, 

                'STATUS_CHANGE', 

                'SUCCESS' if candidate.status == 'Hired' else 'WARNING', 

                f"AI Interview completed. Final Status: {candidate.status}. Score: {score_percentage:.1f}%, Integrity: {integrity_score:.1f}% (threshold: {INTEGRITY_THRESHOLD}%)",

                phase='INTERVIEW'

            )



            response = Response({'status': 'success', 'new_status': candidate.status})

            response["Cache-Control"] = "no-cache, no-store, must-revalidate"

            response["Pragma"] = "no-cache"

            response["Expires"] = "0"

            return response

        except Candidate.DoesNotExist:

            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)





class UpdateIntegrityView(APIView):

    permission_classes = [AllowAny]

    authentication_classes = []

    def post(self, request, pk):

        try:

            candidate = Candidate.objects.get(pk=pk)

            integrity, created = InterviewIntegrity.objects.get_or_create(candidate=candidate)

            

            # Grace Warning System Phase 1: Record counts

            event_type = request.data.get('event_type')

            screenshot_b64 = request.data.get('screenshot')

            webcam_b64 = request.data.get('webcam_screenshot')

            
            if event_type in ['tab_switch', 'tab_switch_return', 'window_blur']:

                integrity.tab_switches += 1

            elif event_type == 'phone_detection':

                integrity.phone_detections += 1

            elif event_type == 'multiface_detection':

                integrity.multiface_detections += 1

            elif event_type in ['no_face_detection', 'face_detection_lost']:

                integrity.no_face_detections += 1

            
            # Create a detailed log entry with dual Base64 storage

            InterviewIntegrityLog.objects.create(

                candidate=candidate,

                event_type=event_type,

                screenshot_base64=screenshot_b64,

                webcam_screenshot_base64=webcam_b64

            )

            

            # Define duration-based penalty weights
            # tab_switch and face_mismatch: penalty scales with duration
            # multiple faces: flat 2% per occurrence
            duration_seconds = request.data.get('duration_seconds', 0)
            try:
                duration_seconds = int(duration_seconds)
            except (TypeError, ValueError):
                duration_seconds = 0

            def get_duration_penalty(dur):
                """Duration-based penalty: <5s=1%, 5-10s=2%, 10-30s=3%, >30s=4%"""
                if dur <= 5:
                    return 1
                elif dur <= 10:
                    return 2
                elif dur <= 30:
                    return 3
                else:
                    return 4

            # Calculate this event's penalty
            if event_type == 'tab_switch_return':
                # This is the "return" event with duration — apply duration-based penalty
                event_penalty = get_duration_penalty(duration_seconds)
            elif event_type in ['tab_switch', 'window_blur']:
                # Initial tab switch event — minimal penalty (duration unknown yet)
                event_penalty = 1
            elif event_type == 'face_mismatch':
                # Face mismatch — DeepFace fires every 30s, so each occurrence = 3%
                event_penalty = 3
            elif event_type in ['multiface_detection', 'phone_detection']:
                # Flat 2% per occurrence
                event_penalty = 2
            elif event_type in ['no_face_detection', 'face_detection_lost']:
                event_penalty = 2
            else:
                event_penalty = 1

            # Accumulate penalty on the integrity object
            if not hasattr(integrity, 'accumulated_penalty'):
                # Calculate from existing data for backward compat
                accumulated = (
                    integrity.tab_switches * 1 +
                    integrity.phone_detections * 2 +
                    integrity.multiface_detections * 2 +
                    integrity.no_face_detections * 1
                )
            else:
                accumulated = 100 - integrity.integrity_score

            # Grace Warning System: First 3 violations are free
            if len(integrity.warning_logs) < 3:
                integrity.warning_logs.append(event_type)
                event_penalty = 0  # Free pass

            total_penalty = accumulated + event_penalty
            integrity.integrity_score = max(0, 100 - total_penalty)
            integrity.save()

            

            return Response({

                "status": "success",

                "integrity_score": integrity.integrity_score,

                "violations": {

                    "tab_switches": integrity.tab_switches,

                    "phone_detections": integrity.phone_detections,

                    "multiface_detections": integrity.multiface_detections,

                    "no_face_detections": integrity.no_face_detections

                }

            })

        except Candidate.DoesNotExist:

            return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)





class CandidatePublicIntegrityUpdateView(APIView):

    permission_classes = [AllowAny]

    authentication_classes = []



    def post(self, request, public_token):

        try:

            candidate = _resolve_public_candidate(public_token)

            integrity, created = InterviewIntegrity.objects.get_or_create(candidate=candidate)



            event_type = request.data.get('event_type')

            screenshot_b64 = request.data.get('screenshot')

            webcam_b64 = request.data.get('webcam_screenshot')



            if event_type in ['tab_switch', 'tab_switch_return', 'window_blur']:

                integrity.tab_switches += 1

            elif event_type == 'phone_detection':

                integrity.phone_detections += 1

            elif event_type == 'multiface_detection':

                integrity.multiface_detections += 1

            elif event_type in ['no_face_detection', 'face_detection_lost']:

                integrity.no_face_detections += 1



            InterviewIntegrityLog.objects.create(

                candidate=candidate,

                event_type=event_type,

                screenshot_base64=screenshot_b64,

                webcam_screenshot_base64=webcam_b64

            )



            if len(integrity.warning_logs) < 3:

                integrity.warning_logs.append(event_type)



            weights = {

                'tab_switch': 2,

                'phone_detection': 2,

                'multiface_detection': 2,

                'no_face_detection': 2,

                'face_detection_lost': 2

            }

            total_raw_penalty = (

                integrity.tab_switches * weights['tab_switch'] +

                integrity.phone_detections * weights['phone_detection'] +

                integrity.multiface_detections * weights['multiface_detection'] +

                integrity.no_face_detections * weights['no_face_detection']

            )

            free_penalty = sum(weights.get(w, 0) for w in integrity.warning_logs)

            integrity.integrity_score = max(0, 100 - (total_raw_penalty - free_penalty))

            integrity.save()



            return Response({

                "status": "success",

                "integrity_score": integrity.integrity_score,

                "violations": {

                    "tab_switches": integrity.tab_switches,

                    "phone_detections": integrity.phone_detections,

                    "multiface_detections": integrity.multiface_detections,

                    "no_face_detections": integrity.no_face_detections

                }

            })

        except Candidate.DoesNotExist:

            return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)



# NOTE: Dead duplicate ProcessAnswerView removed from here. Active class below at ProcessAnswerView (line ~4100).
# NOTE: CandidateTimelineView, LatestActiveBatchView, CandidateReportDownloadView are defined
# later in this file (after TTSView). The duplicates that were here have been removed.








class PanValidationView(APIView):
    """
    Validates PAN card photo using OCR and compares with entered PAN number.
    Returns extracted PAN number from photo and match status.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            pan_photo = request.FILES.get('pan_photo')
            entered_pan = request.data.get('pan_number', '').upper().strip()

            if not pan_photo:
                return Response({'error': 'PAN photo is required'}, status=status.HTTP_400_BAD_REQUEST)

            if not entered_pan:
                return Response({'error': 'PAN number is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate PAN format (5 letters + 4 digits + 1 letter)
            pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            if not re.match(pan_pattern, entered_pan):
                return Response({
                    'error': 'Invalid PAN format. Expected format: ABCDE1234F',
                    'is_valid': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # Read and process image
            image = Image.open(pan_photo)
            
            # Try using EasyOCR if available
            extracted_text = ""
            try:
                reader = _get_reader()
                if reader:
                    img_array = np.array(image)
                    result = reader.readtext(img_array, detail=0)
                    extracted_text = ' '.join(result)
                    logger.info(f"EasyOCR extracted text: {extracted_text}")
            except Exception as ocr_error:
                logger.warning(f"EasyOCR failed: {str(ocr_error)}")

            # If EasyOCR fails, try using DeepSeek Vision
            if not extracted_text:
                try:
                    llm_client = create_llm_client()
                    
                    import base64
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    response = llm_client.chat.completions.create(
                        model=get_default_model(),
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Extract the PAN number from this PAN card image. The PAN number is 10 characters: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F). Return ONLY the PAN number, nothing else."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                                ]
                            }
                        ],
                        max_tokens=20
                    )
                    extracted_text = response.choices[0].message.content.upper().strip()
                    logger.info(f"DeepSeek Vision extracted text: {extracted_text}")
                except Exception as ds_error:
                    logger.warning(f"DeepSeek Vision failed: {str(ds_error)}")

            # Extract PAN-like pattern from text
            pan_from_photo = None
            if extracted_text:
                pan_matches = re.findall(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', extracted_text.upper())
                if pan_matches:
                    pan_from_photo = pan_matches[0]

            # Compare entered PAN with extracted PAN
            is_verified = False
            if pan_from_photo:
                is_verified = (entered_pan == pan_from_photo)

            return Response({
                'entered_pan': entered_pan,
                'extracted_pan': pan_from_photo,
                'is_verified': is_verified,
                'extracted_text': extracted_text if settings.DEBUG else None,
                'message': 'PAN verified successfully' if is_verified else 'PAN mismatch. Please check your PAN number and photo.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"PAN validation error: {str(e)}", exc_info=True)
            return Response({
                'error': f'Failed to validate PAN: {str(e)}',
                'is_verified': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CandidateRegistrationUpdateView(APIView):
    """
    Updates candidate registration details (phone, PAN, resume) when they first open the interview link.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, public_token):
        logger.info(f"POST request to registration for token: {public_token}")
        logger.info(f"[IdentityPhoto] Registration POST received. data_keys={list(request.data.keys())}")
        try:
            candidate = Candidate.objects.get(public_token=public_token)



            phone = request.data.get('phone')
            if phone:
                phone_clean = re.sub(r'\D', '', str(phone))
                if not re.match(r'^[6-9]\d{9}$', phone_clean):
                    logger.warning(f"Registration failed: Invalid phone '{phone}' for candidate {public_token}")
                    return Response(
                        {'error': 'Enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                candidate.phone = phone_clean

            pan_number = request.data.get('pan_number')
            if pan_number:
                pan_number = pan_number.upper().strip()
                pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
                if not re.match(pan_pattern, pan_number):
                    logger.warning(f"Registration failed: Invalid PAN format '{pan_number}' for candidate {public_token}")
                    return Response({'error': 'Invalid PAN format. Expected: ABCDE1234F'}, status=status.HTTP_400_BAD_REQUEST)

                # SECURITY CHECK 1: Prevent PAN changes after interview starts
                if candidate.pan_locked:
                    if candidate.pan_number and candidate.pan_number != pan_number:
                        logger.warning(f"Registration failed: PAN locked for candidate {candidate.email}")
                        return Response({
                            'error': 'PAN number cannot be changed once the interview has started.',
                            'pan_locked': True
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Same PAN re-sent (e.g. face-hash payload includes it) — allow through
                        pass

                # SECURITY CHECK 2: Prevent one person from using multiple PANs
                if candidate.pan_number and candidate.pan_number != pan_number:
                    logger.warning(f"Registration failed: PAN change attempted from {candidate.pan_number} to {pan_number} for candidate {candidate.email}")
                    return Response({
                        'error': 'PAN number cannot be changed. You already registered with a different PAN.',
                        'existing_pan': candidate.pan_number
                    }, status=status.HTTP_400_BAD_REQUEST)

                # For AI interviews, we allow any PAN to be used at the form stage.
                # Identity verification happens during face registration (DeepFace
                # compares the captured face against the PAN root photo). If it
                # doesn't match, a mismatch flag is raised for admin review.

                # Track PAN history for audit
                if not candidate.pan_number:
                    candidate.pan_history = [{
                        'action': 'registered',
                        'pan': pan_number,
                        'timestamp': timezone.now().isoformat()
                    }]

                candidate.pan_number = pan_number

            pan_photo = request.FILES.get('pan_photo')
            if pan_photo:
                candidate.pan_photo = pan_photo

            pan_verified = request.data.get('pan_verified')
            if pan_verified is not None:
                # Convert string to boolean
                if isinstance(pan_verified, str):
                    candidate.pan_verified = pan_verified.lower() == 'true'
                else:
                    candidate.pan_verified = bool(pan_verified)

            resume = request.FILES.get('resume')
            if resume:
                allowed_extensions = ['.pdf', '.doc', '.docx']
                file_name = resume.name.lower()
                if not any(file_name.endswith(ext) for ext in allowed_extensions):
                    return Response(
                        {'error': 'Invalid resume format. Please upload a PDF, DOC, or DOCX file.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                candidate.resume = resume

            full_name = request.data.get('full_name')
            if full_name:
                candidate.full_name = full_name

            email = request.data.get('email')
            if email:
                candidate.email = email

            face_embedding_hash = request.data.get('face_embedding_hash')
            face_verified = request.data.get('face_verified', False)
            identity_mismatch_override = request.data.get('identity_mismatch_override', False)

            # ── PHOTO PERSISTENCE STRATEGY (AI Interview Identity Workflow) ─────────
            # • original_identity_photo  → the LATEST verified registered face (always
            #   updated when no mismatch). This is what the report shows.
            # • pending_identity_photo   → the NEW face captured when a mismatch was
            #   detected. Never auto-promoted; an admin must approve via the
            #   results page to push this into DeepFace.
            # ────────────────────────────────────────────────────────────────────────
            if face_embedding_hash:
                snapshot_b64_payload = (
                    request.data.get('snapshot_b64')
                    or request.data.get('new_face_photo_b64')
                    or request.data.get('original_face_photo_b64')
                )
                logger.info(
                    f"[IdentityPhoto] candidate={candidate.email} token={public_token} "
                    f"snapshot_present={bool(snapshot_b64_payload)} "
                    f"identity_mismatch_override={identity_mismatch_override}"
                )

                if snapshot_b64_payload:
                    try:
                        clean_b64 = snapshot_b64_payload
                        if ',' in clean_b64 and clean_b64.startswith('data:'):
                            clean_b64 = clean_b64.split(',', 1)[1]

                        # Always store this session's captured face.
                        candidate.registered_face_b64 = clean_b64

                        if identity_mismatch_override:
                            # Mismatch: also store as pending for admin review.
                            candidate.pending_face_b64 = clean_b64
                            candidate.photo_update_approved = False
                            logger.info(f"[IdentityPhoto] Stored pending face b64 awaiting admin approval")
                        else:
                            logger.info(f"[IdentityPhoto] Updated registered_face_b64")

                        # Populate master_face_b64: the PAN's trusted master photo.
                        # On first-ever registration (CASE C), the master IS this photo.
                        # On returning verified (CASE B verified), fetch the existing
                        # master from DeepFace so the report can show it for comparison.
                        if not candidate.master_face_b64:
                            # First time for this candidate row — try to fetch from DeepFace.
                            try:
                                import requests as _requests
                                pan_id = str(candidate.pan_number or candidate.public_token).strip().lower()
                                df_photo_url = f"http://127.0.0.1:8500/api/v1/registration/registered/{pan_id}/photo"
                                photo_resp = _requests.get(df_photo_url, timeout=10)
                                if photo_resp.status_code == 200 and photo_resp.content:
                                    import base64 as b64_mod
                                    candidate.master_face_b64 = b64_mod.b64encode(photo_resp.content).decode('ascii')
                                    logger.info(f"[IdentityPhoto] Fetched master face from DeepFace ({len(photo_resp.content)} bytes)")
                                else:
                                    # DeepFace doesn't have one yet (brand new PAN) — use this photo as master.
                                    candidate.master_face_b64 = clean_b64
                                    logger.info(f"[IdentityPhoto] No existing master in DeepFace; using current photo as master")
                            except Exception as fetch_err:
                                # Fallback: use current photo as master.
                                candidate.master_face_b64 = clean_b64
                                logger.warning(f"[IdentityPhoto] Could not fetch master from DeepFace: {fetch_err}; using current")

                        # Register session-scoped anchor in DeepFace for live proctoring.
                        try:
                            from .utils import _register_face_with_deepface
                            pan_id = str(candidate.pan_number or candidate.public_token).strip().lower()
                            token_id = str(candidate.public_token).strip().lower()
                            session_person_id = f"{pan_id}/sessions/{token_id}"
                            logger.info(f"[IdentityPhoto] Registering DeepFace session anchor: {session_person_id}")
                            df_result = _register_face_with_deepface(session_person_id, clean_b64)
                            if df_result and df_result.get('success'):
                                logger.info(f"[IdentityPhoto] Session anchor OK: {session_person_id}")
                            else:
                                logger.error(f"[IdentityPhoto] Session anchor FAILED: {df_result}")
                        except Exception as df_err:
                            logger.exception(f"[IdentityPhoto] DeepFace session anchor error: {df_err}")
                            err_msg = str(df_err).lower()
                            if "quality" in err_msg or "no face detected" in err_msg:
                                return Response({"error": "Image quality too low or no face detected. Please provide a clearer face image."}, status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        logger.error(f"[IdentityPhoto] Failed to persist identity photo: {e}")

            if face_embedding_hash:
                # If frontend detected a returning-candidate face mismatch but allowed them to continue
                if identity_mismatch_override:
                    logger.warning(f"Identity mismatch override for candidate {candidate.email} (token: {public_token}). "
                                   f"Face did not match previously registered photo. New photo stored as pending; "
                                   f"awaiting admin approval before DeepFace is updated.")
                    candidate.identity_mismatch_detected = True
                    candidate.identity_mismatch_details = {
                        'mismatch_at': timezone.now().isoformat(),
                        'mismatch_type': 'returning_candidate_face_mismatch',
                        'original_person_id': str(candidate.pan_number or public_token),
                        'note': 'Candidate face did not match their previously registered photo. New photo stored as pending; admin must approve before DeepFace is updated.'
                    }
                    # Persist the new face hash on THIS candidate (per-interview).
                    # The DeepFace master anchor stays untouched (still the previously
                    # registered face) — admin must approve to swap it. But on this
                    # candidate row, the hash represents the face they actually
                    # registered with for this interview, so a refresh skips the
                    # wizard and resumes the session cleanly.
                    candidate.face_embedding_hash = face_embedding_hash

                # If face was verified by DeepFace against original holder, accept the verification
                elif face_verified:
                    candidate.face_embedding_hash = face_embedding_hash
                    candidate.pan_verified = True
                else:
                    # ── INDEPENDENT IDENTITY MISMATCH CHECK ──────────────────────────
                    # Compare this candidate's face_embedding_hash against ALL other
                    # candidates who share the same PAN. If different hashes exist,
                    # that means different faces used the same PAN → flag mismatch.
                    # This check is INDEPENDENT of DeepFace's live state (which may
                    # have been overwritten by the frontend's register-with-overwrite).
                    mismatch_flagged = False
                    if candidate.pan_number and face_embedding_hash:
                        other_candidates_with_same_pan = Candidate.objects.filter(
                            pan_number=candidate.pan_number,
                            face_embedding_hash__isnull=False,
                        ).exclude(public_token=public_token).exclude(face_embedding_hash=face_embedding_hash)

                        if other_candidates_with_same_pan.exists():
                            original_holder = other_candidates_with_same_pan.first()
                            logger.warning(
                                f"[IdentityPhoto] DB-level face hash mismatch detected! "
                                f"PAN={candidate.pan_number}, current_hash={face_embedding_hash[:16]}..., "
                                f"original_holder={original_holder.full_name} (hash={original_holder.face_embedding_hash[:16]}...)"
                            )
                            candidate.identity_mismatch_detected = True
                            candidate.identity_mismatch_details = {
                                'mismatch_at': timezone.now().isoformat(),
                                'original_holder_token': str(original_holder.public_token),
                                'original_holder_name': original_holder.full_name,
                                'mismatch_type': 'different_face_same_pan',
                                'note': f'Different face hash detected for same PAN. Original: {original_holder.full_name}.'
                            }
                            # Store pending face for admin approval
                            if snapshot_b64_payload:
                                candidate.pending_face_b64 = clean_b64
                                candidate.photo_update_approved = False
                            # Copy original holder's registered face as master for comparison
                            if not candidate.master_face_b64 and original_holder.registered_face_b64:
                                candidate.master_face_b64 = original_holder.registered_face_b64
                            mismatch_flagged = True

                    # Also try DeepFace verification (if available and not already flagged)
                    if not mismatch_flagged and candidate.pan_number:
                        from api.deepface_client import df_is_registered, df_verify
                        pan_id = str(candidate.pan_number).strip().lower()
                        try:
                            if df_is_registered(pan_id):
                                df_res = df_verify(pan_id, clean_b64)
                                if not df_res.get('verified', False):
                                    # Mismatch detected against master DeepFace record
                                    
                                    # Try to resolve original holder's name for the admin report
                                    original_name = 'Registered User'
                                    original_token = 'Unified Record'
                                    
                                    exist_cand = Candidate.objects.filter(pan_number=candidate.pan_number).exclude(public_token=public_token).first()
                                    if exist_cand:
                                        original_name = exist_cand.full_name
                                        original_token = str(exist_cand.public_token)
                                    else:
                                        from api.models import CandidateDetails
                                        detail = CandidateDetails.objects.filter(pan_number=candidate.pan_number).order_by('-id').first()
                                        if detail:
                                            original_name = f"{detail.first_name} {detail.last_name}".strip()

                                    candidate.identity_mismatch_detected = True
                                    candidate.identity_mismatch_details = {
                                        'mismatch_at': timezone.now().isoformat(),
                                        'original_holder_token': original_token,
                                        'original_holder_name': original_name,
                                        'mismatch_type': 'face_mismatch_override'
                                    }

                                    # Store this session's photo as pending (for admin approval UI)
                                    if snapshot_b64_payload:
                                        candidate.pending_face_b64 = clean_b64
                                        candidate.photo_update_approved = False
                                        logger.info(f"[IdentityPhoto] Unified PAN-collision mismatch: stored pending_face_b64")

                                    # Copy the master registered face so the report can show the comparison
                                    if not candidate.master_face_b64:
                                        from api.deepface_client import df_get_photo_b64
                                        master_b64 = df_get_photo_b64(pan_id)
                                        if master_b64:
                                            candidate.master_face_b64 = master_b64

                                else:
                                    candidate.pan_verified = True
                                    candidate.identity_mismatch_detected = False
                            else:
                                candidate.pan_verified = True
                                candidate.identity_mismatch_detected = False
                        except Exception as e:
                            logger.error(f"[IdentityPhoto] Error verifying against unified DeepFace: {e}")
                            candidate.pan_verified = True
                            candidate.identity_mismatch_detected = False

                    if not mismatch_flagged and not candidate.identity_mismatch_detected:
                        candidate.face_embedding_hash = face_embedding_hash
                    elif not mismatch_flagged:
                        candidate.face_embedding_hash = face_embedding_hash
                    else:
                        # Still persist the hash so refreshes work, but mismatch is flagged
                        candidate.face_embedding_hash = face_embedding_hash

                    # Check if face hash belongs to someone else (different PAN)
                    existing_face_holder = Candidate.objects.filter(
                        face_embedding_hash=face_embedding_hash
                    ).exclude(public_token=public_token).exclude(email=candidate.email).first()
                    if existing_face_holder and existing_face_holder.pan_number:
                        if existing_face_holder.pan_number != candidate.pan_number:
                            logger.warning(f"Registration failed: Face already registered to {existing_face_holder.full_name} with different PAN")
                            return Response({
                                'error': f'This face is already registered to another candidate ({existing_face_holder.full_name}). Each person can only register once.',
                                'duplicate_face': True,
                                'registered_to': existing_face_holder.full_name
                            }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                candidate.save()
                
                # If a mismatch was flagged, log it as an integrity violation so it appears in the screenshots grid
                if getattr(candidate, 'identity_mismatch_detected', False) and snapshot_b64_payload:
                    from .models import InterviewIntegrityLog
                    # Extract raw b64
                    clean_b64_log = snapshot_b64_payload.split(',')[-1] if ',' in snapshot_b64_payload else snapshot_b64_payload
                    # Ensure we don't create duplicate logs
                    if not InterviewIntegrityLog.objects.filter(candidate=candidate, event_type="face_mismatch").exists():
                        b64_data = f"data:image/jpeg;base64,{clean_b64_log}"
                        InterviewIntegrityLog.objects.create(
                            candidate=candidate,
                            event_type="face_mismatch",
                            webcam_screenshot_base64=b64_data
                        )
                
                if resume:
                    from .tasks import extract_resume_text_task
                    extract_resume_text_task.delay(candidate.id)
                    logger.info(f"Triggered resume extraction task for candidate {candidate.id}")
                
                # Lock PAN now that registration is complete
                candidate.pan_locked = True
                # NOTE: link_opened_at is intentionally NOT set here.
                # The 1-hour interview timer only starts when the candidate
                # clicks "Begin Interview" (status -> 'Interview'), which is
                # when the countdown timer appears in the UI.
                candidate.save(update_fields=['pan_locked'])
                    
            except IntegrityError as e:
                error_msg = str(e)
                if 'pan_number' in error_msg.lower() or 'ai_candidates_candidate_pan_number' in error_msg:
                    return Response({
                        'error': 'This PAN number is already registered to another candidate. Each PAN can only be used by one person.',
                        'duplicate': True
                    }, status=status.HTTP_400_BAD_REQUEST)
                logger.error(f"Database integrity error during registration: {error_msg}")
                return Response({
                    'error': 'Registration failed due to a data conflict. Please check your information and try again.',
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'success': True,
                'message': 'Registration details updated successfully',
                'candidate': {
                    'id': candidate.id,
                    'full_name': candidate.full_name,
                    'email': candidate.email,
                    'phone': candidate.phone,
                    'pan_number': candidate.pan_number,
                    'pan_verified': candidate.pan_verified,
                    'has_resume': bool(candidate.resume)
                }
            }, status=status.HTTP_200_OK)

        except Candidate.DoesNotExist:
            return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"CRITICAL ERROR in CandidateRegistrationUpdateView: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProcessAnswerView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    @staticmethod
    def _get_difficulty_instructions(experience_level):
        """Return AI prompt instructions based on candidate experience level."""
        mapping = {
            'fresher': (
                "CANDIDATE EXPERIENCE: Fresher (0 years)\n"
                "DIFFICULTY: EASY. Ask basic, introductory-level questions.\n"
                "- Focus on fundamentals, definitions, and simple concepts.\n"
                "- For coding questions, ask simple problems (e.g., reverse a string, find max in array).\n"
                "- Be encouraging and patient. Don't expect real-world project experience.\n"
                "- Score generously if they show understanding of core concepts."
            ),
            '1-2': (
                "CANDIDATE EXPERIENCE: 1-2 Years (Junior)\n"
                "DIFFICULTY: MODERATE. Ask junior-level technical questions.\n"
                "- Expect familiarity with common tools/frameworks but not deep expertise.\n"
                "- For coding questions, ask moderate problems (e.g., basic algorithms, API usage).\n"
                "- They should be able to describe at least one real project they worked on.\n"
                "- Score fairly — they should know basics well, but gaps in advanced topics are okay."
            ),
            '3-5': (
                "CANDIDATE EXPERIENCE: 3-5 Years (Mid-Level)\n"
                "DIFFICULTY: INTERMEDIATE-HARD. Ask mid-level technical questions.\n"
                "- Expect solid understanding of design patterns, debugging, and system thinking.\n"
                "- For coding questions, ask problems involving data structures, optimization, or edge cases.\n"
                "- They should articulate trade-offs and explain WHY they chose certain approaches.\n"
                "- Score strictly — vague or surface-level answers should get lower scores."
            ),
            '5+': (
                "CANDIDATE EXPERIENCE: 5+ Years (Senior)\n"
                "DIFFICULTY: HARD. Ask senior-level, in-depth questions.\n"
                "- Expect expertise in architecture, scalability, team leadership, and mentoring.\n"
                "- For coding questions, ask complex problems involving system design or performance.\n"
                "- Ask about technical decisions, trade-offs, and how they handled failures.\n"
                "- Score strictly — a senior candidate should demonstrate depth, not just breadth."
            ),
        }
        return mapping.get(experience_level, (
            "No specific experience level set. Use a balanced, mid-level difficulty for questions."
        ))

    def post(self, request):
        candidate_id = request.data.get('candidate_id')
        candidate_token = request.data.get('candidate_token')
        current_question = request.data.get('question')
        answer = request.data.get('answer')
        remaining_questions = request.data.get('remaining_questions', [])
        chat_history = request.data.get('chat_history', [])
        # Track whether this is a silent/skipped answer
        SILENCE_MARKER = "[Candidate remained silent/skipped]"
        is_silent_answer = answer and answer.strip() == SILENCE_MARKER

        logger.debug("ProcessAnswer request received for candidate_id=%s silent=%s", candidate_id, is_silent_answer)
        
        # Fallback if question is missing due to frontend race condition
        if not current_question and chat_history:
            for msg in reversed(chat_history):
                role = msg.get('role') or msg.get('sender')
                if role in ['assistant', 'ai']:
                    current_question = msg.get('content') or msg.get('text')
                    break
        
        if not current_question:
            current_question = "Please introduce yourself and your background."

        if not answer:
             return Response({'error': 'Missing answer'}, status=status.HTTP_400_BAD_REQUEST)

        # Clean speech repetition artifacts from candidate's answer
        answer = clean_repetitive_text(answer)

        # Public caller security: require unguessable token for unauthenticated requests.
        if not request.user.is_authenticated and not candidate_token:
            return Response({'error': 'candidate_token is required for public requests.'}, status=status.HTTP_400_BAD_REQUEST)

        # SERVER-SIDE TIMER ENFORCEMENT: Reject answers after 65 minutes (60 min + 5 min grace)
        INTERVIEW_MAX_SECONDS = 65 * 60

        # 1. Synchronize Turn Number with Frontend
        current_turn_number = request.data.get('turn_number')
        
        candidate_name = "Candidate"
        job_title = "Technical Professional"
        resume_context = "No resume available."
        jd_context = "No job description available."
        experience_level = None
        
        candidate = None
        if candidate_token:
            try:
                candidate = _resolve_public_candidate(candidate_token)
                candidate_id = candidate.id
            except Candidate.DoesNotExist:
                return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        elif candidate_id:
            try:
                if isinstance(candidate_id, str) and not candidate_id.isdigit():
                    return Response({'error': 'Invalid candidate_id'}, status=status.HTTP_400_BAD_REQUEST)
                candidate = Candidate.objects.get(pk=candidate_id)
            except Exception as e:
                logger.debug("Candidate lookup error in ProcessAnswerView: %s", str(e))
                return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

        if candidate:
            candidate_name = candidate.full_name
            job_title = candidate.job_title or job_title
            jd_context = candidate.job_description or jd_context
            experience_level = getattr(candidate, 'experience_level', None)
            if candidate.resume_text:
                resume_context = candidate.resume_text

            # SERVER-SIDE TIMER CHECK: Reject if interview time exceeded
            if candidate.link_opened_at:
                elapsed = (timezone.now() - candidate.link_opened_at).total_seconds()
                if elapsed > INTERVIEW_MAX_SECONDS:
                    return Response({
                        'error': 'Interview time has expired.',
                        'is_exit': True,
                        'feedback': 'Time has expired for this interview.',
                        'refined_next_question': None
                    }, status=status.HTTP_403_FORBIDDEN)

        # Determine the max question count for this interview.
        # For student/practice interviews, respect the custom question_count.
        # For company-created interviews, always use the default (14).
        _is_practice = False
        _max_questions = TOTAL_INTERVIEW_QUESTIONS  # Default: 14
        if candidate and isinstance(candidate.automation_settings, dict):
            _is_practice = candidate.automation_settings.get('is_practice', False)
            if _is_practice:
                custom_qc = candidate.automation_settings.get('question_count')
                if custom_qc and isinstance(custom_qc, int) and 5 <= custom_qc <= 20:
                    _max_questions = custom_qc

        try:
            # --- TOKEN-EFFICIENT CONTEXT BUILDING ---
            # Use structured memory instead of full transcript
            conversation_memory = candidate.conversation_memory if candidate else {}
            
            # Build compact memory context (only ~200 tokens)
            memory_context = ""
            if conversation_memory:
                intro_facts = conversation_memory.get('intro_facts', [])
                skills_mentioned = conversation_memory.get('skills_mentioned', [])
                projects_discussed = conversation_memory.get('projects_discussed', [])
                weak_areas = conversation_memory.get('weak_areas', [])
                
                if intro_facts:
                    memory_context += f"Candidate mentioned: {', '.join(intro_facts[:5])}. "
                if skills_mentioned:
                    memory_context += f"Skills discussed: {', '.join(skills_mentioned[:5])}. "
                if projects_discussed:
                    memory_context += f"Projects: {', '.join(projects_discussed[:3])}. "
                if weak_areas:
                    memory_context += f"Struggled with: {', '.join(weak_areas[:3])}. "
            
            # Build minimal recent history (last 2 turns only for immediate context)
            recent_history = ""
            # RELIABLE TURN COUNTING: Use database-backed state if possible, otherwise count history
            if candidate:
                current_turn_number = candidate.total_questions + 1
            elif not current_turn_number:
                if chat_history:
                    ai_questions_count = sum(1 for h in chat_history if h.get('role') in ('ai', 'assistant') or h.get('sender') in ('ai', 'assistant'))
                    current_turn_number = ai_questions_count + 1
                else:
                    current_turn_number = 1

            if chat_history:
                # Only last 2 exchanges for immediate context
                for h in chat_history[-4:]:
                    role = h.get('role') or h.get('sender', 'unknown')
                    content = (h.get('content') or h.get('text', ''))[:200]  # Truncate each message
                    recent_history += f"{role.upper()}: {content}\n"
            else:
                if not current_turn_number:
                    current_turn_number = 1

            # --- RESUME-AWARE ADAPTIVE QUESTIONING ---
            # Instead of a rigid category sequence, the LLM decides what to ask next
            # based on the candidate's performance, gaps, and unexplored areas.
            has_resume = bool(resume_context and "No resume available" not in resume_context and "Extraction Failed" not in resume_context)
            
            # Build adaptive context: what topics have been covered and how well
            covered_topics = []
            weak_topics = []
            strong_topics = []
            if candidate and isinstance(candidate.interview_summary, list):
                for turn in candidate.interview_summary:
                    q = turn.get('question', '')[:80]
                    s = int(turn.get('score', 5))
                    covered_topics.append(q)
                    if s <= 4:
                        weak_topics.append(q)
                    elif s >= 8:
                        strong_topics.append(q)

            # Determine phase based on turn number (loose guidance, not rigid)
            _coding_start = _max_questions - 1  # Second-to-last turn starts coding
            if current_turn_number == 1:
                phase_guidance = "INTRO PHASE: Ask the candidate to introduce themselves and their background. Keep it warm and conversational."
            elif current_turn_number <= max(3, int(_max_questions * 0.4)):
                phase_guidance = "CORE SKILLS PHASE: Focus on Job Description requirements. Ask about specific technologies, concepts, or methodologies mentioned in the JD."
            elif current_turn_number <= max(5, int(_max_questions * 0.7)):
                phase_guidance = "DEEP DIVE PHASE: Probe deeper based on what the candidate has revealed. If they mentioned a project, ask architecture details. If they claimed a skill, test it with a scenario. Focus on WEAK AREAS if any were identified."
            elif current_turn_number < _coding_start:
                phase_guidance = "SCENARIO & PROBLEM-SOLVING PHASE: Present hypothetical workplace scenarios or system design problems relevant to the role."
            elif current_turn_number == _coding_start:
                phase_guidance = "MANDATORY CODING PHASE: You MUST ask a coding/programming question. The candidate will type their answer. You MUST set requires_code_input to true. Do NOT ask a conversational or theoretical question — it MUST be a 'write a function' or 'write code to solve' type question."
            else:
                phase_guidance = "FINAL EVALUATION PHASE: The candidate has just answered the final question. The interview is now complete. Do NOT ask any further questions. Set 'refined_next_question' to null or an empty string. Focus your feedback purely on evaluating their last answer, without proposing any next steps or saying 'let's try something else/easier'."

            # Build adaptive rules based on turn number
            if current_turn_number >= _max_questions:
                adaptive_rules = """1. Since the interview is complete, do NOT ask any next question or suggest any follow-up topics.
2. Set 'refined_next_question' to null or an empty string.
3. Focus your 'feedback' purely on a 1-sentence polite, human-like reaction evaluating their last answer (e.g., "I understand, coding under time pressure can be challenging." or "Thanks for walking me through that logic.").
4. Do NOT say "let's try something else", "let's move on", "let's try something easier", or make any comments about future questions."""
            else:
                # Determine coding turn range dynamically
                _coding_start = _max_questions - 1  # e.g. turn 13 for 14-question interviews
                adaptive_rules = f"""1. NEVER repeat a topic already covered above.
2. If the candidate has WEAK AREAS, ask a FOLLOW-UP that probes deeper into that weakness (give them a chance to recover).
3. If the candidate is STRONG in an area, skip similar topics and explore UNCOVERED ground instead.
4. {'Use the RESUME to find specific projects, skills, or experiences to ask about.' if has_resume else 'Since no resume is available, derive questions from the Job Description and their verbal responses.'}
5. Each question should be HARDER than the last if the candidate is scoring well (7+), or EASIER if they are struggling (≤4).
6. For turns 1-{_coding_start - 1}: ORAL ONLY — never ask them to write code or type anything.
7. For turns {_coding_start}-{_max_questions}: CODING — You MUST ask a coding question (write a function, solve a problem). You MUST set "requires_code_input": true. This is NON-NEGOTIABLE — do NOT ask a theoretical or conversational question on turns {_coding_start}-{_max_questions}."""

            # Adaptive intelligence prompt section
            adaptive_section = f"""===== ADAPTIVE QUESTIONING INTELLIGENCE =====
Turn: {current_turn_number}/{_max_questions}
Phase: {phase_guidance}

TOPICS ALREADY COVERED ({len(covered_topics)} questions asked so far):
{chr(10).join(f'  - {t}' for t in covered_topics[-6:]) if covered_topics else '  None yet (first question)'}

CANDIDATE WEAK AREAS (scored ≤ 4/10):
{chr(10).join(f'  ⚠️ {t}' for t in weak_topics) if weak_topics else '  None identified yet'}

CANDIDATE STRENGTHS (scored ≥ 8/10):
{chr(10).join(f'  ✓ {t}' for t in strong_topics) if strong_topics else '  None identified yet'}

ADAPTIVE RULES:
{adaptive_rules}
"""

            # --- OPTIMIZED PROMPT (reliable JSON output) ---
            # Pre-compute condensed contexts
            jd_condensed = jd_context[:800] if jd_context else "No JD available"
            resume_condensed = resume_context[:1200] if resume_context else "No resume available"
            
            prompt = f"""You are "Indu", a warm, sharp, and experienced technical interviewer conducting a live interview for the position of {job_title}.
Candidate Name: {candidate_name}

===== EXPERIENCE LEVEL & DIFFICULTY =====
{ProcessAnswerView._get_difficulty_instructions(experience_level)}

===== JOB DESCRIPTION =====
{jd_condensed}

===== RESUME =====
{resume_condensed}

===== CONVERSATION MEMORY =====
{memory_context if memory_context else 'First turn - no memory yet.'}

{adaptive_section}

===== RECENT CONVERSATION =====
{recent_history if recent_history else 'START OF INTERVIEW'}

Current Question: "{current_question}"
Candidate Answer: "{answer}"

===== PERSONALITY & TONE RULES =====
- You are a REAL HUMAN interviewer, NOT a robot. Speak naturally.
- Note: The candidate answer might contain transcription artifacts or mechanical speech repetitions. Ignore them semantically and evaluate the underlying answer without giving any score penalty for repetition.
- NEVER use these banned phrases: "Your explanation was clear and concise", "Great answer", "That's a good point", "Well said". These sound robotic.
- Instead, react SPECIFICALLY to what the candidate actually said. Reference their exact words.
- Keep feedback to 1-2 SHORT sentences max. Don't lecture or summarize their answer back to them.
- Use conversational fillers like "Hmm", "I see", "Got it", "Interesting" occasionally to sound human.

===== SCORING GUIDE (0-10) =====
- 10: Perfect, comprehensive, and accurate answer.
- 8-9: Correct and clear answer, perhaps missing minor detail.
- 6-7: Good attempt, mostly correct but a bit vague or lacks depth.
- 4-5: Weak or slightly incorrect answer, but shows basic effort/knowledge.
- 2-3: Very poor or largely incorrect answer, but they tried.
- 0-1: Silent, "I don't know," or "Skip."
BE GENEROUS: If the candidate shows they understand the core concept, lean towards 6 or 7.

===== SPECIAL TRIGGERS =====
- If candidate says "repeat that", "pardon", "what?", "I don't understand" → Set "is_clarification": true and repeat simpler.
- If candidate says "end", "stop", "finish" → Set "is_exit": true and say goodbye.
- FOR TURNS 1-{_coding_start - 1} (ORAL ONLY): You MUST ask conversational questions. NEVER ask the candidate to "write code", "type a solution", or "submit a script". Your question should be answered entirely via speech.
- For turns {_coding_start}-{_max_questions} (CODING) → Set "requires_code_input": true.
- YOUR NEXT QUESTION MUST BE DIFFERENT from all previously covered topics listed above.

===== RESPOND WITH THIS EXACT JSON FORMAT (no markdown, no extra text) =====
{{
    "is_clarification": false,
    "is_exit": false,
    "feedback": "Your 1-2 sentence HUMAN-LIKE reaction to their answer",
    "refined_next_question": "Your ADAPTIVE next question (based on gaps, weaknesses, and uncovered areas)",
    "requires_code_input": false,
    "score": 0,
    "score_reason": "1-sentence justification for the score"
}}"""

            # Lazy-load LLM client for ProcessAnswerView using key rotation
            from ai_assessments.llm_client import LLMKeyManager
            import time as _time

            # Use least-used key for better load balancing with concurrent interviews
            local_api_key = LLMKeyManager.get_least_used_key()
            local_llm_client = create_llm_client(api_key=local_api_key)

            # --- AUTO MODEL FALLBACK WITH KEY ROTATION ---
            DEEPSEEK_MODEL = get_default_model()
            FALLBACK_MODEL = get_default_model()
            COOLDOWN_SECONDS = 60

            # Check if we're currently in cooldown from a previous rate limit
            if not hasattr(ProcessAnswerView, '_fallback_until'):
                ProcessAnswerView._fallback_until = 0

            if _time.time() < ProcessAnswerView._fallback_until:
                chosen_model = FALLBACK_MODEL
                logger.info(f"Using fallback model {FALLBACK_MODEL} (cooldown active for {int(ProcessAnswerView._fallback_until - _time.time())}s more)")
            else:
                chosen_model = DEEPSEEK_MODEL

            try:
                response = local_llm_client.chat.completions.create(
                    model=chosen_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
            except Exception as model_err:
                error_str = str(model_err).lower()
                if ("rate limit" in error_str or "429" in error_str):
                    # Rotate to next key first
                    LLMKeyManager.rotate_key()
                    rotated_key = LLMKeyManager.get_current_key()
                    local_llm_client = create_llm_client(api_key=rotated_key)

                    if chosen_model == DEEPSEEK_MODEL:
                        ProcessAnswerView._fallback_until = _time.time() + COOLDOWN_SECONDS
                        logger.warning(f"Rate-limited! Cooling down for {COOLDOWN_SECONDS}s")
                    
                    response = local_llm_client.chat.completions.create(
                        model=FALLBACK_MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                        response_format={"type": "json_object"}
                    )
                elif "api_key" in error_str or "authentication" in error_str:
                    # Bad key — rotate and retry once
                    LLMKeyManager.rotate_key()
                    rotated_key = LLMKeyManager.get_current_key()
                    local_llm_client = create_llm_client(api_key=rotated_key)
                    logger.warning(f"Bad API key detected, rotated to next key")
                    response = local_llm_client.chat.completions.create(
                        model=chosen_model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                        response_format={"type": "json_object"}
                    )
                else:
                    raise  # Re-raise non-rate-limit errors
            # --- END MODEL FALLBACK ---

            raw_text = response.choices[0].message.content
            logger.info(f"AI Response (turn {current_turn_number}): {raw_text[:500]}")
            data = extract_json(raw_text)
            
            if not data:
                logger.error(f"Invalid JSON from AI: {raw_text}")
                raise ValueError("AI returned invalid JSON structure")

            # --- SERVER-SIDE LABEL SANITIZER ---
            # Strip any leaked category labels like "JD-Q1:", "RESUME-SKILL-Q2:", "PROJECT-Q1" etc.
            import re
            _label_pattern = re.compile(
                r'\b(?:JD|RESUME[- ]?SKILL|PROJECT|SCENARIO|SYNTAX|INTRO)\b[- ]?Q?\d*[:\.\-—]*\s*',
                re.IGNORECASE
            )
            for field in ('feedback', 'refined_next_question'):
                if data.get(field):
                    data[field] = _label_pattern.sub('', data[field]).strip()
            # -----------------------------------

            # -----------------------------------------------

            # Force code input UI for the last 2 turns to ensure the editor appears.
            # NOTE: current_turn_number is the turn that was JUST ANSWERED.
            # So when current_turn_number is (_max_questions - 2), we are generating the coding question.
            # When current_turn_number is (_max_questions - 1), we are generating the last question.
            _coding_force_turns = [_max_questions - 2, _max_questions - 1]
            if current_turn_number in _coding_force_turns:
                data['requires_code_input'] = True
                # Ensure the AI didn't accidentally set is_exit=True too early
                data['is_exit'] = False

            # FIX: If answer was silent, NEVER allow AI to set is_exit=True.
            # Only the frontend 3-consecutive-silence rule should end the interview.
            # Also, do not count silent turns toward total_questions.
            if is_silent_answer:
                data['is_exit'] = False
                # Track consecutive silences in DB
                consecutive_silence_count = (getattr(candidate, 'conversation_memory', {}) or {}).get('_consecutive_silences', 0) + 1
                if candidate:
                    mem = candidate.conversation_memory or {}
                    mem['_consecutive_silences'] = consecutive_silence_count
                    candidate.conversation_memory = mem
                    # Save only conversation_memory (do NOT increment total_questions)
                    try:
                        candidate.save(update_fields=['conversation_memory'])
                    except Exception:
                        pass
                logger.info(f"[Silence] Candidate {getattr(candidate, 'id', '?')} silent answer #{consecutive_silence_count}/3 — is_exit suppressed.")

                # Backend safety: end after 3 consecutive silences (mirrors frontend rule)
                if consecutive_silence_count >= 3:
                    data['is_exit'] = True
                    data['refined_next_question'] = None
                    data['feedback'] = "We haven't been able to hear you for a while. The interview will now be concluded. Thank you for your time."
                    logger.warning(f"[Silence] 3 consecutive silences for candidate {getattr(candidate, 'id', '?')}. Forcing is_exit=True.")
            else:
                # Non-silent answer — reset consecutive silence counter
                if candidate:
                    mem = candidate.conversation_memory or {}
                    if mem.get('_consecutive_silences', 0) > 0:
                        mem['_consecutive_silences'] = 0
                        try:
                            candidate.save(update_fields=['conversation_memory'])
                        except Exception:
                            pass

            # If turn >= 15, force exit
            if current_turn_number >= 15:
                data['is_exit'] = True
                data['refined_next_question'] = "Thank you for your time. The interview is now complete."
            # ------------------------------------
            # -----------------------------------------------

            # Scoring Update
            # FIX: Silent answers do NOT increment total_questions (turn counter).
            # This prevents the turn number from advancing on silence, which was
            # causing the interview to reach turn 15 prematurely and force-exit.
            is_clarification = data.get('is_clarification', False)
            if candidate and data.get('score') is not None and not is_clarification and not is_silent_answer:
                 try:
                    # Update score atomically to prevent race conditions
                    q_score = int(data.get('score', 0))
                    from django.db.models import F
                    Candidate.objects.filter(pk=candidate.id).update(
                        score=F('score') + q_score,
                        total_questions=F('total_questions') + 1
                    )
                    # Refresh to get updated values
                    candidate.refresh_from_db()
                    # Store per-question summary for "Details" button
                    if not isinstance(candidate.interview_summary, list):
                        candidate.interview_summary = []

                    candidate.interview_summary.append({
                        "question": current_question,
                        "answer": answer,
                        "feedback": data.get('feedback', ''),
                        "score": q_score,
                        "reason": data.get('score_reason', 'No reasoning provided.')
                    })

                    # --- UPDATE CONVERSATION MEMORY ---
                    # Extract structured facts from this turn for future context
                    memory = candidate.conversation_memory or {}
                    
                    # Initialize memory structure
                    if not memory:
                        memory = {
                            'intro_facts': [],
                            'skills_mentioned': [],
                            'projects_discussed': [],
                            'weak_areas': []
                        }
                    
                    # Extract facts based on turn category. target_category may be undefined
                    # in some code paths, so guard with locals().
                    target_category_upper = (locals().get('target_category') or "").upper()
                    
                    if target_category_upper == "INTRO" and answer:
                        # Extract key facts from intro (experience, company, role)
                        intro_facts = memory.get('intro_facts', [])
                        # Simple extraction: look for years, company names, roles
                        import re
                        years_match = re.search(r'(\d+)\+?\s*(years?|yrs?)', answer, re.I)
                        if years_match:
                            intro_facts.append(f"{years_match.group(0)} experience")
                        # Store first 50 chars as key intro fact
                        if len(intro_facts) < 5:
                            intro_facts.append(answer[:80].strip())
                        memory['intro_facts'] = list(set(intro_facts))[:5]
                    
                    elif "RESUME-SKILL" in target_category_upper and answer:
                        # Track skills mentioned
                        skills = memory.get('skills_mentioned', [])
                        # Extract skill names from answer (simple: first 30 chars)
                        skills.append(answer[:50].strip())
                        memory['skills_mentioned'] = list(set(skills))[:5]
                    
                    elif "PROJECT" in target_category_upper and answer:
                        # Track projects discussed
                        projects = memory.get('projects_discussed', [])
                        projects.append(answer[:60].strip())
                        memory['projects_discussed'] = list(set(projects))[:3]
                    
                    # Track weak areas based on low scores
                    if q_score <= 4:
                        weak = memory.get('weak_areas', [])
                        weak.append(current_question[:50].strip())
                        memory['weak_areas'] = list(set(weak))[:3]
                    
                    candidate.conversation_memory = memory

                    candidate.save(update_fields=['interview_summary', 'conversation_memory'])
                    logger.info(
                        f"[InterviewSummary] Saved turn {current_turn_number} for candidate {candidate.id}: "
                        f"q='{current_question[:60]}...' score={q_score} "
                        f"summary_len={len(candidate.interview_summary)}"
                    )
                 except Exception as save_err:
                    logger.exception(
                        f"[InterviewSummary] FAILED to save turn for candidate "
                        f"{getattr(candidate, 'id', '?')}: {save_err}"
                    )

            # Also save clarification turns to interview_summary (score=0, no scoring impact)
            # so the transcript always shows what happened, even if the candidate only asked
            # for repeats/clarifications before exiting.
            elif candidate and is_clarification:
                try:
                    candidate.refresh_from_db()
                    if not isinstance(candidate.interview_summary, list):
                        candidate.interview_summary = []

                    candidate.interview_summary.append({
                        "question": current_question,
                        "answer": answer,
                        "feedback": data.get('feedback', ''),
                        "score": 0,
                        "reason": "Clarification request — not scored.",
                        "is_clarification": True
                    })
                    candidate.save(update_fields=['interview_summary'])
                    logger.info(
                        f"[InterviewSummary] Saved clarification turn for candidate {candidate.id}: "
                        f"q='{current_question[:60]}...' answer='{answer[:60]}...'"
                    )
                except Exception as save_err:
                    logger.exception(
                        f"[InterviewSummary] FAILED to save clarification turn for candidate "
                        f"{getattr(candidate, 'id', '?')}: {save_err}"
                    )

            return Response({**data, 'server_turn': current_turn_number}, status=status.HTTP_200_OK)

        except Exception as e:
            error_msg = str(e)
            is_rate_limit = "rate limit" in error_msg.lower() or "429" in error_msg
            is_connection = "connection" in error_msg.lower() or "timeout" in error_msg.lower()
            if is_rate_limit or is_connection:
                logger.warning("Retryable ProcessAnswer error: %s", error_msg)
            else:
                logger.exception("ProcessAnswer failure")
            
            # Treat connection errors as temporary (retryable) just like rate limits
            if is_rate_limit or is_connection:
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
                msg = "Indu is taking a moment to think (AI Busy). Retrying automatically..."
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                msg = "AI is temporarily unavailable. Please try again or click the microphone to resume."

            return Response({"error": msg, "retryable": (is_rate_limit or is_connection)}, status=status_code)


class TTSView(APIView):
    """
    Text-to-Speech endpoint using Edge TTS.
    POST {"text": "Hello!", "candidate_token": "uuid"} → returns audio/mpeg binary response.
    Requires a valid candidate token to prevent abuse.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        text = request.data.get('text', '').strip()
        if not text:
            return Response({"error": "Missing 'text' field"}, status=status.HTTP_400_BAD_REQUEST)

        # Require candidate token OR authenticated user to prevent abuse
        candidate_token = request.data.get('candidate_token') or request.data.get('token')
        if not request.user.is_authenticated and not candidate_token:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if candidate_token:
            try:
                _resolve_public_candidate(candidate_token)
            except Candidate.DoesNotExist:
                return Response({"error": "Invalid candidate token"}, status=status.HTTP_403_FORBIDDEN)

        # Safety: limit text length to prevent extremely long synthesis
        if len(text) > 1500:
            text = text[:1500]

        try:
            from .tts_engine import get_tts_engine
            import asyncio
            engine = get_tts_engine()
            # edge-tts is better handled via asyncio.run for sync views
            wav_bytes = asyncio.run(engine.synthesize(text))

            if not wav_bytes:
                return Response({"error": "Synthesis produced empty audio"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            from django.http import HttpResponse
            # Edge-TTS produces mp3 by default, we'll return as audio/mpeg
            response = HttpResponse(wav_bytes, content_type='audio/mpeg')
            response['Content-Length'] = len(wav_bytes)
            response['Cache-Control'] = 'no-cache'
            return response

        except Exception as e:
            logger.error(f"TTS Error: {str(e)}")
            return Response({"error": f"TTS synthesis failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CandidateTimelineView(APIView):
    """
    Fetches the interview activity logs for a specific candidate.
    Only returns logs relevant to the CURRENT interview session (after link_opened_at).
    """
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
            
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile:
                return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

            user_role = (user_profile.role or '').strip().lower()
            if user_role not in ['company_admin', 'hr_manager', 'hr', 'application_admin', 'recruiter', 'hiring_manager', 'admin']:
                return Response({'error': 'Unauthorized role access.'}, status=status.HTTP_403_FORBIDDEN)

            # Permission check: ensure user belongs to same company
            if not request.user.is_superuser and user_profile.company and candidate.company_id != user_profile.company_id:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

            # Check hierarchy scope
            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)
            if not request.user.is_superuser and scoped_ids is not None and candidate.user_profile_id not in scoped_ids:
                return Response({'error': 'Unauthorized: candidate is outside your reporting scope.'}, status=status.HTTP_403_FORBIDDEN)

            logs = []

            # Use link_opened_at as the session start boundary.
            # Use completed_at as the session end boundary (if available).
            # Only show logs from this interview session.
            session_start = candidate.link_opened_at
            session_end = candidate.completed_at

            # 1. Key interview timestamps
            if candidate.link_opened_at:
                from django.utils import timezone as tz
                local_opened = tz.localtime(candidate.link_opened_at)
                logs.append({
                    'id': 'ts_link_opened',
                    'event_type': 'LINK_OPENED',
                    'status': 'INFO',
                    'phase': 'INTERVIEW',
                    'batch_id': candidate.batch_id,
                    'message': 'Candidate opened the interview link.',
                    'details': {},
                    'timestamp': candidate.link_opened_at.isoformat(),
                    'timestamp_formatted': local_opened.strftime('%B %d, %Y at %I:%M %p'),
                })
            if candidate.completed_at:
                local_completed = tz.localtime(candidate.completed_at)
                logs.append({
                    'id': 'ts_completed',
                    'event_type': 'INTERVIEW_COMPLETED',
                    'status': 'SUCCESS',
                    'phase': 'INTERVIEW',
                    'batch_id': candidate.batch_id,
                    'message': f'Interview completed. Status: {candidate.status}. Score: {candidate.score}.',
                    'details': {'status': candidate.status, 'score': candidate.score},
                    'timestamp': candidate.completed_at.isoformat(),
                    'timestamp_formatted': local_completed.strftime('%B %d, %Y at %I:%M %p'),
                })

            # 2. Integrity events
            integrity_qs = candidate.integrity_logs.all().order_by('timestamp')
            
            # Send first 8 with full base64 for immediate display, rest with just metadata for lazy loading
            INLINE_LIMIT = 8
            integrity_count = 0
            for ilog in integrity_qs:
                integrity_count += 1
                local_ts = tz.localtime(ilog.timestamp) if ilog.timestamp else None
                log_entry = {
                    'id': f'integrity_{ilog.id}',
                    'event_type': ilog.event_type.upper(),
                    'status': 'WARNING',
                    'phase': 'INTEGRITY',
                    'batch_id': candidate.batch_id,
                    'message': f'Integrity event: {ilog.event_type.replace("_", " ").title()}',
                    'details': {},
                    'timestamp': ilog.timestamp.isoformat() if ilog.timestamp else None,
                    'timestamp_formatted': local_ts.strftime('%B %d, %Y at %I:%M %p') if local_ts else '',
                    'has_screenshot': bool(ilog.screenshot_base64),
                    'has_webcam_screenshot': bool(ilog.webcam_screenshot_base64),
                    'screenshot_id': ilog.id,
                }
                # Include inline base64 for first few so page renders immediately
                if integrity_count <= INLINE_LIMIT:
                    log_entry['screenshot_base64'] = ilog.screenshot_base64
                    log_entry['webcam_screenshot_base64'] = ilog.webcam_screenshot_base64
                else:
                    log_entry['screenshot_base64'] = None
                    log_entry['webcam_screenshot_base64'] = None
                logs.append(log_entry)

            # 3. PipelineLog entries
            pipeline_qs = candidate.pipeline_logs.all().order_by('timestamp')
            serializer = PipelineLogSerializer(pipeline_qs, many=True)
            logs.extend(serializer.data)

            # Sort all logs by timestamp
            logs.sort(key=lambda x: x.get('timestamp') or '')

            return Response(logs, status=status.HTTP_200_OK)

        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

class StandaloneTimelineView(APIView):
    """
    Dynamically generates pipeline logs for a manual StandaloneResumeScreening.
    """
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        from .models import StandaloneResumeScreening
        from django.utils import timezone as tz
        try:
            standalone = StandaloneResumeScreening.objects.get(pk=pk)
            
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile:
                return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

            # Permission check: ensure user belongs to same company
            if not request.user.is_superuser and user_profile.company and standalone.company_id != user_profile.company_id:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

            # Check hierarchy scope
            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)
            if not request.user.is_superuser and scoped_ids is not None and standalone.user_profile_id not in scoped_ids:
                return Response({'error': 'Unauthorized: candidate is outside your reporting scope.'}, status=status.HTTP_403_FORBIDDEN)

            logs = []
            
            # 1. Upload Log
            if standalone.created_at:
                local_created = tz.localtime(standalone.created_at)
                logs.append({
                    'id': f'ts_upload_{standalone.id}',
                    'event_type': 'RESUME_UPLOADED',
                    'status': 'INFO',
                    'phase': 'RESUME',
                    'batch_id': standalone.batch_id,
                    'message': 'Manual resume successfully uploaded for processing.',
                    'details': {},
                    'timestamp': standalone.created_at.isoformat(),
                    'timestamp_formatted': local_created.strftime('%B %d, %Y at %I:%M %p'),
                })
            
            # 2. Status Log
            if standalone.status != 'New':
                logs.append({
                    'id': f'ts_status_{standalone.id}',
                    'event_type': 'SCREENING_COMPLETE',
                    'status': 'SUCCESS' if standalone.status == 'Resume Passed' else ('ERROR' if standalone.status == 'Extraction Failed' else 'WARNING'),
                    'phase': 'RESUME',
                    'batch_id': standalone.batch_id,
                    'message': f"Resume screening complete. Score: {standalone.resume_score}%. Status: {standalone.status}",
                    'details': {'summary': standalone.resume_summary},
                    'timestamp': standalone.created_at.isoformat(), # approximation since we don't track update_at
                    'timestamp_formatted': local_created.strftime('%B %d, %Y at %I:%M %p'),
                })

            return Response(logs, status=status.HTTP_200_OK)
            
        except StandaloneResumeScreening.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class IntegrityScreenshotView(APIView):
    """
    Serves a single integrity screenshot image by log ID.
    Returns the base64 image data for lazy loading on the frontend.
    Query param: ?type=webcam (default) or ?type=screen
    """
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, log_id):
        model_type = request.query_params.get('model', 'interview')

        if model_type == 'assessment':
            try:
                from ai_assessments.models import AIAssessmentIntegrityScreenshot
                snap = AIAssessmentIntegrityScreenshot.objects.select_related('submission__assessment').get(pk=log_id)
                
                user_profile = getattr(request.user, 'profile', None)
                if not user_profile:
                    return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

                user_role = (user_profile.role or '').strip().lower()
                if user_role not in ['company_admin', 'hr_manager', 'hr', 'application_admin', 'recruiter', 'hiring_manager', 'admin']:
                    return Response({'error': 'Unauthorized role access.'}, status=status.HTTP_403_FORBIDDEN)

                # Permission check: ensure user belongs to same company
                if not request.user.is_superuser and user_profile.company and snap.submission.assessment.company_id != user_profile.company_id:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

                img_type = request.query_params.get('type', 'webcam')
                img_field = snap.screenshot if img_type == 'screen' else snap.webcam_screenshot

                if not img_field:
                    return Response({'image': None}, status=status.HTTP_200_OK)

                # Read from disk and base64 encode
                try:
                    import base64
                    with img_field.open('rb') as f:
                        data = base64.b64encode(f.read()).decode('utf-8')
                        data = f'data:image/jpeg;base64,{data}'
                    return Response({'image': data}, status=status.HTTP_200_OK)
                except Exception as file_err:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error reading and encoding AIAssessmentIntegrityScreenshot {snap.id}: {file_err}")
                    return Response({'error': f'Failed to read screenshot file: {str(file_err)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except AIAssessmentIntegrityScreenshot.DoesNotExist:
                return Response({'error': 'Screenshot not found'}, status=status.HTTP_404_NOT_FOUND)

        # Default fallback to interview log / interview candidate flow
        try:
            ilog = InterviewIntegrityLog.objects.select_related('candidate').get(pk=log_id)
            
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile:
                return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

            user_role = (user_profile.role or '').strip().lower()
            if user_role not in ['company_admin', 'hr_manager', 'hr', 'application_admin', 'recruiter', 'hiring_manager', 'admin']:
                return Response({'error': 'Unauthorized role access.'}, status=status.HTTP_403_FORBIDDEN)

            # Permission check
            if not request.user.is_superuser and user_profile.company and ilog.candidate.company_id != user_profile.company_id:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

            # Check hierarchy scope
            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)
            if not request.user.is_superuser and scoped_ids is not None and ilog.candidate.user_profile_id not in scoped_ids:
                return Response({'error': 'Unauthorized: candidate is outside your reporting scope.'}, status=status.HTTP_403_FORBIDDEN)

            img_type = request.query_params.get('type', 'webcam')
            if img_type == 'screen':
                data = ilog.screenshot_base64
            else:
                data = ilog.webcam_screenshot_base64

            if not data:
                return Response({'image': None}, status=status.HTTP_200_OK)

            # Return as proper data URI if not already prefixed
            if not data.startswith('data:'):
                data = f'data:image/jpeg;base64,{data}'

            return Response({'image': data}, status=status.HTTP_200_OK)
        except InterviewIntegrityLog.DoesNotExist:
            try:
                from ai_assessments.models import AIAssessmentIntegrityScreenshot
                snap = AIAssessmentIntegrityScreenshot.objects.select_related('submission__assessment').get(pk=log_id)
                
                user_profile = getattr(request.user, 'profile', None)
                if not user_profile:
                    return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

                user_role = (user_profile.role or '').strip().lower()
                if user_role not in ['company_admin', 'hr_manager', 'hr', 'application_admin', 'recruiter', 'hiring_manager', 'admin']:
                    return Response({'error': 'Unauthorized role access.'}, status=status.HTTP_403_FORBIDDEN)

                # Permission check: ensure user belongs to same company
                if not request.user.is_superuser and user_profile.company and snap.submission.assessment.company_id != user_profile.company_id:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

                img_type = request.query_params.get('type', 'webcam')
                img_field = snap.screenshot if img_type == 'screen' else snap.webcam_screenshot

                if not img_field:
                    return Response({'image': None}, status=status.HTTP_200_OK)

                # Read from disk and base64 encode
                try:
                    import base64
                    with img_field.open('rb') as f:
                        data = base64.b64encode(f.read()).decode('utf-8')
                        data = f'data:image/jpeg;base64,{data}'
                    return Response({'image': data}, status=status.HTTP_200_OK)
                except Exception as file_err:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error reading and encoding AIAssessmentIntegrityScreenshot {snap.id}: {file_err}")
                    return Response({'error': f'Failed to read screenshot file: {str(file_err)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except AIAssessmentIntegrityScreenshot.DoesNotExist:
                return Response({'error': 'Screenshot not found'}, status=status.HTTP_404_NOT_FOUND)


class LatestActiveBatchView(APIView):
    """
    Allows the frontend to recover the most recent batch ID if the page was refreshed
    before the ID could be saved to local state.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        # Look for candidates created in the last 15 minutes that are still 'New'
        threshold_time = timezone.now() - timedelta(minutes=15)
        user_profile = getattr(request.user, 'userprofile', None)

        candidates = Candidate.objects.filter(
            status='New',
            created_at__gte=threshold_time
        ).exclude(batch_id__isnull=True).exclude(batch_id='')

        if user_profile:
            candidates = candidates.filter(user_profile=user_profile)

        latest_candidate = candidates.order_by('-created_at').first()

        if latest_candidate:
            return Response({"batch_id": latest_candidate.batch_id}, status=status.HTTP_200_OK)

        return Response({"batch_id": None}, status=status.HTTP_200_OK)


class CandidateReportDownloadView(APIView):
    """
    Generates a comprehensive PDF report for an AI interview session.
    Includes candidate details, identity verification photo, full transcript,
    and integrity violation snapshots.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
            
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile:
                return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

            user_role = (user_profile.role or '').strip().lower()
            if user_role not in ['company_admin', 'hr_manager', 'hr', 'application_admin', 'recruiter', 'hiring_manager', 'admin']:
                return Response({'error': 'Unauthorized role access.'}, status=status.HTTP_403_FORBIDDEN)

            # Ensure user belongs to the same company or is a superuser
            if not request.user.is_superuser and user_profile.company and candidate.company_id != user_profile.company_id:
                return Response({'error': 'Unauthorized access to this candidate report.'}, status=status.HTTP_403_FORBIDDEN)

            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)
            if not request.user.is_superuser and scoped_ids is not None and candidate.user_profile_id not in scoped_ids:
                return Response({'error': 'Unauthorized access to this candidate report.'}, status=status.HTTP_403_FORBIDDEN)

            # Generate PDF in memory
            buffer = io.BytesIO()
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
            from reportlab.lib.units import inch
            import base64

            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            styles = getSampleStyleSheet()
            elements = []

            # 1. Header & Title
            header_style = ParagraphStyle(
                'HeaderStyle', 
                parent=styles['Heading1'], 
                fontSize=26, 
                spaceAfter=20, 
                textColor=colors.HexColor("#4338ca"),
                alignment=1 # Center
            )
            elements.append(Paragraph("VerifiHireAI — Interview Report", header_style))
            elements.append(Paragraph(f"Candidate: {candidate.full_name}", styles['Heading2']))
            elements.append(Spacer(1, 15))

            # Define custom styles if not already present
            if 'Small' not in styles:
                styles.add(ParagraphStyle(
                    name='Small',
                    parent=styles['Normal'],
                    fontSize=8,
                    leading=10,
                    textColor=colors.grey
                ))
            if 'Italic' not in styles:
                styles.add(ParagraphStyle(
                    name='Italic',
                    parent=styles['Normal'],
                    fontName='Helvetica-Oblique'
                ))

            # 2. Candidate Information (Photo on Left, Details on Right)
            elements.append(Paragraph("Candidate Information", styles['Heading3']))
            
            # Identity Verification (Face Registration)
            # Main candidate header photo: prefer the DB-stored registered_face_b64
            # (always the latest verified face), then fall back to DeepFace, then to a
            # webcam screenshot from integrity logs.
            person_img_path = None
            fallback_img_data = None

            # 1. DB-stored face (most reliable).
            if getattr(candidate, 'registered_face_b64', None):
                try:
                    import base64 as b64_mod
                    fallback_img_data = b64_mod.b64decode(candidate.registered_face_b64)
                except Exception:
                    pass

            # 2. DeepFace on-disk face_0.jpg (PAN first, then token).
            if not fallback_img_data:
                deepface_data_dir = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'deepface', 'data', 'registered_faces'))
                path_options = []
                if candidate.pan_number:
                    pan_id = str(candidate.pan_number).strip().lower()
                    path_options.append(os.path.join(deepface_data_dir, pan_id, "face_0.jpg"))
                if candidate.public_token:
                    token_id = str(candidate.public_token).lower()
                    path_options.append(os.path.join(deepface_data_dir, token_id, "face_0.jpg"))

                for p in path_options:
                    if os.path.exists(p):
                        person_img_path = p
                        break

            # Fallback: Use first webcam screenshot from integrity logs
            if not person_img_path and not fallback_img_data:
                first_log = candidate.integrity_logs.filter(webcam_screenshot_base64__isnull=False).order_by('timestamp').first()
                if first_log and first_log.webcam_screenshot_base64:
                    try:
                        b64 = first_log.webcam_screenshot_base64.split(',')[-1]
                        fallback_img_data = base64.b64decode(b64)
                    except:
                        pass

            # Left side: Image
            if person_img_path:
                try:
                    img_elem = RLImage(person_img_path, width=2.0*inch, height=1.5*inch)
                except:
                    img_elem = Paragraph("[Error loading photo]", styles['Italic'])
            elif fallback_img_data:
                try:
                    img_io = io.BytesIO(fallback_img_data)
                    img_elem = RLImage(img_io, width=2.0*inch, height=1.5*inch)
                except:
                    img_elem = Paragraph("[Error loading photo]", styles['Italic'])
            else:
                img_elem = Paragraph("<i>No candidate photo available.</i>", styles['Normal'])

            # Score & Penalty Calculation
            base_score_pct = candidate.score_percentage
            
            integrity_obj = getattr(candidate, 'integrity', None)
            integrity_score = integrity_obj.integrity_score if integrity_obj else 100.0
            
            # No penalty applied to raw score — integrity only affects status (On-Hold if < 75%)
            final_performance_pct = round(base_score_pct, 1)

            # Identity Status Logic
            identity_status = "Verified \u2713"
            ident_status_color = colors.HexColor("#16a34a") # Green
            
            mismatch_info = getattr(candidate, 'identity_mismatch_details', {}) or {}
            
            if getattr(candidate, 'photo_update_approved', False):
                identity_status = "MISMATCH (APPROVED & UPDATED) \u2713"
                ident_status_color = colors.HexColor("#16a34a")
            elif getattr(candidate, 'identity_mismatch_detected', False):
                identity_status = "MISMATCH DETECTED \u2717"
                ident_status_color = colors.HexColor("#dc2626")

            match_score_str = "100%"
            score_val = mismatch_info.get('face_match_score')
            if score_val is not None:
                if score_val <= 1.0:
                    match_score_str = f"{min(100.0, round(score_val * 100.0, 2))}%"
                else:
                    match_score_str = f"{min(100.0, round(score_val, 2))}%"
            elif getattr(candidate, 'identity_mismatch_detected', False):
                match_score_str = "Mismatch \u2717"

            # Localize times to timezone
            from django.utils import timezone
            local_start = timezone.localtime(candidate.link_opened_at) if candidate.link_opened_at else None
            local_end = timezone.localtime(candidate.completed_at) if candidate.completed_at else None

            # Calculate duration
            duration_str = "N/A"
            if candidate.link_opened_at and candidate.completed_at:
                duration_delta = candidate.completed_at - candidate.link_opened_at
                total_seconds = int(duration_delta.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                if hours > 0:
                    duration_str = f"{hours}h {minutes}m {seconds}s"
                else:
                    duration_str = f"{minutes}m {seconds}s"

            # Right side: Summary Table
            info_data = [
                ["Full Name", candidate.full_name],
                ["Email", candidate.email],
                ["Phone", candidate.phone or "N/A"],
                ["PAN Number", candidate.pan_number or "N/A"],
                ["PAN Verified", "Yes \u2713" if candidate.pan_verified else "No \u2717"],
                ["Identity Status", identity_status],
                ["Face Match Score", match_score_str],
                ["Job Title", candidate.job_title or "N/A"],
                ["Interview Score", f"{candidate.score} / {total_possible_marks}"],
                ["Integrity Score", f"{integrity_score:.1f}%"],
                ["Final Performance", f"{final_performance_pct}%"],
                ["Status", candidate.status],
                ["Start Time", local_start.strftime('%B %d, %Y %I:%M %p') if local_start else 'N/A'],
                ["End Time", local_end.strftime('%B %d, %Y %I:%M %p') if local_end else 'Incomplete'],
                ["Total Duration", duration_str],
            ]
            
            summary_table = Table(info_data, colWidths=[1.3*inch, 2.9*inch])
            
            base_styles = [
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f8fafc")),
                ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#475569")),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ('PADDING', (0,0), (-1,-1), 6),
            ]
            
            for i, row in enumerate(info_data):
                if row[0] == 'Identity Status':
                    base_styles.append(('TEXTCOLOR', (1,i), (1,i), ident_status_color))

            summary_table.setStyle(TableStyle(base_styles))

            # Combine in a layout table
            layout_table = Table([[img_elem, summary_table]], colWidths=[2.2*inch, 4.3*inch])
            layout_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (0,0), (0,0), 'LEFT'),
                ('ALIGN', (1,0), (1,0), 'LEFT'),
            ]))
            elements.append(layout_table)
            elements.append(Spacer(1, 20))

            # 2.5 Identity Documents Section - PAN Card
            if candidate.pan_photo:
                elements.append(Paragraph("Identity Documents", styles['Heading3']))
                elements.append(Spacer(1, 10))
                
                # PAN Card Image
                try:
                    pan_img_path = candidate.pan_photo.path
                    if os.path.exists(pan_img_path):
                        pan_img_elem = RLImage(pan_img_path, width=3.0*inch, height=2.0*inch)
                        pan_caption = f"PAN Card: {candidate.pan_number or 'N/A'} (Verified: {'Yes' if candidate.pan_verified else 'No'})"
                        
                        pan_table = Table([
                            [pan_img_elem],
                            [Paragraph(pan_caption, styles['Small'])]
                        ], colWidths=[3.0*inch])
                        pan_table.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ]))
                        elements.append(pan_table)
                    else:
                        elements.append(Paragraph("<i>PAN card image file not found on server.</i>", styles['Normal']))
                except Exception as pan_error:
                    elements.append(Paragraph(f"<i>Error loading PAN card image: {str(pan_error)}</i>", styles['Italic']))
                
                elements.append(Spacer(1, 25))

            # 3. Interview Transcript
            elements.append(Paragraph("Conversation Transcript", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            if isinstance(candidate.interview_summary, list) and candidate.interview_summary:
                for i, turn in enumerate(candidate.interview_summary, 1):
                    # Question Header with background
                    q_header_style = ParagraphStyle(
                        'QHeader',
                        parent=styles['Heading4'],
                        fontSize=11,
                        textColor=colors.HexColor("#4338ca"),
                        spaceBefore=15,
                        spaceAfter=8,
                        backColor=colors.HexColor("#f8fafc"),
                        borderPadding=8,
                        borderWidth=1,
                        borderColor=colors.HexColor("#e2e8f0"),
                        borderRadius=5
                    )
                    elements.append(Paragraph(f"Question #{i}", q_header_style))
                    
                    import html
                    q_escaped = html.escape(turn.get('question', 'N/A')).replace('\n', '<br/>')
                    ans_escaped = html.escape(turn.get('answer', 'N/A')).replace('\n', '<br/>')
                    fb_escaped = html.escape(turn.get('feedback', 'No feedback provided.')).replace('\n', '<br/>')
                    reason_escaped = html.escape(turn.get('reason', '')).replace('\n', '<br/>')

                    # Question text
                    elements.append(Paragraph("<b>Question:</b>", styles['Normal']))
                    elements.append(Paragraph(q_escaped, styles['Normal']))
                    elements.append(Spacer(1, 8))
                    
                    # Answer
                    elements.append(Paragraph("<b>Candidate Answer:</b>", styles['Normal']))
                    elements.append(Paragraph(ans_escaped, styles['Normal']))
                    elements.append(Spacer(1, 8))
                    
                    # AI Analysis
                    elements.append(Paragraph("<b>AI Analysis:</b>", styles['Normal']))
                    elements.append(Paragraph(f"<i>{fb_escaped}</i>", styles['Normal']))
                    elements.append(Spacer(1, 8))
                    
                    # Score with color coding
                    score = turn.get('score', 0)
                    score_color = colors.darkgreen if score >= 7 else (colors.darkorange if score >= 4 else colors.red)
                    score_style = ParagraphStyle(
                        'ScoreStyle',
                        parent=styles['Normal'],
                        fontSize=10,
                        textColor=score_color,
                        spaceBefore=5,
                        spaceAfter=15
                    )
                    elements.append(Paragraph(f"<b>Score: {score}/10</b> — {reason_escaped}", score_style))
                    
                    elements.append(Paragraph('<hr color="#e2e8f0" thickness="1"/>', styles['Normal']))
                    elements.append(Spacer(1, 12))
            else:
                elements.append(Paragraph("No interview transcript data recorded for this session.", styles['Italic']))

            # 4. Integrity Violations & Snapshots
            elements.append(PageBreak())
            elements.append(Paragraph("Proctoring & Integrity Evidence", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            logs = candidate.integrity_logs.all().order_by('timestamp')
            all_images = []
            
            for log in logs:
                # Process Webcam Snapshot
                if log.webcam_screenshot_base64:
                    try:
                        b64 = log.webcam_screenshot_base64.split(',')[-1]
                        img_data = base64.b64decode(b64)
                        img_io = io.BytesIO(img_data)
                        rl_img = RLImage(img_io, width=1.5*inch, height=1.1*inch)
                        all_images.append((rl_img, f"Webcam - {log.event_type.replace('_', ' ').title()} ({timezone.localtime(log.timestamp).strftime('%H:%M:%S')})"))
                    except Exception as webcam_err:
                        logger.warning(f"[PDFReport] Failed to load webcam screenshot for log {log.id}: {webcam_err}")
                
                # Process Desktop Snapshot
                if log.screenshot_base64:
                    try:
                        b64 = log.screenshot_base64.split(',')[-1]
                        img_data = base64.b64decode(b64)
                        img_io = io.BytesIO(img_data)
                        rl_img = RLImage(img_io, width=1.5*inch, height=1.1*inch)
                        all_images.append((rl_img, f"Desktop - {log.event_type.replace('_', ' ').title()} ({timezone.localtime(log.timestamp).strftime('%H:%M:%S')})"))
                    except Exception as desktop_err:
                        logger.warning(f"[PDFReport] Failed to load desktop screenshot for log {log.id}: {desktop_err}")

            # Synthetically inject Face Mismatch photo into the grid if it was flagged but missing from DB logs
            if getattr(candidate, 'identity_mismatch_detected', False) or getattr(candidate, 'photo_update_approved', False):
                has_mismatch = any('Face Mismatch' in caption for _, caption in all_images)
                if not has_mismatch and getattr(candidate, 'pending_face_b64', None):
                    try:
                        b64 = candidate.pending_face_b64.split(',')[-1]
                        img_data = base64.b64decode(b64)
                        img_io = io.BytesIO(img_data)
                        rl_img = RLImage(img_io, width=1.5*inch, height=1.1*inch)
                        # We don't have the exact timestamp, use creation time or a generic one
                        mismatch_time = timezone.localtime(candidate.created_at).strftime('%H:%M:%S') if candidate.created_at else "Initial"
                        all_images.insert(0, (rl_img, f"Face Mismatch ({mismatch_time})"))
                    except Exception as e:
                        logger.warning(f"[PDFReport] Failed to inject synthetic face mismatch image: {e}")

            if all_images:
                elements.append(Paragraph(f"Total violations flagged: {len(all_images)}", styles['Normal']))
                elements.append(Spacer(1, 15))
                
                # Display images in 4-per-row grid
                img_grid = []
                row = []
                for img, caption in all_images:
                    # Each cell will contain both the image and the caption text
                    row.append([img, Paragraph(caption, styles['Small'])])
                    if len(row) == 4:
                        img_grid.append(row)
                        row = []
                if row:  # Add remaining images
                    while len(row) < 4:
                        row.append("")
                    img_grid.append(row)
                
                for grid_row in img_grid:
                    # Passing [grid_row] creates a single table row with 4 columns
                    t_img = Table([grid_row], colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                    t_img.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 2),
                        ('RIGHTPADDING', (0,0), (-1,-1), 2),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ]))
                    elements.append(t_img)
                    elements.append(Spacer(1, 10))
            else:
                elements.append(Paragraph("High Integrity Session: No proctoring violations were recorded.", styles['Normal']))

            # Identity Mismatch Section in PDF (placed below integrity screenshots)
            if getattr(candidate, 'identity_mismatch_detected', False) or getattr(candidate, 'photo_update_approved', False):
                elements.append(Spacer(1, 15))
                mismatch_title_style = ParagraphStyle(
                    'MismatchTitle',
                    parent=styles['Heading3'],
                    fontSize=11,
                    textColor=colors.HexColor("#EE5D50"),
                    fontName='Helvetica-Bold',
                    spaceAfter=6
                )
                elements.append(Paragraph("⚠ IDENTITY EVIDENCE — FACE COMPARISON MISMATCH", mismatch_title_style))
                
                mismatch_info = candidate.identity_mismatch_details or {}
                original_name = mismatch_info.get('original_holder_name', 'another person')
                
                desc_style = ParagraphStyle(
                    'MismatchDesc',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor("#EE5D50"),
                    leading=13
                )
                elements.append(Paragraph(
                    f"The candidate's face did not match the photo previously registered with this PAN card (originally used by {original_name}). "
                    "The interview was allowed to proceed via manual override.", 
                    desc_style
                ))
                elements.append(Spacer(1, 10))
                
                # Side-by-side comparison
                # NEW FACE = the pending photo awaiting admin approval.
                new_photo_elem = None
                if getattr(candidate, 'pending_face_b64', None):
                    try:
                        new_photo_elem = RLImage(io.BytesIO(base64.b64decode(candidate.pending_face_b64)), width=2.0*inch, height=1.5*inch)
                    except Exception:
                        pass

                if not new_photo_elem:
                    try:
                        deepface_data_dir_report = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'deepface', 'data', 'registered_faces'))
                        new_face_candidates = []
                        if candidate.pan_number:
                            new_face_candidates.append(
                                os.path.join(deepface_data_dir_report, str(candidate.pan_number).strip().lower(), "face_0.jpg")
                            )
                        if candidate.public_token:
                            new_face_candidates.append(
                                os.path.join(deepface_data_dir_report, str(candidate.public_token).lower(), "face_0.jpg")
                            )
                        new_face_path = next((p for p in new_face_candidates if os.path.exists(p)), None)
                        if new_face_path:
                            new_photo_elem = RLImage(new_face_path, width=2.0*inch, height=1.5*inch)
                    except Exception:
                        pass
                if not new_photo_elem:
                    new_photo_elem = Paragraph("<i>Current photo not available.</i>", styles['Normal'])

                # ORIGINAL REGISTERED FACE = the PAN master (trusted face)
                old_photo_elem = None
                if getattr(candidate, 'master_face_b64', None):
                    try:
                        old_photo_elem = RLImage(io.BytesIO(base64.b64decode(candidate.master_face_b64)), width=2.0*inch, height=1.5*inch)
                    except Exception:
                        pass

                if not old_photo_elem:
                    old_photo_elem = Paragraph("<i>Original photo not available.</i>", styles['Normal'])
                
                comparison_table = Table([
                    [old_photo_elem, new_photo_elem],
                    [Paragraph("<b>Original Registered Face</b>", styles['Small']), 
                     Paragraph("<b>Current Interview Face</b>", styles['Small'])]
                ], colWidths=[3.25*inch, 3.25*inch])
                
                comparison_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BOX', (0,0), (-1,-1), 1, colors.red),
                    ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#fee2e2")),
                ]))
                
                elements.append(comparison_table)
                elements.append(Spacer(1, 25))

            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            # Prepare Response
            from django.http import HttpResponse
            response = HttpResponse(buffer, content_type='application/pdf')
            safe_name = "".join([c for c in candidate.full_name if c.isalnum() or c==' ']).rstrip().replace(' ', '_')
            filename = f"VerifiHire_Report_{safe_name}_{candidate.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generating PDF report for candidate {pk}: {str(e)}", exc_info=True)
            return Response({'error': f"Critical failure during report generation: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- END OF FILE ---


class LogCandidateActivityView(APIView):
    """
    Public endpoint to log candidate activity during AI interviews.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, public_token):
        try:
            candidate = Candidate.objects.get(public_token=public_token, is_deleted=False)
            action = request.data.get('action')
            details = request.data.get('details', '')

            if action:
                from .utils import log_automation_event
                log_automation_event(
                    candidate,
                    'STATUS_CHANGE',
                    'INFO',
                    f"[Activity] {action}: {details}",
                    phase='INTERVIEW'
                )
                # Also print to server console for real-time monitoring
                print(f"[AI_CANDIDATE_ACTIVITY] {candidate.email} | {action}: {details}")

            return Response({'status': 'logged'})
        except Candidate.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthCheckView(APIView):
    """
    Health check endpoint for load balancers and monitoring.
    GET /health/ → Returns system status
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from .scaling_utils import get_system_health
        from rest_framework import status
        
        health = get_system_health()
        
        if health['status'] == 'healthy':
            return Response(health, status=status.HTTP_200_OK)
        else:
            return Response(health, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class ApprovePendingIdentityPhotoView(APIView):
    """
    Admin-only: approve a candidate's pending identity photo.

    When an AI-interview candidate joins with a face that doesn't match the
    previously registered face, the new photo is stored as `pending_face_b64`
    in the DB. An admin reviewing the result can approve the new photo here, which:
      1. Pushes the pending photo to DeepFace as the new master face for this PAN.
      2. Promotes pending_face_b64 → registered_face_b64 (the report photo).
      3. Clears the mismatch flag so subsequent interviews verify against the new face.

    POST /api/ai-candidates/<pk>/approve-photo/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

        user_role = (user_profile.role or '').strip().lower()
        if user_role not in ['company_admin', 'hr_manager', 'application_admin', 'admin']:
            return Response({'error': 'Unauthorized role access. Admin or HR Manager only.'}, status=status.HTTP_403_FORBIDDEN)

        # Authorization: must belong to the same company as the requesting user.
        if user_profile.company and candidate.company_id != user_profile.company_id:
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        from api._imports import get_scoped_user_ids
        scoped_ids = get_scoped_user_ids(user_profile)
        if scoped_ids is not None and candidate.user_profile_id not in scoped_ids:
            return Response({'error': 'Unauthorized access: Candidate falls outside your reporting hierarchy.'}, status=status.HTTP_403_FORBIDDEN)

        if not candidate.pending_face_b64:
            return Response(
                {'error': 'No pending photo to approve for this candidate.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Push the pending photo to DeepFace as the new master face for this PAN.
        try:
            person_id = (candidate.pan_number or str(candidate.public_token)).strip().lower()
            from .utils import _register_face_with_deepface
            df_result = _register_face_with_deepface(person_id, candidate.pending_face_b64)
            logger.info(f"[ApprovePhoto] DeepFace re-register for {person_id}: {df_result}")
        except Exception as e:
            logger.exception(f"[ApprovePhoto] Failed to push approved photo to DeepFace: {e}")
            return Response(
                {'error': f'Could not update DeepFace: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 2. Promote pending → registered (report photo) and update master.
        candidate.registered_face_b64 = candidate.pending_face_b64
        candidate.master_face_b64 = candidate.pending_face_b64  # New master for this PAN
        
        # 3. Also update the unified IdentityLink
        email = candidate.email.lower().strip() if candidate.email else None
        if email:
            from api.models import IdentityLink
            try:
                identity = IdentityLink.objects.filter(email__iexact=email).order_by('-updated_at').first()
                if identity and candidate.registered_face_b64:
                    import base64
                    from django.core.files.base import ContentFile
                    b64_str = candidate.registered_face_b64
                    if ',' in b64_str:
                        b64_str = b64_str.split(',', 1)[1]
                    img_data = base64.b64decode(b64_str)
                    filename = f"approved_ai_{candidate.id}.jpg"
                    identity.snapshot_image.save(filename, ContentFile(img_data), save=True)
                    logger.info(f"[ApprovePhoto] Updated IdentityLink for {email}")
            except Exception as e:
                logger.error(f"[ApprovePhoto] Failed to update IdentityLink: {e}")

        candidate.pending_face_b64 = None
        candidate.photo_update_approved = True
        candidate.identity_mismatch_detected = False
        details = candidate.identity_mismatch_details or {}
        details['photo_approved_at'] = timezone.now().isoformat()
        details['photo_approved_by'] = request.user.email if hasattr(request.user, 'email') else str(request.user)
        candidate.identity_mismatch_details = details
        candidate.save(update_fields=[
            'registered_face_b64',
            'master_face_b64',
            'pending_face_b64',
            'photo_update_approved',
            'identity_mismatch_detected',
            'identity_mismatch_details',
        ])

        logger.info(
            f"[ApprovePhoto] Admin {request.user} approved new photo for candidate {candidate.id} "
            f"(token: {candidate.public_token})"
        )
        return Response(
            {
                'success': True,
                'message': 'Photo approved and updated successfully.',
                'candidate_id': candidate.id,
            },
            status=status.HTTP_200_OK,
        )


class InterviewsOverviewView(APIView):
    """
    Returns all AI interview batches with per-batch stats and candidate lists.
    GET /api/ai-candidates/interviews-overview/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

        user_role = (user_profile.role or '').strip().lower()
        if user_role not in ['company_admin', 'hr_manager', 'hr', 'application_admin', 'recruiter', 'hiring_manager', 'admin']:
            return Response({'error': 'Unauthorized role access.'}, status=status.HTTP_403_FORBIDDEN)

        company = user_profile.company

        fields_to_fetch = [
            'id', 'batch_id', 'batch_name', 'job_title', 'created_at',
            'score', 'completed_at', 'status', 'link_opened_at',
            'public_token', 'full_name', 'email', 'automation_settings', 'interview_summary',
            'available_from', 'available_until'
        ]
        
        from api._imports import get_scoped_user_ids
        scoped_ids = get_scoped_user_ids(user_profile)

        if scoped_ids is None:
            if company:
                candidates = Candidate.objects.filter(company=company, is_deleted=False).only(*fields_to_fetch).order_by('-created_at')
            else:
                candidates = Candidate.objects.filter(is_deleted=False).only(*fields_to_fetch).order_by('-created_at')
        else:
            if company:
                candidates = Candidate.objects.filter(company=company, user_profile_id__in=scoped_ids, is_deleted=False).only(*fields_to_fetch).order_by('-created_at')
            else:
                candidates = Candidate.objects.filter(user_profile_id__in=scoped_ids, is_deleted=False).only(*fields_to_fetch).order_by('-created_at')

        # Group by batch
        from collections import defaultdict
        batch_map = defaultdict(list)
        for c in candidates:
            key = c.batch_id or f"single_{c.id}"
            batch_map[key].append(c)

        completed_statuses = {'Completed', 'Hired', 'Rejected', 'Interview Passed', 'Interview Failed'}
        in_progress_statuses = {'Interview', 'Resume Passed', 'On-Hold', 'Resume Failed', 'New'}

        total_all = 0
        completed_all = 0
        in_progress_all = 0
        pending_all = 0
        scores = []

        batches = []
        for batch_id, cands in batch_map.items():
            batch_name = cands[0].batch_name or cands[0].job_title or 'Unnamed Batch'
            created_at = cands[0].created_at
            available_from = cands[0].available_from
            available_until = cands[0].available_until

            batch_completed = 0
            batch_in_progress = 0
            batch_pending = 0
            candidate_list = []

            for c in cands:
                # Filter out candidates that are purely for resume screening
                is_ai = False
                if getattr(c, 'automation_settings', {}).get('is_fully_automatic', False):
                    # For fully automatic flows, they only count as an AI Interview if they reach the interview stage
                    if c.status in {'Interview', 'Interview Passed', 'Interview Failed', 'Completed', 'Hired', 'Rejected', 'On-Hold'} or bool(getattr(c, 'interview_summary', None)):
                        is_ai = True
                else:
                    if c.status in {'Interview', 'Interview Passed', 'Interview Failed', 'Completed', 'Hired', 'Rejected', 'On-Hold'}:
                        is_ai = True
                    elif getattr(c, 'automation_settings', {}).get('interview_duration_minutes'):
                        is_ai = True
                    elif bool(getattr(c, 'interview_summary', None)):
                        is_ai = True
                
                if not is_ai:
                    continue

                total_all += 1
                total_possible = TOTAL_INTERVIEW_QUESTIONS * 10
                score_pct = round(c.score_percentage) if c.score is not None and (c.completed_at or c.status in completed_statuses) else None

                if c.status in completed_statuses or c.completed_at:
                    batch_completed += 1
                    completed_all += 1
                    if score_pct is not None:
                        scores.append(score_pct)
                elif c.status in in_progress_statuses or (c.link_opened_at and not c.completed_at):
                    batch_in_progress += 1
                    in_progress_all += 1
                else:
                    batch_pending += 1
                    pending_all += 1

                status_group = 'completed' if (c.status in completed_statuses or c.completed_at) else \
                               'in_progress' if (c.status in in_progress_statuses or c.link_opened_at) else 'pending'

                candidate_list.append({
                    'id': c.id,
                    'public_token': str(c.public_token),
                    'name': c.full_name or 'Unknown',
                    'email': c.email or '',
                    'status': c.status or 'Invited',
                    'status_group': status_group,
                    'score_pct': score_pct,
                })

            if candidate_list:
                batches.append({
                    'batch_id': batch_id,
                    'batch_name': batch_name,
                    'created_at': timezone.localtime(created_at).strftime('%B %d, %Y %I:%M %p') if created_at else '',
                    'created_at_iso': timezone.localtime(created_at).isoformat() if created_at else '',
                    'available_from': timezone.localtime(available_from).strftime('%B %d, %Y %I:%M %p') if available_from else None,
                    'available_until': timezone.localtime(available_until).strftime('%B %d, %Y %I:%M %p') if available_until else None,
                    'total': len(candidate_list),
                    'completed': batch_completed,
                    'in_progress': batch_in_progress,
                    'pending': batch_pending,
                    'candidates': candidate_list,
                })

        # Sort batches by most recent first (use ISO timestamp for accurate ordering)
        batches.sort(key=lambda b: b.get('created_at_iso', ''), reverse=True)

        avg_score = round(sum(scores) / len(scores)) if scores else 0

        return Response({
            'summary': {
                'total': total_all,
                'completed': completed_all,
                'in_progress': in_progress_all,
                'pending': pending_all,
                'avg_score': avg_score,
            },
            'batches': batches,
        })


class ResendInviteView(APIView):
    """
    Resend the interview invite email to a candidate.
    POST /api/ai-candidates/<pk>/resend-invite/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

        user_role = (user_profile.role or '').strip().lower()
        if user_role not in ['company_admin', 'hr_manager', 'hr', 'application_admin', 'recruiter', 'hiring_manager', 'admin']:
            return Response({'error': 'Unauthorized role access.'}, status=status.HTTP_403_FORBIDDEN)

        if user_profile.company and candidate.company_id != user_profile.company_id:
            return Response({'error': 'Unauthorized access: Candidate belongs to another company.'}, status=status.HTTP_403_FORBIDDEN)

        from api._imports import get_scoped_user_ids
        scoped_ids = get_scoped_user_ids(user_profile)
        if scoped_ids is not None and candidate.user_profile_id not in scoped_ids:
            return Response({'error': 'Unauthorized access: Candidate falls outside your reporting hierarchy.'}, status=status.HTTP_403_FORBIDDEN)

        if candidate.completed_at or candidate.status in ['Completed', 'Hired', 'Rejected']:
            return Response({'error': 'Cannot resend invite for a completed interview.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from django.core.mail import send_mail
            frontend_base = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')
            link = f"{frontend_base}/interview-start/{candidate.public_token}"
            name = candidate.full_name or 'Candidate'
            email = candidate.email

            if not email:
                return Response({'error': 'Candidate has no email address.'}, status=status.HTTP_400_BAD_REQUEST)

            subject = f"Reminder: AI Interview Session - {candidate.job_title or 'Interview'}"
            message = f"Dear {name},\n\nThis is a reminder to complete your AI interview.\n\nLink: {link}\n\nBest regards,\nVerifiHireAI"
            html_message = f"""
            <div style="font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #6366F1, #8B5CF6); padding: 24px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 22px;">VerifiHireAI</h1>
                    <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0; font-size: 13px;">AI Interview Reminder</p>
                </div>
                <div style="padding: 32px; background-color: white;">
                    <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{name}</strong>,</p>
                    <p style="line-height: 1.6; margin-bottom: 24px;">This is a reminder to complete your AI-powered video interview session. Please click the button below to start or resume.</p>
                    <div style="text-align: center; margin: 32px 0;">
                        <a href="{link}" style="background-color: #6366F1; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block;">Start Interview</a>
                    </div>
                    <p style="font-size: 13px; color: #64748b; margin-top: 32px; border-top: 1px solid #f1f5f9; padding-top: 16px;">
                        If the button doesn't work, copy this link:<br/>
                        <a href="{link}" style="color: #6366F1;">{link}</a>
                    </p>
                </div>
            </div>
            """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False, html_message=html_message)
            logger.info(f"[ResendInvite] Email resent to {email} for candidate {candidate.id}")
            return Response({'success': True, 'message': f'Invite resent to {email}'})
        except Exception as e:
            logger.error(f"[ResendInvite] Failed to resend invite: {e}")
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import StandaloneResumeScreening
from .serializers import StandaloneResumeScreeningSerializer
from .tasks import process_standalone_resume_screening_task

class StandaloneResumeScreeningListCreateView(generics.ListCreateAPIView):
    queryset = StandaloneResumeScreening.objects.all().order_by('-created_at')
    serializer_class = StandaloneResumeScreeningSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        process_standalone_resume_screening_task.delay(instance.id)

class StandaloneResumeScreeningDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StandaloneResumeScreening.objects.all()
    serializer_class = StandaloneResumeScreeningSerializer


class BatchAddMemberView(APIView):
    """
    POST /api/ai-candidates/batch-add-member/
    Adds a new candidate to an existing batch with the same parameters
    (JD, experience level, scheduling, etc.) and sends the invite email.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        batch_id = request.data.get('batch_id')
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip().lower()

        if not batch_id or not name or not email:
            return Response({'error': 'batch_id, name, and email are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Find an existing candidate in this batch to copy parameters from
        reference = Candidate.objects.filter(batch_id=batch_id, is_deleted=False).first()
        if not reference:
            return Response({'error': 'Batch not found or has no candidates.'}, status=status.HTTP_404_NOT_FOUND)

        # Permission check
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)
        if user_profile.company and reference.company_id != user_profile.company_id:
            return Response({'error': 'Unauthorized: batch belongs to another company.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if email already exists in this batch
        if Candidate.objects.filter(batch_id=batch_id, email=email, is_deleted=False).exists():
            return Response({'error': f'{email} is already in this batch.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create new candidate with same parameters as the reference
        new_candidate = Candidate.objects.create(
            full_name=name,
            email=email,
            job_title=reference.job_title,
            job_description=reference.job_description,
            experience_level=reference.experience_level,
            available_from=reference.available_from,
            available_until=reference.available_until,
            interview_pass_threshold=reference.interview_pass_threshold,
            automation_settings=reference.automation_settings,
            status='Invited',
            company=reference.company,
            user_profile=user_profile,
            created_by=user_profile,
            batch_id=batch_id,
            batch_name=reference.batch_name,
        )

        # Send invite email
        try:
            from django.core.mail import send_mail
            frontend_base = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')
            link = f"{frontend_base}/interview-start/{new_candidate.public_token}"

            from_str = "Immediately"
            if new_candidate.available_from:
                local_from = timezone.localtime(new_candidate.available_from)
                from_str = local_from.strftime('%B %d, %Y at %I:%M %p')
            until_str = "No fixed deadline"
            if new_candidate.available_until:
                local_until = timezone.localtime(new_candidate.available_until)
                until_str = local_until.strftime('%B %d, %Y at %I:%M %p')

            subject = "Invite to VerifiHireAI Interview Session"
            message = f"Dear {name},\n\nYou have been invited to complete an AI-powered video interview.\n\nAvailable From: {from_str}\nAvailable Until: {until_str}\n\nPlease click the link below to start:\n{link}"
            html_message = f"""
            <div style="font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                <div style="background-color: #6366F1; padding: 24px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">Interview Invitation</h1>
                </div>
                <div style="padding: 32px; background-color: white;">
                    <p style="font-size: 16px;">Dear <strong>{name}</strong>,</p>
                    <p>You have been invited to complete an AI-powered video interview session.</p>
                    <div style="background: #f8fafc; padding: 16px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 4px 0; font-size: 14px;"><strong>📅 Available From:</strong> {from_str}</p>
                        <p style="margin: 4px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {until_str}</p>
                    </div>
                    <div style="text-align: center; margin: 24px 0;">
                        <a href="{link}" style="background-color: #6366F1; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">Start Interview Session</a>
                    </div>
                    <p style="font-size: 12px; color: #64748b; margin-top: 24px;">If the button doesn't work, copy this link: <a href="{link}">{link}</a></p>
                </div>
            </div>
            """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False, html_message=html_message)
            logger.info(f"[BatchAddMember] Invite sent to {email} for batch {batch_id}")
        except Exception as mail_err:
            logger.error(f"[BatchAddMember] Email failed for {email}: {mail_err}")

        return Response({
            'message': f'{name} added to batch and invite sent.',
            'candidate_id': new_candidate.id,
            'public_token': str(new_candidate.public_token),
        }, status=status.HTTP_201_CREATED)
