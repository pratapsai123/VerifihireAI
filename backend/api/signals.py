from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from ai_candidates.models import Candidate
from ai_assessments.models import AIAssessmentSubmission
from .tasks import send_assessment_link_task, send_interview_link_task
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Candidate)
def handle_candidate_save(sender, instance, created, **kwargs):
    if instance.status == 'Resume Passed':
        cache_key = f"pipeline_candidate_{instance.id}"
        # Prevent duplicate tasks by caching the state for 24 hours
        if not cache.get(cache_key):
            cache.set(cache_key, True, timeout=86400) 
            logger.info(f"Signal: Candidate {instance.id} passed resume screening. Scheduling assessment task in 120 seconds.")
            # Delay execution by 120 seconds (2 minutes)
            try:
                send_assessment_link_task.apply_async(args=[instance.id], countdown=120)
            except Exception as e:
                logger.error(f"Failed to schedule assessment task: {e}")


@receiver(post_save, sender=AIAssessmentSubmission)
def handle_assessment_save(sender, instance, created, **kwargs):
    if instance.status == 'selected':
        cache_key = f"pipeline_assessment_{instance.id}"
        if not cache.get(cache_key):
            cache.set(cache_key, True, timeout=86400)
            logger.info(f"Signal: Assessment {instance.id} passed. Scheduling interview task in 120 seconds.")
            # Delay execution by 120 seconds (2 minutes)
            try:
                send_interview_link_task.apply_async(args=[instance.id], countdown=120)
            except Exception as e:
                logger.error(f"Failed to schedule interview task: {e}")
