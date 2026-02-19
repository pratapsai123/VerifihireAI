import os
from groq import Groq
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
import traceback
from .models import Assessment, AIAssessmentSubmission
from ai_candidates.views import extract_json

from django.conf import settings
import logging

# Setup Logger
logger = logging.getLogger(__name__)

# Configure Groq
groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
if not groq_api_key:
    raise ValueError("GROQ_API_KEY must be set in settings.py")
groq_client = Groq(api_key=groq_api_key)

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
            
            # Find the existing ongoing submission from intake
            try:
                submission = AIAssessmentSubmission.objects.get(
                    assessment=assessment,
                    candidate_email=email,
                    status='ONGOING'
                )
            except AIAssessmentSubmission.DoesNotExist:
                # Fallback in case intake failed but we have data
                submission = AIAssessmentSubmission.objects.create(
                    assessment=assessment,
                    candidate_name=name,
                    candidate_email=email
                )

            # Simple grading logic for MCQs
            score = 0
            generated_content = assessment.generated_content or {}
            mcqs = generated_content.get('mcqs', [])
            
            for i, mcq in enumerate(mcqs):
                correct_ans = mcq.get('answer', '').strip().upper()
                candidate_ans = answers.get(f'mcq_{i}', '').strip().upper()
                if candidate_ans == correct_ans:
                    score += 1

            total_q = len(mcqs)
            percentage = (score / total_q * 100) if total_q > 0 else 0
            
            # Final integrity check
            pass_status = 'selected' if percentage >= 60 and submission.integrity_score >= 70 else 'rejected'

            submission.answers = answers
            submission.score = score
            submission.total_questions = total_q
            submission.percentage = percentage
            submission.status = pass_status
            submission.save()

            return Response({
                "message": "Assessment submitted successfully",
                "submission_id": submission.id,
                "score": score,
                "total": total_q,
                "percentage": percentage,
                "status": pass_status
            }, status=status.HTTP_200_OK)

        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateAssessmentView(APIView):
    def post(self, request):
        data = request.data
        job_description = data.get('job_description')
        required_skills = data.get('required_skills')
        difficulty = data.get('difficulty', 'Medium')
        try:
            mcq_count = int(data.get('mcq_count', 10))
            coding_count = int(data.get('coding_count', 2))
            duration = int(data.get('duration', 60))
        except (ValueError, TypeError):
            mcq_count, coding_count, duration = 10, 2, 60

        if not job_description or not required_skills:
            return Response({
                "error": "Missing job_description or required_skills",
                "message": "Both fields are required to generate an assessment."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            assessment = Assessment.objects.create(
                job_description=job_description,
                required_skills=required_skills,
                mcq_count=mcq_count,
                coding_count=coding_count,
                duration_minutes=duration,
                difficulty_level=difficulty
            )

            prompt = f"""
            Act as an expert technical recruiter. Create a {difficulty} difficulty technical assessment for a candidate based on the following:
            Job Description: {job_description}
            Required Skills: {required_skills}
            
            Generate:
            1. {mcq_count} Multiple Choice Questions (MCQs). Each MCQ must have:
               - "question": string
               - "options": list of 4 strings
               - "answer": string (must match one of the options exactly)
            2. {coding_count} Coding Challenges. Each challenge must have:
               - "title": string
               - "problem_statement": string
               - "constraints": list of strings
               - "starter_code": string
            
            Format the output strictly as a raw JSON object with these keys: "mcqs", "coding_challenges".
            """

            logger.info(f"Using Groq for {difficulty} Assessment Generation")
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content

            if not raw_text:
                 raise Exception("Groq returned an empty response.")

            generated_data = extract_json(raw_text)
            if not generated_data:
                 raise Exception(f"Failed to parse AI response as JSON.")

            assessment.generated_content = generated_data
            assessment.status = 'SCHEDULED'
            assessment.save()

            return Response({
                "id": assessment.id,
                "message": "Assessment generated successfully",
                "data": generated_data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"ERROR in GenerateAssessmentView: {str(e)}")
            if 'assessment' in locals() and assessment:
                assessment.status = 'FAILED'
                assessment.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateSubmissionView(APIView):
    def post(self, request):
        token = request.data.get('share_token')
        name = request.data.get('candidate_name')
        email = request.data.get('candidate_email')

        if not all([token, name, email]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assessment = Assessment.objects.get(share_token=token)
            submission = AIAssessmentSubmission.objects.create(
                assessment=assessment,
                candidate_name=name,
                candidate_email=email,
                status='ONGOING'
            )
            return Response({
                "submission_id": submission.id,
                "status": "success"
            }, status=status.HTTP_201_CREATED)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

class UpdateAssessmentIntegrityView(APIView):
    def post(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
            event_type = request.data.get('event_type')
            
            if event_type == 'tab_switch':
                submission.tab_switches += 1
            elif event_type == 'phone_detection':
                submission.phone_warnings += 1
            elif event_type == 'face_detection_lost':
                submission.face_warnings += 1
            
            # Simple penalty system
            total_violations = (
                submission.tab_switches * 10 + 
                submission.phone_warnings * 30 + 
                submission.face_warnings * 5
            )
            submission.integrity_score = max(0, 100 - total_violations)
            submission.save()
            
            return Response({
                "status": "success",
                "integrity_score": submission.integrity_score
            })
        except AIAssessmentSubmission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

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
