from .models import PipelineLog
import logging

logger = logging.getLogger(__name__)

def log_automation_event(candidate, event_type, status, message, details=None, phase='GENERAL', batch_id=None):
    """
    Utility helper to create a PipelineLog entry for a candidate.
    """
    try:
        # Use provided batch_id or fallback to candidate's current batch_id
        effective_batch_id = batch_id or getattr(candidate, 'batch_id', None)
        
        PipelineLog.objects.create(
            candidate=candidate,
            event_type=event_type,
            status=status,
            phase=phase,
            batch_id=effective_batch_id,
            message=message,
            details=details or {}
        )
    except Exception as e:
        logger.error(f"Failed to create PipelineLog for candidate {candidate.id if candidate else 'unknown'}: {e}")
