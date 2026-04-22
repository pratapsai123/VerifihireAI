import logging
import traceback as tb
from django.conf import settings
from django.core.mail import send_mail
from urllib.parse import quote
from ai_candidates.models import Candidate
from ai_assessments.models import Assessment, AIAssessmentSubmission

logger = logging.getLogger(__name__)


def process_batch_assessment(batch_id):
    """
    Triggered after a batch processing task completes.
    Generates ONE assessment pool for the entire batch based on who actually passed.
    Sends individual assessment invitation emails to each passed candidate.
    """
    from groq import Groq
    from ai_assessments.ai_logic import (
        _call_groq_with_backoff, _repair_pool_shortfall, _normalize_generated_pool,
        _generate_mcq_pool_ai_only, _generate_execution_verified_coding_pool,
        _expert_assessment_refiner, _validate_mcq_structure,
        _mcq_difficulty_counts, _rebalance_mcq_difficulties, GroqKeyManager
    )
    from ai_candidates.utils import log_automation_event

    try:
        raw_passed_candidates = list(Candidate.objects.filter(batch_id=batch_id, status='Resume Passed').order_by('id'))
        
        passed_candidates = []
        seen_emails = set()
        
        for candidate in raw_passed_candidates:
            email = (candidate.email or "").strip().lower()
            if email and email not in seen_emails:
                seen_emails.add(email)
                passed_candidates.append(candidate)
            elif not email:
                passed_candidates.append(candidate)
                
        num_passed = len(passed_candidates)

        logger.info(f"Pipeline[{batch_id}]: Batch assessment triggered. Found {num_passed} unique passed candidates (out of {len(raw_passed_candidates)} total passed).")

        if num_passed == 0:
            logger.info(f"Pipeline[{batch_id}]: No candidates passed. Skipping assessment generation.")
            return

        # Use the first candidate as a template for automation settings
        trigger_candidate = passed_candidates[0]
        settings_data = trigger_candidate.automation_settings or {}

        # ── 1. GENERATE / REUSE ASSESSMENT POOL ──
        assessment = Assessment.objects.filter(batch_id=batch_id).first()
        if assessment:
            logger.info(f"Pipeline[{batch_id}]: Assessment pool already exists (id={assessment.id}). Reusing for email sends.")
        else:
            logger.info(
                f"Pipeline[{batch_id}]: Generating shared assessment pool for {num_passed} passed candidate(s). "
                f"Job title: '{trigger_candidate.job_title}'"
            )

            job_desc = trigger_candidate.job_description or "General Software Engineering Role"
            difficulty = settings_data.get('difficulty', 'Medium')
            duration = settings_data.get('duration', 60)
            mcq_count = settings_data.get('mcq_count', 10)
            coding_count = settings_data.get('coding_count', 1)
            pass_threshold = settings_data.get('pass_threshold', 60)
            same_questions = bool(settings_data.get('same_questions_for_all', False))

            from django.utils.dateparse import parse_datetime
            from django.utils import timezone as tz

            a_from_str = settings_data.get('assessment_available_from')
            a_until_str = settings_data.get('assessment_available_until')
            assessment_from = parse_datetime(a_from_str) if a_from_str else None
            assessment_until = parse_datetime(a_until_str) if a_until_str else None

            # Calculate per-candidate difficulty breakdown
            mcq_easy_per_candidate = mcq_count // 2
            mcq_medium_per_candidate = (mcq_count * 3) // 10
            mcq_hard_per_candidate = max(0, mcq_count - mcq_easy_per_candidate - mcq_medium_per_candidate)

            # Create Assessment Record with clearer naming/ownership for visibility
            assessment_name = f"[Pipeline] {trigger_candidate.job_title or 'Technical Test'}"
            if trigger_candidate.batch_name:
                assessment_name = f"{assessment_name} - {trigger_candidate.batch_name}"

            assessment = Assessment.objects.create(
                job_description=job_desc,
                required_skills=assessment_name, # Clearly identifiable title
                mcq_count=mcq_count,
                coding_count=coding_count,
                duration_minutes=duration,
                difficulty_level=difficulty,
                pass_threshold=pass_threshold,
                status='GENERATING',
                available_from=assessment_from,
                available_until=assessment_until,
                batch_id=batch_id,
                batch_name=trigger_candidate.batch_name,
                same_questions_for_all=same_questions,
                num_applicants=num_passed,
                # Explicitly link to the recruiter who triggered this batch
                user_profile=getattr(trigger_candidate, 'user_profile', None),
                created_by=getattr(trigger_candidate, 'user_profile', None),
                company=getattr(trigger_candidate, 'company', None),
                mcq_easy=mcq_easy_per_candidate,
                mcq_medium=mcq_medium_per_candidate,
                mcq_hard=mcq_hard_per_candidate,
                total_points=100,
                mcq_weight=int(settings_data.get('mcq_weight', 40)),
                max_candidates_allowed=num_passed,
                invited_count=num_passed,
                creation_type='automatic'
            )
            logger.info(f"Pipeline[{batch_id}]: Assessment record created (id={assessment.id}). Calling AI...")

            # Pool size multipliers
            multiplier = num_passed if (num_passed > 1 and not same_questions) else 1
            pool_mcq_total = mcq_count * multiplier
            pool_coding_total = coding_count * multiplier if coding_count <= 10 else coding_count

            pool_easy = int(pool_mcq_total * 0.5)
            pool_medium = int(pool_mcq_total * 0.3)
            pool_hard = max(0, pool_mcq_total - pool_easy - pool_medium)

            # --- FULL MANUAL-GRADE GENERATION PIPELINE ---
            coding_tasks_list = [difficulty] * coding_count
            pool_coding_tasks = coding_tasks_list * multiplier

            local_api_key = GroqKeyManager.get_current_key()
            local_groq_client = Groq(api_key=local_api_key, timeout=60.0)
            generated_data = {"mcqs": [], "coding_challenges": []}
            AI_MODEL = "llama-3.1-8b-instant"

            # 1. BLACKLIST: Fetch last 20 assessments to avoid duplicate questions
            blacklist_mcqs = []
            blacklist_titles = []
            recent_assessments_bl = Assessment.objects.filter(company=assessment.company, is_deleted=False).order_by('-created_at')[:20]
            for old_asm in recent_assessments_bl:
                old_content = old_asm.generated_content or {}
                for q in old_content.get('mcqs', []):
                    blacklist_mcqs.append(q.get('question', '')[:100])
                for challenge in old_content.get('coding_challenges', []):
                    blacklist_titles.append(challenge.get('title'))

            # 2. GENERATE MCQ POOL (Dedicated AI Call)
            if pool_mcq_total > 0:
                logger.info(f"Pipeline[{batch_id}]: Step 1 — Generating MCQ pool of {pool_mcq_total} questions. Blacklist: {len(blacklist_mcqs)}")
                mcqs = _generate_mcq_pool_ai_only(
                    groq_client=local_groq_client,
                    job_description=job_desc,
                    required_skills=assessment.required_skills,
                    pool_mcq_total=pool_mcq_total,
                    pool_easy=pool_easy,
                    pool_medium=pool_medium,
                    pool_hard=pool_hard,
                    blacklist_qs=blacklist_mcqs,
                    model=AI_MODEL,
                    cancel_token=None
                )
                if mcqs:
                    generated_data['mcqs'] = mcqs[:pool_mcq_total]

            # 3. GENERATE CODING POOL (Skeleton-Based: 100% Accuracy)
            if pool_coding_total > 0:
                logger.info(f"Pipeline[{batch_id}]: Step 2 — Generating {pool_coding_total} execution-verified coding challenges.")
                generated_data['coding_challenges'] = _generate_execution_verified_coding_pool(
                    groq_client=local_groq_client,
                    job_description=job_desc,
                    required_skills=assessment.required_skills,
                    difficulties=pool_coding_tasks,
                    total_required=pool_coding_total,
                    model=AI_MODEL,
                    cancel_token=None
                )
            else:
                generated_data['coding_challenges'] = []

            # 4. EXPERT REFINER GATE
            if generated_data.get('mcqs'):
                if len(generated_data['mcqs']) > 25:
                    logger.info(f"Pipeline[{batch_id}]: Expert Gate BYPASSED — Pool size ({len(generated_data['mcqs'])}) is large.")
                else:
                    logger.info(f"Pipeline[{batch_id}]: Expert Gate — Cleaning and Refining MCQ pool...")
                    mcq_refined_data = _expert_assessment_refiner(
                        groq_client=local_groq_client,
                        raw_content={"mcqs": generated_data['mcqs'], "coding_challenges": []},
                        cancel_token=None
                    )
                    generated_data['mcqs'] = mcq_refined_data.get('mcqs', [])

            # 5. INITIAL DIFFICULTY REBALANCING
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
            final_mcqs = len(generated_data.get('mcqs', []))
            final_coding = len(generated_data.get('coding_challenges', []))

            if final_mcqs >= pool_mcq_total and pool_mcq_total > 0 and (final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):
                logger.warning(f"Pipeline[{batch_id}]: MCQ difficulty skewed ({final_easy}/{final_medium}/{final_hard}). Rebalancing...")
                generated_data['mcqs'] = _rebalance_mcq_difficulties(
                    generated_data.get('mcqs', []),
                    easy_required=pool_easy,
                    medium_required=pool_medium,
                    hard_required=pool_hard,
                )
                final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
                final_mcqs = len(generated_data.get('mcqs', []))

            # 6. SELF-HEALING REPAIR GATE
            final_mcqs = len(generated_data.get('mcqs', []))
            final_coding = len(generated_data.get('coding_challenges', []))
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))

            if (final_mcqs < pool_mcq_total or final_coding < pool_coding_total or
                final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):
                logger.info(f"Pipeline[{batch_id}]: 🔧 SELF-HEALING REPAIR TRIGGERED")
                generated_data = _repair_pool_shortfall(
                    groq_client=local_groq_client,
                    job_description=job_desc,
                    required_skills=assessment.required_skills,
                    pool=generated_data,
                    pool_easy=pool_easy,
                    pool_medium=pool_medium,
                    pool_hard=pool_hard,
                    pool_coding_total=pool_coding_total,
                    coding_tasks=pool_coding_tasks,
                    model=AI_MODEL
                )
                final_mcqs = len(generated_data.get('mcqs', []))
                final_coding = len(generated_data.get('coding_challenges', []))
                final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
                logger.info(f"Pipeline[{batch_id}]: ✅ REPAIR COMPLETE — MCQs: {final_mcqs} ({final_easy}E/{final_medium}M/{final_hard}H), Coding: {final_coding}")

            # 7. FORCED REBALANCING GATE
            if final_mcqs >= pool_mcq_total:
                generated_data['mcqs'] = _rebalance_mcq_difficulties(
                    generated_data.get('mcqs', []),
                    easy_required=pool_easy,
                    medium_required=pool_medium,
                    hard_required=pool_hard
                )
                final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))

            # 8. FINAL MCQ VALIDATION PASS
            logger.info(f"Pipeline[{batch_id}]: 🔍 FINAL PASS — Validating all MCQs...")
            all_mcqs = generated_data.get('mcqs', [])
            valid_mcqs = []
            invalid_count = 0
            for mcq in all_mcqs:
                is_valid, error_msg = _validate_mcq_structure(mcq)
                if is_valid:
                    valid_mcqs.append(mcq)
                else:
                    invalid_count += 1
                    logger.warning(f"Pipeline[{batch_id}]: ⚠️ INVALID MCQ REMOVED: {error_msg}")
            generated_data['mcqs'] = valid_mcqs
            final_mcqs = len(valid_mcqs)
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(valid_mcqs)

            # Post-cleanup MCQ repair
            if invalid_count > 0 and final_mcqs < pool_mcq_total:
                logger.warning(f"Pipeline[{batch_id}]: MCQ shortfall after cleanup ({final_mcqs}/{pool_mcq_total}). Triggering repair...")
                try:
                    repair_generated = _repair_pool_shortfall(
                        groq_client=local_groq_client,
                        job_description=job_desc,
                        required_skills=assessment.required_skills,
                        pool=generated_data,
                        pool_easy=pool_easy,
                        pool_medium=pool_medium,
                        pool_hard=pool_hard,
                        pool_coding_total=pool_coding_total,
                        coding_tasks=pool_coding_tasks,
                        model=AI_MODEL
                    )
                    generated_data = repair_generated
                    all_mcqs_after_repair = generated_data.get('mcqs', [])
                    valid_mcqs_after_repair = [mcq for mcq in all_mcqs_after_repair if _validate_mcq_structure(mcq)[0]]
                    generated_data['mcqs'] = valid_mcqs_after_repair
                    final_mcqs = len(valid_mcqs_after_repair)
                    final_easy, final_medium, final_hard = _mcq_difficulty_counts(valid_mcqs_after_repair)
                    logger.info(f"Pipeline[{batch_id}]: ✅ MCQ repair completed. Now: {final_mcqs} valid")
                except Exception as repair_e:
                    logger.error(f"Pipeline[{batch_id}]: ❌ MCQ repair failed: {repair_e}")
                    raise

            # 9. FINAL CODING VALIDATION PASS
            logger.info(f"Pipeline[{batch_id}]: 🔍 FINAL PASS — Validating coding challenges...")
            all_coding = generated_data.get('coding_challenges', [])
            valid_coding = []
            removed_coding = 0
            MIN_TC = 4
            for challenge in all_coding:
                if len(challenge.get('test_cases', [])) >= MIN_TC:
                    valid_coding.append(challenge)
                else:
                    removed_coding += 1
                    logger.warning(f"Pipeline[{batch_id}]: ⚠️ CODING REMOVED: '{challenge.get('title', 'Unknown')}' — insufficient test cases")
            generated_data['coding_challenges'] = valid_coding
            final_coding = len(valid_coding)

            # Post-cleanup coding repair
            if removed_coding > 0 and final_coding < pool_coding_total:
                logger.warning(f"Pipeline[{batch_id}]: Coding shortfall after cleanup ({final_coding}/{pool_coding_total}). Triggering repair...")
                try:
                    repair_generated = _repair_pool_shortfall(
                        groq_client=local_groq_client,
                        job_description=job_desc,
                        required_skills=assessment.required_skills,
                        pool=generated_data,
                        pool_easy=pool_easy,
                        pool_medium=pool_medium,
                        pool_hard=pool_hard,
                        pool_coding_total=pool_coding_total,
                        coding_tasks=pool_coding_tasks,
                        model=AI_MODEL
                    )
                    generated_data = repair_generated
                    valid_coding_after_repair = [c for c in generated_data.get('coding_challenges', []) if len(c.get('test_cases', [])) >= MIN_TC]
                    generated_data['coding_challenges'] = valid_coding_after_repair
                    final_coding = len(valid_coding_after_repair)
                    logger.info(f"Pipeline[{batch_id}]: ✅ Coding repair completed. Now: {final_coding} valid")
                except Exception as repair_e:
                    logger.error(f"Pipeline[{batch_id}]: ❌ Coding repair failed: {repair_e}")
                    raise

            # 10. FINAL VALIDATION GATE
            if final_mcqs < mcq_count or final_coding < coding_count:
                logger.error(f"Pipeline[{batch_id}]: ❌ FINAL VALIDATION FAILED — MCQs: {final_mcqs}/{mcq_count}, Coding: {final_coding}/{coding_count}")
                raise Exception(
                    f"AI could not satisfy minimum required pool counts. "
                    f"Expected MCQs={mcq_count}, coding={coding_count}; got MCQs={final_mcqs}, coding={final_coding}."
                )

            if not generated_data:
                raise Exception("AI pool generation produced no valid content after all quality gates.")

            assessment.generated_content = generated_data
            assessment.status = 'SCHEDULED'
            assessment.save()

            mcq_count_gen = len(generated_data.get('mcqs', []))
            coding_count_gen = len(generated_data.get('coding_challenges', []))
            logger.info(
                f"Pipeline[{batch_id}]: Assessment pool READY. "
                f"Generated {mcq_count_gen} MCQs + {coding_count_gen} coding challenges. "
                f"Assessment id={assessment.id}, share_token={assessment.share_token}"
            )

            # Log pool generation event for each passed candidate
            for c in passed_candidates:
                log_automation_event(
                    c, 'AI_GENERATION', 'SUCCESS',
                    f"Shared assessment pool generated: {mcq_count_gen} MCQs + {coding_count_gen} coding challenges. "
                    f"Pool covers {num_passed} passed candidate(s) in this batch.",
                    details={
                        'assessment_id': assessment.id,
                        'batch_id': batch_id,
                        'num_passed': num_passed,
                        'mcq_generated': mcq_count_gen,
                        'coding_generated': coding_count_gen,
                    }
                )

        # ── 2. SEND INVITATION EMAILS ──
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')
        from django.utils import timezone as tz

        emails_sent = 0
        emails_failed = 0

        logger.info(f"Pipeline[{batch_id}]: Sending assessment invitation emails to {num_passed} candidate(s)...")

        for candidate in passed_candidates:
            try:
                link = (
                    f"{base_url}/take-ai-assessment/{assessment.share_token}"
                    f"?name={quote(candidate.full_name or '')}"
                    f"&email={quote(candidate.email or '')}"
                )

                from_str = "Immediately"
                if assessment.available_from:
                    local_from = (
                        tz.localtime(assessment.available_from)
                        if tz.is_aware(assessment.available_from)
                        else assessment.available_from
                    )
                    from_str = local_from.strftime('%B %d, %Y at %I:%M %p')

                until_str = "No fixed deadline"
                if assessment.available_until:
                    local_until = (
                        tz.localtime(assessment.available_until)
                        if tz.is_aware(assessment.available_until)
                        else assessment.available_until
                    )
                    until_str = local_until.strftime('%B %d, %Y at %I:%M %p')

                subject = f"Assessment Invitation — {assessment.required_skills}"
                plain_message = (
                    f"Dear {candidate.full_name},\n\n"
                    f"Congratulations! You have passed the resume screening for '{assessment.required_skills}'.\n\n"
                    f"Available From: {from_str}\n"
                    f"Available Until: {until_str}\n"
                    f"Duration: {assessment.duration_minutes} minutes\n\n"
                    f"Start your assessment here: {link}\n\n"
                    f"Best regards,\nVerifiHire Team"
                )
                html_message = f"""
                <div style="font-family: sans-serif; max-width: 600px; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                    <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">🎉 Assessment Invitation</h1>
                    </div>
                    <div style="padding: 32px; background-color: white;">
                        <p>Dear <strong>{candidate.full_name}</strong>,</p>
                        <p>Congratulations! You have <strong>passed the resume screening</strong> and are invited to attempt a technical assessment for <strong>{assessment.required_skills}</strong>.</p>
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px; border-left: 4px solid #4318FF;">
                            <p style="margin: 5px 0;"><strong>📅 Available From:</strong> {from_str}</p>
                            <p style="margin: 5px 0;"><strong>⌛ Available Until:</strong> {until_str}</p>
                            <p style="margin: 5px 0;"><strong>⏱️ Duration:</strong> {assessment.duration_minutes} minutes</p>
                        </div>
                        <div style="text-align: center; margin: 32px 0;">
                            <a href="{link}" style="background-color: #4318FF; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 16px;">
                                Start Assessment
                            </a>
                        </div>
                        <p style="font-size: 13px; color: #64748b; border-top: 1px solid #f1f5f9; padding-top: 16px;">
                            If the button doesn't work, copy this link: <a href="{link}" style="color: #4318FF;">{link}</a>
                        </p>
                    </div>
                </div>
                """

                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[candidate.email],
                    html_message=html_message,
                    fail_silently=False
                )
                emails_sent += 1
                logger.info(
                    f"Pipeline[{batch_id}]: ✅ Assessment invitation email sent to {candidate.full_name} <{candidate.email}>"
                )
                log_automation_event(
                    candidate, 'EMAIL_SENT', 'SUCCESS',
                    f"Assessment invitation email sent successfully to {candidate.email}.",
                    details={'assessment_id': assessment.id, 'link': link}
                )

                # Update InvitedCandidate list
                from ai_assessments.models import InvitedCandidate
                InvitedCandidate.objects.get_or_create(
                    assessment=assessment,
                    email=candidate.email,
                    defaults={'name': candidate.full_name or "Unknown"}
                )

            except Exception as mail_err:
                emails_failed += 1
                logger.error(
                    f"Pipeline[{batch_id}]: ❌ Failed to send assessment email to {candidate.email}: {mail_err}"
                )
                log_automation_event(
                    candidate, 'EMAIL_SENT', 'FAILURE',
                    f"Failed to send assessment invitation email: {str(mail_err)}",
                    details={'assessment_id': assessment.id, 'error': str(mail_err)}
                )

        logger.info(
            f"Pipeline[{batch_id}]: Email summary — "
            f"{emails_sent}/{num_passed} sent successfully, {emails_failed} failed."
        )

    except Exception as e:
        logger.error(f"Pipeline[{batch_id}]: CRITICAL batch assessment error: {str(e)}")
        logger.error(tb.format_exc())


