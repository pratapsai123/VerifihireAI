import os
import uuid
import json
import random
import logging
import traceback
import copy
from datetime import datetime, timedelta
from groq import Groq
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
import uuid
from .models import Assessment, AIAssessmentSubmission, AIAssessmentIntegrityScreenshot
from ai_candidates.views import extract_json
import traceback
import base64
from django.core.files.base import ContentFile
from api.models import UserProfile, DeletionRequest
from api.views._imports import _is_application_admin_email, handle_deletion_request


def _normalize_difficulty_label(value, *, default='Medium'):
    if not isinstance(value, str):
        return default
    clean = value.strip().capitalize()
    if clean in ('Easy', 'Medium', 'Hard'):
        return clean
    return default


def _normalize_generated_pool(payload):
    """Normalize model output into a stable structure used by frontend/backend."""
    if not isinstance(payload, dict):
        return {"mcqs": [], "coding_challenges": []}

    # Unwrap nested wrappers like {"assessment": {"mcqs": [...], ...}}
    if 'mcqs' not in payload and 'coding_challenges' not in payload and 'coding_tasks' not in payload:
        for val in payload.values():
            if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val or 'coding_tasks' in val):
                payload = val
                break

    mcqs = payload.get('mcqs', [])
    coding = payload.get('coding_challenges', []) or payload.get('coding_tasks', [])

    if not isinstance(mcqs, list):
        mcqs = []
    if not isinstance(coding, list):
        coding = []

    normalized_mcqs = []
    for q in mcqs:
        if not isinstance(q, dict):
            continue
        item = copy.deepcopy(q)
        item['difficulty'] = _normalize_difficulty_label(item.get('difficulty'), default='Medium')
        normalized_mcqs.append(item)

    normalized_coding = []
    for c in coding:
        if not isinstance(c, dict):
            continue
        item = copy.deepcopy(c)
        item['difficulty'] = _normalize_difficulty_label(item.get('difficulty'), default='Medium')
        normalized_coding.append(item)

    return {
        "mcqs": normalized_mcqs,
        "coding_challenges": normalized_coding,
    }


def _mcq_difficulty_counts(mcqs):
    easy = 0
    medium = 0
    hard = 0
    for q in mcqs:
        diff = _normalize_difficulty_label(q.get('difficulty'), default='Medium')
        if diff == 'Easy':
            easy += 1
        elif diff == 'Medium':
            medium += 1
        elif diff == 'Hard':
            hard += 1
    return easy, medium, hard


def _rebalance_mcq_difficulties(mcqs, *, easy_required, medium_required, hard_required):
    """Reassign difficulty labels on AI-generated MCQs to satisfy required split exactly."""
    target_total = int(easy_required) + int(medium_required) + int(hard_required)
    if target_total <= 0:
        return []

    pool = [copy.deepcopy(q) for q in (mcqs or []) if isinstance(q, dict)]
    if len(pool) < target_total:
        return pool

    labels = (['Easy'] * int(easy_required)) + (['Medium'] * int(medium_required)) + (['Hard'] * int(hard_required))

    # Shuffle to avoid all labels clustered while keeping deterministic behavior for same input size.
    random.shuffle(pool)

    balanced = pool[:target_total]
    for idx, q in enumerate(balanced):
        q['difficulty'] = labels[idx]
    return balanced


