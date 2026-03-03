import os
from groq import Groq
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
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

from api.views import ensure_role_exists

# Configure Groq
# groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
# if not groq_api_key:
#     raise ValueError("GROQ_API_KEY must be set in settings.py")
# groq_client = Groq(api_key=groq_api_key)

class SubmitAssessmentView(APIView):
    def post(self, request):
        data = request.data
        token = data.get('token')
        name = data.get('name')
        email = data.get('email', '').strip().lower()
        answers = data.get('answers', {})
        coding_results = data.get('codingResults', {}) # Captured test case results

        if not token or not name or not email:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assessment = Assessment.objects.get(share_token=token)
            
            # Absolute block against submitting multiple times
            if AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                submitted_at__isnull=False
            ).exists():
                return Response(
                    {"error": "You have already completed this assessment and cannot retake it."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            submission = AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                status='ONGOING'
            ).order_by('-id').first()

            if not submission:
                submission = AIAssessmentSubmission.objects.create(
                    assessment=assessment,
                    candidate_name=name,
                    candidate_email=email,
                    status='ONGOING'
                )

            generated_content = assessment.generated_content or {}
            
            # Unwrap historic nested dictionaries from Llama-3.1
            if 'mcqs' not in generated_content and 'coding_challenges' not in generated_content:
                for key, val in generated_content.items():
                    if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                        generated_content = val
                        break

            mcqs = generated_content.get('mcqs', [])
            coding_challenges = generated_content.get('coding_challenges', [])
            
            total_possible_points = assessment.total_points or 0
            possible_mcq_points = 0
            possible_coding_points = 0
            candidate_mcq_points = 0
            candidate_coding_points = 0
            
            # Difficulty weights
            weight_map = {'Easy': 100, 'Medium': 200, 'Hard': 300}

            # 1. MCQ Scoring - Fixed 20 points per question
            for i, mcq in enumerate(mcqs):
                weight = 20
                possible_mcq_points += weight
                
                correct_ans = str(mcq.get('answer') or '').strip().upper()
                candidate_ans = str(answers.get(f'mcq_{i}') or '').strip().upper()
                
                if correct_ans and candidate_ans == correct_ans:
                    candidate_mcq_points += weight

            # 2. Coding Challenge Scoring
            for i, challenge in enumerate(coding_challenges):
                difficulty = challenge.get('difficulty', 'Medium')
                weight = weight_map.get(difficulty, 200)
                possible_coding_points += weight
                
                res = coding_results.get(str(i))
                if res:
                    passed = res.get('passed', 0)
                    total_tc = res.get('total', 1)
                    if total_tc > 0:
                        score_fraction = passed / total_tc
                        candidate_coding_points += (score_fraction * weight)

            candidate_total_points = candidate_mcq_points + candidate_coding_points
            
            # Always use the sum of calculated potential points for the denominator
            total_possible_points = possible_mcq_points + possible_coding_points

            if total_possible_points > 0:
                percentage = round((candidate_total_points / total_possible_points) * 100)
            else:
                percentage = 0
            
            pass_status = 'selected' if percentage >= assessment.pass_threshold and submission.integrity_score >= 70 else 'rejected'

            submission.answers = answers
            submission.mcq_score = round(candidate_mcq_points)
            submission.coding_score = round(candidate_coding_points)
            submission.score = round(candidate_total_points)
            submission.total_questions = len(mcqs) + len(coding_challenges)
            submission.percentage = percentage
            submission.status = pass_status
            submission.results_breakdown = {
                "mcq": {"scored": round(candidate_mcq_points), "total": possible_mcq_points},
                "coding": {"scored": round(candidate_coding_points), "total": possible_coding_points},
                "total_possible": total_possible_points
            }
            submission.submitted_at = timezone.now()
            submission.save()

            # After successful save, ensure we return no-cache headers to the submission confirmation
            response_data = {
                "message": "Assessment submitted successfully",
                "submission_id": submission.id,
                "score": submission.score,
                "mcq_score": submission.mcq_score,
                "coding_score": submission.coding_score,
                "total_possible_points": total_possible_points,
                "percentage": percentage,
                "status": pass_status
            }
            response = Response(response_data, status=status.HTTP_200_OK)
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response

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
        
        # Granular inputs from new UI
        mcq_easy = int(data.get('mcq_easy', 5))
        mcq_medium = int(data.get('mcq_medium', 3))
        mcq_hard = int(data.get('mcq_hard', 2))
        coding_tasks = data.get('coding_tasks', ['Medium']) # List of difficulties
        duration = int(data.get('duration', 60))
        total_possible_points = int(data.get('total_possible_points', 1000))
        
        mcq_count = mcq_easy + mcq_medium + mcq_hard
        coding_count = len(coding_tasks)

        if not job_description or not required_skills:
            return Response({
                "error": "Missing job_description or required_skills",
                "message": "Both fields are required to generate an assessment."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Auto-persist role if title is provided
            # required_skills often contains the role title in this app's context
            job_title = data.get('job_title') or data.get('role_title') or required_skills
            if job_title:
                ensure_role_exists(job_title, job_description, user=request.user)

            assessment = Assessment.objects.create(
                job_description=job_description,
                required_skills=required_skills,
                mcq_count=mcq_count,
                coding_count=coding_count,
                duration_minutes=duration,
                total_points=total_possible_points,
                available_from=data.get('available_from'),
                available_until=data.get('available_until'),
                pass_threshold=data.get('pass_threshold', 60)
            )

            # Build a very specific prompt based on the granular breakdown
            mcq_prompt = f"TASK 1: Generate {mcq_count} Multiple Choice Questions (MCQs).\n"
            mcq_prompt += f"- {mcq_easy} Easy questions\n"
            mcq_prompt += f"- {mcq_medium} Medium questions\n"
            mcq_prompt += f"- {mcq_hard} Hard questions\n"
            mcq_prompt += "Each MCQ object must have: 'question', 'options' (list of 4), 'answer', and 'difficulty' (Easy/Medium/Hard)."

            coding_prompt = ""
            keys_expected = '"mcqs"'
            if coding_count > 0:
                coding_prompt = f"TASK 2: Generate {coding_count} Coding Challenges.\n"
                for i, diff in enumerate(coding_tasks):
                    coding_prompt += f"- Challenge {i+1}: {diff} difficulty\n"
                coding_prompt += "Each challenge object must have: 'title', 'problem_statement' (detailed), 'input_format', 'output_format', 'constraints', 'example_input', 'example_output', 'explanation', 'starter_code_java', 'starter_code_python', 'difficulty' (must match requested), and 'test_cases' (list of 5 objects)."
                keys_expected = '"mcqs", "coding_challenges"'

            prompt = f"""
            Act as an expert technical recruiter. Create a comprehensive technical assessment.
            Job Description: {job_description}
            Required Skills: {required_skills}
            
            {mcq_prompt}
            
            {coding_prompt}
            
            CRITICAL FORMATTING INSTRUCTION: 
            You MUST return a single JSON object where the root keys are EXACTLY: {keys_expected}.
            DO NOT wrap the output in any outer keys like "assessment" or "data".
            If a key represents 0 requested items, omit it or make it an empty list.
            """

            logger.info(f"Using Groq for Granular Assessment Generation ({total_possible_points} pts)")
            local_api_key = getattr(settings, 'GROQ_API_KEY', None)
            local_groq_client = Groq(api_key=local_api_key)
            
            response = local_groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content
            
            if not raw_text:
                raise Exception("Empty response from AI engine")

            generated_data = extract_json(raw_text)
            if not generated_data:
                raise Exception("The AI generated a response but the structure was invalid.")

            # === ENFORCE EXACT COUNTS - AI sometimes over-generates ===
            if 'mcqs' in generated_data and len(generated_data['mcqs']) > mcq_count:
                logger.warning(f"AI over-generated {len(generated_data['mcqs'])} MCQs, truncating to {mcq_count}")
                generated_data['mcqs'] = generated_data['mcqs'][:mcq_count]

            if 'coding_challenges' in generated_data and len(generated_data['coding_challenges']) > coding_count:
                logger.warning(f"AI over-generated {len(generated_data['coding_challenges'])} coding challenges, truncating to {coding_count}")
                generated_data['coding_challenges'] = generated_data['coding_challenges'][:coding_count]

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
        email = request.data.get('candidate_email', '').strip().lower()

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

            # Prevent re-testing if already completed (case-insensitive check)
            if AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                submitted_at__isnull=False
            ).exists():
                return Response(
                    {"error": "You have already completed this assessment and cannot retake it."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If an ONGOING session exists, reconnect the user instead of spawning a new one
            submission = AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                status='ONGOING'
            ).order_by('-id').first()

            if not submission:
                submission = AIAssessmentSubmission.objects.create(
                    assessment=assessment,
                    candidate_name=name,
                    candidate_email=email,
                    status='ONGOING'
                )
             
            # Calculate time left
            elapsed = timezone.now() - submission.started_at
            duration_seconds = assessment.duration_minutes * 60
            time_left = max(0, duration_seconds - int(elapsed.total_seconds()))
            
            if time_left <= 0:
                return Response({"error": "Assessment time has expired."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "submission_id": submission.id,
                "status": "success",
                "time_left": time_left,
                "answers": submission.answers,
                "current_question_index": submission.current_question_index
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
            
            # Simple metadata log
            submission.monitoring_logs.append({
                "event": event_type,
                "timestamp": timezone.now().isoformat()
            })
            
            # Grace Warning System Phase 2: Handle First 3 as Warnings
            if len(submission.warning_logs) < 3:
                submission.warning_logs.append(event_type)

            weights = {
                'tab_switch': 10,
                'phone_detection': 30,
                'face_detection_lost': 5
            }

            # Simple penalty system
            total_raw_penalty = (
                submission.tab_switches * weights['tab_switch'] + 
                submission.phone_warnings * weights['phone_detection'] + 
                submission.face_warnings * weights['face_detection_lost']
            )

            # Subtract the "free" penalty from the first 3 warnings
            free_penalty = sum(weights.get(w, 0) for w in submission.warning_logs)

            submission.integrity_score = max(0, 100 - (total_raw_penalty - free_penalty))
            submission.save()
            
            return Response({
                "status": "success",
                "integrity_score": submission.integrity_score
            })
        except AIAssessmentSubmission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

class SaveAssessmentProgressView(APIView):
    def post(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
            if submission.submitted_at:
                return Response({"error": "Already submitted"}, status=status.HTTP_400_BAD_REQUEST)
            
            answers = request.data.get('answers')
            index = request.data.get('current_question_index')
            
            if answers is not None:
                submission.answers = answers
            if index is not None:
                submission.current_question_index = index
            
            submission.save()
            return Response({"status": "progress saved"})
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
                    "mcq_score": sub.mcq_score,
                    "coding_score": sub.coding_score,
                    "results_breakdown": sub.results_breakdown,
                    "total_questions": sub.total_questions,
                    "percentage": sub.percentage,
                    "status": sub.status,
                    "integrity_score": sub.integrity_score,
                    "answers": sub.answers,
                    "submitted_at": sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else "In Progress"
                })

            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "difficulty_level": assessment.difficulty_level,
                "total_points": assessment.total_points,
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
        with open('api_debug.txt', 'a') as f:
            f.write(f"\n[{timezone.now()}] PUBLIC ACCESS: Token='{token}'\n")
            f.write(f"Query Params: {request.query_params}\n")
            f.write(f"Host: {request.get_host()}\n")

        try:
            assessment = Assessment.objects.get(share_token=token)
            gen_content = assessment.generated_content or {}
            
            # Robust extraction: Handle if it's a string or nested dict
            if isinstance(gen_content, str):
                import json
                try:
                    gen_content = json.loads(gen_content)
                except:
                    pass

            # Unwrap if it's a wrapper dict (like {"technical_assessment": {...}})
            if isinstance(gen_content, dict):
                # If it doesn't have the main keys but has a nested dict that does, unwrap it
                if 'mcqs' not in gen_content and 'coding_challenges' not in gen_content:
                    for val in gen_content.values():
                        if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                            gen_content = val
                            break
            # Second pass: if it's still a string (nested string), try one more parse
            if isinstance(gen_content, str):
                try:
                    gen_content = json.loads(gen_content)
                except:
                    pass

            # Check if this specific user email has already completed it (if passed via query param)
            email_param = request.query_params.get('email', '').strip().lower()
            already_completed = False
            if email_param:
                from .models import AIAssessmentSubmission
                already_completed = AIAssessmentSubmission.objects.filter(
                    assessment=assessment,
                    candidate_email__iexact=email_param,
                    submitted_at__isnull=False
                ).exists()

            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": gen_content,
                "status": assessment.status,
                "already_completed": already_completed,
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None
            }
            response = Response(data, status=status.HTTP_200_OK)
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response
        except Assessment.DoesNotExist:
            logger.error(f"PublicAssessmentView: Assessment not found for token {token}")
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
             logger.error(f"PublicAssessmentView Error: {str(e)}\n{traceback.format_exc()}")
             return Response({"error": "Invalid token or data structure"}, status=status.HTTP_400_BAD_REQUEST)
class InviteAssessmentCandidatesView(APIView):
    def post(self, request):
        assessment_id = request.data.get('assessment_id')
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

        invite_type = request.data.get('type')  # 'individual' or 'bulk'
        invited_candidates = []
        
        import urllib.parse
        # Use frontend base URL from settings - Standardized to localhost for dev
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'https://verifyhire.duckdns.org')
        base_link = f"{base_url}/take-ai-assessment/{assessment.share_token}"

        if invite_type == 'individual':
            name = request.data.get('name')
            email = request.data.get('email')
            if not name or not email:
                return Response({"error": "Name and Email are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Append name and email
            encoded_name = urllib.parse.quote(name)
            encoded_email = urllib.parse.quote(email)
            link = f"{base_link}?name={encoded_name}&email={encoded_email}"
            
            invited_candidates.append({"name": name, "email": email, "link": link})
            
            # Send Email
            try:
                subject = f"Invite to AI Technical Assessment: {assessment.required_skills}"
                
                # Format availability dates in local time
                start_time = timezone.localtime(assessment.available_from).strftime('%B %d, %Y at %I:%M %p') if assessment.available_from else "Immediately"
                end_time = timezone.localtime(assessment.available_until).strftime('%B %d, %Y at %I:%M %p') if assessment.available_until else "No fixed deadline"
                
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
                    
                    encoded_name = urllib.parse.quote(name)
                    encoded_email = urllib.parse.quote(email)
                    link = f"{base_link}?name={encoded_name}&email={encoded_email}"
                    
                    invited_candidates.append({"name": name, "email": email, "link": link})
                    
                    try:
                        subject = f"Invite to AI Technical Assessment: {assessment.required_skills}"
                        
                        start_time = timezone.localtime(assessment.available_from).strftime('%B %d, %Y at %I:%M %p') if assessment.available_from else "Immediately"
                        end_time = timezone.localtime(assessment.available_until).strftime('%B %d, %Y at %I:%M %p') if assessment.available_until else "No fixed deadline"

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
