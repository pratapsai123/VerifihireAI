import logging
import copy
import random
import json
import time
import groq
from django.utils import timezone
from ai_candidates.views import extract_json
from .code_generator import CodeGenerator

logger = logging.getLogger(__name__)

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
                    {"role": "system", "content": "Output strict JSON only."},
                    {"role": "user", "content": repair_prompt},
                ],
                response_format={"type": "json_object"},
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

        already_gen_titles = [c.get('title', '') for c in generated]
        avoid_instr = f"\nCRITICAL: DO NOT generate challenges similar to these topics/titles: {already_gen_titles}" if already_gen_titles else ""

        base_prompt = f"""
        Act as an expert technical recruiter and generate coding challenges only.
        JOB DESCRIPTION: {job_description}
        REQUIRED SKILLS: {required_skills}

        TASK: Generate EXACTLY {batch_count} coding challenges.
        REQUIRED DIFFICULTIES in order: {batch_diffs}

        CRITICAL INSTRUCTIONS:
        1. JD-ROOTED: Every challenge MUST be directly relevant to the tasks and technologies described in the Job Description above.
        2. ENTERPRISE SCENARIOS: Use real-world business scenarios (e.g., "Optimize a logistics route", "Parse financial transaction logs", "Implement a caching layer for a high-traffic API") rather than generic "Reverse a string" problems.
        3. DIFFICULTY ALIGNMENT: Ensure the complexity of the algorithm correctly matches the requested difficulty ({batch_diffs}).
        4. NO DUPLICATES: {avoid_instr}

        Each challenge object must include:
        - title (string): Descriptive and professional.
        - problem_statement (string): Clear, detailed, and JD-relevant.
        - difficulty (string): Must match one of {batch_diffs}.
        - function_meta: {{ name: "string", params: [{{name: "string", type: "string"}}], return_type: "string" }}.
        - example_input/example_output: Sample data.
        - explanation: Why the input results in the output.
        - constraints: List of strings (e.g. ["n <= 10^5"]).
        - 10 test_cases: Exactly 10 (1 sample, 9 hidden).

        - JD-ROOTED: Challenges MUST be specifically rooted in the Job Description and Required Skills above.
        - PROFESSIONAL SCENARIOS: Use real-world, enterprise-level scenarios related to the JD. Avoid generic "Hello World" or "Fibonacci" style problems.
        - LOGICAL CONSISTENCY: Each problem must have clear parameters, edge cases (empty input, null, etc.), and unambiguous expected outputs.
        - Ensure VARIETY: Explore different facets, tools, and technical scenarios mentioned in the JD. Each challenge must cover a UNIQUE concept.
        - Avoid DUPLICATION: Do not repeat logic or themes across challenges.{avoid_instr}
        - STDLIB ONLY: DO NOT use external libraries (e.g., EXPRESS, LODASH, AXIOS, REACT). All solutions MUST use standard libraries only.
        - NO WEB SERVERS: Problems must be ALGORITHMIC, not web server-based.
        - STDIN/STDOUT: All problems must be solvable using standard input/output (stdin/stdout).
        - problem_statement must be algorithmic/logic-based and 100% LANGUAGE-AGNOSTIC for 'Code' challenges.
        - CRITICAL: In the problem_statement for 'Code', DO NOT use terms like "Write a Python function" or "Create a Java class". Use generic terms like "Write a solution" or "Implement a function".
        - FOR SQL CHALLENGES: The `problem_statement` MUST include a professional table description of the schema (mimicking the HackerRank/LeetCode style). 
        - SQL TABLE FORMAT: Inside the `problem_statement`, include an HTML table showing the schema. Example:
          `<h3>STATION</h3><table border="1"><tr><th>Field</th><th>Type</th></tr><tr><td>ID</td><td>NUMBER</td></tr><tr><td>CITY</td><td>VARCHAR2(21)</td></tr></table>`
        - CRITICAL: Ensure the SQL query complexity (e.g. JOINs, Subqueries, Window Functions) strictly matches the requested difficulty ({batch_diffs}).
        - NO PLAGIARISM: Do not copy exact questions from HackerRank/LeetCode. Create original scenarios rooted in the JD ({job_description}).
        - BALANCED MIX: If generating more than one challenge, ensure a mix of types (Code vs SQL) as previously instructed.
        - For 'SQL' challenges, use "Write a SQL query" as these are specific to database environments.
        - function_meta must be an object defined as: {{ name: "string", params: [{{name: "string", type: "string"}}], return_type: "string" }}.
        - For SQL, starter_code MUST ONLY contain valid SQL table setup (CREATE/INSERT). If you include descriptions, they MUST be properly commented out using '--'.
        - For non-SQL languages, you do not need to provide starter_code; the system will generate it from function_meta.
        - Generate exactly 10 test_cases per challenge (1 sample, 9 hidden). 
        - CRITICAL for SQL: test_case `input` MUST be an empty string "". The table schema belongs only in `starter_code`.
        - CRITICAL for SQL: test_case `output` MUST be the final query result (e.g. the rows returned by SELECT), NOT the CREATE TABLE statements.
        - For SQL, example_output and test_case outputs should be the raw string result expected from a standard SQL CLI (no Python formatting, no single quotes unless part of the data).
        - CRITICAL: DO NOT use placeholders like `[...]`, `...`, or `null` (unless literal) in test case outputs. They MUST be the FULL expected string that the program should return.
        - Return JSON only with root key: coding_challenges.
        """

        batch_data = None
        prompt = base_prompt

        for attempt in range(attempts_per_batch):
            response = _call_groq_with_backoff(
                groq_client,
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You output valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
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

def _enhance_coding_challenges_with_test_cases(
    *,
    groq_client,
    challenges,
    target_count=10,
):
    """Adds more test cases to existing coding challenges to reach target_count."""
    if not challenges or not isinstance(challenges, list):
        return challenges

    enhanced = []
    for challenge in challenges:
        if not isinstance(challenge, dict):
            enhanced.append(challenge)
            continue
            
        current_test_cases = challenge.get('test_cases', [])
        current_count = len(current_test_cases)
        
        if current_count >= target_count:
            enhanced.append(challenge)
            continue

        needed = target_count - current_count
        title = challenge.get('title', 'Unknown')
        problem = challenge.get('problem_statement', '')

        prompt = f"""
        You are a technical QA engineer. I have a coding challenge:
        Title: {title}
        Problem: {problem}

        Current Test Cases: {len(current_test_cases)}
        
        TASK: Generate EXACTLY {needed} additional hidden test cases for this challenge. 
        Focus on edge cases: large inputs, boundary values, empty cases, or complex constraints.

        Each test_case MUST be an object with "input" and "output" keys.
        Return ONLY valid JSON with root key: "extra_test_cases" (list).
        """

        try:
            response = _call_groq_with_backoff(
                groq_client,
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Output strict JSON only."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=2048,
                temperature=0.2,
            )
            raw = response.choices[0].message.content or ""
            parsed = extract_json(raw) or {}
            extra = parsed.get('extra_test_cases', [])
            
            if isinstance(extra, list):
                # Sanitize and merge
                new_challenge = copy.deepcopy(challenge)
                new_challenge['test_cases'] = (current_test_cases + extra)[:target_count]
                enhanced.append(new_challenge)
            else:
                enhanced.append(challenge)
        except Exception as e:
            logger.warning(f"Enhancement failed for '{title}': {e}")
            enhanced.append(challenge)

    return enhanced

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

    for difficulty, total_count_for_diff in requirements:
        if total_count_for_diff <= 0:
            continue

        idx = 0
        batch_size = 10
        while idx < total_count_for_diff:
            count = min(batch_size, total_count_for_diff - idx)
            
            already_gen_qs = [q.get('question', '')[:100] + "..." for q in generated]
            avoid_instr = f"\nCRITICAL: DO NOT generate questions similar to these topics: {already_gen_qs}" if already_gen_qs else ""

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
                        {"role": "system", "content": "You output valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
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
