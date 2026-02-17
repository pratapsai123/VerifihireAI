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
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class ResumeMatchView(APIView):
    def post(self, request):
        resume_file = request.FILES.get('resume')
        job_description = request.data.get('job_description')

        if not resume_file or not job_description:
            return Response({"error": "Both resume and job description are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
            resume_text = ""
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
            
            Format the output strictly as a raw JSON object with these keys: "match_percentage", "is_eligible", "summary".
            Do not include any markdown formatting or extra text.
            """

            response = model.generate_content(prompt)
            clean_response = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_response)

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CandidateListCreateView(generics.ListCreateAPIView):
    queryset = Candidate.objects.all().order_by('-created_at')
    serializer_class = CandidateSerializer

class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
