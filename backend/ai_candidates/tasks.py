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

    for index, candidate in enumerate(candidates):
        logger.info(f"Processing candidate {index+1}/{total}: {candidate.full_name} (ID: {candidate.id})")
        
        try:
            prompt = f"""
            Act as an expert technical recruiter and interviewer. Analyze the match between the following resume and job description.
            
            Resume Content:
            {candidate.resume_text}
            
            Job Description:
            {job_description}
            
            Please provide:
            1. The candidate's full name. Look at the very top of the document. If missing, use "{candidate.full_name}". 
            2. The candidate's contact email. Look for email patterns. If missing, use "missing@example.com".
            3. A match percentage (0-100) based on skills and experience matching the JD. NOTE: Give partial credit (20-30%) for transferable skills/general experience even if primary tech stack differs. Never return 0% if the candidate has any relevant engineering background.
            4. Eligibility status (True if match percentage >= {threshold}, otherwise False).
            5. A brief 2-3 sentence summary of the fit. Mention both strengths and gaps.
            6. A list of 7 interview questions (5 technical/behavioral questions + 2 coding-specific challenges or deep-dives) based on their resume and the JD. 
            
            Format the output strictly as a raw JSON object with these keys: "candidate_name", "candidate_email", "match_percentage", "is_eligible", "summary", "interview_questions".
            """

            # Try processing with llama-3.3-70b-versatile
            match_result = None
            for attempt in range(2): # 2 attempts in bg task to handle any weirdness
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        temperature=0.1
                    )
                    raw_text = response.choices[0].message.content
                    match_result = extract_json(raw_text)
                    if match_result:
                        break
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"Groq API error for candidate {candidate.id} (attempt {attempt+1}): {e}")
                    time.sleep(5)

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
