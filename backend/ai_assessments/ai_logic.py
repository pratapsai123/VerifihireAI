import os
from difflib import SequenceMatcher
import requests
import logging
import copy
import random
import json
import re
import sys
import time
import threading
from openai import APIStatusError
from .llm_client import (
    LLMKeyManager as GroqKeyManager,
    call_llm_with_backoff as _call_llm_with_backoff,
    create_llm_client,
    get_default_model,
)
from django.conf import settings
from django.core.cache import cache
from .code_generator import CodeGenerator
from .coding_skeletons import CodingSkeletons

logger = logging.getLogger(__name__)

# GroqKeyManager and _call_llm_with_backoff are now imported from llm_client.py
# They are aliased above for backward compatibility with all consumer code.

def _get_experience_guidelines(experience_level):
    """
    Returns experience-appropriate guidelines for MCQ generation.
    Maps frontend experience levels to question complexity and topics.
    """
    guidelines = {
        'fresher': {
            'description': 'Fresher (0 Years)',
            'focus': 'Basic syntax, fundamental concepts, simple problem-solving',
            'avoid': 'Advanced frameworks, metaclasses, async programming, system design, performance optimization',
            'topics': [
                'Python basics (data types, loops, functions, lists, dictionaries)',
                'Basic web concepts (HTTP methods, status codes)',
                'Simple SQL queries (SELECT, INSERT, UPDATE, DELETE)',
                'Git basics (add, commit, push, pull)',
                'Basic programming concepts (variables, conditionals, loops)',
                'Simple debugging and error handling',
                'Basic object-oriented programming (classes, objects, methods)'
            ],
            'difficulty_distribution': {'easy': 0.70, 'medium': 0.25, 'hard': 0.05},
            'prompt_guidance': 'Focus on fundamental concepts and basic syntax. Avoid complex scenarios or advanced patterns.'
        },
        'entry': {
            'description': 'Entry (0-2 years)',
            'focus': 'Framework basics, common patterns, debugging scenarios',
            'avoid': 'Advanced optimization, system design, complex architecture patterns',
            'topics': [
                'Django/Flask basics (models, views, templates, routing)',
                'REST API fundamentals (GET, POST, PUT, DELETE)',
                'Database relationships (foreign keys, joins)',
                'Basic testing concepts (unit tests, assertions)',
                'Version control workflows (branching, merging)',
                'Common debugging scenarios',
                'Basic security concepts (authentication, validation)'
            ],
            'difficulty_distribution': {'easy': 0.60, 'medium': 0.30, 'hard': 0.10},
            'prompt_guidance': 'Include framework fundamentals and common development patterns. Focus on practical scenarios.'
        },
        'mid': {
            'description': 'Mid (2-5 years)',
            'focus': 'Best practices, intermediate patterns, framework proficiency',
            'avoid': 'System architecture, advanced performance tuning, leadership concepts',
            'topics': [
                'Advanced Django/Flask features (middleware, signals, custom managers)',
                'API design patterns and best practices',
                'Database optimization (indexing, query optimization)',
                'Testing strategies (integration tests, mocking)',
                'Code quality and refactoring',
                'Security best practices',
                'Performance considerations'
            ],
            'difficulty_distribution': {'easy': 0.50, 'medium': 0.35, 'hard': 0.15},
            'prompt_guidance': 'Focus on best practices and intermediate patterns. Include real-world problem-solving scenarios.'
        },
        'senior': {
            'description': 'Senior (5-10 years)',
            'focus': 'Architecture decisions, optimization, complex problem-solving',
            'avoid': 'Basic syntax questions, simple concepts',
            'topics': [
                'System architecture and design patterns',
                'Performance optimization and profiling',
                'Advanced database concepts (sharding, replication)',
                'Scalability considerations',
                'Code review and mentoring scenarios',
                'Advanced testing strategies',
                'Security architecture'
            ],
            'difficulty_distribution': {'easy': 0.40, 'medium': 0.40, 'hard': 0.20},
            'prompt_guidance': 'Focus on architecture decisions and optimization. Include complex problem-solving scenarios.'
        },
        'expert': {
            'description': 'Expert (10+ years)',
            'focus': 'System design, advanced patterns, leadership and mentoring',
            'avoid': 'Basic concepts, simple syntax questions',
            'topics': [
                'Distributed systems design',
                'Advanced performance optimization',
                'Technology strategy and decision-making',
                'Team leadership and mentoring',
                'Complex system integration',
                'Advanced security and compliance',
                'Innovation and emerging technologies'
            ],
            'difficulty_distribution': {'easy': 0.30, 'medium': 0.40, 'hard': 0.30},
            'prompt_guidance': 'Focus on advanced concepts and strategic thinking. Include leadership and system design scenarios.'
        }
    }
    
    # Default to 'mid' if experience level not found
    return guidelines.get(experience_level, guidelines['mid'])


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
            
            elif b_type == 'word_break_input':
                # Special generator for Word Break problem
                # Generates a mix of true (segmentable) and false cases — ~50/50
                import random as _rnd
                dict_size = block.get('dict_size', 5)
                base_words = ['cat', 'cats', 'and', 'sand', 'dog', 'app', 'apple', 'pen', 'code', 'node',
                              'data', 'base', 'key', 'map', 'set', 'list', 'tree', 'heap', 'sort', 'find',
                              'get', 'put', 'run', 'log', 'net', 'web', 'api', 'bus', 'job', 'tag']
                chosen_words = _rnd.sample(base_words, min(dict_size, len(base_words)))
                # 60% chance: build s from concatenating 2-3 words (true case)
                # 40% chance: use a random string not in dict (false case)
                if _rnd.random() < 0.6:
                    # true case: s = concat of 2-3 words from dict
                    num_words = _rnd.randint(2, 3)
                    selected = _rnd.choices(chosen_words, k=num_words)
                    s_val = ''.join(selected)
                else:
                    # false case: random string unlikely to be segmentable
                    false_strings = ['handler', 'interface', 'database', 'runtime', 'gateway',
                                     'backend', 'frontend', 'network', 'compiler', 'debugger']
                    s_val = _rnd.choice(false_strings)
                m_val = len(chosen_words)
                output_parts.append(s_val)
                output_parts.append(str(m_val))
                output_parts.append(' '.join(chosen_words))
                context['s'] = s_val
                context['m'] = m_val
                continue  # skip the normal context[b_name] = val at end
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

