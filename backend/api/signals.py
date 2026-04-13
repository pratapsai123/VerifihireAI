from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.db import transaction
from ai_candidates.models import Candidate
from ai_assessments.models import AIAssessmentSubmission
from .tasks import send_assessment_link_task, send_interview_link_task
import logging
from ai_candidates.utils import log_automation_event

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Candidate)
def handle_candidate_save(sender, instance, created, **kwargs):
    if instance.status == 'Resume Passed':
        # ONLY trigger auto-assessment if part of a fully automatic AI flow
        if not instance.automation_settings or not instance.automation_settings.get('is_fully_automatic'):
            logger.info(f"Signal: Candidate {instance.id} passed resume screening (Manual). Skipping auto-scheduling.")
            return

        # 1. Check if already scheduled or assessment exists
        from ai_assessments.models import Assessment
        if Assessment.objects.filter(user_profile=instance.user_profile, required_skills=instance.job_title, company=instance.company).exists():
            # If an assessment for this specific candidate name/job already exists, we might skip.
            # However, many candidates might share same job. Better to check if this candidate
            # has already had a task scheduled via cache.
            pass

        lock_key = f"assessment_scheduled_{instance.id}"
        if cache.get(lock_key):
            return # Already scheduled

        logger.info(f"Signal: Candidate {instance.id} passed resume screening. Scheduling assessment task in 120 seconds.")
        
        # Log the event
        log_automation_event(
            instance, 
            'TASK_SCHEDULED', 
            'INFO', 
            "Resume screening passed. AI assessment generation scheduled (2-minute delay)."
        )

        def schedule_assessment():
            try:
                send_assessment_link_task.apply_async(args=[instance.id], countdown=120)
                cache.set(lock_key, True, 3600) # Lock for 1 hour
            except Exception as e:
                logger.error(f"Failed to schedule assessment task: {e}")
                log_automation_event(instance, 'ERROR', 'FAILURE', f"Failed to schedule task: {str(e)}")
        
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
