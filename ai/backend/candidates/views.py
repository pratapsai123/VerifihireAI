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
from django.core.mail import send_mail
from django.conf import settings

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class ResumeMatchView(APIView):
    def post(self, request):
        resume_file = request.FILES.get('resume')
        job_description = request.data.get('job_description')

        if not resume_file or not job_description:
            return Response({"error": "Both resume and job description are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Get list of files
            resume_files = request.FILES.getlist('resume')
            results = []

            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return Response({"error": "Backend missing API Key"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash-lite')

            for resume_file in resume_files:
                try:
                    # Extract text
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                    resume_text = ""
                    for page in pdf_reader.pages:
                        resume_text += page.extract_text()

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
                    
                    Format the output strictly as a raw JSON object with these keys: "match_percentage", "is_eligible", "summary".
                    Do not include any markdown formatting or extra text.
                    """

                    response = model.generate_content(prompt)
                    clean_response = response.text.replace("```json", "").replace("```", "").strip()
                    
                    try:
                        result_data = json.loads(clean_response)
                        # Add filename for frontend identification
                        result_data['filename'] = resume_file.name
                        results.append(result_data)
                    except json.JSONDecodeError:
                        # Fallback parsing
                        start = clean_response.find('{')
                        end = clean_response.rfind('}') + 1
                        if start != -1 and end != -1:
                            result_data = json.loads(clean_response[start:end])
                            result_data['filename'] = resume_file.name
                            results.append(result_data)
                        else:
                            results.append({
                                "filename": resume_file.name,
                                "error": "Failed to parse AI response"
                            })

                except Exception as file_error:
                    results.append({
                        "filename": resume_file.name,
                        "error": str(file_error)
                    })

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CandidateListCreateView(generics.ListCreateAPIView):
    queryset = Candidate.objects.all().order_by('-created_at')
    serializer_class = CandidateSerializer

class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

class SendInviteView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        link = request.data.get('link')
        job_description = request.data.get('job_description', '')

        if not name or not email or not link:
            return Response({"error": "Name, email, and link are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subject = f"Interview Invitation for {name}"
            message = f"""Dear {name},

We are pleased to invite you to an AI-powered interview.

Please click the link below to start your interview session:
{link}

The session will take approximately 10-15 minutes.

Best regards,
Recruiting Team
"""
            
            # Use console backend if no SMTP settings provided (fail safe for demo)
            # But try real send first
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({"message": "Invite sent successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            # If SMTP fails, we can return the error so the frontend knows
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
