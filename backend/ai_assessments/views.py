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
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

import io
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, PageBreak, HRFlowable, XPreformatted
)
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse

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
    _generate_execution_verified_coding_pool,
    _generate_mcq_pool_ai_only,
    pick_random_subset,
    _expert_assessment_refiner,
    _validate_mcq_structure,
    GroqKeyManager
)

import traceback
import base64
from django.core.files.base import ContentFile
from api.models import UserProfile, DeletionRequest
from api._imports import _is_application_admin_email, handle_deletion_request
from api.utils.batch_utils import generate_batch_id, generate_batch_name
import requests
from api._imports import DEEPFACE_BASE_URL


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
        phone = data.get('phone', '')
        pan_number = data.get('pan_number', '')
        pan_photo = request.FILES.get('pan_photo')
        pan_verified_raw = data.get('pan_verified', False)
        # Handle string 'true'/'false' from FormData
        if isinstance(pan_verified_raw, str):
            pan_verified = pan_verified_raw.lower() == 'true'
        else:
            pan_verified = bool(pan_verified_raw)
        # Parse JSON strings from FormData
        answers_raw = data.get('answers', '{}')
        coding_results_raw = data.get('coding_results', '{}')
        try:
            import json
            answers = json.loads(answers_raw) if isinstance(answers_raw, str) else answers_raw
            coding_results = json.loads(coding_results_raw) if isinstance(coding_results_raw, str) else coding_results_raw
        except json.JSONDecodeError:
            answers = {}
            coding_results = {}

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
                    phone=phone,
                    pan_number=pan_number,
                    pan_photo=pan_photo,
                    pan_verified=pan_verified,
                    status='ONGOING',
                    batch_id=assessment.batch_id,
                    batch_name=assessment.batch_name
                )
            else:
                # If the candidate provided a real name to override an auto-generated one (like "Extraction Failed"), update it
                if name and submission.candidate_name != name:
                    submission.candidate_name = name
                    # Also update email if it was overridden
                    if email and submission.candidate_email != email:
                        submission.candidate_email = email
                # Update PAN details if provided
                if phone:
                    submission.phone = phone
                if pan_number:
                    submission.pan_number = pan_number
                if pan_photo:
                    submission.pan_photo = pan_photo
                submission.pan_verified = pan_verified

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

            # 1. MCQ Scoring - 1 point each
            possible_mcq_points = 0
            candidate_mcq_points = 0
            for i, mcq in enumerate(mcqs):
                weight = 1  # 1 point per MCQ question
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
            # FINAL WEIGHTED SCORING (configurable MCQ% / Coding%)
            # Defaults to 40% MCQ / 60% Coding if not set
            # ---------------------------------------------------------
            mcq_w = (getattr(assessment, 'mcq_weight', 40) or 40) / 100
            coding_w = 1 - mcq_w

            # Calculate individual percentages
            mcq_percentage = (candidate_mcq_points / possible_mcq_points * 100) if possible_mcq_points > 0 else 0
            coding_percentage = (candidate_coding_points / possible_coding_points * 100) if possible_coding_points > 0 else 0
            
            # Aggregate based on weightage
            if possible_mcq_points > 0 and possible_coding_points > 0:
                percentage = round((mcq_percentage * mcq_w) + (coding_percentage * coding_w))
            elif possible_mcq_points > 0:
                # 100% MCQ if no coding challenges are present
                percentage = round(mcq_percentage)
            elif possible_coding_points > 0:
                # 100% Coding if no MCQs are present
                percentage = round(coding_percentage)
            else:
                percentage = 0

            # --- RIGOROUS HIRING STANDARDS ---
            # Enforce minimum thresholds for individual sections: MCQ 60%, Coding 50%, Integrity 70%
            MIN_MCQ_THRESHOLD = 60.0
            MIN_CODING_THRESHOLD = 50.0
            MIN_INTEGRITY_THRESHOLD = 70.0

            passed_overall = percentage >= assessment.pass_threshold
            passed_mcq = mcq_percentage >= MIN_MCQ_THRESHOLD
            passed_coding = coding_percentage >= MIN_CODING_THRESHOLD
            passed_integrity = submission.integrity_score >= MIN_INTEGRITY_THRESHOLD

            # Selection Logic based on user requirement:
            # 1. Integrity < 70% -> REJECTED
            # 2. Performance < Threshold -> REJECTED
            # 3. All Pass -> SELECTED
            
            if not passed_integrity:
                pass_status = 'rejected'
            elif (possible_mcq_points > 0 and not passed_mcq) or (possible_coding_points > 0 and not passed_coding):
                pass_status = 'rejected'
            elif not passed_overall:
                pass_status = 'rejected'
            else:
                pass_status = 'selected'

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
                    "weight": f"{round(mcq_w * 100)}%"
                },
                "coding": {
                    "scored_points": round(candidate_coding_points), 
                    "possible_points": possible_coding_points,
                    "accuracy": f"{int(coding_percentage)}%",
                    "weight": f"{round(coding_w * 100)}%"
                },
                "coding_results": coding_results,
                "weighted_final": f"{percentage}%"
            }
            submission.submitted_at = timezone.now()
            submission.save()

            # CROSS-UPDATE: Synchronize with the Candidate record
            try:
                # Use iexact and prioritize the same batch if possible
                candidates = Candidate.objects.filter(email__iexact=email).order_by('-id')
                candidate = candidates.filter(batch_id=assessment.batch_id).first()

                if candidate:
                    logger.info(f"SubmitAssessment: Updating candidate {candidate.id} results for {email} (Submission ID={submission.id})")
                    candidate.score = percentage
                    candidate.status = 'Assessment Passed'
                    candidate.save(update_fields=['score', 'status'])

                else:
                    logger.info(f"SubmitAssessment: No matching Candidate record found for {email} to update results.")

                    # ── TRIGGER NEXT STAGE ──
                    # If they passed, automatically trigger the AI Interview invitation
                    if pass_status == 'selected':
                        try:
                            from api.pipeline import process_assessment_passed
                            # This handles generating the interview link and sending the email
                            process_assessment_passed(submission.id)
                        except Exception as pipe_err:
                            logger.error(f"Pipeline Automation Error: Failed to trigger interview for {email}: {pipe_err}")

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

class CancelGenerationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            # sendBeacon might send raw text or JSON
            if request.content_type == 'text/plain':
                data = json.loads(request.body)
            else:
                data = request.data
            token = data.get('cancel_token') or data.get('token')
            if token:
                logger.warning(f"Frontend sent abort signal for generation token: {token}")
                cache.set(f"abort_{token}", True, timeout=300)
                return Response({"status": "aborted"})
            return Response({"error": "No token"}, status=400)
        except Exception as e:
            logger.error(f"Cancel error: {e}")
            return Response({"error": "Invalid format"}, status=400)

