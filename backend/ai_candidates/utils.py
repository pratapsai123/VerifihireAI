from .models import PipelineLog
import logging

logger = logging.getLogger(__name__)

def log_automation_event(candidate, event_type, status, message, details=None):
    """
    Utility helper to create a PipelineLog entry for a candidate.
    """
    try:
        PipelineLog.objects.create(
            candidate=candidate,
            event_type=event_type,
            status=status,
            message=message,
            details=details or {}
        )
    except Exception as e:
        logger.error(f"Failed to create PipelineLog for candidate {candidate.id if candidate else 'unknown'}: {e}")
