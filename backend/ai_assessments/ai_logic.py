import os
import requests
import logging
import copy
import random
import json
import re
import sys
import time
import groq
from django.conf import settings
from ai_candidates.views import extract_json
from .code_generator import CodeGenerator

logger = logging.getLogger(__name__)

EXPERT_VALIDATOR_PROMPT = """
You are an expert AI Assessment Validator and Fixer.

You will be given AI-generated assessment content in JSON format containing:
- MCQs
- Coding challenges

Your task is to CLEAN, FIX, and STANDARDIZE the content so it is production-ready.

-----------------------------
🔧 TASK REQUIREMENTS
-----------------------------

1. MCQ VALIDATION
- Ensure each question has ONLY ONE correct answer
- Fix incorrect answers
- Remove ambiguous or multiple-correct-answer questions
- Remove duplicate or repeated questions
- Improve clarity of questions and options
- Keep difficulty levels appropriate (Easy | Medium | Hard)

2. CODING CHALLENGE FIXES
For each coding problem:

✅ Input Format
- Convert vague or text-based inputs into structured JSON
- Ensure inputs match the function signature

✅ Test Cases
- Generate EXACTLY 5 test cases:
  1. Empty input
  2. Single element
  3. Edge case
  4. Normal case
  5. Large input

- Each test case MUST include:
  {
    "input": ...,
    "output": ...
  }

- Output must be 100% correct, non-empty, and logically derived.
- Every coding problem MUST have 5 unique cases. No placeholders like 'None' or '[]' for output.

❌ Remove:
- Empty outputs
- Text descriptions as input
- Invalid or non-executable test cases

3. OUTPUT STANDARDIZATION
Return clean JSON in this format:

{
  "mcqs": [
    {
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "answer": "...",
      "difficulty": "Easy|Medium|Hard"
    }
  ],
  "coding_challenges": [
    {
      "title": "...",
      "difficulty": "...",
      "problem_statement": "...",
      "function_name": "...",
      "test_cases": [
        {
          "input": ...,
          "output": ...
        }
      ]
    }
  ]
}

4. STRICT RULES
- Do NOT leave any field empty
- Do NOT return explanations
- Do NOT include invalid JSON
- Ensure everything is executable and testable
- Keep outputs deterministic (no randomness)
"""

EXECUTOR_BASE_URL = os.environ.get("EXECUTOR_BASE_URL", "http://localhost:4000").rstrip("/")

