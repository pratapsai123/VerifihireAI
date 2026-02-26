import logging
from django.conf import settings
from django.core.mail import send_mail
from groq import Groq
from ai_candidates.models import Candidate 
from ai_assessments.models import Assessment, AIAssessmentSubmission
from ai_candidates.views import extract_json

logger = logging.getLogger(__name__)

groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)

def process_resume_passed(candidate_id):
    try:
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
        
        # Generate Assessment Database Record
        assessment = Assessment.objects.create(
            job_description=job_desc,
            required_skills="Technical Assessment", 
            mcq_count=mcq_count,
            coding_count=coding_count,
            duration_minutes=duration,
            difficulty_level=difficulty,
            pass_threshold=pass_threshold,
            status='GENERATING'
        )
        
        prompt = f"""
        Act as an expert technical recruiter. Create a {difficulty} difficulty technical assessment.
        Job Description: {job_desc}
        
        TASK 1: Generate {mcq_count} Multiple Choice Questions (MCQs).
        Each MCQ object must have: "question", "options" (list of 4 strings), "answer" (string matching exactly one option).

        TASK 2: Generate {coding_count} Coding Challenge(s).
        Challenge object must have: "title", "problem_statement", "input_format", "output_format", "constraints", "example_input", "example_output", "explanation", "starter_code_java", "starter_code_python", "test_cases" (list of 5 objects with "input" and "output").
        
        Format strictly as JSON with keys: "mcqs", "coding_challenges".
        """
        
        if groq_api_key:
            response = groq_client.chat.completions.create(
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
        message = f"Dear {candidate.full_name},\n\nCongratulations! Your resume has been shortlisted.\nPlease complete the following technical assessment:\n{link}\n\nGood luck!"
        
        html_message = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Congratulations {candidate.full_name}!</h2>
            <p>Your resume has successfully passed our initial AI screening.</p>
            <p>The next step is a technical assessment automatically tailored to your background.</p>
            <a href="{link}" style="display: inline-block; margin-top: 15px; padding: 12px 24px; background-color: #6366F1; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">Start Assessment</a>
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
        message = f"Dear {candidate.full_name},\n\nYou passed the technical assessment!\nPlease complete the final AI video interview here:\n{link}\n\nGood luck!"
        
        html_message = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Excellent work {candidate.full_name}!</h2>
            <p>You have successfully passed the technical assessment portion.</p>
            <p>The final step is an AI-powered video interview.</p>
            <a href="{link}" style="display: inline-block; margin-top: 15px; padding: 12px 24px; background-color: #6366F1; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">Start Video Interview</a>
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