def process_resume_passed(candidate_id):
    """
    Fallback for single/non-batch fully-automatic flows.
    """
    from groq import Groq
    from ai_assessments.ai_logic import (
        _call_groq_with_backoff, _repair_pool_shortfall, _normalize_generated_pool,
        _generate_mcq_pool_ai_only, _generate_execution_verified_coding_pool,
        _expert_assessment_refiner, _validate_mcq_structure,
        _mcq_difficulty_counts, _rebalance_mcq_difficulties, GroqKeyManager
    )
    from ai_candidates.utils import log_automation_event

    try:
        candidate = Candidate.objects.get(id=candidate_id)
        if candidate.status != 'Resume Passed':
            logger.info(f"Pipeline: Candidate {candidate_id} is not 'Resume Passed'. Skipping.")
            return

        # Skip if batch already has an assessment (handled by batch task)
        if candidate.batch_id and Assessment.objects.filter(batch_id=candidate.batch_id).exists():
            logger.info(f"Pipeline: Batch assessment already exists for candidate {candidate_id}. Skipping individual.")
            return

        logger.info(f"Pipeline: Individual assessment generation for {candidate.full_name} (id={candidate_id})")
        settings_data = candidate.automation_settings or {}
        same_questions = bool(settings_data.get('same_questions_for_all', False))

        from django.utils.dateparse import parse_datetime
        a_from_str = settings_data.get('assessment_available_from')
        a_until_str = settings_data.get('assessment_available_until')
        assessment_from = parse_datetime(a_from_str) if a_from_str else None
        assessment_until = parse_datetime(a_until_str) if a_until_str else None

        mcq_count = settings_data.get('mcq_count', 10)
        mcq_easy_per_candidate = mcq_count // 2
        mcq_medium_per_candidate = (mcq_count * 3) // 10
        mcq_hard_per_candidate = max(0, mcq_count - mcq_easy_per_candidate - mcq_medium_per_candidate)

        assessment = Assessment.objects.create(
            job_description=candidate.job_description or "Technical Role",
            required_skills=candidate.job_title or "Technical Assessment",
            mcq_count=mcq_count,
            coding_count=settings_data.get('coding_count', 1),
            duration_minutes=settings_data.get('duration', 60),
            difficulty_level=settings_data.get('difficulty', 'Medium'),
            pass_threshold=settings_data.get('pass_threshold', 60),
            status='GENERATING',
            available_from=assessment_from,
            available_until=assessment_until,
            company=candidate.company,
            user_profile=getattr(candidate, 'user_profile', None),
            created_by=getattr(candidate, 'user_profile', None),
            same_questions_for_all=same_questions,
            max_candidates_allowed=1,
            invited_count=1,
            num_applicants=1,
            mcq_easy=mcq_easy_per_candidate, 
            mcq_medium=mcq_medium_per_candidate, 
            mcq_hard=mcq_hard_per_candidate, 
            total_points=100,
            mcq_weight=int(settings_data.get('mcq_weight', 40)),
            creation_type='automatic'
        )

        # --- FULL MANUAL-GRADE GENERATION PIPELINE ---
        coding_count = settings_data.get('coding_count', 1)
        difficulty = settings_data.get('difficulty', 'Medium')
        pool_mcq_total = mcq_count
        pool_easy = mcq_easy_per_candidate
        pool_medium = mcq_medium_per_candidate
        pool_hard = mcq_hard_per_candidate
        pool_coding_total = coding_count
        coding_tasks_list = [difficulty] * coding_count

        local_api_key = GroqKeyManager.get_current_key()
        local_groq_client = Groq(api_key=local_api_key, timeout=60.0)
        generated_data = {"mcqs": [], "coding_challenges": []}
        AI_MODEL = "llama-3.1-8b-instant"

        # 1. BLACKLIST: Fetch last 20 assessments to avoid duplicate questions
        blacklist_mcqs = []
        blacklist_titles = []
        recent_assessments_bl = Assessment.objects.filter(company=candidate.company, is_deleted=False).order_by('-created_at')[:20]
        for old_asm in recent_assessments_bl:
            old_content = old_asm.generated_content or {}
            for q in old_content.get('mcqs', []):
                blacklist_mcqs.append(q.get('question', '')[:100])
            for challenge in old_content.get('coding_challenges', []):
                blacklist_titles.append(challenge.get('title'))

        # 2. GENERATE MCQ POOL (Dedicated AI Call)
        if pool_mcq_total > 0:
            logger.info(f"Pipeline[individual-{candidate_id}]: Step 1 — Generating MCQ pool of {pool_mcq_total} questions. Blacklist: {len(blacklist_mcqs)}")
            mcqs = _generate_mcq_pool_ai_only(
                groq_client=local_groq_client,
                job_description=assessment.job_description,
                required_skills=assessment.required_skills,
                pool_mcq_total=pool_mcq_total,
                pool_easy=pool_easy,
                pool_medium=pool_medium,
                pool_hard=pool_hard,
                blacklist_qs=blacklist_mcqs,
                model=AI_MODEL,
                cancel_token=None
            )
            if mcqs:
                generated_data['mcqs'] = mcqs[:pool_mcq_total]

        # 3. GENERATE CODING POOL (Skeleton-Based: 100% Accuracy)
        if pool_coding_total > 0:
            logger.info(f"Pipeline[individual-{candidate_id}]: Step 2 — Generating {pool_coding_total} execution-verified coding challenges.")
            generated_data['coding_challenges'] = _generate_execution_verified_coding_pool(
                groq_client=local_groq_client,
                job_description=assessment.job_description,
                required_skills=assessment.required_skills,
                difficulties=coding_tasks_list,
                total_required=pool_coding_total,
                model=AI_MODEL,
                cancel_token=None
            )
        else:
            generated_data['coding_challenges'] = []

        # 4. EXPERT REFINER GATE
        if generated_data.get('mcqs'):
            if len(generated_data['mcqs']) > 25:
                logger.info(f"Pipeline[individual-{candidate_id}]: Expert Gate BYPASSED — Pool size ({len(generated_data['mcqs'])}) is large.")
            else:
                logger.info(f"Pipeline[individual-{candidate_id}]: Expert Gate — Cleaning and Refining MCQ pool...")
                mcq_refined_data = _expert_assessment_refiner(
                    groq_client=local_groq_client,
                    raw_content={"mcqs": generated_data['mcqs'], "coding_challenges": []},
                    cancel_token=None
                )
                generated_data['mcqs'] = mcq_refined_data.get('mcqs', [])

        # 5. INITIAL DIFFICULTY REBALANCING
        final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
        final_mcqs = len(generated_data.get('mcqs', []))
        final_coding = len(generated_data.get('coding_challenges', []))

        if final_mcqs >= pool_mcq_total and pool_mcq_total > 0 and (final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):
            logger.warning(f"Pipeline[individual-{candidate_id}]: MCQ difficulty skewed. Rebalancing...")
            generated_data['mcqs'] = _rebalance_mcq_difficulties(
                generated_data.get('mcqs', []),
                easy_required=pool_easy,
                medium_required=pool_medium,
                hard_required=pool_hard,
            )
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
            final_mcqs = len(generated_data.get('mcqs', []))

        # 6. SELF-HEALING REPAIR GATE
        final_mcqs = len(generated_data.get('mcqs', []))
        final_coding = len(generated_data.get('coding_challenges', []))
        final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))

        if (final_mcqs < pool_mcq_total or final_coding < pool_coding_total or
            final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):
            logger.info(f"Pipeline[individual-{candidate_id}]: 🔧 SELF-HEALING REPAIR TRIGGERED")
            generated_data = _repair_pool_shortfall(
                groq_client=local_groq_client,
                job_description=assessment.job_description,
                required_skills=assessment.required_skills,
                pool=generated_data,
                pool_easy=pool_easy,
                pool_medium=pool_medium,
                pool_hard=pool_hard,
                pool_coding_total=pool_coding_total,
                coding_tasks=coding_tasks_list,
                model=AI_MODEL
            )
            final_mcqs = len(generated_data.get('mcqs', []))
            final_coding = len(generated_data.get('coding_challenges', []))
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
            logger.info(f"Pipeline[individual-{candidate_id}]: ✅ REPAIR COMPLETE — MCQs: {final_mcqs}, Coding: {final_coding}")

        # 7. FORCED REBALANCING GATE
        if final_mcqs >= pool_mcq_total:
            generated_data['mcqs'] = _rebalance_mcq_difficulties(
                generated_data.get('mcqs', []),
                easy_required=pool_easy,
                medium_required=pool_medium,
                hard_required=pool_hard
            )
            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))

        # 8. FINAL MCQ VALIDATION PASS
        logger.info(f"Pipeline[individual-{candidate_id}]: 🔍 FINAL PASS — Validating all MCQs...")
        all_mcqs = generated_data.get('mcqs', [])
        valid_mcqs = []
        invalid_count = 0
        for mcq in all_mcqs:
            is_valid, error_msg = _validate_mcq_structure(mcq)
            if is_valid:
                valid_mcqs.append(mcq)
            else:
                invalid_count += 1
                logger.warning(f"Pipeline[individual-{candidate_id}]: ⚠️ INVALID MCQ REMOVED: {error_msg}")
        generated_data['mcqs'] = valid_mcqs
        final_mcqs = len(valid_mcqs)
        final_easy, final_medium, final_hard = _mcq_difficulty_counts(valid_mcqs)

        # Post-cleanup MCQ repair
        if invalid_count > 0 and final_mcqs < pool_mcq_total:
            logger.warning(f"Pipeline[individual-{candidate_id}]: MCQ shortfall after cleanup. Triggering repair...")
            try:
                repair_generated = _repair_pool_shortfall(
                    groq_client=local_groq_client,
                    job_description=assessment.job_description,
                    required_skills=assessment.required_skills,
                    pool=generated_data,
                    pool_easy=pool_easy,
                    pool_medium=pool_medium,
                    pool_hard=pool_hard,
                    pool_coding_total=pool_coding_total,
                    coding_tasks=coding_tasks_list,
                    model=AI_MODEL
                )
                generated_data = repair_generated
                all_mcqs_after_repair = generated_data.get('mcqs', [])
                valid_mcqs_after_repair = [mcq for mcq in all_mcqs_after_repair if _validate_mcq_structure(mcq)[0]]
                generated_data['mcqs'] = valid_mcqs_after_repair
                final_mcqs = len(valid_mcqs_after_repair)
                final_easy, final_medium, final_hard = _mcq_difficulty_counts(valid_mcqs_after_repair)
                logger.info(f"Pipeline[individual-{candidate_id}]: ✅ MCQ repair completed. Now: {final_mcqs} valid")
            except Exception as repair_e:
                logger.error(f"Pipeline[individual-{candidate_id}]: ❌ MCQ repair failed: {repair_e}")
                raise

        # 9. FINAL CODING VALIDATION PASS
        logger.info(f"Pipeline[individual-{candidate_id}]: 🔍 FINAL PASS — Validating coding challenges...")
        all_coding = generated_data.get('coding_challenges', [])
        valid_coding = []
        removed_coding = 0
        MIN_TC = 4
        for challenge in all_coding:
            if len(challenge.get('test_cases', [])) >= MIN_TC:
                valid_coding.append(challenge)
            else:
                removed_coding += 1
                logger.warning(f"Pipeline[individual-{candidate_id}]: ⚠️ CODING REMOVED: '{challenge.get('title', 'Unknown')}'")
        generated_data['coding_challenges'] = valid_coding
        final_coding = len(valid_coding)

        # Post-cleanup coding repair
        if removed_coding > 0 and final_coding < pool_coding_total:
            logger.warning(f"Pipeline[individual-{candidate_id}]: Coding shortfall after cleanup. Triggering repair...")
            try:
                repair_generated = _repair_pool_shortfall(
                    groq_client=local_groq_client,
                    job_description=assessment.job_description,
                    required_skills=assessment.required_skills,
                    pool=generated_data,
                    pool_easy=pool_easy,
                    pool_medium=pool_medium,
                    pool_hard=pool_hard,
                    pool_coding_total=pool_coding_total,
                    coding_tasks=coding_tasks_list,
                    model=AI_MODEL
                )
                generated_data = repair_generated
                valid_coding_after_repair = [c for c in generated_data.get('coding_challenges', []) if len(c.get('test_cases', [])) >= MIN_TC]
                generated_data['coding_challenges'] = valid_coding_after_repair
                final_coding = len(valid_coding_after_repair)
                logger.info(f"Pipeline[individual-{candidate_id}]: ✅ Coding repair completed. Now: {final_coding} valid")
            except Exception as repair_e:
                logger.error(f"Pipeline[individual-{candidate_id}]: ❌ Coding repair failed: {repair_e}")
                raise

        # 10. FINAL VALIDATION GATE
        if final_mcqs < mcq_count or final_coding < coding_count:
            logger.warning(
                f"Pipeline[individual-{candidate_id}]: ⚠️ FINAL GATE WARNING — "
                f"AI could not satisfy minimum required pool counts exactly. "
                f"Expected MCQs={mcq_count}, coding={coding_count}; "
                f"Got MCQs={final_mcqs}, coding={final_coding}. "
                "Proceeding with best-effort pool."
            )
            # We enforce a MINIMUM requirement only: at least 1 MCQ or 1 coding challenge
            if final_mcqs == 0 and final_coding == 0:
                raise Exception("CRITICAL: AI failed to generate ANY valid questions (MCQs=0, Coding=0). Aborting assessment.")


        if not generated_data:
            raise Exception("AI pool generation produced no valid content after all quality gates.")

        assessment.generated_content = generated_data
        assessment.status = 'SCHEDULED'
        assessment.save()

        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')
        link = (
            f"{base_url}/take-ai-assessment/{assessment.share_token}"
            f"?name={quote(candidate.full_name or '')}"
            f"&email={quote(candidate.email or '')}"
        )

        html_message = f"""
        <div style="font-family: sans-serif; max-width: 600px; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
            <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">🎉 Assessment Invitation</h1>
            </div>
            <div style="padding: 32px; background-color: white;">
                <p>Dear <strong>{candidate.full_name}</strong>,</p>
                <p>You have passed the resume screening. Please complete your technical assessment.</p>
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{link}" style="background-color: #4318FF; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">Start Assessment</a>
                </div>
                <p style="font-size: 13px; color: #64748b;">Link: <a href="{link}">{link}</a></p>
            </div>
        </div>
        """

        send_mail(
            subject=f"Assessment Invitation — {assessment.required_skills}",
            message=f"Dear {candidate.full_name}, please start your assessment: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate.email],
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f"Pipeline: Individual assessment invitation sent to {candidate.email}")
        log_automation_event(
            candidate, 'EMAIL_SENT', 'SUCCESS',
            f"Individual assessment invitation email sent to {candidate.email}.",
            details={'assessment_id': assessment.id, 'link': link}
        )

        # Update InvitedCandidate list
        from ai_assessments.models import InvitedCandidate
        InvitedCandidate.objects.get_or_create(
            assessment=assessment,
            email=candidate.email,
            defaults={'name': candidate.full_name or "Unknown"}
        )

    except Exception as e:
        logger.error(f"Pipeline Individual Error for candidate {candidate_id}: {e}")
        logger.error(tb.format_exc())


