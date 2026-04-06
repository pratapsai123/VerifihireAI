import os
import uuid
import json
import random
import logging
import traceback
import copy
from datetime import datetime, timedelta
from groq import Groq
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
import uuid
from .models import Assessment, AIAssessmentSubmission, AIAssessmentIntegrityScreenshot
from ai_candidates.models import Candidate
from ai_candidates.views import extract_json
from .ai_logic import (
    _normalize_difficulty_label,
    _normalize_generated_pool,
    _mcq_difficulty_counts,
    _rebalance_mcq_difficulties,
    _repair_pool_shortfall,
    _generate_coding_pool_ai_only,
    _generate_mcq_pool_ai_only,
    pick_random_subset,
    _verify_reference_solutions,
    _expert_assessment_refiner,
    _generate_execution_verified_test_cases
)
import traceback
import base64
from django.core.files.base import ContentFile
from api.models import UserProfile, DeletionRequest
from api._imports import _is_application_admin_email, handle_deletion_request


# Helper functions moved to ai_logic.py

logger = logging.getLogger(__name__)
MAX_CODING_TASKS = 50

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
            else:
                # If the candidate provided a real name to override an auto-generated one (like "Extraction Failed"), update it
                if name and submission.candidate_name != name:
                    submission.candidate_name = name
                    # Also update email if it was overridden
                    if email and submission.candidate_email != email:
                        submission.candidate_email = email
                    
                    
                    # CROSS-UPDATE: Synchronize with the Candidate record if exists
                    try:
                        candidate = Candidate.objects.filter(email__iexact=email).first()
                        if candidate:
                            if name and (candidate.full_name == "Extraction Failed" or candidate.full_name != name):
                                candidate.full_name = name
                                candidate.save(update_fields=['full_name'])
                    except Exception as sync_err:
                        logger.warning(f"Failed to cross-update candidate {email}: {sync_err}")

            # Use candidate_questions (the subset) instead of the whole pool
            generated_content = submission.candidate_questions or assessment.generated_content or {}
            
            # Unwrap historic nested dictionaries from Llama-3.1
            if 'mcqs' not in generated_content and 'coding_challenges' not in generated_content:
                for key, val in generated_content.items():
                    if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                        generated_content = val
                        break

            generated_content = _normalize_generated_pool(generated_content)
            mcqs = generated_content.get('mcqs', [])
            coding_challenges = generated_content.get('coding_challenges', [])
            
            total_possible_points = 0
            candidate_total_points = 0
            
            # Difficulty weight multipliers (matches user requirement: Easy=1x, Medium=2x, Hard=3x)
            # Base points = 100 per question
            weight_map = {'Easy': 100, 'Medium': 200, 'Hard': 300}

            import re
            def clean_ans(s):
                if not s: return ""
                # Strip common choice prefixes like "a) ", "1. ", "Choice A: "
                return re.sub(r'^(?:choice\s+)?[a-z0-9][\.\)\:\s-]+\s*', '', s.lower()).strip()

            # 1. MCQ Scoring - Flat 20 points each
            possible_mcq_points = 0
            candidate_mcq_points = 0
            for i, mcq in enumerate(mcqs):
                weight = 20
                possible_mcq_points += weight
                
                correct_ans = str(mcq.get('answer') or mcq.get('correct_answer') or '').strip()
                candidate_ans = str(answers.get(f'mcq_{i}') or '').strip()
                
                if correct_ans and clean_ans(candidate_ans) == clean_ans(correct_ans):
                    candidate_mcq_points += weight

            # 2. Coding Challenge Scoring - Weighted (100, 200, 300)
            possible_coding_points = 0
            candidate_coding_points = 0
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

            # ---------------------------------------------------------
            # FINAL WEIGHTED SCORING (40% MCQ / 60% Coding)
            # ---------------------------------------------------------
            
            # Calculate individual percentages
            mcq_percentage = (candidate_mcq_points / possible_mcq_points * 100) if possible_mcq_points > 0 else 0
            coding_percentage = (candidate_coding_points / possible_coding_points * 100) if possible_coding_points > 0 else 0
            
            # Aggregate based on weightage
            if possible_mcq_points > 0 and possible_coding_points > 0:
                percentage = round((mcq_percentage * 0.4) + (coding_percentage * 0.6))
            elif possible_mcq_points > 0:
                # 100% MCQ if no coding challenges are present
                percentage = round(mcq_percentage)
            elif possible_coding_points > 0:
                # 100% Coding if no MCQs are present
                percentage = round(coding_percentage)
            else:
                percentage = 0

            pass_status = 'selected' if percentage >= assessment.pass_threshold and submission.integrity_score >= 50 else 'rejected'

            submission.answers = answers
            submission.mcq_score = round(mcq_percentage) # Store % for internal tracking
            submission.coding_score = round(coding_percentage) # Store % for internal tracking
            submission.score = percentage 
            submission.total_questions = len(mcqs) + len(coding_challenges)
            submission.percentage = percentage
            submission.status = pass_status
            submission.results_breakdown = {
                "mcq": {
                    "scored_points": round(candidate_mcq_points), 
                    "possible_points": possible_mcq_points,
                    "accuracy": f"{int(mcq_percentage)}%",
                    "weight": "40%"
                },
                "coding": {
                    "scored_points": round(candidate_coding_points), 
                    "possible_points": possible_coding_points,
                    "accuracy": f"{int(coding_percentage)}%",
                    "weight": "60%"
                },
                "coding_results": coding_results,
                "weighted_final": f"{percentage}%"
            }
            submission.submitted_at = timezone.now()
            submission.save()

            # CROSS-UPDATE: Synchronize with the Candidate record
            try:
                candidate = Candidate.objects.filter(email__iexact=email).first()
                if candidate:
                    candidate.score = percentage
                    candidate.status = 'Completed'
                    candidate.completed_at = timezone.now()
                    
                    if not isinstance(candidate.interview_summary, list):
                        candidate.interview_summary = []
                    
                    candidate.interview_summary.append({
                        "type": "AI_ASSESSMENT",
                        "assessment_id": assessment.id,
                        "mcq_accuracy": f"{round(candidate_mcq_points/20)}/{len(mcqs)} ({int(mcq_percentage)}%)",
                        "coding_accuracy": f"{int(coding_percentage)}%",
                        "weighted_mcq": f"{(mcq_percentage * 0.4):.1f}%",
                        "weighted_coding": f"{(coding_percentage * 0.6):.1f}%",
                        "integrity_score": f"{int(submission.integrity_score)}%",
                        "timestamp": timezone.now().isoformat()
                    })
                    candidate.save()
            except Exception as sync_err:
                logger.warning(f"Failed to cross-update candidate {email}: {sync_err}")

            response_data = {
                "message": "Assessment submitted successfully",
                "submission_id": submission.id,
                "final_score": percentage,
                "mcq_score": int(mcq_percentage),
                "coding_score": int(coding_percentage),
                "weightage": "40/60 (MCQ/Coding)",
                "status": pass_status,
                "display_percentage": f"{percentage}%"
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
    PRIMARY_MODEL = "llama-3.1-8b-instant"
    FALLBACK_MODEL = "llama-3.1-8b-instant"
    _fallback_until = 0

    def post(self, request):
        data = request.data
        job_description = data.get('job_description')
        required_skills = data.get('required_skills')
        
        # Robust Question Count Extraction
        # 1. MCQs: Priority to Granular (if they have non-zero sum) > Total count
        input_mcq_total = int(data.get('mcq_count', 0))
        input_easy = int(data.get('mcq_easy', 0))
        input_medium = int(data.get('mcq_medium', 0))
        input_hard = int(data.get('mcq_hard', 0))
        
        granular_sum = input_easy + input_medium + input_hard
        
        if granular_sum > 0:
            mcq_count = granular_sum
            mcq_easy = input_easy
            mcq_medium = input_medium
            mcq_hard = input_hard
        elif input_mcq_total > 0:
            mcq_count = input_mcq_total
            mcq_easy = mcq_count // 2
            mcq_medium = (mcq_count * 3) // 10
            mcq_hard = max(0, mcq_count - mcq_easy - mcq_medium)
        else:
            # Absolute default fallback
            mcq_count = 10
            mcq_easy = 5
            mcq_medium = 3
            mcq_hard = 2

        # 2. Coding Challenges: Priority to Non-Empty coding_tasks > coding_count
        input_coding_count = int(data.get('coding_count', 0))
        input_coding_count = max(0, min(input_coding_count, MAX_CODING_TASKS))
        coding_tasks = data.get('coding_tasks', [])
        
        if isinstance(coding_tasks, str) and coding_tasks:
            try:
                coding_tasks = json.loads(coding_tasks)
            except:
                coding_tasks = []

        if isinstance(coding_tasks, list):
            coding_tasks = coding_tasks[:MAX_CODING_TASKS]

        if isinstance(coding_tasks, list) and len(coding_tasks) > 0:
            coding_count = len(coding_tasks)
        elif input_coding_count > 0:
            coding_count = input_coding_count
            coding_tasks = ['Medium'] * coding_count
        else:
            # Absolute default fallback
            coding_count = 2
            coding_tasks = ['Medium', 'Hard']

        # Log for debugging
        logger.info(f"Generated Assessment Config: MCQs={mcq_count} ({mcq_easy}/{mcq_medium}/{mcq_hard}), Coding={coding_count} ({coding_tasks})")
        
        duration = int(data.get('duration', 60))
        total_possible_points = int(data.get('total_possible_points', 1000))

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
            
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None

            assessment = Assessment.objects.create(
                job_description=job_description,
                required_skills=required_skills,
                mcq_count=mcq_count,
                mcq_easy=mcq_easy,
                mcq_medium=mcq_medium,
                mcq_hard=mcq_hard,
                coding_count=coding_count,
                coding_difficulty_list=coding_tasks,
                duration_minutes=duration,
                total_points=total_possible_points,
                num_applicants=int(data.get('num_applicants', 0)),
                available_from=data.get('available_from'),
                available_until=data.get('available_until'),
                pass_threshold=data.get('pass_threshold', 60),
                company=company,
                user_profile=user_profile
            )

            # Pool multipliers based on number of applicants (min 2x for randomization)
            num_applicants = assessment.num_applicants or 2
            pool_multiplier = max(2, num_applicants)

            pool_easy = mcq_easy * pool_multiplier
            pool_medium = mcq_medium * pool_multiplier
            pool_hard = mcq_hard * pool_multiplier
            pool_mcq_total = pool_easy + pool_medium + pool_hard
            pool_coding_total = coding_count * pool_multiplier
            pool_coding_tasks = coding_tasks * pool_multiplier

            logger.info(f"Generating Pool for {num_applicants} applicants: MCQs={pool_mcq_total}, Coding={pool_coding_total}")
            
            local_api_key = getattr(settings, 'GROQ_API_KEY', None)
            local_groq_client = Groq(api_key=local_api_key, timeout=60.0)
            generated_data = {"mcqs": [], "coding_challenges": []}

            # 1. GENERATE MCQ POOL (Dedicated AI Call)
            blacklist_mcqs = []
            blacklist_titles = []
            
            # Fetch last 20 assessments for this company to avoid replicates
            recent_assessments = Assessment.objects.filter(company=company, is_deleted=False).order_by('-created_at')[:20]
            for old_asm in recent_assessments:
                old_content = old_asm.generated_content or {}
                for q in old_content.get('mcqs', []):
                    blacklist_mcqs.append(q.get('question', '')[:100])
                for challenge in old_content.get('coding_challenges', []):
                    blacklist_titles.append(challenge.get('title'))

            if pool_mcq_total > 0:
                logger.info(f"Step 1: Generating MCQ pool of {pool_mcq_total} questions. Blacklist: {len(blacklist_mcqs)}")
                mcqs = _generate_mcq_pool_ai_only(
                    groq_client=local_groq_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    pool_mcq_total=pool_mcq_total,
                    pool_easy=pool_easy,
                    pool_medium=pool_medium,
                    pool_hard=pool_hard,
                    blacklist_qs=blacklist_mcqs,
                    model=self.FALLBACK_MODEL
                )
                if mcqs:
                    generated_data['mcqs'] = mcqs[:pool_mcq_total]

            # 2. GENERATE CODING POOL (Simplified: Question + Working Answer only, no test cases)
            final_coding_challenges = []
            coding_attempts = 0
            max_coding_attempts = 3
            blacklist_titles = list(blacklist_titles)

            while len(final_coding_challenges) < pool_coding_total and coding_attempts < max_coding_attempts:
                coding_attempts += 1
                needed = pool_coding_total - len(final_coding_challenges)
                logger.info(f"Step 2: Generating {needed} coding challenges (Attempt {coding_attempts}/{max_coding_attempts})")
                
                current_difficulties = pool_coding_tasks[len(final_coding_challenges):pool_coding_total]
                
                new_challenges = _generate_coding_pool_ai_only(
                    groq_client=local_groq_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    difficulties=current_difficulties,
                    total_required=needed,
                    batch_size=1,
                    blacklist_titles=blacklist_titles + [c.get('title') for c in final_coding_challenges],
                    model=self.PRIMARY_MODEL
                )
                
                if not new_challenges:
                    continue
                
                # Verify reference solutions actually execute correctly
                verified_batch = _verify_reference_solutions(
                    groq_client=local_groq_client,
                    challenges=new_challenges,
                    model=self.PRIMARY_MODEL
                )
                
                # ONLY ADD IF VERIFIED (NO N/A OUTPUTS)
                for v in verified_batch:
                    v_out = str(v.get('example_output', 'N/A')).strip()
                    if v_out and v_out != "N/A":
                        final_coding_challenges.append(v)
                    else:
                        logger.warning(f"Verification FAILED for '{v.get('title')}'. Trashing and regenerating...")
                
            # Finalize the coding pool
            final_coding_challenges = final_coding_challenges[:pool_coding_total]
            
            if final_coding_challenges:
                logger.info("Test Case Gate: Generating 5 execution-verified hidden test cases per challenge...")
                final_coding_challenges = _generate_execution_verified_test_cases(
                    groq_client=local_groq_client,
                    challenges=final_coding_challenges,
                    target_count=5,
                    model=self.PRIMARY_MODEL
                )

            generated_data['coding_challenges'] = final_coding_challenges

            # --- RESTORED ORIGINAL MCQ PASS ---
            # Now we call the refiner on the MCQ pool that was generated in Step 1
            if generated_data.get('mcqs'):
                logger.info("Expert Gate: Cleaning and Refining MCQ pool as originally requested...")
                mcq_refined_data = _expert_assessment_refiner(
                    groq_client=local_groq_client,
                    raw_content={"mcqs": generated_data['mcqs'], "coding_challenges": []}
                )
                generated_data['mcqs'] = mcq_refined_data.get('mcqs', [])

            # RE-CALCULATE FINAL METRICS
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
            final_mcqs = len(generated_data.get('mcqs', []))
            final_coding = len(generated_data.get('coding_challenges', []))

            # If MCQ count is enough but labels are still skewed, rebalance labels over AI-generated MCQs.
            if final_mcqs >= pool_mcq_total and pool_mcq_total > 0 and (final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):
                logger.warning(
                    f"Dedicated MCQ generation still skewed (got {final_easy}/{final_medium}/{final_hard}). "
                    "Rebalancing difficulty labels on AI-generated MCQs to match requested split."
                )
                generated_data['mcqs'] = _rebalance_mcq_difficulties(
                    generated_data.get('mcqs', []),
                    easy_required=pool_easy,
                    medium_required=pool_medium,
                    hard_required=pool_hard,
                )
                # Refresh metrics after rebalance
                final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
                final_mcqs = len(generated_data.get('mcqs', []))

            if final_mcqs < pool_mcq_total or final_coding < coding_count:
                raise Exception(
                    f"AI could not satisfy minimum required counts. Expected pool MCQs={pool_mcq_total}, min coding={coding_count}; "
                    f"got MCQs={final_mcqs}, coding={final_coding}."
                )
            if final_coding >= coding_count and final_coding < pool_coding_total:
                logger.warning(f"Coding pool smaller than requested ({final_coding} vs {pool_coding_total}), but sufficient for candidate ({coding_count}).")
            if final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard:
                raise Exception(
                    f"AI could not satisfy requested MCQ difficulty split. Expected Easy/Medium/Hard="
                    f"{pool_easy}/{pool_medium}/{pool_hard}; got {final_easy}/{final_medium}/{final_hard}."
                )

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
            
            # Log to terminal-like file for easy debugging
            error_log = f"\n[{timezone.now()}] ERROR in GenerateAssessmentView: {str(e)}\n{tb}\nRAW: {raw_resp}\n"
            try:
                with open('api_debug.txt', 'a') as f:
                    f.write(error_log)
            except Exception:
                pass # Ignore if file is locked

            
            logger.error(f"ERROR in GenerateAssessmentView: {str(e)}\n{tb}\nRAW: {raw_resp}")
            if 'assessment' in locals() and assessment:
                assessment.status = 'FAILED'
                assessment.save()
            
            error_msg = str(e)
            if "rate_limit_exceeded" in error_msg.lower():
                user_msg = "AI Provider rate limit reached. Please wait a few minutes and try again."
            elif "json_validate_failed" in error_msg.lower() or "badrequest" in error_msg.lower():
                user_msg = "AI generation failed to produce a valid structure. Please try simplifying your Job Description or reducing question counts."
            else:
                user_msg = f"Generation failed: {error_msg}"

            return Response({"error": error_msg, "message": user_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                
                # CROSS-UPDATE: Synchronize with the Candidate record if exists
                try:
                    candidate = Candidate.objects.filter(email__iexact=email).first()
                    if candidate:
                        if name and (candidate.full_name == "Extraction Failed" or candidate.full_name != name):
                            candidate.full_name = name
                            candidate.save(update_fields=['full_name'])
                except Exception as sync_err:
                    logger.warning(f"Failed to cross-update candidate {email} on creation: {sync_err}")
                
                # Lock in randomized questions upon first creation
                if not submission.candidate_questions:
                    gen_content = assessment.generated_content or {}
                    if isinstance(gen_content, str):
                        try:
                            gen_content = json.loads(gen_content)
                        except:
                            pass
                    
                    # Unwrap if nested
                    if isinstance(gen_content, dict) and 'mcqs' not in gen_content and 'coding_challenges' not in gen_content:
                        for val in gen_content.values():
                            if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                                gen_content = val
                                break

                    submission.candidate_questions = pick_random_subset(assessment, gen_content, seed=email)
                    submission.save(update_fields=['candidate_questions'])
             
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
                "current_question_index": submission.current_question_index,
                "codingResults": (submission.results_breakdown or {}).get('coding_progress', {}),
                "codeDrafts": (submission.results_breakdown or {}).get('code_drafts', {})
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
            
            # Handle Screenshot
            screenshot_b64 = request.data.get('screenshot')
            webcam_b64 = request.data.get('webcam_screenshot')
            
            if screenshot_b64 or webcam_b64:
                try:
                    integrity_snap = AIAssessmentIntegrityScreenshot(
                        submission=submission,
                        event_type=event_type,
                        timestamp=timezone.now()
                    )
                    
                    if screenshot_b64:
                        if ';' in screenshot_b64 and 'base64,' in screenshot_b64:
                            header, imgstr = screenshot_b64.split(';base64,')
                            ext = header.split('/')[-1]
                        else:
                            imgstr = screenshot_b64
                            ext = 'png'
                        
                        img_data = base64.b64decode(imgstr)
                        fname = f"ai_integrity_{submission.id}_{event_type}_{int(timezone.now().timestamp())}.{ext}"
                        integrity_snap.screenshot.save(fname, ContentFile(img_data), save=False)

                    if webcam_b64:
                        if ';' in webcam_b64 and 'base64,' in webcam_b64:
                            header, imgstr = webcam_b64.split(';base64,')
                            ext = header.split('/')[-1]
                        else:
                            imgstr = webcam_b64
                            ext = 'png'
                        
                        webcam_data = base64.b64decode(imgstr)
                        cname = f"ai_cam_{submission.id}_{event_type}_{int(timezone.now().timestamp())}.{ext}"
                        integrity_snap.webcam_screenshot.save(cname, ContentFile(webcam_data), save=False)

                    integrity_snap.save()

                except Exception as se:
                    logger.error(f"Failed to save AI integrity screenshot: {str(se)}")

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
            coding_results = request.data.get('codingResults')
            code_drafts = request.data.get('codeDrafts')
            
            if answers is not None:
                submission.answers = answers
            if index is not None:
                submission.current_question_index = index
            
            if not submission.results_breakdown:
                submission.results_breakdown = {}
                
            if coding_results is not None:
                submission.results_breakdown['coding_progress'] = coding_results
            if code_drafts is not None:
                submission.results_breakdown['code_drafts'] = code_drafts
            
            submission.save()
            return Response({"status": "progress saved"})
        except AIAssessmentSubmission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

class AssessmentListView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            if not company:
                return Response([], status=status.HTTP_200_OK)

            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)

            if scoped_ids is None:
                # Application Admin: all in company, OR assessments with company=None that they created
                assessments = Assessment.objects.filter(
                    models.Q(company=company) | models.Q(company__isnull=True, user_profile=user_profile),
                    is_deleted=False
                ).order_by('-created_at')
            else:
                # Scoped: only assessments created by users in this user's reporting hierarchy
                assessments = Assessment.objects.filter(
                    company=company, 
                    user_profile_id__in=scoped_ids, 
                    is_deleted=False
                ).order_by('-created_at')

            data = []
            for assessment in assessments:
                count = AIAssessmentSubmission.objects.filter(assessment=assessment).count()
                completed_count = AIAssessmentSubmission.objects.filter(assessment=assessment, submitted_at__isnull=False).count()
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
                    "generated_content": _normalize_generated_pool(assessment.generated_content or {}),
                    "status": assessment.status,
                    "share_token": str(assessment.share_token),
                    "candidate_count": count,
                    "completed_count": completed_count,
                    "invited_count": assessment.invited_count,
                    "num_applicants": assessment.num_applicants,
                    "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                    "available_until": assessment.available_until.isoformat() if assessment.available_until else None
                })
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AssessmentDetailView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)

            if scoped_ids is None:
                # Primary attempt: By ID and Company
                assessment = Assessment.objects.filter(pk=pk, company=company).first()
                # Fallback: By ID and Creator (handles legacy/admin assessments with company=None)
                if not assessment:
                    assessment = Assessment.objects.filter(pk=pk, user_profile=user_profile).first()
            else:
                assessment = Assessment.objects.filter(pk=pk, company=company, user_profile_id__in=scoped_ids).first()
            
            if not assessment:
                raise Assessment.DoesNotExist
                
            submissions = AIAssessmentSubmission.objects.filter(assessment=assessment).order_by('-submitted_at')
            
            submission_data = []
            for sub in submissions:
                integrity_snapshots = AIAssessmentIntegrityScreenshot.objects.filter(submission=sub).order_by('timestamp')
                screenshots_data = []
                for snap in integrity_snapshots:
                    screenshots_data.append({
                        "event_type": snap.event_type,
                        "timestamp": snap.timestamp.isoformat() if snap.timestamp else None,
                        "screenshot_url": request.build_absolute_uri(snap.screenshot.url) if snap.screenshot else None,
                        "webcam_screenshot_url": request.build_absolute_uri(snap.webcam_screenshot.url) if snap.webcam_screenshot else None,
                    })

                submission_data.append({
                    "id": sub.id,
                    "submission_id": f"ai_{sub.id}",
                    "candidate_name": sub.candidate_name,
                    "candidate_email": sub.candidate_email,
                    "score": sub.score,
                    "mcq_score": sub.mcq_score,
                    "coding_score": sub.coding_score,
                    "results_breakdown": sub.results_breakdown,
                    "percentage": sub.percentage,
                    "status": sub.status,
                    "final_status": sub.status,
                    "integrity_score": sub.integrity_score,
                    "submitted_at": sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else None,
                    "candidate_questions": sub.candidate_questions,
                    "answers": sub.answers,
                    "integrity_screenshots": screenshots_data,
                    "is_resume_screening": False
                })


            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "role_title": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "difficulty_level": assessment.difficulty_level,
                "total_points": assessment.total_points,
                "pass_threshold": assessment.pass_threshold,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M") if assessment.created_at else None,
                "generated_content": _normalize_generated_pool(assessment.generated_content or {}),
                "status": assessment.status,
                "share_token": str(assessment.share_token),
                "num_applicants": assessment.num_applicants,
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None,
                "submissions": submission_data,
                "assigned_interviewers": []
            }
            # Safely try to load assigned_interviewers
            try:
                data["assigned_interviewers"] = [
                    {"id": i.id, "name": i.user.get_full_name() or i.user.username, "email": i.user.email, "role": i.role}
                    for i in assessment.assigned_interviewers.all()
                ]
            except Exception:
                pass

            return Response(data, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)

            if scoped_ids is None:
                assessment = Assessment.objects.filter(pk=pk, company=company).first()
                if not assessment:
                    assessment = Assessment.objects.filter(pk=pk, user_profile=user_profile).first()
            else:
                assessment = Assessment.objects.filter(pk=pk, company=company, user_profile_id__in=scoped_ids).first()

            if not assessment:
                return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update fields
            if 'num_applicants' in request.data:
                assessment.num_applicants = request.data['num_applicants']
            # role_title is not in the model, we use required_skills
            if 'role_title' in request.data:
                assessment.required_skills = request.data['role_title']
            
            assessment.save()
            return Response({
                "message": "Assessment updated successfully",
                "num_applicants": assessment.num_applicants,
                "role_title": assessment.role_title
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile or not user_profile.company:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
            assessment = Assessment.objects.get(pk=pk, company=user_profile.company)
            
            # Use centralized helper to handle policy and workflow
            response, handled = handle_deletion_request(
                user_profile=user_profile,
                company=user_profile.company,
                content_type='Assessment',
                object_id=assessment.id,
                object_repr=f"AI Assessment: {assessment.required_skills}",
                reason=request.data.get('reason')
            )
            
            if handled:
                return response

            assessment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Assessment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def pick_random_subset(self, assessment, pool):
        return pick_random_subset(assessment, pool)

class PublicAssessmentView(APIView):
    def get(self, request, token):
        try:
            with open('api_debug.txt', 'a') as f:
                f.write(f"\n[{timezone.now()}] PUBLIC ACCESS: Token='{token}'\n")
                f.write(f"Query Params: {request.query_params}\n")
                f.write(f"Host: {request.get_host()}\n")
        except Exception:
            pass

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

            # 1. Handle Candidate-Specific Randomized Content
            email_param = request.query_params.get('email', '').strip().lower()
            name_param = request.query_params.get('name', '').strip()
            
            gen_content = _normalize_generated_pool(gen_content)
            final_content = gen_content
            already_completed = False
            
            if email_param:
                from .models import AIAssessmentSubmission
                import random

                # Check for existing submission
                submission = AIAssessmentSubmission.objects.filter(
                    assessment=assessment,
                    candidate_email__iexact=email_param
                ).first()

                if submission:
                    already_completed = submission.submitted_at is not None
                    # If we already have locked-in questions, use them
                    if submission.candidate_questions:
                        final_content = submission.candidate_questions
                    else:
                        # Case: Submission exists but no questions locked yet (e.g. legacy/error)
                        # Pick a subset now and lock it
                        final_content = pick_random_subset(assessment, gen_content, seed=email_param)
                        submission.candidate_questions = final_content
                        submission.save(update_fields=['candidate_questions'])
                else:
                    # No submission yet, but we have an email. 
                    # We can pick the set now so it's consistent even before they "start"
                    final_content = pick_random_subset(assessment, gen_content, seed=email_param)
                    # We don't create the submission here to keep CreateSubmissionView as the source of truth for "Starting"
                    # However, we need to ensure CreateSubmissionView also locks it in or reuses this logic.
                    # BETTER: Always use a helper to get/create consistent set.

            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": final_content,
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
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def post(self, request):
        assessment_id = request.data.get('assessment_id')
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            assessment = Assessment.objects.get(pk=assessment_id, company=company)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

        invite_type = request.data.get('type')  # 'individual' or 'bulk'
        invited_candidates = []
        
        import urllib.parse
        # Use frontend base URL from settings - Standardized to localhost for dev
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
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
            
            # Increment invited count
            assessment.invited_count += 1
            assessment.save(update_fields=['invited_count'])
            
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

                assessment.invited_count += len(df)
                assessment.save(update_fields=['invited_count'])

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
            # Coerce stdin to a string if it's a dict/list from JSON test cases
            if isinstance(stdin, (dict, list)):
                import json
                stdin = json.dumps(stdin)
            elif stdin is None or (isinstance(stdin, str) and stdin.strip().lower() in ["none", "null"]):
                stdin = ""
            else:
                stdin = str(stdin)
            code = files[0]['content'] if files else ''
            
            # Get executor URL from environment or fallback to localhost:4000
            executor_base_url = os.environ.get("EXECUTOR_BASE_URL", "http://localhost:4000").rstrip("/")
            
            # Prepare payload for internal executor
            payload = {
                "language": language,
                "source_code": code,
                "stdin": stdin,
                "time_limit_ms": 30000,
                "memory_mb": 2048,
            }

            # Special handling for SQL (default to sqlite for AI assessments)
            if language == 'sql':
                payload["database_engine"] = "sqlite"
                payload["stdin"] = "" # SQL executor shouldn't parse stdin as SQL if it's JSON

            # Call internal executor
            try:
                response = requests.post(f"{executor_base_url}/execute", json=payload, timeout=120)
                result = response.json()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"ProxyCodeExecuteView executor timeout/error: {str(e)}")
                return Response({
                    "run": {
                        "stdout": "",
                        "stderr": f"Execution Service Timeout: {str(e)}",
                        "code": 1,
                        "output": f"The code execution service (port 4000) Timed Out after 120s. Please restart the executor or simplify your code."
                    }
                }, status=status.HTTP_200_OK)

            if not result.get('ok'):
                return Response({
                    "run": {
                        "stdout": "",
                        "stderr": result.get('error', 'Executor Error'),
                        "code": 1,
                        "output": result.get('error', 'Executor Error')
                    }
                }, status=status.HTTP_200_OK)

            # Map executor response to the format expected by the frontend
            piston_response = {
                "run": {
                    "stdout": result.get('stdout', ''),
                    "stderr": result.get('stderr', ''),
                    "code": result.get('exit_code', 0),
                    "output": result.get('stdout', '') + result.get('stderr', '')
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
            }, status=status.HTTP_200_OK)

class AIAssessmentSubmissionDetailView(generics.RetrieveDestroyAPIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_profile = getattr(self.request.user, 'profile', None)
        company = user_profile.company if user_profile and user_profile.company else None
        if not company:
            return AIAssessmentSubmission.objects.none()
        return AIAssessmentSubmission.objects.filter(assessment__company=company, is_deleted=False)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.company:
            return super().destroy(request, *args, **kwargs)

        instance = self.get_object()
        
        # Use centralized helper to handle policy and workflow
        response, handled = handle_deletion_request(
            user_profile=user_profile,
            company=user_profile.company,
            content_type='AIAssessmentSubmission',
            object_id=instance.id,
            object_repr=f"AI Submission for {instance.candidate_name} ({instance.candidate_email})",
            reason=request.data.get('reason')
        )
        
        if handled:
            return response

        return self.destroy(request, *args, **kwargs)

class AIAssessmentAssignmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or user_profile.role not in ['company_admin', 'hr_manager', 'ROLE_COMPANY_ADMIN', 'ROLE_HR_MANAGER']:
            return Response({"error": "Unauthorized"}, status=403)
            
        try:
            assessment = Assessment.objects.get(pk=pk, company=user_profile.company)
            interviewer_ids = request.data.get('interviewer_ids', [])
            
            interviewers = UserProfile.objects.filter(id__in=interviewer_ids, company=user_profile.company)
            assessment.assigned_interviewers.set(interviewers)
            
            return Response({"message": "Interviewers assigned successfully"})
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=404)

class AIAssessmentAvailableInterviewersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.company:
            return Response({"error": "Unauthorized"}, status=403)
            
        # exclude candidates
        members = UserProfile.objects.filter(company=user_profile.company).exclude(role__in=['candidate', 'ROLE_CANDIDATE'])
        data = [
            {"id": m.id, "name": f"{m.first_name or ''} {m.last_name or ''}".strip() or m.email, "email": m.email, "role": m.role}
            for m in members
        ]
        return Response(data)
