import logging
import traceback as tb
from django.conf import settings
from django.core.mail import send_mail
from groq import Groq
from ai_candidates.models import Candidate 
from ai_assessments.models import Assessment, AIAssessmentSubmission
from ai_candidates.views import extract_json

logger = logging.getLogger(__name__)

# groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
# if groq_api_key:
#     groq_client = Groq(api_key=groq_api_key)

def process_resume_passed(candidate_id):
    from ai_assessments.ai_logic import _call_groq_with_backoff, _repair_pool_shortfall, _normalize_generated_pool, _mcq_difficulty_counts, _generate_coding_pool_ai_only
    from ai_candidates.utils import log_automation_event

    try:
        candidate = Candidate.objects.get(id=candidate_id)
        if candidate.status != 'Resume Passed':
            return
            
        logger.info(f"Pipeline: Generating Assessment for {candidate.full_name}")
        log_automation_event(
            candidate, 
            'AI_GENERATION', 
            'INFO', 
            "Starting AI-powered technical assessment generation."
        )
        
        job_desc = candidate.job_description or "General Software Engineering Role"
        settings_data = candidate.automation_settings or {}
        
        difficulty = settings_data.get('difficulty', 'Medium')
        duration = settings_data.get('duration', 60)
        mcq_count = settings_data.get('mcq_count', 10)
        coding_count = settings_data.get('coding_count', 1)
        pass_threshold = settings_data.get('pass_threshold', 60)
        
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        
        a_from_str = settings_data.get('assessment_available_from')
        a_until_str = settings_data.get('assessment_available_until')
        assessment_from = parse_datetime(a_from_str) if a_from_str else None
        assessment_until = parse_datetime(a_until_str) if a_until_str else None
        
        # Generate Assessment Database Record
        assessment = Assessment()
        assessment.job_description = job_desc
        assessment.required_skills = candidate.job_title or "Technical Assessment"
        assessment.mcq_count = mcq_count
        assessment.coding_count = coding_count
        assessment.duration_minutes = duration
        assessment.difficulty_level = difficulty
        assessment.pass_threshold = pass_threshold
        assessment.status = 'GENERATING'
        assessment.available_from = assessment_from
        assessment.available_until = assessment_until
        
        user_prof = getattr(candidate, 'user_profile', None)
        assessment.user_profile = user_prof
        assessment.created_by = user_prof
        assessment.company = getattr(candidate, 'company', None)
        
        assessment.coding_difficulty_list = []
        assessment.mcq_easy = 5
        assessment.mcq_medium = 3
        assessment.mcq_hard = 2
        assessment.total_points = 100
        assessment.save()

        # Pool multipliers
        pool_mcq_total = mcq_count * 2
        pool_coding_total = coding_count * 2 if coding_count <= 10 else coding_count
        
        pool_easy = int(pool_mcq_total * 0.5)
        pool_medium = int(pool_mcq_total * 0.3)
        pool_hard = max(0, pool_mcq_total - pool_easy - pool_medium)
        
        mcq_prompt = f"TASK 1: Generate a POOL of {pool_mcq_total} MCQs.\n"
        mcq_prompt += f"- {pool_easy} Easy, {pool_medium} Medium, {pool_hard} Hard.\n"
        mcq_prompt += "Each MCQ must have: 'question', 'options' (list of 4), 'answer', and 'difficulty'."

        coding_prompt = ""
        keys_expected = '"mcqs"'
        if coding_count > 0:
            coding_prompt = f"TASK 2: Generate a POOL of {pool_coding_total} Coding Challenges.\n"
            coding_prompt += (
                "Each challenge must have: 'title', 'problem_statement', 'input_format', 'output_format', "
                "'constraints', 'example_input', 'example_output', 'explanation', 'starter_code', 'difficulty', and 'test_cases'.\n"
            )
            # SIMPLIFIED: Only request Python and Javascript for reliability, can expand locally if needed
            coding_prompt += "CRITICAL: 'starter_code' MUST be a JSON mapping keys 'python' and 'javascript' ONLY.\n"
            coding_prompt += "CRITICAL: Generate EXACTLY 5 test_cases for each challenge.\n"
            keys_expected = '"mcqs", "coding_challenges"'

        main_prompt = f"""
        Act as an expert technical recruiter. Create an assessment for: {job_desc}
        
        {mcq_prompt}
        
        {coding_prompt}
        
        Return a single JSON object with keys: {keys_expected}. Output valid JSON only.
        """
        
        # Use robust caller with backoff and key rotation
        system_msg = "You are a detailed assessment generator. Always return valid JSON matching the schema."
        raw_result = _call_groq_with_backoff(prompt=main_prompt, system_msg=system_msg, is_json=True)
        
        if not raw_result:
            raise Exception("AI failed to provide a valid response after multiple retries.")

        generated_data = _normalize_generated_pool(raw_result)
        
        # Repair if needed
        generated_data = _repair_pool_shortfall(
            groq_client=None, # _repair_pool_shortfall will use its own internal caller logic if we adapt it or pass None
            job_description=job_desc,
            required_skills="Technical Assessment",
            pool=generated_data,
            pool_easy=pool_easy,
            pool_medium=pool_medium,
            pool_hard=pool_hard,
            pool_coding_total=pool_coding_total,
            coding_tasks=['Medium'] * pool_coding_total,
            max_attempts=2,
        )

        if generated_data:
            assessment.generated_content = generated_data
            assessment.status = 'SCHEDULED'
            assessment.save()
            log_automation_event(
                candidate, 
                'AI_GENERATION', 
                'SUCCESS', 
                f"Assessment generated successfully ({len(generated_data.get('mcqs', []))} MCQs, {len(generated_data.get('coding_challenges', []))} Coding challenges)."
            )
        else:
            raise Exception("Critical failure: Could not generate valid assessment structure.")
                
        # Send Email
        from urllib.parse import quote
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        link = f"{base_url}/take-ai-assessment/{assessment.share_token}?name={quote(candidate.full_name)}&email={quote(candidate.email)}"
        
        subject = f"Next Steps: Technical Assessment for {candidate.full_name}"
        
        from_str = "Immediately"
        if assessment_from:
            local_from = timezone.localtime(assessment_from) if timezone.is_aware(assessment_from) else assessment_from
            from_str = local_from.strftime('%B %d, %Y at %I:%M %p')
            
        until_str = "No fixed deadline"
        if assessment_until:
            local_until = timezone.localtime(assessment_until) if timezone.is_aware(assessment_until) else assessment_until
            until_str = local_until.strftime('%B %d, %Y at %I:%M %p')
            
        message = f"Dear {candidate.full_name},\n\nYou have been invited to attempt an AI technical assessment for the role of {job_desc}.\n\nTiming Details:\n- Available From: {from_str}\n- Available Until: {until_str}\n- Duration: {duration} minutes\n\nPlease click the link below to start your assessment during the availability window:\n{link}\n\nBest of luck!"
        
        html_message = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
            <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">Assessment Invitation</h1>
            </div>
            <div style="padding: 32px; background-color: white;">
                <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{candidate.full_name}</strong>,</p>
                <p style="line-height: 1.6; margin-bottom: 24px;">You have been invited to attempt an AI technical assessment for the role: <br/><strong>{job_desc}</strong></p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                    <h3 style="margin-top: 0; color: #4318FF; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>
                    <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {from_str}</p>
                    <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {until_str}</p>
                    <p style="margin: 8px 0; font-size: 14px;"><strong>⏱️ Duration:</strong> {duration} minutes</p>
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
        
        # 5. Send Email Notification
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@verifihire.com')
        # Use simple try-catch for mail to avoid crashing pipeline if SMTP isn't setup
        try:
            send_mail(subject, message, from_email, [candidate.email], fail_silently=False, html_message=html_message)
            print(f"PIPELINE SUCCESS: Assessment email sent to {candidate.email}")
            logger.info(f"Pipeline: Assessment email sent to {candidate.email}")
            log_automation_event(
                candidate, 
                'EMAIL_SENT', 
                'SUCCESS', 
                f"Assessment invitation email sent to {candidate.email}."
            )
        except Exception as e:
            print(f"PIPELINE EMAIL FAILED: {e}")
            logger.error(f"Pipeline: Failed to send assessment email to {candidate.email}: {str(e)}")
            log_automation_event(
                candidate, 
                'EMAIL_SENT', 
                'FAILURE', 
                f"Failed to send invitation email: {str(e)}"
            )
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Pipeline Error (Resume): {error_msg}")
        # Log to the new timeline
        try:
            candidate = Candidate.objects.get(id=candidate_id)
            log_automation_event(candidate, 'ERROR', 'FAILURE', f"Pipeline generation failed: {error_msg}")
        except:
            pass
        
        print(f"PIPELINE ERROR (Resume): {e}")
        print(tb.format_exc())


