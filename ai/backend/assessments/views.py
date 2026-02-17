import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Assessment
import json

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class GenerateAssessmentView(APIView):
    def post(self, request):
        data = request.data
        job_description = data.get('job_description')
        required_skills = data.get('required_skills')
        mcq_count = data.get('mcq_count', 10)
        coding_count = data.get('coding_count', 2)
        duration = data.get('duration', 60)

        # 1. Save request to DB (Initial record)
        assessment = Assessment.objects.create(
            job_description=job_description,
            required_skills=required_skills,
            mcq_count=mcq_count,
            coding_count=coding_count,
            duration_minutes=duration
        )

        try:
            # 2. Call Gemini API
            # 2. Call Gemini API
            model = genai.GenerativeModel('gemini-flash-latest')
            
            prompt = f"""
            Act as an expert technical recruiter. Create a technical assessment for a candidate based on the following:
            
            Job Description: {job_description}
            Required Skills: {required_skills}
            
            Please generate:
            - {mcq_count} Multiple Choice Questions (MCQs) with 4 options and the correct answer.
            - {coding_count} Coding Challenges with a problem statement and example input/output.
            
            Output the response strictly in valid JSON format with the following structure:
            {{
                "mcqs": [
                    {{ "question": "...", "options": ["A", "B", "C", "D"], "answer": "..." }}
                ],
                "coding_challenges": [
                    {{ "title": "...", "problem": "...", "example": "..." }}
                ]
            }}
            Do not include markdown formatting like ```json ... ```. Just the raw JSON.
            """

            response = model.generate_content(prompt)
            
            # Clean response if it contains markdown code blocks
            clean_response = response.text.replace("```json", "").replace("```", "").strip()
            
            generated_data = json.loads(clean_response)

            # 3. Update DB with generated content
            assessment.generated_content = generated_data
            assessment.save()

            return Response({
                "id": assessment.id,
                "message": "Assessment generated successfully",
                "data": generated_data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # In case of error (e.g. invalid API key), return error but save what we have
            return Response({
                "error": str(e), 
                "message": "Failed to generate AI content. Please check API key."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AssessmentListView(APIView):
    def get(self, request):
        assessments = Assessment.objects.all().order_by('-created_at')
        data = []
        for assessment in assessments:
            data.append({
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": assessment.generated_content
            })
        return Response(data, status=status.HTTP_200_OK)

class AssessmentDetailView(APIView):
    def get(self, request, pk):
        try:
            assessment = Assessment.objects.get(pk=pk)
            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": assessment.generated_content
            }
            return Response(data, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
