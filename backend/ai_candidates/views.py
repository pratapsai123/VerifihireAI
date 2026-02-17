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

# Configure Gemini
from django.conf import settings
from django.core.mail import send_mail
import pandas as pd
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

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
            
            prompt = f"""
            Act as an expert technical recruiter. Analyze the match between the following resume and job description.
            
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
        current_question = request.data.get('question')
        answer = request.data.get('answer')
        
        if not current_question or not answer:
             return Response({'error': 'Missing question or answer'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            prompt = f"""
            Act as an experienced technical interviewer conducting a live video interview.
            
            Current Question: "{current_question}"
            Candidate's Answer: "{answer}"
            
            Your Task:
            1. Analyze the candidate's answer.
            2. Generate a natural, conversational response ("feedback"). 
               - If the answer is good, acknowledge a specific detail they mentioned.
               - If the candidate says "I don't know" or is unsure, be encouraging (e.g., "That's perfectly fine, it's a specific topic."). Do NOT ask a follow-up question.
               - If the answer is vague but they seem to know something, ask for clarification.
            3. Decide if a follow-up question is needed immediately.
               - RETURN NULL for follow_up_question if the candidate said "I don't know".
            
            Output strictly valid JSON:
            {{
                "feedback": "Your conversational reaction here.",
                "follow_up_question": "The follow-up question if needed, otherwise null"
            }}
            Do not include Markdown formatting.
            """
            
            response = model.generate_content(prompt)
            clean_response = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_response)
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Fallback if AI fails
            return Response({
                "feedback": "Thank you for that answer.",
                "follow_up_question": None
            }, status=status.HTTP_200_OK)
