import io
import PyPDF2
from groq import Groq
import os
import json
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import Candidate, InterviewIntegrity
from .serializers import CandidateSerializer
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import traceback
import time
import re
import logging
from api.ocr_utils import _get_reader

from django.conf import settings
from django.core.mail import send_mail
import pandas as pd

# Setup Logger
logger = logging.getLogger(__name__)
MAX_CODING_TASKS = 50

from api.views import ensure_role_exists
from api.models import UserProfile
from api._imports import _is_application_admin_email, handle_deletion_request

# Configure Groq
# groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
# if not groq_api_key:
#     raise ValueError("GROQ_API_KEY must be set in settings.py")
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

    try:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return _unwrap_payload(json.loads(match.group(1)))
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return _unwrap_payload(json.loads(match.group(0)))
        return _unwrap_payload(json.loads(text.strip()))
    except Exception as e:
        logger.error(f"JSON Extraction Error: {e}")
        return None

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
        
        if not file or not job_description:
            return Response({"error": "File and Job Description are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
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
                    status='Invited',
                    company=company
                )
                link = f"http://localhost:3000/interview-start/{candidate.id}"
                
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
                "message": f"Successfully invited {len(invited_candidates)} candidates.",
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
        job_description = request.data.get('job_description')
        threshold = request.data.get('threshold', 70)
        try:
            threshold = int(threshold)
        except:
            threshold = 70

        # Handle the logic differently if we have a specific candidate_id (usually for single interview start)
        if candidate_id and not resume_files:
             try:
                candidate = Candidate.objects.get(id=candidate_id)
                if not job_description:
                    job_description = candidate.job_description or "General requirements and responsibilities for this role."
                if not candidate.resume:
                    return Response({"error": "Candidate has no resume uploaded"}, status=status.HTTP_400_BAD_REQUEST)
                resume_files = [candidate.resume] # Process this single resume
             except Candidate.DoesNotExist:
                 return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)

        if not job_description:
            job_description = "General requirements and responsibilities for this role."

        if not resume_files or not job_description:
            missing = []
            if not resume_files: missing.append("resume/candidate_id")
            if not job_description: missing.append("job_description")
            error_msg = f"Missing required fields: {', '.join(missing)}"
            logger.error(f"400 Bad Request: {error_msg}")
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        try:
            # Scoped lazy initialization for AI match
            local_api_key = getattr(settings, 'GROQ_API_KEY', None)
            local_groq_client = Groq(api_key=local_api_key)

            for resume_file in resume_files:
                current_candidate = None
                if candidate_id:
                    try:
                        current_candidate = Candidate.objects.get(id=candidate_id)
                    except Candidate.DoesNotExist:
                        continue # Should not happen if confirmed above
                
                # --- Interview Time Lock Check (only for single candidate flow) ---
                if current_candidate:
                    now = timezone.now()
                    if current_candidate.available_from and now < current_candidate.available_from:
                        formatted_time = current_candidate.available_from.strftime('%B %d, %Y %I:%M %p')
                        results.append({
                            "error": f"Interview not available for {current_candidate.full_name}. Session starts at {formatted_time}.",
                            "available_from": current_candidate.available_from,
                            "time_locked": True,
                            "candidate_id": current_candidate.id
                        })
                        continue
                    
                    if current_candidate.available_until and now > current_candidate.available_until:
                        results.append({
                            "error": f"Session expired for {current_candidate.full_name}. Please contact HR.",
                            "available_until": current_candidate.available_until,
                            "time_locked": True,
                            "candidate_id": current_candidate.id
                        })
                        continue

                try:
                    resume_text = ""
                    # If it's a FileField object (from candidate.resume) it might need different opening
                    if hasattr(resume_file, 'open'):
                        with resume_file.open('rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            for page in pdf_reader.pages:
                                resume_text += page.extract_text()
                    else:
                        resume_file.seek(0)
                        pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                        for page in pdf_reader.pages:
                            resume_text += (page.extract_text() or "")
                        
                        # --- OCR Fallback for Scanned PDFs ---
                        if len(resume_text.strip()) < 100:
                            logger.info(f"RESUME DEBUG: Regular extraction failed ({len(resume_text)} chars). Attempting IMAGE/OCR fallback.")
                            try:
                                # Try to open as image (case where PDF is just a renamed image or standard OCR case)
                                resume_file.seek(0)
                                reader = _get_reader()
                                if reader:
                                    # We try to read it as an image first
                                    try:
                                        img = Image.open(resume_file)
                                        results = reader.readtext(np.array(img), detail=0)
                                        ocr_text = " ".join(results)
                                        if len(ocr_text.strip()) > len(resume_text.strip()):
                                            resume_text = ocr_text
                                            logger.info(f"RESUME DEBUG: OCR Success! extracted {len(resume_text)} chars from image-pdf.")
                                    except:
                                        # Not an image? Maybe we need pdf2image or fitz, but let's try reading the first few bytes.
                                        pass
                            except Exception as ocr_e:
                                logger.error(f"OCR Fallback Error: {ocr_e}")

                        logger.info(f"RESUME DEBUG: Final extracted {len(resume_text)} characters from {getattr(resume_file, 'name', 'unknown')}")

                    # --- Validation for Empty or Short Text ---
                    if not resume_text or len(resume_text.strip()) < 50:
                         results.append({
                             "error": f"Unreadable resume: {getattr(resume_file, 'name', 'unknown')}. Ensure it's text-based.",
                             "candidate_name": getattr(resume_file, 'name', 'Unknown'),
                             "is_eligible": False
                         })
                         continue

                    # --- If no current_candidate, create one ---
                    if not current_candidate:
                        job_title = request.data.get('job_title') or request.data.get('role_title')
                        if job_title:
                            ensure_role_exists(job_title, job_description, user=request.user)

                        user_profile = getattr(request.user, 'profile', None)
                        company = user_profile.company if user_profile else None
                        
                        current_candidate = Candidate.objects.create(
                            full_name=getattr(resume_file, 'name', 'Candidate').replace('.pdf', ''),
                            email="pending@example.com",
                            job_title=job_title or "Applicant",
                            resume=None if hasattr(resume_file, 'open') else resume_file,
                            resume_text=resume_text,
                            status='New',
                            job_description=job_description,
                            company=company,
                            user_profile=user_profile
                        )

                    prompt = f"""
                    Act as an expert technical recruiter and interviewer. Analyze the match between the following resume and job description.
                    
                    Resume Content:
                    {resume_text}
                    
                    Job Description:
                    {job_description}
                    
                    Please provide:
                    1. The candidate's full name. Look at the very top of the document. If missing, return "Extraction Failed".
                    2. The candidate's contact email. Look for email patterns. If missing, return "Extraction Failed".
                    3. A match percentage (0-100) based on skills and experience matching the JD.
                    4. Eligibility status (True if match percentage >= {threshold}, otherwise False).
                    5. A brief 2-3 sentence summary of the fit.
                    6. A list of 7 interview questions (5 technical/behavioral questions + 2 coding-specific challenges or deep-dives) based on their resume and the JD. 
                    
                    CRITICAL: You MUST extract the name and email if they are present in ANY form. Do not be overly strict with formatting.
                    
                    Format the output strictly as a raw JSON object with these keys: "candidate_name", "candidate_email", "match_percentage", "is_eligible", "summary", "interview_questions".
                    """

                    response = local_groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        temperature=0.1
                    )
                    raw_text = response.choices[0].message.content
                    match_result = extract_json(raw_text)
                    
                    if match_result:
                        extracted_name = match_result.get('candidate_name') or match_result.get('full_name') or match_result.get('name') or "Extraction Failed"
                        extracted_email = match_result.get('candidate_email') or match_result.get('email') or match_result.get('email_address') or "Extraction Failed"
                        
                        current_candidate.full_name = extracted_name
                        current_candidate.email = extracted_email
                        
                        percentage = match_result.get('match_percentage', 0)
                        try:
                            num_percentage = int(float(percentage))
                        except (ValueError, TypeError):
                            num_percentage = 0
                        
                        current_candidate.resume_score = num_percentage
                        is_eligible = (num_percentage >= threshold)
                        match_result['is_eligible'] = is_eligible
                        current_candidate.status = 'Resume Passed' if is_eligible else 'Resume Failed'
                        
                        # Trigger automated assessment if in fully automatic mode
                        # Harden boolean check because it might be string "true" or "True"
                        is_auto_field = request.data.get('is_fully_automatic')
                        is_auto_match = False
                        if is_auto_field:
                            if isinstance(is_auto_field, str):
                                is_auto_match = is_auto_field.lower() == 'true'
                            else:
                                is_auto_match = bool(is_auto_field)

                        logger.info(f"CELERY DEBUG: Populating settings? is_auto={is_auto_match}")
                        
                        if is_auto_match:
                            coding_count = request.data.get('coding_count')
                            c_count = 1
                            if coding_count is not None:
                                try:
                                    c_count = int(coding_count)
                                except:
                                    c_count = 1
                            c_count = max(0, min(c_count, MAX_CODING_TASKS))

                            current_candidate.automation_settings = {
                                'difficulty': request.data.get('difficulty', 'Medium'),
                                'duration': int(request.data.get('duration', 60)),
                                'mcq_count': int(request.data.get('mcq_count', 10)),
                                'coding_count': c_count,
                                'pass_threshold': int(request.data.get('pass_threshold', 60)),
                                'assessment_available_from': request.data.get('assessment_available_from'),
                                'assessment_available_until': request.data.get('assessment_available_until')
                            }

                            interview_from = request.data.get('interview_available_from')
                            interview_until = request.data.get('interview_available_until')
                            if interview_from: current_candidate.available_from = parse_datetime(interview_from)
                            if interview_until: current_candidate.available_until = parse_datetime(interview_until)
                        
                        current_candidate.save()
                        
                        # Trigger automated assessment if in fully automatic mode
                        # Harden boolean check because it might be string "true" or "True"
                        raw_is_auto = request.data.get('is_fully_automatic')
                        is_auto = False
                        if raw_is_auto:
                            if isinstance(raw_is_auto, str):
                                is_auto = raw_is_auto.lower() == 'true'
                            else:
                                is_auto = bool(raw_is_auto)

                        logger.info(f"CELERY DEBUG: candidate={current_candidate.id}, is_auto_flag={is_auto}, is_eligible={is_eligible}")
                        
                        match_result['candidate_id'] = current_candidate.id
                        results.append(match_result)
                except Exception as loop_e:
                    logger.error(f"Error processing single resume: {loop_e}")
                    results.append({"error": str(loop_e), "is_eligible": False})

            return Response(results if len(results) > 1 or not candidate_id else results[0], status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"ERROR in ResumeMatchView: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

INTERVIEW_LINK_TTL_MINUTES = 60

class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CandidateSerializer

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
        
        # Use centralized helper to handle policy and workflow
        response, handled = handle_deletion_request(
            user_profile=user_profile,
            company=user_profile.company,
            content_type='Candidate',
            object_id=instance.id,
            object_repr=f"Candidate Profile: {instance.name} ({instance.email})",
            reason=request.data.get('reason')
        )
        
        if handled:
            return response

        return super().destroy(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        candidate = self.get_object()
        now = timezone.now()

        # Prevent retaking if already completed
        if candidate.status in ['Completed', 'Hired', 'Rejected'] or candidate.completed_at:
            from rest_framework.response import Response as DRFResponse
            return DRFResponse(
                {'error': 'You have already completed this interview session and cannot retake it.', 'link_expired': True},
                status=403
            )

        # First access — stamp the time
        if not candidate.link_opened_at:
            candidate.link_opened_at = now
            candidate.save(update_fields=['link_opened_at'])
        else:
            # Check if link has expired
            elapsed = now - candidate.link_opened_at
            if elapsed.total_seconds() > INTERVIEW_LINK_TTL_MINUTES * 60:
                from rest_framework.response import Response as DRFResponse
                return DRFResponse(
                    {'error': 'Interview link has expired.', 'link_expired': True},
                    status=403
                )

        response = super().get(request, *args, **kwargs)
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response


class CandidateStatusUpdateView(APIView):
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

class UpdateIntegrityView(APIView):
    def post(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
            integrity, created = InterviewIntegrity.objects.get_or_create(candidate=candidate)
            
            # Grace Warning System Phase 1: Record counts
            event_type = request.data.get('event_type')
            if event_type == 'tab_switch':
                integrity.tab_switches += 1
            elif event_type == 'phone_detection':
                integrity.phone_detections += 1
            elif event_type == 'multiface_detection':
                integrity.multiface_detections += 1
            elif event_type == 'no_face_detection':
                integrity.no_face_detections += 1
            
            # Grace Warning System Phase 2: Handle First 3 as Warnings
            # We track the types of the first 3 events that should be "free"
            if len(integrity.warning_logs) < 3:
                integrity.warning_logs.append(event_type)
            
            # Define weights
            weights = {
                'tab_switch': 10,
                'phone_detection': 30,
                'multiface_detection': 15,
                'no_face_detection': 5,
                'face_detection_lost': 5  # alias for no_face
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

class ProcessAnswerView(APIView):
    def post(self, request):
        candidate_id = request.data.get('candidate_id')
        current_question = request.data.get('question')
        answer = request.data.get('answer')
        remaining_questions = request.data.get('remaining_questions', [])
        chat_history = request.data.get('chat_history', []) 
        
        # DEBUG LOGGING
        with open('debug_ai.log', 'a') as f:
            f.write(f"\n--- New Request {datetime.now()} ---\n")
            f.write(f"Candidate ID: {candidate_id}\n")
            f.write(f"Question: {current_question}\n")
            f.write(f"Answer: {answer}\n")
        
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

        candidate_name = "Candidate"
        resume_context = "No resume available."
        jd_context = "No job description available."
        
        if candidate_id:
            try:
                if isinstance(candidate_id, str) and not candidate_id.isdigit():
                    pass
                else:
                    candidate = Candidate.objects.get(pk=candidate_id)
                    candidate_name = candidate.full_name
                    jd_context = candidate.job_description or jd_context
                    if candidate.resume_text:
                         resume_context = candidate.resume_text
            except Exception as e:
                with open('debug_ai.log', 'a') as f:
                    f.write(f"Lookup Error: {str(e)}\n")

        try:
            # Construct Chat History context with safety
            history_context = ""
            if chat_history:
                turns = []
                for h in chat_history[-6:]: # Increased history
                    role = h.get('role') or h.get('sender', 'unknown')
                    content = h.get('content') or h.get('text', '')
                    turns.append(f"{role.upper()}: {content}")
                history_context = "CONVERSATION HISTORY:\n" + "\n".join(turns) + "\n"

            prompt = f"""
        Role: "Rigorous Technical Auditor & Expert Interviewer". 
        Candidate: {candidate_name}
        Job Context: {jd_context[:200]}
        
        GOAL:
        Determine if the Candidate Answer is (A) A CLARIFICATION REQUEST, (B) An EXIT REQUEST, or (C) An ACTUAL ANSWER.

        (A) CLARIFICATION REQUEST - Trigger if:
        - The candidate explicitly asks to repeat: "repeat that", "pardon", "what?".
        - The candidate indicates they didn't hear or understand the question.
        
        (B) EXIT REQUEST - Trigger if:
        - The candidate asks to "end", "stop", "finish", or "exit" the interview.
        - The candidate expresses they no longer want to continue.

        (C) ACTUAL ANSWER - Trigger for:
        - Any substantive information, greetings, or "I don't know" / "skip".
        - IMPORTANT: If a candidate says "I don't know", "no idea", or "skip", it is an ACTUAL ANSWER (Score 0), NOT a clarification request. You must MOVE ON to the next topic.
        
        STT & CONTEXT AWARENESS:
        - NEVER loop more than once on the same question. If they tried to answer (even with just "I don't know"), MOVE ON.
        - DO NOT be a robot. If they gave any info, acknowledge it briefly and move to a DIFFERENT topic.
        - DO NOT start the question with "You were asked to..." or "Let's try again...". Just provide the next logical question.

        IF (A) CLARIFICATION REQUEST:
        1. Set "is_clarification": true, "is_exit": false.
        2. Set "feedback": A helpful rephrasing of the Last Question.
        3. Set "refined_next_question": current_question.

        IF (B) EXIT REQUEST:
        1. Set "is_clarification": false, "is_exit": true.
        2. Set "feedback": "I understand. Thank you for your time today. Goodbye!".
        3. Set "refined_next_question": null.

        IF (C) ACTUAL ANSWER:
        1. Set "is_clarification": false, "is_exit": false.
        2. "feedback": A brief acknowledgement.
        3. "refined_next_question": MUST BE A NEW, DIFFERENT QUESTION.
        4. SCORING: 0-1 for "I don't know", 2-4 for vague, 5-10 for correct.

        CONTEXT:
        Resume: {resume_context[:1000]}
        {history_context}
        
        CURRENT TURN:
        Last Question: "{current_question}"
        Candidate Answer: "{answer}"
        
        OUTPUT (JSON):
        {{
            "is_clarification": boolean,
            "is_exit": boolean,
            "feedback": "...",
            "refined_next_question": "...",
            "score": integer
        }}
        """

            # Lazy-load Groq for ProcessAnswerView
            local_api_key = getattr(settings, 'GROQ_API_KEY', None)
            local_groq_client = Groq(api_key=local_api_key)

            response = local_groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content
            data = extract_json(raw_text)
            
            if not data:
                raise ValueError("AI returned invalid JSON structure")

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
            if candidate_id and data.get('score') is not None and not data.get('is_clarification'):
                 try:
                    if not isinstance(candidate_id, str) or candidate_id.isdigit():
                        candidate = Candidate.objects.get(pk=candidate_id)
                        
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
                            "score": q_score
                        })
                        
                        candidate.save()
                 except: pass

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            with open('debug_ai.log', 'a') as f:
                f.write(f"PROCESS ERROR: {str(e)}\n")
                f.write(traceback.format_exc())
            
            return Response({
                "error": "AI is temporarily unavailable. Please try again or contact support."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
