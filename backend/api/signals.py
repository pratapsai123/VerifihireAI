from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.db import transaction
from ai_candidates.models import Candidate
from ai_assessments.models import AIAssessmentSubmission
from .tasks import send_assessment_link_task, send_interview_link_task
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Candidate)
def handle_candidate_save(sender, instance, created, **kwargs):
    if instance.status == 'Resume Passed':
        logger.info(f"Signal: Candidate {instance.id} passed resume screening. Scheduling assessment task in 120 seconds.")
        # Use transaction.on_commit to avoid race condition where signal fires before DB commit
        def schedule_assessment():
            try:
                send_assessment_link_task.apply_async(args=[instance.id], countdown=120)
            except Exception as e:
                logger.error(f"Failed to schedule assessment task: {e}")
        transaction.on_commit(schedule_assessment)


@receiver(post_save, sender=AIAssessmentSubmission)
def handle_assessment_save(sender, instance, created, **kwargs):
    if instance.status == 'selected':
        logger.info(f"Signal: Assessment {instance.id} passed. Scheduling interview task in 120 seconds.")
        def schedule_interview():
            try:
                send_interview_link_task.apply_async(args=[instance.id], countdown=120)
            except Exception as e:
                logger.error(f"Failed to schedule interview task: {e}")
        transaction.on_commit(schedule_interview)