# _call_llm_with_backoff is now imported from llm_client.py (aliased above)
# It handles exponential backoff, key rotation, and error recovery for DeepSeek V4 Flash.

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


# =============================================================================
# MCQ ACCURACY VERIFICATION LAYER (4-Layer AI Quality Check)
# These functions run AFTER structure validation, BEFORE accepting a question.
# They do NOT change generation flow — only filter out bad questions silently.
# =============================================================================

def _verify_mcq_answer(mcq, llm_client, model="deepseek-v4-flash"):
    """
    Layer 2: Self-Verify
    Sends the question WITHOUT the answer back to AI in a fresh context.
    Checks if AI independently picks the same answer.
    Returns (passed: bool, ai_answer: str)
    """
    question = mcq.get('question', '')
    options = mcq.get('options', [])
    correct_answer = mcq.get('answer', '')

    # Build options list as A/B/C/D for clean prompt
    options_text = '\n'.join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])

    verify_prompt = f"""You are a technical expert. Answer this question by selecting the correct option.

Question: {question}

Options:
{options_text}

Return ONLY a JSON object in this exact format:
{{"correct_option": "the exact text of the correct option"}}

Do not explain. Just return the JSON."""

    try:
        response = _call_llm_with_backoff(
            llm_client,
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise technical expert. Answer questions accurately. Return only valid JSON."},
                {"role": "user", "content": verify_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0.0,  # Zero temperature for deterministic answer
        )

        if not response:
            return True, ""  # If verify fails, give benefit of doubt

        # Parse response
        if isinstance(response, dict):
            ai_answer = response.get('correct_option', '').strip()
        else:
            parsed = extract_json(response)
            ai_answer = (parsed or {}).get('correct_option', '').strip()

        if not ai_answer:
            return True, ""  # If can't parse, give benefit of doubt

        # Compare AI's answer with original answer (case-insensitive)
        ai_lower = ai_answer.lower().strip()
        correct_lower = correct_answer.lower().strip()

        # Direct match
        if ai_lower == correct_lower:
            return True, ai_answer

        # Partial match (AI might return slightly different phrasing)
        if ai_lower in correct_lower or correct_lower in ai_lower:
            return True, ai_answer

        # Check if AI answer matches any option that is the correct one
        for opt in options:
            if opt.lower().strip() == ai_lower and opt.lower().strip() == correct_lower:
                return True, ai_answer

        logger.debug(f"VERIFY MISMATCH: Original='{correct_answer[:50]}' AI='{ai_answer[:50]}'")
        return False, ai_answer

    except Exception as e:
        logger.debug(f"Answer verify error (giving benefit of doubt): {e}")
        return True, ""  # On error, give benefit of doubt


def _verify_mcq_options(mcq, llm_client, model="deepseek-v4-flash"):
    """
    Layer 4: Option Quality Check
    Verifies that the 3 wrong options are genuinely wrong (not accidentally correct).
    Forces AI to PROVE each wrong option is wrong, not just agree.
    Returns (passed: bool, reason: str)
    """
    question = mcq.get('question', '')
    options = mcq.get('options', [])
    correct_answer = mcq.get('answer', '')

    # Build wrong options list
    wrong_options = [opt for opt in options if opt.lower().strip() != correct_answer.lower().strip()]

    if not wrong_options:
        return True, "No wrong options to check"

    wrong_options_text = '\n'.join([f"{i+1}. {opt}" for i, opt in enumerate(wrong_options)])

    verify_prompt = f"""You are a strict technical expert reviewing a multiple choice question for accuracy.

QUESTION: {question}
MARKED CORRECT ANSWER: {correct_answer}

WRONG OPTIONS TO EVALUATE:
{wrong_options_text}

YOUR TASK:
For EACH wrong option above, you MUST do two things:
1. Try your hardest to think of ANY scenario, context, or interpretation where that option could ALSO be correct
2. If you find even ONE valid scenario where it is correct -- mark it CONTAMINATED

IMPORTANT RULES:
- If a wrong option is ALSO a valid correct answer (even in a different context) -- CONTAMINATED
- If a wrong option is a deprecated but still working approach -- CONTAMINATED  
- If a wrong option works in a newer version of the technology -- CONTAMINATED
- Only mark CLEAN if you can PROVE with certainty each option is completely wrong

Return ONLY this JSON:
{{"verdict": "CLEAN", "analysis": "brief proof why each wrong option is definitely wrong"}}
OR
{{"verdict": "CONTAMINATED", "analysis": "which option number is also correct and why"}}"""

    try:
        response = _call_llm_with_backoff(
            llm_client,
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict technical accuracy reviewer. "
                        "Your job is to find problems with MCQ options. "
                        "Be skeptical -- if a wrong option could be correct in ANY scenario, flag it. "
                        "Return only valid JSON."
                    )
                },
                {"role": "user", "content": verify_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=400,
            temperature=0.0,
        )

        if not response:
            return True, "Verify unavailable"

        if isinstance(response, dict):
            verdict = response.get('verdict', 'CLEAN').strip().upper()
            analysis = response.get('analysis', '')
        else:
            parsed = extract_json(response)
            verdict = (parsed or {}).get('verdict', 'CLEAN').strip().upper()
            analysis = (parsed or {}).get('analysis', '')

        if verdict == 'CONTAMINATED':
            logger.warning(f"OPTION QUALITY FAILED: {analysis[:100]}")
            return False, analysis

        return True, "Clean"

    except Exception as e:
        logger.debug(f"Option verify error (giving benefit of doubt): {e}")
        return True, "Verify unavailable"


