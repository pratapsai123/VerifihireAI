"""
Feature 14: Real-time Alert System

Broadcasts alerts via WebSocket with throttling per alert type.
Supports severity levels: INFO, WARNING, CRITICAL.
"""

import logging
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.config import ALERT_COOLDOWN_SECONDS
from app.models.schemas import AlertMessage
from app.utils.constants import VIOLATION_DESCRIPTIONS, VIOLATION_SEVERITY_MAP, Severity

logger = logging.getLogger(__name__)


class AlertSystem:
    """
    Manages alert generation with per-type cooldown throttling.
    Alerts are collected per analysis cycle and can be pushed via WebSocket.
    """

    def __init__(self, cooldown_seconds: float = ALERT_COOLDOWN_SECONDS):
        self.cooldown = cooldown_seconds
        self.last_alert_time: Dict[str, float] = defaultdict(float)
        self.pending_alerts: List[AlertMessage] = []
        self.total_alerts_generated: int = 0

    def trigger(
        self,
        violation_type: str,
        severity: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Optional[AlertMessage]:
        """
        Trigger an alert if the cooldown for this type has elapsed.

        Args:
            violation_type: Type constant from ViolationType.
            severity: Override severity. Defaults to mapped severity.
            message: Override message. Defaults to mapped description.
            details: Additional alert metadata.

        Returns:
            AlertMessage if the alert was generated, None if throttled.
        """
        now = time.time()
        last = self.last_alert_time[violation_type]

        # Throttle: skip if within cooldown window
        if (now - last) < self.cooldown:
            return None

        # Generate alert
        sev = severity or VIOLATION_SEVERITY_MAP.get(violation_type, Severity.INFO)
        msg = message or VIOLATION_DESCRIPTIONS.get(violation_type, violation_type)

        alert = AlertMessage(
            type=violation_type,
            severity=sev,
            message=msg,
            timestamp=datetime.utcnow(),
            details=details,
        )

        self.last_alert_time[violation_type] = now
        self.pending_alerts.append(alert)
        self.total_alerts_generated += 1

        logger.info(f"Alert [{sev}]: {msg}")

        return alert

    def flush(self) -> List[AlertMessage]:
        """
        Retrieve and clear all pending alerts.

        Returns:
            List of pending AlertMessage objects.
        """
        alerts = self.pending_alerts.copy()
        self.pending_alerts.clear()
        return alerts

    def reset_cooldown(self, violation_type: str):
        """Reset the cooldown timer for a specific violation type."""
        self.last_alert_time[violation_type] = 0.0

    def reset_all(self):
        """Reset all cooldown timers."""
        self.last_alert_time.clear()
        self.pending_alerts.clear()
