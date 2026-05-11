import re
import hashlib
import time
import logging
import io
import json
import PyPDF2
import fitz
import numpy as np
from PIL import Image
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from ai_assessments.llm_client import (
    create_llm_client,
    LLMKeyManager,
    call_llm_with_backoff,
    get_default_model
)
from .models import Candidate
from .utils import log_automation_event
from api.ocr_utils import _get_reader

# Backward-compatible aliases
GroqKeyManager = LLMKeyManager
_call_groq_with_backoff = call_llm_with_backoff

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
    api_keys = getattr(settings, 'DEEPSEEK_API_KEYS', [])
    if not api_keys:
        single_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        api_keys = [single_key] if single_key else []
    
    if not api_keys:
        logger.error("No DEEPSEEK_API_KEYS found!")
        return


    # DeepSeek V4 Flash - single model, no fallback needed
    primary_model = get_default_model()
    fallback_model = get_default_model()

    print(f"\nSTARTING OPTIMIZED BATCH: {total} candidates")
    print(f"Using {len(api_keys)} API keys with rotation.")
    print("------------------------------------------------------------")

    # Log batch start for each candidate if needed, 
    # but usually we log per candidate's specific start

    for index, candidate in enumerate(candidates):
        progress = f"[{index + 1}/{total}]"
        print(f"\n{progress} Processing: {candidate.full_name or 'Unknown'}")
        
        try:
            candidate.refresh_from_db()

            # 1. TEXT EXTRACTION (Moved from View to Task)
            if candidate.resume and not candidate.resume_text:
                print(f"   Reading file...", end="", flush=True)
                try:
                    file_bytes = candidate.resume.read()
                    
                    file_hash = hashlib.md5(file_bytes).hexdigest()
                    
                    if candidate.resume_hash == file_hash and candidate.resume_text:
                        print(f" Skipped (cached text reused)")
                    else:
                        text = ""
                        
                        try:
                            doc = fitz.open(stream=file_bytes, filetype="pdf")
                            for page in doc: text += page.get_text()
                            doc.close()
                        except fitz.FileDataError as e:
                            logger.warning(f"PyMuPDF failed for {candidate.id}: {e}")
                        except Exception as e:
                            logger.error(f"Unexpected PyMuPDF error: {e}")
                        
                        if len(text.strip()) < 100:
                            try:
                                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                                for page in pdf_reader.pages:
                                    text += (page.extract_text() or "")
                            except Exception as e:
                                logger.warning(f"PyPDF2 failed for {candidate.id}: {e}")
                        
                        if len(text.strip()) < 100:
                            print(" (OCR Fallback)...", end="", flush=True)
                            try:
                                reader = _get_reader()
                                if reader:
                                    doc = fitz.open(stream=file_bytes, filetype="pdf")
                                    if doc.page_count > 0:
                                        pix = doc.load_page(0).get_pixmap()
                                        img = Image.frombytes(
                                            "RGB", 
                                            [pix.width, pix.height], 
                                            pix.samples
                                        )
                                        text = " ".join(
                                            reader.readtext(np.array(img), detail=0)
                                        )
                                    doc.close()
                            except Exception as e:
                                logger.error(f"OCR failed for {candidate.id}: {e}")
                        
                        candidate.resume_text = text
                        candidate.resume_hash = file_hash
                        candidate.save()
                        print(f" Done ({len(text)} chars)")

                except Exception as e:
                    print(f" Extraction failed: {e}")
                    candidate.status = 'Extraction Failed'
                    candidate.save()
                    continue

            if not candidate.resume_text:
                print("   No text found in resume. Skipping.")
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

            # 2. AI ANALYSIS (Cascading Fallback: 70B -> 8B -> Sleep -> Retry)
            from openai import OpenAI
            import random
            groq_keys = list(getattr(settings, 'GROQ_API_KEYS', []))
            match_result = None
            
            if not groq_keys:
                logger.error("No GROQ_API_KEYS found in settings!")
            else:
                max_retries = 3
                for attempt in range(max_retries):
                    random.shuffle(groq_keys)
                    
                    # STEP 1: Exhaust all keys on 70B model first
                    print(f"\n   --- Attempt {attempt+1}: Prioritizing High-Accuracy 70B ---")
                    for key in groq_keys:
                        try:
                            print(f"   🤖 Trying 70B (llama-3.3-70b-versatile)... ", end="", flush=True)
                            groq_client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
                            response = groq_client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "user", "content": prompt}],
                                response_format={"type": "json_object"},
                                temperature=0.0,
                                seed=42
                            )
                            raw_text = response.choices[0].message.content
                            match_result = extract_json(raw_text)
                            if match_result:
                                print("✅ Success!")
                                break
                        except Exception as e:
                            print(f"❌ Rate limit/Error. Rotating key...")
                            continue
                    
                    if match_result:
                        break
                    
                    # STEP 2: Exhaust all keys on 8B model (Safety Net)
                    print(f"   ⚠️ 70B Exhausted. Falling back to 8B Safety Net ---")
                    for key in groq_keys:
                        try:
                            print(f"   🤖 Trying 8B (llama-3.1-8b-instant)... ", end="", flush=True)
                            groq_client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
                            response = groq_client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=[{"role": "user", "content": prompt}],
                                response_format={"type": "json_object"},
                                temperature=0.0,
                                seed=42
                            )
                            raw_text = response.choices[0].message.content
                            match_result = extract_json(raw_text)
                            if match_result:
                                print("✅ Success!")
                                break
                        except Exception as e:
                            print(f"❌ Rate limit/Error. Rotating key...")
                            continue
                    
                    if match_result:
                        break
                    
                    # STEP 3: If both models failed across all keys, Sleep and Retry
                    if attempt < max_retries - 1:
                        sleep_time = 10 * (2 ** attempt)  # 10s, 20s
                        print(f"   📉 All keys and models exhausted. Sleeping {sleep_time}s before full retry...")
                        time.sleep(sleep_time)
                
                if not match_result:
                    print(f"   🚨 CRITICAL: AI Analysis failed completely after {max_retries} full rotation cycles.")

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
                status_icon = "PASS" if is_eligible else "FAIL"
                print(f"\n   Done! Score: {percentage}% {status_icon}")

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
                print("\n   All AI attempts failed.")
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
                print(f"   Cooldown {wait}s...", end="", flush=True)
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

    print(f"\nBATCH COMPLETE: Processed {total} candidates.")

    if is_fully_automatic:
        passed_count = Candidate.objects.filter(batch_id=batch_id, status='Resume Passed').count()
        if passed_count > 0:
            print(f"Triggering automated assessment for {passed_count} passed candidates...")
            from api.tasks import trigger_batch_assessment_task
            trigger_batch_assessment_task.delay(batch_id)
        else:
            print("No candidates passed. Skipping automated assessment.")


