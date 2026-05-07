"""
Middleware for rate limiting and request queuing for AI interview scaling
"""
import time
import json
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class InterviewRateLimitMiddleware:
    """
    Rate limiting middleware for AI interview endpoints
    Prevents system overload during high concurrency
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate limiting configuration
        self.RATE_LIMITS = {
            'process-answer': {
                'requests_per_minute': 100,  # 100 requests per minute
                'burst_size': 20,             # Allow bursts of 20
                'window_size': 60             # 1 minute window
            },
            'process-answer-async': {
                'requests_per_minute': 200,  # Higher limit for async
                'burst_size': 50,
                'window_size': 60
            },
            'default': {
                'requests_per_minute': 1000,
                'burst_size': 100,
                'window_size': 60
            }
        }
    
    def __call__(self, request):
        # Only rate limit AI interview endpoints
        if self._should_rate_limit(request):
            client_ip = self._get_client_ip(request)
            endpoint_key = self._get_endpoint_key(request)
            
            # Check rate limit
            if not self._check_rate_limit(client_ip, endpoint_key):
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.',
                    'retry_after': 60
                }, status=429)
        
        return self.get_response(request)
    
    def _should_rate_limit(self, request):
        """Check if request should be rate limited"""
        path = request.path
        return any(endpoint in path for endpoint in [
            '/process-answer',
            '/process-answer-async',
            '/task-status'
        ])
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    
    def _get_endpoint_key(self, request):
        """Get rate limit key for endpoint"""
        path = request.path
        if 'process-answer-async' in path:
            return 'process-answer-async'
        elif 'process-answer' in path:
            return 'process-answer'
        return 'default'
    
    def _check_rate_limit(self, client_ip, endpoint_key):
        """Check if request is within rate limits"""
        rate_config = self.RATE_LIMITS.get(endpoint_key, self.RATE_LIMITS['default'])
        
        # Cache keys
        bucket_key = f"rate_limit:{endpoint_key}:{client_ip}"
        burst_key = f"burst_limit:{endpoint_key}:{client_ip}"
        
        current_time = int(time.time())
        window_start = current_time - rate_config['window_size']
        
        # Get current request count
        request_count = cache.get(bucket_key, 0)
        burst_count = cache.get(burst_key, 0)
        
        # Check burst limit first (more restrictive)
        if burst_count >= rate_config['burst_size']:
            logger.warning(f"Burst limit exceeded for {client_ip} on {endpoint_key}")
            return False
        
        # Check rate limit
        if request_count >= rate_config['requests_per_minute']:
            logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint_key}")
            return False
        
        # Increment counters
        cache.set(bucket_key, request_count + 1, rate_config['window_size'])
        cache.set(burst_key, burst_count + 1, 10)  # Burst counter resets faster
        
        # Clean old entries (simple cleanup)
        if request_count % 10 == 0:
            self._cleanup_old_entries(window_start)
        
        return True
    
    def _cleanup_old_entries(self, cutoff_time):
        """Clean up old rate limit entries"""
        # This is a simplified cleanup - in production, use more efficient methods
        pass


class InterviewQueueMiddleware:
    """
    Request queuing middleware for AI interview processing
    Implements intelligent queue management for high load
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Queue configuration
        self.QUEUE_CONFIG = {
            'max_queue_size': 500,        # Maximum requests in queue
            'queue_timeout': 300,         # 5 minutes max wait time
            'priority_threshold': 80,     # System load percentage for priority queuing
        }
    
    def __call__(self, request):
        # Only queue AI interview processing endpoints
        if self._should_queue(request):
            queue_status = self._check_queue_status()
            
            if queue_status['overloaded']:
                return JsonResponse({
                    'error': 'System overloaded',
                    'message': 'Interview system is currently at capacity. Please try again in a few minutes.',
                    'queue_size': queue_status['queue_size'],
                    'estimated_wait': queue_status['estimated_wait']
                }, status=503)
        
        return self.get_response(request)
    
    def _should_queue(self, request):
        """Check if request should be queued"""
        path = request.path
        return 'process-answer' in path
    
    def _check_queue_status(self):
        """Check current queue status and system load"""
        try:
            # Get current queue size from Celery
            from celery import current_app
            inspect = current_app.control.inspect()
            
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()
            reserved_tasks = inspect.reserved()
            
            queue_size = (
                sum(len(tasks) for tasks in (active_tasks or {}).values()) +
                sum(len(tasks) for tasks in (scheduled_tasks or {}).values()) +
                sum(len(tasks) for tasks in (reserved_tasks or {}).values())
            )
            
            # Get system capacity
            from ai_assessments.ai_logic import GroqKeyManager
            key_stats = GroqKeyManager.get_usage_stats()
            total_capacity = len(key_stats.get('usage_per_key', {})) * 30  # 30 req/min per key
            
            # Calculate system load
            system_load = (queue_size / total_capacity * 100) if total_capacity > 0 else 0
            
            # Estimate wait time (rough calculation)
            estimated_wait = max(0, (queue_size / total_capacity) * 60) if total_capacity > 0 else 0
            
            return {
                'queue_size': queue_size,
                'system_load': system_load,
                'overloaded': queue_size > self.QUEUE_CONFIG['max_queue_size'] or system_load > self.QUEUE_CONFIG['priority_threshold'],
                'estimated_wait': min(estimated_wait, self.QUEUE_CONFIG['queue_timeout'])
            }
            
        except Exception as e:
            logger.error(f"Error checking queue status: {e}")
            return {
                'queue_size': 0,
                'system_load': 0,
                'overloaded': False,
                'estimated_wait': 0
            }


