"""
Plagiarism Detection Engine — VerifiHireAI
==========================================
Algorithm : Token-Based Winnowing (MOSS-style k-gram fingerprinting)
Standard  : Industry-grade — same algorithm used by Stanford MOSS, JPlag, Dolos
Language  : Pure Python — uses ONLY built-in stdlib (re, hashlib, itertools)
Zero deps : No pip install, no API key, no internet required.

How It Works
------------
1. Remove all comments (single-line and multi-line)
2. Normalize all identifiers → IDENT, all numbers → NUM
3. Build overlapping k-grams (windows of K tokens)
4. Hash each k-gram using MD5 into a fingerprint
5. Apply winnowing: select minimum hash per sliding window → fingerprint SET
6. Compare two fingerprint sets using Jaccard Similarity
   Jaccard = |intersection| / |union| × 100

Immune To
---------
- Variable/function renaming  (IDENT normalization)
- Comment changes             (comment stripping)
- Whitespace / formatting     (normalization)
- String/number literal changes (NUM normalization)

NOT Immune To (known limitations)
----------------------------------
- Full semantic rewrites (e.g. bubble sort → merge sort, same logic completely different structure)
- This is expected — no offline tool catches this without AI embeddings

Usage
-----
    from api.utils.plagiarism_checker import check_plagiarism
    result = check_plagiarism(new_submission_id=42, question_id=7)
"""

import re
import hashlib
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ─── Tuning Parameters ────────────────────────────────────────────────────────

KGRAM_SIZE   = 5    # Number of tokens per k-gram (5 is MOSS default)
WINDOW_SIZE  = 4    # Winnowing window size (select 1 min hash per window)

# Similarity thresholds (percentage)
THRESHOLD_CLEAN      = 50   # Below this → clean (no flag)
THRESHOLD_SUSPICIOUS = 75   # Above this → suspicious (logged silently)
THRESHOLD_FLAGGED    = 85   # Above this → flagged for HR review
THRESHOLD_HIGH_RISK  = 93   # Above this → high risk

# ─── Step 1: Code Normalizer ──────────────────────────────────────────────────

def normalize_code(source_code: str) -> str:
    """
    Normalize source code to be language-agnostic and evasion-resistant.

    Transformations applied:
    - Remove Python/Ruby/Bash single-line comments  (# ...)
    - Remove C/C++/Java/JS single-line comments     (// ...)
    - Remove C/C++/Java/JS multi-line comments      (/* ... */)
    - Remove SQL single-line comments               (-- ...)
    - Remove Python docstrings / multi-line strings (\"\"\"...\"\"\" and '''...''')
    - Remove string literals                        ("..." and '...')
    - Normalize all identifiers → IDENT
    - Normalize all numbers     → NUM
    - Collapse whitespace
    """
    code = source_code

    # 1. Remove multi-line block comments: /* ... */
    code = re.sub(r'/\*.*?\*/', ' ', code, flags=re.DOTALL)

    # 2. Remove Python/Java triple-quoted strings (docstrings)
    code = re.sub(r'""".*?"""', ' ', code, flags=re.DOTALL)
    code = re.sub(r"'''.*?'''", ' ', code, flags=re.DOTALL)

    # 3. Remove single-line comments:  // ...  # ...  -- ...
    code = re.sub(r'//.*', ' ', code)
    code = re.sub(r'#.*',  ' ', code)
    code = re.sub(r'--.*', ' ', code)

    # 4. Remove string literals (double-quoted and single-quoted)
    code = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', 'STR', code)
    code = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", 'STR', code)

    # 5. Normalize numbers → NUM (before IDENT to avoid collision)
    code = re.sub(r'\b\d+\.?\d*\b', 'NUM', code)

    # 6. Normalize all identifiers → IDENT
    #    (skip reserved structural tokens like if, for, while, return, class, def, etc.)
    RESERVED = {
        'if', 'else', 'elif', 'for', 'while', 'do', 'switch', 'case',
        'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw',
        'throws', 'new', 'delete', 'import', 'from', 'class', 'def',
        'function', 'var', 'let', 'const', 'int', 'float', 'double',
        'string', 'bool', 'boolean', 'void', 'public', 'private',
        'protected', 'static', 'final', 'abstract', 'override', 'async',
        'await', 'yield', 'lambda', 'pass', 'None', 'True', 'False',
        'null', 'undefined', 'true', 'false', 'self', 'this', 'super',
        'extends', 'implements', 'interface', 'enum', 'struct', 'type',
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'GROUP', 'BY', 'ORDER',
        'HAVING', 'LIMIT', 'OFFSET', 'INNER', 'LEFT', 'RIGHT', 'OUTER',
        'AND', 'OR', 'NOT', 'IN', 'IS', 'NULL', 'AS', 'DISTINCT',
        'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'BETWEEN', 'LIKE',
        'STR', 'NUM', 'IDENT',
    }

    def replace_identifier(match):
        word = match.group(0)
        if word in RESERVED:
            return word
        return 'IDENT'

    code = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', replace_identifier, code)

    # 7. Collapse all whitespace and punctuation into single spaces
    code = re.sub(r'\s+', ' ', code)
    code = code.strip()

    return code


