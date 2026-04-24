import time
import logging
import io
import json
import uuid
import random
import PyPDF2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from groq import Groq
from .models import Candidate
from .utils import log_automation_event
from api.ocr_utils import _get_reader
from ai_assessments.ai_logic import _call_groq_with_backoff

logger = logging.getLogger(__name__)

def extract_json(text):
    """
    Robustly extracts and repairs JSON from AI responses.
    Handles unescaped quotes, trailing commas, and markdown blocks.
    """
    if not text:
        return None
        
    # 1. Basic Markdown Cleaning
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # 2. Extract first-level object/array
    try:
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1:
            json_str = cleaned[start:end+1]
            
            # Simple repairs for common AI hallucinations
            # A. Remove trailing commas in objects/arrays
            import re
            json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
            
            # B. Try parsing
            return json.loads(json_str, strict=False)
    except Exception as e:
        logger.error(f"JSON extraction error in tasks: {e}")
    return None

@shared_task(bind=True)
def process_resume_batch_task(self, batch_id, job_description, threshold=70, is_fully_automatic=False, automation_settings=None):
    """
    Background task to process a batch of resumes.
    Now includes File Extraction (OCR) and optimized AI rotation.
    """
    candidates = Candidate.objects.filter(batch_id=batch_id, status='New')
    total = candidates.count()
    
    # 0. Setup Keys
    api_keys = getattr(settings, 'GROQ_API_KEYS', [])
    if not api_keys:
        single_key = getattr(settings, 'GROQ_API_KEY', None)
        api_keys = [single_key] if single_key else []
    
    if not api_keys:
        logger.error("No GROQ_API_KEYS found!")
        return


    # FAST MODEL first, powerful one as fallback
    primary_model = "llama-3.1-8b-instant"
    fallback_model = "llama-3.3-70b-versatile"

    print(f"\n🚀 STARTING OPTIMIZED BATCH: {total} candidates")
    print(f"🔑 Using {len(api_keys)} API keys with rotation.")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Log batch start for each candidate if needed, 
    # but usually we log per candidate's specific start

    for index, candidate in enumerate(candidates):
        progress = f"[{index + 1}/{total}]"
        print(f"\n{progress} 📄 Processing: {candidate.full_name or 'Unknown'}")
        
        try:
            candidate.refresh_from_db()

            # 1. TEXT EXTRACTION (Moved from View to Task)
            if not candidate.resume_text and candidate.resume:
                print(f"   📖 Reading file...", end="", flush=True)
                try:
                    file_bytes = candidate.resume.read()
                    text = ""
                    
                    # Try PyMuPDF
                    try:
                        doc = fitz.open(stream=file_bytes, filetype="pdf")
                        for page in doc: text += page.get_text()
                        doc.close()
                    except: pass
                    
                    # Try PyPDF2 fallback
                    if len(text.strip()) < 100:
                        try:
                            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                            for page in pdf_reader.pages: text += (page.extract_text() or "")
                        except: pass
                    
                    # Try OCR if still empty
                    if len(text.strip()) < 100:
                        print(" (OCR Fallback)...", end="", flush=True)
                        try:
                            reader = _get_reader()
                            if reader:
                                doc = fitz.open(stream=file_bytes, filetype="pdf")
                                if doc.page_count > 0:
                                    pix = doc.load_page(0).get_pixmap()
                                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                    text = " ".join(reader.readtext(np.array(img), detail=0))
                                doc.close()
                        except: pass
                    
                    candidate.resume_text = text
                    candidate.save()
                    print(f" Done ({len(text)} chars)")
                except Exception as e:
                    print(f" ❌ Extraction failed: {e}")
                    candidate.status = 'Extraction Failed'
                    candidate.save()
                    continue

            if not candidate.resume_text:
                print("   ❌ No text found in resume. Skipping.")
                candidate.status = 'Extraction Failed'
                candidate.save()
                continue

            # 2. AI ANALYSIS (with rotation)
            # Use 70b as primary again because user needs strict accuracy
            current_model = fallback_model 
            match_result = None
            
            prompt = f"""
            Act as an expert technical recruiter and interviewer. Analyze the match between the following resume and job description.
            
            RESUME:
            {candidate.resume_text[:10000]}
            
            JOB DESCRIPTION:
            {job_description}
            
            SCORING RULES (Weighted & Professional):
            1. CORE SKILLS (60% weight): For every MUST-HAVE technology mentioned in the JD that is missing, subtract 10-15 points.
            2. SECONDARY SKILLS (20% weight): For minor tools or nice-to-have libraries, subtract only 3-5 points.
            3. EXPERIENCE (20% weight): Evaluate depth of experience and project complexity.
            4. If the candidate has NO relevant industry experience for the role, cap the total score at 50%.
            5. BE CONSISTENT: Identical Resume/JD pairs must result in the same logical evaluation.
            6. OBJECTIVITY: Base the score ONLY on the text in the resume. Do not assume skills.
            
            Please provide:
            1. The candidate's full name. 
            2. The candidate's contact email.
            3. A match percentage (0-100). 
            4. A 2-3 sentence summary that EXPLICITLY mentions what core skills are MISSING.
            5. A list of 7 interview questions based strictly on the JD requirements and their actual experience.
            
            Format the output strictly as a raw JSON object with these keys: "candidate_name", "candidate_email", "match_percentage", "summary", "interview_questions".
            CRITICAL: You MUST properly escape any internal double quotes inside strings (e.g., use \\" instead of ") to ensure the JSON is perfectly valid and parsable.
            """

            # Centralized API call with exponential backoff and key rotation
            try:
                print(f"   🧠 AI Analysis ({current_model})...", end="", flush=True)
                # Initialize a dummy client for the first attempt; helper will rotate if needed
                temp_client = Groq(api_key=api_keys[0]) 
                
                # _call_groq_with_backoff now returns the content/dict directly
                result = _call_groq_with_backoff(
                    temp_client,
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=2048,
                    temperature=0.0,
                    seed=42
                )
                match_result = result if isinstance(result, dict) else extract_json(result)
            except Exception as e:
                print(f"\n   ❌ AI Final Error: {e}")
                match_result = None

            # 3. SAVE RESULTS
            if match_result:
                try:
                    percentage = int(float(match_result.get('match_percentage', 0)))
                except: percentage = 0
                
                # Only overwrite identity if it's a new placeholder record (Bulk Upload flow)
                # This prevents invited candidates from accidentally (or maliciously) changing their identity
                # by uploading a resume with different contact details.
                # Only overwrite identity if it's missing or a placeholder.
                # This prevents valid recruiter-entered data from being replaced by AI extraction errors.
                is_placeholder_email = not candidate.email or any(p in candidate.email.lower() for p in ['pending', 'extraction', 'unknown'])
                is_placeholder_name = not candidate.full_name or any(p in candidate.full_name.lower() for p in ['extraction', 'unknown', 'pending'])

                ext_name = match_result.get('candidate_name')
                ext_email = match_result.get('candidate_email')

                if is_placeholder_name and ext_name and ext_name != "Extraction Failed":
                    candidate.full_name = ext_name
                
                if is_placeholder_email and ext_email and ext_email != "Extraction Failed":
                    candidate.email = ext_email
                candidate.resume_score = percentage
                is_eligible = (percentage >= threshold)
                candidate.status = 'Resume Passed' if is_eligible else 'Resume Failed'
                candidate.interview_questions = match_result.get('interview_questions', [])
                
                if automation_settings:
                    # Persist the settings 
                    candidate.automation_settings = automation_settings
                    # Explicitly save the flag for UI distinction
                    candidate.automation_settings['is_fully_automatic'] = is_fully_automatic
                    
                    # Set interview pass threshold from automation settings
                    candidate.interview_pass_threshold = automation_settings.get('interview_pass_threshold', 50)
                    
                    i_from = automation_settings.get('interview_available_from')
                    i_until = automation_settings.get('interview_available_until')
                    if i_from: candidate.available_from = parse_datetime(i_from)
                    if i_until: candidate.available_until = parse_datetime(i_until)

                candidate.save()
                status_icon = "✅" if is_eligible else "❌"
                print(f"\n   🏁 Done! Score: {percentage}% {status_icon}")

                # Log the screening result
                log_automation_event(
                    candidate, 
                    'STATUS_CHANGE', 
                    'SUCCESS' if is_eligible else 'WARNING', 
                    f"Resume screening complete. Score: {percentage}%. Status: {candidate.status}",
                    phase='RESUME'
                )
            else:
                candidate.status = 'Extraction Failed'
                candidate.save()
                print("\n   ❌ All AI attempts failed.")
                log_automation_event(
                    candidate, 
                    'ERROR', 
                    'FAILURE', 
                    "AI Analysis failed: model could not extract valid candidate data after multiple attempts.",
                    phase='RESUME'
                )

            # Cooldown (Minimal because of key rotation and fast model)
            if index < total - 1:
                wait = 3 if len(api_keys) > 1 else 10
                print(f"   ⏳ Cooldown {wait}s...", end="", flush=True)
                time.sleep(wait)
                print("Ready!")

        except Exception as e:
            logger.error(f"Critical error for candidate {candidate.id}: {e}")
            candidate.status = 'Extraction Failed'
            candidate.save()
            log_automation_event(
                candidate, 
                'ERROR', 
                'FAILURE', 
                f"Critical failure during resume processing: {str(e)}",
                phase='RESUME'
            )

    print(f"\n✨ BATCH COMPLETE: Processed {total} candidates.")

    if is_fully_automatic:
        passed_count = Candidate.objects.filter(batch_id=batch_id, status='Resume Passed').count()
        if passed_count > 0:
            print(f"🚀 Triggering automated assessment for {passed_count} passed candidates...")
            from api.tasks import trigger_batch_assessment_task
            trigger_batch_assessment_task.delay(batch_id)
        else:
            print("ℹ️ No candidates passed. Skipping automated assessment.")