def _repair_pool_shortfall(
    *,
    groq_client,
    job_description,
    required_skills,
    pool,
    pool_easy,
    pool_medium,
    pool_hard,
    pool_coding_total,
    coding_tasks,
    max_attempts=5,
):
    """Top up missing MCQ/coding items when model under-generates in initial pass."""
    repaired = _normalize_generated_pool(pool)

    for attempt in range(max_attempts):
        easy_count, medium_count, hard_count = _mcq_difficulty_counts(repaired.get('mcqs', []))
        current_coding = len(repaired.get('coding_challenges', []))

        missing_easy = max(0, pool_easy - easy_count)
        missing_medium = max(0, pool_medium - medium_count)
        missing_hard = max(0, pool_hard - hard_count)
        missing_coding = max(0, pool_coding_total - current_coding)

        if (missing_easy + missing_medium + missing_hard + missing_coding) == 0:
            break

        repair_prompt_parts = []

        missing_mcqs = missing_easy + missing_medium + missing_hard
        if missing_mcqs > 0:
            repair_prompt_parts.append(
                "Generate ONLY missing MCQs as JSON objects with keys: "
                "question, options (4), answer, difficulty. "
                f"Required missing MCQs: Easy={missing_easy}, Medium={missing_medium}, Hard={missing_hard}."
            )

        if missing_coding > 0:
            if coding_tasks:
                needed_diffs = [
                    _normalize_difficulty_label(coding_tasks[i % len(coding_tasks)], default='Medium')
                    for i in range(missing_coding)
                ]
            else:
                needed_diffs = ['Medium'] * missing_coding
            repair_prompt_parts.append(
                "Generate ONLY missing coding challenges. "
                f"Required missing coding count={missing_coding}, difficulties={needed_diffs}. "
                "Each coding challenge must include: title, problem_statement, input_format, output_format, "
                "constraints, example_input, example_output, explanation, starter_code, difficulty, test_cases. "
                "CRITICAL: Do not return an empty coding_challenges list when missing_coding > 0."
            )

        repair_prompt = f"""
        You are repairing an under-generated technical assessment pool.
        Job Description: {job_description}
        Required Skills: {required_skills}

        {" ".join(repair_prompt_parts)}

        Return ONLY valid JSON with root keys exactly:
        - mcqs (list)
        - coding_challenges (list)
        Include only newly generated items. Do not repeat previous items.
        """

        try:
            repair_response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Output strict JSON only."},
                    {"role": "user", "content": repair_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            repair_text = repair_response.choices[0].message.content or ""
            repair_data = _normalize_generated_pool(extract_json(repair_text) or {})

            if repair_data.get('mcqs'):
                repaired['mcqs'].extend(repair_data['mcqs'])
            if repair_data.get('coding_challenges'):
                repaired['coding_challenges'].extend(repair_data['coding_challenges'])

        except Exception as repair_err:
            logger.warning(f"Repair attempt {attempt + 1}/{max_attempts} failed: {repair_err}")
            continue

    # Trim to exact pool size after repair.
    target_mcq_total = pool_easy + pool_medium + pool_hard
    repaired['mcqs'] = repaired.get('mcqs', [])[:target_mcq_total]
    repaired['coding_challenges'] = repaired.get('coding_challenges', [])[:pool_coding_total]

    return repaired


def _generate_coding_pool_ai_only(
    *,
    groq_client,
    job_description,
    required_skills,
    difficulties,
    total_required,
    batch_size=2,
    attempts_per_batch=4,
):
    """Generate coding challenges via dedicated AI-only batched calls."""
    if total_required <= 0:
        return []

    desired = list(difficulties or [])
    if len(desired) < total_required:
        desired.extend(['Medium'] * (total_required - len(desired)))
    desired = desired[:total_required]

    generated = []
    idx = 0

    while idx < total_required:
        batch_diffs = desired[idx: idx + batch_size]
        batch_count = len(batch_diffs)

        base_prompt = f"""
        Act as an expert technical recruiter and generate coding challenges only.
        Job Description: {job_description}
        Required Skills: {required_skills}

        TASK: Generate EXACTLY {batch_count} coding challenges.
        Required difficulties in order: {batch_diffs}

        Each challenge object must include keys:
        title, problem_statement, input_format, output_format, constraints,
        example_input, example_output, explanation, starter_code, difficulty, test_cases.

        CRITICAL:
        - problem_statement must be algorithmic/logic-based and language-agnostic.
        - starter_code must be an object with keys: python, java, javascript, cpp, csharp, kotlin, swift, sql.
        - starter_code must be boilerplate only (no solution logic).
        - Generate exactly 10 test_cases per challenge.
        - Return JSON only with root key: coding_challenges.
        """

        batch_data = None
        prompt = base_prompt

        for attempt in range(attempts_per_batch):
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You output valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw = response.choices[0].message.content or ""
            parsed = _normalize_generated_pool(extract_json(raw) or {})
            coding = parsed.get('coding_challenges', [])

            if len(coding) >= batch_count:
                batch_data = coding[:batch_count]
                break

            prompt = (
                base_prompt
                + "\n\nCORRECTION: Previous attempt returned insufficient coding_challenges. "
                + f"Expected {batch_count}, got {len(coding)}. Regenerate and return full count."
            )

        if not batch_data:
            # Stop early; caller will raise with clear count mismatch.
            break

        # Ensure requested difficulty sequence is retained for downstream selection logic.
        for i, item in enumerate(batch_data):
            item['difficulty'] = _normalize_difficulty_label(batch_diffs[i], default='Medium')

        generated.extend(batch_data)
        idx += batch_count

    return generated[:total_required]


def _generate_mcq_pool_ai_only(
    *,
    groq_client,
    job_description,
    required_skills,
    easy_required,
    medium_required,
    hard_required,
    attempts_per_batch=4,
):
    """Generate MCQs via dedicated AI-only calls per difficulty to satisfy strict split."""
    requirements = [
        ('Easy', max(0, int(easy_required))),
        ('Medium', max(0, int(medium_required))),
        ('Hard', max(0, int(hard_required))),
    ]

    generated = []

    for difficulty, count in requirements:
        if count <= 0:
            continue

        base_prompt = f"""
        Act as an expert technical recruiter and generate MCQs only.
        Job Description: {job_description}
        Required Skills: {required_skills}

        TASK: Generate EXACTLY {count} {difficulty} MCQs.
        Each MCQ object must include keys:
        - question
        - options (list of exactly 4 strings)
        - answer (must match one option exactly)
        - difficulty (must be exactly \"{difficulty}\")

        Return JSON only with root key: mcqs.
        """

        batch_mcqs = None
        prompt = base_prompt

        for attempt in range(attempts_per_batch):
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You output valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw = response.choices[0].message.content or ""
            parsed = _normalize_generated_pool(extract_json(raw) or {})
            mcqs = parsed.get('mcqs', [])
            same_diff = [q for q in mcqs if _normalize_difficulty_label(q.get('difficulty')) == difficulty]

            if len(same_diff) >= count:
                batch_mcqs = same_diff[:count]
                break

            prompt = (
                base_prompt
                + "\n\nCORRECTION: Previous attempt had wrong count or difficulty labels. "
                + f"Expected {count} MCQs with difficulty {difficulty}, got {len(same_diff)}. Regenerate correctly."
            )

        if not batch_mcqs:
            break

        for q in batch_mcqs:
            q['difficulty'] = difficulty
        generated.extend(batch_mcqs)

    return generated

def pick_random_subset(assessment, pool, seed=None):
    """Randomly selects a subset of questions from the pool based on assessment targets.
    GUARANTEES: The applicant receives exactly mcq_count MCQs and coding_count coding challenges.
    """
    if not pool:
        return {}
        
    import copy
    local_random = random.Random(seed) if seed else random.Random()
    
    subset = {"mcqs": [], "coding_challenges": []}
    
    normalized_pool = _normalize_generated_pool(pool)
    pool_mcqs = list(normalized_pool.get('mcqs', []))
    pool_coding = copy.deepcopy(normalized_pool.get('coding_challenges', []))
    
    # === 1. Select MCQs by difficulty, then fill up to mcq_count ===
    target_mcq_count = getattr(assessment, 'mcq_count', 10)
    target_mcqs = [
        ('Easy', getattr(assessment, 'mcq_easy', 0)), 
        ('Medium', getattr(assessment, 'mcq_medium', 0)), 
        ('Hard', getattr(assessment, 'mcq_hard', 0))
    ]
    
    # If granular targets sum to 0, distribute the total count evenly
    if sum(t for _, t in target_mcqs) == 0:
        target_mcqs = [
            ('Easy', target_mcq_count // 2),
            ('Medium', (target_mcq_count * 3) // 10),
            ('Hard', max(0, target_mcq_count - target_mcq_count // 2 - (target_mcq_count * 3) // 10))
        ]

    selected_mcq_ids = set()
    
    for diff, target in target_mcqs:
        diff_pool = [q for q in pool_mcqs if q.get('difficulty') == diff and id(q) not in selected_mcq_ids]
        if diff_pool:
            sample_size = min(len(diff_pool), target)
            chosen = local_random.sample(diff_pool, sample_size)
            subset['mcqs'].extend(chosen)
            selected_mcq_ids.update(id(q) for q in chosen)
    
    # FILL-UP: If we still don't have enough MCQs, grab from remaining pool
    if len(subset['mcqs']) < target_mcq_count:
        remaining = [q for q in pool_mcqs if id(q) not in selected_mcq_ids]
        needed = target_mcq_count - len(subset['mcqs'])
        if remaining:
            fill = local_random.sample(remaining, min(len(remaining), needed))
            subset['mcqs'].extend(fill)

    # === 2. Select Coding Challenges, then fill up to coding_count ===
    target_coding_count = getattr(assessment, 'coding_count', 2)
    targets = getattr(assessment, 'coding_difficulty_list', None) or ['Medium'] * target_coding_count
    
    for diff in targets:
        diff_pool = [c for c in pool_coding if c.get('difficulty') == diff]
        if not diff_pool and pool_coding:
            diff_pool = list(pool_coding)  # Fallback: use any remaining
            
        if diff_pool:
            choice = local_random.choice(diff_pool)
            subset['coding_challenges'].append(choice)
            if choice in pool_coding:
                pool_coding.remove(choice)
    
    # FILL-UP: If we still don't have enough coding challenges, grab from remaining pool
    if len(subset['coding_challenges']) < target_coding_count:
        needed = target_coding_count - len(subset['coding_challenges'])
        if pool_coding:
            fill = local_random.sample(pool_coding, min(len(pool_coding), needed))
            subset['coding_challenges'].extend(fill)

    # === 3. Final Shuffle so difficulty isn't ordered ===
    local_random.shuffle(subset['mcqs'])
    
    logger.info(f"pick_random_subset: Selected {len(subset['mcqs'])}/{target_mcq_count} MCQs, {len(subset['coding_challenges'])}/{target_coding_count} Coding")
    
    return subset

logger = logging.getLogger(__name__)
MAX_CODING_TASKS = 50

from api.views import ensure_role_exists

# Configure Groq
# groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
# if not groq_api_key:
#     raise ValueError("GROQ_API_KEY must be set in settings.py")
# groq_client = Groq(api_key=groq_api_key)

class SubmitAssessmentView(APIView):
    def post(self, request):
        data = request.data
        token = data.get('token')
        name = data.get('name')
        email = data.get('email', '').strip().lower()
        answers = data.get('answers', {})
        coding_results = data.get('codingResults', {}) # Captured test case results

        if not token or not name or not email:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assessment = Assessment.objects.get(share_token=token)
            
            # Absolute block against submitting multiple times
            if AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                submitted_at__isnull=False
            ).exists():
                return Response(
                    {"error": "You have already completed this assessment and cannot retake it."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            submission = AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                status='ONGOING'
            ).order_by('-id').first()

            if not submission:
                submission = AIAssessmentSubmission.objects.create(
                    assessment=assessment,
                    candidate_name=name,
                    candidate_email=email,
                    status='ONGOING'
                )

            generated_content = assessment.generated_content or {}
            
            # Unwrap historic nested dictionaries from Llama-3.1
            if 'mcqs' not in generated_content and 'coding_challenges' not in generated_content:
                for key, val in generated_content.items():
                    if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                        generated_content = val
                        break

            generated_content = _normalize_generated_pool(generated_content)
            mcqs = generated_content.get('mcqs', [])
            coding_challenges = generated_content.get('coding_challenges', [])
            
            total_possible_points = assessment.total_points or 0
            possible_mcq_points = 0
            possible_coding_points = 0
            candidate_mcq_points = 0
            candidate_coding_points = 0
            
            # Difficulty weights
            weight_map = {'Easy': 100, 'Medium': 200, 'Hard': 300}

            # 1. MCQ Scoring - Fixed 20 points per question
            for i, mcq in enumerate(mcqs):
                weight = 20
                possible_mcq_points += weight
                
                # Check both 'answer' and 'correct_answer' for robustness
                correct_ans = str(mcq.get('answer') or mcq.get('correct_answer') or '').strip().upper()
                candidate_ans = str(answers.get(f'mcq_{i}') or '').strip().upper()
                
                if correct_ans and candidate_ans == correct_ans:
                    candidate_mcq_points += weight

            # 2. Coding Challenge Scoring
            for i, challenge in enumerate(coding_challenges):
                difficulty = challenge.get('difficulty', 'Medium')
                weight = weight_map.get(difficulty, 200)
                possible_coding_points += weight
                
                res = coding_results.get(str(i))
                if res:
                    passed = res.get('passed', 0)
                    total_tc = res.get('total', 0) # Changed default to 0 for explicit division by zero guard
                    if total_tc > 0: # Guard against division by zero
                        score_fraction = passed / total_tc
                        candidate_coding_points += (score_fraction * weight)

            candidate_total_points = candidate_mcq_points + candidate_coding_points
            
            # Always use the sum of calculated potential points for the denominator
            total_possible_points = possible_mcq_points + possible_coding_points

            if total_possible_points > 0:
                percentage = round((candidate_total_points / total_possible_points) * 100)
            else:
                percentage = 0
            
            pass_status = 'selected' if percentage >= assessment.pass_threshold and submission.integrity_score >= 70 else 'rejected'

            submission.answers = answers
            submission.mcq_score = round(candidate_mcq_points)
            submission.coding_score = round(candidate_coding_points)
            submission.score = round(candidate_total_points)
            submission.total_questions = len(mcqs) + len(coding_challenges)
            submission.percentage = percentage
            submission.status = pass_status
            submission.results_breakdown = {
                "mcq": {"scored": round(candidate_mcq_points), "total": possible_mcq_points},
                "coding": {"scored": round(candidate_coding_points), "total": possible_coding_points},
                "total_possible": total_possible_points
            }
            submission.submitted_at = timezone.now()
            submission.save()

            # After successful save, ensure we return no-cache headers to the submission confirmation
            response_data = {
                "message": "Assessment submitted successfully",
                "submission_id": submission.id,
                "score": submission.score,
                "mcq_score": submission.mcq_score,
                "coding_score": submission.coding_score,
                "total_possible_points": total_possible_points,
                "percentage": percentage,
                "status": pass_status
            }
            response = Response(response_data, status=status.HTTP_200_OK)
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response

        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"SUMBISSION ERROR: {str(e)}\n{traceback.format_exc()}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateAssessmentView(APIView):
    def post(self, request):
        data = request.data
        job_description = data.get('job_description')
        required_skills = data.get('required_skills')
        
        # Robust Question Count Extraction
        # 1. MCQs: Priority to Granular (if they have non-zero sum) > Total count
        input_mcq_total = int(data.get('mcq_count', 0))
        input_easy = int(data.get('mcq_easy', 0))
        input_medium = int(data.get('mcq_medium', 0))
        input_hard = int(data.get('mcq_hard', 0))
        
        granular_sum = input_easy + input_medium + input_hard
        
        if granular_sum > 0:
            mcq_count = granular_sum
            mcq_easy = input_easy
            mcq_medium = input_medium
            mcq_hard = input_hard
        elif input_mcq_total > 0:
            mcq_count = input_mcq_total
            mcq_easy = mcq_count // 2
            mcq_medium = (mcq_count * 3) // 10
            mcq_hard = max(0, mcq_count - mcq_easy - mcq_medium)
        else:
            # Absolute default fallback
            mcq_count = 10
            mcq_easy = 5
            mcq_medium = 3
            mcq_hard = 2

        # 2. Coding Challenges: Priority to Non-Empty coding_tasks > coding_count
        input_coding_count = int(data.get('coding_count', 0))
        input_coding_count = max(0, min(input_coding_count, MAX_CODING_TASKS))
        coding_tasks = data.get('coding_tasks', [])
        
        if isinstance(coding_tasks, str) and coding_tasks:
            try:
                coding_tasks = json.loads(coding_tasks)
            except:
                coding_tasks = []

        if isinstance(coding_tasks, list):
            coding_tasks = coding_tasks[:MAX_CODING_TASKS]

        if isinstance(coding_tasks, list) and len(coding_tasks) > 0:
            coding_count = len(coding_tasks)
        elif input_coding_count > 0:
            coding_count = input_coding_count
            coding_tasks = ['Medium'] * coding_count
        else:
            # Absolute default fallback
            coding_count = 2
            coding_tasks = ['Medium', 'Hard']

        # Log for debugging
        logger.info(f"Generated Assessment Config: MCQs={mcq_count} ({mcq_easy}/{mcq_medium}/{mcq_hard}), Coding={coding_count} ({coding_tasks})")
        
        duration = int(data.get('duration', 60))
        total_possible_points = int(data.get('total_possible_points', 1000))

        if not job_description or not required_skills:
            return Response({
                "error": "Missing job_description or required_skills",
                "message": "Both fields are required to generate an assessment."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Auto-persist role if title is provided
            # required_skills often contains the role title in this app's context
            job_title = data.get('job_title') or data.get('role_title') or required_skills
            if job_title:
                ensure_role_exists(job_title, job_description, user=request.user)
            
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None

            assessment = Assessment.objects.create(
                job_description=job_description,
                required_skills=required_skills,
                mcq_count=mcq_count,
                mcq_easy=mcq_easy,
                mcq_medium=mcq_medium,
                mcq_hard=mcq_hard,
                coding_count=coding_count,
                coding_difficulty_list=coding_tasks,
                duration_minutes=duration,
                total_points=total_possible_points,
                available_from=data.get('available_from'),
                available_until=data.get('available_until'),
                pass_threshold=data.get('pass_threshold', 60),
                company=company
            )

            # Pool multipliers - generate 2x the requested amount for randomization
            pool_easy = mcq_easy * 2
            pool_medium = mcq_medium * 2
            pool_hard = mcq_hard * 2
            pool_mcq_total = pool_easy + pool_medium + pool_hard
            coding_pool_multiplier = 1 if coding_count > 10 else 2
            pool_coding_total = coding_count * coding_pool_multiplier

            # Build a very specific prompt based on the granular breakdown for a POOL
            mcq_prompt = f"TASK 1: Generate a POOL of {pool_mcq_total} Multiple Choice Questions (MCQs).\n"
            mcq_prompt += f"- {pool_easy} Easy questions\n"
            mcq_prompt += f"- {pool_medium} Medium questions\n"
            mcq_prompt += f"- {pool_hard} Hard questions\n"
            mcq_prompt += "MIX the sequence of topics and difficulty levels throughout the list. "
            mcq_prompt += "Each MCQ object must have: 'question', 'options' (list of 4), 'answer', and 'difficulty' (Easy/Medium/Hard)."

            coding_prompt = ""
            keys_expected = '"mcqs"'
            pool_coding_tasks = []
            if coding_count > 0:
                coding_prompt = f"TASK 2: Generate a POOL of {pool_coding_total} Coding Challenges.\n"
                # Duplicate the difficulty list for the pool
                pool_coding_tasks = coding_tasks * coding_pool_multiplier
                for i, diff in enumerate(pool_coding_tasks):
                    coding_prompt += f"- Challenge {i+1}: {diff} difficulty\n"
                
                coding_prompt += (
                    "Each challenge object must have: 'title', 'problem_statement' (detailed), 'input_format', 'output_format', "
                    "'constraints', 'example_input', 'example_output', 'explanation', 'starter_code', 'difficulty', and 'test_cases'.\n"
                )
                coding_prompt += "CRITICAL: The 'problem_statement' MUST BE ALGORITHMIC or LOGIC-BASED (e.g., Array manipulation, String processing, Math, Data Structures). DO NOT generate UI or React-specific questions. All problems must be solvable using standard input/output (stdin/stdout).\n"
                coding_prompt += "CRITICAL: The 'problem_statement' MUST BE LANGUAGE-AGNOSTIC. Do not mention specific language names.\n"
                coding_prompt += "CRITICAL: 'starter_code' MUST be a JSON object mapping these exact keys: python, java, javascript, cpp, csharp, kotlin, swift, sql.\n"
                coding_prompt += "CRITICAL - PROVIDE ONLY BOILERPLATE: The 'starter_code' snippets MUST NOT contain any solution logic. The function body or main block MUST BE EMPTY except for a single line comment like '// TODO: Write logic here'.\n"
                coding_prompt += "CRITICAL: The starter code MUST include all necessary imports and the basic input/output (stdin/stdout) handling logic. The part where the problem is solved MUST BE LEFT BLANK.\n"
                coding_prompt += (
                    "CRITICAL: Generate EXACTLY 10 test_cases for each challenge. "
                    "The first 2 should be 'Sample' cases (provided in the description), and the remaining 8 should be 'Hidden' cases including edge cases (empty inputs, large numbers, boundary conditions).\n"
                )
                coding_prompt += "NOTE: Use '# ' for Python comments and '// ' for Java/C++/JS comments.\n"
                coding_prompt += "CRITICAL: The 'starter_code' dictionary MUST contain valid JSON strings. Escape newlines with \\n and tabs with \\t.\n"
                coding_prompt += (
                    "CRITICAL - TEST CASE FORMAT: Each test_case MUST be an object with \"input\" and \"output\" keys. "
                    "The \"output\" value MUST BE THE RAW RESULT. DO NOT wrap it in literal quotes. DO NOT double-escape characters. "
                    "Example: If the reversed string is 'abc', write \"output\": \"abc\", NOT \"output\": \"\\\"abc\\\"\". "
                    "Ensure test inputs and outputs use standard alphanumeric characters to avoid JSON parsing typos."
                )
                keys_expected = '"mcqs", "coding_challenges"'

            prompt = f"""
            Act as an expert technical recruiter. Create a comprehensive technical assessment.
            Job Description: {job_description}
            Required Skills: {required_skills}
            
            {mcq_prompt}
            
            {coding_prompt}
            
            CRITICAL FORMATTING INSTRUCTION: 
            You MUST return a single JSON object where the root keys are EXACTLY: {keys_expected}.
            DO NOT wrap the output in any outer keys like "assessment" or "data".
            If a key represents 0 requested items, omit it or make it an empty list.
            """

            logger.info(f"Using Groq for Granular Assessment Generation ({total_possible_points} pts)")
            local_api_key = getattr(settings, 'GROQ_API_KEY', None)
            local_groq_client = Groq(api_key=local_api_key)
            
            attempts = 0
            max_attempts = 3
            current_prompt = prompt
            generated_data = {}
            raw_text = ""

            while attempts < max_attempts:
                attempts += 1
                logger.info(f"AI Generation Attempt {attempts}/{max_attempts}")
                
                response = local_groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a professional assessment generator. You MUST output valid JSON only. ALWAYS provide the EXACT counts requested."}, 
                        {"role": "user", "content": current_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1 if attempts == 1 else 0.2
                )
                raw_text = response.choices[0].message.content
                if not raw_text: continue

                generated_data = _normalize_generated_pool(extract_json(raw_text) or {})
                if not generated_data: continue

                # Count Validation
                mcqs = generated_data.get('mcqs', [])
                actual_mcqs = len(mcqs)
                coding = generated_data.get('coding_challenges', [])
                actual_coding = len(coding)
                
                # Check for difficulty distribution sufficiency
                easy_count, medium_count, hard_count = _mcq_difficulty_counts(mcqs)
                
                mcq_satisfied = (actual_mcqs >= pool_mcq_total) and (easy_count >= pool_easy) and (medium_count >= pool_medium) and (hard_count >= pool_hard)
                coding_satisfied = (actual_coding >= pool_coding_total)

                if mcq_satisfied and coding_satisfied:
                    logger.info(f"AI Success on attempt {attempts}: Full pool generated with correct difficulties.")
                    break
                else:
                    # Provide corrective feedback
                    error_msg = f"In the last attempt, you generated {actual_mcqs} MCQs ({easy_count} Easy, {medium_count} Medium, {hard_count} Hard) and {actual_coding} coding challenges. "
                    error_msg += f"I explicitly requested a POOL of {pool_mcq_total} MCQs (Easy:{pool_easy}, Medium:{pool_medium}, Hard:{pool_hard}) and {pool_coding_total} coding challenges. "
                    error_msg += "PLEASE REDO THIS and ensure you provide the full requested quantity and correct 'difficulty' labels for EACH object."
                    current_prompt = prompt + "\n\nCORRECTION FROM PREVIOUS ATTEMPT:\n" + error_msg
                    logger.warning(f"AI under-generated on attempt {attempts}. Retrying with feedback.")

            if not generated_data:
                raise Exception("The AI failed to generate a valid response after multiple attempts.")

            # Normalize/repair missing items so saved content always follows expected keys and counts.
            generated_data = _repair_pool_shortfall(
                groq_client=local_groq_client,
                job_description=job_description,
                required_skills=required_skills,
                pool=generated_data,
                pool_easy=pool_easy,
                pool_medium=pool_medium,
                pool_hard=pool_hard,
                pool_coding_total=pool_coding_total,
                coding_tasks=coding_tasks,
                max_attempts=5,
            )

            # === ENFORCE POOL LIMITS - AI sometimes over-generates ===
            if 'mcqs' in generated_data and len(generated_data['mcqs']) > pool_mcq_total:
                generated_data['mcqs'] = generated_data['mcqs'][:pool_mcq_total]

            if 'coding_challenges' in generated_data and len(generated_data['coding_challenges']) > pool_coding_total:
                generated_data['coding_challenges'] = generated_data['coding_challenges'][:pool_coding_total]

            final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
            final_mcqs = len(generated_data.get('mcqs', []))
            final_coding = len(generated_data.get('coding_challenges', []))

            # AI-only recovery path for coding: when combined prompt under-delivers, generate coding in small dedicated batches.
            if coding_count > 0 and final_coding < pool_coding_total:
                missing = pool_coding_total - final_coding
                remaining_diffs = pool_coding_tasks[final_coding:final_coding + missing] if pool_coding_tasks else (['Medium'] * missing)
                logger.warning(
                    f"Combined prompt under-generated coding ({final_coding}/{pool_coding_total}). "
                    f"Running dedicated coding generation for remaining {missing}."
                )
                extra_coding = _generate_coding_pool_ai_only(
                    groq_client=local_groq_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    difficulties=remaining_diffs,
                    total_required=missing,
                    batch_size=2,
                    attempts_per_batch=4,
                )
                if extra_coding:
                    generated_data['coding_challenges'] = (generated_data.get('coding_challenges', []) + extra_coding)[:pool_coding_total]
                    final_coding = len(generated_data.get('coding_challenges', []))

            # AI-only recovery path for MCQ difficulty split: regenerate dedicated MCQ pool if split is not satisfied.
            if final_mcqs >= pool_mcq_total and (final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):
                logger.warning(
                    f"Combined prompt under-generated MCQ split (got {final_easy}/{final_medium}/{final_hard}, "
                    f"need {pool_easy}/{pool_medium}/{pool_hard}). Running dedicated MCQ generation."
                )
                recovered_mcqs = _generate_mcq_pool_ai_only(
                    groq_client=local_groq_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    easy_required=pool_easy,
                    medium_required=pool_medium,
                    hard_required=pool_hard,
                    attempts_per_batch=4,
                )
                if recovered_mcqs and len(recovered_mcqs) >= pool_mcq_total:
                    generated_data['mcqs'] = recovered_mcqs[:pool_mcq_total]
                    final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
                    final_mcqs = len(generated_data.get('mcqs', []))

            # If MCQ count is enough but labels are still skewed, rebalance labels over AI-generated MCQs.
            if final_mcqs >= pool_mcq_total and (final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard):
                logger.warning(
                    f"Dedicated MCQ generation still skewed (got {final_easy}/{final_medium}/{final_hard}). "
                    "Rebalancing difficulty labels on AI-generated MCQs to match requested split."
                )
                generated_data['mcqs'] = _rebalance_mcq_difficulties(
                    generated_data.get('mcqs', []),
                    easy_required=pool_easy,
                    medium_required=pool_medium,
                    hard_required=pool_hard,
                )
                final_easy, final_medium, final_hard = _mcq_difficulty_counts(generated_data.get('mcqs', []))
                final_mcqs = len(generated_data.get('mcqs', []))

            if final_mcqs < pool_mcq_total or final_coding < pool_coding_total:
                raise Exception(
                    f"AI could not satisfy requested counts. Expected pool MCQs={pool_mcq_total}, coding={pool_coding_total}; "
                    f"got MCQs={final_mcqs}, coding={final_coding}."
                )
            if final_easy < pool_easy or final_medium < pool_medium or final_hard < pool_hard:
                raise Exception(
                    f"AI could not satisfy requested MCQ difficulty split. Expected Easy/Medium/Hard="
                    f"{pool_easy}/{pool_medium}/{pool_hard}; got {final_easy}/{final_medium}/{final_hard}."
                )

            assessment.generated_content = generated_data
            assessment.status = 'SCHEDULED'
            assessment.save()

            return Response({
                "id": assessment.id,
                "message": "Assessment generated successfully",
                "data": generated_data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            tb = traceback.format_exc()
            raw_resp = locals().get('raw_text', 'No response received')
            
            # Log to terminal-like file for easy debugging
            error_log = f"\n[{timezone.now()}] ERROR in GenerateAssessmentView: {str(e)}\n{tb}\nRAW: {raw_resp}\n"
            with open('api_debug.txt', 'a') as f:
                f.write(error_log)
            
            logger.error(f"ERROR in GenerateAssessmentView: {str(e)}\n{tb}\nRAW: {raw_resp}")
            if 'assessment' in locals() and assessment:
                assessment.status = 'FAILED'
                assessment.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateSubmissionView(APIView):
    def post(self, request):
        token = request.data.get('share_token')
        name = request.data.get('candidate_name')
        email = request.data.get('candidate_email', '').strip().lower()

        if not all([token, name, email]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assessment = Assessment.objects.get(share_token=token)
            
            # Availability Guard
            now = timezone.now()
            if assessment.available_from and now < assessment.available_from:
                return Response({"error": "This assessment is not yet available."}, status=status.HTTP_400_BAD_REQUEST)
            if assessment.available_until and now > assessment.available_until:
                return Response({"error": "This assessment has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Prevent re-testing if already completed (case-insensitive check)
            if AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                submitted_at__isnull=False
            ).exists():
                return Response(
                    {"error": "You have already completed this assessment and cannot retake it."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If an ONGOING session exists, reconnect the user instead of spawning a new one
            submission = AIAssessmentSubmission.objects.filter(
                assessment=assessment,
                candidate_email__iexact=email,
                status='ONGOING'
            ).order_by('-id').first()

            if not submission:
                submission = AIAssessmentSubmission.objects.create(
                    assessment=assessment,
                    candidate_name=name,
                    candidate_email=email,
                    status='ONGOING'
                )
                
                # Lock in randomized questions upon first creation
                if not submission.candidate_questions:
                    gen_content = assessment.generated_content or {}
                    if isinstance(gen_content, str):
                        try:
                            gen_content = json.loads(gen_content)
                        except:
                            pass
                    
                    # Unwrap if nested
                    if isinstance(gen_content, dict) and 'mcqs' not in gen_content and 'coding_challenges' not in gen_content:
                        for val in gen_content.values():
                            if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                                gen_content = val
                                break

                    submission.candidate_questions = pick_random_subset(assessment, gen_content, seed=email)
                    submission.save(update_fields=['candidate_questions'])
             
            # Calculate time left
            elapsed = timezone.now() - submission.started_at
            duration_seconds = assessment.duration_minutes * 60
            time_left = max(0, duration_seconds - int(elapsed.total_seconds()))
            
            if time_left <= 0:
                return Response({"error": "Assessment time has expired."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "submission_id": submission.id,
                "status": "success",
                "time_left": time_left,
                "answers": submission.answers,
                "current_question_index": submission.current_question_index,
                "codingResults": (submission.results_breakdown or {}).get('coding_progress', {}),
                "codeDrafts": (submission.results_breakdown or {}).get('code_drafts', {})
            }, status=status.HTTP_201_CREATED)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

class UpdateAssessmentIntegrityView(APIView):
    def post(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
            event_type = request.data.get('event_type')
            
            if event_type == 'tab_switch':
                submission.tab_switches += 1
            elif event_type == 'phone_detection':
                submission.phone_warnings += 1
            elif event_type == 'face_detection_lost':
                submission.face_warnings += 1
            
            # Simple metadata log
            submission.monitoring_logs.append({
                "event": event_type,
                "timestamp": timezone.now().isoformat()
            })
            
            # Grace Warning System Phase 2: Handle First 3 as Warnings
            if len(submission.warning_logs) < 3:
                submission.warning_logs.append(event_type)

            weights = {
                'tab_switch': 10,
                'phone_detection': 30,
                'face_detection_lost': 5
            }

            # Simple penalty system
            total_raw_penalty = (
                submission.tab_switches * weights['tab_switch'] + 
                submission.phone_warnings * weights['phone_detection'] + 
                submission.face_warnings * weights['face_detection_lost']
            )

            # Subtract the "free" penalty from the first 3 warnings
            free_penalty = sum(weights.get(w, 0) for w in submission.warning_logs)

            submission.integrity_score = max(0, 100 - (total_raw_penalty - free_penalty))
            
            # Handle Screenshot
            screenshot_b64 = request.data.get('screenshot')
            webcam_b64 = request.data.get('webcam_screenshot')
            
            if screenshot_b64 or webcam_b64:
                try:
                    integrity_snap = AIAssessmentIntegrityScreenshot(
                        submission=submission,
                        event_type=event_type,
                        timestamp=timezone.now()
                    )
                    
                    if screenshot_b64:
                        if ';' in screenshot_b64 and 'base64,' in screenshot_b64:
                            header, imgstr = screenshot_b64.split(';base64,')
                            ext = header.split('/')[-1]
                        else:
                            imgstr = screenshot_b64
                            ext = 'png'
                        
                        img_data = base64.b64decode(imgstr)
                        fname = f"ai_integrity_{submission.id}_{event_type}_{int(timezone.now().timestamp())}.{ext}"
                        integrity_snap.screenshot.save(fname, ContentFile(img_data), save=False)

                    if webcam_b64:
                        if ';' in webcam_b64 and 'base64,' in webcam_b64:
                            header, imgstr = webcam_b64.split(';base64,')
                            ext = header.split('/')[-1]
                        else:
                            imgstr = webcam_b64
                            ext = 'png'
                        
                        webcam_data = base64.b64decode(imgstr)
                        cname = f"ai_cam_{submission.id}_{event_type}_{int(timezone.now().timestamp())}.{ext}"
                        integrity_snap.webcam_screenshot.save(cname, ContentFile(webcam_data), save=False)

                    integrity_snap.save()

                except Exception as se:
                    logger.error(f"Failed to save AI integrity screenshot: {str(se)}")

            submission.save()
            
            return Response({
                "status": "success",
                "integrity_score": submission.integrity_score
            })
        except AIAssessmentSubmission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

class SaveAssessmentProgressView(APIView):
    def post(self, request, pk):
        try:
            submission = AIAssessmentSubmission.objects.get(pk=pk)
            if submission.submitted_at:
                return Response({"error": "Already submitted"}, status=status.HTTP_400_BAD_REQUEST)
            
            answers = request.data.get('answers')
            index = request.data.get('current_question_index')
            coding_results = request.data.get('codingResults')
            code_drafts = request.data.get('codeDrafts')
            
            if answers is not None:
                submission.answers = answers
            if index is not None:
                submission.current_question_index = index
            
            if not submission.results_breakdown:
                submission.results_breakdown = {}
                
            if coding_results is not None:
                submission.results_breakdown['coding_progress'] = coding_results
            if code_drafts is not None:
                submission.results_breakdown['code_drafts'] = code_drafts
            
            submission.save()
            return Response({"status": "progress saved"})
        except AIAssessmentSubmission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

class AssessmentListView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = getattr(request.user, 'profile', None)
        company = user_profile.company if user_profile else None
        
        if not company:
            return Response([], status=status.HTTP_200_OK)

        assessments = Assessment.objects.filter(company=company, is_deleted=False).order_by('-created_at')
        data = []
        for assessment in assessments:
            count = AIAssessmentSubmission.objects.filter(assessment=assessment).count()
            completed_count = AIAssessmentSubmission.objects.filter(assessment=assessment, submitted_at__isnull=False).count()
            # Use available_until as expiry if present, else fallback to 7 days
            if assessment.available_until:
                expiry_at = assessment.available_until
            else:
                expiry_at = assessment.created_at + timedelta(days=7)

            data.append({
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "expiry_at": expiry_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": _normalize_generated_pool(assessment.generated_content or {}),
                "status": assessment.status,
                "share_token": str(assessment.share_token),
                "candidate_count": count,
                "completed_count": completed_count,
                "invited_count": assessment.invited_count,
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None
            })
        return Response(data, status=status.HTTP_200_OK)

class AssessmentDetailView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            assessment = Assessment.objects.get(pk=pk, company=company)
            submissions = AIAssessmentSubmission.objects.filter(assessment=assessment).order_by('-submitted_at')
            
            submission_data = []
            for sub in submissions:
                submission_data.append({
                    "id": sub.id,
                    "candidate_name": sub.candidate_name,
                    "candidate_email": sub.candidate_email,
                    "score": sub.score,
                    "mcq_score": sub.mcq_score,
                    "coding_score": sub.coding_score,
                    "results_breakdown": sub.results_breakdown,
                    "total_questions": sub.total_questions,
                    "percentage": sub.percentage,
                    "status": sub.status,
                    "integrity_score": sub.integrity_score,
                    "answers": sub.answers,
                    "submitted_at": sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else "In Progress"
                })

            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "difficulty_level": assessment.difficulty_level,
                "total_points": assessment.total_points,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": _normalize_generated_pool(assessment.generated_content or {}),
                "status": assessment.status,
                "share_token": str(assessment.share_token),
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None,
                "submissions": submission_data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            user_profile = getattr(request.user, 'profile', None)
            if not user_profile or not user_profile.company:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            
            assessment = Assessment.objects.get(pk=pk, company=user_profile.company)
            
            # Use centralized helper to handle policy and workflow
            response, handled = handle_deletion_request(
                user_profile=user_profile,
                company=user_profile.company,
                content_type='Assessment',
                object_id=assessment.id,
                object_repr=f"AI Assessment: {assessment.required_skills}",
                reason=request.data.get('reason')
            )
            
            if handled:
                return response

            assessment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Assessment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def pick_random_subset(self, assessment, pool):
        return pick_random_subset(assessment, pool)

class PublicAssessmentView(APIView):
    def get(self, request, token):
        with open('api_debug.txt', 'a') as f:
            f.write(f"\n[{timezone.now()}] PUBLIC ACCESS: Token='{token}'\n")
            f.write(f"Query Params: {request.query_params}\n")
            f.write(f"Host: {request.get_host()}\n")

        try:
            assessment = Assessment.objects.get(share_token=token)
            gen_content = assessment.generated_content or {}
            
            # Robust extraction: Handle if it's a string or nested dict
            if isinstance(gen_content, str):
                import json
                try:
                    gen_content = json.loads(gen_content)
                except:
                    pass

            # Unwrap if it's a wrapper dict (like {"technical_assessment": {...}})
            if isinstance(gen_content, dict):
                # If it doesn't have the main keys but has a nested dict that does, unwrap it
                if 'mcqs' not in gen_content and 'coding_challenges' not in gen_content:
                    for val in gen_content.values():
                        if isinstance(val, dict) and ('mcqs' in val or 'coding_challenges' in val):
                            gen_content = val
                            break
            # Second pass: if it's still a string (nested string), try one more parse
            if isinstance(gen_content, str):
                try:
                    gen_content = json.loads(gen_content)
                except:
                    pass

            # 1. Handle Candidate-Specific Randomized Content
            email_param = request.query_params.get('email', '').strip().lower()
            name_param = request.query_params.get('name', '').strip()
            
            gen_content = _normalize_generated_pool(gen_content)
            final_content = gen_content
            already_completed = False
            
            if email_param:
                from .models import AIAssessmentSubmission
                import random

                # Check for existing submission
                submission = AIAssessmentSubmission.objects.filter(
                    assessment=assessment,
                    candidate_email__iexact=email_param
                ).first()

                if submission:
                    already_completed = submission.submitted_at is not None
                    # If we already have locked-in questions, use them
                    if submission.candidate_questions:
                        final_content = submission.candidate_questions
                    else:
                        # Case: Submission exists but no questions locked yet (e.g. legacy/error)
                        # Pick a subset now and lock it
                        final_content = pick_random_subset(assessment, gen_content, seed=email_param)
                        submission.candidate_questions = final_content
                        submission.save(update_fields=['candidate_questions'])
                else:
                    # No submission yet, but we have an email. 
                    # We can pick the set now so it's consistent even before they "start"
                    final_content = pick_random_subset(assessment, gen_content, seed=email_param)
                    # We don't create the submission here to keep CreateSubmissionView as the source of truth for "Starting"
                    # However, we need to ensure CreateSubmissionView also locks it in or reuses this logic.
                    # BETTER: Always use a helper to get/create consistent set.

            data = {
                "id": assessment.id,
                "job_description": assessment.job_description,
                "required_skills": assessment.required_skills,
                "mcq_count": assessment.mcq_count,
                "coding_count": assessment.coding_count,
                "duration_minutes": assessment.duration_minutes,
                "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
                "generated_content": final_content,
                "status": assessment.status,
                "already_completed": already_completed,
                "available_from": assessment.available_from.isoformat() if assessment.available_from else None,
                "available_until": assessment.available_until.isoformat() if assessment.available_until else None
            }
            response = Response(data, status=status.HTTP_200_OK)
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response
        except Assessment.DoesNotExist:
            logger.error(f"PublicAssessmentView: Assessment not found for token {token}")
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
             logger.error(f"PublicAssessmentView Error: {str(e)}\n{traceback.format_exc()}")
             return Response({"error": "Invalid token or data structure"}, status=status.HTTP_400_BAD_REQUEST)
class InviteAssessmentCandidatesView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def post(self, request):
        assessment_id = request.data.get('assessment_id')
        try:
            user_profile = getattr(request.user, 'profile', None)
            company = user_profile.company if user_profile else None
            
            assessment = Assessment.objects.get(pk=assessment_id, company=company)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

        invite_type = request.data.get('type')  # 'individual' or 'bulk'
        invited_candidates = []
        
        import urllib.parse
        # Use frontend base URL from settings - Standardized to localhost for dev
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        base_link = f"{base_url}/take-ai-assessment/{assessment.share_token}"

        if invite_type == 'individual':
            name = request.data.get('name')
            email = request.data.get('email')
            if not name or not email:
                return Response({"error": "Name and Email are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Append name and email
            encoded_name = urllib.parse.quote(name)
            encoded_email = urllib.parse.quote(email)
            link = f"{base_link}?name={encoded_name}&email={encoded_email}"
            
            # Increment invited count
            assessment.invited_count += 1
            assessment.save(update_fields=['invited_count'])
            
            invited_candidates.append({"name": name, "email": email, "link": link})
            
            # Send Email
            try:
                subject = f"Invite to AI Technical Assessment: {assessment.required_skills}"
                
                # Format availability dates in local time
                start_time = timezone.localtime(assessment.available_from).strftime('%B %d, %Y at %I:%M %p') if assessment.available_from else "Immediately"
                end_time = timezone.localtime(assessment.available_until).strftime('%B %d, %Y at %I:%M %p') if assessment.available_until else "No fixed deadline"
                
                jd_preview = (assessment.job_description or '')[:200]
                
                # Plain text fallback
                message = f"Dear {name},\n\nYou have been invited to attempt an AI technical assessment for the role of {assessment.required_skills}.\n\nTiming Details:\n- Available From: {start_time}\n- Available Until: {end_time}\n- Duration: {assessment.duration_minutes} minutes\n\nPlease click the link below to start your assessment during the availability window:\n{link}\n\nBest of luck!"
                
                # HTML version
                html_message = f"""
                <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                    <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">Assessment Invitation</h1>
                    </div>
                    <div style="padding: 32px; background-color: white;">
                        <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{name}</strong>,</p>
                        <p style="line-height: 1.6; margin-bottom: 24px;">You have been invited to attempt an AI technical assessment for the role: <br/><strong>{assessment.required_skills}</strong></p>
                        
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                            <h3 style="margin-top: 0; color: #4318FF; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>
                            <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {start_time}</p>
                            <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {end_time}</p>
                            <p style="margin: 8px 0; font-size: 14px;"><strong>⏱️ Duration:</strong> {assessment.duration_minutes} minutes</p>
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
                
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False, html_message=html_message)
                logger.info(f"Individual invite sent to {email}")
            except Exception as e:
                import traceback
                logger.error(f"Email error for {email}: {str(e)}")
                logger.error(traceback.format_exc())
                return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        elif invite_type == 'bulk':
            file = request.FILES.get('file')
            if not file:
                return Response({"error": "File is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                import pandas as pd
                if file.name.lower().endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                df.columns = df.columns.str.lower().str.strip()
                if 'name' not in df.columns or 'email' not in df.columns:
                    return Response({"error": "File must have 'name' and 'email' columns"}, status=status.HTTP_400_BAD_REQUEST)

                assessment.invited_count += len(df)
                assessment.save(update_fields=['invited_count'])

                for _, row in df.iterrows():
                    name = str(row['name']).strip()
                    email = str(row['email']).strip()
                    
                    encoded_name = urllib.parse.quote(name)
                    encoded_email = urllib.parse.quote(email)
                    link = f"{base_link}?name={encoded_name}&email={encoded_email}"
                    
                    invited_candidates.append({"name": name, "email": email, "link": link})
                    
                    try:
                        subject = f"Invite to AI Technical Assessment: {assessment.required_skills}"
                        
                        start_time = timezone.localtime(assessment.available_from).strftime('%B %d, %Y at %I:%M %p') if assessment.available_from else "Immediately"
                        end_time = timezone.localtime(assessment.available_until).strftime('%B %d, %Y at %I:%M %p') if assessment.available_until else "No fixed deadline"

                        message = f"Dear {name},\n\nYou have been invited to attempt an AI technical assessment for the role: {assessment.required_skills}.\n\nTiming Details:\n- Available From: {start_time}\n- Available Until: {end_time}\n- Duration: {assessment.duration_minutes} minutes\n\nLink: {link}\n\nGood luck!"
                        
                        html_message = f"""
                        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
                            <div style="background-color: #4318FF; padding: 24px; text-align: center;">
                                <h1 style="color: white; margin: 0; font-size: 24px;">Assessment Invitation</h1>
                            </div>
                            <div style="padding: 32px; background-color: white;">
                                <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{name}</strong>,</p>
                                <p style="line-height: 1.6; margin-bottom: 24px;">You have been invited to attempt an AI technical assessment for the role: <br/><strong>{assessment.required_skills}</strong></p>
                                
                                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                                    <h3 style="margin-top: 0; color: #4318FF; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Timing Details</h3>
                                    <p style="margin: 8px 0; font-size: 14px;"><strong>📅 Available From:</strong> {start_time}</p>
                                    <p style="margin: 8px 0; font-size: 14px;"><strong>⌛ Available Until:</strong> {end_time}</p>
                                    <p style="margin: 8px 0; font-size: 14px;"><strong>⏱️ Duration:</strong> {assessment.duration_minutes} minutes</p>
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

                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False, html_message=html_message)
                        logger.info(f"Bulk invite sent to {email}")
                    except Exception as mail_err:
                        logger.error(f"Bulk email error for {email}: {mail_err}")
            except Exception as e:
                return Response({"error": f"Error parsing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": f"Successfully invited {len(invited_candidates)} candidates",
            "count": len(invited_candidates)
        }, status=status.HTTP_200_OK)
import requests

from rest_framework.permissions import AllowAny

class ProxyCodeExecuteView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        try:
            language = request.data.get('language')
            files = request.data.get('files', [])
            stdin = request.data.get('stdin', '')
            if stdin is None or (isinstance(stdin, str) and stdin.strip().lower() in ["none", "null"]):
                stdin = ""
            code = files[0]['content'] if files else ''
            
            # Get executor URL from environment or fallback to localhost:4000
            executor_base_url = os.environ.get("EXECUTOR_BASE_URL", "http://localhost:4000").rstrip("/")
            
            # Prepare payload for internal executor
            payload = {
                "language": language,
                "source_code": code,
                "stdin": stdin,
                "time_limit_ms": 30000,
                "memory_mb": 2048,
            }

            # Special handling for SQL (default to sqlite for AI assessments)
            if language == 'sql':
                payload["database_engine"] = "sqlite"

            # Call internal executor
            response = requests.post(f"{executor_base_url}/execute", json=payload, timeout=120)
            result = response.json()

            if not result.get('ok'):
                return Response({
                    "run": {
                        "stdout": "",
                        "stderr": result.get('error', 'Executor Error'),
                        "code": 1,
                        "output": result.get('error', 'Executor Error')
                    }
                }, status=status.HTTP_200_OK)

            # Map executor response to the format expected by the frontend
            piston_response = {
                "run": {
                    "stdout": result.get('stdout', ''),
                    "stderr": result.get('stderr', ''),
                    "code": result.get('exit_code', 0),
                    "output": result.get('stdout', '') + result.get('stderr', '')
                }
            }

            return Response(piston_response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Code Execution Proxy Error: {str(e)}")
            return Response({
                "run": {
                    "stdout": "",
                    "stderr": f"Execution Error: {str(e)}",
                    "code": 1
                }
            }, status=status.HTTP_200_OK)

class AIAssessmentSubmissionDetailView(generics.RetrieveDestroyAPIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_profile = getattr(self.request.user, 'profile', None)
        company = user_profile.company if user_profile and user_profile.company else None
        if not company:
            return AIAssessmentSubmission.objects.none()
        return AIAssessmentSubmission.objects.filter(assessment__company=company, is_deleted=False)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.company:
            return super().destroy(request, *args, **kwargs)

        instance = self.get_object()
        
        # Use centralized helper to handle policy and workflow
        response, handled = handle_deletion_request(
            user_profile=user_profile,
            company=user_profile.company,
            content_type='AIAssessmentSubmission',
            object_id=instance.id,
            object_repr=f"AI Submission for {instance.candidate_email}",
            reason=request.data.get('reason')
        )
        
        if handled:
            return response

        return self.destroy(request, *args, **kwargs)