def _ai_verify_mcq(mcq, llm_client, model="deepseek-v4-flash"):
    """
    Master verification function combining Layer 2 + Layer 4.
    Layer 2: Verify the correct answer is actually correct (with majority vote)
    Layer 4: Verify wrong options are genuinely wrong

    Returns (passed: bool, reason: str)
    """
    question_preview = mcq.get('question', '')[:60]

    # --- LAYER 2: Answer Verification (with majority vote) ---
    verify1_passed, ai_answer1 = _verify_mcq_answer(mcq, llm_client, model)

    if not verify1_passed:
        # First check failed — do a second check (majority vote)
        verify2_passed, ai_answer2 = _verify_mcq_answer(mcq, llm_client, model)

        if not verify2_passed:
            # Both checks disagree with original answer — reject
            logger.warning(
                f"MCQ ANSWER REJECTED (2/2 disagree): '{question_preview}...' "
                f"Original='{mcq.get('answer','')[:40]}' AI1='{ai_answer1[:40]}' AI2='{ai_answer2[:40]}'"
            )
            return False, f"Answer verification failed: AI consistently disagrees with provided answer"
        else:
            # 1 disagrees, 1 agrees — give benefit of doubt, accept
            logger.debug(f"MCQ ANSWER: Split decision, accepting (1 agree, 1 disagree): '{question_preview}...'")

    # --- LAYER 4: Option Quality Check ---
    options_passed, options_reason = _verify_mcq_options(mcq, llm_client, model)

    if not options_passed:
        logger.warning(f"MCQ OPTIONS REJECTED: '{question_preview}...' Reason: {options_reason[:80]}")
        return False, f"Option quality failed: {options_reason}"

    logger.debug(f"MCQ VERIFIED OK: '{question_preview}...'")
    return True, "Verified"


