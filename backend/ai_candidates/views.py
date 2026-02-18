import io
import PyPDF2
import google.generativeai as genai
import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import Candidate
from .serializers import CandidateSerializer
import traceback

# Configure Gemini
from django.conf import settings
from django.core.mail import send_mail
import pandas as pd
genai.configure(api_key=settings.GEMINI_API_KEY)

class BulkInviteView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        job_description = request.data.get('job_description')
        
        if not file or not job_description:
            return Response({"error": "File and Job Description are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Parse file based on extension
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                return Response({"error": "Unsupported file format. Use CSV or Excel."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Normalize headers
            df.columns = df.columns.str.lower().str.strip()
            
            # Check for required columns
            required_cols = ['name', 'email']
            if not all(col in df.columns for col in required_cols):
                return Response({"error": f"File must contain columns: {', '.join(required_cols)}"}, status=status.HTTP_400_BAD_REQUEST)
                
            invited_candidates = []
            
            for _, row in df.iterrows():
                name = row['name']
                email = row['email']
                
                # Create Candidate
                candidate = Candidate.objects.create(
                    full_name=name,
                    email=email,
                    job_description=job_description,
                    status='Invited'
                )
                
                # Generate Link (frontend URL)
                link = f"http://localhost:3000/ai/ai_interview_start.html?token={candidate.id}"
                
                invited_candidates.append({
                    "id": candidate.id,
                    "name": name,
                    "email": email,
                    "link": link
                })
                
                # Send Email
                try:
                    subject = "Invite to VerifiHireAI Interview Session"
                    message = f"""
                    Dear {name},
                    
                    You have been invited to complete an AI-powered video interview for the position described below.
                    
                    Please click the link below to verify your details and start your session:
                    {link}
                    
                    Best regards,
                    The VerifiHireAI Team
                    """
                    
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
                    print(f"Email sent successfully to {email}")
                    
                except Exception as mail_error:
                    print(f"Failed to send email to {email}: {str(mail_error)}")
                
            return Response({
                "message": f"Successfully invited {len(invited_candidates)} candidates.",
                "candidates": invited_candidates
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
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
                # Fallback to stored JD if not provided
                if not job_description:
                    job_description = candidate.job_description
            except Candidate.DoesNotExist:
                 return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)

        if (not resume_file and not candidate) or not job_description:
            return Response({"error": "Job description and either resume or candidate_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resume_text = ""
            
            # Case 1: Uploading Resume for Existing Candidate (New Flow)
            if resume_file and candidate:
                candidate.resume = resume_file
                candidate.save()
                # Read from upload directly
                resume_file.seek(0)
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()

            # Case 2: New Candidate Upload (Old Flow)
            elif resume_file and not candidate:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
                
                resume_file.seek(0)
                # Create temp candidate
                candidate = Candidate.objects.create(
                    full_name=resume_file.name.replace('.pdf', ''),
                    email="pending@example.com",
                    job_title="Applicant",
                    resume=resume_file,
                    status='New',
                    job_description=job_description
                )
                candidate_id = candidate.id
            
            # Case 3: Existing Candidate with Existing Resume
            elif candidate and not resume_file:
                if not candidate.resume:
                    return Response({"error": "Candidate has no resume uploaded"}, status=status.HTTP_400_BAD_REQUEST)
                with candidate.resume.open('rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        resume_text += page.extract_text()

            # 2. Call Gemini
            model = genai.GenerativeModel('gemini-flash-latest')
            candidate_name = candidate.full_name if candidate else "the candidate"
            
            prompt = f"""
            Act as an expert technical recruiter. Analyze the match between the following resume and job description for {candidate_name}.
            
            Resume Content:
            {resume_text}
            
            Job Description:
            {job_description}
            
            Please provide:
            1. A match percentage (0-100).
            2. Eligibility status (True if match percentage > 70, otherwise False).
            3. A brief 2-3 sentence summary of the fit, highlighting key strengths and missing requirements.
            4. A list of 5 interview questions. 
               - The FIRST question MUST be: "Could you please introduce yourself and provide a brief overview of your professional background?"
               - The remaining 4 questions should be technical, tailored to the candidate's resume and the job description.
            
            Format the output strictly as a raw JSON object with these keys: "match_percentage", "is_eligible", "summary", "interview_questions".
            The "interview_questions" key must be a list of strings.
            Do not include any markdown formatting or extra text.
            """

            response = model.generate_content(prompt)
            clean_response = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_response)
            
            # Add candidate_id to response
            result['candidate_id'] = candidate_id

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
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
                candidate.save()
                return Response({'status': 'success', 'new_status': candidate.status})
            else:
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

class ProcessAnswerView(APIView):
    def post(self, request):
        candidate_id = request.data.get('candidate_id')
        current_question = request.data.get('question')
        answer = request.data.get('answer')
        next_question = request.data.get('next_question')
        chat_history = request.data.get('chat_history', []) 
        
        if not current_question or not answer:
             return Response({'error': 'Missing question or answer'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Fetch Candidate Context if ID is provided
        resume_context = "No resume available."
        jd_context = "No job description available."
        candidate_name = "Candidate"
        
        candidate_email = "No email provided"
        
        if candidate_id:
            try:
                candidate = Candidate.objects.get(pk=candidate_id)
                candidate_name = candidate.full_name
                candidate_email = candidate.email or candidate_email
                jd_context = candidate.job_description or jd_context
                
                if candidate.resume:
                    try:
                        import PyPDF2
                        with candidate.resume.open('rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            resume_text = ""
                            for page in pdf_reader.pages:
                                resume_text += page.extract_text()
                            resume_context = resume_text if resume_text.strip() else resume_context
                    except Exception as e:
                        print(f"Resume Parse Error: {e}")
            except Candidate.DoesNotExist:
                print(f"Candidate {candidate_id} not found.")

        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            
            # Format history for the prompt
            history_context = ""
            if chat_history:
                history_context = "CONVERSATION HISTORY:\n" + "\n".join([f"{h['role'].upper()}: {h['content']}" for h in chat_history[-4:]]) + "\n"

            prompt = f"""
            Act as an elite technical interviewer named "HireAI". 
            You are interviewing {candidate_name} (Email: {candidate_email}).
            You are profoundly empathetic, "human-like", and sweet. 
            Your goal is to make {candidate_name} feel valued and supported.
            
            CANDIDATE CONTEXT:
            Resume: {resume_context[:2000]} # Truncated for token limits
            Job Description: {jd_context[:1000]}
            
            {history_context}
            CURRENT TURN:
            Question Asked: "{current_question}"
            Candidate's Answer: "{answer}"
            Next Planned Topic/Question: "{next_question if next_question else "Wrap up the interview"}"
            
            YOUR TASK:
            1. **Personalized Reaction**: 
               - Give a SWEET AND SIMPLE reaction to their answer (Strictly 1 sentence).
               - Use their resume context to acknowledge specific skills or experiences if relevant (e.g., "That's a great point about your work with Python!").
               - If they say "I don't know", be exceptionally sweet and encouraging.
            2. **Topic Control & Flow**:
               - You must NOT stay on the same topic for more than one follow-up.
               - If the candidate's answer is complete or they just finished a follow-up, SEAMLESSLY TRANSITION to the 'Next Planned Topic/Question'.
               - Your bridge should be warm and bridge the old topic to the new one.
            3. **Brevity**: Strictly 1-2 concise sentences total for your entire response. No paragraphs. No robotic filler.
            
            OUTPUT RULES:
            - Output strictly valid JSON.
            - "feedback": Your conversational response (Sweet Reaction + Seamless Bridge/Question).
            - "follow_up_question": A BRIEF follow-up only if they left a "deep dive" hook, otherwise NULL to proceed to the next planned topic.
            - No markdown, no extra text.
            
            JSON FORMAT:
            {{
                "feedback": "...",
                "follow_up_question": "..."
            }}
            """
            
            response = model.generate_content(prompt)
            clean_response = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_response)
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"CRITICAL Gemini Error: {str(e)}")
            traceback.print_exc()
            # Even if API fails, we want empathetic fallback
            fallback_feedback = "I hear you. It's perfectly fine if that's a bit unclear for now—interviews can be high-pressure! Let's just pivot to a different topic. Here's the next one for you:"
            return Response({
                "feedback": fallback_feedback,
                "follow_up_question": None
            }, status=status.HTTP_200_OK)
