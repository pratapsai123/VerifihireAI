# Scaling AI Interview System to 100+ Concurrent Interviews

## Current Architecture Bottlenecks (50-100 capacity)

| Bottleneck | Current State | Impact |
|------------|--------------|--------|
| **Database** | No connection pooling | Connection exhaustion at ~100 concurrent |
| **TTS** | `asyncio.run()` in sync views | Blocks worker threads, 1-3s per request |
| **Groq API** | 3 keys, rate limit ~30 req/min/key | Max ~90 requests/minute across all interviews |
| **Django Workers** | Default sync workers | Each interview holds a worker for entire duration |
| **WebSockets** | One per candidate via Redis | Memory pressure at scale |
| **No Queue** | Direct processing | Backpressure causes cascading failures |

---

## Scaling Strategy Roadmap

### Phase 1: Immediate Fixes (Capacity: 100-200)
**Implementation Time: 1-2 days**

#### 1.1 Database Connection Pooling
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'new_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'root'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30s query timeout
        }
    }
}
```
**Impact**: Reduces connection overhead from ~50ms to ~0ms for pooled connections.

#### 1.2 Async TTS Endpoint
Convert TTS to async Django views:
```python
# views.py
from asgiref.sync import sync_to_async
from django.http import HttpResponse
import asyncio

class AsyncTTSView(APIView):
    permission_classes = [AllowAny]
    
    async def post(self, request):
        text = request.data.get('text', '')
        if not text:
            return Response({"error": "Missing text"}, status=400)
        
        try:
            from .tts_engine import get_tts_engine
            engine = get_tts_engine()
            wav_bytes = await engine.synthesize(text)
            
            response = HttpResponse(wav_bytes, content_type='audio/mpeg')
            response['Cache-Control'] = 'no-cache'
            return response
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return Response({"error": str(e)}, status=500)
```
**Impact**: Frees up worker threads during TTS processing (1-3s saved per request).

#### 1.3 Response Caching for Common Questions
```python
# Cache AI responses for identical contexts
from django.core.cache import cache

def get_cached_or_generate(prompt_hash, generate_func):
    cached = cache.get(f"ai_response:{prompt_hash}")
    if cached:
        return cached
    
    result = generate_func()
    cache.set(f"ai_response:{prompt_hash}", result, timeout=300)  # 5 min cache
    return result
```

---

### Phase 2: Async Architecture (Capacity: 200-500)
**Implementation Time: 3-5 days**

#### 2.1 Convert to ASGI + Async Views
```python
# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Already async-capable
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

#### 2.2 Async Database Queries
```python
from asgiref.sync import sync_to_async

@sync_to_async
def get_candidate_async(candidate_id):
    return Candidate.objects.get(id=candidate_id)

# Usage in async view
candidate = await get_candidate_async(candidate_id)
```

#### 2.3 Batch Groq API Requests
```python
# Queue multiple requests and batch them
import asyncio
from groq import AsyncGroq

class AsyncGroqManager:
    def __init__(self):
        self.clients = [AsyncGroq(api_key=key) for key in settings.GROQ_API_KEYS]
        self.current_idx = 0
    
    async def generate(self, prompt):
        client = self.clients[self.current_idx % len(self.clients)]
        self.current_idx += 1
        
        return await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
```

---

### Phase 3: Queue-Based Processing (Capacity: 500-1000+)
**Implementation Time: 1 week**

#### 3.1 Celery for AI Processing
```python
# tasks.py
from celery import shared_task, group
from celery.exceptions import MaxRetriesExceededError

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def process_interview_answer(self, candidate_id, question, answer, chat_history):
    """Process interview answer asynchronously."""
    try:
        result = generate_ai_response(candidate_id, question, answer, chat_history)
        
        # Store result for polling
        cache.set(f"interview_response:{candidate_id}:{self.request.id}", result, timeout=300)
        
        return result
    except RateLimitError as e:
        # Retry with exponential backoff
        retry_in = 2 ** self.request.retries
        raise self.retry(exc=e, countdown=retry_in)
    except Exception as e:
        logger.error(f"AI processing failed: {e}")
        raise

@shared_task
def batch_process_answers(answer_batch):
    """Process multiple answers in parallel."""
    job = group(
        process_interview_answer.s(**answer) for answer in answer_batch
    )
    result = job.apply_async()
    return result.get()
```

#### 3.2 Polling-Based Response Pattern
```python
# views.py - Submit answer
class SubmitAnswerAsyncView(APIView):
    def post(self, request):
        data = request.data
        
        # Queue the task
        task = process_interview_answer.delay(
            candidate_id=data['candidate_id'],
            question=data['question'],
            answer=data['answer'],
            chat_history=data.get('chat_history', [])
        )
        
        return Response({
            "task_id": task.id,
            "status": "processing",
            "poll_url": f"/api/interview/status/{task.id}/"
        })

# Poll for result
class InterviewStatusView(APIView):
    def get(self, request, task_id):
        result = cache.get(f"interview_response:{task_id}")
        if result:
            return Response({"status": "complete", "data": result})
        
        task = process_interview_answer.AsyncResult(task_id)
        return Response({
            "status": task.status,
            "ready": result is not None
        })
```

