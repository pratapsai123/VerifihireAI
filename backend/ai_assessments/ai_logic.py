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
from django.core.cache import cache
from .code_generator import CodeGenerator
from .coding_skeletons import CodingSkeletons

logger = logging.getLogger(__name__)

class GroqKeyManager:
    _current_index = 0

    @classmethod
    def get_current_key(cls):
        keys = getattr(settings, 'GROQ_API_KEYS', [])
        if not keys:
            # Fallback to the single legacy key if list is missing/empty
            return getattr(settings, 'GROQ_API_KEY', None)
        return keys[cls._current_index % len(keys)]

    @classmethod
    def rotate_key(cls):
        keys = getattr(settings, 'GROQ_API_KEYS', [])
        if keys and len(keys) > 1:
            old_idx = cls._current_index
            cls._current_index = (cls._current_index + 1) % len(keys)
            logger.warning(f"GROQ ROTATION: Rate limit reached at index {old_idx}. Switched to key index {cls._current_index}")
            return True
        return False


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
            
            # 3. ADVANCED REPAIR: Fix unescaped internal quotes
            # This complex regex targets quotes that aren't preceded by {[: or followed by ,:]}
            # Helps solve "Expecting ',' delimiter" errors at line X column Y.
            import re
            
            # A. Fix trailing commas
            json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
            
            # B. Escape internal double quotes that aren't delimiters
            # Look for quotes that are between other word characters or aren't next to structural JSON chars
            # This is a heuristic that works for most descriptive fields
            def escape_internal_quotes(match):
                body = match.group(0)
                # If it's "key": "value", it's likely a delimiter and should stay
                # We target quotes that are surrounded by text
                return body.replace('"', '\\"')

            # Heuristic: Find content between actual delimiters and escape internal quotes
            # But let's start with a simpler one: fix "He said "Hello"" issues
            # We look for a quote preceded by an alphabetical char and followed by an alphabetical char
            json_str = re.sub(r'(?<=[a-zA-Z0-9])"(?=[a-zA-Z0-9])', r'\"', json_str)
            
            try:
                return json.loads(json_str, strict=False)
            except json.JSONDecodeError:
                # If still failing, try one last desperation: remove newlines inside quotes
                # (Some models break strings across lines)
                pass
            
            return json.loads(json_str, strict=False)
    except Exception as e:
        logger.error(f"JSON extraction error in ai_logic: {e}")
    return None

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
1. MCQ VALIDATION: 
   - One correct answer, no duplicates, clear language.
   - CRITICAL: Each option MUST be actual descriptive answer text (NOT just "A", "B", "C", "D", "Option A", "Choice 1", or placeholder letters).
   - The `answer` field MUST contain the complete text of one of the options, NOT just a letter.
   - Example GOOD: {"question": "What is Django?", "options": ["A web framework", "A database", "A testing tool", "A package manager"], "answer": "A web framework"}
   - Example BAD: {"question": "What is Django?", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Option A"}
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
    - Generate EXACTLY 6 test cases per challenge.
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

def _call_groq_with_backoff(groq_client=None, prompt=None, system_msg=None, is_json=True, **kwargs):
    """Wrapper for Groq API calls with exponential backoff, account rotation, and model fallback."""
    max_retries = 10
    base_delay = 5
    
    # 1. Initialize Client if needed
    if groq_client is None:
        key = GroqKeyManager.get_current_key()
        groq_client = groq.Groq(api_key=key, timeout=60.0)
    
    current_client = groq_client
    attempt = 0
    rotations_this_attempt = 0
    keys_count = len(getattr(settings, 'GROQ_API_KEYS', [])) or 1
    
    # Prepare messages
    messages = kwargs.pop('messages', [])
    if not messages and prompt:
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": prompt})

    # Prepare response format
    response_format = kwargs.pop('response_format', None)
    if not response_format and is_json:
        response_format = {"type": "json_object"}

    # 70b -> 8b Fallback tracking
    original_model = kwargs.get('model', 'llama-3.1-8b-instant')
    powerful_model = "llama-3.3-70b-versatile"
    fast_model = "llama-3.1-8b-instant"
    current_model = original_model
    model_fallback_active = False

    while attempt < max_retries:
        # Use the current model (possibly downgraded)
        kwargs['model'] = current_model
        try:
            resp = current_client.chat.completions.create(
                messages=messages,
                response_format=response_format,
                **kwargs
            )
            content = resp.choices[0].message.content
            if is_json:
                from .views import extract_json # circular import? use local or ensure views handled
                # Better to use a non-circular extract_json or just json.loads
                import json
                try:
                    return json.loads(content)
                except:
                    # Fallback to local extract_json if available
                    from ai_candidates.views import extract_json
                    return extract_json(content)
            return content
        except groq.RateLimitError as e:
            # 1. Try rotating to a different account's API key
            if keys_count > 1 and rotations_this_attempt < keys_count:
                if GroqKeyManager.rotate_key():
                    time.sleep(1) # Breathe
                    new_key = GroqKeyManager.get_current_key()
                    timeout = getattr(current_client, '_timeout', 60.0)
                    current_client = groq.Groq(api_key=new_key, timeout=timeout)
                    logger.info(f"Retrying with rotated API key index {GroqKeyManager._current_index} (Attempt {attempt + 1}/{max_retries})")
                    rotations_this_attempt += 1
                    continue 
            
            # 2. Try falling back to a lighter model if using the powerful one
            if current_model == powerful_model and not model_fallback_active:
                logger.warning(f"70b Model Rate Limited on all keys. Falling back to 8b-instant...")
                current_model = fast_model
                model_fallback_active = True
                rotations_this_attempt = 0 # Try all keys again with the lighter model
                continue

            # 3. Both models/all keys exhausted: Full exponential backoff
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), 120)
                logger.warning(f"All Groq paths exhausted. Cooling down for {delay}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                attempt += 1
                rotations_this_attempt = 0 
                model_fallback_active = False
                current_model = original_model # Try the powerful model again after a long sleep
                continue
            raise e
        except groq.BadRequestError as e:
            # Handle JSON validation errors - retry with simpler prompt
            error_msg = str(e)
            if 'json_validate_failed' in error_msg or 'Failed to generate JSON' in error_msg:
                logger.warning(f"Groq JSON Validation Failed: Retrying... (Attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    attempt += 1
                    continue
            # Other bad requests - usually unrecoverable
            logger.error(f"Groq Bad Request (400): {error_msg}")
            raise e
        except groq.APIStatusError as e:
            if e.status_code == 429:
                 if keys_count > 1 and rotations_this_attempt < keys_count:
                     if GroqKeyManager.rotate_key():
                        time.sleep(1)
                        new_key = GroqKeyManager.get_current_key()
                        current_client = groq.Groq(api_key=new_key)
                        rotations_this_attempt += 1
                        continue
            if e.status_code == 413:
                if GroqKeyManager.rotate_key():
                    new_key = GroqKeyManager.get_current_key()
                    current_client = groq.Groq(api_key=new_key)
                    continue 
                logger.error(f"Groq Request Too Large (413): {e.message}")
                raise e
            raise e
        except (groq.APIConnectionError, groq.APITimeoutError) as e:
            if attempt < max_retries - 1:
                delay = base_delay + attempt 
                logger.warning(f"Groq Connection Error: {e}. Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                attempt += 1
                continue
            raise e
        except Exception as e:
            err_msg = str(e).lower()
            if "status_code=503" in err_msg or "overloaded" in err_msg:
                if attempt < max_retries - 1:
                    time.sleep(base_delay)
                    attempt += 1
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
    import re
    def clean_ans(s):
        if not s: return ""
        return re.sub(r'^(?:choice\s+)?[a-z0-9][\.\)\:\s-]+\s*', '', str(s).lower()).strip()

    for q in mcqs:
        if not isinstance(q, dict):
            continue
        item = copy.deepcopy(q)
        item['difficulty'] = _normalize_difficulty_label(item.get('difficulty'), default='Medium')
        
        # Consolidate answer fields
        raw_ans = item.get('answer') or item.get('correct_answer') or item.get('ans') or item.get('correct_option') or ''
        
        options = item.get('options', [])
        if isinstance(options, list) and raw_ans:
            cleaned_raw = clean_ans(raw_ans)
            matched = False
            for opt in options:
                if clean_ans(opt) == cleaned_raw:
                    item['answer'] = opt
                    matched = True
                    break
            
            if not matched:
                # FALLBACK: Try mapping if answer is a numeric index or a single letter (A, B, C, D)
                raw_ans_str = str(raw_ans).strip().upper()
                mapped = False
                
                # Case 1: Numeric index string (e.g. "1", "2")
                if raw_ans_str.isdigit():
                    try:
                        idx = int(raw_ans_str) - 1
                        if 0 <= idx < len(options):
                            item['answer'] = options[idx]
                            mapped = True
                    except: pass
                
                # Case 2: Letter index (A, B, C, D)
                if not mapped and len(raw_ans_str) == 1 and 'A' <= raw_ans_str <= 'D':
                    idx = ord(raw_ans_str) - ord('A')
                    if 0 <= idx < len(options):
                        item['answer'] = options[idx]
                        mapped = True

                if not mapped:
                    item['answer'] = str(raw_ans).strip()
        else:
            item['answer'] = str(raw_ans).strip()
            
        for k in ['correct_answer', 'ans', 'correct_option']:
            item.pop(k, None)

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
        
        # Ensure test cases are normalized to 'test_cases' with 'output' key
        tc = item.get('test_cases', item.get('testcases', item.get('cases', [])))
        if not isinstance(tc, list):
            tc = []
        
        # Internal normalization of test case keys
        normalized_tc = []
        for t in tc:
            if not isinstance(t, dict): continue
            t_norm = copy.deepcopy(t)
            # Ensure 'output' exists if 'expected_output' was provided
            if 'expected_output' in t_norm and 'output' not in t_norm:
                t_norm['output'] = t_norm['expected_output']
            normalized_tc.append(t_norm)
        
        item['test_cases'] = normalized_tc
        
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

def _validate_mcq_structure(mcq):
    """
    Validates that an MCQ has all required fields with correct structure.
    Returns (is_valid: bool, error_msg: str)
    """
    if not mcq.get('question') or not isinstance(mcq.get('question'), str):
        return False, "Missing or empty 'question' field"
    
    if not isinstance(mcq.get('options'), list) or len(mcq.get('options', [])) != 4:
        return False, f"Must have exactly 4 options, got {len(mcq.get('options', []))}"
    
    # Check that each option is non-empty AND meaningful (not just placeholder letters)
    options = mcq.get('options', [])
    for idx, opt in enumerate(options):
        opt_str = str(opt).strip()
        if not opt_str:
            return False, f"Option {idx+1} is empty or whitespace"
        
        # CRITICAL: Reject placeholder letters like "A", "B", "C", "D" or "A)", "B)", etc.
        # Options must be actual answer text (>3 chars, meaningful content)
        import re
        cleaned_opt = opt_str.rstrip(')').rstrip(':').rstrip('.').strip()
        
        if len(cleaned_opt) <= 1:
            return False, f"Option {idx+1} is placeholder letter '{opt_str}' (not actual answer text)"
        
        # Reject if option is ONLY a single letter choice
        if cleaned_opt.upper() in ('A', 'B', 'C', 'D'):
            return False, f"Option {idx+1} '{opt_str}' is a single letter placeholder"
            
        # Reject "Option A", "Choice B", "Answer 1", etc.
        if re.match(r'^(Option|Choice|Answer|Selection)\s*[A-D0-9]?$', cleaned_opt, re.IGNORECASE):
            return False, f"Option {idx+1} '{opt_str}' is a generic placeholder (e.g. 'Option A')"

        # Check option is not too long (should be under 15 words for readability)
        word_count = len(opt_str.split())
        if word_count > 15:
            return False, f"Option {idx+1} is too long ({word_count} words, max 15)"
    
    answer = mcq.get('answer')
    if not answer:
        return False, "Missing or empty 'answer' field"
    
    # Check answer matches one of options (case-insensitive)
    answer_lower = str(answer).lower().strip()
    options_lower = [str(opt).lower().strip() for opt in mcq.get('options', [])]
    if answer_lower not in options_lower:
        return False, f"Answer '{answer}' doesn't match any option: {mcq.get('options')}"
    
    if mcq.get('difficulty') not in ('Easy', 'Medium', 'Hard'):
        return False, f"Invalid difficulty: {mcq.get('difficulty')}"
    
    return True, "Valid"

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
    model="llama-3.1-8b-instant",
    cancel_token=None
):
    """Top up missing MCQ/coding items when model under-generates in initial pass."""
    repaired = _normalize_generated_pool(pool)

    for attempt in range(max_attempts):
        if cancel_token and cache.get(f"abort_{cancel_token}"):
            raise Exception("Generation Aborted by User")
            
        easy_count, medium_count, hard_count = _mcq_difficulty_counts(repaired.get('mcqs', []))
        current_coding = len(repaired.get('coding_challenges', []))

        missing_easy = max(0, pool_easy - easy_count)
        missing_medium = max(0, pool_medium - medium_count)
        missing_hard = max(0, pool_hard - hard_count)
        missing_coding = max(0, pool_coding_total - current_coding)

        missing_total = missing_easy + missing_medium + missing_hard + missing_coding
        if missing_total == 0:
            break

        # 1. REPAIR CODING (Skeleton-Based)
        if missing_coding > 0:
            needed_diffs = (coding_tasks or ['Medium'])[current_coding:current_coding + missing_coding]
            if not needed_diffs:
                needed_diffs = ['Medium'] * missing_coding
                
            logger.info(f"REPAIR: Rescuing {missing_coding} missing coding challenges.")
            new_coding = _generate_execution_verified_coding_pool(
                groq_client=groq_client,
                job_description=job_description,
                required_skills=required_skills,
                difficulties=needed_diffs,
                total_required=missing_coding,
                model=model,
                cancel_token=cancel_token
            )
            repaired['coding_challenges'].extend(new_coding)

        # 2. REPAIR MCQs (AI-Only)
        missing_mcqs = missing_easy + missing_medium + missing_hard
        if missing_mcqs > 0:
            logger.info(f"REPAIR: Rescuing {missing_mcqs} missing MCQs (E:{missing_easy}, M:{missing_medium}, H:{missing_hard}).")
            
            # Use the highly resilient, batch-based generator instead of a single brittle prompt
            # It already has a "one-by-one" gap filler built in, guaranteeing we hit the count.
            blacklist_qs = [q.get('question', '')[:100] for q in repaired.get('mcqs', [])]
            
            try:
                new_mcqs = _generate_mcq_pool_ai_only(
                    groq_client=groq_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    pool_mcq_total=missing_mcqs,
                    pool_easy=missing_easy,
                    pool_medium=missing_medium,
                    pool_hard=missing_hard,
                    attempts_per_batch=5,  # We are already in a retry loop
                    blacklist_qs=blacklist_qs,
                    model=model,
                    cancel_token=cancel_token
                )
                if new_mcqs:
                    repaired['mcqs'].extend(new_mcqs)
            except Exception as repair_err:
                logger.warning(f"Repair attempt {attempt + 1}/{max_attempts} for MCQs failed: {repair_err}")
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
    batch_size=1,
    attempts_per_batch=3,
    blacklist_titles=None,
    model="llama-3.1-8b-instant",
    cancel_token=None
):
    """
    SKELETON-BASED GENERATION:
    1. Pick a proven math skeleton from coding_skeletons.py
    2. Ask AI to write ONLY the professional story/scenario matching the JD
    3. Use pre-verified solutions — NO AI code generation needed
    """
    if total_required <= 0:
        return []

    blacklist = blacklist_titles or []
    
    desired = list(difficulties or [])
    if len(desired) < total_required:
        desired.extend(['Medium'] * (total_required - len(desired)))
    desired = desired[:total_required]

    generated = []
    used_skeleton_ids = set()
    used_categories = set()

    for i in range(total_required):
        if cancel_token and cache.get(f"abort_{cancel_token}"):
            raise Exception("Generation Aborted by User")
            
        diff = desired[i]
        
        # 1. STRICT: Filter skeletons strictly by required difficulty
        available_for_diff = [s for s in CodingSkeletons.SKELETONS if s.get('difficulty') == diff]
        if not available_for_diff:
            # Fallback if no skeletons exist for this difficulty at all
            available_for_diff = CodingSkeletons.SKELETONS

        # 2. DIVERSITY FILTER: Try to pick a completely new logic category
        unused_cat_candidates = [s for s in available_for_diff if s.get('category') not in used_categories and s['id'] not in used_skeleton_ids]
        
        if unused_cat_candidates:
            skeleton = random.choice(unused_cat_candidates)
        else:
            # 3. If we ran out of unique categories for this difficulty, relax category rule but keep puzzle unique
            unused_id_candidates = [s for s in available_for_diff if s['id'] not in used_skeleton_ids]
            if unused_id_candidates:
                skeleton = random.choice(unused_id_candidates)
            else:
                # 4. Absolute fallback: just pick any for this difficulty to avoid crashing
                skeleton = random.choice(available_for_diff)
        
        used_skeleton_ids.add(skeleton['id'])
        if skeleton.get('category'):
            used_categories.add(skeleton['category'])

        format_override = ""
        if diff == 'Easy':
            format_override = """
CRITICAL OVERRIDE FOR EASY QUESTIONS:
- Do NOT write a long, complicated real-world scenario.
- Write the problem EXACTLY like a classic LeetCode problem.
- Start directly with the core requirement (e.g., "Given an array of integers `nums` and an integer `k`, return...").
- Ensure the student understands instantly that this is a straightforward, purely algorithmic question.
"""
        elif diff == 'Medium':
            format_override = """
CRITICAL OVERRIDE FOR MEDIUM QUESTIONS:
- Do NOT write a long, complicated real-world scenario.
- Write the problem EXACTLY like a classic LeetCode Medium problem.
- Provide a clear, technical definition of the problem (e.g., "You are given an integer array... Find... Return...").
- State any "Notice" or edge case rules clearly (e.g., "Notice that you may not slant the container.").
- Keep the language purely technical, algorithmic, and free of unnecessary background story.
"""
        elif diff == 'Hard':
            format_override = """
CRITICAL OVERRIDE FOR HARD QUESTIONS:
- Do NOT write a long, complicated real-world scenario.
- Write the problem EXACTLY like a classic LeetCode Hard problem.
- Provide a rigorous, highly technical definition of the problem (e.g., "Given an input string `s` and a pattern `p`, implement...").
- State complex edge cases, matching rules, or strict conditions clearly.
- Keep the language purely technical, algorithmic, and mathematics-focused.
"""

        # Ask AI ONLY for the story — NO code generation
        story_prompt = f"""You are a professional assessment writer. Create a coding challenge DESCRIPTION for a job candidate.

JOB DESCRIPTION: {job_description[:1000]}
REQUIRED SKILLS: {required_skills[:500] if required_skills else 'General Programming'}

MATHEMATICAL LOGIC TO USE (DO NOT CHANGE THE MATH):
- Pattern: {skeleton['title_hint']}
- Description: {skeleton['logic_desc']}
- Difficulty: {skeleton['difficulty']}

ALREADY GENERATED TITLES (AVOID DUPLICATES): {[c.get('title','') for c in generated] + blacklist}
{format_override}
YOUR TASK:
Write a PROFESSIONAL problem statement that:
1. Is purely technical, algorithmic, and follows a strict LeetCode style (Do NOT invent background stories or real-world scenarios).
2. Follows the EXACT mathematical logic described above.
3. Is clear and easy for a student to understand, while respecting the difficulty level.

RETURN THIS EXACT JSON FORMAT:
{{
    "title": "<Professional title related to JD, e.g. 'Optimizing API Response Times'>",
    "problem_statement": "<3-5 sentences describing the scenario. MUST clearly explain: what the input represents, what to compute, and what to output.>",
    "explanation": "<Step-by-step explanation of how to solve it>",
    "constraints": "<e.g. 1 <= N <= 10^5>"
}}

RULES:
- DO NOT include Any examples, test cases, or sample inputs/outputs in the problem_statement. These will be added automatically by the system.
- MUST include a short **Input Format** section at the end of the `problem_statement` describing exactly what each line of the input represents (e.g. "The first line contains N, the second line contains...").
- Return JSON ONLY. No markdown.
- CRITICAL: You MUST escape any internal double quotes inside strings (e.g., use \\" instead of ") to ensure valid JSON!
- Title must be unique and related to the JD.
- Problem statement must be clear enough for a student to understand in 30 seconds.
"""

        for attempt in range(attempts_per_batch):
            try:
                result = _call_groq_with_backoff(
                    groq_client,
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional assessment writer. Return JSON only."},
                        {"role": "user", "content": story_prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=2048,
                    temperature=0.8,
                )
                data = result if isinstance(result, dict) else extract_json(result)

                if data and data.get('title') and data.get('problem_statement'):
                    # Build the complete challenge by merging AI story + Skeleton math
                    challenge = {
                        "title": data['title'],
                        "difficulty": skeleton['difficulty'],
                        "topic": skeleton['title_hint'].split('/')[0].strip(),
                        "problem_statement": data['problem_statement'],
                        "constraints": data.get('constraints', 'N <= 10^5'),
                        "explanation": data.get('explanation', ''),
                        "input_generator_schema": skeleton['input_schema'],
                        "reference_solution": skeleton['gold_solution'],
                        "example_input": "N/A",  # Will be generated during verification
                        "example_output": "N/A",
                        "function_meta": {"name": "solve", "params": [{"name": "data", "type": "string"}], "return_type": "string"}
                    }
                    generated.append(challenge)
                    logger.info(f"SKELETON: Generated '{challenge['title']}' using pattern '{skeleton['id']}' ({skeleton['difficulty']})")
                    break
                else:
                    logger.warning(f"SKELETON: AI story attempt {attempt+1} returned incomplete JSON for '{skeleton['id']}'")
            except Exception as e:
                logger.error(f"SKELETON: Failed attempt {attempt+1} for '{skeleton['id']}': {e}")

    return generated[:total_required]
def _generate_execution_verified_coding_pool(*, groq_client, job_description, required_skills, difficulties, total_required, model="llama-3.1-8b-instant", cancel_token=None):
    """
    Entry point for skeleton-based generation.
    1. Generates the pool using skeletons.
    2. Runs each skeleton once to populate example_input/output.
    """
    # 1. Generate story-wrapped skeletons
    challenges = _generate_coding_pool_ai_only(
        groq_client=groq_client,
        job_description=job_description,
        required_skills=required_skills,
        difficulties=difficulties,
        total_required=total_required,
        model=model,
        cancel_token=cancel_token
    )

    # 2. POPULATE EXAMPLE DATA & TEST CASES
    # Skeletons come with gold_solution and input_schema, but we need actual text for the UI.
    verified_challenges = []
    for challenge in challenges:
        if cancel_token and cache.get(f"abort_{cancel_token}"):
            raise Exception("Generation Aborted by User")
        try:
            schema = challenge.get('input_generator_schema')
            ref_sol = challenge.get('reference_solution')
            
            # Generate one real example for the UI
            example_input = InputDataGenerator.generate(schema)
            res = _call_executor(language='python', source_code=ref_sol, stdin=example_input)
            
            if res.get('ok') and res.get('stdout'):
                challenge['example_input'] = example_input
                challenge['example_output'] = str(res.get('stdout', '')).strip()
                
                # Append formatted, verified example to description
                challenge['problem_statement'] += (
                    f"\n\n### Example 1:\n"
                    f"**Input:**\n"
                    f"```text\n{challenge['example_input']}\n```\n"
                    f"**Output:**\n"
                    f"```text\n{challenge['example_output']}\n```"
                )
                
                # Generate test cases (4-6 required, targeting 6)
                MIN_TEST_CASES = 4
                MAX_TEST_CASES = 6
                MAX_REPAIR_ATTEMPTS = 2
                
                test_cases = []
                for idx in range(MAX_TEST_CASES):
                    if cancel_token and cache.get(f"abort_{cancel_token}"):
                        raise Exception("Generation Aborted by User")
                    tc_input = InputDataGenerator.generate(schema)
                    tc_res = _call_executor(language='python', source_code=ref_sol, stdin=tc_input)
                    if tc_res.get('ok'):
                        test_cases.append({
                            "id": f"tc_{idx+1}",
                            "input": tc_input,
                            "output": str(tc_res.get('stdout', '')).strip(),
                            "is_hidden": True
                        })
                
                # Check initial test case count
                if len(test_cases) < MIN_TEST_CASES:
                    # Repair attempt: Retry test case generation (0 tokens)
                    for repair_attempt in range(MAX_REPAIR_ATTEMPTS):
                        logger.info(f"[Repair {repair_attempt+1}/{MAX_REPAIR_ATTEMPTS}] Retrying test case generation for '{challenge['title']}'...")
                        test_cases = []
                        
                        for idx in range(MAX_TEST_CASES):
                            if cancel_token and cache.get(f"abort_{cancel_token}"):
                                raise Exception("Generation Aborted by User")
                            tc_input = InputDataGenerator.generate(schema)
                            tc_res = _call_executor(language='python', source_code=ref_sol, stdin=tc_input)
                            if tc_res.get('ok'):
                                test_cases.append({
                                    "id": f"tc_{idx+1}",
                                    "input": tc_input,
                                    "output": str(tc_res.get('stdout', '')).strip(),
                                    "is_hidden": True
                                })
                        
                        if len(test_cases) >= MIN_TEST_CASES:
                            logger.info(f"✅ [Repair {repair_attempt+1}] SUCCESS! Generated {len(test_cases)} test cases.")
                            break
                    else:
                        # All repair attempts failed
                        logger.error(
                            f"❌ TEST CASE COMPLETENESS FAILED: '{challenge['title']}'. "
                            f"Generated {len(test_cases)}/{MIN_TEST_CASES}-{MAX_TEST_CASES} test cases after {MAX_REPAIR_ATTEMPTS} repair attempts. "
                            f"Minimum {MIN_TEST_CASES} required. Challenge REJECTED and will be replaced via repair pool."
                        )
                        continue  # Skip this challenge, counts as shortfall
                
                challenge['test_cases'] = test_cases
                verified_challenges.append(challenge)
                logger.info(f"✅ Verified Skeleton: '{challenge['title']}' with {len(test_cases)}/{MAX_TEST_CASES} test cases.")
            else:
                logger.error(f"SKELETON FAILED VERIFICATION: '{challenge['title']}'. Error: {res.get('error')}")
        except Exception as e:
            logger.error(f"Error verifying skeleton '{challenge.get('title')}': {e}")

    return verified_challenges

def _generate_mcq_pool_ai_only(
    *,
    groq_client,
    job_description,
    required_skills,
    pool_mcq_total,
    pool_easy,
    pool_medium,
    pool_hard,
    attempts_per_batch=20, # INCREASED: Maximum persistence for rotation
    blacklist_qs=None,
    model="llama-3.1-8b-instant",
    cancel_token=None
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
        batch_size = 15 # TURBO: Increased batch size for faster large-pool generation (scales down on 413)
        while idx < total_count_for_diff:
            if cancel_token and cache.get(f"abort_{cancel_token}"):
                raise Exception("Generation Aborted by User")
            
            count = min(batch_size, total_count_for_diff - idx)
            
            # Compress instructions to save token overhead
            avoid_list = (blacklist + [q.get('question', '')[:50] for q in generated])[:10]
            avoid_txt = f"Exclude topics: {avoid_list}" if avoid_list else ""
            
            prompt = f"""
            JD: {job_description} | Skills: {required_skills}
            TASK: Generate {count} technical MCQs ({difficulty}).
            JSON FORMAT: {{ "mcqs": [ {{ "question": "What is Django?", "options": ["A web framework for Python", "A database management system", "A testing library", "A package manager"], "answer": "A web framework for Python", "difficulty": "{difficulty}" }} ] }}
            RULES:
            - Generate valid JSON only (do NOT use escape sequences)
            - UNIQUE: Questions must be specific to JD facets. {avoid_txt}
            - OPTIONS MUST BE DESCRIPTIVE: Each option MUST be a short (under 15 words) sentence or phrase that actually describes a possible answer.
            - NO PLACEHOLDERS: NEVER use options like "Option A", "Option B", "Choice 1", or simply "A", "B", "C", "D".
            - NEGATIVE EXAMPLE (DO NOT DO THIS): {{ "options": ["Option A", "Option B", "Option C", "Option D"] }}
            - POSITIVE EXAMPLE: {{ "options": ["A high-level programming language", "A low-level assembly language", "A database system", "A web browser"] }}
            - ANSWER FIELD: The answer MUST be the exact text from one of the options.
            - Each question gets exactly 4 options and 1 correct answer.
            """

            batch_mcqs = None

            for attempt in range(attempts_per_batch):
                try:
                    response = _call_groq_with_backoff(
                        groq_client,
                        model=model,
                        messages=[
                            {"role": "system", "content": "You output JSON only."},
                            {"role": "user", "content": prompt},
                        ],
                        response_format={"type": "json_object"},
                        max_tokens=4096,
                        temperature=0.2,
                    )
                    
                    if not response:
                        logger.warning(f"Empty/Invalid response on attempt {attempt + 1}")
                        continue

                    parsed = _normalize_generated_pool(response if isinstance(response, dict) else (extract_json(response) or {}))
                    mcqs = parsed.get('mcqs', [])
                    same_diff = [q for q in mcqs if _normalize_difficulty_label(q.get('difficulty')) == difficulty]

                    # VALIDATE each MCQ structure before accepting
                    validated_mcqs = []
                    for q in same_diff:
                        is_valid, error_msg = _validate_mcq_structure(q)
                        if is_valid:
                            validated_mcqs.append(q)
                        else:
                            logger.debug(f"MCQ VALIDATION FAILED: {error_msg}. Question: {q.get('question', '')[:40]}...")

                    if len(validated_mcqs) >= count:
                        batch_mcqs = validated_mcqs[:count]
                        logger.info(f"MCQ Batch attempt {attempt + 1}: Generated {len(validated_mcqs)} valid {difficulty} MCQs")
                        break
                    elif len(same_diff) > 0:
                        logger.warning(f"MCQ Batch attempt {attempt + 1}: Generated {len(same_diff)} MCQs, only {len(validated_mcqs)} valid")
                        
                    # Correction for next attempt in same batch
                    prompt = prompt + f"\nRetry: Ensure exactly {count} {difficulty} MCQs are returned. CRITICAL: Each MCQ MUST have all fields: question, 4 options, answer (matched to option), difficulty."

                except groq.APIStatusError as e:
                    if e.status_code == 413 and batch_size > 2:
                        logger.warning(f"Batch {batch_size} too large (413). Auto-scaling down to {batch_size-2}...")
                        batch_size -= 2
                        # Reset this specific batch attempt to start over with smaller size
                        break # Exits "attempts" loop but stays in "while idx" loop
                    raise e
                except Exception as e:
                    logger.warning(f"MCQ Batch attempt {attempt + 1} failed: {e}")
                    if attempt == attempts_per_batch - 1:
                        # Final failure for this batch
                        break

            if not batch_mcqs:
                # RECOVERY: If a batch fails, log and retry with single regeneration
                logger.error(
                    f"❌ MCQ Batch VALIDATION FAILED all {attempts_per_batch} attempts for {difficulty} ({count} questions). "
                    f"Will be replaced via repair pool shortfall mechanism."
                )
                idx += count # Advance so we don't get stuck in a loop, but we accept the shortfall
                continue

            for q in batch_mcqs:
                q['difficulty'] = difficulty
            generated.extend(batch_mcqs)
            idx += count
            
        # FINAL RESCUE: If we still have a shortfall, fill it one-by-one to avoid all limits
        while len([q for q in generated if q.get('difficulty') == difficulty]) < total_count_for_diff:
            if cancel_token and cache.get(f"abort_{cancel_token}"):
                raise Exception("Generation Aborted by User")
                
            shortfall = total_count_for_diff - len([q for q in generated if q.get('difficulty') == difficulty])
            logger.info(f"MCQ Resilient Gap-Filler: Generating {shortfall} more {difficulty} MCQs one-by-one.")
            
            rescue_prompt = f"""
            JD: {job_description} | Skills: {required_skills}
            TASK: Generate EXACTLY 1 UNIQUE technical MCQ ({difficulty}).
            JSON: {{ "mcqs": [ {{ "question": "What is REST?", "options": ["Representational State Transfer architecture", "A testing framework", "A database query language", "A version control system"], "answer": "Representational State Transfer architecture", "difficulty": "{difficulty}" }} ] }}
            RULES:
            - Return JSON only.
            - OPTIONS MUST BE DESCRIPTIVE: Each option MUST be actual answer text (NOT placeholder letters like "A", "B" or "Option A").
            - NO PLACEHOLDERS: NEVER use "Option A", "Choice 1", etc.
            - The answer field MUST be the exact text from one of the options.
            - Exclude topics: {[q.get('question', '')[:30] for q in generated][-10:]}
            """
            try:
                resp = _call_groq_with_backoff(
                    groq_client, 
                    model=model, 
                    messages=[{"role": "user", "content": rescue_prompt}], 
                    response_format={"type": "json_object"},
                    max_tokens=1024
                )
                rescue_mcqs = _normalize_generated_pool((resp if isinstance(resp, dict) else extract_json(resp)) or {}).get('mcqs', [])
                for rq in rescue_mcqs:
                    # Validate each rescue MCQ
                    is_valid, error_msg = _validate_mcq_structure(rq)
                    if not is_valid:
                        logger.warning(f"Gap-Filler MCQ validation failed: {error_msg}")
                        continue
                    
                    rq['difficulty'] = difficulty
                    generated.append(rq)
                    logger.info(f"✅ Gap-Filler added 1 {difficulty} MCQ. Total {difficulty}: {len([q for q in generated if q.get('difficulty') == difficulty])}/{total_count_for_diff}")
                    if len([q for q in generated if q.get('difficulty') == difficulty]) >= total_count_for_diff:
                        break
            except Exception as e:
                logger.error(f"Gap-Filler failed: {e}. Exiting relief loop.")
                break

            # Increased delay to 2s to mitigate Groq Rate Limits (TPM/RPM)
            if idx < total_count_for_diff:
                time.sleep(2)

    return generated

def _expert_assessment_refiner(groq_client, raw_content, cancel_token=None):
    """
    Uses a high-reasoning model to clean, fix, and standardize the generated pool
    according to strict production-ready requirements.
    """
    if cancel_token and cache.get(f"abort_{cancel_token}"):
        raise Exception("Generation Aborted by User")

    if not raw_content or (not raw_content.get('mcqs') and not raw_content.get('coding_challenges')):
        return raw_content

    logger.info("Expert Validator: Refinement pass started...")
    
    try:
        # Ensure the input is stringified JSON for the model
        input_json_str = json.dumps(raw_content, indent=2)
        
        # Call Groq with the high-reasoning model (Llama 3.3 70B)
        response = _call_groq_with_backoff(
            groq_client,
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional recruiter. Return JSON only."},
                {"role": "user", "content": f"INPUT:\n{input_json_str}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=8192,
            temperature=0.0,
            seed=42
        )
        
        refined_data = response if isinstance(response, dict) else extract_json(response)
        
        if refined_data and (refined_data.get('mcqs') or refined_data.get('coding_challenges')):
            logger.info("Expert Validator: Refinement SUCCESSFUL.")
            # Re-normalize to ensure standard structure (difficulty labels, etc)
            return _normalize_generated_pool(refined_data)
        
        logger.warning("Expert Validator: AI returned invalid or empty JSON. Falling back to raw content.")
        return raw_content
    except Exception as e:
        logger.error(f"Expert Validator: Refinement FAILED: {e}")
        return raw_content

def pick_random_subset(assessment, pool, seed=None, candidate_index=None):
    """
    Selects a subset of questions from the pool for a specific candidate.

    Uniqueness Strategy:
    - If `candidate_index` is provided AND `same_questions_for_all` is False:
        MCQs are distributed using a PARTITIONED approach — the pool is shuffled
        with a deterministic batch-level seed (assessment.batch_id), then sliced
        so each candidate gets a non-overlapping slice. Like dealing cards from
        a shuffled deck.
    - Otherwise (same_questions_for_all=True or no index given):
        Questions are randomly sampled with the email-based seed (reproducible
        but may overlap between candidates).

    Coding challenges are always unique — they are removed from the pool after
    selection, so no two candidates receive the same coding challenge
    (when same_questions_for_all=False).
    """
    if not pool:
        return {}

    local_random = random.Random(seed) if seed else random.Random()
    subset = {"mcqs": [], "coding_challenges": []}

    normalized_pool = _normalize_generated_pool(pool)
    pool_mcqs = list(normalized_pool.get('mcqs', []))
    pool_coding = copy.deepcopy(normalized_pool.get('coding_challenges', []))

    # Determine question target counts and difficulty breakdown
    target_mcq_count = getattr(assessment, 'mcq_count', 10)
    same_for_all = getattr(assessment, 'same_questions_for_all', True)

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

    # ── 1. SELECT MCQs ──────────────────────────────────────────────────────────
    use_partitioned = (
        candidate_index is not None
        and not same_for_all
        and len(pool_mcqs) >= target_mcq_count
    )

    if use_partitioned:
        # Partitioned mode: shuffle entire pool with a stable batch-level seed,
        # then assign each candidate a non-overlapping slice per difficulty tier.
        batch_seed = str(getattr(assessment, 'batch_id', '') or getattr(assessment, 'id', ''))
        batch_random = random.Random(batch_seed)

        for diff, target in target_mcqs:
            if target == 0:
                continue
            diff_pool = [q for q in pool_mcqs if q.get('difficulty') == diff]
            # Deterministically shuffle this tier's pool using batch seed
            batch_random_tier = random.Random(batch_seed + diff)
            batch_random_tier.shuffle(diff_pool)
            # Slice: candidate i gets indices [i*target : (i+1)*target]
            start = candidate_index * target
            end = start + target
            slice_qs = diff_pool[start:end]
            if slice_qs:
                subset['mcqs'].extend(slice_qs)

        # Backfill if slice didn't yield enough (pool smaller than expected)
        if len(subset['mcqs']) < target_mcq_count:
            selected_ids = {id(q) for q in subset['mcqs']}
            remaining = [q for q in pool_mcqs if id(q) not in selected_ids]
            needed = target_mcq_count - len(subset['mcqs'])
            if remaining:
                fill = local_random.sample(remaining, min(len(remaining), needed))
                subset['mcqs'].extend(fill)
    else:
        # Sampling mode (same_for_all or no index): email-seeded random sample
        selected_mcq_ids = set()
        for diff, target in target_mcqs:
            diff_pool = [q for q in pool_mcqs if q.get('difficulty') == diff and id(q) not in selected_mcq_ids]
            if diff_pool:
                sample_size = min(len(diff_pool), target)
                chosen = local_random.sample(diff_pool, sample_size)
                subset['mcqs'].extend(chosen)
                selected_mcq_ids.update(id(q) for q in chosen)

        if len(subset['mcqs']) < target_mcq_count:
            selected_mcq_ids = {id(q) for q in subset['mcqs']}
            remaining = [q for q in pool_mcqs if id(q) not in selected_mcq_ids]
            needed = target_mcq_count - len(subset['mcqs'])
            if remaining:
                fill = local_random.sample(remaining, min(len(remaining), needed))
                subset['mcqs'].extend(fill)

    # ── 2. SELECT CODING CHALLENGES ─────────────────────────────────────────────
    # Coding is always unique: chosen items are removed from pool after selection
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