# ─── Step 2: K-gram Builder ───────────────────────────────────────────────────

def build_kgrams(normalized_code: str, k: int = KGRAM_SIZE) -> list:
    """
    Split normalized code into tokens and build overlapping k-grams.

    Example:
        tokens = ['if', 'IDENT', '==', 'NUM', 'return']
        k=3 → kgrams = ['if IDENT ==', 'IDENT == NUM', '== NUM return']
    """
    tokens = normalized_code.split()
    if len(tokens) < k:
        # Code is too short for k-grams — use the whole code as one gram
        return [' '.join(tokens)] if tokens else []

    return [' '.join(tokens[i:i+k]) for i in range(len(tokens) - k + 1)]


# ─── Step 3: Hashing ─────────────────────────────────────────────────────────

def hash_kgram(kgram: str) -> int:
    """Hash a k-gram string into an integer using MD5 (fast, deterministic)."""
    return int(hashlib.md5(kgram.encode('utf-8')).hexdigest(), 16)


# ─── Step 4: Winnowing ───────────────────────────────────────────────────────

def winnow(kgrams: list, window_size: int = WINDOW_SIZE) -> set:
    """
    Apply the Winnowing algorithm to select a representative fingerprint SET.

    For each sliding window of `window_size` hashes, select the minimum hash.
    This produces a compact but representative set of fingerprints.

    Returns a set of integer hashes (the code's fingerprint).
    """
    if not kgrams:
        return set()

    hashes = [hash_kgram(kg) for kg in kgrams]

    if len(hashes) <= window_size:
        # Too short for windowing — use all hashes directly
        return set(hashes)

    fingerprints = set()
    for i in range(len(hashes) - window_size + 1):
        window = hashes[i:i + window_size]
        fingerprints.add(min(window))

    return fingerprints


# ─── Step 5: Similarity ───────────────────────────────────────────────────────

def jaccard_similarity(fp1: set, fp2: set) -> float:
    """
    Compute Jaccard similarity between two fingerprint sets.

    Jaccard = |intersection| / |union| × 100

    Returns a float between 0.0 and 100.0
    """
    if not fp1 or not fp2:
        return 0.0

    intersection = len(fp1 & fp2)
    union = len(fp1 | fp2)

    if union == 0:
        return 0.0

    return round((intersection / union) * 100, 2)


# ─── Step 6: Fingerprint a Single Submission ─────────────────────────────────

def get_fingerprint(source_code: str) -> set:
    """
    Full pipeline: raw source code → fingerprint set.
    normalize → k-grams → winnow → fingerprint set
    """
    if not source_code or not source_code.strip():
        return set()

    normalized = normalize_code(source_code)
    kgrams     = build_kgrams(normalized, k=KGRAM_SIZE)
    fingerprint = winnow(kgrams, window_size=WINDOW_SIZE)
    return fingerprint


# ─── Step 7: Risk Level Classifier ───────────────────────────────────────────

def classify_risk(similarity: float) -> dict:
    """
    Classify the similarity score into a risk level.

    Returns a dict with:
        - level: 'clean' | 'suspicious' | 'flagged' | 'high_risk'
        - label: Human-readable label
        - action: Recommended action
        - color: For UI badge coloring
    """
    if similarity < THRESHOLD_CLEAN:
        return {
            'level':  'clean',
            'label':  'Clean',
            'action': 'No action required',
            'color':  'green',
        }
    elif similarity < THRESHOLD_SUSPICIOUS:
        return {
            'level':  'suspicious',
            'label':  'Suspicious',
            'action': 'Logged silently — no HR review required',
            'color':  'yellow',
        }
    elif similarity < THRESHOLD_FLAGGED:
        return {
            'level':  'flagged',
            'label':  'Flagged for Review',
            'action': 'HR review recommended — may be false positive',
            'color':  'orange',
        }
    else:
        return {
            'level':  'high_risk',
            'label':  'High Risk',
            'action': 'HR review required — strong plagiarism signal',
            'color':  'red',
        }


