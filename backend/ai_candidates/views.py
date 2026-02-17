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
        candidate_id = request.data.get('candidate_id')
        job_description = request.data.get('job_description')

        if (not resume_file and not candidate_id) or not job_description:
            return Response({"error": "Job description and either resume or candidate_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resume_text = ""
            
            # Case 1: File Upload
            if resume_file:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
            
            # Case 2: Existing Candidate
            elif candidate_id:
                try:
                    candidate = Candidate.objects.get(id=candidate_id)
                    # Open the file from storage
                    with candidate.resume.open('rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            resume_text += page.extract_text()
                except Candidate.DoesNotExist:
                     return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                     return Response({"error": f"Error reading candidate resume: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Create Candidate record if new upload
            candidate_obj = None
            if resume_file:
                # Basic creation - could be enhanced with parsing
                candidate_obj = Candidate.objects.create(
                    full_name=resume_file.name.replace('.pdf', ''), # Placeholder name
                    email="pending@example.com", # Placeholder
                    job_title="Applicant", # Placeholder
                    resume=resume_file,
                    status='New'
                )
                candidate_id = candidate_obj.id
            elif candidate_id:
                try:
                    candidate_obj = Candidate.objects.get(id=candidate_id)
                except Candidate.DoesNotExist:
                    pass

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
