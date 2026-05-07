#!/usr/bin/env python
"""
Test script to verify 50+ concurrent AI interview handling
Tests the new async processing system under load
"""
import asyncio
import aiohttp
import json
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import statistics

# Configuration
BASE_URL = "http://127.0.0.1:8001/api/ai-candidates"
CONCURRENT_INTERVIEWS = 50
TEST_DURATION = 300  # 5 minutes

class InterviewTester:
    def __init__(self):
        self.results = []
        self.errors = []
        self.start_time = None
        
    async def create_test_candidate(self, session, candidate_id):
        """Create a test candidate for interview"""
        try:
            candidate_data = {
                "full_name": f"Test Candidate {candidate_id}",
                "email": f"test{candidate_id}@example.com",
                "phone": f"123456789{candidate_id:02d}",
                "pan_number": f"ABCDE{candidate_id:05d}F",
                "job_title": "Software Engineer",
                "job_description": "Looking for experienced software engineer with Python, Django, and React skills.",
                "experience_level": random.choice(["fresher", "1-2", "3-5", "5+"])
            }
            
            async with session.post(f"{BASE_URL}/", json=candidate_data) as response:
                if response.status == 201:
                    candidate = await response.json()
                    return candidate["id"], candidate["public_token"]
                else:
                    error_text = await response.text()
                    self.errors.append(f"Create candidate {candidate_id}: {response.status} - {error_text}")
                    return None, None
                    
        except Exception as e:
            self.errors.append(f"Create candidate {candidate_id}: {str(e)}")
            return None, None
    
    async def submit_interview_answer(self, session, candidate_id, question_number=1):
        """Submit interview answer using async endpoint"""
        try:
            answer_data = {
                "candidate_id": candidate_id,
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
            
            # Use async endpoint
            async with session.post(f"{BASE_URL}/process-answer-async/", json=answer_data) as response:
                if response.status == 202:
                    result = await response.json()
                    task_id = result.get("task_id")
                    return task_id
                else:
                    error_text = await response.text()
                    self.errors.append(f"Submit answer {candidate_id}: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            self.errors.append(f"Submit answer {candidate_id}: {str(e)}")
            return None
    
    async def check_task_status(self, session, task_id, max_wait=30):
        """Check task completion status"""
        start_wait = time.time()
        
        while time.time() - start_wait < max_wait:
            try:
                async with session.get(f"{BASE_URL}/task-status/{task_id}/") as response:
                    if response.status == 200:
                        status_data = await response.json()
                        
                        if status_data.get("ready"):
                            return status_data.get("result"), status_data.get("status")
                        elif status_data.get("status") == "FAILURE":
                            return None, "FAILED"
                            
                    await asyncio.sleep(1)  # Poll every second
                    
            except Exception as e:
                self.errors.append(f"Check task status {task_id}: {str(e)}")
                return None, "ERROR"
        
        return None, "TIMEOUT"
    
    async def get_queue_status(self, session):
        """Get current queue status"""
        try:
            async with session.get(f"{BASE_URL}/queue-status/") as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            self.errors.append(f"Queue status: {str(e)}")
        return None
    
    async def run_single_interview_test(self, session, candidate_id):
        """Run complete interview test for one candidate"""
        start_time = time.time()
        
        # Create candidate
        candidate_db_id, public_token = await self.create_test_candidate(session, candidate_id)
        if not candidate_db_id:
            return {"candidate_id": candidate_id, "status": "FAILED", "error": "Candidate creation failed"}
        
        # Submit multiple answers (simulate interview)
        answer_times = []
        successful_answers = 0
        
        for question_num in range(1, 4):  # 3 questions per interview
            answer_start = time.time()
            
            # Submit answer
            task_id = await self.submit_interview_answer(session, candidate_db_id, question_num)
            if not task_id:
                continue
            
            # Wait for completion
            result, status = await self.check_task_status(session, task_id)
            
            answer_time = time.time() - answer_start
            answer_times.append(answer_time)
            
            if status == "SUCCESS" and result:
                successful_answers += 1
            else:
                self.errors.append(f"Candidate {candidate_id} Q{question_num}: {status}")
        
        total_time = time.time() - start_time
        
        return {
            "candidate_id": candidate_id,
            "status": "SUCCESS" if successful_answers > 0 else "FAILED",
            "total_time": total_time,
            "successful_answers": successful_answers,
            "answer_times": answer_times,
            "avg_answer_time": statistics.mean(answer_times) if answer_times else 0
        }
    
    async def run_concurrent_test(self):
        """Run concurrent interview test"""
        print(f"🚀 Starting {CONCURRENT_INTERVIEWS} concurrent AI interview test...")
        print(f"⏰ Test duration: {TEST_DURATION} seconds")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Create HTTP session
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=TEST_DURATION + 60)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Get initial queue status
            initial_queue = await self.get_queue_status(session)
            if initial_queue:
                print(f"📊 Initial queue status: {initial_queue['queue_status']['active_tasks']} active tasks")
            
            # Run concurrent interviews
            tasks = []
            for i in range(1, CONCURRENT_INTERVIEWS + 1):
                task = asyncio.create_task(self.run_single_interview_test(session, i))
                tasks.append(task)
            
            # Wait for all to complete
            print("⏳ Running concurrent interviews...")
            self.results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Get final queue status
            final_queue = await self.get_queue_status(session)
            if final_queue:
                print(f"📊 Final queue status: {final_queue['queue_status']['active_tasks']} active tasks")
        
        # Analyze results
        self.analyze_results()
    
    def analyze_results(self):
        """Analyze test results"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS ANALYSIS")
        print("=" * 60)
        
        successful_tests = [r for r in self.results if isinstance(r, dict) and r.get("status") == "SUCCESS"]
        failed_tests = [r for r in self.results if isinstance(r, dict) and r.get("status") == "FAILED"]
        exceptions = [r for r in self.results if isinstance(r, Exception)]
        
        print(f"✅ Successful interviews: {len(successful_tests)}/{CONCURRENT_INTERVIEWS}")
        print(f"❌ Failed interviews: {len(failed_tests)}/{CONCURRENT_INTERVIEWS}")
        print(f"⚠️ Exceptions: {len(exceptions)}")
        print(f"🚫 Errors: {len(self.errors)}")
        
        if successful_tests:
            total_times = [r["total_time"] for r in successful_tests]
            avg_times = [r["avg_answer_time"] for r in successful_tests if r["avg_answer_time"] > 0]
            total_answers = sum(r["successful_answers"] for r in successful_tests)
            
            print(f"\n⏱️  Performance Metrics:")
            print(f"   Average total time: {statistics.mean(total_times):.2f}s")
            print(f"   Median total time: {statistics.median(total_times):.2f}s")
            print(f"   Min total time: {min(total_times):.2f}s")
            print(f"   Max total time: {max(total_times):.2f}s")
            
            if avg_times:
                print(f"   Average answer time: {statistics.mean(avg_times):.2f}s")
                print(f"   Median answer time: {statistics.median(avg_times):.2f}s")
            
            print(f"   Total answers processed: {total_answers}")
            print(f"   Answers per minute: {total_answers / ((time.time() - self.start_time) / 60):.1f}")
        
        if self.errors:
            print(f"\n🚫 Sample Errors (first 10):")
            for error in self.errors[:10]:
                print(f"   - {error}")
        
        # Success criteria
        success_rate = len(successful_tests) / CONCURRENT_INTERVIEWS * 100
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("✅ EXCELLENT: System handles 50+ concurrent interviews very well!")
        elif success_rate >= 75:
            print("✅ GOOD: System handles 50+ concurrent interviews adequately!")
        elif success_rate >= 50:
            print("⚠️  NEEDS IMPROVEMENT: System struggles with 50+ concurrent interviews")
        else:
            print("❌ FAIL: System cannot handle 50+ concurrent interviews")
        
        print(f"\n⏰ Total test time: {time.time() - self.start_time:.2f}s")


async def main():
    """Main test runner"""
    print("🧪 AI Interview Concurrent Load Test")
    print(f"Testing {CONCURRENT_INTERVIEWS} concurrent interviews")
    print(f"Target: Verify 100+ concurrent interview capability")
    print()
    
    tester = InterviewTester()
    await tester.run_concurrent_test()


if __name__ == "__main__":
    print("⚠️  Make sure Django server is running on http://127.0.0.1:8001")
    print("⚠️  Make sure Celery workers are running")
    print("⚠️  Make sure Redis is running")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