def process_assessment_passed(submission_id):
    """
    Pipeline triggered when a candidate clears an AI assessment.
    Sends an HTML interview invitation email and logs the event.
    """
    from ai_candidates.utils import log_automation_event

    try:
        submission = AIAssessmentSubmission.objects.select_related('assessment').get(id=submission_id)
        if submission.status != 'selected':
            logger.info(f"Pipeline: Submission {submission_id} status is '{submission.status}', not 'selected'. Skipping.")
            return

        logger.info(
            f"Pipeline: Assessment PASSED — generating interview invite for "
            f"{submission.candidate_name} <{submission.candidate_email}> "
            f"(submission id={submission_id}, score={submission.percentage}%)"
        )

        # Find or create the candidate record
        candidates = Candidate.objects.filter(
            email=submission.candidate_email,
            company=submission.assessment.company
        ).order_by('-id')

        if candidates.exists():
            candidate = candidates.first()
            candidate.status = 'Interview'
            # Synchronize batch info from submission to candidate if it doesn't exist
            if not candidate.batch_id:
                candidate.batch_id = submission.batch_id
            if not candidate.batch_name:
                candidate.batch_name = submission.batch_name
            candidate.save(update_fields=['status', 'batch_id', 'batch_name'])
            logger.info(f"Pipeline: Updated existing candidate {candidate.id} status to 'Interview'.")
        else:
            candidate = Candidate.objects.create(
                full_name=submission.candidate_name,
                email=submission.candidate_email,
                job_title=submission.assessment.required_skills or "Applicant",
                job_description=submission.assessment.job_description,
                status='Interview',
                batch_id=submission.batch_id,
                batch_name=submission.batch_name,
                company=submission.assessment.company,
                user_profile=getattr(submission.assessment, 'user_profile', None),
                created_by=getattr(submission.assessment, 'user_profile', None),
            )
            logger.info(f"Pipeline: Created new candidate record {candidate.id} for interview stage and linked to batch {submission.batch_id}.")

        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')
        link = f"{base_url}/interview-start/{candidate.public_token}"

        role_name = submission.assessment.required_skills or "the role"
        subject = f"Congratulations! You're invited for an Interview — {role_name}"
        plain_message = (
            f"Dear {candidate.full_name},\n\n"
            f"Congratulations! You have successfully passed the assessment for '{role_name}' "
            f"with a score of {submission.percentage}%.\n\n"
            f"You are now invited to the next stage — the AI Video Interview.\n\n"
            f"Start your interview here: {link}\n\n"
            f"Best regards,\nVerifiHire Team"
        )
        html_message = f"""
        <div style="font-family: sans-serif; max-width: 600px; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
            <div style="background-color: #059669; padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">🏆 Interview Invitation</h1>
            </div>
            <div style="padding: 32px; background-color: white;">
                <p>Dear <strong>{candidate.full_name}</strong>,</p>
                <p>Congratulations! You have <strong>passed the assessment</strong> for <strong>{role_name}</strong>
                   with a score of <strong>{submission.percentage}%</strong>.</p>
                <p>You are now invited to the next stage — the <strong>AI Video Interview</strong>.</p>
                <div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; margin: 24px 0; border-left: 4px solid #059669;">
                    <p style="margin: 5px 0;"><strong>📋 Role:</strong> {role_name}</p>
                    <p style="margin: 5px 0;"><strong>✅ Assessment Score:</strong> {submission.percentage}%</p>
                </div>
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{link}" style="background-color: #059669; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 16px;">
                        Start Interview
                    </a>
                </div>
                <p style="font-size: 13px; color: #64748b; border-top: 1px solid #f1f5f9; padding-top: 16px;">
                    If the button doesn't work, copy this link: <a href="{link}" style="color: #059669;">{link}</a>
                </p>
                <p style="font-size: 13px; color: #64748b;">Best regards,<br/><strong>The VerifiHire Team</strong></p>
            </div>
        </div>
        """

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate.email],
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f"Pipeline: ✅ Interview invitation email sent to {candidate.email}")
        log_automation_event(
            candidate, 'EMAIL_SENT', 'SUCCESS',
            f"Interview invitation email sent after passing assessment with {submission.percentage}%.",
            details={'submission_id': submission_id, 'score': submission.percentage, 'link': link}
        )

    except Exception as e:
        logger.error(f"Pipeline Error (assessment passed → interview invite) for submission {submission_id}: {e}")
        logger.error(tb.format_exc())
