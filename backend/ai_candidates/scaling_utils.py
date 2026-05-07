"""
Scaling utilities for AI Interview System
- Response caching
- Rate limiting
- Health checks
"""
import hashlib
import time
import functools
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter using Django cache (Redis)."""
    
    def __init__(self, key_prefix, max_requests, window_seconds):
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window = window_seconds
    
    def is_allowed(self, identifier='global'):
        """Check if request is within rate limit."""
        key = f"{self.key_prefix}:{identifier}"
        
        # Get current count
        current = cache.get(key, 0)
        
        if current >= self.max_requests:
            return False
        
        # Increment and set expiry if first request
        if current == 0:
            cache.set(key, 1, timeout=self.window)
        else:
            cache.incr(key)
        
        return True
    
    def get_remaining(self, identifier='global'):
        """Get remaining requests in current window."""
        key = f"{self.key_prefix}:{identifier}"
        current = cache.get(key, 0)
        return max(0, self.max_requests - current)


# Global rate limiters - scaled for 100+ concurrent interviews
# Each key can handle 30 req/min, so with 3 keys = 90 req/min total
llm_limiter = RateLimiter("llm_api", max_requests=90, window_seconds=60)
# Backward-compatible alias
groq_limiter = llm_limiter
tts_limiter = RateLimiter("tts_api", max_requests=200, window_seconds=60)


def cache_ai_response(timeout=300):
    """
    Decorator to cache AI responses based on prompt content.
    Only caches successful responses.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key_parts = [func.__name__]
            
            # Add args to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    cache_key_parts.append(str(arg))
            
            # Add kwargs to key (sorted for consistency)
            for key in sorted(kwargs.keys()):
                val = kwargs[key]
                if isinstance(val, (str, int, float, bool)):
                    cache_key_parts.append(f"{key}={val}")
            
            # Create hash
            key_string = "|".join(cache_key_parts)
            cache_key = f"ai_cache:{hashlib.md5(key_string.encode()).hexdigest()}"
            
            # Check cache
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"AI cache hit for {func.__name__}")
                return cached
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache successful results
            if result and not isinstance(result, Exception):
                cache.set(cache_key, result, timeout=timeout)
                logger.debug(f"AI cache set for {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


def rate_limit(limiter, identifier_func=None):
    """
    Decorator to apply rate limiting.
    
    Args:
        limiter: RateLimiter instance
        identifier_func: Function to extract identifier from request
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get identifier
            if identifier_func:
                identifier = identifier_func(request)
            else:
                identifier = 'global'
            
            # Check rate limit
            if not limiter.is_allowed(identifier):
                from rest_framework.response import Response
                from rest_framework import status
                
                remaining = limiter.get_remaining(identifier)
                return Response({
                    'error': 'Rate limit exceeded. Please try again in a moment.',
                    'retry_after': limiter.window,
                    'remaining': remaining
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def get_system_health():
    """Get current system health metrics."""
    # Get system resources (psutil is optional)
    resources = {}
    try:
        import psutil
        resources = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }
    except ImportError:
        resources = {
            'cpu_percent': None,
            'memory_percent': None,
            'disk_percent': None,
            'note': 'psutil not installed'
        }
    
    # Get Redis connection status
    redis_status = 'unknown'
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', timeout=5)
        redis_status = 'connected' if cache.get('health_check') == 'ok' else 'disconnected'
    except Exception as e:
        redis_status = f'error: {str(e)}'
    
    # Get database status
    db_status = 'unknown'
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    # Get Celery status
    celery_status = 'unknown'
    try:
        from celery.app.control import Control
        from celery import current_app
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        celery_status = 'connected' if stats else 'disconnected'
    except Exception as e:
        celery_status = f'not_configured'
    
    # Determine overall health
    is_healthy = all([
        redis_status == 'connected',
        db_status == 'connected',
        celery_status in ['connected', 'not_configured']
    ])
    
    return {
        'status': 'healthy' if is_healthy else 'degraded',
        'timestamp': time.time(),
        'components': {
            'database': db_status,
            'redis': redis_status,
            'celery': celery_status,
        },
        'resources': resources
    }
