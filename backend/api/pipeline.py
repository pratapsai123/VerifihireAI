import logging
import traceback as tb
import json
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
    """
    from ai_assessments.ai_logic import _call_groq_with_backoff, _repair_pool_shortfall, _normalize_generated_pool
    from ai_candidates.utils import log_automation_event

    try:
        passed_candidates = Candidate.objects.filter(batch_id=batch_id, status='Resume Passed')
        num_passed = passed_candidates.count()
        if num_passed == 0:
            logger.info(f"Pipeline: No candidates passed in batch {batch_id}. Skipping assessment generation.")
            return

        # Use the first candidate as a template for automation settings 
        trigger_candidate = passed_candidates.first()
        settings_data = trigger_candidate.automation_settings or {}
        
        # 1. DEDUPLICATION: Check if an assessment already exists
        assessment = Assessment.objects.filter(batch_id=batch_id).first()
        if assessment:
            logger.info(f"Pipeline: Assessment already exists for batch {batch_id}. Skipping generation.")
        else:
            logger.info(f"Pipeline: Generating shared Assessment for {num_passed} passed candidates in batch {batch_id}")
            
            job_desc = trigger_candidate.job_description or "General Software Engineering Role"
            difficulty = settings_data.get('difficulty', 'Medium')
            duration = settings_data.get('duration', 60)
            mcq_count = settings_data.get('mcq_count', 10)
            coding_count = settings_data.get('coding_count', 1)
            pass_threshold = settings_data.get('pass_threshold', 60)
            same_questions = bool(settings_data.get('same_questions_for_all', False))
            
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone
            
            a_from_str = settings_data.get('assessment_available_from')
            a_until_str = settings_data.get('assessment_available_until')
            assessment_from = parse_datetime(a_from_str) if a_from_str else None
            assessment_until = parse_datetime(a_until_str) if a_until_str else None
            
            # Create Assessment Record with all required fields explicitly set to satisfy DB constraints
            assessment = Assessment.objects.create(
                job_description=job_desc,
                required_skills=trigger_candidate.job_title or "Technical Assessment",
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
                user_profile=getattr(trigger_candidate, 'user_profile', None),
                created_by=getattr(trigger_candidate, 'user_profile', None),
                company=getattr(trigger_candidate, 'company', None),
                mcq_easy=5,
                mcq_medium=3,
                mcq_hard=2,
                total_points=100
            )

            # --- Pool multipliers ---
            multiplier = num_passed if (num_passed > 1 and not same_questions) else 1
            pool_mcq_total = mcq_count * multiplier
            pool_coding_total = coding_count * multiplier if coding_count <= 10 else coding_count
            
            pool_easy = int(pool_mcq_total * 0.5)
            pool_medium = int(pool_mcq_total * 0.3)
            pool_hard = max(0, pool_mcq_total - pool_easy - pool_medium)
            
            mcq_prompt = f"TASK 1: Generate a POOL of {pool_mcq_total} MCQs.\n- {pool_easy} Easy, {pool_medium} Medium, {pool_hard} Hard.\n"
            mcq_prompt += "Each MCQ must have: 'question', 'options' (list of 4), 'answer', and 'difficulty'."
            keys_expected = '"mcqs"'
            coding_prompt = ""
            if coding_count > 0:
                coding_prompt = f"TASK 2: Generate a POOL of {pool_coding_total} Coding Challenges.\nCRITICAL: 'starter_code' MUST be a JSON mapping keys 'python' and 'javascript' ONLY.\n"
                keys_expected = '"mcqs", "coding_challenges"'

            main_prompt = f"Create assessment for: {job_desc}\n{mcq_prompt}\n{coding_prompt}\nReturn JSON with keys: {keys_expected}."
            raw_result = _call_groq_with_backoff(prompt=main_prompt, system_msg="Return valid JSON schema.", is_json=True)
            
            if not raw_result: raise Exception("AI generation failed.")
            generated_data = _normalize_generated_pool(raw_result)
            
            generated_data = _repair_pool_shortfall(
                groq_client=None, job_description=job_desc, required_skills=assessment.required_skills,
                pool=generated_data, pool_easy=pool_easy, pool_medium=pool_medium, pool_hard=pool_hard,
                pool_coding_total=pool_coding_total, coding_tasks=['Medium'] * pool_coding_total
            )

            if generated_data:
                assessment.generated_content = generated_data
                assessment.status = 'SCHEDULED'
                assessment.save()
            else:
                raise Exception("Could not generate valid pool.")

        # ── 2. LOOP AND SEND EMAILS ──
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'https://verifihireai.com')
        from django.utils import timezone

        for candidate in passed_candidates:
            link = f"{base_url}/take-ai-assessment/{assessment.share_token}?name={quote(candidate.full_name)}&email={quote(candidate.email)}"
            
            from_str = "Immediately"
            if assessment.available_from:
                local_from = timezone.localtime(assessment.available_from) if timezone.is_aware(assessment.available_from) else assessment.available_from
                from_str = local_from.strftime('%B %d, %Y at %I:%M %p')
            until_str = "No fixed deadline"
            if assessment.available_until:
                local_until = timezone.localtime(assessment.available_until) if timezone.is_aware(assessment.available_until) else assessment.available_until
                until_str = local_until.strftime('%B %d, %Y at %I:%M %p')

            html_message = f"""
            <div style="font-family: sans-serif; max-width: 600px; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                <div style="background-color: #4318FF; padding: 24px; text-align: center;"><h1 style="color: white; margin: 0; font-size: 24px;">Assessment Invitation</h1></div>
                <div style="padding: 32px; background-color: white;">
                    <p>Dear <strong>{candidate.full_name}</strong>,</p>
                    <p>Congratulations! You have passed the resume screening. You are invited to attempt a technical assessment for <strong>{assessment.required_skills}</strong>.</p>
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                        <p><strong>📅 Available From:</strong> {from_str}</p>
                        <p><strong>⌛ Available Until:</strong> {until_str}</p>
                        <p><strong>⏱️ Duration:</strong> {assessment.duration_minutes} minutes</p>
                    </div>
                    <div style="text-align: center;"><a href="{link}" style="background-color: #4318FF; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">Start Assessment</a></div>
                </div>
            </div>
            """
            send_mail(f"Assessment Invitation: {candidate.full_name}", "", settings.DEFAULT_FROM_EMAIL, [candidate.email], html_message=html_message)
            log_automation_event(candidate, 'AI_GENERATION', 'SUCCESS', "Automated assessment invitation sent.")

    except Exception as e:
        logger.error(f"Pipeline Batch Error: {str(e)}")
        logger.error(tb.format_exc())

def process_resume_passed(candidate_id):
    """
    Fallback for single/manual resume screening triggers or non-batch flows.
    """
    from ai_assessments.ai_logic import _call_groq_with_backoff, _repair_pool_shortfall, _normalize_generated_pool
    from ai_candidates.utils import log_automation_event

    try:
        candidate = Candidate.objects.get(id=candidate_id)
        if candidate.status != 'Resume Passed': return
        
        if candidate.batch_id and Assessment.objects.filter(batch_id=candidate.batch_id).exists():
            return

        logger.info(f"Pipeline: Individual Assessment for {candidate.full_name}")
        settings_data = candidate.automation_settings or {}
        same_questions = bool(settings_data.get('same_questions_for_all', False))
        
        from django.utils.dateparse import parse_datetime
        a_from_str = settings_data.get('assessment_available_from')
        a_until_str = settings_data.get('assessment_available_until')
        assessment_from = parse_datetime(a_from_str) if a_from_str else None
        assessment_until = parse_datetime(a_until_str) if a_until_str else None

        # Robust creation for individual case
        assessment = Assessment.objects.create(
            job_description=candidate.job_description or "Technical Role",
            required_skills=candidate.job_title or "Technical Assessment",
            mcq_count=settings_data.get('mcq_count', 10),
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
            mcq_easy=5, mcq_medium=3, mcq_hard=2, total_points=100
        )
        
        raw_result = _call_groq_with_backoff(prompt=f"Generate {assessment.mcq_count} MCQs for {assessment.job_description}", is_json=True)
        if raw_result:
            assessment.generated_content = _normalize_generated_pool(raw_result)
            assessment.status = 'SCHEDULED'
            assessment.save()
            
            base_url = getattr(settings, 'FRONTEND_BASE_URL', 'https://verifihireai.com')
            link = f"{base_url}/take-ai-assessment/{assessment.share_token}?name={quote(candidate.full_name)}&email={quote(candidate.email)}"
            html_message = f"<div>Invite for {candidate.full_name}. <a href='{link}'>Link</a></div>"
            send_mail("Assessment Invitation", "", settings.DEFAULT_FROM_EMAIL, [candidate.email], html_message=html_message)
            log_automation_event(candidate, 'AI_GENERATION', 'SUCCESS', "Individual assessment sent.")

    except Exception as e:
        logger.error(f"Pipeline Individual Error: {e}")

def process_assessment_passed(submission_id):
    """
    Pipeline triggered when a candidate clears an AI assessment.
    """
    try:
        submission = AIAssessmentSubmission.objects.get(id=submission_id)
        if submission.status != 'selected': return
        logger.info(f"Pipeline: Generating Interview Invite for {submission.candidate_name}")
        
        candidates = Candidate.objects.filter(email=submission.candidate_email).order_by('-id')
        if not candidates.exists():
            candidate = Candidate.objects.create(
                full_name=submission.candidate_name, email=submission.candidate_email,
                job_title=submission.assessment.required_skills or "Applicant",
                job_description=submission.assessment.job_description, status='Interview',
                company=submission.assessment.company, user_profile=getattr(submission.assessment, 'user_profile', None)
            )
        else:
            candidate = candidates.first(); candidate.status = 'Interview'; candidate.save()
        
        link = f"{getattr(settings, 'FRONTEND_BASE_URL', 'https://verifihireai.com')}/interview-start/{candidate.id}"
        send_mail("Interview Invitation", f"Clear link: {link}", settings.DEFAULT_FROM_EMAIL, [candidate.email])
        logger.info(f"Pipeline: Interview email sent to {candidate.email}")
    except Exception as e:
        logger.error(f"Pipeline Error (Assessment): {e}")
