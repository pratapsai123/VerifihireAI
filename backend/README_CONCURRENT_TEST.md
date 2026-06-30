# AI Interview Concurrent Test Documentation

## Overview
These test scripts verify that the AI interview system can handle 50+ concurrent interviews using the new async processing architecture.

## Test Scripts

### 1. `simple_concurrent_test.py` (Recommended)
- **Purpose**: Easy-to-run synchronous test using threading
- **Dependencies**: Only `requests` library
- **Usage**: `python simple_concurrent_test.py`

### 2. `test_concurrent_interviews.py` (Advanced)
- **Purpose**: Full async test with detailed metrics
- **Dependencies**: `aiohttp`, `asyncio`
- **Usage**: `python test_concurrent_interviews.py`

## Prerequisites

Before running tests, ensure:

1. **Django Server Running**
   ```bash
   cd backend
   python manage.py runserver 8001
   ```

2. **Redis Running**
   ```bash
   redis-server
   ```

3. **Celery Workers Running**
   ```bash
   cd backend
   celery -A VerifiHireAI_backend worker -l info --concurrency=10
   ```

## Test Scenarios

### What the Tests Do:
1. **Create 50 test candidates** with unique PAN numbers
2. **Submit interview answers** using the new async endpoint `/process-answer-async/`
3. **Monitor task completion** via `/task-status/{task_id}/`
4. **Measure performance** metrics (response times, success rates)
5. **Check queue status** to monitor system load

### Success Criteria:
- ✅ **90%+ success rate**: System handles 50+ concurrent interviews excellently
- ✅ **75%+ success rate**: System handles 50+ concurrent interviews well
- ⚠️ **50-75% success rate**: System needs improvement
- ❌ **<50% success rate**: System cannot handle the load

## Expected Results

With proper scaling implementation, you should see:
- **50 concurrent interviews** processed successfully
- **Response times** under 15 seconds per answer
- **Queue management** preventing system overload
- **No database timeouts** or connection errors

## Troubleshooting

### Common Issues:

1. **Connection Refused**
   - Ensure Django server is running on port 8001
   - Check firewall settings

2. **Task Timeout**
   - Increase Celery worker concurrency: `--concurrency=20`
   - Check Redis connection

3. **Rate Limit Errors**
   - Rate limiting is intentional - shows system is working
   - Adjust rate limits in `middleware.py` if needed

4. **Database Errors**
   - Check PostgreSQL connection pool settings
   - Verify database is running and accessible

## Performance Metrics

The tests measure:
- **Success Rate**: Percentage of interviews completed successfully
- **Response Time**: Time to process each answer
- **Throughput**: Answers processed per minute
- **Queue Load**: Number of tasks in queue

## Interpreting Results

### Excellent Performance (90%+ success):
```
✅ SUCCESSFUL: 45/50
❌ FAILED: 5/50
🎯 SUCCESS RATE: 90.0%
✅ EXCELLENT: System handles 50+ concurrent interviews very well!
```

### Needs Improvement (50-75% success):
```
✅ SUCCESSFUL: 30/50
❌ FAILED: 20/50
🎯 SUCCESS RATE: 60.0%
⚠️ NEEDS IMPROVEMENT: System struggles with 50+ concurrent interviews
```

## Running the Test

### Quick Start:
```bash
# Terminal 1: Start Django
cd backend
python manage.py runserver 8001

# Terminal 2: Start Celery
cd backend
celery -A VerifiHireAI_backend worker -l info --concurrency=10

# Terminal 3: Run test
python simple_concurrent_test.py
```

### Monitor During Test:
Watch the Celery worker logs to see tasks being processed:
```
[2026-05-07 10:30:00,000: INFO/MainProcess] Received task: ai_candidates.tasks.process_ai_interview_answer_task[abc123]
[2026-05-07 10:30:05,000: INFO/MainProcess] Task ai_candidates.tasks.process_ai_interview_answer_task[abc123] succeeded in 5.2s
```

## Customization

### Adjust Concurrent Count:
```python
# In test script
CONCURRENT_INTERVIEWS = 100  # Increase to 100 for stress testing
```

### Modify Test Duration:
```python
TIMEOUT = 120  # Increase timeout for slower systems
```

### Change Question Count:
```python
for question_num in range(1, 5):  # Test with 4 questions instead of 2
```

## Next Steps

After successful testing:
1. **Monitor production** with similar load tests
2. **Scale Celery workers** based on results
3. **Add more Groq API keys** if rate limited
4. **Implement frontend integration** with async endpoints
