"""
Async views for AI interview processing to handle 100+ concurrent sessions
"""
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
import json
import logging
from .tasks import process_ai_interview_answer_task
from .models import Candidate

logger = logging.getLogger(__name__)


class AsyncProcessAnswerView(APIView):
    """
    Async version of ProcessAnswerView that queues AI processing
    Enables 100+ concurrent interviews by offloading AI calls to Celery
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        try:
            candidate_id = request.data.get('candidate_id')
            answer_text = request.data.get('answer_text', '')
            current_question = request.data.get('current_question', '')
            remaining_questions = request.data.get('remaining_questions', [])
            conversation_memory = request.data.get('conversation_memory', {})
            current_turn_number = request.data.get('current_turn_number', 1)
            
            if not candidate_id:
                return Response({'error': 'Missing candidate_id'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate candidate exists
            try:
                candidate = Candidate.objects.get(pk=candidate_id)
            except Candidate.DoesNotExist:
                return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if there's already a task in progress for this candidate
            task_key = f"interview_task_{candidate_id}"
            existing_task_id = cache.get(task_key)
            
            if existing_task_id:
                # Check if the existing task is still running
                from celery.result import AsyncResult
                task_result = AsyncResult(existing_task_id)
                
                if task_result.state in ['PENDING', 'PROGRESS', 'RETRY']:
                    return Response({
                        'status': 'processing',
                        'message': 'Previous answer still being processed',
                        'task_id': existing_task_id
                    }, status=status.HTTP_202_ACCEPTED)
                else:
                    # Clear the old task
                    cache.delete(task_key)
            
            # Queue the AI processing task
            task = process_ai_interview_answer_task.delay(
                candidate_id=candidate_id,
                answer_text=answer_text,
                current_question=current_question,
                remaining_questions=remaining_questions,
                conversation_memory=conversation_memory,
                current_turn_number=current_turn_number
            )
            
            # Store task ID for deduplication
            cache.set(task_key, task.id, timeout=300)  # 5 minute timeout
            
            logger.info(f"Queued AI processing for candidate {candidate_id}, task {task.id}")
            
            return Response({
                'status': 'queued',
                'message': 'Answer queued for AI processing',
                'task_id': task.id,
                'estimated_wait': '5-15 seconds'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error in AsyncProcessAnswerView: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskStatusView(APIView):
    """
    Check the status of async AI processing tasks
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request, task_id):
        try:
            from celery.result import AsyncResult
            
            task_result = AsyncResult(task_id)
            
            response_data = {
                'task_id': task_id,
                'status': task_result.state,
                'ready': task_result.ready()
            }
            
            if task_result.ready():
                if task_result.successful():
                    response_data.update({
                        'result': task_result.result,
                        'completed_at': task_result.date_done
                    })
                else:
                    response_data.update({
                        'error': str(task_result.result),
                        'failed_at': task_result.date_done
                    })
            elif task_result.state == 'PROGRESS':
                # Add progress info if available
                response_data.update({
                    'progress': task_result.info or {}
                })
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error checking task status: {e}")
            return Response({'error': 'Failed to check task status'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InterviewQueueStatusView(APIView):
    """
    Monitor the interview processing queue for load balancing
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        try:
            from celery import current_app
            
            # Get queue statistics
            inspect = current_app.control.inspect()
            
            # Active tasks
            active_tasks = inspect.active()
            active_count = sum(len(tasks) for tasks in (active_tasks or {}).values())
            
            # Scheduled tasks
            scheduled_tasks = inspect.scheduled()
            scheduled_count = sum(len(tasks) for tasks in (scheduled_tasks or {}).values())
            
            # Reserved tasks
            reserved_tasks = inspect.reserved()
            reserved_count = sum(len(tasks) for tasks in (reserved_tasks or {}).values())
            
            # Get Groq key usage stats
            from ai_assessments.ai_logic import GroqKeyManager
            key_stats = GroqKeyManager.get_usage_stats()
            
            # Calculate capacity
            total_capacity = len(key_stats.get('usage_per_key', {})) * 30  # 30 req/min per key
            current_load = active_count + scheduled_count + reserved_count
            capacity_utilization = (current_load / total_capacity * 100) if total_capacity > 0 else 0
            
            response_data = {
                'queue_status': {
                    'active_tasks': active_count,
                    'scheduled_tasks': scheduled_count,
                    'reserved_tasks': reserved_count,
                    'total_pending': current_load
                },
                'capacity': {
                    'total_capacity': total_capacity,
                    'current_load': current_load,
                    'utilization_percent': round(capacity_utilization, 2),
                    'can_handle_more': capacity_utilization < 80
                },
                'groq_keys': key_stats,
                'system_health': 'healthy' if capacity_utilization < 80 else 'overloaded'
            }
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return Response({'error': 'Failed to get queue status'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
