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

def _is_raw_data(s):
    """
    Helper to detect if a string is raw test data (numbers, simple text)
    vs a descriptive fragment or complex JSON/Code snippet.
    """
    if not s:
        return False
    s_clean = str(s).lower().strip()
    
    # Strictly reject code assignments, brackets, or braces
    if "=" in s_clean or "{" in s_clean or "[" in s_clean or "}" in s_clean or "]" in s_clean:
        return False
        
    # If it's a single number or word, it's likely raw
    if s_clean.isdigit() or len(s_clean.split()) == 1:
        return True
        
    # If it has ":" or descriptive keywords, it's likely a description
    if ":" in s_clean or "input:" in s_clean:
        return False
        
    return True

class InputDataGenerator:
    """
    Backend-native random data generator for coding challenges.
    Generates plain-text strings perfectly formatted for CP-style stdin.
    """
    @staticmethod
    def generate(schema):
        if not isinstance(schema, list):
            return str(schema) if schema else ""
        
        output_parts = []
        context = {} # Tracks generated values for size_ref
        
        # SAFETY CAPS for test case generation - STRICTION ENFORCEMENT
        MAX_COUNT = 30 # Reduced from 50
        MAX_INT = 1000
        MAX_STR_LEN = 32
        
        TOTAL_CHAR_LIMIT = 300 # Global hard cap as requested by user

        for i, block in enumerate(schema):
            # Check global limit before each block
            current_total = len('\n'.join(p for p in output_parts if p))
            if current_total > TOTAL_CHAR_LIMIT:
                break

            b_type = block.get('type', 'int')
            b_name = block.get('name', f"var_{i}")
            
            val = None
            if b_type == 'int':
                # Enforce reasonable ranges for test cases
                low = block.get('min', 1)
                high = block.get('max', 100)
                high = min(high, MAX_INT)
                val = random.randint(low, high)
                output_parts.append(str(val))
            elif b_type == 'float':
                low = block.get('min', 0.0)
                high = block.get('max', 100.0)
                high = min(high, MAX_INT)
                val = round(random.uniform(low, high), block.get('precision', 2))
                output_parts.append(str(val))
            elif b_type == 'string':
                # Use professional terms even for individual strings to make them "meaningful"
                prof_terms = ["algorithm", "backend", "client", "database", "encryption", "frontend", "gateway", "handler", "interface", "json", "token", "query", "user", "server", "active", "sync", "auth"]
                chars = block.get('chars', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                length = block.get('length', random.randint(8, 20))
                length = max(1, min(length, MAX_STR_LEN))
                
                # If using default alphabets, use a professional word or a clean identifier
                if "abcdefg" in chars.lower():
                    prefixes = ["USER", "TASK", "REQ", "ITEM", "DATA", "LOG", "MSG", "KEY", "TOKEN", "ID", "VAL"]
                    if random.random() > 0.5:
                        val = f"{random.choice(prefixes)}-{random.randint(100, 999)}"
                    else:
                        val = random.choice(prof_terms)
                    val = val[:length]
                else:
                    val = ''.join(random.choice(chars) for _ in range(length))
                output_parts.append(val)
            elif b_type == 'array':
                # Determine count
                count = block.get('count', 5)
                count_ref = block.get('count_ref')
                if count_ref in context:
                    count = context[count_ref]
                
                # SAFETY CAP on array size
                count = min(int(count), MAX_COUNT)

                items = []
                sub = block.get('item', {"type": "int", "min": 1, "max": 100})
                for _ in range(max(0, count)):
                    if sub['type'] == 'int':
                        items.append(str(random.randint(sub.get('min', 1), min(sub.get('max', 100), MAX_INT))))
                    elif sub['type'] == 'string':
                        # Use professional terms for array items too
                        prof_terms = ["node", "link", "value", "task", "job", "status", "port", "host"]
                        if random.random() > 0.3:
                            items.append(random.choice(prof_terms))
                        else:
                            items.append(f"item_{random.randint(10, 99)}")
                
                val = items # Storing as list in context, but string in output
                output_parts.append(' '.join(items))
            elif b_type == 'matrix':
                rows = block.get('rows', 3)
                cols = block.get('cols', 3)
                rows_ref = block.get('rows_ref')
                if rows_ref in context: rows = context[rows_ref]
                
                # SAFETY CAP on matrix dimensions
                rows = min(int(rows), MAX_COUNT)
                cols = min(int(cols), 8) # Reduced from 10 for safety

                matrix_lines = []
                sub = block.get('item', {"type": "int", "min": 0, "max": 1})
                for _ in range(max(0, rows)):
                    row_items = []
                    for _ in range(max(0, cols)):
                        if sub['type'] == 'int':
                            row_items.append(str(random.randint(sub.get('min', 0), min(sub.get('max', 1), MAX_INT))))
                        elif sub['type'] == 'string':
                            row_items.append(f"val_{random.randint(10, 99)}")
                    matrix_lines.append(' '.join(row_items))
                val = matrix_lines
                output_parts.append('\n'.join(matrix_lines))
            
            elif b_type == 'raw':
                # Generate a paragraph of text
                # Professional, technical, and common terms for "sensible" inputs
                words = [
                    "algorithm", "backend", "client", "database", "encryption", "frontend", "gateway", "handler", "interface", "json",
                    "kernel", "latency", "metadata", "network", "object", "password", "query", "runtime", "server", "token",
                    "user", "version", "webhook", "xml", "yield", "zero", "active", "binary", "cache", "debugger",
                    "error", "feature", "git", "host", "internal", "job", "key", "link", "memory", "node",
                    "output", "process", "rest", "schema", "task", "unit", "value", "worker", "async", "block"
                ]
                # Cap raw word count - RE-TIGHTENED for user limit
                word_count = min(block.get('count', 10), 20) 
                val = ' '.join(random.choice(words) for _ in range(word_count))
                output_parts.append(val)
            
            context[b_name] = val
            
        final_output = '\n'.join(p for p in output_parts if p)
        # FINAL HARD TRUNCATION to 300 chars
        if len(final_output) > TOTAL_CHAR_LIMIT:
            final_output = final_output[:TOTAL_CHAR_LIMIT].rsplit(' ', 1)[0]
            
        return final_output

EXPERT_VALIDATOR_PROMPT = """
You are an expert AI Assessment Validator and Fixer.

You will be given AI-generated assessment content in JSON format.
Your task is to CLEAN, FIX, and STANDARDIZE the content so it is production-ready.

🔧 TASK REQUIREMENTS:
1. MCQ VALIDATION: One correct answer, no duplicates, clear language.
2. CODING CHALLENGE FIXES:
    - Convert vague inputs into pure competitive-programming RAW TEXT formats (numbers and strings separated by spaces).
    - PURGE ALL JSON: If the problem input contains dictionaries `{}`, lists `[]`, or quotes, you MUST completely rewrite the problem to use simple space/newline separated text instead.
- 2. SCHEMA GENERATION:
    - For each coding challenge, you MUST provide an `input_generator_schema` list.
    - This schema is for generating 5 small random test cases to VALIDATE logic.
    - SCHEMA LIMITS: Even if the problem constraints are large (e.g. N=10^5), the schema MUST use small values (e.g. max 50) so generation and execution are fast.
    - SUPPORTED TYPES: 
      - `{"type": "int", "name": "var_name", "min": 1, "max": 50}` (Use small max for test cases)
      - `{"type": "float", "name": "price", "min": 0, "max": 100, "precision": 2}`
      - `{"type": "string", "name": "token", "length": 16}` (Length MUST be 1-32 characters)
      - `{"type": "raw", "name": "text_block", "count": 10}` (Paragraph of ~10 words)
      - `{"type": "array", "name": "arr", "count_ref": "var_name", "item": {"type": "int"}}`
    - TYPE SEPARATION: If the question requires numbers, use `int` or `float`. If it requires words/alphabets, use `string`. Do NOT mix them.
      - `{"type": "matrix", "name": "grid", "rows_ref": "N", "cols": 10, "item": {"type": "int"}}`
    - DATA FLATTENING EXAMPLE:
      - BEFORE: `students = [{"name": "Alice", "score": 90 }, {"name": "Bob", "score": 80 }]`
      - AFTER (SCHEMA): `[{"type": "int", "name": "N", "min": 1, "max": 5}, {"type": "array", "name": "students", "count_ref": "N", "item": {"type": "string"}}, {"type": "array", "name": "scores", "count_ref": "N", "item": {"type": "int"}}]`
    - Generate EXACTLY 5 test cases per challenge.
    - EXAMPLES: The problem description MUST contain EXACTLY ONE example input/output pair.
    - CRITICAL: No variable names or JSON in the actual inputs. The backend generator handles that.
3. LOGIC & METADATA check:
   - Ensure the `reference_solution` perfectly matches the `input_generator_schema`.
   - The solution MUST read the exact types and counts defined in the schema.
   - FUNCTION METADATA: You MUST provide a correct `function_meta` object for every challenge.
     Format: `{"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "arr", "type": "int[]"}], "return_type": "string"}`
     This metadata is USED to generate starter code for candidates. Ensure the types match the schema.

4. STRICT RULES:
- JSON ESCAPING OVERRIDE: You MUST properly escape all internal double quotes (`\"`) and newlines (`\n`) inside string values! Returning unescaped double quotes inside a JSON string value will cause a syntax error (e.g. `Expecting ',' delimiter`).
- Return ONLY valid JSON in the requested schema.
- No explanations. No placeholders.
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
        # Increase timeout to 300 seconds (5 minutes) to allow for full LLVM compilation of heavy languages like Swift.
        resp = requests.post(f"{EXECUTOR_BASE_URL}/execute", json=payload, timeout=300)
        if resp.status_code == 200:
            return resp.json()
        error_msg = f"Executor returned {resp.status_code}"
        logger.error(error_msg)
        return {"ok": False, "error": error_msg}
    except Exception as e:
        error_msg = str(e)
        # Detailed failure logging specifically for timeouts or crashes
        try:
            with open('api_debug.txt', 'a') as f:
                ts = time.strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"\n[{ts}] EXECUTOR FAILURE: {error_msg}\nPAYLOAD: {json.dumps(payload, indent=2)}\n")
        except:
            pass
        logger.error(f"Executor exception: {error_msg}")
        return {"ok": False, "error": error_msg}

def _call_groq_with_backoff(groq_client, **kwargs):
    """Wrapper for Groq API calls with exponential backoff for rate limits and connection resets."""
    max_retries = 5
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            return groq_client.chat.completions.create(**kwargs)
        except groq.RateLimitError as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Groq Rate Limit hit. Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            raise e
        except (groq.APIConnectionError, groq.APITimeoutError) as e:
            # This handles the specific 'Connection error' the user is seeing.
            if attempt < max_retries - 1:
                delay = base_delay + attempt # Linear-ish escape for connections
                logger.warning(f"Groq Connection Error: {e}. Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            raise e
        except Exception as e:
            err_msg = str(e).lower()
            if "status_code=503" in err_msg or "overloaded" in err_msg:
                if attempt < max_retries - 1:
                    time.sleep(base_delay)
                    continue
            
            logger.error(f"Groq API call failed: {e}")
            raise e

def _normalize_difficulty_label(value, *, default='Medium'):
    if not isinstance(value, str):
        return default
    clean = value.strip().capitalize()
    if clean in ('Easy', 'Medium', 'Hard'):
        return clean
    return default

def _audit_signature(prob_desc: str, tc_input: str) -> bool:
    """
    Checks if a test case input likely contains all required arguments 
    based on keywords in the problem description.
    """
    desc = prob_desc.lower()
    inp = str(tc_input).lower()
    
    # Check for Sliding Window / k-based parameters
    if any(k in desc for k in ["window", "size k", "integer k", "value k", "length k"]):
        # If 'k' is mentioned, we expect at least two distinct numbers or a number and an array
        # This is a heuristic to prevent inputs that are just [1,2,3] when k is needed.
        if "k" not in inp and not re.search(r'\d.*\d', inp):
             return False

    # Check for Target/Sum parameters
    if any(k in desc for k in ["target", "sum as", "total of"]):
        if not re.search(r'\d.*\d', inp): # Expect at least two numbers (array + target)
            return False
            
    return True

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

def _inject_example_into_statement(statement, input_data, output_data):
    """
    Synchronizes the problem statement text with the actual generated test case.
    Replaces static examples with the verified backend-generated pattern.
    Forces ONLY ONE example by removing any extra AI-generated ones.
    """
    if not statement:
        return statement
        
    s = str(statement)
    
    # 1. Patterns for identifying Example sections
    # We want to keep anything before the first "Example" block, then inject ours, then discard other examples.
    
    # Check for "Example 2" or "Example 2:" or "Example 2: "
    extra_examples_regex = re.compile(r'\n+(?:Example\s+)?2:?.*', re.DOTALL | re.IGNORECASE)
    s = extra_examples_regex.sub('', s) # Cut off anything from "Example 2" onwards

    input_regex = re.compile(r'(?:Example\s+)?Input:?.*?(?=(?:Example\s+)?(?:Expected\s+)?Output:?|$)', re.DOTALL | re.IGNORECASE)
    output_regex = re.compile(r'(?:Example\s+)?(?:Expected\s+)?Output:?.*?(?=\n+(?:Example\s+)?2|$)', re.DOTALL | re.IGNORECASE)
    
    # Format with Markdown Code Blocks for clarity
    new_input_block = f"\nExample Input:\n```\n{input_data}\n```\n"
    new_output_block = f"Expected Output:\n```\n{output_data}\n```"
    
    # Replace the FIRST Input found
    if input_regex.search(s):
        s = input_regex.sub(new_input_block, s, count=1)
    else:
        s += f"\n\n{new_input_block}"
        
    # Replace the FIRST Output found
    if output_regex.search(s):
        s = output_regex.sub(new_output_block, s, count=1)
    else:
        s += f"\n{new_output_block}"
        
    return s.strip()

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
        
        # Ensure test cases are normalized to 'test_cases'
        tc = item.get('test_cases', item.get('testcases', item.get('cases', [])))
        if not isinstance(tc, list):
            tc = []
        item['test_cases'] = tc
        
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
    model="llama-3.1-8b-instant"
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
                "Each coding challenge must include: title, problem_statement, difficulty, reference_solution, "
                "input_generator_schema (e.g. [{\"type\": \"int\", \"name\": \"N\", \"min\": 1, \"max\": 10}, {\"type\": \"array\", \"count_ref\": \"N\", \"item\": {\"type\": \"int\"}}]), "
                "and a function_meta object with keys: name (string), params (list of {name: str, type: str}), "
                "return_type (string). No SQL or database problems allowed. "
                "CRITICAL: Do NOT generate `example_input` or `test_cases`. The backend will generate them from the `input_generator_schema`.\n"
            )

        repair_prompt = f"""
        You are repairing an under-generated technical assessment pool.
        Job Description: {job_description}
        Required Skills: {required_skills}

        {" ".join(repair_prompt_parts)}

        CRITICAL OVERRIDE:
        - JSON ESCAPING: You MUST properly escape all internal double quotes (`\\"`) and newlines (`\\n`) inside string values! Returning unescaped double quotes inside a JSON string value will cause a syntax error.

        Return ONLY valid JSON with root keys exactly:
        - mcqs (list)
        - coding_challenges (list)
        Include only newly generated items. Do not repeat previous items.
        """

        try:
            repair_response = _call_groq_with_backoff(
                groq_client,
                model=model,
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
    batch_size=1, # Reduced from 2 for better reliability in large 70b outputs
    attempts_per_batch=4,
    blacklist_titles=None,
    model="llama-3.1-8b-instant" # Switched from 70b for rate-limit stability
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
        You are a coding question generator for an AI assessment platform.
        Session ID: {salt}
        JOB DESCRIPTION: {job_description}
        REQUIRED SKILLS: {required_skills}

        Your task is to generate HIGH-QUALITY coding problems strictly following the format below.
        Generate EXACTLY {batch_count} coding challenge(s).
        REQUIRED DIFFICULTIES in order: {batch_diffs}

        {avoid_instr}

        --------------------------------------
        DIFFICULTY RULES (MANDATORY)

        Easy:
        - Basic logic (loops, conditions)
        - Small constraints (n <= 1000)
        - Brute force acceptable

        Medium:
        - Requires optimization (HashMap, sorting, sliding window)
        - Constraints up to n <= 10^5
        - Brute force should NOT pass all cases

        Hard:
        - Advanced algorithms (DP, Graph, Backtracking)
        - Large constraints (n <= 10^6 or complex states)
        - Requires deep problem-solving

        --------------------------------------
        OUTPUT FORMAT (STRICT)

        You MUST return a JSON object with a root key "coding_challenges" containing an array of EXACTLY {batch_count} problem objects.
        Each problem object MUST have these exact keys:

        "title": "<Short and clear problem name>"
        "difficulty": "<Easy / Medium / Hard>"
        "topic": "<Array / String / Hashing / DP / Graph / etc>"
        "problem_statement": "<Clear and precise description. Avoid ambiguity. Keep it logical and easy to understand.>"
        "constraints": "<Define constraints based on difficulty level (e.g. n <= 10^5)>"
        "input_generator_schema": [ {{"type": "int", "name": "N", "min": 1, "max": 50}}, {{"type": "array", "count_ref": "N", "item": {{"type": "int"}}}} ]
        "explanation": "<Clear step-by-step explanation>"
        CRITICAL: Schema values MUST be small (max 50) for fast test execution, even if `constraints` are large.
        CRITICAL: Input strings MUST be 1-32 characters long. Use correct types: numbers as `int`, alphabets as `string`.
        "reference_solution": "<A COMPLETE, standalone Python 3 script. MUST read the raw text input from stdin using `sys.stdin.read()` or `input()`, and print the raw text output. Use standard logic. No external DB/APIs. STDLIB ONLY. MUST properly escape newlines and quotes.>"
        "function_meta": {{ "name": "function_name", "params": [{{"name": "param_name", "type": "string"}}], "return_type": "string" }}

        --------------------------------------
        STRICT INSTRUCTIONS:
        - JSON ESCAPING OVERRIDE: You MUST properly escape all internal double quotes (`\\"`) and newlines (`\\n`) inside string values! Returning unescaped double quotes inside a JSON string value will cause a syntax error (e.g. `Expecting ',' delimiter`). 
        - Do NOT skip any section
        - Ensure problem is logically correct and solvable
        - Ensure examples match the problem perfectly
        - EXACTLY ONE EXAMPLE: Provide only one example input/output pair in the problem description.
        - Do NOT include test cases
        - STRICT CP-STYLE INPUT: The text in `example_input` MUST NOT contain JSON, curly braces `{{}}`, array brackets `[]`, or string quotes. It MUST be pure competitive-programming raw text (only spaces, numbers, plain letters, and newlines). No key-value pairs or dictionaries.
        - COMPLEX DATA HANDLING: If the problem scenario involves complex entities (like "Users", "ML Models", "Products"), you MUST flatten the input into parallel arrays or 2D matrices of integers/strings. NEVER use dictionaries to represent them.
        - DATA FLATTENING EXAMPLE:
          - BEFORE: `students = [{{ "name": "Alice", "score": 90 }}, {{ "name": "Bob", "score": 80 }}]`
          - AFTER (CORRECT): `2\nAlice 90\nBob 80` (where 2 is the count, followed by space-separated attributes)
        - JD-ROOTED: Challenges MUST be specifically rooted in the Job Description and Required Skills above.
        - PROFESSIONAL SCENARIOS: Use real-world, enterprise-level scenarios related to the JD. Avoid generic "Hello World" or "Fibonacci" style problems.
        - NO WEB SERVERS OR DATABASES: Problems must be purely ALGORITHMIC (e.g., arrays, data structures, math). Never generate questions about building APIs, REST endpoints, JSON parsing, database schemas, or SQL.
        - STDIN/STDOUT: All problems must be solvable using standard input/output (stdin/stdout).
        - Return JSON only. No markdown formatting outside of JSON strings.
        """

        batch_data = None
        prompt = base_prompt

        for attempt in range(attempts_per_batch):
            response = _call_groq_with_backoff(
                groq_client,
                model=model,
                messages=[
                    {"role": "system", "content": "You are a creative technical assessment architect. You output JSON only. Avoid repetitive logic at all costs."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=4096,
                temperature=0.8, # Increased from 0.2 for much higher variety
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
                + f"Expected {batch_count}, got {len(coding)}. Regenerate and return full count. ENSURE VARIETY."
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

def _verify_reference_solutions(*, groq_client, challenges, model="llama-3.1-8b-instant"):
    """
    Simplified verification: runs each challenge's reference_solution with its
    example_input through the executor. If the solution runs without errors,
    the challenge is kept. If it fails, AI is asked to fix the solution (up to 2 retries).
    No test cases are generated — only the question + working answer.
    """
    if not challenges:
        return challenges

    verified = []
    for challenge in challenges:
        if not isinstance(challenge, dict):
            continue

        title = challenge.get('title', 'Unknown')
        ref_sol = challenge.get('reference_solution', '')
        example_input = str(challenge.get('example_input', '')).strip()

        # SQL challenges: skip execution verification
        if 'SELECT' in str(challenge.get('problem_statement', '')).upper():
            challenge['test_cases'] = []  # no test cases
            verified.append(challenge)
            logger.info(f"Verify: '{title}' is SQL — skipped execution check.")
            continue

        # If no reference solution, ask AI to generate one
        if not ref_sol:
            prob = challenge.get('problem_statement', '')
            prompt = f"""
            Provide a COMPLETE, executable Python 3 script for this problem:
            Title: {title}
            Problem: {prob}

            The script must:
            1. Import `sys`.
            2. Read the RAW TEXT input from stdin using `sys.stdin.read()` or `input()`.
            3. Compute the result using logic only (NO external DB/API).
            4. Print the final RAW TEXT result to stdout using `print()`.
            Output the raw code only, no markdown.
            """
            try:
                resp = _call_groq_with_backoff(groq_client, model=model, messages=[{"role": "user", "content": prompt}], temperature=0)
                ref_sol = resp.choices[0].message.content.strip().replace('```python', '').replace('```', '')
                challenge['reference_solution'] = ref_sol
            except Exception as e:
                logger.error(f"Verify: Failed to generate reference solution for '{title}': {e}")
                continue

        # Try running the reference solution
        # If example_input is "N/A" (placeholder), generate a real one from schema first
        current_input = str(example_input).strip()
        schema = challenge.get('input_generator_schema')
        
        if (current_input == "N/A" or not current_input) and schema:
            try:
                current_input = InputDataGenerator.generate(schema)
                challenge['example_input'] = current_input # Early sync for verification
                logger.info(f"Verify: Generated early input for '{title}' from schema.")
            except: pass

        solution_works = False
        max_fix_attempts = 2

        for attempt in range(max_fix_attempts + 1):
            if not ref_sol.strip():
                break

            res = _call_executor(language='python', source_code=ref_sol, stdin=current_input)
            stdout = str(res.get('stdout', '')).strip()
            stderr = str(res.get('stderr', '')).strip()

            if res.get('ok') and stdout is not None and not stderr:
                solution_works = True
                # CRITICAL: Overwrite AI hallucinated expected output with ACTUAL execution result!
                challenge['example_output'] = stdout
                logger.info(f"Verify: '{title}' reference solution PASSED (attempt {attempt + 1}). Output: {stdout[:50]}")
                break
            else:
                error_info = stderr or res.get('error', 'Unknown error')
                logger.warning(f"Verify: '{title}' reference solution FAILED (attempt {attempt + 1}): {error_info[:100]}")

                if attempt < max_fix_attempts:
                    # Ask AI to fix the solution
                    fix_prompt = f"""
                    The following Python 3 solution has an error. Fix it.
                    
                    Problem: {challenge.get('problem_statement', '')}
                    Example Input: {example_input}
                    
                    Current Code:
                    {ref_sol}
                    
                    Error:
                    {error_info[:500]}
                    
                    Return ONLY the fixed Python code. No markdown, no explanation.
                    The script MUST read RAW TEXT input from stdin and print RAW TEXT output to stdout using `print()`. Do NOT use json parsing on stdin unless explicitly required by the problem.
                    MUST properly escape newlines and internal quotes.
                    """
                    try:
                        fix_resp = _call_groq_with_backoff(groq_client, model=model, messages=[{"role": "user", "content": fix_prompt}], temperature=0)
                        ref_sol = fix_resp.choices[0].message.content.strip().replace('```python', '').replace('```', '')
                        challenge['reference_solution'] = ref_sol
                    except:
                        break

        if solution_works:
            # Generate 5 unique test cases based on the schema
            test_cases = []
            for tc_idx in range(5):
                tc_input = InputDataGenerator.generate(schema)
                # Run the reference solution on this new input
                tc_res = _call_executor(language='python', source_code=ref_sol, stdin=tc_input)
                tc_output = str(tc_res.get('stdout', '')).strip()
                
                if tc_res.get('ok') and tc_output:
                    test_cases.append({
                        "id": f"tc_{tc_idx+1}",
                        "input": tc_input,
                        "expected_output": tc_output,
                        "is_hidden": tc_idx > 0 # First one is public
                    })
            
            challenge['test_cases'] = test_cases
            
            # Sync function_meta with the verified solution
            import re
            func_match = re.search(r'def\s+(\w+)\s*\(([^)]*)\)', ref_sol)
            if func_match:
                func_name = func_match.group(1)
                raw_params = func_match.group(2).strip()
                param_names = [p.strip().split(':')[0].strip().split('=')[0].strip() for p in raw_params.split(',')]
                params = [{'name': p, 'type': 'any'} for p in param_names if p]
                
                challenge['function_meta'] = {'name': func_name, 'params': params, 'return_type': 'any'}
                
                starter_code = {}
                for lang in ['python', 'java', 'javascript', 'cpp', 'csharp']:
                    starter_code[lang] = CodeGenerator.generate_starter_code(lang, func_name, params, 'any')
                challenge['starter_code'] = starter_code
            
            # ONLY add to verified list if it has working test cases and a valid example output
            if len(test_cases) > 0 and challenge.get('example_output') != "N/A":
                verified.append(challenge)
            else:
                logger.error(f"Verify: '{title}' DISCARDED — produced N/A or empty test cases.")
        else:
            logger.error(f"Verify: '{title}' DISCARDED — reference solution could not be fixed.")

    return verified

def _generate_execution_verified_test_cases(*, groq_client, challenges, target_count=5, model="llama-3.1-8b-instant"):
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
        
        # No longer handling SQL specially since we banned it
        if 'SELECT ' in str(challenge.get('problem_statement', '')).upper():
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
            1. Read RAW TEXT input using `sys.stdin.read()` or `input()`.
            2. Compute the result using logic only (NO external DB/API).
            3. Print the final result back as RAW TEXT using `print()`. Do NOT output JSON.
            CRITICAL: Use standard Python 3. Output the raw code only, no markdown.
            """
            resp = _call_groq_with_backoff(groq_client, model=model, messages=[{"role": "user", "content": prompt}], temperature=0)
            ref_sol = resp.choices[0].message.content.strip().replace('```python', '').replace('```', '')
            challenge['reference_solution'] = ref_sol

        unique_inputs = []
        schema = challenge.get('input_generator_schema')
        title = challenge.get('title', 'Unknown')
        
        with open('gen_debug.txt', 'a', encoding='utf-8') as f_log:
            f_log.write(f"\n--- DEBUG: Generating cases for '{title}' ---\n")
            f_log.write(f"Schema: {schema}\n")

            # Generate 6 inputs (1 for Example, 5 for Hidden)
            if schema and isinstance(schema, list):
                logger.info(f"Generating 6 test cases for '{title}' using Backend Engine.")
                for idx_g in range(6):
                    try:
                        new_inp = InputDataGenerator.generate(schema)
                        unique_inputs.append(new_inp)
                        # Fix SyntaxError: move backslash out of f-string
                        formatted_inp = str(new_inp).replace('\n', ' [NL] ')
                        f_log.write(f"Generated Input {idx_g}: {formatted_inp}\n")
                    except Exception as e:
                        logger.error(f"Input Generation Error: {e}")
                        f_log.write(f"Gen Error {idx_g}: {e}\n")
        
            # FALLBACK: If schema generation failed or was empty, try to scavenge AI's example_input first
            if not unique_inputs:
                f_log.write("WARNING: No schema found. Attempting legacy scavenge.\n")
                ai_ex = challenge.get('example_input')
                if ai_ex and ai_ex != "N/A" and _is_raw_data(ai_ex):
                    unique_inputs.append(ai_ex)
                    f_log.write(f"Scavenged Example: {ai_ex}\n")
                
                test_cases = challenge.get('test_cases', [])
                if isinstance(test_cases, str): test_cases = extract_json(test_cases) or []
                for tc in test_cases:
                    inp = str(tc.get('input', '')).strip() if isinstance(tc, dict) else str(tc).strip()
                    if inp and _is_raw_data(inp) and inp not in unique_inputs:
                        unique_inputs.append(inp)
            
            # We need at least 1 input to proceed
            if not unique_inputs:
                logger.warning(f"No inputs generated for '{title}'. Skipping execution verification.")
                verified_challenges.append(challenge)
                f_log.write("FAILED: No inputs found at all.\n")
                continue

            verified_test_cases = []
            for i, inp in enumerate(unique_inputs):
                # Run through executor
                res = _call_executor(language='python', source_code=ref_sol, stdin=inp)
                actual_stdout = str(res.get('stdout', '')).strip()
                
                if res.get('ok') and actual_stdout:
                    tc_obj = {
                        "input": str(inp),
                        "output": actual_stdout,
                        "verified": True
                    }
                    verified_test_cases.append(tc_obj)
                    
                    # If this is the FIRST successful execution, synchronize it into the Example fields
                    # Ensure we overwrite "N/A"
                    if i == 0 or challenge.get('example_input') == "N/A" or not challenge.get('example_input'):
                        challenge['example_input'] = str(inp)
                        challenge['example_output'] = actual_stdout
                        
                        # DYNAMIC INJECTION: Sync the textual problem statement with the first test case
                        old_statement = challenge.get('problem_statement', '')
                        challenge['problem_statement'] = _inject_example_into_statement(old_statement, str(inp), actual_stdout)
                        
                        logger.info(f"Sync: Updated Example Input/Output and Problem Statement for '{title}' from Backend Execution.")
                        f_log.write(f"SYNC SUCCESS for input {i}\n")
                else:
                    err_msg = res.get('error', 'Empty Stdout')
                    logger.warning(f"Execution Verifier: Failure for input {i} on '{title}': {err_msg}")
                    f_log.write(f"EXEC FAILURE for input {i}: {err_msg}\n")

            challenge['test_cases'] = verified_test_cases
            verified_challenges.append(challenge)

    return verified_challenges

def _final_validation_gate(groq_client, challenges, target_count=6, model="llama-3.1-8b-instant"):
    """
    The ultimate logic check.
    1. Audits input signatures (e.g. is 'k' missing?).
    2. Performs 'Double-Blind' AI verification for EVERY test case.
    3. Rescues failing challenges up to 2 times.
    4. Discards challenges that can't meet strict accuracy bars.
    """
    if not challenges:
        return []

    high_quality_pool = []
    
    for challenge in challenges:
        if not isinstance(challenge, dict):
            continue

        prob_title = challenge.get('title', 'Unknown')
        prob_desc = challenge.get('problem_statement', '')
        test_cases = challenge.get('test_cases', [])
        valid_cases = []
        
        logger.info(f"Final Gate: Auditing logic for '{prob_title}'...")

        # 1. DOUBLE-BLIND VERIFICATION for initial cases
        for tc in test_cases:
            if not isinstance(tc, dict): continue
            
            # Harmonize keys
            if 'expected_output' in tc and 'output' not in tc:
                tc['output'] = tc.pop('expected_output')
            
            inp = str(tc.get('input', '')).strip()
            out = str(tc.get('output', '')).strip()
            
            # Basic Quality + Signature Audit
            if not (inp and out and len(inp) > 1 and _is_raw_data(inp)):
                continue
            
            if not _audit_signature(prob_desc, inp):
                logger.warning(f"Final Gate: REJECTED signature for '{prob_title}' (Missing parameters in input: {inp[:30]})")
                continue

            # AI Second Opinion (Double-Blind)
            try:
                check_prompt = f"""
                Problem: {prob_desc}
                Input: {inp}
                Claimed Output: {out}
                
                Is this output mathematically and logically 100% correct for the given input?
                Reply ONLY with 'YES' or 'NO'. No explanation.
                """
                cc_resp = _call_groq_with_backoff(groq_client, model=model, messages=[{"role": "user", "content": check_prompt}], temperature=0)
                decision = cc_resp.choices[0].message.content.strip().upper()
                
                if "YES" in decision:
                    valid_cases.append(tc)
                else:
                    logger.warning(f"Final Gate: REJECTED logic for '{prob_title}' (AI logic mismatch for output: {out[:20]})")
            except Exception as e:
                # If AI check fails, trust prior verification if it exists, else skip
                if tc.get('verified'):
                    valid_cases.append(tc)

        # 2. MANDATORY RESCUE LOOP (Up to 3 Times)
        rescue_attempt = 0
        while len(valid_cases) < target_count and rescue_attempt < 3:
            rescue_attempt += 1
            needed = target_count - len(valid_cases)
            logger.warning(f"Final Gate: '{prob_title}' needs rescue (only {len(valid_cases)} valid cases). Attempt {rescue_attempt}")
            
            rescue_prompt = f"""
            Generate EXACTLY {needed} UNIQUE and ACCURATE test cases.
            CRITICAL: Ensure inputs include ALL parameters mentioned (like 'k', etc.).
            Return ONLY a JSON list: [{{"input": "...", "output": "..."}}]
            """
            try:
                resp = _call_groq_with_backoff(groq_client, model=model, messages=[{"role": "user", "content": rescue_prompt}])
                repaired = extract_json(resp.choices[0].message.content or "[]")
                if isinstance(repaired, list):
                    for rtc in repaired:
                        r_inp = str(rtc.get('input', '')).strip()
                        r_out = str(rtc.get('output', '')).strip()
                        if r_inp and r_out and _is_raw_data(r_inp) and _audit_signature(prob_desc, r_inp):
                            # Verify rescued cases too
                            v_prompt = f"Problem: {prob_desc}\nInput: {r_inp}\nIs Output: {r_out} correct? YES/NO."
                            v_resp = _call_groq_with_backoff(groq_client, model=model, messages=[{"role": "user", "content": v_prompt}], temperature=0)
                            if "YES" in v_resp.choices[0].message.content.strip().upper():
                                valid_cases.append({"input": r_inp, "output": r_out, "rescued": True})
            except: pass

        # 3. Final Decision: STRICT 6 or DISCARD
        if len(valid_cases) >= target_count:
            challenge['test_cases'] = valid_cases[:target_count]
            high_quality_pool.append(challenge)
            logger.info(f"Final Gate: '{prob_title}' PASSED with exactly {target_count} logic-checked cases.")
        else:
            logger.error(f"Final Gate: '{prob_title}' DISCARDED (Only {len(valid_cases)} cases found, need {target_count}).")

    return high_quality_pool
def _generate_mcq_pool_ai_only(
    *,
    groq_client,
    job_description,
    required_skills,
    pool_mcq_total,
    pool_easy,
    pool_medium,
    pool_hard,
    attempts_per_batch=4,
    blacklist_qs=None,
    model="llama-3.1-8b-instant" 
):
    """Generate MCQs via dedicated AI-only calls per difficulty to satisfy strict split."""
    # Add a random salt to ensure diversity across sessions
    salt = str(random.getrandbits(32))
    blacklist = blacklist_qs or []

    requirements = [
        ('Easy', max(0, int(pool_easy))),
        ('Medium', max(0, int(pool_medium))),
        ('Hard', max(0, int(pool_hard))),
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
            - JSON ESCAPING OVERRIDE: You MUST properly escape all internal double quotes (`\\"`) and newlines (`\\n`) inside string values! Returning unescaped double quotes inside a JSON string value will cause a syntax error.
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
                    model=model,
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
            
            # Increased delay to 2s to mitigate Groq Rate Limits (TPM/RPM)
            if idx < total_count_for_diff:
                time.sleep(2)

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
