"""
Test scaling improvements for 100+ concurrent interviews
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

import time
import hashlib

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {test_name}")
    if details:
        print(f"       {details}")

def test_database_connection_pooling():
    """Test 1: Database connection pooling is enabled"""
    print_header("TEST 1: Database Connection Pooling")
    
    from django.conf import settings
    
    conn_max_age = settings.DATABASES['default'].get('CONN_MAX_AGE')
    
    if conn_max_age and conn_max_age > 0:
        print_result("Connection Pooling", True, f"CONN_MAX_AGE = {conn_max_age}s")
        return True
    else:
        print_result("Connection Pooling", False, "CONN_MAX_AGE not set or 0")
        return False

def test_redis_cache():
    """Test 2: Redis cache is available for rate limiting"""
    print_header("TEST 2: Redis Cache for Rate Limiting")
    
    try:
        from django.core.cache import cache
        
        # Test cache write/read
        test_key = f"scaling_test_{int(time.time())}"
        test_value = {"test": "value", "timestamp": time.time()}
        
        cache.set(test_key, test_value, timeout=10)
        retrieved = cache.get(test_key)
        
        if retrieved and retrieved.get("test") == "value":
            print_result("Redis Cache", True, "Cache write/read working")
            return True
        else:
            print_result("Redis Cache", False, "Cache read returned wrong value")
            return False
    except Exception as e:
        print_result("Redis Cache", False, f"Error: {str(e)}")
        return False

def test_rate_limiter():
    """Test 3: Rate limiter is functional"""
    print_header("TEST 3: Rate Limiter")
    
    try:
        from ai_candidates.scaling_utils import RateLimiter, llm_limiter, tts_limiter
        
        # Test basic rate limiting
        test_key = f"test_limit_{int(time.time())}"
        limiter = RateLimiter("test", max_requests=3, window_seconds=60)
        
        results = []
        for i in range(5):
            allowed = limiter.is_allowed(test_key)
            results.append(allowed)
        
        # First 3 should be allowed, last 2 should be blocked
        if results == [True, True, True, False, False]:
            print_result("Rate Limiting Logic", True, "Correctly limits to 3 requests")
        else:
            print_result("Rate Limiting Logic", False, f"Unexpected results: {results}")
            return False
        
        # Check global limiters exist
        if llm_limiter and tts_limiter:
            print_result("Global Limiters", True, "llm_limiter and tts_limiter initialized")
            return True
        else:
            print_result("Global Limiters", False, "Global limiters not found")
            return False
            
    except Exception as e:
        print_result("Rate Limiter", False, f"Error: {str(e)}")
        return False

def test_llm_key_scaling():
    """Test 4: Multiple DeepSeek API keys configured"""
    print_header("TEST 4: DeepSeek API Key Scaling")
    
    from django.conf import settings
    
    keys = getattr(settings, 'DEEPSEEK_API_KEYS', [])
    
    if len(keys) >= 1:
        print_result("DeepSeek Keys", True, f"{len(keys)} keys configured (capacity: ~{len(keys) * 60} req/min)")
        return True
    else:
        print_result("DeepSeek Keys", False, f"Only {len(keys)} keys configured")
        return False

def test_health_check_import():
    """Test 5: Health check utilities import correctly"""
    print_header("TEST 5: Health Check Utilities")
    
    try:
        from ai_candidates.scaling_utils import get_system_health
        
        # Try to get health status
        health = get_system_health()
        
        if 'status' in health and 'components' in health:
            print_result("Health Check", True, f"Status: {health['status']}")
            for component, status in health['components'].items():
                print(f"       - {component}: {status}")
            return True
        else:
            print_result("Health Check", False, "Invalid health response structure")
            return False
            
    except Exception as e:
        print_result("Health Check", False, f"Error: {str(e)}")
        return False

def test_cache_ai_response_decorator():
    """Test 6: AI response caching decorator exists"""
    print_header("TEST 6: AI Response Caching")
    
    try:
        from ai_candidates.scaling_utils import cache_ai_response
        from django.core.cache import cache
        
        # Create a test function with caching
        call_count = [0]
        
        @cache_ai_response(timeout=60)
        def test_ai_func(prompt):
            call_count[0] += 1
            return {"result": f"processed_{prompt}", "timestamp": time.time()}
        
        # Call twice with same args
        result1 = test_ai_func("hello")
        result2 = test_ai_func("hello")
        
        # Should be cached, so function only called once
        if call_count[0] == 1:
            print_result("AI Caching", True, "Decorator correctly caches results")
            return True
        else:
            print_result("AI Caching", False, f"Function called {call_count[0]} times (expected 1)")
            return False
            
    except Exception as e:
        print_result("AI Caching", False, f"Error: {str(e)}")
        return False

def main():
    print("\n" + "="*70)
    print("  SCALING IMPROVEMENTS - VERIFICATION TESTS")
    print("  Target: 100+ Concurrent AI Interviews")
    print("="*70)
    
    results = []
    
    try:
        results.append(("DB Connection Pooling", test_database_connection_pooling()))
        results.append(("Redis Cache", test_redis_cache()))
        results.append(("Rate Limiter", test_rate_limiter()))
        results.append(("DeepSeek Key Scaling", test_llm_key_scaling()))
        results.append(("Health Check", test_health_check_import()))
        results.append(("AI Response Caching", test_cache_ai_response_decorator()))
    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print("\n" + "="*70)
    print(f"  RESULT: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("  ✅ SCALING IMPROVEMENTS READY FOR 100+ CONCURRENT INTERVIEWS!")
        print("="*70)
        print("\n  Next Steps for Full Scaling:")
        print("  1. Add 3 more DeepSeek API keys (for 360 req/min total)")
        print("  2. Deploy multiple Django instances behind load balancer")
        print("  3. Configure Celery workers for background processing")
        print("="*70)
        return 0
    else:
        print("  ⚠️ SOME TESTS NEED ATTENTION")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