# ─── Step 8: Main Entry Point ─────────────────────────────────────────────────

def check_plagiarism(new_submission_id: int, question_id: int) -> dict:
    """
    Check a newly saved CodingSubmission against all previous submissions
    for the same question_id using Winnowing fingerprint matching.

    Parameters
    ----------
    new_submission_id : int
        The ID of the newly submitted CodingSubmission.
    question_id : int
        The question's ID — used to scope comparison to same question only.

    Returns
    -------
    dict with:
        checked            : bool
        total_compared     : int
        similarity_score   : float  (0.0 – 100.0)
        matched_submission_id : int | None
        matched_candidate  : str | None
        flagged            : bool
        risk               : dict  (level, label, action, color)
        checked_at         : str   (ISO datetime)
        error              : str | None  (only if something failed)
    """
    from api.models import CodingSubmission

    result_template = {
        'checked':               True,
        'total_compared':        0,
        'similarity_score':      0.0,
        'matched_submission_id': None,
        'matched_candidate':     None,
        'flagged':               False,
        'risk':                  classify_risk(0.0),
        'checked_at':            datetime.now(timezone.utc).isoformat(),
        'error':                 None,
    }

    try:
        # 1. Load the new submission
        try:
            new_sub = CodingSubmission.objects.get(id=new_submission_id)
        except CodingSubmission.DoesNotExist:
            result_template['error'] = f"Submission {new_submission_id} not found"
            result_template['checked'] = False
            return result_template

        new_code = new_sub.submitted_code or ''
        if not new_code.strip():
            result_template['error'] = 'Submitted code is empty'
            result_template['checked'] = False
            return result_template

        # 2. Compute fingerprint for new submission
        new_fp = get_fingerprint(new_code)
        if not new_fp:
            result_template['error'] = 'Code too short to fingerprint'
            result_template['checked'] = False
            return result_template

        # 3. Load all previous submissions for same question (excluding current)
        previous = CodingSubmission.objects.filter(
            question_id=question_id
        ).exclude(
            id=new_submission_id
        ).only(
            'id', 'submitted_code', 'user_email', 'candidate_name'
        ).order_by('-created_at')[:500]   # Cap at 500 for performance

        total_compared = 0
        best_score     = 0.0
        best_match_id  = None
        best_candidate = None

        # 4. Compare against each historical submission
        for prev_sub in previous:
            prev_code = prev_sub.submitted_code or ''
            if not prev_code.strip():
                continue

            prev_fp = get_fingerprint(prev_code)
            if not prev_fp:
                continue

            score = jaccard_similarity(new_fp, prev_fp)
            total_compared += 1

            if score > best_score:
                best_score     = score
                best_match_id  = prev_sub.id
                best_candidate = prev_sub.user_email or prev_sub.candidate_name or f"Submission #{prev_sub.id}"

        # 5. Classify risk
        risk    = classify_risk(best_score)
        flagged = best_score >= THRESHOLD_SUSPICIOUS

        # 6. Log for visibility
        if flagged:
            logger.warning(
                f"[PLAGIARISM] Submission #{new_submission_id} | Question #{question_id} | "
                f"Score: {best_score}% | Matched: #{best_match_id} ({best_candidate}) | "
                f"Risk: {risk['level'].upper()} | Compared: {total_compared}"
            )
        else:
            logger.info(
                f"[PLAGIARISM] Submission #{new_submission_id} | Score: {best_score}% | "
                f"Clean | Compared: {total_compared}"
            )

        return {
            'checked':               True,
            'total_compared':        total_compared,
            'similarity_score':      best_score,
            'matched_submission_id': best_match_id,
            'matched_candidate':     best_candidate,
            'flagged':               flagged,
            'risk':                  risk,
            'checked_at':            datetime.now(timezone.utc).isoformat(),
            'error':                 None,
        }

    except Exception as exc:
        logger.error(f"[PLAGIARISM] Error checking submission #{new_submission_id}: {exc}", exc_info=True)
        result_template['checked'] = False
        result_template['error']   = str(exc)
        return result_template
