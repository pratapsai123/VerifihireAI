"""
Unified LLM Client for VerifiHireAI
====================================
Provides a single abstraction layer for all AI/LLM calls across the platform.
Currently backed by DeepSeek V4 Flash via the OpenAI-compatible API.

Usage:
    from ai_assessments.llm_client import LLMKeyManager, create_llm_client, call_llm_with_backoff

    # Option A: Direct client usage
    client = create_llm_client()
    response = client.chat.completions.create(
        model=get_default_model(),
        messages=[{"role": "user", "content": "Hello"}],
    )

    # Option B: With automatic retry, key rotation, and backoff
    result = call_llm_with_backoff(
        prompt="Analyze this resume...",
        is_json=True,
        model=get_default_model(),
        max_tokens=2048,
    )
"""

import json
import time
import logging
import threading

from django.conf import settings
from django.core.cache import cache
from openai import OpenAI, RateLimitError, APIStatusError, APIConnectionError, APITimeoutError, BadRequestError

logger = logging.getLogger(__name__)


# ─── Model Configuration ─────────────────────────────────────────────────────

def get_default_model():
    """Returns the primary model identifier from settings."""
    return getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-v4-flash')


def get_base_url():
    """Returns the API base URL from settings."""
    return getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com')


# ─── Key Manager (Thread-Safe Rotation) ──────────────────────────────────────

class LLMKeyManager:
    """
    Thread-safe API key manager with round-robin rotation and usage tracking.
    Drop-in replacement for the old GroqKeyManager.
    """
    _current_index = 0
    _lock = threading.Lock()
    _key_usage_count = {}

    @classmethod
    def _get_keys(cls):
        return getattr(settings, 'DEEPSEEK_API_KEYS', [])

    @classmethod
    def get_current_key(cls):
        keys = cls._get_keys()
        if not keys:
            return getattr(settings, 'DEEPSEEK_API_KEY', None)
        with cls._lock:
            key = keys[cls._current_index % len(keys)]
            cls._key_usage_count[cls._current_index] = cls._key_usage_count.get(cls._current_index, 0) + 1
            return key

    @classmethod
    def get_least_used_key(cls):
        """Get the key with lowest usage count for load balancing."""
        keys = cls._get_keys()
        if not keys:
            return getattr(settings, 'DEEPSEEK_API_KEY', None)
        with cls._lock:
            if not cls._key_usage_count:
                return keys[0]
            min_idx = min(range(len(keys)), key=lambda i: cls._key_usage_count.get(i, 0))
            cls._key_usage_count[min_idx] = cls._key_usage_count.get(min_idx, 0) + 1
            return keys[min_idx]

    @classmethod
    def rotate_key(cls):
        keys = cls._get_keys()
        if keys and len(keys) > 1:
            with cls._lock:
                old_idx = cls._current_index
                cls._current_index = (cls._current_index + 1) % len(keys)
                logger.warning(
                    f"LLM KEY ROTATION: Rate limit reached at index {old_idx}. "
                    f"Switched to key index {cls._current_index}"
                )
                return True
        return False

    @classmethod
    def get_usage_stats(cls):
        """Return usage statistics for monitoring."""
        keys = cls._get_keys()
        with cls._lock:
            return {
                'total_keys': len(keys),
                'current_index': cls._current_index,
                'usage_per_key': {i: cls._key_usage_count.get(i, 0) for i in range(len(keys))}
            }


# ─── Client Factory ──────────────────────────────────────────────────────────

def create_llm_client(api_key=None, timeout=60.0):
    """
    Create an OpenAI-compatible client pointing at DeepSeek.
    The returned client has the exact same interface as the old Groq client:
        client.chat.completions.create(...)
    """
    key = api_key or LLMKeyManager.get_current_key()
    if not key:
        raise ValueError(
            "No DeepSeek API key configured. "
            "Set DEEPSEEK_API_KEY_1 in your .env or settings.py"
        )
    return OpenAI(
        api_key=key,
        base_url=get_base_url(),
        timeout=timeout,
    )


# ─── Unified Call with Backoff ───────────────────────────────────────────────

