"""
Features 15 & 19: Violation Event Logging & Micro-Violation Scoring

Persists violation events to the database and computes a rolling
micro-violation score that accumulates minor infractions.
"""

import logging
import time
from collections import defaultdict
from typing import Dict, List, Optional

from app.config import (
    MICRO_VIOLATION_CRITICAL_THRESHOLD,
    MICRO_VIOLATION_DECAY_SECONDS,
    VIOLATION_WEIGHTS,
)
from app.models import database as db
from app.utils.constants import ViolationType, Severity, VIOLATION_SEVERITY_MAP, VIOLATION_DESCRIPTIONS
from app.utils.image_utils import create_thumbnail, encode_image_to_base64

import numpy as np

logger = logging.getLogger(__name__)


class ViolationLogger:
    """
    Manages violation event logging and micro-violation scoring for a session.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.violations: List[Dict] = []
        self.micro_violations: List[Dict] = []  # (timestamp, type, weight)
        self.violation_counts: Dict[str, int] = defaultdict(int)

    async def log(
        self,
        violation_type: str,
        severity: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Dict] = None,
        frame: Optional[np.ndarray] = None,
    ) -> int:
        """
        Log a violation event to the database.

        Args:
            violation_type: Type from ViolationType.
            severity: Override severity.
            message: Override message.
            details: Additional context data.
            frame: Optional frame snapshot for the report.

        Returns:
            Violation record ID.
        """
        sev = severity or VIOLATION_SEVERITY_MAP.get(violation_type, Severity.INFO)
        msg = message or VIOLATION_DESCRIPTIONS.get(violation_type, violation_type)

        # Create frame thumbnail if provided
        snapshot_b64 = None
        if frame is not None:
            try:
                thumb = create_thumbnail(frame, size=(160, 120))
                snapshot_b64 = encode_image_to_base64(thumb, quality=50)
            except Exception as e:
                logger.debug(f"Snapshot creation failed: {e}")

        # Persist to database
        violation_id = await db.log_violation(
            session_id=self.session_id,
            violation_type=violation_type,
            severity=sev,
            message=msg,
            details=details,
            frame_snapshot=snapshot_b64,
        )

        # Track locally
        self.violation_counts[violation_type] += 1
        self.violations.append({
            "id": violation_id,
            "type": violation_type,
            "severity": sev,
            "timestamp": time.time(),
        })

        # Add to micro-violation tracker
        weight = VIOLATION_WEIGHTS.get(violation_type, 1.0)
        self.micro_violations.append({
            "timestamp": time.time(),
            "type": violation_type,
            "weight": weight,
        })

        logger.debug(
            f"Violation logged: [{sev}] {violation_type} (ID: {violation_id})"
        )

        return violation_id

    def compute_micro_violation_score(self) -> float:
        """
        Compute the accumulated micro-violation score.

        Violations decay over time — older violations contribute less.
        Score = sum of (weight * decay_factor) for all violations.

        Returns:
            Current micro-violation score.
        """
        now = time.time()
        score = 0.0

        for v in self.micro_violations:
            age = now - v["timestamp"]
            # Exponential decay: violations older than DECAY_SECONDS lose impact
            decay = max(0.0, 1.0 - (age / MICRO_VIOLATION_DECAY_SECONDS))
            score += v["weight"] * decay

        return round(score, 2)

    def is_critical(self) -> bool:
        """Check if micro-violation score exceeds the critical threshold."""
        return self.compute_micro_violation_score() >= MICRO_VIOLATION_CRITICAL_THRESHOLD

    def get_breakdown(self) -> Dict[str, int]:
        """Get violation count breakdown by type."""
        return dict(self.violation_counts)

    def get_total(self) -> int:
        """Get total number of violations logged."""
        return len(self.violations)
