import io
import PyPDF2
from groq import Groq
import os
import json
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

from django.conf import settings
from django.core.mail import send_mail
import pandas as pd

# Setup Logger
logger = logging.getLogger(__name__)

# Configure Groq
groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
if not groq_api_key:
    raise ValueError("GROQ_API_KEY must be set in settings.py")
groq_client = Groq(api_key=groq_api_key)

def extract_json(text):
    if not text:
        return None
    try:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"JSON Extraction Error: {e}")
        return None

class BulkInviteView(APIView):
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
                
                candidate = Candidate.objects.create(
                    full_name=name,
                    email=email,
                    available_from=available_from,
                    available_until=available_until,
                    interview_time=batch_interview_time,
                    job_description=job_description,
                    status='Invited'
                )
                link = f"http://localhost:3000/interview-start/{candidate.id}"
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
    def post(self, request):
        resume_file = request.FILES.get('resume')
        candidate_id = request.data.get('candidate_id')
        job_description = request.data.get('job_description')

        candidate = None
        if candidate_id:
            try:
                candidate = Candidate.objects.get(id=candidate_id)
                if not job_description:
                    job_description = candidate.job_description
            except Candidate.DoesNotExist:
                 return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)

        threshold = request.data.get('threshold', 70)
        try:
            threshold = int(threshold)
        except:
            threshold = 70

        if (not resume_file and not candidate) or not job_description:
            return Response({"error": "Job description and either resume or candidate_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Interview Time Lock Check ---
        if candidate:
            now = timezone.now()
            if candidate.available_from and now < candidate.available_from:
                formatted_time = candidate.available_from.strftime('%B %d, %Y %I:%M %p')
                return Response({
                    "error": f"Interview not available. Your session is scheduled to start at {formatted_time}. Please return at that time.",
                    "available_from": candidate.available_from,
                    "time_locked": True
                }, status=status.HTTP_403_FORBIDDEN)
            
            if candidate.available_until and now > candidate.available_until:
                return Response({
                    "error": "This interview session has expired. Please contact your recruiter.",
                    "available_until": candidate.available_until,
                    "time_locked": True
                }, status=status.HTTP_403_FORBIDDEN)
        # ----------------------------------

        try:
            resume_text = ""
            if resume_file and candidate:
                candidate.resume = resume_file
                resume_file.seek(0)
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
                candidate.resume_text = resume_text
                candidate.save()
            elif resume_file and not candidate:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
                resume_file.seek(0)
                candidate = Candidate.objects.create(
                    full_name=resume_file.name.replace('.pdf', ''),
                    email="pending@example.com",
                    job_title="Applicant",
                    resume=resume_file,
                    resume_text=resume_text,
                    status='New',
                    job_description=job_description
                )
                candidate_id = candidate.id
            elif candidate and not resume_file:
                if not candidate.resume:
                    return Response({"error": "Candidate has no resume uploaded"}, status=status.HTTP_400_BAD_REQUEST)
                if candidate.resume_text:
                     resume_text = candidate.resume_text
                else:
                    with candidate.resume.open('rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            resume_text += page.extract_text()
                    candidate.resume_text = resume_text
                    candidate.save()

            candidate_name = candidate.full_name if candidate else "the candidate"
            prompt = f"""
            Act as an expert technical recruiter and interviewer. Analyze the match between the following resume and job description for {candidate_name}.
            
            Resume Content:
            {resume_text}
            
            Job Description:
            {job_description}
            
            Please provide:
            1. A match percentage (0-100).
            2. Eligibility status (True if match percentage >= {threshold}, otherwise False).
            3. A brief 2-3 sentence summary of the fit.
            4. A list of 5 interview questions. 
               - The FIRST question MUST be EXACTLY: "Could you please introduce yourself and provide a brief overview of your professional background?"
               - Questions 2-5 MUST be technical and specific, based on the candidate's resume weaknesses or key job requirements.
            
            Format the output strictly as a raw JSON object with these keys: "match_percentage", "is_eligible", "summary", "interview_questions".
            The "interview_questions" key must be a list of STRINGS only.
            """

            logger.info("Using Groq for Resume Match")
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content

            if not raw_text:
                raise Exception("Empty response from Groq")

            match_result = extract_json(raw_text)
            if not match_result:
                raise Exception(f"Failed to parse Groq response: {raw_text[:200]}")
            
            # --- Safeguard: Flatten questions if AI returned objects ---
            if 'interview_questions' in match_result and isinstance(match_result['interview_questions'], list):
                sanitized_qs = []
                for q in match_result['interview_questions']:
                    if isinstance(q, dict):
                        sanitized_qs.append(q.get('question', str(q)))
                    else:
                        sanitized_qs.append(str(q))
                match_result['interview_questions'] = sanitized_qs
            # -----------------------------------------------------------

            # --- Safeguard: Ensure is_eligible matches threshold ---
            percentage = match_result.get('match_percentage', 0)
            try:
                percentage = int(percentage)
            except:
                percentage = 0
            match_result['is_eligible'] = percentage >= threshold
            # -----------------------------------------------------------

            # --- Save resume score and status to Candidate ---
            if candidate:
                candidate.resume_score = percentage
                candidate.status = 'Resume Passed' if percentage >= threshold else 'Resume Failed'
                candidate.save()
            # ---------------------------------------------------
            
            match_result['candidate_id'] = candidate_id
            return Response(match_result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"ERROR in ResumeMatchView: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CandidateListCreateView(generics.ListCreateAPIView):
    queryset = Candidate.objects.all().order_by('-created_at')
    serializer_class = CandidateSerializer

class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

class CandidateStatusUpdateView(APIView):
    def patch(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
            new_status = request.data.get('status')
            if new_status in dict(Candidate.STATUS_CHOICES):
                candidate.status = new_status
                if new_status in ['Completed', 'Hired', 'Rejected', 'Resume Failed']:
                    candidate.resume_text = None
                if new_status == 'Completed':
                    candidate.completed_at = timezone.now()
                candidate.save()
                return Response({'status': 'success', 'new_status': candidate.status})
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

class UpdateIntegrityView(APIView):
    def post(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
            integrity, created = InterviewIntegrity.objects.get_or_create(candidate=candidate)
            
            event_type = request.data.get('event_type')
            if event_type == 'tab_switch':
                integrity.tab_switches += 1
            elif event_type == 'phone_detection':
                integrity.phone_detections += 1
            elif event_type == 'multiface_detection':
                integrity.multiface_detections += 1
            elif event_type == 'no_face_detection':
                integrity.no_face_detections += 1
            
            # Simple penalty system
            total_violations = (
                integrity.tab_switches * 10 + 
                integrity.phone_detections * 30 + 
                integrity.multiface_detections * 15 + 
                integrity.no_face_detections * 5
            )
            integrity.integrity_score = max(0, 100 - total_violations)
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
            Role: "Expert Human Interviewer". 
            Candidate: {candidate_name}
            Job Context: {jd_context[:200]}
            
            GOAL:
            Be extremely concise. Aim for 15-25 words total.
            
            STRUCTURE:
            1. Response (1 sentence): Brief, human acknowledgment.
            2. Question (1 sentence): One clear technical or behavioral question.
            
            RULES:
            - NO FILLERS: Be direct.
            - PIVOT: If they don't know, quickly switch to a skill from their resume.
            
            CONTEXT:
            Resume: {resume_context[:1000]}
            {history_context}
            
            CURRENT TURN:
            Last Question: "{current_question}"
            Candidate Answer: "{answer}"
            
            OUTPUT (JSON):
            {{
                "feedback": "1-2 sentences of specific, thoughtful acknowledgment.",
                "refined_next_question": "One clear technical or behavioral question. End with ?",
                "score": "Integer 0-10"
            }}
            """

            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content
            data = extract_json(raw_text)
            
            if not data:
                raise ValueError("AI returned invalid JSON structure")

            # Scoring Update (Silent)
            if candidate_id and data.get('score'):
                 try:
                    if not isinstance(candidate_id, str) or candidate_id.isdigit():
                        candidate = Candidate.objects.get(pk=candidate_id)
                        candidate.score += int(data.get('score', 0))
                        candidate.total_questions += 1
                        candidate.save()
                 except: pass

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            with open('debug_ai.log', 'a') as f:
                f.write(f"PROCESS ERROR: {str(e)}\n")
                f.write(traceback.format_exc())
            
            fallback_q = remaining_questions[0] if remaining_questions else "Tell me more about your technical background."
            return Response({
                "feedback": "I appreciate you sharing that. It gives me a better sense of your approach.",
                "refined_next_question": fallback_q,
                "score": 0
            }, status=status.HTTP_200_OK)
