#!/usr/bin/env python
"""
Simple concurrent interview test - synchronous version
Easier to run without complex dependencies
"""
import requests
import threading
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://127.0.0.1:8001/api/ai-candidates"
CONCURRENT_INTERVIEWS = 50
TIMEOUT = 60  # seconds per request

class SimpleInterviewTester:
    def __init__(self):
        self.results = []
        self.errors = []
        self.lock = threading.Lock()
    
    def create_test_candidate(self, candidate_id):
        """Create a test candidate using direct model creation"""
        try:
            # Import Django models and create candidate directly
            import os
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
            import django
            django.setup()
            
            from ai_candidates.models import Candidate
            
            # Create candidate directly in database
            candidate = Candidate.objects.create(
                full_name=f"Test Candidate {candidate_id}",
                email=f"test{candidate_id}@example.com",
                phone=f"123456789{candidate_id % 10}",
                pan_number=f"ABCDE{candidate_id % 10000:04d}F",  # 10 characters total
                job_title="Software Engineer",
                job_description="Looking for experienced software engineer with Python, Django, and React skills.",
                experience_level=random.choice(["fresher", "1-2", "3-5", "5+"]),
                status='Interview',
                interview_questions=[
                    "Tell me about your experience with Python and Django.",
                    "What is your experience with React?",
                    "Describe a challenging project you worked on."
                ]
            )
            
            return candidate.id, str(candidate.public_token)
                
        except Exception as e:
            with self.lock:
                self.errors.append(f"Create candidate {candidate_id}: {str(e)}")
            return None, None
    
    def submit_interview_answer(self, candidate_db_id, question_number=1):
        """Submit interview answer using async endpoint"""
        try:
            answer_data = {
                "candidate_id": candidate_db_id,
                "answer_text": f"This is my answer to question {question_number}. I have experience with Python and Django frameworks.",
                "current_question": f"Tell me about your experience with Python and Django.",
                "remaining_questions": [
                    "What is your experience with React?",
                    "Describe a challenging project you worked on.",
                    "How do you handle tight deadlines?"
                ],
                "conversation_memory": {
                    "skills_mentioned": ["Python", "Django"],
                    "experience_level": "mid"
                },
                "current_turn_number": question_number
            }
            
            # Test async endpoint
            response = requests.post(f"{BASE_URL}/process-answer-async/", json=answer_data, timeout=TIMEOUT)
            if response.status_code == 202:
                result = response.json()
                return result.get("task_id")
            else:
                with self.lock:
                    self.errors.append(f"Submit answer {candidate_db_id}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            with self.lock:
                self.errors.append(f"Submit answer {candidate_db_id}: {str(e)}")
            return None
    
    def check_task_status(self, task_id, max_wait=30):
        """Check task completion status"""
        start_wait = time.time()
        
        while time.time() - start_wait < max_wait:
            try:
                response = requests.get(f"{BASE_URL}/task-status/{task_id}/", timeout=TIMEOUT)
                if response.status_code == 200:
                    status_data = response.json()
                    
                    if status_data.get("ready"):
                        return status_data.get("result"), status_data.get("status")
                    elif status_data.get("status") == "FAILURE":
                        return None, "FAILED"
                        
                time.sleep(1)  # Poll every second
                
            except Exception as e:
                with self.lock:
                    self.errors.append(f"Check task status {task_id}: {str(e)}")
                return None, "ERROR"
        
        return None, "TIMEOUT"
    
    def test_single_candidate(self, candidate_id):
        """Test interview flow for one candidate"""
        start_time = time.time()
        
        # Create candidate
        candidate_db_id, public_token = self.create_test_candidate(candidate_id)
        if not candidate_db_id:
            return {"candidate_id": candidate_id, "status": "FAILED", "error": "Candidate creation failed"}
        
        # Submit and check answers
        successful_answers = 0
        answer_times = []
        
        for question_num in range(1, 3):  # 2 questions per test
            answer_start = time.time()
            
            # Submit answer
            task_id = self.submit_interview_answer(candidate_db_id, question_num)
            if not task_id:
                continue
            
            # Wait for completion
            result, status = self.check_task_status(task_id)
            
            answer_time = time.time() - answer_start
            answer_times.append(answer_time)
            
            if status == "SUCCESS" and result:
                successful_answers += 1
            else:
                with self.lock:
                    self.errors.append(f"Candidate {candidate_id} Q{question_num}: {status}")
        
        total_time = time.time() - start_time
        
        return {
            "candidate_id": candidate_id,
            "status": "SUCCESS" if successful_answers > 0 else "FAILED",
            "total_time": total_time,
            "successful_answers": successful_answers,
            "answer_times": answer_times,
            "avg_answer_time": sum(answer_times) / len(answer_times) if answer_times else 0
        }
    
    def get_queue_status(self):
        """Get current queue status"""
        try:
            response = requests.get(f"{BASE_URL}/queue-status/", timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            with self.lock:
                self.errors.append(f"Queue status: {str(e)}")
        return None
    
    def run_concurrent_test(self):
        """Run concurrent test with threading"""
        print(f"🚀 Starting {CONCURRENT_INTERVIEWS} concurrent AI interview test...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Get initial queue status
        initial_queue = self.get_queue_status()
        if initial_queue:
            print(f"📊 Initial queue: {initial_queue['queue_status']['active_tasks']} active tasks")
        
        # Run concurrent tests
        with ThreadPoolExecutor(max_workers=CONCURRENT_INTERVIEWS) as executor:
            # Submit all tasks
            futures = [executor.submit(self.test_single_candidate, i) for i in range(1, CONCURRENT_INTERVIEWS + 1)]
            
            # Collect results
            print("⏳ Running concurrent interviews...")
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    self.errors.append(f"Future error: {str(e)}")
        
        # Get final queue status
        final_queue = self.get_queue_status()
        if final_queue:
            print(f"📊 Final queue: {final_queue['queue_status']['active_tasks']} active tasks")
        
        total_time = time.time() - start_time
        
        # Analyze results
        self.analyze_results(total_time)
    
    def analyze_results(self, total_time):
        """Analyze test results"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)
        
        successful_tests = [r for r in self.results if r.get("status") == "SUCCESS"]
        failed_tests = [r for r in self.results if r.get("status") == "FAILED"]
        
        print(f"✅ Successful: {len(successful_tests)}/{CONCURRENT_INTERVIEWS}")
        print(f"❌ Failed: {len(failed_tests)}/{CONCURRENT_INTERVIEWS}")
        print(f"🚫 Errors: {len(self.errors)}")
        print(f"⏱️  Total time: {total_time:.2f}s")
        
        if successful_tests:
            total_times = [r["total_time"] for r in successful_tests]
            avg_times = [r["avg_answer_time"] for r in successful_tests if r["avg_answer_time"] > 0]
            total_answers = sum(r["successful_answers"] for r in successful_tests)
            
            print(f"\n⏱️  Performance:")
            print(f"   Avg total time: {sum(total_times) / len(total_times):.2f}s")
            print(f"   Min total time: {min(total_times):.2f}s")
            print(f"   Max total time: {max(total_times):.2f}s")
            
            if avg_times:
                print(f"   Avg answer time: {sum(avg_times) / len(avg_times):.2f}s")
            
            print(f"   Total answers: {total_answers}")
            print(f"   Answers/min: {total_answers / (total_time / 60):.1f}")
        
        if self.errors:
            print(f"\n🚫 Sample errors (first 5):")
            for error in self.errors[:5]:
                print(f"   - {error}")
        
        # Success rate
        success_rate = len(successful_tests) / CONCURRENT_INTERVIEWS * 100
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("✅ EXCELLENT: System handles 50+ concurrent interviews!")
        elif success_rate >= 75:
            print("✅ GOOD: System handles 50+ concurrent interviews well!")
        elif success_rate >= 50:
            print("⚠️  NEEDS IMPROVEMENT: System struggles with 50+ concurrent")
        else:
            print("❌ FAIL: System cannot handle 50+ concurrent interviews")


def check_system_health():
    """Check if system components are ready"""
    print("🔍 Checking system health...")
    
    # Check Django server
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=10)
        if response.status_code == 200:
            print("✅ Django server: OK")
        else:
            print(f"❌ Django server: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Django server: {e}")
        return False
    
    # Check queue status endpoint
    try:
        response = requests.get(f"{BASE_URL}/queue-status/", timeout=10)
        if response.status_code == 200:
            print("✅ Queue status endpoint: OK")
        else:
            print(f"❌ Queue status endpoint: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Queue status endpoint: {e}")
        return False
    
    return True


def main():
    """Main test runner"""
    print("🧪 Simple AI Interview Concurrent Test")
    print(f"Testing {CONCURRENT_INTERVIEWS} concurrent interviews")
    print()
    
    # Check system health first
    if not check_system_health():
        print("\n❌ System health check failed. Please ensure:")
        print("   1. Django server is running on http://127.0.0.1:8001")
        print("   2. Redis is running")
        print("   3. Celery workers are running")
        return
    
    tester = SimpleInterviewTester()
    tester.run_concurrent_test()


if __name__ == "__main__":
    print("⚠️  Prerequisites:")
    print("   1. Django server running on http://127.0.0.1:8001")
    print("   2. Redis running")
    print("   3. Celery workers running")
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
