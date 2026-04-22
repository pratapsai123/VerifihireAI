"""
Feature 13: Engagement Scoring Engine

Computes a composite 0-100 engagement score from multiple signals:
  - Face presence
  - Head pose (attentive?)
  - Liveness
  - Verification status
"""

import logging
from typing import Dict, Optional

from app.config import ENGAGEMENT_WEIGHTS

logger = logging.getLogger(__name__)


def compute_engagement_score(
    face_present: bool = False,
    face_count: int = 0,
    head_pose_attentive: bool = True,
    liveness_passed: bool = True,
    verification_passed: bool = True,
) -> Dict:
    """
    Compute a weighted engagement score from multiple signals.

    Args:
        face_present: Is a face detected?
        face_count: Number of faces detected.
        head_pose_attentive: Is head pose within acceptable limits?
        liveness_passed: Did the frame pass liveness checks?
        verification_passed: Did the frame pass verification?

    Returns:
        Dict with overall score and component scores.
    """
    weights = ENGAGEMENT_WEIGHTS

    # Component scores (each 0.0 to 1.0)
    components = {}

    # Face presence: 1.0 if exactly 1 face, 0.5 if multiple, 0.0 if none
    if face_present and face_count == 1:
        components["face_presence"] = 1.0
    elif face_present and face_count > 1:
        components["face_presence"] = 0.5
    else:
        components["face_presence"] = 0.0


    components["head_pose_attentive"] = 1.0 if head_pose_attentive else 0.3
    components["liveness"] = 1.0 if liveness_passed else 0.0
    components["verification"] = 1.0 if verification_passed else 0.0

    # Compute weighted score
    score = 0.0
    for key, weight in weights.items():
        component_value = components.get(key, 0.0)
        score += component_value * weight

    # Convert to 0-100 scale
    final_score = round(score * 100, 1)

    return {
        "score": final_score,
        "components": components,
        "weights": weights,
    }
