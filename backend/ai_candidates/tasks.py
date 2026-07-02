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
    get_default_model,
    GroqKeyManager,
    call_groq_with_backoff,
    get_groq_model
)
from .models import Candidate
from .utils import log_automation_event, clean_repetitive_text
from api.ocr_utils import _get_reader

# Backward-compatible aliases
_call_groq_with_backoff = call_groq_with_backoff

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
    api_keys = getattr(settings, 'GROQ_API_KEYS', [])
    if not api_keys:
        single_key = getattr(settings, 'GROQ_API_KEY', None)
        api_keys = [single_key] if single_key else []
    
    if not api_keys:
        logger.error("No GROQ_API_KEYS found!")
        return


    primary_model = get_groq_model()
    fallback_model = get_groq_model()

    print(f"\nSTARTING OPTIMIZED BATCH: {total} candidates")
    print(f"Using {len(api_keys)} Groq API keys with rotation.")
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
                    file_name = candidate.resume.name.lower()
                    file_hash = hashlib.md5(file_bytes).hexdigest()
                    
                    if candidate.resume_hash == file_hash and candidate.resume_text:
                        print(f" Skipped (cached text reused)")
                    else:
                        text = ""
                        
                        if file_name.endswith('.pdf'):
                            # Try standard PDF extraction
                            try:
                                doc = fitz.open(stream=file_bytes, filetype="pdf")
                                for page in doc: text += page.get_text()
                                doc.close()
                            except Exception as e:
                                logger.warning(f"PyMuPDF failed for {candidate.id}: {e}")
                            
                            if len(text.strip()) < 250:
                                try:
                                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                                    for page in pdf_reader.pages:
                                        text += (page.extract_text() or "")
                                except Exception as e:
                                    logger.warning(f"PyPDF2 failed for {candidate.id}: {e}")
                            
                            # Fallback to OCR if still no/little text
                            if len(text.strip()) < 250:
                                print(" (OCR Fallback)...", end="", flush=True)
                                from api.ocr_utils import extract_text_from_pdf_ocr
                                text = extract_text_from_pdf_ocr(file_bytes)

                        elif file_name.endswith('.docx'):
                            # Try standard DOCX extraction
                            try:
                                from docx import Document
                                doc = Document(io.BytesIO(file_bytes))
                                for paragraph in doc.paragraphs:
                                    text += paragraph.text + " "
                                for table in doc.tables:
                                    for row in table.rows:
                                        for cell in row.cells:
                                            text += cell.text + " "
                            except Exception as e:
                                logger.warning(f"python-docx failed for {candidate.id}: {e}")

                            # Fallback to OCR for image-based DOCX
                            if len(text.strip()) < 250:
                                print(" (OCR Fallback)...", end="", flush=True)
                                from api.ocr_utils import extract_text_from_docx_ocr
                                text = extract_text_from_docx_ocr(file_bytes)
                        
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

            # 1.5 ATS FORMAT VALIDATION — reject resumes missing critical sections
            resume_lower = candidate.resume_text.lower()
            ats_sections_found = 0
            ats_missing = []

            # Check for Contact Info (email or phone pattern)
            has_contact = bool(
                re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', candidate.resume_text) or
                re.search(r'[\+]?[\d\s\-\(\)]{7,15}', candidate.resume_text)
            )
            if has_contact:
                ats_sections_found += 1
            else:
                ats_missing.append('Contact Info')

            # Check for Experience section
            has_experience = bool(re.search(
                r'\b(experience|work\s*history|employment|professional\s*background|work\s*experience|career\s*history|positions?\s*held)\b',
                resume_lower
            ))
            if has_experience:
                ats_sections_found += 1
            else:
                ats_missing.append('Experience')

            # Check for Education section
            has_education = bool(re.search(
                r'\b(education|academic|qualification|degree|university|college|bachelor|master|b\.?tech|m\.?tech|b\.?e\b|m\.?e\b|b\.?sc|m\.?sc|diploma|school)\b',
                resume_lower
            ))
            if has_education:
                ats_sections_found += 1
            else:
                ats_missing.append('Education')

            # Check for Skills section
            has_skills = bool(re.search(
                r'\b(skills|technical\s*skills|core\s*competenc|proficienc|technologies|tools|frameworks|languages\s*known|expertise)\b',
                resume_lower
            ))
            if has_skills:
                ats_sections_found += 1
            else:
                ats_missing.append('Skills')

            # Require at least 3 out of 4 ATS sections
            if ats_sections_found < 3:
                print(f"   ❌ ATS Validation Failed — Missing: {', '.join(ats_missing)}")
                candidate.status = 'Invalid Resume Format'
                candidate.resume_summary = f"Resume rejected: Missing required ATS sections — {', '.join(ats_missing)}. A valid resume must include at least 3 of: Contact Info, Experience, Education, Skills."
                candidate.save()
                log_automation_event(
                    candidate,
                    'STATUS_CHANGE',
                    'WARNING',
                    f"ATS validation failed. Missing sections: {', '.join(ats_missing)}. Found {ats_sections_found}/4 required sections.",
                    phase='RESUME'
                )
                continue
            else:
                print(f"   ✅ ATS Validation Passed ({ats_sections_found}/4 sections found)")

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
            1. CORE SKILLS (50% weight): For every MUST-HAVE technology mentioned in the JD that is missing, subtract 10-15 points.
            2. SECONDARY SKILLS (15% weight): For minor tools or nice-to-have libraries, subtract only 3-5 points.
            3. EXPERIENCE (20% weight): Evaluate depth of experience and project complexity.
            4. CERTIFICATIONS (15% weight): 
               - Award 10-15 bonus points for certifications that DIRECTLY match the JD role (e.g., Python certification for a Python Developer role).
               - Award 5-8 points for certifications that PARTIALLY match (e.g., HTML/CSS/JS certification for a Full Stack Developer role — relevant but incomplete coverage).
               - Award 0 points for certifications completely unrelated to the JD.
               - If the candidate has NO certifications, do NOT penalize — just award 0 bonus points.
            5. If the candidate has NO relevant industry experience for the role, cap the total score at 50%.
            6. BE CONSISTENT: Identical Resume/JD pairs must result in the same logical evaluation.
            7. OBJECTIVITY: Base the score ONLY on the text in the resume. Do not assume skills.
            
            DEEP SKILL ANALYSIS RULES:
            - Do NOT treat skill keywords at face value. Analyze the DEPTH of each skill based on project descriptions, years of usage, and complexity of work done.
            - A candidate who lists "React" but has only built a to-do app should score LOWER than one who built production-level dashboards.
            - If the JD requires "Full Stack Developer" but the candidate only has frontend skills/certifications, recognize this as a PARTIAL match (not full).
            - Cross-reference certifications against the JD: a "Python PCAP" cert for a "Python Developer" JD is a STRONG match, but a "Google Analytics" cert for the same role is IRRELEVANT.
            
            Please provide:
            1. The candidate's full name. 
            2. The candidate's contact email.
            3. A match percentage (0-100). 
            4. A 2-3 sentence summary that EXPLICITLY mentions what core skills are MISSING and whether certifications are relevant.
            5. A list of 7 interview questions based strictly on the JD requirements and their actual experience.
            
            Format the output strictly as a raw JSON object with these keys: "candidate_name", "candidate_email", "match_percentage", "summary", "interview_questions".
            CRITICAL: You MUST properly escape any internal double quotes inside strings (e.g., use \\" instead of ") to ensure the JSON is perfectly valid and parsable.
            """

            # 2. AI ANALYSIS (Using unified LLM client with backoff and key rotation)
            match_result = None
            
            try:
                print(f"   🤖 Calling Groq ({get_groq_model()})... ", end="", flush=True)
                match_result = call_groq_with_backoff(
                    prompt=prompt,
                    is_json=True,
                    max_tokens=4096,
                    temperature=0.0,
                )
                if match_result:
                    print("✅ Success!")
                else:
                    print("❌ Empty response")
            except Exception as llm_err:
                print(f"❌ LLM Error: {llm_err}")
                logger.error(f"LLM analysis failed for candidate {candidate.id}: {llm_err}")

            if not match_result:
                print(f"   🚨 CRITICAL: AI Analysis failed completely.")

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
                
                # Determine if this candidate should be scored
                # 1. Bulk creation of AI Interviews (no scoring wanted)
                is_bulk_ai_interview = (
                    automation_settings and 
                    isinstance(automation_settings, dict) and 
                    'interview_duration_minutes' in automation_settings and 
                    not is_fully_automatic
                )
                
                # 2. Candidate is starting the interview via the public link
                # ResumeMatchView passes automation_settings={} for this flow
                is_interview_start_flow = (automation_settings == {})

                if is_bulk_ai_interview or is_interview_start_flow:
                    # AI Interview: just store questions, do NOT overwrite their existing resume_score
                    candidate.resume_summary = match_result.get('summary', '')
                else:
                    # Resume Screening OR Fully-Automatic: score and set pass/fail
                    candidate.resume_score = percentage
                    candidate.resume_summary = match_result.get('summary', 'No summary provided by AI.')
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

@shared_task(bind=True, max_retries=2)
def extract_resume_text_task(self, candidate_id):
    """
    Standalone async task to extract text from a single candidate's resume.
    Used during the registration flow when a candidate uploads a resume.
    Uses the same PyMuPDF → PyPDF2 → OCR cascade as the batch processor.
    """
    try:
        candidate = Candidate.objects.get(pk=candidate_id)
    except Candidate.DoesNotExist:
        logger.error(f"extract_resume_text_task: Candidate {candidate_id} not found")
        return

    if not candidate.resume:
        logger.info(f"extract_resume_text_task: Candidate {candidate_id} has no resume file. Skipping.")
        return

    if candidate.resume_text and len(candidate.resume_text.strip()) > 100:
        logger.info(f"extract_resume_text_task: Candidate {candidate_id} already has extracted text. Skipping.")
        return

    logger.info(f"extract_resume_text_task: Starting extraction for candidate {candidate_id}")

    try:
        file_bytes = candidate.resume.read()
        file_hash = hashlib.md5(file_bytes).hexdigest()

        # Skip if hash matches (already processed)
        if candidate.resume_hash == file_hash and candidate.resume_text:
            logger.info(f"extract_resume_text_task: Hash match — reusing cached text for {candidate_id}")
            return

        text = ""

        # Step 1: PyMuPDF
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            logger.warning(f"extract_resume_text_task: PyMuPDF failed for {candidate_id}: {e}")

        # Step 2: PyPDF2 fallback
        if len(text.strip()) < 100:
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                for page in pdf_reader.pages:
                    text += (page.extract_text() or "")
            except Exception as e:
                logger.warning(f"extract_resume_text_task: PyPDF2 failed for {candidate_id}: {e}")

        # Step 3: OCR fallback
        if len(text.strip()) < 100:
            try:
                reader = _get_reader()
                if reader:
                    doc = fitz.open(stream=file_bytes, filetype="pdf")
                    if doc.page_count > 0:
                        pix = doc.load_page(0).get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        text = " ".join(reader.readtext(np.array(img), detail=0))
                    doc.close()
            except Exception as e:
                logger.error(f"extract_resume_text_task: OCR failed for {candidate_id}: {e}")

        candidate.resume_text = text
        candidate.resume_hash = file_hash
        candidate.save(update_fields=['resume_text', 'resume_hash'])
        logger.info(f"extract_resume_text_task: Extracted {len(text)} chars for candidate {candidate_id}")

    except Exception as e:
        logger.error(f"extract_resume_text_task: Critical error for {candidate_id}: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=5 * (self.request.retries + 1), exc=e)


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
    
    # Clean speech repetition artifacts from candidate's answer
    answer_text = clean_repetitive_text(answer_text)
    
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

Note: The candidate answer might contain transcription artifacts or mechanical speech repetitions. Ignore them semantically and evaluate the underlying answer without giving any score penalty for repetition.

You must respond with a JSON object containing:
{{
    "is_clarification": true/false,
    "is_exit": true/false,
    "refined_next_question": "Next question if not clarification/exit",
    "feedback": "Feedback on current answer",
    "score": "0-10 (where 0 is completely wrong/irrelevant and 10 is a perfect expert answer)",
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
        
        # Track whether this is a silent/skipped answer
        SILENCE_MARKER = "[Candidate remained silent/skipped]"
        is_silent_answer = answer_text and answer_text.strip() == SILENCE_MARKER

        # FIX: If answer was silent, NEVER allow AI to set is_exit=True.
        # Only the frontend 3-consecutive-silence rule should end the interview.
        # Also, do not count silent turns toward total_questions.
        if is_silent_answer:
            data['is_exit'] = False
            # Track consecutive silences in DB
            consecutive_silence_count = (candidate.conversation_memory or {}).get('_consecutive_silences', 0) + 1
            mem = candidate.conversation_memory or {}
            mem['_consecutive_silences'] = consecutive_silence_count
            candidate.conversation_memory = mem
            try:
                candidate.save(update_fields=['conversation_memory'])
            except Exception:
                pass
            logger.info(f"[Silence Async] Candidate {candidate_id} silent answer #{consecutive_silence_count}/3 — is_exit suppressed.")

            # Backend safety: end after 3 consecutive silences (mirrors frontend rule)
            if consecutive_silence_count >= 3:
                data['is_exit'] = True
                data['refined_next_question'] = None
                data['feedback'] = "We haven't been able to hear you for a while. The interview will now be concluded. Thank you for your time."
                logger.warning(f"[Silence Async] 3 consecutive silences for candidate {candidate_id}. Forcing is_exit=True.")
        else:
            # Non-silent answer — reset consecutive silence counter
            mem = candidate.conversation_memory or {}
            if mem.get('_consecutive_silences', 0) > 0:
                mem['_consecutive_silences'] = 0
                try:
                    candidate.save(update_fields=['conversation_memory'])
                except Exception:
                    pass

        # Update candidate score silently
        # FIX: Silent answers do NOT increment total_questions (turn counter).
        if data.get('score') is not None and not data.get('is_clarification') and not is_silent_answer:
            q_score = int(data.get('score', 0))
            
            # Use F() expressions to prevent race conditions with concurrent requests
            from django.db.models import F
            Candidate.objects.filter(pk=candidate_id).update(
                score=F('score') + q_score,
                total_questions=F('total_questions') + 1
            )
            # Refresh to get updated values
            candidate.refresh_from_db()
            
            # Store per-question summary
            if not isinstance(candidate.interview_summary, list):
                candidate.interview_summary = []
            
            candidate.interview_summary.append({
                'question': current_question,
                'answer': answer_text[:10000],  # Truncate to a higher limit (10k) for long code snippets
                'feedback': data.get('feedback', ''),
                'score': q_score,
                'score_reason': data.get('score_reason', ''),
                'turn_number': current_turn_number,
                'is_clarification': data.get('is_clarification', False),
                'processed_at': timezone.now().isoformat()
            })
            
            # Update conversation memory (aligned with sync ProcessAnswerView structure)
            if not isinstance(candidate.conversation_memory, dict):
                candidate.conversation_memory = {}
            
            memory = candidate.conversation_memory
            if not memory.get('intro_facts'):
                memory['intro_facts'] = []
            if not memory.get('skills_mentioned'):
                memory['skills_mentioned'] = []
            if not memory.get('projects_discussed'):
                memory['projects_discussed'] = []
            if not memory.get('weak_areas'):
                memory['weak_areas'] = []
            
            # Extract key facts from answer for memory
            if answer_text and len(answer_text.strip()) > 10:
                if current_turn_number == 1:
                    memory['intro_facts'].append(answer_text[:80].strip())
                    memory['intro_facts'] = list(set(memory['intro_facts']))[:5]
                elif current_turn_number in [6, 7]:
                    memory['skills_mentioned'].append(answer_text[:50].strip())
                    memory['skills_mentioned'] = list(set(memory['skills_mentioned']))[:5]
                elif current_turn_number in [8, 9]:
                    memory['projects_discussed'].append(answer_text[:60].strip())
                    memory['projects_discussed'] = list(set(memory['projects_discussed']))[:3]
                
                if q_score <= 4:
                     memory['weak_areas'].append(current_question[:50].strip())
                     memory['weak_areas'] = list(set(memory['weak_areas']))[:3]
            
            candidate.conversation_memory = memory
            candidate.save(update_fields=['interview_summary', 'conversation_memory'])
        
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
            logger.error(f"AI processing error: {e}")
            if self.request.retries < self.max_retries:
                # Exponential backoff retry
                countdown = 2 ** self.request.retries
                raise self.retry(countdown=countdown, exc=e)
            return {'error': 'Task failed after retries'}

@shared_task(bind=True)
def process_standalone_resume_screening_task(self, record_id, threshold=50):
    from .models import StandaloneResumeScreening
    try:
        record = StandaloneResumeScreening.objects.get(pk=record_id)
    except StandaloneResumeScreening.DoesNotExist:
        logger.error(f"process_standalone_resume_screening_task: Record {record_id} not found")
        return

    # 1. TEXT EXTRACTION (Same logic as original Candidate task)
    try:
        if record.resume and not record.resume_text:
            print(f"   Reading file...", end="", flush=True)
            file_bytes = record.resume.read()
            file_name = record.resume.name.lower()
            file_hash = hashlib.md5(file_bytes).hexdigest()

            if record.resume_hash == file_hash and record.resume_text:
                print(f" Skipped (cached text reused)")
            else:
                text = ""

                if file_name.endswith('.pdf'):
                    # Try standard PDF extraction
                    try:
                        doc = fitz.open(stream=file_bytes, filetype="pdf")
                        for page in doc: text += page.get_text()
                        doc.close()
                    except Exception as e:
                        logger.warning(f"PyMuPDF failed for standalone {record.id}: {e}")

                    if len(text.strip()) < 250:
                        try:
                            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                            for page in pdf_reader.pages:
                                text += (page.extract_text() or "")
                        except Exception as e:
                            logger.warning(f"PyPDF2 failed for standalone {record.id}: {e}")

                    # Fallback to OCR if still no/little text
                    if len(text.strip()) < 250:
                        print(" (OCR Fallback)...", end="", flush=True)
                        from api.ocr_utils import extract_text_from_pdf_ocr
                        text = extract_text_from_pdf_ocr(file_bytes)

                elif file_name.endswith('.docx'):
                    # Try standard DOCX extraction
                    try:
                        from docx import Document
                        doc = Document(io.BytesIO(file_bytes))
                        for paragraph in doc.paragraphs:
                            text += paragraph.text + " "
                        for table in doc.tables:
                            for row in table.rows:
                                for cell in row.cells:
                                    text += cell.text + " "
                    except Exception as e:
                        logger.warning(f"python-docx failed for standalone {record.id}: {e}")

                    # Fallback to OCR for image-based DOCX
                    if len(text.strip()) < 250:
                        print(" (OCR Fallback)...", end="", flush=True)
                        from api.ocr_utils import extract_text_from_docx_ocr
                        text = extract_text_from_docx_ocr(file_bytes)

                record.resume_text = text
                record.resume_hash = file_hash
                record.save()
                print(f" Done ({len(text)} chars)")

    except Exception as e:
        print(f" Extraction failed: {e}")
        logger.error(f"Extraction failed for standalone {record.id}: {e}")
        record.status = 'Extraction Failed'
        record.save()
        return

    if not record.resume_text:
        print("   No text found in resume. Skipping.")
        record.status = 'Extraction Failed'
        record.save()
        return

    # 1.5 ATS FORMAT VALIDATION — reject resumes missing critical sections (Same as original)
    resume_lower = record.resume_text.lower()
    ats_sections_found = 0
    ats_missing = []

    # Check for Contact Info (email or phone pattern)
    has_contact = bool(
        re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', record.resume_text) or
        re.search(r'[\+]?[\d\s\-\(\)]{7,15}', record.resume_text)
    )
    if has_contact:
        ats_sections_found += 1
    else:
        ats_missing.append('Contact Info')

    # Check for Experience section
    has_experience = bool(re.search(
        r'\b(experience|work\s*history|employment|professional\s*background|work\s*experience|career\s*history|positions?\s*held)\b',
        resume_lower
    ))
    if has_experience:
        ats_sections_found += 1
    else:
        ats_missing.append('Experience')

    # Check for Education section
    has_education = bool(re.search(
        r'\b(education|academic|qualification|degree|university|college|bachelor|master|b\.?tech|m\.?tech|b\.?e\b|m\.?e\b|b\.?sc|m\.?sc|diploma|school)\b',
        resume_lower
    ))
    if has_education:
        ats_sections_found += 1
    else:
        ats_missing.append('Education')

    # Check for Skills section
    has_skills = bool(re.search(
        r'\b(skills|technical\s*skills|core\s*competenc|proficienc|technologies|tools|frameworks|languages\s*known|expertise)\b',
        resume_lower
    ))
    if has_skills:
        ats_sections_found += 1
    else:
        ats_missing.append('Skills')

    # Require at least 3 out of 4 ATS sections
    if ats_sections_found < 3:
        print(f"   ❌ ATS Validation Failed — Missing: {', '.join(ats_missing)}")
        record.status = 'Invalid Resume Format'
        record.resume_summary = f"Resume rejected: Missing required ATS sections — {', '.join(ats_missing)}. A valid resume must include at least 3 of: Contact Info, Experience, Education, Skills."
        record.save()
        return
    else:
        print(f"   ✅ ATS Validation Passed ({ats_sections_found}/4 sections found)")

    # 2. AI ANALYSIS (Same prompt and scoring as original Candidate task)
    job_description = record.job_description or "General requirements"
    prompt = f"""
    Act as an expert technical recruiter and interviewer. Analyze the match between the following resume and job description.
    
    RESUME:
    {record.resume_text[:10000]}
    
    JOB DESCRIPTION:
    {job_description}
    
    Sensitivity threshold: {threshold}%
    
    SCORING RULES (Weighted & Professional):
    1. CORE SKILLS (50% weight): For every MUST-HAVE technology mentioned in the JD that is missing, subtract 10-15 points.
    2. SECONDARY SKILLS (15% weight): For minor tools or nice-to-have libraries, subtract only 3-5 points.
    3. EXPERIENCE (20% weight): Evaluate depth of experience and project complexity.
    4. CERTIFICATIONS (15% weight): 
       - Award 10-15 bonus points for certifications that DIRECTLY match the JD role (e.g., Python certification for a Python Developer role).
       - Award 5-8 points for certifications that PARTIALLY match (e.g., HTML/CSS/JS certification for a Full Stack Developer role — relevant but incomplete coverage).
       - Award 0 points for certifications completely unrelated to the JD.
       - If the candidate has NO certifications, do NOT penalize — just award 0 bonus points.
    5. If the candidate has NO relevant industry experience for the role, cap the total score at 50%.
    6. BE CONSISTENT: Identical Resume/JD pairs must result in the same logical evaluation.
    7. OBJECTIVITY: Base the score ONLY on the text in the resume. Do not assume skills.
    
    DEEP SKILL ANALYSIS RULES:
    - Do NOT treat skill keywords at face value. Analyze the DEPTH of each skill based on project descriptions, years of usage, and complexity of work done.
    - A candidate who lists "React" but has only built a to-do app should score LOWER than one who built production-level dashboards.
    - If the JD requires "Full Stack Developer" but the candidate only has frontend skills/certifications, recognize this as a PARTIAL match (not full).
    - Cross-reference certifications against the JD: a "Python PCAP" cert for a "Python Developer" JD is a STRONG match, but a "Google Analytics" cert for the same role is IRRELEVANT.
    
    Please provide:
    1. The candidate's full name (extracted from the resume).
    2. The candidate's contact email (extracted from the resume).
    3. The candidate's phone number (extracted from the resume, or null if not found).
    4. A match percentage (0-100).
    5. A 2-3 sentence summary that EXPLICITLY mentions what core skills are MISSING and whether certifications are relevant.
    
    Format the output strictly as a raw JSON object with keys: "candidate_name", "candidate_email", "candidate_phone", "match_percentage", "summary".
    CRITICAL: You MUST properly escape any internal double quotes inside strings (e.g., use \\" instead of ") to ensure the JSON is perfectly valid and parsable.
    """

    # 3. SAVE RESULTS (Same logic as original Candidate task)
    try:
        match_result = call_groq_with_backoff(prompt=prompt, is_json=True, max_tokens=4096, temperature=0.0)
        if match_result:
            try:
                percentage = int(float(match_result.get('match_percentage', 0)))
            except:
                percentage = 0

            # Extract name, email, phone from resume via AI
            ext_name = match_result.get('candidate_name')
            ext_email = match_result.get('candidate_email')
            ext_phone = match_result.get('candidate_phone')

            is_placeholder_name = not record.full_name or any(p in record.full_name.lower() for p in ['extraction', 'unknown', 'pending'])
            is_placeholder_email = not record.email or any(p in record.email.lower() for p in ['pending', 'extraction', 'unknown'])

            if is_placeholder_name and ext_name and ext_name not in ['null', 'None', 'Extraction Failed']:
                record.full_name = ext_name
            if is_placeholder_email and ext_email and ext_email not in ['null', 'None', 'Extraction Failed', 'pending@example.com']:
                record.email = ext_email
            if ext_phone and ext_phone not in ['null', 'None']:
                record.phone = ext_phone

            record.resume_score = percentage
            record.resume_summary = match_result.get('summary', 'No summary provided by AI.')
            record.status = 'Resume Passed' if percentage >= threshold else 'Resume Failed'
            record.save()
            status_icon = "PASS" if percentage >= threshold else "FAIL"
            print(f"\n   Done! Score: {percentage}% {status_icon}")
        else:
            record.status = 'AI Analysis Failed'
            record.save()
    except Exception as e:
        logger.error(f"AI error for standalone {record.id}: {e}")
        record.status = 'AI Analysis Failed'
        record.save()



@shared_task
def auto_complete_abandoned_interviews_task():
    """
    Periodic task: Auto-complete interviews that were started but abandoned.
    Runs every 30 minutes via Celery Beat.
    
    Finds candidates where:
    - link_opened_at is set (interview was started)
    - status is 'Interview' (still in progress)
    - Time elapsed > interview duration + 30 min buffer
    - completed_at is None (never completed)
    
    Auto-completes them with their current score, marking as Rejected/Hired based on threshold.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    
    # Find all abandoned interviews
    candidates = Candidate.objects.filter(
        link_opened_at__isnull=False,
        completed_at__isnull=True,
        status='Interview',
        is_deleted=False,
    )
    
    completed_count = 0
    
    for candidate in candidates:
        # Get interview duration from automation_settings (default 60 min)
        duration_minutes = 60
        if isinstance(candidate.automation_settings, dict):
            duration_minutes = candidate.automation_settings.get('interview_duration_minutes', 60)
        
        # Add 30 min buffer (grace period for network issues, slow submissions)
        max_elapsed = timedelta(minutes=duration_minutes + 30)
        elapsed = now - candidate.link_opened_at
        
        if elapsed <= max_elapsed:
            continue  # Not expired yet, skip
        
        # Auto-complete this interview
        try:
            # Calculate score percentage
            total_possible = 14 * 10  # Always 140 (14 questions × 10 max score)
            score_percentage = (candidate.score / total_possible * 100) if total_possible > 0 else 0
            
            # Get integrity score
            integrity_score = 100.0
            try:
                if hasattr(candidate, 'integrity') and candidate.integrity:
                    integrity_score = candidate.integrity.integrity_score
            except Exception:
                pass
            
            # Determine final status
            threshold = candidate.interview_pass_threshold if candidate.interview_pass_threshold is not None else 50
            INTEGRITY_THRESHOLD = 75.0
            
            if score_percentage >= threshold and integrity_score >= INTEGRITY_THRESHOLD:
                candidate.status = 'Hired'
            elif score_percentage >= threshold and integrity_score < INTEGRITY_THRESHOLD:
                candidate.status = 'On-Hold'
            else:
                candidate.status = 'Rejected'
            
            candidate.completed_at = now
            candidate.save(update_fields=['status', 'completed_at'])
            
            # Log the auto-completion
            log_automation_event(
                candidate,
                'STATUS_CHANGE',
                'WARNING',
                f"Interview auto-completed (abandoned). Elapsed: {elapsed.total_seconds() / 60:.0f} min "
                f"(limit: {duration_minutes} min + 30 min buffer). "
                f"Score: {score_percentage:.1f}%, Status: {candidate.status}",
                phase='INTERVIEW'
            )
            
            completed_count += 1
            logger.info(
                f"[AutoComplete] Candidate {candidate.id} ({candidate.email}) "
                f"auto-completed after {elapsed.total_seconds() / 60:.0f} min. "
                f"Score: {score_percentage:.1f}%, Status: {candidate.status}"
            )
        except Exception as e:
            logger.error(f"[AutoComplete] Failed for candidate {candidate.id}: {e}")
    
    if completed_count > 0:
        logger.info(f"[AutoComplete] Completed {completed_count} abandoned interview(s).")
    
    return f"Auto-completed {completed_count} abandoned interviews."
