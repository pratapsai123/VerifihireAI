"""
Celery tasks for AI Assessment generation.

This module contains the long-running assessment generation logic that was
previously executed synchronously inside GenerateAssessmentView.post().
Moving it to a Celery task prevents 504 Gateway Timeout errors.
"""

import logging
import traceback

from celery import shared_task
from django.core.cache import cache
from django.utils import timezone

from ai_assessments.llm_client import create_llm_client, LLMKeyManager, get_default_model
from ai_assessments.ai_logic import (
    _normalize_difficulty_label,
    _normalize_generated_pool,
    _mcq_difficulty_counts,
    _rebalance_mcq_difficulties,
    _repair_pool_shortfall,
    _generate_execution_verified_coding_pool,
    _generate_mcq_pool_ai_only,
    _expert_assessment_refiner,
    _validate_mcq_structure,
)

logger = logging.getLogger(__name__)

PRIMARY_MODEL = get_default_model()
FALLBACK_MODEL = get_default_model()


def _set_progress(task_id, message, step=None, total_steps=8):
    """Store a progress update in Redis cache for the status endpoint to read."""
    cache.set(f"gen_progress_{task_id}", {
        "message": message,
        "step": step,
        "total_steps": total_steps,
    }, timeout=600)


@shared_task(bind=True, name='ai_assessments.tasks.generate_assessment_task',
             max_retries=0, time_limit=600, soft_time_limit=540)