@shared_task(bind=True, max_retries=3)
def process_ai_interview_answer_task(self, candidate_id, answer_text, current_question, remaining_questions, conversation_memory, current_turn_number):
    """
    Async task to process AI interview answers for high concurrency
    Handles 100+ concurrent interviews by queuing AI processing
    """
    from .models import Candidate, InterviewIntegrity
    from ai_assessments.ai_logic import extract_json
    import time as _time
    import re
    
    try:
        candidate = Candidate.objects.get(pk=candidate_id)
    except Candidate.DoesNotExist:
        logger.error(f"Candidate {candidate_id} not found in async task")
        return {'error': 'Candidate not found'}
    
    # Get least-used API key for load balancing
    api_key = LLMKeyManager.get_least_used_key()
    local_llm_client = create_llm_client(api_key=api_key)
    
    # Model configuration - DeepSeek V4 Flash (single model)
    PRIMARY_MODEL = get_default_model()
    FALLBACK_MODEL = get_default_model()
    COOLDOWN_SECONDS = 60
    
    # Check cooldown status
    if not hasattr(process_ai_interview_answer_task, '_fallback_until'):
        process_ai_interview_answer_task._fallback_until = 0
    
    if _time.time() < process_ai_interview_answer_task._fallback_until:
        chosen_model = FALLBACK_MODEL
        logger.info(f"Using fallback model {FALLBACK_MODEL} (70b cooldown active)")
    else:
        chosen_model = PRIMARY_MODEL
    
    # Build prompt with conversation context
    context_prompt = ""
    if conversation_memory:
        context_prompt = f"""
CONVERSATION CONTEXT (for reference only - do NOT repeat this info):
{json.dumps(conversation_memory, indent=2)}

"""
    
    prompt = f"""{context_prompt}CURRENT INTERVIEW TURN:
Candidate Answer: "{answer_text}"
Current Question: "{current_question}"
Turn Number: {current_turn_number}

{candidate._get_difficulty_instructions(candidate.experience_level) if hasattr(candidate, '_get_difficulty_instructions') else ''}

You must respond with a JSON object containing:
{{
    "is_clarification": true/false,
    "is_exit": true/false,
    "refined_next_question": "Next question if not clarification/exit",
    "feedback": "Feedback on current answer",
    "score": 0-100,
    "score_reason": "1-sentence justification for the score"
}}"""

    try:
        # Process with AI
        response = local_llm_client.chat.completions.create(
            model=chosen_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            seed=42,
            response_format={"type": "json_object"}
        )
        
        raw_text = response.choices[0].message.content
        data = extract_json(raw_text)
        
        if not data:
            logger.error(f"Invalid JSON from AI: {raw_text}")
            return {'error': 'Invalid AI response'}
        
        # Clean any leaked labels
        _label_pattern = re.compile(
            r'\b(?:JD|RESUME[- ]?SKILL|PROJECT|SCENARIO|SYNTAX|INTRO)\b[- ]?Q?\d*[:\.\-—]*\s*',
            re.IGNORECASE
        )
        for field in ('feedback', 'refined_next_question'):
            if data.get(field):
                data[field] = _label_pattern.sub('', data[field]).strip()
        
        # Update candidate score silently
        if data.get('score') is not None and not data.get('is_clarification'):
            q_score = int(data.get('score', 0))
            candidate.score += q_score
            candidate.total_questions += 1
            
            # Store per-question summary
            if not isinstance(candidate.interview_summary, list):
                candidate.interview_summary = []
            
            candidate.interview_summary.append({
                'question': current_question,
                'answer': answer_text[:500],  # Truncate for storage
                'feedback': data.get('feedback', ''),
                'score': q_score,
                'score_reason': data.get('score_reason', ''),
                'turn_number': current_turn_number,
                'is_clarification': data.get('is_clarification', False),
                'processed_at': timezone.now().isoformat()
            })
            
            # Update conversation memory
            if not isinstance(candidate.conversation_memory, dict):
                candidate.conversation_memory = {}
            
            # Extract key facts from answer for memory
            if answer_text and len(answer_text.strip()) > 10:
                memory_key = f"turn_{current_turn_number}"
                candidate.conversation_memory[memory_key] = {
                    'question': current_question,
                    'answer_summary': answer_text[:200],
                    'key_points': data.get('feedback', '')[:100]
                }
            
            candidate.save()
        
        return {
            'status': 'success',
            'data': data,
            'candidate_score': candidate.score,
            'total_questions': candidate.total_questions
        }
        
    except Exception as e:
        error_str = str(e).lower()
        
        if "rate limit" in error_str or "429" in error_str:
            LLMKeyManager.rotate_key()
            rotated_key = LLMKeyManager.get_current_key()
            local_llm_client = create_llm_client(api_key=rotated_key)
            
            if chosen_model == PRIMARY_MODEL:
                process_ai_interview_answer_task._fallback_until = _time.time() + COOLDOWN_SECONDS
                logger.warning(f"70b rate-limited! Falling back to {FALLBACK_MODEL}")
            
            try:
                # Retry with fallback
                response = local_llm_client.chat.completions.create(
                    model=FALLBACK_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    seed=42,
                    response_format={"type": "json_object"}
                )
                
                raw_text = response.choices[0].message.content
                data = extract_json(raw_text)
                
                if data:
                    return {'status': 'success', 'data': data, 'fallback_used': True}
                else:
                    return {'error': 'AI processing failed after retry'}
            except Exception as retry_err:
                logger.error(f"Fallback also failed: {retry_err}")
                return {'error': 'Both primary and fallback AI failed'}
        else:
            logger.error(f"AI processing error: {model_err}")
            if self.request.retries < self.max_retries:
                # Exponential backoff retry
                countdown = 2 ** self.request.retries
                raise self.retry(countdown=countdown, exc=model_err)
            return {'error': 'Task failed after retries'}