class InterviewHealthCheckMiddleware:
    """
    Health check middleware for AI interview system
    Provides system health information for load balancers
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path == '/ai-interview-health':
            return self._health_check_response()
        
        return self.get_response(request)
    
    def _health_check_response(self):
        """Return system health status"""
        try:
            health_data = {
                'status': 'healthy',
                'timestamp': time.time(),
                'checks': {}
            }
            
            # Database health
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                health_data['checks']['database'] = 'healthy'
            except Exception as e:
                health_data['checks']['database'] = f'unhealthy: {str(e)}'
                health_data['status'] = 'degraded'
            
            # Redis health (if configured)
            try:
                cache.set('health_check', 'ok', 10)
                cache.get('health_check')
                health_data['checks']['redis'] = 'healthy'
            except Exception as e:
                health_data['checks']['redis'] = f'unhealthy: {str(e)}'
                health_data['status'] = 'degraded'
            
            # Celery health
            try:
                from celery import current_app
                inspect = current_app.control.inspect()
                stats = inspect.stats()
                if stats:
                    health_data['checks']['celery'] = 'healthy'
                else:
                    health_data['checks']['celery'] = 'no workers'
                    health_data['status'] = 'degraded'
            except Exception as e:
                health_data['checks']['celery'] = f'unhealthy: {str(e)}'
                health_data['status'] = 'unhealthy'
            
            # Groq API health
            try:
                from ai_assessments.ai_logic import GroqKeyManager
                key_stats = GroqKeyManager.get_usage_stats()
                health_data['checks']['groq_api'] = {
                    'status': 'healthy',
                    'keys_available': key_stats['total_keys'],
                    'usage_stats': key_stats['usage_per_key']
                }
            except Exception as e:
                health_data['checks']['groq_api'] = f'unhealthy: {str(e)}'
                health_data['status'] = 'degraded'
            
            # Queue status
            try:
                from celery import current_app
                inspect = current_app.control.inspect()
                active_tasks = inspect.active() or {}
                queue_size = sum(len(tasks) for tasks in active_tasks.values())
                
                health_data['checks']['queue'] = {
                    'status': 'healthy' if queue_size < 100 else 'busy',
                    'active_tasks': queue_size
                }
                
                if queue_size > 200:
                    health_data['status'] = 'busy'
                    
            except Exception as e:
                health_data['checks']['queue'] = f'unhealthy: {str(e)}'
                health_data['status'] = 'degraded'
            
            status_code = 200 if health_data['status'] == 'healthy' else 503
            
            return JsonResponse(health_data, status=status_code)
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }, status=503)