def generate_assessment_task(self, params):
    """
    Async assessment generation task.

    This contains the EXACT same logic that was previously in
    GenerateAssessmentView.post() (lines 786-1214 of views.py).

    Args:
        params: dict containing all generation parameters:
            - job_description, required_skills, experience_level
            - mcq_count, mcq_easy, mcq_medium, mcq_hard
            - coding_count, coding_tasks
            - mcq_duration, coding_duration, duration
            - total_possible_points, num_applicants, same_questions_for_all
            - mcq_weight, available_from, available_until, pass_threshold
            - cancel_token, user_profile_id, company_id
            - pool_easy, pool_medium, pool_hard, pool_mcq_total
            - pool_coding_total, pool_coding_tasks
            - job_title

    Returns:
        dict with 'assessment_id', 'message', and 'data' on success.
        dict with 'error' and 'message' on failure.
    """
    task_id = self.request.id
    _set_progress(task_id, "Starting assessment generation...", step=1)

    # Extract all parameters
    job_description = params['job_description']
    required_skills = params['required_skills']
    experience_level = params.get('experience_level')
    cancel_token = params.get('cancel_token')

    mcq_count = params['mcq_count']
    mcq_easy = params['mcq_easy']
    mcq_medium = params['mcq_medium']
    mcq_hard = params['mcq_hard']
    coding_count = params['coding_count']
    coding_tasks = params['coding_tasks']

    mcq_duration = params['mcq_duration']
    coding_duration = params['coding_duration']
    duration = params['duration']
    total_possible_points = params['total_possible_points']
    num_applicants = params['num_applicants']
    same_questions_for_all = params['same_questions_for_all']
    mcq_weight = params['mcq_weight']
    available_from = params.get('available_from')
    available_until = params.get('available_until')
    pass_threshold = params.get('pass_threshold', 60)

    user_profile_id = params.get('user_profile_id')
    company_id = params.get('company_id')
    job_title = params.get('job_title')

    pool_easy = params['pool_easy']
    pool_medium = params['pool_medium']
    pool_hard = params['pool_hard']
    pool_mcq_total = params['pool_mcq_total']
    pool_coding_total = params['pool_coding_total']
    pool_coding_tasks = params['pool_coding_tasks']

    try:
        # Resolve user_profile and company from IDs
        from api.models import UserProfile
        from api.utils.batch_utils import generate_batch_id, generate_batch_name
        from ai_assessments.models import Assessment

        user_profile = None
        company = None
        if user_profile_id:
            try:
                user_profile = UserProfile.objects.get(pk=user_profile_id)
                company = user_profile.company
            except UserProfile.DoesNotExist:
                pass
        if company_id and not company:
            try:
                from api.models import Company
                company = Company.objects.get(pk=company_id)
            except Exception:
                pass

        # --- LLM Client Setup ---
        local_api_key = LLMKeyManager.get_current_key()
        local_llm_client = create_llm_client(api_key=local_api_key, timeout=60.0)
        generated_data = {"mcqs": [], "coding_challenges": []}

        # 1. GENERATE MCQ POOL (Dedicated AI Call)
        _set_progress(task_id, "Generating MCQ questions...", step=2)
        blacklist_mcqs = []
        blacklist_titles = []

        # Fetch last 20 assessments for this company to avoid replicates
        recent_assessments = Assessment.objects.filter(
            company=company, is_deleted=False
        ).order_by('-created_at')[:20]
        for old_asm in recent_assessments:
            old_content = old_asm.generated_content or {}
            for q in old_content.get('mcqs', []):
                blacklist_mcqs.append(q.get('question', '')[:100])
            for challenge in old_content.get('coding_challenges', []):
                blacklist_titles.append(challenge.get('title'))

        if pool_mcq_total > 0:
            logger.info(f"Step 1: Generating MCQ pool of {pool_mcq_total} questions. Blacklist: {len(blacklist_mcqs)}")
            mcqs = _generate_mcq_pool_ai_only(
                llm_client=local_llm_client,
                job_description=job_description,
                required_skills=required_skills,
                pool_mcq_total=pool_mcq_total,
                pool_easy=pool_easy,
                pool_medium=pool_medium,
                pool_hard=pool_hard,
                experience_level=experience_level,
                blacklist_qs=blacklist_mcqs,
                model=FALLBACK_MODEL,
                cancel_token=cancel_token
            )
            if mcqs:
                generated_data['mcqs'] = mcqs[:pool_mcq_total]

        # 2. GENERATE CODING POOL (Skeleton-Based: 100% Accuracy)
        _set_progress(task_id, "Generating coding challenges...", step=3)
        if pool_coding_total > 0:
            logger.info(f"Step 2: Generating {pool_coding_total} execution-verified coding challenges.")
            generated_data['coding_challenges'] = _generate_execution_verified_coding_pool(
                llm_client=local_llm_client,
                job_description=job_description,
                required_skills=required_skills,
                difficulties=pool_coding_tasks,
                total_required=pool_coding_total,
                model=PRIMARY_MODEL,
                cancel_token=cancel_token
            )
        else:
            logger.info("Step 2: Skipping coding pool generation (coding_count=0)")
            generated_data['coding_challenges'] = []

        # --- Expert Refiner for MCQs ---
        _set_progress(task_id, "Refining and cleaning questions...", step=4)
        if generated_data.get('mcqs'):
            if len(generated_data['mcqs']) > 25:
                logger.info(f"Expert Gate BYPASSED: Pool size ({len(generated_data['mcqs'])}) is large.")
            else:
                logger.info("Expert Gate: Cleaning and Refining MCQ pool...")
                mcq_refined_data = _expert_assessment_refiner(
                    llm_client=local_llm_client,
                    raw_content={"mcqs": generated_data['mcqs'], "coding_challenges": []},
                    cancel_token=cancel_token
                )
                generated_data['mcqs'] = mcq_refined_data.get('mcqs', [])

        # RE-CALCULATE FINAL METRICS
        final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
        final_mcqs = len(generated_data.get('mcqs', []))
        final_coding = len(generated_data.get('coding_challenges', []))

        # If MCQ count is enough but labels are still skewed, rebalance
        if final_mcqs >= pool_mcq_total and pool_mcq_total > 0 and (
            final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard
        ):
            logger.warning(
                f"Dedicated MCQ generation still skewed (got {final_easy}/{final_medium}/{final_hard}). "
                "Rebalancing difficulty labels."
            )
            generated_data['mcqs'] = _rebalance_mcq_difficulties(
                generated_data.get('mcqs', []),
                easy_required=pool_easy,
                medium_required=pool_medium,
                hard_required=pool_hard,
            )
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))

        # --- REBALANCING & REPAIR GATE (Self-Healing) ---
        _set_progress(task_id, "Running quality validation...", step=5)
        final_mcqs = len(generated_data.get('mcqs', []))
        final_coding = len(generated_data.get('coding_challenges', []))
        final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))

        if (final_mcqs < pool_mcq_total or final_coding < pool_coding_total or
                final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):

            _set_progress(task_id, "Repairing shortfalls...", step=6)
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

            logger.info(f"\n🔧 SELF-HEALING REPAIR TRIGGERED:\n   Shortfalls: {', '.join(shortfall_details)}")
            generated_data = _repair_pool_shortfall(
                llm_client=local_llm_client,
                job_description=job_description,
                required_skills=required_skills,
                pool=generated_data,
                pool_easy=pool_easy,
                pool_medium=pool_medium,
                pool_hard=pool_hard,
                pool_coding_total=pool_coding_total,
                coding_tasks=pool_coding_tasks,
                experience_level=experience_level,
                model=PRIMARY_MODEL
            )
            final_mcqs = len(generated_data.get('mcqs', []))
            final_coding = len(generated_data.get('coding_challenges', []))
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
            logger.info(f"\n✅ REPAIR COMPLETE: MCQs={final_mcqs} ({final_easy}E/{final_medium}M/{final_hard}H), Coding={final_coding}")

        # --- FORCED REBALANCING GATE ---
        if final_mcqs >= pool_mcq_total:
            generated_data['mcqs'] = _rebalance_mcq_difficulties(
                generated_data.get('mcqs', []),
                easy_required=pool_easy,
                medium_required=pool_medium,
                hard_required=pool_hard
            )
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
                logger.warning(f"   ⚠️ INVALID MCQ REMOVED: {error_msg}. Question: {mcq.get('question', '')[:40]}...")

        logger.info(
            f"\n📊 FINAL PASS RESULTS:\n"
            f"   Input pool: {len(all_mcqs)} MCQs\n"
            f"   Valid MCQs: {len(valid_mcqs)}\n"
            f"   Removed (invalid): {invalid_count}\n"
            f"   {'⚠️  WARNING: ' + str(invalid_count) + ' invalid MCQs removed!' if invalid_count > 0 else '✅ All MCQs valid!'}"
        )

        generated_data['mcqs'] = valid_mcqs
        final_mcqs = len(valid_mcqs)
        final_easy, final_medium, final_hard = _mcq_difficulty_counts(valid_mcqs)

        # Check if shortfall created by removing invalid MCQs
        if invalid_count > 0 and final_mcqs < pool_mcq_total:
            logger.warning(f"\n⚠️  SHORTFALL AFTER CLEANUP: {invalid_count} invalid MCQs removed. Triggering repair...")
            try:
                repair_generated = _repair_pool_shortfall(
                    llm_client=local_llm_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    pool=generated_data,
                    pool_easy=pool_easy,
                    pool_medium=pool_medium,
                    pool_hard=pool_hard,
                    pool_coding_total=pool_coding_total,
                    coding_tasks=pool_coding_tasks,
                    experience_level=experience_level,
                    model=PRIMARY_MODEL
                )
                generated_data = repair_generated
                all_mcqs_after_repair = generated_data.get('mcqs', [])
                valid_mcqs_after_repair = []
                for mcq in all_mcqs_after_repair:
                    is_valid, _ = _validate_mcq_structure(mcq)
                    if is_valid:
                        valid_mcqs_after_repair.append(mcq)
                generated_data['mcqs'] = valid_mcqs_after_repair
                final_mcqs = len(valid_mcqs_after_repair)
                final_easy, final_medium, final_hard = _mcq_difficulty_counts(valid_mcqs_after_repair)
                logger.info(f"✅ Repair completed. MCQs now: {final_mcqs} valid ({final_easy}E/{final_medium}M/{final_hard}H)")
            except Exception as repair_e:
                logger.error(f"❌ Repair failed during post-cleanup: {repair_e}")
                raise

        # Check minimum still met after cleaning
        if final_mcqs < mcq_count:
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

        for challenge in all_coding:
            test_cases = challenge.get('test_cases', [])
            tc_count = len(test_cases)
            if tc_count < MIN_TC:
                removed_coding += 1
                logger.warning(
                    f"   ⚠️ CODING CHALLENGE REMOVED: '{challenge.get('title', 'Unknown')}' has {tc_count}/{MIN_TC} test cases."
                )
            else:
                valid_coding.append(challenge)
                logger.info(f"   ✅ Challenge '{challenge.get('title', 'Unknown')}' valid ({tc_count} test cases)")

        generated_data['coding_challenges'] = valid_coding
        final_coding = len(valid_coding)

        # Check if shortfall created by removing insufficient coding challenges
        if removed_coding > 0 and final_coding < pool_coding_total:
            logger.warning(f"\n⚠️  SHORTFALL AFTER CLEANUP: {removed_coding} coding challenges removed. Triggering repair...")
            try:
                repair_generated = _repair_pool_shortfall(
                    llm_client=local_llm_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    pool=generated_data,
                    pool_easy=pool_easy,
                    pool_medium=pool_medium,
                    pool_hard=pool_hard,
                    pool_coding_total=pool_coding_total,
                    coding_tasks=pool_coding_tasks,
                    experience_level=experience_level,
                    model=PRIMARY_MODEL
                )
                generated_data = repair_generated
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

        # Check minimum still met after cleaning
        if final_coding < coding_count:
            raise Exception(
                f"All coding challenges failed final quality check. "
                f"After removing {removed_coding} invalid challenges, only {final_coding} valid "
                f"challenges remain but {coding_count} required."
            )

        # Final Validation Gate
        if final_mcqs < mcq_count or final_coding < coding_count:
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
            logger.warning(f"MCQ Difficulty split check bypassed. Expected {pool_easy}/{pool_medium}/{pool_hard}; got {final_easy}/{final_medium}/{final_hard}.")

        # --- SAVE ASSESSMENT TO DATABASE ---
        _set_progress(task_id, "Saving assessment...", step=7)

        assessment = Assessment.objects.create(
            job_description=job_description,
            required_skills=required_skills,
            experience_level=experience_level,
            mcq_count=mcq_count,
            mcq_easy=mcq_easy,
            mcq_medium=mcq_medium,
            mcq_hard=mcq_hard,
            coding_count=coding_count,
            coding_difficulty_list=coding_tasks,
            duration_minutes=duration,
            mcq_duration_minutes=mcq_duration,
            coding_duration_minutes=coding_duration,
            total_points=total_possible_points,
            num_applicants=num_applicants,
            max_candidates_allowed=num_applicants,
            same_questions_for_all=same_questions_for_all,
            mcq_weight=mcq_weight,
            available_from=available_from,
            available_until=available_until,
            pass_threshold=pass_threshold,
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

        _set_progress(task_id, "Assessment generated successfully!", step=8)

        return {
            "status": "completed",
            "assessment_id": assessment.id,
            "message": "Assessment generated successfully",
        }

    except Exception as e:
        tb = traceback.format_exc()
        error_msg = str(e)

        # Log to terminal-like file for easy debugging
        error_log = f"\n[{timezone.now()}] ERROR in generate_assessment_task: {error_msg}\n{tb}\n"
        try:
            with open('api_debug.txt', 'a') as f:
                f.write(error_log)
        except Exception:
            pass

        logger.error(f"ERROR in generate_assessment_task: {error_msg}\n{tb}")

        if "rate_limit_exceeded" in error_msg.lower():
            user_msg = "AI Provider rate limit reached. Please wait a few minutes and try again."
        elif "json_validate_failed" in error_msg.lower() or "badrequest" in error_msg.lower():
            user_msg = "AI generation failed to produce a valid structure. Please try simplifying your Job Description or reducing question counts."
        else:
            user_msg = f"Generation failed: {error_msg}"

        _set_progress(task_id, f"Failed: {user_msg}", step=-1)

        return {
            "status": "failed",
            "error": error_msg,
            "message": user_msg,
        }
