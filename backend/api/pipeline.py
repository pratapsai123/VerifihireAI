import logging
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
    try:
        # Local Groq client for lazy loading
        local_groq_key = getattr(settings, 'GROQ_API_KEY', None)
        local_groq_client = Groq(api_key=local_groq_key) if local_groq_key else None
        candidate = Candidate.objects.get(id=candidate_id)
        if candidate.status != 'Resume Passed':
            return
            
        logger.info(f"Pipeline: Generating Assessment for {candidate.full_name}")
        
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
        assessment = Assessment.objects.create(
            job_description=job_desc,
            required_skills="Technical Assessment", 
            mcq_count=mcq_count,
            coding_count=coding_count,
            duration_minutes=duration,
            difficulty_level=difficulty,
            pass_threshold=pass_threshold,
            status='GENERATING',
            available_from=assessment_from,
            available_until=assessment_until
        )
        
        coding_prompt = ""
        keys_expected = '"mcqs"'
        if int(coding_count) > 0:
            coding_prompt = f"""
        TASK 2: Generate {coding_count} Coding Challenge(s).
        Challenge object must have: "title", "problem_statement", "input_format", "output_format", "constraints", "example_input", "example_output", "explanation", "starter_code_java", "starter_code_python", "test_cases" (list of 5 objects with "input" and "output").
        """
            keys_expected = '"mcqs", "coding_challenges"'
            
        prompt = f"""
        Act as an expert technical recruiter. Create a {difficulty} difficulty technical assessment.
        Job Description: {job_desc}
        
        TASK 1: Generate {mcq_count} Multiple Choice Questions (MCQs).
        Each MCQ object must have: "question", "options" (list of 4 strings), "answer" (string matching exactly one option).
{coding_prompt}
        CRITICAL FORMATTING INSTRUCTION: 
        You MUST return a single JSON object where the root keys are EXACTLY: {keys_expected}.
        DO NOT wrap the output in any outer keys like "assessment" or "data".
        If a key represents 0 requested items, omit it or make it an empty list.
        """
        
        if local_groq_client:
            response = local_groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content
            generated_data = extract_json(raw_text)
            
            if generated_data:
                assessment.generated_content = generated_data
                assessment.status = 'SCHEDULED'
                assessment.save()
            else:
                raise Exception("Failed to parse Groq response")
                
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
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@verifihire.com')
        # Use simple try-catch for mail to avoid crashing pipeline if SMTP isn't setup
        try:
            send_mail(subject, message, from_email, [candidate.email], fail_silently=False, html_message=html_message)
            logger.info(f"Pipeline: Assessment email sent to {candidate.email}")
        except Exception as e:
            logger.error(f"Pipeline: Failed to send assessment email to {candidate.email}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Pipeline Error (Resume): {e}")


def process_assessment_passed(submission_id):
    try:
        submission = AIAssessmentSubmission.objects.get(id=submission_id)
        if submission.status != 'selected':
            return
            
        logger.info(f"Pipeline: Generating Interview Invite for {submission.candidate_name}")
        
        # Link back to the Candidate model based on email
        candidates = Candidate.objects.filter(email=submission.candidate_email).order_by('-id')
        if not candidates.exists():
            logger.error(f"Pipeline Error: Candidate not found for email {submission.candidate_email}")
            return
            
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
            logger.info(f"Pipeline: Interview email sent to {candidate.email}")
        except Exception as e:
            logger.error(f"Pipeline: Failed to send interview email to {candidate.email}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Pipeline Error (Assessment): {e}")
