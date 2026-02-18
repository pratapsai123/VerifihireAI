import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Assessment, AIAssessmentSubmission
import json
import uuid

from django.conf import settings

class SubmitAssessmentView(APIView):
    def post(self, request):
        data = request.data
        token = data.get('token')
        name = data.get('name')
        email = data.get('email')
        answers = data.get('answers', {})

        if not token or not name or not email:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assessment = Assessment.objects.get(share_token=token)
            
            # Simple grading logic for MCQs
            score = 0
            generated_content = assessment.generated_content or {}
            mcqs = generated_content.get('mcqs', [])
            
            # Grading
            for i, mcq in enumerate(mcqs):
                correct_ans = mcq.get('answer', '').strip().upper()
                candidate_ans = answers.get(f'mcq_{i}', '').strip().upper()
                if candidate_ans == correct_ans:
                    score += 1

            total_q = len(mcqs)
            percentage = (score / total_q * 100) if total_q > 0 else 0
            
            # Monitoring Data
            integrity_score = data.get('integrity_score', 100.0)
            tab_switches = data.get('tab_switches', 0)
            face_warnings = data.get('face_warnings', 0)
            phone_warnings = data.get('phone_warnings', 0)
            
            # Determine status (Threshold 60% AND Integrity > 80%)
            pass_status = 'selected' if percentage >= 60 and integrity_score >= 80 else 'rejected'

            submission = AIAssessmentSubmission.objects.create(
                assessment=assessment,
                candidate_name=name,
                candidate_email=email,
                answers=answers,
                score=score,
                total_questions=total_q,
                percentage=percentage,
                status=pass_status,
                integrity_score=integrity_score,
                tab_switches=tab_switches,
                face_warnings=face_warnings,
                phone_warnings=phone_warnings
            )

            return Response({
                "message": "Assessment submitted successfully",
                "submission_id": submission.id,
                "score": score,
                "total": total_q,
                "percentage": percentage,
                "status": pass_status
            }, status=status.HTTP_201_CREATED)

        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Configure Gemini
api_key = getattr(settings, 'GEMINI_API_KEY', None)
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)

class GenerateAssessmentView(APIView):
    def post(self, request):
        data = request.data
        job_description = data.get('job_description')
        required_skills = data.get('required_skills')
        mcq_count = data.get('mcq_count', 10)
        coding_count = data.get('coding_count', 2)
        duration = data.get('duration', 60)

        if not job_description or not required_skills:
            return Response({
                "error": "Missing job_description or required_skills",
                "message": "Both fields are required to generate an assessment."
            }, status=status.HTTP_400_BAD_REQUEST)

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
            
            if not response or not response.text:
                 raise Exception("Gemini returned an empty response or was blocked.")

            # Clean response if it contains markdown code blocks
            clean_response = response.text.replace("```json", "").replace("```", "").strip()
            
            generated_data = json.loads(clean_response)

            # 3. Update DB with generated content
            assessment.generated_content = generated_data
            assessment.status = 'SCHEDULED'
            assessment.save()

            return Response({
                "id": assessment.id,
                "message": "Assessment generated successfully",
                "data": generated_data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Update status if failed
            assessment.status = 'FAILED'
            assessment.save()
            
            return Response({
                "error": str(e), 
                "message": "Failed to generate AI content. Please check API key or prompt constraints."
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
                "generated_content": assessment.generated_content,
                "status": assessment.status,
                "share_token": str(assessment.share_token)
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
                "generated_content": assessment.generated_content,
                "status": assessment.status,
                "share_token": str(assessment.share_token)
            }
            return Response(data, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

class PublicAssessmentView(APIView):
    def get(self, request, token):
        try:
            assessment = Assessment.objects.get(share_token=token)
            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": assessment.generated_content,
                "status": assessment.status
            }
            return Response(data, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