def call_llm_with_backoff(
    client=None,
    prompt=None,
    system_msg=None,
    is_json=True,
    **kwargs
):
    """
    Wrapper for LLM API calls with exponential backoff and key rotation.
    Drop-in replacement for the old _call_groq_with_backoff.

    Returns parsed JSON dict (if is_json=True) or raw string content.
    """
    max_retries = 10
    base_delay = 5
    model = kwargs.pop('model', get_default_model())

    # 1. Initialize Client if needed
    if client is None:
        client = create_llm_client()

    current_client = client
    attempt = 0
    rotations_this_attempt = 0
    keys_count = len(LLMKeyManager._get_keys()) or 1

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

    while attempt < max_retries:
        try:
            create_kwargs = {
                "model": model,
                "messages": messages,
                **kwargs,
            }
            if response_format:
                create_kwargs["response_format"] = response_format

            resp = current_client.chat.completions.create(**create_kwargs)
            content = resp.choices[0].message.content

            if is_json:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Fallback: try extracting JSON from markdown blocks
                    from ai_candidates.views import extract_json
                    return extract_json(content)
            return content

        except RateLimitError as e:
            # 1. Try rotating to a different API key
            if keys_count > 1 and rotations_this_attempt < keys_count:
                if LLMKeyManager.rotate_key():
                    time.sleep(1)
                    new_key = LLMKeyManager.get_current_key()
                    current_client = create_llm_client(api_key=new_key)
                    logger.info(
                        f"Retrying with rotated API key index {LLMKeyManager._current_index} "
                        f"(Attempt {attempt + 1}/{max_retries})"
                    )
                    rotations_this_attempt += 1
                    continue

            # 2. Full exponential backoff
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), 120)
                logger.warning(
                    f"All LLM keys exhausted. Cooling down for {delay}s... "
                    f"(Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(delay)
                attempt += 1
                rotations_this_attempt = 0
                continue
            raise e

        except BadRequestError as e:
            error_msg = str(e)
            if 'json' in error_msg.lower() or 'format' in error_msg.lower():
                logger.warning(
                    f"LLM JSON Validation Failed: Retrying... "
                    f"(Attempt {attempt + 1}/{max_retries})"
                )
                if attempt < max_retries - 1:
                    time.sleep(1)
                    attempt += 1
                    continue
            logger.error(f"LLM Bad Request (400): {error_msg}")
            raise e

        except APIStatusError as e:
            if e.status_code == 429:
                if keys_count > 1 and rotations_this_attempt < keys_count:
                    if LLMKeyManager.rotate_key():
                        time.sleep(1)
                        new_key = LLMKeyManager.get_current_key()
                        current_client = create_llm_client(api_key=new_key)
                        rotations_this_attempt += 1
                        continue
            if e.status_code == 413:
                if LLMKeyManager.rotate_key():
                    new_key = LLMKeyManager.get_current_key()
                    current_client = create_llm_client(api_key=new_key)
                    continue
                logger.error(f"LLM Request Too Large (413): {e.message}")
                raise e
            raise e

        except (APIConnectionError, APITimeoutError) as e:
            if attempt < max_retries - 1:
                delay = base_delay + attempt
                logger.warning(
                    f"LLM Connection Error: {e}. Retrying in {delay}s... "
                    f"(Attempt {attempt + 1}/{max_retries})"
                )
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

            logger.error(f"LLM API call failed: {e}")
            raise e


# ─── Groq Key Manager (for Resume Screening) ─────────────────────────────────

class GroqKeyManager:
    """
    Thread-safe Groq API key manager with round-robin rotation.
    Used exclusively for resume screening (fast, free-tier Groq).
    Falls back to DeepSeek if all Groq keys are exhausted.
    """
    _current_index = 0
    _lock = threading.Lock()
    _key_usage_count = {}

    @classmethod
    def _get_keys(cls):
        return getattr(settings, 'GROQ_API_KEYS', [])

    @classmethod
    def get_current_key(cls):
        keys = cls._get_keys()
        if not keys:
            return None
        with cls._lock:
            key = keys[cls._current_index % len(keys)]
            cls._key_usage_count[cls._current_index] = cls._key_usage_count.get(cls._current_index, 0) + 1
            return key

    @classmethod
    def get_least_used_key(cls):
        keys = cls._get_keys()
        if not keys:
            return None
        with cls._lock:
            if not cls._key_usage_count:
                return keys[0]
            min_idx = min(range(len(keys)), key=lambda i: cls._key_usage_count.get(i, 0))
            cls._key_usage_count[min_idx] = cls._key_usage_count.get(min_idx, 0) + 1
            return keys[min_idx]

    @classmethod
    def rotate_key(cls):
        keys = cls._get_keys()
        if keys and len(keys) > 1:
            with cls._lock:
                old_idx = cls._current_index
                cls._current_index = (cls._current_index + 1) % len(keys)
                logger.warning(
                    f"GROQ KEY ROTATION: Rate limit at index {old_idx}. "
                    f"Switched to key index {cls._current_index}"
                )
                return True
        return False

    @classmethod
    def get_usage_stats(cls):
        keys = cls._get_keys()
        with cls._lock:
            return {
                'total_keys': len(keys),
                'current_index': cls._current_index,
                'usage_per_key': {i: cls._key_usage_count.get(i, 0) for i in range(len(keys))}
            }


def create_groq_client(api_key=None, timeout=60.0):
    """
    Create an OpenAI-compatible client pointing at Groq.
    Used for resume screening — fast and free-tier friendly.
    """
    key = api_key or GroqKeyManager.get_current_key()
    if not key:
        raise ValueError(
            "No Groq API key configured. "
            "Set GROQ_API_KEYS in settings.py"
        )
    return OpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1",
        timeout=timeout,
    )