class GenerateAssessmentView(APIView):
    PRIMARY_MODEL = "llama-3.1-8b-instant"
    FALLBACK_MODEL = "llama-3.1-8b-instant"
    _fallback_until = 0

    def post(self, request):
        data = request.data
        job_description = data.get('job_description')
        required_skills = data.get('required_skills')
        cancel_token = data.get('cancel_token')
        
        # Robust Question Count Extraction
        # 1. MCQs: Priority to Granular (if they have non-zero sum) > Total count
        input_mcq_total = int(data.get('mcq_count', 0))
        input_easy = int(data.get('mcq_easy', 0))
        input_medium = int(data.get('mcq_medium', 0))
        input_hard = int(data.get('mcq_hard', 0))
        
        granular_sum = input_easy + input_medium + input_hard
        
        # Check if mcq_count or granular fields were explicitly provided
        mcq_count_provided = 'mcq_count' in data
        mcq_granular_provided = 'mcq_easy' in data or 'mcq_medium' in data or 'mcq_hard' in data
        
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
        elif mcq_count_provided and input_mcq_total == 0:
            # User explicitly set 0 MCQs via mcq_count field
            mcq_count = 0
            mcq_easy = 0
            mcq_medium = 0
            mcq_hard = 0
        elif mcq_granular_provided and granular_sum == 0:
            # User explicitly set 0 MCQs via all granular fields being 0
            mcq_count = 0
            mcq_easy = 0
            mcq_medium = 0
            mcq_hard = 0
        else:
            # Absolute default fallback (only when not explicitly provided)
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
            # Respect user's coding_count=0 - don't force a default
            coding_count = 0
            coding_tasks = []

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

            # Read new flag
            same_questions_for_all = bool(data.get('same_questions_for_all', False))
            num_applicants = int(data.get('num_applicants', 0)) or 1

            # Case 1: Single candidate — generate exactly required count (1x)
            # Case 3: Same questions for all — generate exactly required count (1x)
            # Case 2: Multiple candidates, unique — generate num_applicants * required_count
            if num_applicants <= 1 or same_questions_for_all:
                pool_multiplier = 1
            else:
                pool_multiplier = num_applicants


            pool_easy = mcq_easy * pool_multiplier
            pool_medium = mcq_medium * pool_multiplier
            pool_hard = mcq_hard * pool_multiplier
            pool_mcq_total = pool_easy + pool_medium + pool_hard
            pool_coding_total = coding_count * pool_multiplier
            pool_coding_tasks = coding_tasks * pool_multiplier

            logger.info(f"Generating Pool (Case {'3' if same_questions_for_all else ('1' if num_applicants <= 1 else '2')}) for {num_applicants} applicants: Multiplier={pool_multiplier}")

            
            local_api_key = GroqKeyManager.get_current_key()
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
                    model=self.FALLBACK_MODEL,
                    cancel_token=cancel_token
                )
                if mcqs:
                    generated_data['mcqs'] = mcqs[:pool_mcq_total]

            # 2. GENERATE CODING POOL (Skeleton-Based: 100% Accuracy)
            if pool_coding_total > 0:
                logger.info(f"Step 2: Generating {pool_coding_total} execution-verified coding challenges using Skeleton-Based Engine.")
                generated_data['coding_challenges'] = _generate_execution_verified_coding_pool(
                    groq_client=local_groq_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    difficulties=pool_coding_tasks,
                    total_required=pool_coding_total,
                    model=self.PRIMARY_MODEL,
                    cancel_token=cancel_token
                )
            else:
                logger.info(f"Step 2: Skipping coding pool generation (coding_count=0)")
                generated_data['coding_challenges'] = []

            # --- RESTORED ORIGINAL MCQ PASS ---
            # Now we call the refiner on the MCQ pool that was generated in Step 1
            if generated_data.get('mcqs'):
                if len(generated_data['mcqs']) > 25:
                    logger.info(f"Expert Gate BYPASSED: Pool size ({len(generated_data['mcqs'])}) is large. Bypassing refiner to avoid 3-minute latency.")
                else:
                    logger.info("Expert Gate: Cleaning and Refining MCQ pool as originally requested...")
                    mcq_refined_data = _expert_assessment_refiner(
                        groq_client=local_groq_client,
                        raw_content={"mcqs": generated_data['mcqs'], "coding_challenges": []},
                        cancel_token=cancel_token
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

            # --- REBALANCING & REPAIR GATE (Self-Healing) ---
            final_mcqs = len(generated_data.get('mcqs', []))
            final_coding = len(generated_data.get('coding_challenges', []))
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))

            # Trigger repair if counts or difficulties are insufficient
            if (final_mcqs < pool_mcq_total or final_coding < pool_coding_total or 
                final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):
                
                shortfall_details = []
                if final_mcqs < pool_mcq_total:
                    shortfall_details.append(f"MCQs: {final_mcqs}/{pool_mcq_total}")
                if final_coding < pool_coding_total:
                    shortfall_details.append(f"Coding: {final_coding}/{pool_coding_total}")
                if final_easy < pool_easy:
                    shortfall_details.append(f"Easy: {final_easy}/{pool_easy}")
                if final_medium < pool_medium:
                    shortfall_details.append(f"Medium: {final_medium}/{pool_medium}")
                if final_hard < pool_hard:
                    shortfall_details.append(f"Hard: {final_hard}/{pool_hard}")
                
                logger.info(f"\n🔧 SELF-HEALING REPAIR TRIGGERED:\n   Shortfalls detected: {', '.join(shortfall_details)}\n   Starting repair cycle...")
                generated_data = _repair_pool_shortfall(
                    groq_client=local_groq_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    pool=generated_data,
                    pool_easy=pool_easy,
                    pool_medium=pool_medium,
                    pool_hard=pool_hard,
                    pool_coding_total=pool_coding_total,
                    coding_tasks=pool_coding_tasks,
                    model=self.PRIMARY_MODEL
                )
                # Recalculate after repair
                final_mcqs = len(generated_data.get('mcqs', []))
                final_coding = len(generated_data.get('coding_challenges', []))
                final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
                
                logger.info(f"\n✅ REPAIR CYCLE COMPLETE:\n   Final MCQs: {final_mcqs} ({final_easy}E/{final_medium}M/{final_hard}H)\n   Final Coding: {final_coding}")

            # --- FORCED REBALANCING GATE ---
            # If we have enough total MCQs, force-align their difficulty labels to match requested split
            if final_mcqs >= pool_mcq_total:
                logger.info(f"Self-Healing: Rebalancing {final_mcqs} MCQs to satisfy split {pool_easy}/{pool_medium}/{pool_hard}")
                generated_data['mcqs'] = _rebalance_mcq_difficulties(
                    generated_data.get('mcqs', []),
                    easy_required=pool_easy,
                    medium_required=pool_medium,
                    hard_required=pool_hard
                )
                # Update final metrics after rebalancing
                final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))

            # --- FINAL PASS: CLEAN ALL MCQs FOR 100% ACCURACY ---
            logger.info("\n🔍 FINAL PASS: Validating all MCQs for quality assurance...")
            all_mcqs = generated_data.get('mcqs', [])
            valid_mcqs = []
            invalid_count = 0
            
            for mcq in all_mcqs:
                is_valid, error_msg = _validate_mcq_structure(mcq)
                if is_valid:
                    valid_mcqs.append(mcq)
                else:
                    invalid_count += 1
                    logger.warning(
                        f"   ⚠️ INVALID MCQ REMOVED: {error_msg}. "
                        f"Question: {mcq.get('question', '')[:40]}..."
                    )
            
            logger.info(
                f"\n📊 FINAL PASS RESULTS:\n"
                f"   Input pool: {len(all_mcqs)} MCQs\n"
                f"   Valid MCQs: {len(valid_mcqs)}\n"
                f"   Removed (invalid): {invalid_count}\n"
                f"   {f'⚠️  WARNING: {invalid_count} invalid MCQs removed!' if invalid_count > 0 else '✅ All MCQs valid!'}"
            )
            
            # Update pool with only valid MCQs
            generated_data['mcqs'] = valid_mcqs
            final_mcqs = len(valid_mcqs)
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(valid_mcqs)
            
            # Check if shortfall created by removing invalid MCQs
            if invalid_count > 0 and final_mcqs < pool_mcq_total:
                logger.warning(
                    f"\n⚠️  SHORTFALL AFTER CLEANUP: Removed {invalid_count} invalid MCQs.\n"
                    f"   Current: {final_mcqs} valid MCQs\n"
                    f"   Required pool: {pool_mcq_total}\n"
                    f"   Shortfall: {pool_mcq_total - final_mcqs}\n"
                    f"   Triggering repair to fill gap..."
                )
                
                # Trigger repair for the shortfall
                try:
                    repair_generated = _repair_pool_shortfall(
                        groq_client=local_groq_client,
                        job_description=job_description,
                        required_skills=required_skills,
                        pool=generated_data,
                        pool_easy=pool_easy,
                        pool_medium=pool_medium,
                        pool_hard=pool_hard,
                        pool_coding_total=pool_coding_total,
                        coding_tasks=pool_coding_tasks,
                        model=self.PRIMARY_MODEL
                    )
                    
                    # Use repaired data
                    generated_data = repair_generated
                    
                    # Validate REPAIRED MCQs too (recursive validation)
                    all_mcqs_after_repair = generated_data.get('mcqs', [])
                    valid_mcqs_after_repair = []
                    for mcq in all_mcqs_after_repair:
                        is_valid, _ = _validate_mcq_structure(mcq)
                        if is_valid:
                            valid_mcqs_after_repair.append(mcq)
                    
                    generated_data['mcqs'] = valid_mcqs_after_repair
                    final_mcqs = len(valid_mcqs_after_repair)
                    final_easy, final_medium, final_hard = _mcq_difficulty_counts(valid_mcqs_after_repair)
                    
                    logger.info(
                        f"✅ Repair completed. MCQs now: {final_mcqs} valid ({final_easy}E/{final_medium}M/{final_hard}H)"
                    )
                except Exception as repair_e:
                    logger.error(f"❌ Repair failed during post-cleanup: {repair_e}")
                    raise
            
            # Check minimum still met after cleaning (and repair if triggered)
            if final_mcqs < mcq_count:
                logger.error(
                    f"\n❌ FINAL PASS FAILED: Not enough valid MCQs after cleaning!\n"
                    f"   Required minimum: {mcq_count}, After cleanup: {final_mcqs}\n"
                    f"   Removed {invalid_count} invalid MCQs during final pass.\n"
                    f"   Cannot meet minimum requirement. Assessment rejected."
                )
                raise Exception(
                    f"All MCQs failed final quality check. After removing {invalid_count} invalid MCQs, "
                    f"only {final_mcqs} valid MCQs remain but {mcq_count} required."
                )

            # --- FINAL PASS: CLEAN ALL CODING CHALLENGES FOR 100% ACCURACY ---
            logger.info("\n🔍 FINAL PASS: Validating all coding challenges...")
            all_coding = generated_data.get('coding_challenges', [])
            valid_coding = []
            removed_coding = 0
            MIN_TC = 4
            MAX_TC = 6
            
            for challenge in all_coding:
                test_cases = challenge.get('test_cases', [])
                tc_count = len(test_cases)
                
                if tc_count < MIN_TC:
                    removed_coding += 1
                    logger.warning(
                        f"   ⚠️ CODING CHALLENGE REMOVED: '{challenge.get('title', 'Unknown')}' has {tc_count}/{MIN_TC}-{MAX_TC} test cases. "
                        f"Minimum {MIN_TC} required."
                    )
                else:
                    valid_coding.append(challenge)
                    logger.info(f"   ✅ Challenge '{challenge.get('title', 'Unknown')}' valid ({tc_count} test cases)")
            
            logger.info(
                f"\n📊 CODING VALIDATION RESULTS:\n"
                f"   Input pool: {len(all_coding)} challenges\n"
                f"   Valid challenges: {len(valid_coding)} ({min(4, len(valid_coding))} tests)\n"
                f"   Removed (insufficient test cases): {removed_coding}\n"
                f"   {f'⚠️  WARNING: {removed_coding} challenges removed!' if removed_coding > 0 else '✅ All challenges valid!'}"
            )
            
            # Update pool with only valid coding challenges
            generated_data['coding_challenges'] = valid_coding
            final_coding = len(valid_coding)
            
            # Check if shortfall created by removing insufficient coding challenges
            if removed_coding > 0 and final_coding < pool_coding_total:
                logger.warning(
                    f"\n⚠️  SHORTFALL AFTER CLEANUP: Removed {removed_coding} coding challenges.\n"
                    f"   Current: {final_coding} valid challenges\n"
                    f"   Required pool: {pool_coding_total}\n"
                    f"   Shortfall: {pool_coding_total - final_coding}\n"
                    f"   Triggering repair to fill gap..."
                )
                
                # Trigger repair for coding shortfall
                try:
                    repair_generated = _repair_pool_shortfall(
                        groq_client=local_groq_client,
                        job_description=job_description,
                        required_skills=required_skills,
                        pool=generated_data,
                        pool_easy=pool_easy,
                        pool_medium=pool_medium,
                        pool_hard=pool_hard,
                        pool_coding_total=pool_coding_total,
                        coding_tasks=pool_coding_tasks,
                        model=self.PRIMARY_MODEL
                    )
                    
                    # Use repaired data
                    generated_data = repair_generated
                    
                    # Validate REPAIRED coding challenges too (check test cases)
                    all_coding_after_repair = generated_data.get('coding_challenges', [])
                    valid_coding_after_repair = []
                    for challenge in all_coding_after_repair:
                        tc_count = len(challenge.get('test_cases', []))
                        if tc_count >= MIN_TC:
                            valid_coding_after_repair.append(challenge)
                    
                    generated_data['coding_challenges'] = valid_coding_after_repair
                    final_coding = len(valid_coding_after_repair)
                    
                    logger.info(f"✅ Coding repair completed. Challenges now: {final_coding} valid")
                except Exception as repair_e:
                    logger.error(f"❌ Repair failed during post-cleanup (coding): {repair_e}")
                    raise
            
            # Check minimum still met after cleaning (and repair if triggered)
            if final_coding < coding_count:
                logger.error(
                    f"\n❌ CODING VALIDATION FAILED: Not enough valid challenges!\n"
                    f"   Required minimum: {coding_count}, After cleaning: {final_coding}\n"
                    f"   Removed {removed_coding} challenges with insufficient test cases.\n"
                    f"   Cannot meet minimum requirement. Assessment rejected."
                )
                raise Exception(
                    f"All coding challenges failed final quality check (insufficient test cases). "
                    f"After removing {removed_coding} invalid challenges, only {final_coding} valid challenges remain but {coding_count} required."
                )

            # Final Validation Gate
            if final_mcqs < mcq_count or final_coding < coding_count:
                logger.error(
                    f"\n❌ FINAL VALIDATION FAILED:\n"
                    f"   Required minimum - MCQs: {mcq_count}, Coding: {coding_count}\n"
                    f"   Got - MCQs: {final_mcqs}, Coding: {final_coding}\n"
                    f"   Buffer pool target was MCQs: {pool_mcq_total}, Coding: {pool_coding_total}\n"
                    f"   Assessment generation ABORTED."
                )
                raise Exception(
                    f"AI could not satisfy minimum required pool counts even after repair. "
                    f"Expected MINIMUM MCQs={mcq_count}, min coding={coding_count}; "
                    f"got MCQs={final_mcqs}, coding={final_coding}. (Buffer Pool target was {pool_mcq_total})"
                )

            if final_mcqs >= mcq_count and final_mcqs < pool_mcq_total:
                logger.warning(f"MCQ pool smaller than requested ({final_mcqs} vs {pool_mcq_total}), but sufficient for candidate ({mcq_count}).")

            if final_coding >= coding_count and final_coding < pool_coding_total:
                logger.warning(f"Coding pool smaller than requested ({final_coding} vs {pool_coding_total}), but sufficient for candidate ({coding_count}).")

            if (final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):
                # This should only happen if total count is somehow met but rebalance failed
                logger.warning(f"MCQ Difficulty split check bypassed. Expected {pool_easy}/{pool_medium}/{pool_hard}; got {final_easy}/{final_medium}/{final_hard}.")

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
                num_applicants=num_applicants,
                max_candidates_allowed=num_applicants,
                same_questions_for_all=same_questions_for_all,
                mcq_weight=int(data.get('mcq_weight', 40)),
                available_from=data.get('available_from'),
                available_until=data.get('available_until'),
                pass_threshold=data.get('pass_threshold', 60),
                company=company,
                user_profile=user_profile,
                generated_content=generated_data,
                batch_id=generate_batch_id(),
                batch_name=generate_batch_name(job_title),
                status='SCHEDULED',
                creation_type='manual',
                has_mcq_cutoff=False,
                min_mcq_pass_percentage=50,
                min_coding_pass_percentage=50
            )

            logger.info(
                f"\n✨ ASSESSMENT CREATED SUCCESSFULLY (ID: {assessment.id}):\n"
                f"   Skills: {required_skills}\n"
                f"   Questions: {final_mcqs} MCQs ({final_easy}E/{final_medium}M/{final_hard}H) + {final_coding} Coding\n"
                f"   Candidates: {num_applicants} ({'same questions' if same_questions_for_all else 'unique questions'})\n"
                f"   Status: {assessment.status}\n"
                f"   Share Token: {assessment.share_token}"
            )

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
            # If assessment fails, we simply return an error. Since we moved DB creation to the end, 
            # there is no orphaned database row to mark as 'FAILED' or 'is_deleted'.
            error_msg = str(e)
            if "rate_limit_exceeded" in error_msg.lower():
                user_msg = "AI Provider rate limit reached. Please wait a few minutes and try again."
            elif "json_validate_failed" in error_msg.lower() or "badrequest" in error_msg.lower():
                user_msg = "AI generation failed to produce a valid structure. Please try simplifying your Job Description or reducing question counts."
            else:
                user_msg = f"Generation failed: {error_msg}"

            return Response({"error": error_msg, "message": user_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _register_face_with_deepface(person_id, snapshot_b64):
    """
    Calls the DeepFace microservice to register/update the candidate's face.
    Ensures biometric data is persisted so that the proctoring session can start.
    """
    try:
        url = f"{DEEPFACE_BASE_URL}/registration/register"
        payload = {
            "person_id": person_id,
            "image_base64": snapshot_b64,
            "label": "registration_snapshot"
        }
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            print(f"DeepFace registration successful for {person_id}")
            return True
        else:
            print(f"DeepFace registration failed for {person_id}: {resp.text}")
            return False
    except Exception as e:
        print(f"DeepFace registration error for {person_id}: {str(e)}")
        return False

class CreateSubmissionView(APIView):
    def post(self, request):
        token = request.data.get('share_token')
        name = request.data.get('candidate_name')
        email = request.data.get('candidate_email', '').strip().lower()
        snapshot = request.data.get('snapshot')
        phone = request.data.get('phone', '')
        pan_number = request.data.get('pan_number', '')
        pan_photo = request.FILES.get('pan_photo')
        pan_verified_raw = request.data.get('pan_verified', False)
        # Handle string 'true'/'false' from FormData
        if isinstance(pan_verified_raw, str):
            pan_verified = pan_verified_raw.lower() == 'true'
        else:
            pan_verified = bool(pan_verified_raw)

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
                    phone=phone,
                    pan_number=pan_number,
                    pan_photo=pan_photo,
                    pan_verified=pan_verified,
                    status='ONGOING',
                    batch_id=assessment.batch_id,
                    batch_name=assessment.batch_name
                )
                
                # --- DEEPFACE REGISTRATION ---
                if snapshot:
                    _register_face_with_deepface(email, snapshot)
                
                # CROSS-UPDATE: Synchronize with the Candidate record if exists
                try:
                    # Use iexact and prioritize the same batch
                    candidates = Candidate.objects.filter(email__iexact=email).order_by('-id')
                    candidate = candidates.filter(batch_id=assessment.batch_id).first()
                    
                    # ONLY update the name if the candidate belongs to the SAME batch.
                    # Do not blindly fallback to candidates.first() for name updates, 
                    # as that mutates records from other pipelines.
                    if candidate:
                        logger.info(f"CreateSubmission: Reconciled candidate {candidate.id} for {email} in assessment {assessment.id}")
                        if name and (candidate.full_name == "Extraction Failed" or candidate.full_name != name):
                            candidate.full_name = name
                            candidate.save(update_fields=['full_name'])
                    else:
                        logger.info(f"CreateSubmission: No matching Candidate record found for {email} in batch {assessment.batch_id}")
                except Exception as sync_err:
                    logger.warning(f"Failed to cross-update candidate {email} on creation: {sync_err}")
                
            # Only pick and lock questions if they haven't been locked yet
            if not submission.candidate_questions:
                # Unique MCQ Distribution:
                # Resolve this candidate's 0-based index within the batch so pick_random_subset
                # can assign a non-overlapping slice of the MCQ pool (partitioned mode).
                # For same_questions_for_all, candidate_index is not used (sampling mode).
                candidate_index = None
                if not assessment.same_questions_for_all:
                    try:
                        # Index = position of this candidate's submission among all ONGOING/submitted
                        # submissions for this assessment, ordered by creation time.
                        all_subs = list(
                            AIAssessmentSubmission.objects.filter(
                                assessment=assessment
                            ).order_by('id').values_list('id', flat=True)
                        )
                        if submission.id in all_subs:
                            candidate_index = all_subs.index(submission.id)
                        else:
                            candidate_index = len(all_subs)  # fallback: append to end
                    except Exception as idx_err:
                        logger.warning(f"Could not resolve candidate_index for {email}: {idx_err}")

                submission.candidate_questions = pick_random_subset(
                    assessment, assessment.generated_content,
                    seed=email,
                    candidate_index=candidate_index
                )
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
                "coding_results": (submission.results_breakdown or {}).get('coding_results', {}),
                "codeDrafts": (submission.results_breakdown or {}).get('code_drafts', {}),
                "candidate_questions": submission.candidate_questions
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
            elif event_type in ['face_detection_lost', 'no_face_detection', 'no_face']:
                submission.face_warnings += 1
            elif event_type in ['multiface_detection', 'multiple_faces', 'multi_person']:
                submission.face_warnings += 1
            elif event_type in ['looking_away', 'head_yaw_exceeded', 'head_pitch_exceeded']:
                submission.face_warnings += 1
            elif event_type in ['face_mismatch', 'verification_failed']:
                submission.face_warnings += 1
            
            # Simple metadata log
            submission.monitoring_logs.append({
                "event": event_type,
                "timestamp": timezone.now().isoformat()
            })
            
            # Grace Warning System Phase 2: Handle First 3 as Warnings
            is_warning = len(submission.warning_logs) < 3
            if is_warning:
                submission.warning_logs.append(event_type)

            # Calculate integrity score based on violations
            # Start at 100, deduct penalties for actual violations (after grace period)
            if not is_warning:
                # Define penalties for different violation types
                penalties = {
                    'tab_switch': 3,
                    'window_blur': 2,
                    'screen_stop': 2,
                    'phone_detection': 10,
                    'face_detection_lost': 5,
                    'no_face_detection': 5,
                    'no_face': 5,
                    'multiface_detection': 10,
                    'multiple_faces': 10,
                    'multi_person': 10,
                    'looking_away': 3,
                    'head_yaw_exceeded': 3,
                    'head_pitch_exceeded': 3,
                    'face_mismatch': 10,
                    'verification_failed': 10,
                }
                
                # Get penalty for this event (default to 5 if not specified)
                penalty = penalties.get(event_type, 5)
                
                # Apply penalty
                submission.integrity_score = max(0, submission.integrity_score - penalty)
            
            # If this is the first violation being recorded, ensure we start from 100
            if submission.integrity_score is None or submission.integrity_score == 0:
                submission.integrity_score = 100.0
            
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
            coding_results = request.data.get('coding_results')
            code_drafts = request.data.get('codeDrafts')
            
            if answers is not None:
                submission.answers = answers
            if index is not None:
                submission.current_question_index = index
            
            if not submission.results_breakdown:
                submission.results_breakdown = {}
                
            if coding_results is not None:
                submission.results_breakdown['coding_results'] = coding_results
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
                ).exclude(status='FAILED').order_by('-created_at')
            else:
                # Scoped: only assessments created by users in this user's reporting hierarchy
                assessments = Assessment.objects.filter(
                    company=company, 
                    user_profile_id__in=scoped_ids, 
                    is_deleted=False
                ).exclude(status='FAILED').order_by('-created_at')

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
                    "batch_name": assessment.batch_name,
                    "creation_type": assessment.creation_type,
                    "max_candidates_allowed": assessment.max_candidates_allowed,
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
                    "job_title": assessment.required_skills,
                    "role": assessment.required_skills,
                    "assessment_name": assessment.required_skills,
                    "score": sub.score,
                    "mcq_score": sub.mcq_score,
                    "coding_score": sub.coding_score,
                    "results_breakdown": sub.results_breakdown,
                    "percentage": sub.percentage,
                    "status": sub.status,
                    "final_status": sub.status,
                    "integrity_score": sub.integrity_score,
                    "submitted_at": timezone.localtime(sub.submitted_at).strftime("%Y-%m-%d %H:%M") if sub.submitted_at else None,
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
                "mcq_weight": getattr(assessment, 'mcq_weight', 40) or 40,
                "coding_weight": 100 - (getattr(assessment, 'mcq_weight', 40) or 40),
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M") if assessment.created_at else None,
                "generated_content": _normalize_generated_pool(assessment.generated_content or {}),
                "status": assessment.status,
                "batch_name": assessment.batch_name,
                "creation_type": assessment.creation_type,
                "share_token": str(assessment.share_token),
                "num_applicants": assessment.num_applicants,
                "max_candidates_allowed": assessment.max_candidates_allowed,
                "same_questions_for_all": assessment.same_questions_for_all,
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
                "role_title": assessment.required_skills
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                        # Case 1 & 3 Bypass
                        if assessment.num_applicants <= 1 or assessment.same_questions_for_all:
                            final_content = _normalize_generated_pool(gen_content)
                        else:
                            # Use consistent index logic even in preview if submission exists
                            candidate_index = None
                            try:
                                all_subs = list(AIAssessmentSubmission.objects.filter(assessment=assessment).order_by('id').values_list('id', flat=True))
                                if submission.id in all_subs:
                                    candidate_index = all_subs.index(submission.id)
                            except: pass
                            final_content = pick_random_subset(assessment, gen_content, seed=email_param, candidate_index=candidate_index)
                            
                        submission.candidate_questions = final_content
                        submission.save(update_fields=['candidate_questions'])
                else:
                    # No submission yet, but we have an email. 
                    # Consistent set for the UI. Since there is no submission ID yet, 
                    # we use a fallback that will be reconciled when the submission is created.
                    if assessment.num_applicants <= 1 or assessment.same_questions_for_all:
                        final_content = _normalize_generated_pool(gen_content)
                    else:
                        final_content = pick_random_subset(assessment, gen_content, seed=email_param)


            # Prevent Answer Leakage: Strip MCQ answers from the public payload
            if isinstance(final_content, dict) and 'mcqs' in final_content:
                for mcq in final_content['mcqs']:
                    if isinstance(mcq, dict):
                        mcq.pop('answer', None)
                        mcq.pop('correct_answer', None)

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
        
        # Check if max candidates reached
        from .models import InvitedCandidate
        already_invited = InvitedCandidate.objects.filter(assessment=assessment).count()
        max_allowed = assessment.max_candidates_allowed
        
        import urllib.parse
        # Use frontend base URL from settings - Standardized to localhost for dev
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        base_link = f"{base_url}/take-ai-assessment/{assessment.share_token}"

        if invite_type == 'individual':
            name = request.data.get('name')
            email = request.data.get('email')
            if not name or not email:
                return Response({"error": "Name and Email are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if max reached
            if already_invited >= max_allowed:
                return Response({"error": f"Maximum {max_allowed} candidates allowed. Already invited {already_invited}."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already invited
            if InvitedCandidate.objects.filter(assessment=assessment, email=email).exists():
                return Response({"error": f"Candidate {email} already invited."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Append name and email
            encoded_name = urllib.parse.quote(name)
            encoded_email = urllib.parse.quote(email)
            link = f"{base_link}?name={encoded_name}&email={encoded_email}"
            
            # Save invited candidate
            InvitedCandidate.objects.create(assessment=assessment, name=name, email=email)
            
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

                # Check capacity
                max_allowed = assessment.max_candidates_allowed
                available_slots = max_allowed - already_invited
                num_to_invite = min(len(df), available_slots)
                
                if num_to_invite == 0:
                    return Response(
                        {"error": f"No available slots. Max {max_allowed} allowed, {already_invited} already invited."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                invitation_count = 0
                skipped_count = 0

                for idx, row in df.iterrows():
                    if invitation_count >= num_to_invite:
                        break
                        
                    name = str(row['name']).strip()
                    email = str(row['email']).strip()
                    
                    # Check if already invited
                    if InvitedCandidate.objects.filter(assessment=assessment, email=email).exists():
                        skipped_count += 1
                        continue
                    
                    encoded_name = urllib.parse.quote(name)
                    encoded_email = urllib.parse.quote(email)
                    link = f"{base_link}?name={encoded_name}&email={encoded_email}"
                    
                    # Save invited candidate
                    InvitedCandidate.objects.create(assessment=assessment, name=name, email=email)
                    invitation_count += 1
                    
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
        
        # Update assessment invited count to match invited candidates count
        assessment.invited_count = InvitedCandidate.objects.filter(assessment=assessment).count()
        assessment.save(update_fields=['invited_count'])
        
        # Calculate remaining spots
        remaining_spots = max(0, assessment.max_candidates_allowed - assessment.invited_count)

        return Response({
            "message": f"Successfully invited {len(invited_candidates)} {'candidate' if len(invited_candidates) == 1 else 'candidates'}",
            "count": len(invited_candidates),
            "total_invited": assessment.invited_count,
            "max_allowed": assessment.max_candidates_allowed,
            "remaining_spots": remaining_spots
        }, status=status.HTTP_200_OK)

class GetInvitedCandidatesView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]
    
    def get(self, request, assessment_id):
        """Get list of invited candidates for an assessment"""
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            assessment = Assessment.objects.filter(pk=assessment_id, company=company).first()
            if not assessment:
                assessment = Assessment.objects.filter(pk=assessment_id, user_profile=user_profile).first()
            
            if not assessment:
                raise Assessment.DoesNotExist
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        from .models import InvitedCandidate
        invited_qs = InvitedCandidate.objects.filter(assessment=assessment).order_by('-invited_at')
        
        invited_list = []
        for cand in invited_qs:
            invited_list.append({
                "name": cand.name,
                "email": cand.email,
                "status": cand.status,
                "invited_at": cand.invited_at.strftime("%Y-%m-%d %H:%M") if cand.invited_at else None
            })
        
        # Calculate candidate points (Division based on num_applicants vs same_questions)
        divisor = max(1, assessment.num_applicants) if not assessment.same_questions_for_all else 1
        
        mcq_pool_size = assessment.mcq_count if hasattr(assessment, 'mcq_count') else 0
        coding_pool_size = assessment.coding_count if hasattr(assessment, 'coding_count') else 0
        
        candidate_mcq_count = mcq_pool_size // divisor
        candidate_coding_count = coding_pool_size // divisor
        
        # Scoring: 1 pt per MCQ + weighted coding (matching actual scoring engine)
        mcq_points = candidate_mcq_count * 1
        
        # Calculate coding points based on difficulty weights of challenges in the pool
        coding_points = 0
        generated_content = assessment.generated_content or {}
        coding_pool = generated_content.get('coding_challenges', [])
        weight_map = {'Easy': 100, 'Medium': 200, 'Hard': 300}
        
        for i in range(min(len(coding_pool), candidate_coding_count)):
            difficulty = coding_pool[i].get('difficulty', 'Medium')
            coding_points += weight_map.get(difficulty, 200)
            
        total_candidate_points = mcq_points + coding_points
        
        remaining_spots = max(0, assessment.max_candidates_allowed - invited_qs.count())
        
        return Response({
            "invited_candidates": invited_list,
            "total_invited": invited_qs.count(),
            "max_allowed": assessment.max_candidates_allowed,
            "remaining_spots": remaining_spots,
            "can_invite_more": remaining_spots > 0,
            "candidate_points": {
                "mcq_count": candidate_mcq_count,
                "mcq_points": mcq_points,
                "coding_count": candidate_coding_count,
                "coding_points": coding_points,
                "total_points": total_candidate_points
            }
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
            
        from api._imports import get_scoped_user_ids
        scoped_ids = get_scoped_user_ids(user_profile)

        if scoped_ids is None:
            return AIAssessmentSubmission.objects.filter(assessment__company=company, is_deleted=False)
            
        return AIAssessmentSubmission.objects.filter(
            assessment__company=company, 
            assessment__user_profile_id__in=scoped_ids, 
            is_deleted=False
        )

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
            object_repr=f"AI Assessment Submission: {instance.candidate_name} ({instance.candidate_email})",
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

class AIAssessmentReportDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
            assessment = submission.assessment
            
            # RBAC: Ensure user belongs to the same company or is a superuser
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile or (user_profile.company != assessment.company and not request.user.is_superuser):
                return Response({'error': 'Unauthorized access to this assessment report.'}, status=status.HTTP_403_FORBIDDEN)

            # Generate PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )
            styles = getSampleStyleSheet()
            
            # Custom Styles for Premium Look
            styles.add(ParagraphStyle(
                'SubHeader',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor("#707EAE"),
                alignment=0,
                spaceAfter=12
            ))
            styles.add(ParagraphStyle(
                'CardLabel',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor("#A3AED0"),
                fontName='Helvetica-Bold',
                alignment=1,
                textTransform='uppercase'
            ))
            styles.add(ParagraphStyle(
                'CardValue',
                parent=styles['Normal'],
                fontSize=18,
                textColor=colors.HexColor("#4318FF"),
                fontName='Helvetica-Bold',
                alignment=1
            ))
            styles.add(ParagraphStyle(
                'CardSubValue',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-Bold',
                alignment=1
            ))
            styles.add(ParagraphStyle(
                'BannerLabel',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor("#A3AED0"),
                fontName='Helvetica-Bold',
                alignment=1,
                textTransform='uppercase'
            ))
            styles.add(ParagraphStyle(
                'BannerValue',
                parent=styles['Normal'],
                fontSize=28,
                textColor=colors.HexColor("#4318FF"),
                fontName='Helvetica-Bold',
                alignment=1
            ))
            styles.add(ParagraphStyle(
                'BannerStatus',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-Bold',
                alignment=1,
                textTransform='uppercase'
            ))
            styles.add(ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-Bold',
                spaceBefore=20,
                spaceAfter=15
            ))
            styles.add(ParagraphStyle(
                'QuestionHeader',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor("#707EAE"),
                fontName='Helvetica-Bold',
                textTransform='uppercase'
            ))
            styles.add(ParagraphStyle(
                'QuestionText',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-Bold',
                leading=14
            ))
            styles.add(ParagraphStyle(
                'BadgeCorrect',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor("#05CD99"),
                fontName='Helvetica-Bold',
                alignment=2
            ))
            styles.add(ParagraphStyle(
                'BadgeIncorrect',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor("#EE5D50"),
                fontName='Helvetica-Bold',
                alignment=2
            ))
            styles.add(ParagraphStyle(
                'SolutionBox',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor("#1B254B"),
                backColor=colors.HexColor("#E6FBF5"),
                borderPadding=10,
                borderWidth=0,
                borderRadius=10,
                fontName='Helvetica-Bold'
            ))
            styles.add(ParagraphStyle(
                'CodeTitle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.white,
                backColor=colors.HexColor("#4318FF"),
                borderPadding=5,
                borderRadius=5,
                fontName='Helvetica-Bold',
                alignment=0
            ))
            styles.add(ParagraphStyle(
                'RefCodeTitle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.white,
                backColor=colors.HexColor("#05CD99"),
                borderPadding=5,
                borderRadius=5,
                fontName='Helvetica-Bold',
                alignment=0
            ))
            styles.add(ParagraphStyle(
                'CodeContent',
                parent=styles['Code'],
                fontSize=8,
                textColor=colors.HexColor("#05CD99"),
                backColor=colors.HexColor("#1B254B"),
                borderPadding=15,
                borderRadius=15,
                fontName='Courier'
            ))
            styles.add(ParagraphStyle(
                'RefCodeContent',
                parent=styles['Code'],
                fontSize=8,
                textColor=colors.HexColor("#7EE787"),
                backColor=colors.HexColor("#0D1117"),
                borderPadding=15,
                borderRadius=15,
                fontName='Courier'
            ))

            elements = []

            # Calculate scores
            res_brk = submission.results_breakdown or {}
            mcq_scored = res_brk.get('mcq', {}).get('scored_points', 0)
            mcq_total = res_brk.get('mcq', {}).get('possible_points', submission.total_questions or 10)
            mcq_pct = round((mcq_scored / mcq_total * 100)) if mcq_total > 0 else 0
            
            coding_scored = res_brk.get('coding', {}).get('scored_points', 0)
            coding_total = res_brk.get('coding', {}).get('possible_points', 0)
            coding_pct = round((coding_scored / coding_total * 100)) if coding_total > 0 else 0

            integrity_score = submission.integrity_score
            integrity_label = "✓ Reliable" if integrity_score >= 50 else "⚠ Suspicious"
            integrity_color = colors.HexColor("#05CD99") if integrity_score >= 50 else colors.HexColor("#EE5D50")

            # Status display
            status_display = "Assessment Passed" if submission.status == 'selected' else "Not Qualified" if submission.status in ['rejected', 'hold'] else submission.status.upper()
            status_color = colors.HexColor("#05CD99") if submission.status == 'selected' else colors.HexColor("#EE5D50")

            # 1. Report Header - Interview Report Style
            elements.append(Paragraph("VerifiHireAI — Assessment Report", ParagraphStyle(
                'ReportHeader',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor("#4F46E5"),
                alignment=1,  # Center
                spaceAfter=6
            )))
            elements.append(Paragraph(f"Candidate: {submission.candidate_name}", ParagraphStyle(
                'CandidateSubHeader',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor("#1B254B"),
                alignment=1,
                spaceAfter=20
            )))

            # 2. Candidate Information Section
            elements.append(Paragraph("Candidate Information", ParagraphStyle(
                'SectionTitleItalic',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor("#1B254B"),
                fontName='Helvetica-BoldOblique',
                spaceAfter=10
            )))

            # Get candidate photo - try DeepFace registered face first
            candidate_img = None
            person_id = submission.candidate_email.lower().strip() if submission.candidate_email else None
            
            if person_id:
                try:
                    # Try to fetch registered face from DeepFace service
                    from pathlib import Path
                    import requests
                    
                    # Check if deepface has a registered face endpoint to retrieve image
                    deepface_img_url = f"{DEEPFACE_BASE_URL}/registration/registered/{person_id}"
                    resp = requests.get(deepface_img_url, timeout=5)
                    if resp.status_code == 200 and resp.json().get('registered'):
                        # Try to find the registered face image file
                        # DeepFace stores at: data/registered_faces/{person_id}/registration_snapshot.jpg
                        deepface_data_dir = Path(__file__).resolve().parent.parent.parent / 'deepface' / 'data' / 'registered_faces'
                        person_face_dir = deepface_data_dir / person_id
                        if person_face_dir.exists():
                            # Look for the registration snapshot
                            for img_file in person_face_dir.glob('*.jpg'):
                                try:
                                    candidate_img = RLImage(str(img_file), width=1.4*inch, height=1.4*inch)
                                    break
                                except:
                                    continue
                except Exception as e:
                    pass  # Fall back to screenshots
            
            # Fallback: Get from integrity screenshots (prefer webcam, avoid face_not_detected events)
            if not candidate_img:
                screenshots_qs = submission.screenshots.all().order_by('timestamp')
                for shot in screenshots_qs:
                    # Skip frames with no face detected
                    if shot.event_type and 'face_not_detected' in shot.event_type.lower():
                        continue
                    if shot.webcam_screenshot:
                        try:
                            candidate_img = RLImage(shot.webcam_screenshot.path, width=1.4*inch, height=1.4*inch)
                            break
                        except:
                            continue
                    elif shot.screenshot:
                        try:
                            candidate_img = RLImage(shot.screenshot.path, width=1.4*inch, height=1.4*inch)
                            break
                        except:
                            continue

            # Info table data
            # Handle old submissions without PAN data
            if submission.pan_number:
                pan_verified_text = "Yes ✓" if submission.pan_verified else "No ✗"
            else:
                pan_verified_text = "N/A"
            info_data = [
                ['Full Name', submission.candidate_name],
                ['Email', submission.candidate_email or 'N/A'],
                ['Phone', submission.phone or 'N/A'],
                ['PAN Number', submission.pan_number or 'N/A'],
                ['PAN Verified', pan_verified_text],
                ['Job Title', assessment.required_skills or 'N/A'],
                ['MCQ Score', f"{mcq_pct}% ({mcq_scored} / {mcq_total} Correct)"],
                ['Coding Score', f"{coding_pct}% ({coding_scored} / {coding_total} pts)"],
                ['Integrity Score', f"{integrity_score}% {integrity_label}"],
                ['Overall Result', f"{submission.percentage}%"],
                ['Status', status_display],
                ['Submission Date', submission.submitted_at.strftime('%B %d, %Y %I:%M %p') if submission.submitted_at else 'N/A'],
            ]

            # Style the info table
            info_table = Table(info_data, colWidths=[1.4*inch, 3.0*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8F9FF")),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (0,-1), 9),
                ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#64748b")),
                ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (1,0), (1,-1), 10),
                ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor("#1B254B")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (0,-1), 10),
                ('LEFTPADDING', (1,0), (1,-1), 10),
                ('TOPPADDING', (0,0), (-1,-1), 7),
                ('BOTTOMPADDING', (0,0), (-1,-1), 7),
                ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E0E5F2")),
                # Color coding for specific rows
                ('TEXTCOLOR', (1,5), (1,5), integrity_color),
                ('FONTNAME', (1,5), (1,5), 'Helvetica-Bold'),
                ('TEXTCOLOR', (1,6), (1,6), status_color),
                ('FONTNAME', (1,6), (1,6), 'Helvetica-Bold'),
                ('TEXTCOLOR', (1,7), (1,7), status_color),
                ('FONTNAME', (1,7), (1,7), 'Helvetica-Bold'),
            ]))

            # Photo section
            if candidate_img:
                photo_label = Paragraph("Candidate Photo", ParagraphStyle('PhotoLabel', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor("#707EAE")))
                photo_cell = [[candidate_img], [photo_label]]
                photo_table = Table(photo_cell, colWidths=[1.5*inch], rowHeights=[1.5*inch, 18])
                photo_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (0,0), 'CENTER'),
                    ('VALIGN', (0,0), (0,0), 'MIDDLE'),
                    ('ALIGN', (0,1), (0,1), 'CENTER'),
                    ('VALIGN', (0,1), (0,1), 'TOP'),
                    ('TOPPADDING', (0,1), (0,1), 4),
                ]))
            else:
                no_photo_text = Paragraph("No candidate<br/>photo available", ParagraphStyle('NoPhoto', parent=styles['Normal'], fontSize=9, alignment=1, textColor=colors.grey))
                photo_table = Table([[no_photo_text]], colWidths=[1.5*inch], rowHeights=[1.5*inch])
                photo_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F4F7FE")),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))

            # Combine photo + info in a bordered container
            page_width = A4[0] - 100  # Total usable width (50pt margins each side)
            combined_data = [[photo_table, info_table]]
            combined_table = Table(combined_data, colWidths=[1.8*inch, page_width - 1.8*inch])
            combined_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (0,0), (0,0), 'CENTER'),
                ('LEFTPADDING', (0,0), (0,0), 10),
                ('RIGHTPADDING', (0,0), (0,0), 10),
                ('LEFTPADDING', (1,0), (1,0), 5),
                ('RIGHTPADDING', (1,0), (1,0), 5),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                # Outer border box
                ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#D0D5E4")),
                ('ROUNDEDCORNERS', [6, 6, 6, 6]),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FCFCFF")),
                # Vertical divider between photo and info
                ('LINEAFTER', (0,0), (0,-1), 0.5, colors.HexColor("#E0E5F2")),
            ]))
            elements.append(combined_table)

            elements.append(Spacer(1, 30))

            # 4. MCQ Section
            generated_content = submission.candidate_questions or assessment.generated_content or {}
            if 'mcqs' not in generated_content and 'coding_challenges' not in generated_content:
                for val in generated_content.values():
                    if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                        generated_content = val
                        break
            
            mcqs = generated_content.get('mcqs', [])
            coding_challenges = generated_content.get('coding_challenges', [])
            answers = submission.answers or {}

            if mcqs:
                elements.append(Paragraph("MCQ Answer Verification", styles['SectionTitle']))
                page_width = A4[0] - 100  # Usable width

                for i, mcq in enumerate(mcqs):
                    q_text = mcq.get('question', 'N/A')
                    options = mcq.get('options', [])
                    correct_ans = str(mcq.get('answer') or mcq.get('correct_answer') or '').strip()
                    candidate_ans = str(answers.get(f'mcq_{i}') or '').strip()
                    is_correct = candidate_ans == correct_ans

                    # Question Header with Badge — full width
                    badge_text = "CORRECT" if is_correct else "INCORRECT"
                    badge_style = styles['BadgeCorrect'] if is_correct else styles['BadgeIncorrect']
                    q_header_table = Table(
                        [[Paragraph(f"QUESTION {i+1}", styles['QuestionHeader']), Paragraph(badge_text, badge_style)]],
                        colWidths=[page_width - 1.6*inch, 1.6*inch]
                    )
                    q_header_table.setStyle(TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('ALIGN', (1,0), (1,0), 'RIGHT'),
                    ]))
                    elements.append(q_header_table)
                    elements.append(Paragraph(q_text, styles['QuestionText']))
                    elements.append(Spacer(1, 8))

                    # Options — stacked vertically, each as a full-width bordered row
                    for oi, opt in enumerate(options):
                        is_selected = opt == candidate_ans
                        is_ans = opt == correct_ans
                        
                        bg = colors.white
                        border_color = colors.HexColor("#E0E5F2")
                        txt_color = colors.HexColor("#1B254B")
                        marker = ""
                        
                        if is_ans:
                            bg = colors.HexColor("#E6FBF5")
                            border_color = colors.HexColor("#05CD99")
                            txt_color = colors.HexColor("#05CD99")
                            marker = " (Correct Answer)"
                        elif is_selected and not is_correct:
                            bg = colors.HexColor("#FFF5F5")
                            border_color = colors.HexColor("#EE5D50")
                            txt_color = colors.HexColor("#EE5D50")
                            marker = " (Your Answer)"
                        elif is_selected and is_correct:
                            marker = " (Your Answer)"
                        
                        prefix = f"{chr(65+oi)}."
                        opt_para = Paragraph(
                            f"<b>{prefix}</b> {opt}<font color='#94A3B8'>{marker}</font>",
                            ParagraphStyle('OptStyle', parent=styles['Normal'], textColor=txt_color, fontSize=9, leading=13)
                        )
                        opt_table = Table([[opt_para]], colWidths=[page_width - 10])
                        opt_table.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,-1), bg),
                            ('BOX', (0,0), (-1,-1), 0.8, border_color),
                            ('LEFTPADDING', (0,0), (-1,-1), 10),
                            ('RIGHTPADDING', (0,0), (-1,-1), 10),
                            ('TOPPADDING', (0,0), (-1,-1), 6),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ]))
                        elements.append(opt_table)
                        elements.append(Spacer(1, 3))

                    # Correct Solution Box if incorrect
                    if not is_correct:
                        elements.append(Spacer(1, 6))
                        sol_box = Table(
                            [[Paragraph("CORRECT ANSWER:", styles['QuestionHeader']), Paragraph(correct_ans, styles['SolutionBox'])]],
                            colWidths=[1.5*inch, page_width - 1.5*inch]
                        )
                        sol_box.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E6FBF5")),
                            ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#05CD99")),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('LEFTPADDING', (0,0), (-1,-1), 10),
                            ('TOPPADDING', (0,0), (-1,-1), 6),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ]))
                        elements.append(sol_box)

                    elements.append(Spacer(1, 20))

            # 5. Coding Section
            if coding_challenges:
                elements.append(PageBreak())
                elements.append(Paragraph("Coding Verification", styles['SectionTitle']))
                coding_results = (submission.results_breakdown or {}).get('coding_results', {})

                for i, challenge in enumerate(coding_challenges):
                    title = challenge.get('title', 'N/A')
                    desc = challenge.get('problem_statement', challenge.get('description', 'N/A'))
                    student_code = answers.get(f'coding_{i}', '// No code submitted')
                    ref_solution = challenge.get('reference_solution', '')
                    
                    res = coding_results.get(str(i), {})
                    passed = res.get('passed', 0)
                    total_tc = res.get('total', challenge.get('test_cases', []).__len__() if isinstance(challenge.get('test_cases'), list) else 0)
                    
                    # Challenge Header
                    elements.append(Paragraph(title, styles['Heading3']))
                    elements.append(Paragraph(desc, styles['Normal']))
                    elements.append(Paragraph(f"<b>Passed Tests:</b> {passed} / {total_tc}", styles['Normal']))
                    elements.append(Spacer(1, 15))

                    # Candidate Submission
                    elements.append(Paragraph("CANDIDATE SUBMISSION", styles['CodeTitle']))
                    elements.append(XPreformatted(student_code, styles['CodeContent']))
                    elements.append(Spacer(1, 15))

                    # Reference Solution
                    if ref_solution:
                        elements.append(Paragraph("✓ REFERENCE SOLUTION (ANSWER KEY)", styles['RefCodeTitle']))
                        elements.append(XPreformatted(ref_solution, styles['RefCodeContent']))
                        elements.append(Spacer(1, 30))

            # 6. Integrity Violations Log
            elements.append(PageBreak())
            elements.append(Paragraph("Integrity Violations Log", styles['SectionTitle']))
            
            screenshots = submission.screenshots.all().order_by('timestamp')
            if screenshots.exists():
                # Display in a grid-like fashion (4 images per row)
                shots_list = list(screenshots)
                img_grid = []
                current_row = []
                page_width = A4[0] - 100  # Usable width
                col_w = page_width / 4
                
                for shot in shots_list:
                    img_path = None
                    if shot.webcam_screenshot: img_path = shot.webcam_screenshot.path
                    elif shot.screenshot: img_path = shot.screenshot.path
                    
                    try:
                        if img_path:
                            rl_img = RLImage(img_path, width=col_w - 12, height=(col_w - 12) * 0.75)
                            label = f"{shot.event_type.replace('_', ' ').title()} ({shot.timestamp.strftime('%I:%M:%S %p')})"
                            current_row.append([rl_img, Paragraph(label, ParagraphStyle('ShotLabel', parent=styles['Normal'], fontSize=7, alignment=1, textColor=colors.grey, leading=9))])
                        else:
                            current_row.append(Paragraph("No Image", styles['Normal']))
                    except:
                        current_row.append(Paragraph("Error Loading", styles['Normal']))

                    if len(current_row) == 4:
                        img_grid.append(current_row)
                        current_row = []

                if current_row:
                    while len(current_row) < 4:
                        current_row.append("")
                    img_grid.append(current_row)

                for grid_row in img_grid:
                    t = Table([grid_row], colWidths=[col_w] * 4)
                    t.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 3),
                        ('RIGHTPADDING', (0,0), (-1,-1), 3),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                    ]))
                    elements.append(t)
            else:
                elements.append(Paragraph("No violations recorded. Candidate maintained full integrity.", styles['Italic']))

            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            # Prepare Response
            response = HttpResponse(buffer, content_type='application/pdf')
            safe_name = "".join([c for c in submission.candidate_name if c.isalnum() or c==' ']).rstrip().replace(' ', '_')
            filename = f"AI_Assessment_Report_{safe_name}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except AIAssessmentSubmission.DoesNotExist:
            return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generating PDF report for submission {pk}: {str(e)}", exc_info=True)
            return Response({'error': f"Critical failure: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AIAssessmentSubmissionListView(APIView):
    def get(self, request):
        candidate_email = request.query_params.get('candidate_email')
        batch_name = request.query_params.get('batch_name')
        batch_id = request.query_params.get('batch_id')
        submission_id = request.query_params.get('submission_id')
        
        if not candidate_email and not submission_id:
            return Response({"error": "candidate_email or submission_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        qs = AIAssessmentSubmission.objects.all()
        if candidate_email:
            qs = qs.filter(candidate_email__iexact=candidate_email)
        if batch_name:
            qs = qs.filter(batch_name=batch_name)
        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        if submission_id:
            qs = qs.filter(id=submission_id.replace('ai_', '') if str(submission_id).startswith('ai_') else submission_id)
            
        submissions = qs.order_by('-submitted_at')
        
        data = []
        from django.utils import timezone
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

            data.append({
                "id": sub.id,
                "submission_id": f"ai_{sub.id}",
                "candidate_name": sub.candidate_name,
                "candidate_email": sub.candidate_email,
                "job_title": sub.assessment.required_skills,
                "role": sub.assessment.required_skills,
                "assessment_name": sub.assessment.required_skills,
                "score": sub.score,
                "mcq_score": sub.mcq_score,
                "coding_score": sub.coding_score,
                "results_breakdown": sub.results_breakdown,
                "percentage": sub.percentage,
                "status": sub.status,
                "final_status": sub.status,
                "integrity_score": sub.integrity_score,
                "submitted_at": timezone.localtime(sub.submitted_at).strftime("%Y-%m-%d %H:%M") if sub.submitted_at else None,
                "candidate_questions": sub.candidate_questions,
                "answers": sub.answers,
                "integrity_screenshots": screenshots_data,
                "is_resume_screening": False,
                "assessment": {
                    "id": sub.assessment.id,
                    "display_name": sub.assessment.required_skills,
                    "name": sub.assessment.required_skills
                }
            })
        return Response({"results": data}, status=status.HTTP_200_OK)