def _call_executor(*, language: str, source_code: str, stdin: str | None, time_limit_ms: int = 5000, memory_mb: int = 256) -> dict:
    """Helper to call the internal code executor."""
    payload = {
        "language": language,
        "source_code": source_code,
        "stdin": stdin or "",
        "time_limit_ms": time_limit_ms,
        "memory_mb": memory_mb,
    }
    try:
        resp = requests.post(f"{EXECUTOR_BASE_URL}/execute", json=payload, timeout=10)
        return resp.json() if resp.status_code == 200 else {"ok": False, "error": f"Executor returned {resp.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _call_groq_with_backoff(groq_client, **kwargs):
    """Wrapper for Groq API calls with exponential backoff for rate limits."""
    max_retries = 5
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            return groq_client.chat.completions.create(**kwargs)
        except (groq.RateLimitError, Exception) as e:
            err_msg = str(e).lower()
            # specifically look for rate limit indicators
            is_rate_limit = "rate_limit_exceeded" in err_msg or "429" in err_msg or "rate limit" in err_msg
            
            if is_rate_limit and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Groq Rate Limit hit. Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            
            # If it's not a rate limit or we're out of retries, re-raise
            logger.error(f"Groq API call failed: {e}")
            raise e

def _normalize_difficulty_label(value, *, default='Medium'):
    if not isinstance(value, str):
        return default
    clean = value.strip().capitalize()
    if clean in ('Easy', 'Medium', 'Hard'):
        return clean
    return default

def _is_raw_data(s):
    """Helper to detect if a string is raw data or a text description."""
    if not isinstance(s, str):
        return True
    s = s.strip()
    if not s:
        return False
    # If it has many spaces, it's likely a description, not raw data (e.g. an array or hex)
    if len(s.split()) > 10:
        return False
    # If it ends with a period and isn't a decimal/filename, it's likely a sentence
    if s.endswith('.') and not re.search(r'\d\.$', s):
        return False
    return True

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

    mcqs = payload.get('mcqs', payload.get('questions', payload.get('multiple_choice', [])))
    coding = payload.get('coding_challenges', payload.get('coding_tasks', []))

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
        
        # Normalize starter_code keys to lowercase
        sc = item.get('starter_code', {})
        if not isinstance(sc, dict):
            sc = {}
        
        # Priority 1: If AI provided function metadata, use our professional CodeGenerator templates
        meta = item.get('function_meta')
        if isinstance(meta, dict) and meta.get('name'):
            func_name = meta.get('name')
            params = meta.get('params', [])
            ret_type = meta.get('return_type', 'void')
            
            # Generate code for all supported non-SQL languages automatically
            for lang in ['python', 'java', 'javascript', 'cpp', 'csharp']:
                sc[lang] = CodeGenerator.generate_starter_code(lang, func_name, params, ret_type)
        
        # Priority 2: Fill in or overwrite with normalized keys from existing sc (like SQL)
        item['starter_code'] = {str(k).lower(): v for k, v in sc.items()}
            
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

    # Shuffle to avoid all labels clustered
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
                "constraints, example_input, example_output, explanation, difficulty, test_cases, "
                "and a function_meta object with keys: name (string), params (list of {name: str, type: str}), "
                "return_type (string). For SQL, also include starter_code with table setup. "
                "Important: Generate EXACTLY 10 test_cases per challenge (1 sample, 9 hidden). "
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
            repair_response = _call_groq_with_backoff(
                groq_client,
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You output JSON only."},
                    {"role": "user", "content": repair_prompt},
                ],
                max_tokens=4096,
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
    blacklist_titles=None,
):
    """Generate coding challenges via dedicated AI-only batched calls."""
    if total_required <= 0:
        return []

    # Add a random salt to ensure diversity across sessions
    salt = str(random.getrandbits(32))
    blacklist = blacklist_titles or []

    desired = list(difficulties or [])
    if len(desired) < total_required:
        desired.extend(['Medium'] * (total_required - len(desired)))
    desired = desired[:total_required]

    generated = []
    idx = 0

    while idx < total_required:
        batch_diffs = desired[idx: idx + batch_size]
        batch_count = len(batch_diffs)

        already_gen_titles = [c.get('title', '') for c in generated]
        avoid_instr = f"\nCRITICAL: DO NOT generate challenges similar to these topics/titles: {already_gen_titles + blacklist}" if (already_gen_titles or blacklist) else ""

        base_prompt = f"""
        Act as an expert technical recruiter and generate coding challenges only.
        Session ID: {salt}
        JOB DESCRIPTION: {job_description}
        REQUIRED SKILLS: {required_skills}

        TASK: Generate EXACTLY {batch_count} coding challenges.
        REQUIRED DIFFICULTIES in order: {batch_diffs}

        CRITICAL INSTRUCTIONS:
        1. COMPETITIVE PROGRAMMING FORMAT: Every challenge MUST be an algorithmic problem solvable with standard data structures.
        2. DATA-CENTRIC INPUTS: The "test_cases" MUST contain ONLY raw machine data. NO sentences. NO stories.
        3. EXAMPLE: If the task is "Caching", the input should be a list of keys like `["user1", "user2"]`, NOT a story about "10 users requesting data".
        4. DIFFICULTY ALIGNMENT: Ensure the complexity of the algorithm correctly matches the requested difficulty ({batch_diffs}).
        5. NO DUPLICATES: {avoid_instr}

        - 5 test_cases: Generate EXACTLY 5 diverse inputs as a list of RAW JSON strings. 
          STRICT RULE: If you use a single English word like "users", "request", or "slow" in the "input" field, the generation will FAIL. 
          ONLY use numbers, arrays, objects, or primitive strings.
        - reference_solution (string): A COMPLETE, standalone Python 3 script.
          CRITICAL: The script MUST read the input from stdin using `json.loads(sys.stdin.read())`.
          CRITICAL: Use standard logic. No external DB/APIs.
        - title / problem_statement / difficulty / constraints / example_input / example_output / explanation.

        - JD-ROOTED: Challenges MUST be specifically rooted in the Job Description and Required Skills above.
        - PROFESSIONAL SCENARIOS: Use real-world, enterprise-level scenarios related to the JD. Avoid generic "Hello World" or "Fibonacci" style problems.
        - LOGICAL CONSISTENCY: Each problem must have clear parameters, edge cases (empty input, null, etc.), and unambiguous expected outputs.
        - Ensure VARIETY: Explore different facets, tools, and technical scenarios mentioned in the JD. Each challenge cover a UNIQUE concept.
        - Avoid DUPLICATION: Do not repeat logic or themes across challenges.{avoid_instr}
        - STDLIB ONLY: DO NOT use external libraries. All solutions MUST use standard libraries only.
        - NO WEB SERVERS: Problems must be ALGORITHMIC, not web server-based.
        - STDIN/STDOUT: All problems must be solvable using standard input/output (stdin/stdout).
        - problem_statement must be algorithmic/logic-based and 100% LANGUAGE-AGNOSTIC for 'Code' challenges.
        - FOR SQL CHALLENGES: The `problem_statement` MUST include a professional table description of the schema.
        - function_meta: {{ name: "string", params: [{{name: "string", type: "string"}}], return_type: "string" }}.
        - For SQL, starter_code MUST ONLY contain valid SQL table setup (CREATE/INSERT). 
        - Return JSON only with root key: coding_challenges.
        """

        batch_data = None
        prompt = base_prompt

        for attempt in range(attempts_per_batch):
            response = _call_groq_with_backoff(
                groq_client,
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You output JSON only."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=4096,
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
            break

        for i, item in enumerate(batch_data):
            item['difficulty'] = _normalize_difficulty_label(batch_diffs[i], default='Medium')

        generated.extend(batch_data)
        idx += batch_count
        
        # Small delay between batches to stay under TPM
        if idx < total_required:
            time.sleep(1)

    return generated[:total_required]

def _generate_execution_verified_test_cases(*, groq_client, challenges, target_count=5):
    """
    Enhances test cases by running a reference solution through the in-process executor.
    This eliminates AI hallucinations by using actual execution results as 'Expected Output'.
    """
    if not challenges:
        return challenges

    verified_challenges = []
    for challenge in challenges:
        if not isinstance(challenge, dict):
            verified_challenges.append(challenge)
            continue

        ref_sol = challenge.get('reference_solution')
        test_cases = challenge.get('test_cases', [])
        
        # If SQL, we still trust AI for now as cross-session setup is complex
        if 'SELECT' in str(challenge.get('problem_statement', '')).upper():
            # Ensure we have the 'output' key (standardize from 'expected_output' if AI hallucinated it)
            for tc in test_cases:
                if 'expected_output' in tc and 'output' not in tc:
                    tc['output'] = tc.pop('expected_output')
            verified_challenges.append(challenge)
            continue

        if not ref_sol:
            # Fallback: Ask AI for reference solution if missing
            title = challenge.get('title')
            prob = challenge.get('problem_statement')
            prompt = f"""
            Provide a COMPLETE, executable Python 3 script for this problem:
            Title: {title}
            Problem: {prob}
            
            The script must:
            1. Import `json` and `sys`.
            2. Read the input using `json.loads(sys.stdin.read())`.
            3. Compute the result using logic only (NO external DB/API).
            4. Print the final result back as a string or JSON.
            Output the raw code only, no markdown.
            """
            resp = _call_groq_with_backoff(groq_client, model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], temperature=0)
            ref_sol = resp.choices[0].message.content.strip().replace('```python', '').replace('```', '')
            challenge['reference_solution'] = ref_sol

        verified_test_cases = []
        # Use a set to track unique inputs
        unique_inputs = []
        seen_inputs = set()
        
        # Parse test_cases safely. Ensure it's a list.
        if isinstance(test_cases, str):
            # If the AI accidentally returned a stringified list, parse it
            test_cases = extract_json(test_cases) or []
            
        if not isinstance(test_cases, list):
            test_cases = []

        for tc in test_cases:
            # Standardize key
            if 'expected_output' in tc and 'output' not in tc:
                tc['output'] = tc.pop('expected_output')
            
            inp = ""
            if isinstance(tc, dict):
                inp = str(tc.get('input', '')).strip()
            elif isinstance(tc, str):
                inp = tc.strip()
            
            # Skip fragments or too-short inputs, and strictly enforce _is_raw_data
            if inp and len(inp) > 1 and _is_raw_data(inp) and inp not in seen_inputs:
                unique_inputs.append(inp)
                seen_inputs.add(inp)
        
        # If fewer than target_count unique inputs, ask AI for more UNIQUE ones
        if len(unique_inputs) < target_count:
            needed = target_count - len(unique_inputs)
            prompt = f"""
            Generate {needed} additional UNIQUE and DIVERSE test inputs for: {challenge.get('title')}
            Problem: {challenge.get('problem_statement')}
            
            Already have these inputs (DO NOT REPEAT): {list(seen_inputs)}
            
            Format: Return a JSON object with a single key "inputs" containing a list of strings.
            Example: {{"inputs": ["input1", "input2"]}}
            """
            # We REMOVE response_format={"type": "json_object"} here to prevent Groq 400 errors
            # if the content is complex. extract_json will handle it safely.
            resp = _call_groq_with_backoff(groq_client, model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            extra_data = extract_json(resp.choices[0].message.content or "{}")
            extra = extra_data.get('inputs', []) if isinstance(extra_data, dict) else []
            
            for e in extra:
                e_str = str(e).strip()
                if e_str and e_str not in seen_inputs and len(unique_inputs) < target_count:
                    unique_inputs.append(e_str)
                    seen_inputs.add(e_str)

        for inp in unique_inputs[:target_count]:
            # Run through executor
            res = _call_executor(language='python', source_code=ref_sol, stdin=inp)
            if res.get('ok') and res.get('stdout', '').strip():
                verified_test_cases.append({
                    "input": str(inp),
                    "output": str(res.get('stdout', '')).strip(),
                    "verified": True
                })
            else:
                # If executor fails OR returns empty stdout, check if we already have an AI output
                existing_output = tc.get('output') if isinstance(tc, dict) else ""
                if existing_output and len(str(existing_output).strip()) > 0:
                    verified_test_cases.append({
                        "input": str(inp),
                        "output": str(existing_output).strip(),
                        "verified": False,
                        "retained_from_ai": True
                    })
                else:
                    # Fallback to fresh AI derivation if both fail
                    logger.info(f"Execution Verifier: Fresh AI derivation for input: {inp[:20]}")
                    prompt = f"Problem: {challenge.get('title')}\nReference: {ref_sol}\nInput: {inp}\nWhat is the Expected Output? Return only the output string."
                    resp = _call_groq_with_backoff(groq_client, model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                    verified_test_cases.append({
                        "input": str(inp),
                        "output": resp.choices[0].message.content.strip(),
                        "verified": False
                    })

        challenge['test_cases'] = verified_test_cases
        verified_challenges.append(challenge)

    return verified_challenges

def _final_validation_gate(groq_client, challenges, target_count=5):
    """
    Scanning and Repairing phase to ensure every challenge has a full set 
    of 5 non-empty test cases with verified inputs and outputs.
    """
    if not challenges:
        return []

    logger.info(f"Final Gate: Scanning {len(challenges)} challenges for data integrity...")
    high_quality_pool = []

    for challenge in challenges:
        if not isinstance(challenge, dict):
            continue
            
        test_cases = challenge.get('test_cases', [])
        valid_cases = []
        
        # 1. First pass: Filter out definitely broken cases
        for tc in test_cases:
            # Pre-process: harmonize keys
            if 'expected_output' in tc and 'output' not in tc:
                tc['output'] = tc.pop('expected_output')
            
            inp = str(tc.get('input', '')).strip()
            out = str(tc.get('output', '')).strip()
            # Skip fragments or placeholders or non-raw data
            if inp and out and len(inp) > 1 and _is_raw_data(inp) and "placeholder" not in out.lower():
                valid_cases.append(tc)

        # 2. If short on cases, try ONE LAST EMERGENCY REPAIR for just the missing fields
        if len(valid_cases) < target_count:
            needed = target_count - len(valid_cases)
            logger.warning(f"Final Gate: '{challenge.get('title')}' is missing {needed} cases. Attempting emergency repair.")
            
            ref_sol = challenge.get('reference_solution', '')
            prob = challenge.get('problem_statement', '')
            
            # Request specific missing pairs from AI in a very simple format
            repair_prompt = f"""
            The coding challenge '{challenge.get('title')}' is missing valid test cases.
            Problem: {prob}
            
            Provide EXACTLY {needed} more UNIQUE test cases.
            Return ONLY a JSON list of objects: [{{"input": "...", "output": "..."}}, ...]
            Ensure inputs are RAW DATA (no descriptions) and outputs are LOGICALLY CORRECT.
            """
            try:
                resp = _call_groq_with_backoff(groq_client, model="llama-3.1-8b-instant", messages=[{"role": "user", "content": repair_prompt}])
                repaired_data = extract_json(resp.choices[0].message.content or "[]")
                if isinstance(repaired_data, list):
                    for rtc in repaired_data:
                        r_inp = str(rtc.get('input', '')).strip()
                        r_out = str(rtc.get('output', '')).strip()
                        if r_inp and r_out and _is_raw_data(r_inp):
                            valid_cases.append({
                                "input": r_inp,
                                "output": r_out,
                                "verified": False,
                                "repaired": True
                            })
            except Exception as e:
                logger.error(f"Final Gate: Emergency repair failed for '{challenge.get('title')}': {e}")

        # 3. Final decision: Only keep if we have at least 3 valid cases (prefer 5)
        # We allow it to move forward with 3-5 cases to avoid discarding too much,
        # but we prioritize the full 5.
        if len(valid_cases) >= 3:
            challenge['test_cases'] = valid_cases[:target_count]
            high_quality_pool.append(challenge)
            logger.info(f"Final Gate: '{challenge.get('title')}' PASSED with {len(valid_cases)} cases.")
        else:
            logger.error(f"Final Gate: '{challenge.get('title')}' DISCARDED (only {len(valid_cases)} valid cases).")

    return high_quality_pool

def _generate_mcq_pool_ai_only(
    *,
    groq_client,
    job_description,
    required_skills,
    easy_required,
    medium_required,
    hard_required,
    attempts_per_batch=4,
    blacklist_qs=None
):
    """Generate MCQs via dedicated AI-only calls per difficulty to satisfy strict split."""
    # Add a random salt to ensure diversity across sessions
    salt = str(random.getrandbits(32))
    blacklist = blacklist_qs or []

    requirements = [
        ('Easy', max(0, int(easy_required))),
        ('Medium', max(0, int(medium_required))),
        ('Hard', max(0, int(hard_required))),
    ]

    generated = []

    for difficulty, total_count_for_diff in requirements:
        if total_count_for_diff <= 0:
            continue

        idx = 0
        batch_size = 10
        while idx < total_count_for_diff:
            count = min(batch_size, total_count_for_diff - idx)
            
            # Combine current batch and historical blacklist
            combined_blacklist = (blacklist + [q.get('question', '')[:100] for q in generated])
            avoid_instr = f"\nCRITICAL: DO NOT generate questions similar to these topics: {combined_blacklist}" if combined_blacklist else ""

            base_prompt = f"""
            Act as an expert technical recruiter and generate MCQs only.
            Session ID: {salt}
            Job Description: {job_description}
            Required Skills: {required_skills}

            TASK: Generate EXACTLY {count} {difficulty} MCQs.
            Each MCQ object must include keys:
            - question
            - options (list of exactly 4 strings)
            - answer (must match one option exactly)
            - difficulty (must be exactly \"{difficulty}\")

            CRITICAL:
            - JD-ROOTED: Questions MUST be specifically rooted in the Job Description and Required Skills above.
            - Ensure VARIETY: Explore different facets, tools, and scenarios mentioned in the JD. Each question must cover a UNIQUE concept.
            - Avoid DUPLICATION: Do not repeat similar concepts or questions.{avoid_instr}

            Return JSON only with root key: mcqs.
            """

            batch_mcqs = None
            prompt = base_prompt

            for attempt in range(attempts_per_batch):
                response = _call_groq_with_backoff(
                    groq_client,
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You output JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=4096,
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
                # If we fail a batch, break this difficulty loop
                break

            for q in batch_mcqs:
                q['difficulty'] = difficulty
            generated.extend(batch_mcqs)
            idx += count
            
            # Small delay between difficulty batches
            if idx < total_count_for_diff:
                time.sleep(1)

    return generated

def _expert_assessment_refiner(groq_client, raw_content):
    """
    Uses a high-reasoning model to clean, fix, and standardize the generated pool
    according to strict production-ready requirements.
    """
    if not raw_content or (not raw_content.get('mcqs') and not raw_content.get('coding_challenges')):
        return raw_content

    logger.info("Expert Validator: Refinement pass started...")
    
    try:
        # Ensure the input is stringified JSON for the model
        input_json_str = json.dumps(raw_content, indent=2)
        
        # Call Groq with the high-reasoning model (Llama 3.3 70B)
        response = _call_groq_with_backoff(
            groq_client,
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": EXPERT_VALIDATOR_PROMPT},
                {"role": "user", "content": f"INPUT:\n{input_json_str}"}
            ],
            max_tokens=8192,
            temperature=0.1 # Low temperature for consistency
        )
        
        refined_text = response.choices[0].message.content or ""
        refined_data = extract_json(refined_text)
        
        if refined_data and (refined_data.get('mcqs') or refined_data.get('coding_challenges')):
            logger.info("Expert Validator: Refinement SUCCESSFUL.")
            # Re-normalize to ensure standard structure (difficulty labels, etc)
            return _normalize_generated_pool(refined_data)
        
        logger.warning("Expert Validator: AI returned invalid or empty JSON. Falling back to raw content.")
        return raw_content
    except Exception as e:
        logger.error(f"Expert Validator: Refinement FAILED: {e}")
        return raw_content

def pick_random_subset(assessment, pool, seed=None):
    """Randomly selects a subset of questions from the pool based on assessment targets."""
    if not pool:
        return {}
        
    local_random = random.Random(seed) if seed else random.Random()
    subset = {"mcqs": [], "coding_challenges": []}
    
    normalized_pool = _normalize_generated_pool(pool)
    pool_mcqs = list(normalized_pool.get('mcqs', []))
    pool_coding = copy.deepcopy(normalized_pool.get('coding_challenges', []))
    
    # 1. Select MCQs
    target_mcq_count = getattr(assessment, 'mcq_count', 10)
    target_mcqs = [
        ('Easy', getattr(assessment, 'mcq_easy', 0)), 
        ('Medium', getattr(assessment, 'mcq_medium', 0)), 
        ('Hard', getattr(assessment, 'mcq_hard', 0))
    ]
    
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
    
    if len(subset['mcqs']) < target_mcq_count:
        remaining = [q for q in pool_mcqs if id(q) not in selected_mcq_ids]
        needed = target_mcq_count - len(subset['mcqs'])
        if remaining:
            fill = local_random.sample(remaining, min(len(remaining), needed))
            subset['mcqs'].extend(fill)

    # 2. Select Coding Challenges
    target_coding_count = getattr(assessment, 'coding_count', 2)
    targets = getattr(assessment, 'coding_difficulty_list', None) or ['Medium'] * target_coding_count
    
    for diff in targets:
        diff_pool = [c for c in pool_coding if c.get('difficulty') == diff]
        if not diff_pool and pool_coding:
            diff_pool = list(pool_coding)
        if diff_pool:
            choice = local_random.choice(diff_pool)
            subset['coding_challenges'].append(choice)
            if choice in pool_coding:
                pool_coding.remove(choice)
    
    if len(subset['coding_challenges']) < target_coding_count:
        needed = target_coding_count - len(subset['coding_challenges'])
        if pool_coding:
            fill = local_random.sample(pool_coding, min(len(pool_coding), needed))
            subset['coding_challenges'].extend(fill)

    local_random.shuffle(subset['mcqs'])
    return subset