def _repair_pool_shortfall(
    *,
    llm_client,
    job_description,
    required_skills,
    pool,
    pool_easy,
    pool_medium,
    pool_hard,
    pool_coding_total,
    coding_tasks,
    experience_level=None,
    max_attempts=5,
    model="deepseek-v4-flash",
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
                llm_client=llm_client,
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
                    llm_client=llm_client,
                    job_description=job_description,
                    required_skills=required_skills,
                    pool_mcq_total=missing_mcqs,
                    pool_easy=missing_easy,
                    pool_medium=missing_medium,
                    pool_hard=missing_hard,
                    experience_level=experience_level,
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

def _generate_input_format(schema):
    """
    Auto-generates an Input Format description based on the input_generator_schema.
    Returns a human-readable markdown string describing each line of input.
    """
    if not schema:
        return ""
    
    lines = []
    line_num = 1
    seen_params = set()
    array_idx = 0  # Track array occurrence for descriptive naming
    
    for item in schema:
        item_type = item.get('type', '')
        name = item.get('name', '')
        
        # For non-array items, skip duplicates by name
        if item_type != 'array' and name in seen_params:
            continue
        if name:
            seen_params.add(name)
        
        if item_type == 'int':
            lines.append(f"- Line {line_num}: An integer `{name.lower() or 'n'}`.")
            line_num += 1
        elif item_type == 'float':
            lines.append(f"- Line {line_num}: A floating-point number `{name.lower() or 'x'}`.")
            line_num += 1
        elif item_type == 'string':
            lines.append(f"- Line {line_num}: A string `{name.lower() or 's'}`.")
            line_num += 1
        elif item_type == 'array':
            array_idx += 1
            count_ref = item.get('count_ref', '')
            # Parse count_ref like "N*2" -> "2*N"
            ref_display = _describe_count_ref(count_ref) if count_ref else 'the specified count'
            item_inner = item.get('item', {})
            inner_type = item_inner.get('type', '')
            
            # Generate descriptive label based on context
            type_label = _get_type_label(inner_type)
            
            # If no name, generate descriptive one based on array index and schema context
            array_label = name.lower() if name else _generate_array_label(schema, array_idx, item)
            
            lines.append(f"- Line {line_num}: {ref_display} space-separated {type_label} (`{array_label}`).")
            line_num += 1
    
    if not lines:
        return ""
    
    # Ensure proper markdown formatting with bullet points
    formatted_lines = []
    for line in lines:
        # Ensure each line starts with a bullet point if it doesn't already
        if not line.strip().startswith('-'):
            formatted_lines.append(f"- {line}")
        else:
            formatted_lines.append(line)
    
    return "\n\n**Input Format:**\n" + "\n".join(formatted_lines)


def _describe_count_ref(count_ref):
    """Convert count_ref like 'N' or 'N*2' to human-readable description."""
    if not count_ref:
        return "the specified count"
    count_ref = str(count_ref).strip()
    if '*' in count_ref:
        parts = count_ref.split('*')
        if len(parts) == 2:
            try:
                multiplier = int(parts[1])
                base = parts[0].lower()
                return f"{multiplier}*{base}"
            except ValueError:
                pass
    return count_ref.lower()


def _get_type_label(inner_type):
    """Get human-readable type label."""
    labels = {
        'int': 'integers',
        'string': 'strings',
        'float': 'floating-point numbers',
    }
    return labels.get(inner_type, 'values')


def _generate_array_label(schema, array_idx, current_item):
    """Generate a descriptive label for an unnamed array based on schema context."""
    # Count how many arrays in the schema
    total_arrays = sum(1 for s in schema if s.get('type') == 'array')
    
    # Check if this looks like an interval problem (2 arrays with same count)
    if total_arrays == 2:
        # Check if both arrays have the same count_ref
        arrays = [s for s in schema if s.get('type') == 'array']
        if len(arrays) == 2:
            count1 = arrays[0].get('count_ref', '')
            count2 = arrays[1].get('count_ref', '')
            if count1 and count1 == count2:  # Same count reference suggests interval pairs
                if array_idx == 1:
                    return "start_times"
                elif array_idx == 2:
                    return "end_times"
    
    # Check for single array case
    if total_arrays == 1:
        # Look for context in other schema items
        has_n = any(s.get('name', '').upper() == 'N' and s.get('type') == 'int' for s in schema)
        if has_n:
            return "array"
    
    # Default labeling for multiple arrays
    if total_arrays == 2:
        if array_idx == 1:
            return "first_array"
        elif array_idx == 2:
            return "second_array"
    elif total_arrays == 3:
        if array_idx == 1:
            return "first_array"
        elif array_idx == 2:
            return "second_array"
        elif array_idx == 3:
            return "third_array"
    
    return f"array_{array_idx}"


def _strip_ai_examples(problem_statement):
    """
    Remove any examples, input format sections, or markdown code blocks that the AI
    may have included in the problem statement, to prevent duplication with system-generated examples.
    """
    import re
    if not problem_statement:
        return problem_statement
    
    text = problem_statement
    
    # Remove markdown code blocks (``` ... ```)
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Remove "Input Format:" sections
    text = re.sub(r'\*\*Input Format:\*\*[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Input Format:[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    
    # Remove "Example" sections (Example 1:, Example 2:, etc.)
    text = re.sub(r'\*\*Example \d+:\*\*[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'### Example \d+:[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Example \d+:[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*Input:\*\*[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*Output:\*\*[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*Explanation:\*\*[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    
    # Remove "Sample Input/Output" sections
    text = re.sub(r'Sample Input[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Sample Output[\s\S]*?(?=\n\n|\Z)', '', text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def _generate_coding_pool_ai_only(
    *,
    llm_client,
    job_description,
    required_skills,
    difficulties,
    total_required,
    batch_size=1,
    attempts_per_batch=3,
    blacklist_titles=None,
    model="deepseek-v4-flash",
    cancel_token=None
):
    """
    SKELETON-BASED GENERATION:
    1. Pick a proven math skeleton from coding_skeletons.py
    2. Ask AI to write ONLY the professional story/scenario matching the JD
    3. Use pre-verified solutions -- NO AI code generation needed
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
            format_override = f"""
DIFFICULTY: Easy
STYLE: Pure algorithmic — exactly like LeetCode Easy. No story, no context.

STRUCTURE TO FOLLOW:
1. One direct sentence: "Given [input], return [output]."
2. Optionally one clarifying sentence about edge cases or constraints.
3. Nothing else.

EXAMPLES OF PERFECT EASY PROBLEMS (follow this style exactly):
- "Given an integer array nums, return true if any value appears at least twice, and false if every element is distinct."
- "Given an array of integers nums and an integer target, return the indices of the two numbers that add up to target."
- "Given a string s, find the length of the longest substring without repeating characters."

VARIABLE NAMES: Use lowercase names that match the input schema fields exactly.
The mathematical logic to implement: {skeleton['logic_desc']}
"""
        elif diff == 'Medium':
            format_override = f"""
DIFFICULTY: Medium
STYLE: One sentence of professional context + clear algorithmic requirement. Like LeetCode Medium.

STRUCTURE TO FOLLOW:
1. ONE sentence of real-world context tied to the job role (e.g., "You are processing server logs for a distributed system.")
2. ONE or TWO sentences stating the exact algorithmic requirement.
3. Nothing else. No backstory, no company names, no character names.

EXAMPLES OF PERFECT MEDIUM PROBLEMS (follow this style exactly):
- "You are analyzing network packet timestamps. Given an array of n integers representing packet arrival times and n integers representing departure times, return the maximum number of packets being processed simultaneously."
- "You are optimizing a caching system. Given an array of strings representing cache keys, group the keys that are anagrams of each other and return the number of unique groups."
- "You are processing financial transactions. Given an integer array nums where nums[i] is the price of a stock on day i, return the maximum profit from a single buy-sell transaction."

VARIABLE NAMES: Use lowercase names that match the input schema fields exactly.
The mathematical logic to implement: {skeleton['logic_desc']}
"""
        elif diff == 'Hard':
            format_override = f"""
DIFFICULTY: Hard
STYLE: 2-3 sentences of professional context that EXACTLY matches the input format. Like LeetCode Hard or HackerRank Hard.

STRICT RULES:
1. The story MUST describe the EXACT same computation as the mathematical logic below. Do NOT invent a different problem.
2. If the input is an array of integers, the story must be about processing a list/sequence of values — NOT about designing a class or OOP.
3. If the input has two values (N and K), both must appear naturally in the story.
4. Keep it to 2-3 sentences maximum. No long backstories.
5. End with a precise algorithmic requirement: "Return..." or "Find..." or "Compute..."

EXAMPLES OF PERFECT HARD PROBLEMS (follow this style exactly):
- "You are building a real-time analytics dashboard that monitors server response times. Given an array of n response times and a window size k, return the maximum response time in each sliding window of size k as the window moves from left to right."
- "You are implementing a text diff tool for a code review system. Given two code snippets word1 and word2, return the minimum number of single-character edits (insert, delete, or replace) required to transform word1 into word2."
- "You are designing a flood risk assessment system for a city. Given an elevation map represented as an array of n non-negative integers where each value represents the height of a terrain column, compute the total volume of rainwater that can be trapped between the columns."

VARIABLE NAMES: Use lowercase names that match the input schema fields exactly.
The mathematical logic to implement: {skeleton['logic_desc']}
"""

        # Ask AI ONLY for the story -- NO code generation
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
Write a PROFESSIONAL problem statement following the difficulty style above.
The problem statement must:
1. Follow the exact style and structure defined in the DIFFICULTY section above.
2. Implement the EXACT mathematical logic described — do not change the algorithm.
3. Be instantly clear to a candidate — they should understand what to compute in 15 seconds.
4. Use variable names that match the input schema fields.

RETURN THIS EXACT JSON FORMAT:
{{
    "title": "<Professional title related to JD, e.g. 'Optimizing API Response Times'>",
    "problem_statement": "<3-5 sentences describing the scenario. MUST clearly explain: what the input represents, what to compute, and what to output.>",
    "explanation": "<Step-by-step explanation of how to solve it>",
    "constraints": "<Write EACH constraint on a separate line. e.g. 1 <= N <= 10^5\n-10^9 <= nums[i] <= 10^9>"
}}

RULES:
- DO NOT include any Input Format section, examples, test cases, or sample inputs/outputs in the problem_statement. These will be added automatically by the system.
- DO NOT use any markdown formatting — no ###, no **, no backticks, no ---, no bullet points with -.
- Focus ONLY on describing the problem scenario, requirements, and what the candidate must compute.
- Write in plain sentences only.
- Return JSON ONLY. No markdown.
- CRITICAL: You MUST escape any internal double quotes inside strings (e.g., use \\" instead of ") to ensure valid JSON!
- Title must be unique and related to the JD.
- Problem statement must be clear enough for a student to understand in 30 seconds.
"""

        # Check if skeleton has pre-defined problem statement -- skip AI if so
        if skeleton.get('problem_statement'):
            # Use pre-defined problem statement directly (human-controlled story depth)
            challenge = {
                "title": skeleton.get('title_hint', skeleton['id']).split('/')[0].strip(),
                "difficulty": skeleton['difficulty'],
                "topic": skeleton['title_hint'].split('/')[0].strip(),
                "problem_statement": skeleton['problem_statement'],
                "constraints": skeleton.get('constraints', 'N <= 10^5'),
                "explanation": skeleton.get('explanation', ''),
                "input_generator_schema": skeleton['input_schema'],
                "reference_solution": skeleton['gold_solution'],
                "example_input": "N/A",  # Will be generated during verification
                "example_output": "N/A",
                "function_meta": {"name": "solve", "params": [{"name": "data", "type": "string"}], "return_type": "string"}
            }
            generated.append(challenge)
            logger.info(f"SKELETON: Used PRE-DEFINED problem statement for '{skeleton['id']}' ({skeleton['difficulty']})")
            continue

        for attempt in range(attempts_per_batch):
            try:
                result = _call_llm_with_backoff(
                    llm_client,
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
def _generate_execution_verified_coding_pool(*, llm_client, job_description, required_skills, difficulties, total_required, model="deepseek-v4-flash", cancel_token=None):
    """
    Entry point for skeleton-based generation.
    1. Generates the pool using skeletons.
    2. Runs each skeleton once to populate example_input/output.
    """
    # 1. Generate story-wrapped skeletons
    challenges = _generate_coding_pool_ai_only(
        llm_client=llm_client,
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
                
                # Strip any AI-included examples/input format to prevent duplication
                challenge['problem_statement'] = _strip_ai_examples(challenge['problem_statement'])
                
                # Auto-generate Input Format from schema and append
                input_format = _generate_input_format(schema)
                challenge['problem_statement'] += input_format
                
                # Append formatted, verified example to description
                challenge['problem_statement'] += (
                    f"\n\n---\n\n### Example 1:\n"
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

def _is_duplicate_mcq(new_question, existing_questions, threshold=0.92):
    """
    HARD DEDUP: Check if a new MCQ is a near-exact duplicate of another in the CURRENT session.
    Only checks within-assessment uniqueness (not cross-assessment).
    Threshold 0.92 = catches only true repeats/rephrases.
    Returns (is_duplicate: bool, matched_question: str or None)
    """
    if not new_question or not existing_questions:
        return False, None

    new_clean = new_question.lower().strip()[:150]
    if len(new_clean) < 10:
        return False, None

    for existing in existing_questions:
        if not existing:
            continue
        existing_clean = existing.lower().strip()[:150]
        if len(existing_clean) < 10:
            continue

        # Fast pre-check: exact match
        if new_clean == existing_clean:
            return True, existing

        # Similarity check -- 0.92 catches only true repeats
        ratio = SequenceMatcher(None, new_clean, existing_clean).ratio()
        if ratio >= threshold:
            return True, existing

    return False, None


def _generate_mcq_pool_ai_only(
    *,
    llm_client,
    job_description,
    required_skills,
    pool_mcq_total,
    pool_easy,
    pool_medium,
    pool_hard,
    experience_level=None,
    attempts_per_batch=20, # INCREASED: Maximum persistence for rotation
    blacklist_qs=None,
    model="deepseek-v4-flash",
    cancel_token=None
):
    """Generate MCQs via dedicated AI-only calls per difficulty to satisfy strict split."""
    # Add a random salt to ensure diversity across sessions
    salt = str(random.getrandbits(32))
    blacklist = blacklist_qs or []

    # Get experience-level guidelines
    exp_guidelines = _get_experience_guidelines(experience_level or 'mid')
    
    # EXPERIENCE-LEVEL AWARE DIFFICULTY ADJUSTMENT
    if experience_level:
        total_questions = pool_easy + pool_medium + pool_hard
        if total_questions > 0:
            dist = exp_guidelines['difficulty_distribution']
            pool_easy = int(total_questions * dist['easy'])
            pool_medium = int(total_questions * dist['medium'])
            pool_hard = max(1, total_questions - pool_easy - pool_medium)  # At least 1 hard
            logger.info(f"Experience-adjusted distribution for {experience_level}: Easy={pool_easy}, Medium={pool_medium}, Hard={pool_hard}")

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
            avoid_list = (blacklist + [q.get('question', '')[:80] for q in generated])[:50]
            avoid_txt = f"Exclude topics: {avoid_list}" if avoid_list else ""
            
            # Build experience-specific guidance
            exp_focus = exp_guidelines['focus']
            exp_avoid = exp_guidelines['avoid']
            exp_topics = '\n'.join([f"- {topic}" for topic in exp_guidelines['topics'][:8]])  # Limit to 8 topics
            exp_prompt_guidance = exp_guidelines['prompt_guidance']
            
            prompt = f"""
            JOB DESCRIPTION: {job_description[:800]}
            REQUIRED SKILLS: {required_skills[:400] if required_skills else 'General Programming'}
            EXPERIENCE LEVEL: {exp_guidelines['description']}

            EXPERIENCE-LEVEL GUIDELINES:
            FOCUS ON: {exp_focus}
            AVOID: {exp_avoid}

            APPROPRIATE TOPICS FOR THIS LEVEL:
            {exp_topics}

            TASK: Generate {count} technical MCQs for {difficulty} difficulty level.
            {exp_prompt_guidance}

            CHAIN-OF-THOUGHT REQUIREMENT (Layer 1 Accuracy):
            Before writing each question, mentally:
            1. Pick a specific concept from the JD/skills
            2. Solve or reason through the correct answer yourself
            3. Write the question based on your reasoning
            4. Write 3 wrong options that are PROVABLY and CLEARLY wrong
            5. Confirm the correct answer is 100% accurate

            CRITICAL REQUIREMENTS:
            1. EXPERIENCE-APPROPRIATE: Questions MUST match the {exp_guidelines['description']} level
            2. JD-RELEVANT: Focus on skills mentioned in the job description
            3. UNIQUE CONCEPTS: Each question MUST test a DIFFERENT specific concept
            4. ACCURACY: Every correct answer must be factually correct. Every wrong option must be genuinely wrong.
            5. WRONG OPTIONS: Must be plausible but clearly incorrect -- never accidentally correct

            QUESTION COMPLEXITY BY DIFFICULTY:
            - Easy: Basic concepts, syntax, fundamental usage
            - Medium: Common patterns, best practices, debugging scenarios
            - Hard: Complex scenarios, optimization, advanced concepts (but still appropriate for experience level)

            JSON FORMAT: {{ "mcqs": [ {{ "question": "In Python, which method is used to add an element to the end of a list?", "options": ["append()", "add()", "insert()", "push()"], "answer": "append()", "difficulty": "{difficulty}" }} ] }}

            STRICT RULES:
            - Generate valid JSON only (do NOT use escape sequences)
            - UNIQUE: Every question must cover a DIFFERENT sub-topic. {avoid_txt}
            - OPTIONS MUST BE DESCRIPTIVE: Each option MUST be actual answer text (NOT just "A", "B", "C", "D")
            - NO PLACEHOLDERS: NEVER use options like "Option A", "Option B", "Choice 1", etc.
            - ANSWER FIELD: The answer MUST be the exact text from one of the options
            - Each question gets exactly 4 options and 1 correct answer
            """
            batch_mcqs = []

            for attempt in range(attempts_per_batch):
                if cancel_token and cache.get(f"abort_{cancel_token}"):
                    raise Exception("Generation Aborted by User")
                
                remaining = count - len(batch_mcqs)
                if remaining <= 0:
                    break  # Already have enough from previous attempts
                
                # Update prompt to only ask for remaining count
                current_prompt = f"""
            JOB DESCRIPTION: {job_description[:800]}
            REQUIRED SKILLS: {required_skills[:400] if required_skills else 'General Programming'}
            EXPERIENCE LEVEL: {exp_guidelines['description']}

            EXPERIENCE-LEVEL GUIDELINES:
            FOCUS ON: {exp_focus}
            AVOID: {exp_avoid}

            APPROPRIATE TOPICS FOR THIS LEVEL:
            {exp_topics}

            TASK: Generate {remaining} technical MCQs for {difficulty} difficulty level.
            {exp_prompt_guidance}

            CHAIN-OF-THOUGHT REQUIREMENT (Layer 1 Accuracy):
            Before writing each question, mentally:
            1. Pick a specific concept from the JD/skills
            2. Solve or reason through the correct answer yourself
            3. Write the question based on your reasoning
            4. Write 3 wrong options that are PROVABLY and CLEARLY wrong
            5. Confirm the correct answer is 100% accurate

            CRITICAL REQUIREMENTS:
            1. EXPERIENCE-APPROPRIATE: Questions MUST match the {exp_guidelines['description']} level
            2. JD-RELEVANT: Focus on skills mentioned in the job description
            3. UNIQUE CONCEPTS: Each question MUST test a DIFFERENT specific concept
            4. ACCURACY: Every correct answer must be factually correct. Every wrong option must be genuinely wrong.
            5. WRONG OPTIONS: Must be plausible but clearly incorrect -- never accidentally correct

            QUESTION COMPLEXITY BY DIFFICULTY:
            - Easy: Basic concepts, syntax, fundamental usage
            - Medium: Common patterns, best practices, debugging scenarios
            - Hard: Complex scenarios, optimization, advanced concepts (but still appropriate for experience level)

            JSON FORMAT: {{ "mcqs": [ {{ "question": "In Python, which method is used to add an element to the end of a list?", "options": ["append()", "add()", "insert()", "push()"], "answer": "append()", "difficulty": "{difficulty}" }} ] }}

            STRICT RULES:
            - Generate valid JSON only (do NOT use escape sequences)
            - UNIQUE: Every question must cover a DIFFERENT sub-topic. {avoid_txt}
            - OPTIONS MUST BE DESCRIPTIVE: Each option MUST be actual answer text (NOT just "A", "B", "C", "D")
            - NO PLACEHOLDERS: NEVER use options like "Option A", "Option B", "Choice 1", etc.
            - ANSWER FIELD: The answer MUST be the exact text from one of the options
            - Each question gets exactly 4 options and 1 correct answer
            """

                try:
                    response = _call_llm_with_backoff(
                        llm_client,
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a senior technical interviewer. Generate specific, deep questions that test real knowledge -- not surface-level definitions. Output JSON only."},
                            {"role": "user", "content": current_prompt},
                        ],
                        response_format={"type": "json_object"},
                        max_tokens=4096,
                        temperature=0.7,
                    )
                    
                    if not response:
                        logger.warning(f"Empty/Invalid response on attempt {attempt + 1}")
                        continue

                    parsed = _normalize_generated_pool(response if isinstance(response, dict) else (extract_json(response) or {}))
                    mcqs = parsed.get('mcqs', [])
                    same_diff = [q for q in mcqs if _normalize_difficulty_label(q.get('difficulty')) == difficulty]

                    # VALIDATE each MCQ structure + WITHIN-SESSION DEDUP before accepting
                    new_valid_count = 0
                    session_qs = [q.get('question', '') for q in generated] + [q.get('question', '') for q in batch_mcqs]
                    for q in same_diff:
                        if len(batch_mcqs) >= count:
                            break  # Already accumulated enough
                        is_valid, error_msg = _validate_mcq_structure(q)
                        if not is_valid:
                            logger.debug(f"MCQ VALIDATION FAILED: {error_msg}. Question: {q.get('question', '')[:40]}...")
                            continue
                        # WITHIN-SESSION DEDUP: Check against ALL accepted questions (generated + batch_mcqs)
                        is_dup, matched = _is_duplicate_mcq(q.get('question', ''), session_qs)
                        if is_dup:
                            logger.warning(f"MCQ DUPLICATE REJECTED: '{q.get('question', '')[:50]}...'")
                            continue
                        # AI ACCURACY VERIFICATION (Layer 2 + Layer 4)
                        ai_passed, ai_reason = _ai_verify_mcq(q, llm_client, model)
                        if not ai_passed:
                            logger.warning(f"MCQ AI-VERIFY REJECTED: '{q.get('question', '')[:50]}...' Reason: {ai_reason[:60]}")
                            continue
                        batch_mcqs.append(q)
                        session_qs.append(q.get('question', ''))
                        new_valid_count += 1

                    logger.info(f"MCQ Batch attempt {attempt + 1}: +{new_valid_count} valid {difficulty} MCQs (total accumulated: {len(batch_mcqs)}/{count})")
                    
                    if len(batch_mcqs) >= count:
                        break  # Done! We have enough

                except APIStatusError as e:
                    if e.status_code == 413 and batch_size > 2:
                        logger.warning(f"Batch {batch_size} too large (413). Auto-scaling down to {batch_size-2}...")
                        batch_size -= 2
                        break # Exits "attempts" loop but stays in "while idx" loop
                    raise e
                except Exception as e:
                    logger.warning(f"MCQ Batch attempt {attempt + 1} failed: {e}")
                    if attempt == attempts_per_batch - 1:
                        break

            if not batch_mcqs:
                # RECOVERY: If a batch fails, log and retry with single regeneration
                logger.error(
                    f"❌ MCQ Batch VALIDATION FAILED all {attempts_per_batch} attempts for {difficulty} ({count} questions). "
                    f"Will be replaced via repair pool shortfall mechanism."
                )
                idx += count # Advance so we don't get stuck in a loop, but we accept the shortfall
                continue

            batch_mcqs = batch_mcqs[:count]  # Trim to exact count needed
            for q in batch_mcqs:
                q['difficulty'] = difficulty
            generated.extend(batch_mcqs)
            idx += count
            
        # FINAL RESCUE: If we still have a shortfall, fill it one-by-one to avoid all limits
        gap_attempts = 0
        MAX_GAP_ATTEMPTS = 30  # Safety cap to prevent infinite loops when dedup rejects many
        while len([q for q in generated if q.get('difficulty') == difficulty]) < total_count_for_diff and gap_attempts < MAX_GAP_ATTEMPTS:
            gap_attempts += 1
            if cancel_token and cache.get(f"abort_{cancel_token}"):
                raise Exception("Generation Aborted by User")
                
            shortfall = total_count_for_diff - len([q for q in generated if q.get('difficulty') == difficulty])
            logger.info(f"MCQ Resilient Gap-Filler (attempt {gap_attempts}/{MAX_GAP_ATTEMPTS}): Generating {shortfall} more {difficulty} MCQs one-by-one.")
            
            # Expanded exclude list for better AI awareness of existing questions
            existing_topics = [q.get('question', '')[:60] for q in generated][-30:]
            rescue_prompt = f"""
            JD: {job_description} | Skills: {required_skills}
            TASK: Generate EXACTLY 1 UNIQUE technical MCQ ({difficulty}).
            JSON: {{ "mcqs": [ {{ "question": "What is REST?", "options": ["Representational State Transfer architecture", "A testing framework", "A database query language", "A version control system"], "answer": "Representational State Transfer architecture", "difficulty": "{difficulty}" }} ] }}
            RULES:
            - Return JSON only.
            - OPTIONS MUST BE DESCRIPTIVE: Each option MUST be actual answer text (NOT placeholder letters like "A", "B" or "Option A").
            - NO PLACEHOLDERS: NEVER use "Option A", "Choice 1", etc.
            - The answer field MUST be the exact text from one of the options.
            - CRITICAL: Generate a completely UNIQUE question. Do NOT repeat or rephrase any of these existing questions:
              {existing_topics}
            """
            try:
                resp = _call_llm_with_backoff(
                    llm_client, 
                    model=model, 
                    messages=[{"role": "user", "content": rescue_prompt}], 
                    response_format={"type": "json_object"},
                    max_tokens=1024
                )
                rescue_mcqs = _normalize_generated_pool((resp if isinstance(resp, dict) else extract_json(resp)) or {}).get('mcqs', [])
                session_qs = [q.get('question', '') for q in generated]
                for rq in rescue_mcqs:
                    # Validate each rescue MCQ
                    is_valid, error_msg = _validate_mcq_structure(rq)
                    if not is_valid:
                        logger.warning(f"Gap-Filler MCQ validation failed: {error_msg}")
                        continue
                    # WITHIN-SESSION DEDUP: Only check against current assessment's questions
                    is_dup, matched = _is_duplicate_mcq(rq.get('question', ''), session_qs)
                    if is_dup:
                        logger.warning(f"Gap-Filler DUPLICATE REJECTED: '{rq.get('question', '')[:50]}...'")
                        continue
                    # AI ACCURACY VERIFICATION (Layer 2 + Layer 4)
                    ai_passed, ai_reason = _ai_verify_mcq(rq, llm_client, model)
                    if not ai_passed:
                        logger.warning(f"Gap-Filler AI-VERIFY REJECTED: '{rq.get('question', '')[:50]}...' Reason: {ai_reason[:60]}")
                        continue

                    rq['difficulty'] = difficulty
                    generated.append(rq)
                    session_qs.append(rq.get('question', ''))
                    logger.info(f"✅ Gap-Filler added 1 UNIQUE {difficulty} MCQ. Total {difficulty}: {len([q for q in generated if q.get('difficulty') == difficulty])}/{total_count_for_diff}")
                    if len([q for q in generated if q.get('difficulty') == difficulty]) >= total_count_for_diff:
                        break
            except Exception as e:
                logger.error(f"Gap-Filler failed (attempt {gap_attempts}): {e}. Retrying...")

            # Delay to mitigate Groq Rate Limits (TPM/RPM)
            time.sleep(2)
        
        if gap_attempts >= MAX_GAP_ATTEMPTS:
            final_count = len([q for q in generated if q.get('difficulty') == difficulty])
            logger.warning(f"Gap-Filler reached max attempts ({MAX_GAP_ATTEMPTS}). {difficulty}: {final_count}/{total_count_for_diff}")

    return generated

def _expert_assessment_refiner(llm_client, raw_content, cancel_token=None):
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
        response = _call_llm_with_backoff(
            llm_client,
            model="deepseek-v4-flash",
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
        MCQs are distributed using a PARTITIONED approach -- the pool is shuffled
        with a deterministic batch-level seed (assessment.batch_id), then sliced
        so each candidate gets a non-overlapping slice. Like dealing cards from
        a shuffled deck.
    - Otherwise (same_questions_for_all=True or no index given):
        Questions are randomly sampled with the email-based seed (reproducible
        but may overlap between candidates).

    Coding challenges are always unique -- they are removed from the pool after
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