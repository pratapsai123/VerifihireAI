import io
import PyPDF2
import fitz  # PyMuPDF
from groq import Groq
import os
import json
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Candidate, InterviewIntegrity, InterviewIntegrityLog, PipelineLog
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
TOTAL_INTERVIEW_QUESTIONS = 13

from api.views import ensure_role_exists
from api.models import UserProfile
from api._imports import _is_application_admin_email, handle_deletion_request

import uuid
from .tasks import process_resume_batch_task
# Import extract_json if needed or just keep local one if already there. 
# Looking at views.py it is usually defined at top.
# groq_client = Groq(api_key=groq_api_key)

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
    permission_classes = [AllowAny]
    authentication_classes = []
    def get(self, request):
        api_key = getattr(settings, 'ASSEMBLYAI_API_KEY', None)
        if not api_key:
            return Response({'error': 'ASSEMBLYAI_API_KEY is missing from configuration.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            response = requests.post(
                "https://api.assemblyai.com/v2/realtime/token",
                headers={"Authorization": api_key, "Content-Type": "application/json"},
                json={"expires_in": 3600}
            )
            response.raise_for_status()
            return Response(response.json())
        except Exception as e:
            logger.error(f"Failed to generate AssemblyAI token: {str(e)}")
            return Response({'error': 'Failed to generate transcription token.'}, status=status.HTTP_502_BAD_GATEWAY)

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
        try:
            interview_pass_threshold = int(interview_pass_threshold)
        except:
            interview_pass_threshold = 50

        
        if not file or not job_description:
            return Response({"error": "File and Job Description are required"}, status=status.HTTP_400_BAD_REQUEST)
            
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
                
            invited_candidates = []
            
            for _, row in df.iterrows():
                name = str(row['name']).strip()
                email = str(row['email']).strip()
                
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
                    logger.info(f"Email sent to {email}")
                except Exception as mail_error:
                    error_msg = f"Failed to send email to {email}: {str(mail_error)}"
                    logger.error(error_msg)
                    # Temporary file logging for debugging
                    with open('email_errors.log', 'a') as f:
                        f.write(f"{timezone.now()} - {error_msg}\n")
                
            return Response({
                "message": f"Successfully invited {len(invited_candidates)} {'candidate' if len(invited_candidates) == 1 else 'candidates'}.",
                "candidates": invited_candidates
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
        threshold = request.data.get('threshold', 70)
        try:
            threshold = int(threshold)
        except:
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
            elif not candidate.resume:
                return Response({"error": "Candidate has no resume uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Ensure candidate has a company/profile link if missing (e.g. from public link)
            # but don't overwrite if it already has one.
            if not candidate.user_profile and request.user.is_authenticated:
                candidate.user_profile = getattr(request.user, 'profile', None)
                if not candidate.company and candidate.user_profile:
                    candidate.company = candidate.user_profile.company

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
            # INSTANT SAVE: Create Candidate records without waiting for OCR
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
                    batch_name=batch_name
                )
                results.append({"id": new_candidate.id, "name": candidate_name, "status": "Queued"})

            # 2. Trigger processing as a background task
            is_auto = False
            raw_is_auto = request.data.get('is_fully_automatic')
            if raw_is_auto:
                if isinstance(raw_is_auto, str): is_auto = raw_is_auto.lower() == 'true'
                else: is_auto = bool(raw_is_auto)

            same_q = False
            raw_same_q = request.data.get('same_questions_for_all')
            if raw_same_q:
                if isinstance(raw_same_q, str): same_q = raw_same_q.lower() == 'true'
                else: same_q = bool(raw_same_q)

            automation_settings = {
                'difficulty': request.data.get('difficulty', 'Medium'),
                'duration': int(request.data.get('duration', 60)),
                'mcq_count': int(request.data.get('mcq_count', 10)),
                'coding_count': int(request.data.get('coding_count', 1)),
                'pass_threshold': int(request.data.get('pass_threshold', 60)),
                'interview_pass_threshold': int(request.data.get('interview_pass_threshold', 50)),
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
            return Response({"error": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)
        
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
                "summary": "Match calculated in background." if c.status != 'Extraction Failed' else f"Extraction failed for {c.full_name}."
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

                # Retry with Key Rotation
                match_result = None
                current_model = "llama-3.3-70b-versatile"
                
                for key_index in range(len(api_keys)):
                    try:
                        temp_client = Groq(api_key=api_keys[key_index % len(api_keys)])
                        print(f"   🤖 Calling AI ({current_model})...", end="", flush=True)
                        
                        response = temp_client.chat.completions.create(
                            model=current_model,
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"},
                            temperature=0.0
                        )
                        raw_text = response.choices[0].message.content
                        print(" Done!") # No streaming in retry view yet to keep it simple, but visible
                        match_result = extract_json(raw_text)
                        if match_result:
                            break
                    except Exception as e:
                        error_msg = str(e).lower()
                        if ("429" in error_msg or "rate limit" in error_msg or "quota" in error_msg):
                            if key_index < len(api_keys) - 1:
                                print(f"\n   🔄 Key {key_index+1} limit reached. Rotating...")
                                continue
                            elif current_model == "llama-3.3-70b-versatile":
                                print(f"\n   📉 All keys hit 70b limit. Using 8b fallback...")
                                current_model = "llama-3.1-8b-instant"
                                key_index = -1
                                continue
                        
                        print(f"\n   ❌ Error: {str(e)}")
                        break
                
                if match_result:
                    extracted_name = match_result.get('candidate_name') or match_result.get('full_name') or match_result.get('name') or "Extraction Failed"
                    extracted_email = match_result.get('candidate_email') or match_result.get('email') or match_result.get('email_address') or "Extraction Failed"
                    
                    candidate.full_name = extracted_name
                    candidate.email = extracted_email
                    
                    percentage = match_result.get('match_percentage', 0)
                    try:
                        num_percentage = int(float(percentage))
                    except:
                        num_percentage = 0
                    
                    candidate.resume_score = num_percentage
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
        serializer.save(company=company, user_profile=user_profile)

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
    authentication_classes = []

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

        if candidate.status in ['Completed', 'Hired', 'Rejected'] or candidate.completed_at:
            return Response(
                {'error': 'You have already completed this interview session and cannot retake it.', 'link_expired': True},
                status=status.HTTP_403_FORBIDDEN
            )



        if not candidate.link_opened_at:
            candidate.link_opened_at = now
            candidate.save(update_fields=['link_opened_at'])
            
            # Log interview start
            from .utils import log_automation_event
            log_automation_event(
                candidate, 
                'STATUS_CHANGE', 
                'SUCCESS', 
                f"AI Interview session started. Candidate accessed the link.",
                phase='INTERVIEW'
            )
        else:
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


class CandidateStatusUpdateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def patch(self, request, pk):
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile and user_profile.company else None
            
            # If recruiter, filter by company. If candidate (not auth), AllowAny might be needed?
            # Existing code didn't have permission_classes, so it was public.
            # We'll allow status updates if either recruiter from same company or AllowAny (for backward compat)
            if request.user.is_authenticated and company:
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

    def patch(self, request, public_token):
        try:
            candidate = _resolve_public_candidate(public_token)
            new_status = request.data.get('status')
            if new_status not in dict(Candidate.STATUS_CHOICES):
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            if new_status != 'Completed':
                return Response({'error': 'Only completion status is allowed for public links.'}, status=status.HTTP_403_FORBIDDEN)

            # Calculate final score percentage
            total_possible = candidate.total_questions * 10 if candidate.total_questions > 0 else 100
            score_percentage = (candidate.score / total_possible) * 100 if total_possible > 0 else 0

            # Determine pass/fail based on threshold
            threshold = candidate.interview_pass_threshold or 50
            if score_percentage >= threshold:
                candidate.status = 'Hired'
            else:
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
                f"AI Interview completed. Final Status: {candidate.status}. Score: {score_percentage}%",
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
            
            if event_type == 'tab_switch':
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
            
            # Grace Warning System Phase 2: Handle First 3 as Warnings
            if len(integrity.warning_logs) < 3:
                integrity.warning_logs.append(event_type)
            
            # Define weights
            weights = {
                'tab_switch': 2,
                'phone_detection': 2,
                'multiface_detection': 2,
                'no_face_detection': 2,
                'face_detection_lost': 2
            }

            # Simple penalty system
            total_raw_penalty = (
                integrity.tab_switches * weights['tab_switch'] + 
                integrity.phone_detections * weights['phone_detection'] + 
                integrity.multiface_detections * weights['multiface_detection'] + 
                integrity.no_face_detections * weights['no_face_detection']
            )

            # Subtract the "free" penalty from the first 3 warnings
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

            if event_type == 'tab_switch':
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
        
        logger.debug("ProcessAnswer request received for candidate_id=%s", candidate_id)
        
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

        # Public caller security: require unguessable token for unauthenticated requests.
        if not request.user.is_authenticated and not candidate_token:
            return Response({'error': 'candidate_token is required for public requests.'}, status=status.HTTP_400_BAD_REQUEST)

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

        try:
            # Construct Chat History context with safety
            history_context = ""
            if chat_history:
                turns = []
                # Fallback calculation if frontend didn't pass turn_number
                if not current_turn_number:
                    ai_questions_count = sum(1 for h in chat_history if h.get('role') in ('ai', 'assistant') or h.get('sender') in ('ai', 'assistant'))
                    current_turn_number = ai_questions_count + 1 
                
                for h in chat_history[-10:]: # Show more history for better context
                    role = h.get('role') or h.get('sender', 'unknown')
                    content = h.get('content') or h.get('text', '')
                    turns.append(f"{role.upper()}: {content}")
                history_context = f"CURRENT QUESTION NUMBER: {current_turn_number} of 13\nCONVERSATION HISTORY:\n" + "\n".join(turns) + "\n"
            else:
                if not current_turn_number:
                    current_turn_number = 1
                history_context = "This is the START of the interview. Question #1.\n"

            # --- DYNAMIC CATEGORY INJECTION ---
            category_map = {
                1: ("INTRO", "Greet the candidate warmly and ask them to introduce themselves."),
                2: ("JD-Q1", "Ask a question derived DIRECTLY from the Job Description requirements."),
                3: ("JD-Q2", "Ask another question derived DIRECTLY from the Job Description requirements."),
                4: ("JD-Q3", "Ask a third question derived DIRECTLY from the Job Description requirements."),
                5: ("JD-Q4", "Ask a fourth question derived DIRECTLY from the Job Description requirements."),
                6: ("RESUME-SKILL-Q1", "Ask about a SPECIFIC SKILL listed in the Resume that is relevant to the JD."),
                7: ("RESUME-SKILL-Q2", "Ask about a DIFFERENT SPECIFIC SKILL from the Resume relevant to the JD."),
                8: ("PROJECT-Q1", "Ask about a SPECIFIC PROJECT mentioned in the Resume (role, challenges, or architecture)."),
                9: ("PROJECT-Q2", "Ask about a DIFFERENT PROJECT from the Resume (or deeper dive into the previous project)."),
                10: ("SCENARIO-Q1", "Ask a 'Imagine you are...' or 'How would you handle...' hypothetical workplace scenario derived DIRECTLY from the Job Description requirements."),
                11: ("SCENARIO-Q2", "Ask a DIFFERENT hypothetical scenario-based question, also derived DIRECTLY from the Job Description."),
                12: ("SYNTAX-Q1", "Ask a CODING or SYNTAX question: 'Write a function that...', 'What does this code output?', etc."),
                13: ("SYNTAX-Q2", "Ask a DIFFERENT coding or syntax question.")
            }
            
            # Get current turn instructions
            target_category, target_instruction = category_map.get(current_turn_number, ("EXIT", "The interview is over. Say goodbye."))
            # ----------------------------------

            prompt = f"""
        You are "Indu", a warm, sharp, and experienced technical interviewer conducting a live interview for the position of **{job_title}**.
        Candidate Name: {candidate_name}
        
        ===== YOUR SPECIFIC MISSION FOR THIS TURN (TURN #{current_turn_number}) =====
        CATEGORY: {target_category}
        INSTRUCTION: {target_instruction} (STRICTLY FOLLOW THIS)
        
        ===== JOB DESCRIPTION =====
        {jd_context[:1500]}
        
        ===== RESUME =====
        {resume_context[:3000]}
        
        ===== EXPERIENCE LEVEL & DIFFICULTY =====
        {self._get_difficulty_instructions(experience_level)}
        
        ===== PERSONALITY & TONE RULES =====
        - You are a REAL HUMAN interviewer, NOT a robot. Speak naturally.
        - NEVER use these banned phrases: "Your explanation was clear and concise", "Great answer", "That's a good point", "Well said", "That's not a great sign", "That's a concern". These sound robotic and repetitive.
        - Instead, react SPECIFICALLY to what the candidate actually said. Reference their exact words. Examples:
          * "Interesting that you chose React.memo for that — I've seen teams debate that approach..."
          * "So you went with lazy loading — that makes sense for a dashboard with heavy data."
          * "Hmm, that's a solid approach. Let me throw a curveball at you..."
          * "Got it. I'd love to dig deeper into something you mentioned..."
        - Keep feedback to 1-2 SHORT sentences max. Don't lecture or summarize their answer back to them.
        - ⚠️ ABSOLUTE BAN: NEVER include ANY of these category tags in your spoken output: JD-Q1, JD-Q2, JD-Q3, JD-Q4, RESUME-SKILL-Q1, RESUME-SKILL-Q2, PROJECT-Q1, PROJECT-Q2, SCENARIO-Q1, SCENARIO-Q2, SYNTAX-Q1, SYNTAX-Q2, INTRO. These tags are ONLY for YOUR internal tracking. If the candidate hears them, the system is broken.
        - NEVER announce or reference the question number, turn number, or category.
        - NEVER repeat the same feedback phrasing twice in the same interview. Each response MUST be unique.
        - When asking resume/project questions, START with a specific detail from the resume (e.g., "I noticed you worked on [specific project name]...", "Your resume mentions [specific skill]...").
        - Use conversational fillers like "Hmm", "I see", "Got it", "Interesting", "Fair enough" occasionally to sound like you are listening.
        - Vary your transitions naturally. Choose from these styles:
            * Curiosity: "Now I'm curious about...", "I'd love to hear more about..."
            * Shifting Gears: "Let's pivot slightly to...", "Alright, moving on to...", "Switching gears a bit..."
            * Casual: "Okay, next up...", "So, tell me about...", "I want to ask you about..."
            * Deep Dive: "Let's dig into...", "I want to focus on a particular area..."
        - If the candidate gives a weak or wrong answer, gently note it: "That's not quite what I was looking for, but let's keep going."
        - If they say "I don't know", say something like: "No worries, let's move on to something else."
        - Avoid starting every response with "Great," "Alright," or "Okay." Mix it up.
        
        ===== CRITICAL ENFORCEMENT RULES =====
        - You MUST ask a question matching the CATEGORY: {target_category}.
        - For RESUME-SKILL questions: Pick a SPECIFIC skill from the resume.
        - For PROJECT questions: Reference a SPECIFIC project from the resume by name.
        - For SYNTAX questions (Turns 12-13): Ask actual coding problems, NOT conceptual questions.
        - For SCENARIO questions (Turns 10-11): These MUST be hypothetical scenarios based on the Job Description's requirements or the challenges typical to the **{job_title}** role.
        - Do NOT ask follow-up questions on the same topic. Each turn MUST move to the next category.
        
        ===== INPUT MODE =====
        - Turns 1-11: Set "requires_code_input": false (audio/verbal mode)
        - Turns 12-13: Set "requires_code_input": true (keyboard/coding mode)
        
        ===== INTERVIEW COMPLETION =====
        - If target_category == "EXIT" or current_turn_number >= 14: The interview is OVER. Set "is_exit": true.
        
        ===== SPECIAL TRIGGERS =====
        (A) CLARIFICATION: If candidate says "repeat that", "pardon", "what?", "I don't understand", or asks for clarification:
            1. Set "is_clarification": true.
            2. In "feedback", write a friendly 1-sentence acknowledgement.
            3. In "refined_next_question", provide a simplified or rephrased version of the EXACT SAME topic (Turn #{current_turn_number}). Do NOT move to the next category.
        (B) EXIT: If candidate says "end", "stop", "finish" → Set "is_exit": true, say goodbye.
        
        ===== SCORING GUIDES (0-10) =====
        - 10: Perfect, comprehensive, and accurate answer.
        - 8-9: Correct and clear answer, perhaps missing minor detail. (BEYOND SATISFACTORY)
        - 6-7: Good attempt, mostly correct but a bit vague or lacks depth. (PASSABLE)
        - 4-5: Weak or slightly incorrect answer, but shows basic effort/knowledge. (LENIENT PARTIAL CREDIT)
        - 2-3: Very poor or largely incorrect answer, but they tried to speak.
        - 0-1: Silent, "I don't know," or "Skip."
        
        *BE GENEROUS*: If the candidate shows they understand the core concept but struggle to articulate it perfectly, lean towards a 6 or 7.
        
        ===== CONVERSATION CONTEXT =====
        {history_context}
        
        CURRENT TURN:
        Last Question: "{current_question}"
        Target Category for this next question: {target_category}
        Candidate Answer: "{answer}"
        
        ===== RESPOND WITH THIS EXACT JSON =====
        {{
            "is_clarification": false,
            "is_exit": false,
            "feedback": "Your 1-2 sentence HUMAN-LIKE reaction to their answer (NEVER generic praise)",
            "refined_next_question": "Your next question — MUST match the category for Turn #{current_turn_number + 1}",
            "requires_code_input": false, // Set to TRUE ONLY IF Turn #{current_turn_number + 1} is a SYNTAX Turn (12-13)
            "score": 0,
            "score_reason": "1-sentence justification for the score"
        }}
        """

            # Lazy-load Groq for ProcessAnswerView using GroqKeyManager for key rotation
            from ai_assessments.ai_logic import GroqKeyManager
            import time as _time

            local_api_key = GroqKeyManager.get_current_key()
            local_groq_client = Groq(api_key=local_api_key)

            # --- AUTO MODEL FALLBACK WITH KEY ROTATION ---
            PRIMARY_MODEL = "llama-3.3-70b-versatile"
            FALLBACK_MODEL = "llama-3.1-8b-instant"
            COOLDOWN_SECONDS = 60

            # Check if we're currently in cooldown from a previous 70b rate limit
            if not hasattr(ProcessAnswerView, '_fallback_until'):
                ProcessAnswerView._fallback_until = 0

            if _time.time() < ProcessAnswerView._fallback_until:
                chosen_model = FALLBACK_MODEL
                logger.info(f"Using fallback model {FALLBACK_MODEL} (70b cooldown active for {int(ProcessAnswerView._fallback_until - _time.time())}s more)")
            else:
                chosen_model = PRIMARY_MODEL

            try:
                response = local_groq_client.chat.completions.create(
                    model=chosen_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
            except Exception as model_err:
                error_str = str(model_err).lower()
                if ("rate limit" in error_str or "429" in error_str):
                    # Rotate to next key first
                    GroqKeyManager.rotate_key()
                    rotated_key = GroqKeyManager.get_current_key()
                    local_groq_client = Groq(api_key=rotated_key)

                    if chosen_model == PRIMARY_MODEL:
                        # 70b hit rate limit → activate cooldown and retry with 8b immediately
                        ProcessAnswerView._fallback_until = _time.time() + COOLDOWN_SECONDS
                        logger.warning(f"70b rate-limited! Falling back to {FALLBACK_MODEL} for {COOLDOWN_SECONDS}s")
                    
                    response = local_groq_client.chat.completions.create(
                        model=FALLBACK_MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        response_format={"type": "json_object"}
                    )
                elif "api_key" in error_str or "authentication" in error_str:
                    # Bad key — rotate and retry once
                    GroqKeyManager.rotate_key()
                    rotated_key = GroqKeyManager.get_current_key()
                    local_groq_client = Groq(api_key=rotated_key)
                    logger.warning(f"Bad API key detected, rotated to next key")
                    response = local_groq_client.chat.completions.create(
                        model=chosen_model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        response_format={"type": "json_object"}
                    )
                else:
                    raise  # Re-raise non-rate-limit errors
            # --- END MODEL FALLBACK ---

            raw_text = response.choices[0].message.content
            data = extract_json(raw_text)
            
            if not data:
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

            # --- SAFETY GUARD: Prevent Question Looping ---
            # If the candidate said "I don't know" or similar, and the AI tries to repeat the question 
            # even while setting is_clarification=false, we force it to move on.
            refined_q = data.get('refined_next_question')
            if not data.get('is_clarification') and not data.get('is_exit'):
                if refined_q == current_question or not refined_q:
                    logger.warning(f"AI attempted to repeat question: {current_question}. Forcing move to next.")
                    if remaining_questions:
                        data['refined_next_question'] = remaining_questions[0]
                    else:
                        data['refined_next_question'] = "That's perfectly fine. Tell me about another project you've worked on recently."
            # -----------------------------------------------

            # Scoring Update (Silent)
            if candidate and data.get('score') is not None and not data.get('is_clarification'):
                 try:
                    # Update score
                    q_score = int(data.get('score', 0))
                    candidate.score += q_score
                    candidate.total_questions += 1

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

                    candidate.save()
                 except: pass

            return Response(data, status=status.HTTP_200_OK)

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
    Text-to-Speech endpoint using Coqui TTS.
    POST {"text": "Hello!"} → returns audio/wav binary response.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        text = request.data.get('text', '').strip()
        if not text:
            return Response({"error": "Missing 'text' field"}, status=status.HTTP_400_BAD_REQUEST)

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
    Fetches the history (PipelineLog) for a specific candidate.
    """
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
            # Permission check: ensure user belongs to same company
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile or (user_profile.company != candidate.company and not self.request.user.is_superuser):
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
            logs = candidate.pipeline_logs.all().order_by('timestamp')
            serializer = PipelineLogSerializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

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
            
            # RBAC: Ensure user belongs to the same company or is a superuser
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile or (user_profile.company != candidate.company and not request.user.is_superuser):
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
            # First try deepface directory using public token (which is what the frontend uses for registration)
            person_img_path = None
            deepface_data_dir = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'deepface', 'data', 'registered_faces'))
            person_id = str(candidate.public_token).lower() if candidate.public_token else None
            path_options = []
            
            if person_id:
                path_options = [
                    os.path.join(deepface_data_dir, person_id, "face_0.jpg"),
                ]
            
            for p in path_options:
                if os.path.exists(p):
                    person_img_path = p
                    break

            # Fallback: Use first webcam screenshot from integrity logs
            fallback_img_data = None
            if not person_img_path:
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
            total_possible_marks = TOTAL_INTERVIEW_QUESTIONS * 10
            base_score_pct = (candidate.score / total_possible_marks * 100) if total_possible_marks > 0 else 0
            
            integrity_obj = getattr(candidate, 'integrity', None)
            integrity_score = integrity_obj.integrity_score if integrity_obj else 100.0
            integrity_penalty = max(0, 100.0 - integrity_score)
            
            final_performance_pct = max(0, round(base_score_pct - integrity_penalty, 1))

            # Right side: Summary Table
            info_data = [
                ["Full Name", candidate.full_name],
                ["Email", candidate.email],
                ["Job Title", candidate.job_title or "N/A"],
                ["Interview Score", f"{candidate.score} / {total_possible_marks}"],
                ["Integrity Penalty", f"-{integrity_penalty:.1f}%"],
                ["Final Performance", f"{final_performance_pct}%"],
                ["Status", candidate.status],
                ["Completion Date", candidate.completed_at.strftime('%B %d, %Y %I:%M %p') if candidate.completed_at else 'Incomplete'],
            ]
            
            summary_table = Table(info_data, colWidths=[1.2*inch, 3.0*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f8fafc")),
                ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#475569")),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))

            # Combine in a layout table
            layout_table = Table([[img_elem, summary_table]], colWidths=[2.2*inch, 4.3*inch])
            layout_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (0,0), (0,0), 'LEFT'),
                ('ALIGN', (1,0), (1,0), 'LEFT'),
            ]))
            elements.append(layout_table)
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
                    
                    # Question text
                    elements.append(Paragraph(f"<b>Question:</b>", styles['Normal']))
                    elements.append(Paragraph(turn.get('question', 'N/A'), styles['Normal']))
                    elements.append(Spacer(1, 8))
                    
                    # Answer
                    elements.append(Paragraph(f"<b>Candidate Answer:</b>", styles['Normal']))
                    elements.append(Paragraph(turn.get('answer', 'N/A'), styles['Normal']))
                    elements.append(Spacer(1, 8))
                    
                    # AI Analysis
                    elements.append(Paragraph(f"<b>AI Analysis:</b>", styles['Normal']))
                    elements.append(Paragraph(f"<i>{turn.get('feedback', 'No feedback provided.')}</i>", styles['Normal']))
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
                    elements.append(Paragraph(f"<b>Score: {score}/10</b> — {turn.get('reason', '')}", score_style))
                    
                    elements.append(Paragraph('<hr color="#e2e8f0" thickness="1"/>', styles['Normal']))
                    elements.append(Spacer(1, 12))
            else:
                elements.append(Paragraph("No interview transcript data recorded for this session.", styles['Italic']))

            # 4. Integrity Violations & Snapshots
            elements.append(PageBreak())
            elements.append(Paragraph("Proctoring & Integrity Evidence", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            logs = candidate.integrity_logs.all().order_by('timestamp')
            if logs.exists():
                elements.append(Paragraph(f"Total violations flagged: {logs.count()}", styles['Normal']))
                elements.append(Spacer(1, 15))
                
                # Collect all images across all logs for 4-per-row layout
                all_images = []
                for log in logs:
                    # Process Webcam Snapshot
                    if log.webcam_screenshot_base64:
                        try:
                            b64 = log.webcam_screenshot_base64.split(',')[-1]
                            img_data = base64.b64decode(b64)
                            img_io = io.BytesIO(img_data)
                            rl_img = RLImage(img_io, width=1.5*inch, height=1.1*inch)
                            all_images.append((rl_img, f"Webcam - {log.event_type.replace('_', ' ').title()} ({log.timestamp.strftime('%H:%M:%S')})"))
                        except: pass
                    
                    # Process Desktop Snapshot
                    if log.screenshot_base64:
                        try:
                            b64 = log.screenshot_base64.split(',')[-1]
                            img_data = base64.b64decode(b64)
                            img_io = io.BytesIO(img_data)
                            rl_img = RLImage(img_io, width=1.5*inch, height=1.1*inch)
                            all_images.append((rl_img, f"Desktop - {log.event_type.replace('_', ' ').title()} ({log.timestamp.strftime('%H:%M:%S')})"))
                        except: pass
                
                if all_images:
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
                    elements.append(Paragraph("[No visual evidence captured for violations]", styles['Small']))
            else:
                elements.append(Paragraph("High Integrity Session: No proctoring violations were recorded.", styles['Normal']))

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

class CandidateTimelineView(APIView):
    """
    Fetches the history (PipelineLog) for a specific candidate.
    """
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
            # Permission check: ensure user belongs to same company
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile or (user_profile.company != candidate.company and not self.request.user.is_superuser):
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
            logs = candidate.pipeline_logs.all().order_by('timestamp')
            serializer = PipelineLogSerializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

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