def get_groq_model():
    """Returns the primary Groq model (70b) for resume screening."""
    return getattr(settings, 'GROQ_MODEL_PRIMARY', 'llama-3.3-70b-versatile')


def get_groq_fallback_model():
    """Returns the fallback Groq model (8b) when all 70b attempts fail."""
    return getattr(settings, 'GROQ_MODEL_FALLBACK', 'llama3-8b-8192')


def call_groq_with_backoff(
    client=None,
    prompt=None,
    system_msg=None,
    is_json=True,
    **kwargs
):
    """
    Groq-only wrapper with 2-phase model fallback + circular key rotation.
    NO DeepSeek — Groq only.

    Phase 1 (70b):  Key 1 → Key 2 → Key 3
    Phase 2 (8b):   Key 1 → Key 2 → Key 3  (if ALL 70b attempts failed)

    If Phase 2 also fully fails → raises RuntimeError.
    """
    keys = GroqKeyManager._get_keys()
    if not keys:
        raise ValueError("No GROQ_API_KEYS configured in settings.py")

    primary_model  = get_groq_model()           # 70b
    fallback_model = get_groq_fallback_model()  # 8b

    # Pop model kwarg — we control the model internally
    kwargs.pop('model', None)

    # Build messages
    messages = kwargs.pop('messages', [])
    if not messages and prompt:
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": prompt})

    response_format = kwargs.pop('response_format', None)
    if not response_format and is_json:
        response_format = {"type": "json_object"}

    def _try_key(model, key_idx):
        """Single attempt with a specific model + key. Returns result or raises."""
        groq_key = keys[key_idx]
        groq_client = create_groq_client(api_key=groq_key)
        create_kwargs = {"model": model, "messages": messages, **kwargs}
        if response_format:
            create_kwargs["response_format"] = response_format
        resp = groq_client.chat.completions.create(**create_kwargs)
        content = resp.choices[0].message.content
        if is_json:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                from ai_candidates.views import extract_json
                return extract_json(content)
        return content

    def _is_rate_limit(e):
        err = str(e).lower()
        return isinstance(e, RateLimitError) or "429" in err or "rate" in err

    # ── Phase 1: 70b across all 3 keys ──────────────────────────────────────
    logger.info(f"Groq Phase 1: trying {primary_model} across {len(keys)} keys")
    for key_idx in range(len(keys)):
        try:
            result = _try_key(primary_model, key_idx)
            logger.info(f"Groq Phase 1 success: {primary_model} key {key_idx + 1}")
            return result
        except (RateLimitError, APIConnectionError, APITimeoutError) as e:
            logger.warning(
                f"Groq Phase 1 — {primary_model} key {key_idx + 1}/{len(keys)} failed: {type(e).__name__}. "
                f"{'Trying next key...' if key_idx < len(keys) - 1 else 'All 70b keys exhausted.'}"
            )
            time.sleep(2)
            continue
        except Exception as e:
            if _is_rate_limit(e):
                logger.warning(f"Groq Phase 1 — {primary_model} key {key_idx + 1} rate-limited. Rotating...")
                time.sleep(2)
                continue
            logger.error(f"Groq Phase 1 — {primary_model} key {key_idx + 1} error: {e}. Rotating...")
            time.sleep(1)
            continue

    # ── Phase 2: 8b across all 3 keys (starting from Key 1 again) ───────────
    logger.warning(
        f"Groq Phase 1 fully exhausted ({primary_model}). "
        f"Starting Phase 2 with {fallback_model} from Key 1."
    )
    for key_idx in range(len(keys)):
        try:
            result = _try_key(fallback_model, key_idx)
            logger.info(f"Groq Phase 2 success: {fallback_model} key {key_idx + 1}")
            return result
        except (RateLimitError, APIConnectionError, APITimeoutError) as e:
            logger.warning(
                f"Groq Phase 2 — {fallback_model} key {key_idx + 1}/{len(keys)} failed: {type(e).__name__}. "
                f"{'Trying next key...' if key_idx < len(keys) - 1 else 'All 8b keys exhausted.'}"
            )
            time.sleep(2)
            continue
        except Exception as e:
            if _is_rate_limit(e):
                logger.warning(f"Groq Phase 2 — {fallback_model} key {key_idx + 1} rate-limited. Rotating...")
                time.sleep(2)
                continue
            logger.error(f"Groq Phase 2 — {fallback_model} key {key_idx + 1} error: {e}. Rotating...")
            time.sleep(1)
            continue

    raise RuntimeError(
        f"Groq resume screening failed completely. "
        f"Phase 1 ({primary_model}) and Phase 2 ({fallback_model}) both exhausted all {len(keys)} keys."
    )


# ─── Backward Compatibility Aliases ──────────────────────────────────────────
# These allow existing code that imports GroqKeyManager to continue working.

_call_groq_with_backoff = call_llm_with_backoff
