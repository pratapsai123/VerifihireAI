import time
import logging
from celery import shared_task
from django.conf import settings
from groq import Groq
from .models import Candidate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import json

logger = logging.getLogger(__name__)

def extract_json(text):
    try:
        # Find the first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            json_str = text[start:end+1]
            return json.loads(json_str)
    except Exception as e:
        logger.error(f"JSON extraction error in background task: {e}")
    return None

@shared_task
def process_resume_batch_task(batch_id, job_description, threshold=70, is_fully_automatic=False, automation_settings=None):
    """
    Background task to process a batch of candidates one-by-one with delays to respect Groq rate limits.
    Uses llama-3.3-70b-versatile for high quality.
    """
    candidates = Candidate.objects.filter(batch_id=batch_id, status='New')
    total = candidates.count()
    logger.info(f"Starting background processing for batch {batch_id}. Total candidates: {total}")

    local_api_key = getattr(settings, 'GROQ_API_KEY', None)
    if not local_api_key:
        logger.error("GROQ_API_KEY not found in settings")
        return

    client = Groq(api_key=local_api_key)

    current_model = "llama-3.3-70b-versatile"
    
    for index, candidate in enumerate(candidates):
        # Debug: Check if resume text exists
        resume_len = len(candidate.resume_text or "")
        logger.info(f"--- DEBUG: Processing candidate {candidate.id} ---")
        logger.info(f"Resume text length: {resume_len} characters")
        logger.info(f"JD length: {len(job_description or '')} characters")
        
        if resume_len < 100:
            logger.warning(f"Candidate {candidate.id} has very short resume text. Scoring may be inaccurate.")
        
        try:
            # Re-read from DB to ensure we have latest data
            candidate.refresh_from_db()
            
            prompt = f"""
            Act as an expert technical recruiter and interviewer. Analyze the match between the following resume and job description.
            
            RESUME:
            {candidate.resume_text}
            
            JOB DESCRIPTION:
            {job_description}
            
            SCORING RULES (Strict & Objective):
            1. Start with a BASE SCORE of 100%.
            2. For every CORE SKILL or TECHNOLOGY mentioned in the JD that is MISSING from the resume, SUBTRACT 15-20 points.
            3. If the candidate has NO relevant industry experience for the role, the final score must be below 20%.
            4. If the resume and JD are a 100% match, return 100%.
            5. Be brutally honest. Do not "inflate" the score, but do not drop to 0% unless there is zero relevance.
            
            Please provide:
            1. The candidate's full name. Look at the very top of the document. If missing, use "{candidate.full_name}". 
            2. The candidate's contact email. Look for email patterns. If missing, use "missing@example.com".
            3. A match percentage (0-100). 
            4. A brief 2-3 sentence summary of the fit. Explicitly mention any missing core skills.
            5. A list of 7 interview questions (5 technical/behavioral questions + 2 coding-specific challenges or deep-dives) based on their resume and the JD. 
            
            Format the output strictly as a raw JSON object with these keys: "candidate_name", "candidate_email", "match_percentage", "summary", "interview_questions".
            """

            match_result = None
            max_attempts = 2
            for attempt in range(max_attempts):
                try:
                    response = client.chat.completions.create(
                        model=current_model,
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        temperature=0.0
                    )
                    raw_text = response.choices[0].message.content
                    logger.info(f"Raw AI Response for {candidate.id}: {raw_text}")
                    match_result = extract_json(raw_text)
                    if match_result:
                        break
                    time.sleep(2)
                except Exception as e:
                    error_msg = str(e).lower()
                    # Check for rate limit / quota exceeded
                    if ("429" in error_msg or "rate limit" in error_msg or "quota" in error_msg) and current_model == "llama-3.3-70b-versatile":
                        logger.warning(f"Quota reached for 70b model. Falling back to 8b model for candidate {candidate.id} and remaining batch.")
                        current_model = "llama-3.1-8b-instant"
                        # Reset attempts for the new model if this happened on first attempt
                        # Actually, just let the next iteration of the 'for attempt' loop use the new model
                        continue 
                    
                    logger.warning(f"Groq API error for candidate {candidate.id} (attempt {attempt+1}): {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(10) # Wait a bit longer on error

            if match_result:
                percentage = match_result.get('match_percentage', 0)
                try:
                    num_percentage = int(float(percentage))
                except:
                    num_percentage = 0
                
                candidate.full_name = match_result.get('candidate_name', candidate.full_name)
                candidate.email = match_result.get('candidate_email', candidate.email)
                candidate.resume_score = num_percentage
                is_eligible = (num_percentage >= threshold)
                candidate.status = 'Resume Passed' if is_eligible else 'Resume Failed'
                candidate.interview_questions = match_result.get('interview_questions', [])
                
                # Apply automation settings if provided
                if is_fully_automatic and automation_settings:
                    candidate.automation_settings = automation_settings
                    # Handle dates
                    i_from = automation_settings.get('interview_available_from')
                    i_until = automation_settings.get('interview_available_until')
                    if i_from: candidate.available_from = parse_datetime(i_from)
                    if i_until: candidate.available_until = parse_datetime(i_until)

                candidate.save()
                logger.info(f"Successfully processed candidate {candidate.id}. Score: {num_percentage}%")
            else:
                logger.error(f"Failed to extract results for candidate {candidate.id} after retries.")
                # We don't mark as failure here so it can be manually retried if needed, or 
                # we could mark it as failure. Let's keep it as 'New' or mark as error?
                # Actually, let's mark it so the UI knows it failed.
                candidate.status = 'Extraction Failed'
                candidate.save()

        except Exception as e:
            logger.error(f"Ultimate error in background task for candidate {candidate.id}: {e}")
            candidate.status = 'Extraction Failed'
            candidate.save()

        # RATE LIMITING: Sleep between candidates to respect Groq free tier (6,000 tokens/min)
        if index < total - 1:
            logger.info(f"Sleeping 20 seconds before next candidate to respect rate limits...")
            time.sleep(20)

    logger.info(f"Background processing complete for batch {batch_id}.")