def process_assessment_passed(submission_id):
    try:
        submission = AIAssessmentSubmission.objects.get(id=submission_id)
        if submission.status != 'selected':
            return
            
        logger.info(f"Pipeline: Generating Interview Invite for {submission.candidate_name}")
        
        # Link back to the Candidate model based on email.
        # If the candidate used a public assessment link, they won't have a Candidate record yet.
        candidates = Candidate.objects.filter(email=submission.candidate_email).order_by('-id')
        if not candidates.exists():
            logger.info(f"Pipeline: Candidate not found for email {submission.candidate_email}. Creating new Candidate record.")
            candidate = Candidate.objects.create(
                full_name=submission.candidate_name,
                email=submission.candidate_email,
                job_title=submission.assessment.required_skills or "Applicant",
                job_description=submission.assessment.job_description,
                status='Interview',
                company=submission.assessment.company,
                user_profile=getattr(submission.assessment, 'user_profile', None)
            )
        else:
            candidate = candidates.first()
            candidate.status = 'Interview'
            candidate.save()
        
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        link = f"{base_url}/interview-start/{candidate.id}"
        
        subject = f"Final Step: AI Video Interview Invitation"
        
        from django.utils import timezone
        
        # Format availability dates for email (converted to local time)
        from_str = "Immediately"
        if candidate.available_from:
            local_from = timezone.localtime(candidate.available_from)
            from_str = local_from.strftime('%B %d, %Y at %I:%M %p')
            
        until_str = "No fixed deadline"
        if candidate.available_until:
            local_until = timezone.localtime(candidate.available_until)
            until_str = local_until.strftime('%B %d, %Y at %I:%M %p')
        
        message = f"Dear {candidate.full_name},\n\nYou have been invited to complete an AI-powered video interview.\n\nTiming Details:\n- Available From: {from_str}\n- Available Until: {until_str}\n\nPlease click the link below to verify your details and start your session:\n{link}"
        
        html_message = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
            <div style="background-color: #6366F1; padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">Interview Invitation</h1>
            </div>
            <div style="padding: 32px; background-color: white;">
                <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{candidate.full_name}</strong>,</p>
                <p style="line-height: 1.6; margin-bottom: 24px;">You have successfully passed the technical assessment portion. You have been invited to attempt an AI-powered video interview session.</p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                    <h3 style="margin-top: 0; color: #6366F1; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>
                    <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {from_str}</p>
                    <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {until_str}</p>
                </div>
                
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{link}" style="background-color: #6366F1; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2);">Start Interview Session</a>
                </div>
                
                <p style="font-size: 13px; color: #64748b; margin-top: 32px; border-top: 1px solid #f1f5f9; padding-top: 16px;">If the button above doesn't work, copy and paste this link into your browser:<br/>
                <a href="{link}" style="color: #6366F1;">{link}</a></p>
            </div>
            <div style="background-color: #f1f5f9; padding: 16px; text-align: center; font-size: 12px; color: #94a3b8;">
                &copy; 2026 VerifiHireAI. All rights reserved.
            </div>
        </div>
        """
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@verifihire.com')
        try:
            send_mail(subject, message, from_email, [candidate.email], fail_silently=False, html_message=html_message)
            print(f"PIPELINE SUCCESS: Interview email sent to {candidate.email}")
            logger.info(f"Pipeline: Interview email sent to {candidate.email}")
        except Exception as e:
            print(f"PIPELINE EMAIL FAILED: {e}")
            logger.error(f"Pipeline: Failed to send interview email to {candidate.email}: {str(e)}")
            
    except Exception as e:
        print(f"PIPELINE ERROR (Assessment): {e}")
        print(tb.format_exc())
        logger.error(f"Pipeline Error (Assessment): {e}")
