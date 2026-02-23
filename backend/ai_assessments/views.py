import os
from groq import Groq
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
from .models import Assessment, AIAssessmentSubmission
from ai_candidates.views import extract_json
import traceback

from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
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
            submission = AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email=email,
                status='ONGOING'
            ).order_by('-id').first()

            if not submission:
                # Fallback in case intake failed but we have data
                submission = AIAssessmentSubmission.objects.create(
                    assessment=assessment,
                    candidate_name=name,
                    candidate_email=email,
                    status='ONGOING'
                )

            # Simple grading logic for MCQs
            score = 0
            generated_content = assessment.generated_content or {}
            mcqs = generated_content.get('mcqs', [])
            
            for i, mcq in enumerate(mcqs):
                correct_ans = str(mcq.get('answer') or '').strip().upper()
                candidate_ans = str(answers.get(f'mcq_{i}') or '').strip().upper()
                if correct_ans and candidate_ans == correct_ans:
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
            submission.submitted_at = timezone.now()
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
            logger.error(f"SUMBISSION ERROR: {str(e)}\n{traceback.format_exc()}")
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
                difficulty_level=difficulty,
                available_from=data.get('available_from'),
                available_until=data.get('available_until')
            )

            # Cap overly ambitious coding counts to prevent AI hallucinations/timeouts
            safe_coding_count = min(coding_count, 3)

            prompt = f"""
            Act as an expert technical recruiter. Create a {difficulty} difficulty technical assessment.
            Job Description: {job_description}
            Required Skills: {required_skills}
            
            TASK 1: Generate {mcq_count} Multiple Choice Questions (MCQs).
            Each MCQ object must have:
            - "question": string
            - "options": list of 4 strings
            - "answer": string (must match one of the options exactly)

            TASK 2: Generate {safe_coding_count} Coding Challenges.
            Each challenge object must have:
            - "title": string
            - "problem_statement": string (DETAILED description, at least 2 paragraphs, explaining the scenario, edge cases, and requirements clearly like LeetCode/HackerRank)
            - "input_format": string (e.g., "The first line contains an integer N...")
            - "output_format": string (e.g., "Return a list of integers...")
            - "constraints": list of strings (e.g., "1 <= N <= 10^5")
            - "example_input": string (e.g., "5\\n1 2 3 4 5")
            - "example_output": string (e.g., "15")
            - "explanation": string (Step-by-step logic for the example)
               - "starter_code_java": string (MUST be a complete class structure with imports, e.g., "import java.util.*;\nclass Solution {{\n    public static int solve(int[] arr) {{\n        // Write logic here\n        return 0;\n    }}\n}}")
               - "starter_code_python": string (MUST be a function definition, e.g., "def solve(arr):\n    # Write logic here\n    pass")
               - "test_cases": list of at least 5 objects for hidden evaluation: {{ "input": "...", "output": "..." }}
            
            Format the output strictly as a raw JSON object with these keys: "mcqs", "coding_challenges".Ensure Java code is wrapped in a 'Solution' or 'Main' class.
            """

            logger.info(f"Using Groq for {difficulty} Assessment Generation")
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content
            logger.info(f"GROQ RAW RESPONSE: {raw_text}")

            if not raw_text:
                raise Exception("Empty response from AI engine")

            generated_data = extract_json(raw_text)
            if not generated_data:
                logger.error(f"Failed JSON extraction from: {raw_text}")
                raise Exception("The AI generated a response but the structure was invalid. Please try again.")

            assessment.generated_content = generated_data
            assessment.status = 'SCHEDULED'
            assessment.save()

            return Response({
                "id": assessment.id,
                "message": "Assessment generated successfully",
                "data": generated_data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            tb = traceback.format_exc()
            raw_resp = locals().get('raw_text', 'No response received')
            logger.error(f"ERROR in GenerateAssessmentView: {str(e)}\n{tb}\nRAW: {raw_resp}")
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
            
            # Availability Guard
            now = timezone.now()
            if assessment.available_from and now < assessment.available_from:
                return Response({"error": "This assessment is not yet available."}, status=status.HTTP_400_BAD_REQUEST)
            if assessment.available_until and now > assessment.available_until:
                return Response({"error": "This assessment has expired."}, status=status.HTTP_400_BAD_REQUEST)

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
            count = AIAssessmentSubmission.objects.filter(assessment=assessment).count()
            # Use available_until as expiry if present, else fallback to 7 days
            if assessment.available_until:
                expiry_at = assessment.available_until
            else:
                expiry_at = assessment.created_at + timedelta(days=7)

            data.append({
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "expiry_at": expiry_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": assessment.generated_content,
                "status": assessment.status,
                "share_token": str(assessment.share_token),
                "candidate_count": count,
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None
            })
        return Response(data, status=status.HTTP_200_OK)

class AssessmentDetailView(APIView):
    def get(self, request, pk):
        try:
            assessment = Assessment.objects.get(pk=pk)
            submissions = AIAssessmentSubmission.objects.filter(assessment=assessment).order_by('-submitted_at')
            
            submission_data = []
            for sub in submissions:
                submission_data.append({
                    "id": sub.id,
                    "candidate_name": sub.candidate_name,
                    "candidate_email": sub.candidate_email,
                    "score": sub.score,
                    "total_questions": sub.total_questions,
                    "percentage": sub.percentage,
                    "status": sub.status,
                    "integrity_score": sub.integrity_score,
                    "answers": sub.answers,
                    "submitted_at": sub.submitted_at.strftime("%Y-%m-%d %H:%M")
                })

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
                "share_token": str(assessment.share_token),
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None,
                "submissions": submission_data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            assessment = Assessment.objects.get(pk=pk)
            assessment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Assessment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

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
                "status": assessment.status,
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None
            }
            return Response(data, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
class InviteAssessmentCandidatesView(APIView):
    def post(self, request):
        assessment_id = request.data.get('assessment_id')
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

        invite_type = request.data.get('type')  # 'individual' or 'bulk'
        invited_candidates = []
        
        # Use frontend base URL from settings
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        link = f"{base_url}/take-ai-assessment/{assessment.share_token}"

        if invite_type == 'individual':
            name = request.data.get('name')
            email = request.data.get('email')
            if not name or not email:
                return Response({"error": "Name and Email are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            invited_candidates.append({"name": name, "email": email, "link": link})
            
            # Send Email
            try:
                subject = f"Invite to AI Technical Assessment: {assessment.required_skills}"
                
                # Format availability dates
                start_time = assessment.available_from.strftime('%B %d, %Y at %I:%M %p') if assessment.available_from else "Immediately"
                end_time = assessment.available_until.strftime('%B %d, %Y at %I:%M %p') if assessment.available_until else "No fixed deadline"
                
                jd_preview = (assessment.job_description or '')[:200]
                
                # Plain text fallback
                message = f"Dear {name},\n\nYou have been invited to attempt an AI technical assessment for the role of {assessment.required_skills}.\n\nTiming Details:\n- Available From: {start_time}\n- Available Until: {end_time}\n- Duration: {assessment.duration_minutes} minutes\n\nPlease click the link below to start your assessment during the availability window:\n{link}\n\nBest of luck!"
                
                # HTML version
                html_message = f"""
                <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                    <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">Assessment Invitation</h1>
                    </div>
                    <div style="padding: 32px; background-color: white;">
                        <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{name}</strong>,</p>
                        <p style="line-height: 1.6; margin-bottom: 24px;">You have been invited to attempt an AI technical assessment for the role: <br/><strong>{assessment.required_skills}</strong></p>
                        
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                            <h3 style="margin-top: 0; color: #4318FF; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>
                            <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {start_time}</p>
                            <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {end_time}</p>
                            <p style="margin: 8px 0; font-size: 14px;"><strong>⏱️ Duration:</strong> {assessment.duration_minutes} minutes</p>
                        </div>
                        
                        <div style="text-align: center; margin: 32px 0;">
                            <a href="{link}" style="background-color: #4318FF; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(67, 24, 255, 0.2);">Start Assessment</a>
                        </div>
                        
                        <p style="font-size: 13px; color: #64748b; margin-top: 32px; border-top: 1px solid #f1f5f9; pt: 16px;">If the button above doesn't work, copy and paste this link into your browser:<br/>
                        <a href="{link}" style="color: #4318FF;">{link}</a></p>
                    </div>
                    <div style="background-color: #f1f5f9; padding: 16px; text-align: center; font-size: 12px; color: #94a3b8;">
                        &copy; 2026 VerifiHireAI. All rights reserved.
                    </div>
                </div>
                """
                
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False, html_message=html_message)
                logger.info(f"Individual invite sent to {email}")
            except Exception as e:
                import traceback
                logger.error(f"Email error for {email}: {str(e)}")
                logger.error(traceback.format_exc())
                return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        elif invite_type == 'bulk':
            file = request.FILES.get('file')
            if not file:
                return Response({"error": "File is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                import pandas as pd
                if file.name.lower().endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                df.columns = df.columns.str.lower().str.strip()
                if 'name' not in df.columns or 'email' not in df.columns:
                    return Response({"error": "File must have 'name' and 'email' columns"}, status=status.HTTP_400_BAD_REQUEST)

                for _, row in df.iterrows():
                    name = str(row['name']).strip()
                    email = str(row['email']).strip()
                    invited_candidates.append({"name": name, "email": email, "link": link})
                    
                    try:
                        subject = f"Invite to AI Technical Assessment: {assessment.required_skills}"
                        
                        start_time = assessment.available_from.strftime('%B %d, %Y at %I:%M %p') if assessment.available_from else "Immediately"
                        end_time = assessment.available_until.strftime('%B %d, %Y at %I:%M %p') if assessment.available_until else "No fixed deadline"

                        message = f"Dear {name},\n\nYou have been invited to attempt an AI technical assessment for the role: {assessment.required_skills}.\n\nTiming Details:\n- Available From: {start_time}\n- Available Until: {end_time}\n- Duration: {assessment.duration_minutes} minutes\n\nLink: {link}\n\nGood luck!"
                        
                        html_message = f"""
                        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                            <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                                <h1 style="color: white; margin: 0; font-size: 24px;">Assessment Invitation</h1>
                            </div>
                            <div style="padding: 32px; background-color: white;">
                                <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{name}</strong>,</p>
                                <p style="line-height: 1.6; margin-bottom: 24px;">You have been invited to attempt an AI technical assessment for the role: <br/><strong>{assessment.required_skills}</strong></p>
                                
                                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                                    <h3 style="margin-top: 0; color: #4318FF; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>
                                    <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {start_time}</p>
                                    <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {end_time}</p>
                                    <p style="margin: 8px 0; font-size: 14px;"><strong>⏱️ Duration:</strong> {assessment.duration_minutes} minutes</p>
                                </div>
                                
                                <div style="text-align: center; margin: 32px 0;">
                                    <a href="{link}" style="background-color: #4318FF; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(67, 24, 255, 0.2);">Start Assessment</a>
                                </div>
                                
                                <p style="font-size: 13px; color: #64748b; margin-top: 32px; border-top: 1px solid #f1f5f9; pt: 16px;">If the button above doesn't work, copy and paste this link into your browser:<br/>
                                <a href="{link}" style="color: #4318FF;">{link}</a></p>
                            </div>
                            <div style="background-color: #f1f5f9; padding: 16px; text-align: center; font-size: 12px; color: #94a3b8;">
                                &copy; 2026 VerifiHireAI. All rights reserved.
                            </div>
                        </div>
                        """

                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False, html_message=html_message)
                        logger.info(f"Bulk invite sent to {email}")
                    except Exception as mail_err:
                        logger.error(f"Bulk email error for {email}: {mail_err}")
            except Exception as e:
                return Response({"error": f"Error parsing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": f"Successfully invited {len(invited_candidates)} candidates",
            "count": len(invited_candidates)
        }, status=status.HTTP_200_OK)
import requests

from rest_framework.permissions import AllowAny

class ProxyCodeExecuteView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        try:
            language = request.data.get('language')
            files = request.data.get('files', [])
            stdin = request.data.get('stdin', '')
            code = files[0]['content'] if files else ''

            # Specific Auto-fix for Java unnamed class error (preview feature)
            if language == 'java':
                # Automatically add util imports
                if "import java.util" not in code:
                    code = "import java.util.*;\nimport java.io.*;\n" + code

                # If no class declaration exists but methods are present
                if "class " not in code:
                    # Check for main method, if not present, try to add a dummy runner
                    runner = ""
                    if "public static void main" not in code:
                       # Try to find a method to call - naive approach
                       # better approach: just wrap it and let user define main or use JShell mode if supported (Wandbox doesn't support JShell easily)
                       # For now, we wrap the code in a class. The user MUST have a main method or we add one that does nothing to at least compile.
                       runner = "\n    public static void main(String[] args) { \n        // Test your method here \n    }"
                    
                    code = f"public class Main {{\n{code}\n{runner}\n}}"
            
            # Map to Wandbox compilers
            compiler = 'gcc-head' # Default
            if language == 'python':
                compiler = 'cpython-3.10.15'
            elif language == 'java':
                compiler = 'openjdk-jdk-21+35'
            elif language == 'javascript':
                compiler = 'nodejs-20.17.0'
            elif language in ['cpp', 'c++']:
                compiler = 'gcc-10.5.0'

            payload = {
                "compiler": compiler,
                "code": code,
                "stdin": stdin,
                "save": False
            }

            # Wandbox API
            wb_url = 'https://wandbox.org/api/compile.json'
            response = requests.post(wb_url, json=payload, timeout=15)
            wb_data = response.json()
            
            # Map Wandbox response to Piston format for frontend compatibility
            # Wandbox returns: status (str), program_message (stdout), program_error (stderr), compiler_error
            
            stdout = wb_data.get('program_message', '') or wb_data.get('program_output', '')
            stderr = wb_data.get('program_error', '') or wb_data.get('compiler_error', '')
            status_code = wb_data.get('status', '1')
            
            try:
                exit_code = int(status_code)
            except:
                exit_code = 1

            piston_response = {
                "run": {
                    "stdout": stdout,
                    "stderr": stderr,
                    "code": exit_code,
                    "output": stdout + stderr
                }
            }

            return Response(piston_response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Code Execution Proxy Error: {str(e)}")
            return Response({
                "run": {
                    "stdout": "",
                    "stderr": f"Execution Error: {str(e)}",
                    "code": 1
                }
            }, status=status.HTTP_200_OK) # Return 200 so frontend parses the error in 'run'

class AIAssessmentSubmissionDetailView(generics.RetrieveDestroyAPIView):
    queryset = AIAssessmentSubmission.objects.all()
    # serializer_class = ... # Not strictly needed for simple delete, but good practice
    permission_classes = [AllowAny]