#### 3.3 Redis-Based Rate Limiting
```python
import redis
from django.conf import settings

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)

class RateLimiter:
    def __init__(self, key_prefix, max_requests, window_seconds):
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window = window_seconds
    
    def is_allowed(self, identifier):
        key = f"{self.key_prefix}:{identifier}"
        current = redis_client.incr(key)
        
        if current == 1:
            redis_client.expire(key, self.window)
        
        return current <= self.max_requests

# Usage
groq_limiter = RateLimiter("groq_api", max_requests=30, window_seconds=60)

if not groq_limiter.is_allowed("global"):
    return Response({"error": "Rate limit exceeded"}, status=429)
```

---

### Phase 4: Horizontal Scaling (Capacity: 1000+)
**Implementation Time: 1-2 weeks**

#### 4.1 Load Balancer Configuration
```nginx
# nginx.conf
upstream django_backend {
    least_conn;  # Route to least busy worker
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
    keepalive 32;  # Keep connections alive
}

server {
    location /api/ {
        proxy_pass http://django_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts for long-polling
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

#### 4.2 Multiple Django Instances
```bash
# Start multiple Gunicorn workers
# Instance 1
gunicorn VerifiHireAI_backend.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001 --workers 4 --threads 2

# Instance 2
gunicorn VerifiHireAI_backend.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002 --workers 4 --threads 2

# Instance 3
gunicorn VerifiHireAI_backend.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8003 --workers 4 --threads 2

# Instance 4
gunicorn VerifiHireAI_backend.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8004 --workers 4 --threads 2
```

#### 4.3 Shared State with Redis
```python
# Use Redis for:
# - Session storage
# - Interview state
# - WebSocket broadcasts
# - Rate limiting counters

CACHES = {
    'default': {
        'BACKGROUND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

---

## Implementation Priority

### Week 1: Critical Fixes
1. ✅ Database connection pooling (30 min)
2. ✅ Add response caching (2 hours)
3. ✅ Implement rate limiting (2 hours)
4. ✅ Add more Groq API keys (15 min)

### Week 2: Async Migration
1. Convert TTS to async endpoint (1 day)
2. Convert ProcessAnswerView to async (2 days)
3. Add Celery queue for background tasks (1 day)

### Week 3: Queue System
1. Implement polling-based responses (2 days)
2. Add batch processing for AI requests (1 day)
3. Stress testing & optimization (2 days)

### Week 4: Horizontal Scaling
1. Configure load balancer (1 day)
2. Deploy multiple Django instances (1 day)
3. Redis cluster setup (1 day)
4. Production monitoring (2 days)

---

## Monitoring & Alerting

### Key Metrics to Track
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Track AI API latency
ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'Time spent processing AI requests',
    buckets=[.1, .25, .5, 1, 2.5, 5, 10]
)

# Track active interviews
active_interviews = Gauge(
    'active_interviews_total',
    'Number of currently active interviews'
)

# Track rate limit hits
rate_limit_hits = Counter(
    'rate_limit_hits_total',
    'Number of rate limit errors from AI APIs'
)

# Track queue depth
celery_queue_depth = Gauge(
    'celery_queue_depth',
    'Number of pending tasks in Celery queue'
)
```

### Alert Thresholds
- **AI API Latency > 5s**: Investigate Groq API issues
- **Queue Depth > 100**: Scale up workers
- **Rate Limit Errors > 10/min**: Add more API keys
- **Database Connections > 80%**: Enable connection pooling
- **Memory Usage > 85%**: Scale horizontally

---

## Expected Capacity by Phase

| Phase | Concurrent Interviews | Response Time | Infrastructure |
|-------|----------------------|---------------|----------------|
| Current | 50-100 | 2-5s | Single server |
| Phase 1 | 100-200 | 1.5-4s | Single server + Redis |
| Phase 2 | 200-500 | 1-3s | Single server + Celery workers |
| Phase 3 | 500-1000 | 1-3s | Single server + 4-8 Celery workers |
| Phase 4 | 1000+ | 0.5-2s | 4+ servers + Redis cluster |

---

## Quick Wins (Implement Today)

### 1. Add More Groq API Keys
```python
# settings.py
GROQ_API_KEYS = [
    'gsk_...',  # existing
    'gsk_...',  # new key 4
    'gsk_...',  # new key 5
    'gsk_...',  # new key 6
    'gsk_...',  # new key 7
    'gsk_...',  # new key 8
]
```

### 2. Enable Connection Pooling
Add `CONN_MAX_AGE: 600` to DATABASES setting.

### 3. Add Response Caching
Cache AI responses for repeated/similar questions.

### 4. Implement Health Checks
Add `/health/` endpoint for load balancer health checks.
