import io
import PyPDF2
from groq import Groq
import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import Candidate, InterviewIntegrity
from .serializers import CandidateSerializer
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
        batch_interview_time = request.data.get('interview_time') # Get batch time from request
        
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
                    time_info = f"\n\nYour interview is scheduled to start at {batch_interview_time}." if batch_interview_time else ""
                    message = f"Dear {name},\n\nYou have been invited to complete an AI-powered video interview.{time_info}\n\nPlease click the link below to verify your details and start your session:\n{link}"
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                    logger.info(f"Email sent to {email}")
                except Exception as mail_error:
                    logger.error(f"Failed to send email to {email}: {str(mail_error)}")
                
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
        next_question = request.data.get('next_question')
        chat_history = request.data.get('chat_history', []) 
        
        if not current_question or not answer:
             return Response({'error': 'Missing question or answer'}, status=status.HTTP_400_BAD_REQUEST)

        candidate_name = "Candidate"
        resume_context = "No resume available."
        jd_context = "No job description available."
        
        if candidate_id:
            try:
                candidate = Candidate.objects.get(pk=candidate_id)
                candidate_name = candidate.full_name
                jd_context = candidate.job_description or jd_context
                if candidate.resume_text:
                     resume_context = candidate.resume_text
            except Candidate.DoesNotExist:
                pass

        try:
            history_context = ""
            if chat_history:
                history_context = "CONVERSATION HISTORY:\n" + "\n".join([f"{h['role'].upper()}: {h['content']}" for h in chat_history[-4:]]) + "\n"

            prompt = f"""
            Role: "HireAI", a professional, elite technical interviewer for {candidate_name}.
            
            RULES:
            1. **ADAPTIVE**: Respond naturally to the candidate's answer. If they are vague, ask for details.
            2. **PERSONA**: Professional, encouraging but serious. Do not be overly chatty.
            3. **SELF-CORRECTION**: If the candidate asks a question, answer briefly and pivot back to the interview.
            4. **CONCISE**: Your feedback should be 1-2 sentences max.
            
            CONTEXT:
            Resume: {resume_context[:1000]} 
            Job Description: {jd_context[:500]}
            {history_context}
            
            CURRENT TURN:
            Question Asked: "{current_question}"
            Candidate Answer: "{answer}"
            Planned Next Question: "{next_question or 'End of Interview'}"
            
            OUTPUT (JSON Only):
            {{
                "feedback": "Short reaction + transition to next part",
                "refined_next_question": "Adjusted next question if needed, otherwise matches Planned Next Question",
                "follow_up_question": "Immediate clarification if the answer was incomplete (else null)"
            }}
            """

            logger.info("Using Groq for Process Answer")
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content

            if not raw_text:
                raise Exception("Empty response from Groq")

            data = extract_json(raw_text)
            if not data:
                data = {"feedback": raw_text.strip(), "refined_next_question": next_question, "follow_up_question": None}
            
            # Safeguard: Flatten next question if it's an object
            if data and 'refined_next_question' in data:
                q = data['refined_next_question']
                if isinstance(q, dict):
                    data['refined_next_question'] = q.get('question', str(q))

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in ProcessAnswerView: {str(e)}")
            return Response({
                "feedback": "Understood. Moving to the next question.",
                "follow_up_question": None,
                "refined_next_question": next_question
            }, status=status.HTTP_200_OK)
