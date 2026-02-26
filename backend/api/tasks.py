from celery import shared_task
from .pipeline import process_resume_passed, process_assessment_passed
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_assessment_link_task(candidate_id):
    logger.info(f"Executing send_assessment_link_task for candidate {candidate_id}")
    process_resume_passed(candidate_id)

@shared_task
def send_interview_link_task(submission_id):
    logger.info(f"Executing send_interview_link_task for submission {submission_id}")
    process_assessment_passed(submission_id)
