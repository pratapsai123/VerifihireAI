"""
Features 2, 6, 18: Face Verification Service (Hybrid Model Architecture)

- ArcFace: Used at registration & initial session verification (high accuracy)
- SFace: Used for continuous real-time monitoring (high speed)
- Periodic re-verification with ArcFace at configurable intervals
- Low-confidence flagging for uncertain matches
"""

import logging
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.config import (
    LOW_CONFIDENCE_MARGIN,
    MONITORING_DETECTOR,
    MONITORING_DISTANCE_METRIC,
    MONITORING_MODEL,
    MONITORING_THRESHOLD,
    REGISTRATION_DETECTOR,
    REGISTRATION_DISTANCE_METRIC,
    REGISTRATION_MODEL,
    REGISTRATION_THRESHOLD,
    REVERIFY_INTERVAL_SECONDS,
    REVERIFY_SFACE_INTERVAL,
)
from app.services.face_registration import get_registered_embeddings
from app.utils.image_utils import decode_base64_image, enhance_for_recognition, resize_image

logger = logging.getLogger(__name__)

# Lazy-load deepface
_deepface = None


def _get_deepface():
    global _deepface
    if _deepface is None:
        from deepface import DeepFace
        _deepface = DeepFace
    return _deepface


def _resolve_model_profile(model_name: Optional[str]):
    """Return the DeepFace, threshold, detector, and metric settings for a model."""
    use_model = model_name or REGISTRATION_MODEL
    if use_model == "SFace":
        return use_model, MONITORING_THRESHOLD, MONITORING_DETECTOR, MONITORING_DISTANCE_METRIC
    return use_model, REGISTRATION_THRESHOLD, REGISTRATION_DETECTOR, REGISTRATION_DISTANCE_METRIC


def verify_face(
    person_id: str,
    image_base64: str,
    model: Optional[str] = None,
) -> Dict:
    """
    Verify a face against a registered person.

    Args:
        person_id: Registered person to verify against.
        image_base64: Base64-encoded face image.
        model: Override model ('ArcFace' or 'SFace'). Defaults to ArcFace.

    Returns:
        Verification result dict.
    """
    DeepFace = _get_deepface()

    # Select model and threshold
    use_model, threshold, detector, metric = _resolve_model_profile(model)

    try:
        img = decode_base64_image(image_base64)
        img = resize_image(img, max_width=640, max_height=480)

        # Get stored embeddings for the selected model.
        stored_embeddings = get_registered_embeddings(person_id, model=use_model)

        if not stored_embeddings and use_model != REGISTRATION_MODEL:
            stored_embeddings = get_registered_embeddings(person_id, model=REGISTRATION_MODEL)
            if stored_embeddings:
                use_model = REGISTRATION_MODEL
                threshold = REGISTRATION_THRESHOLD
                detector = REGISTRATION_DETECTOR
                metric = REGISTRATION_DISTANCE_METRIC

        if not stored_embeddings:
            return {
                "verified": False,
                "confidence": 0.0,
                "distance": 1.0,
                "threshold": threshold,
                "model_used": use_model,
                "low_confidence": False,
                "message": f"No registered face found for person: {person_id}",
            }

        # Enhance image for better recognition in varied lighting
        img_enhanced = enhance_for_recognition(img)

        # Extract embedding from current image
        current_embeddings = DeepFace.represent(
            img_path=img_enhanced,
            model_name=use_model,
            detector_backend=detector,
            enforce_detection=False,
        )

        if not current_embeddings:
            return {
                "verified": False,
                "confidence": 0.0,
                "distance": 1.0,
                "threshold": threshold,
                "model_used": use_model,
                "low_confidence": False,
                "message": "No face detected in the provided image.",
            }

        current_embedding = np.array(current_embeddings[0]["embedding"])

        # Compare against all stored embeddings, take minimum distance
        min_distance = float("inf")
        for stored_emb in stored_embeddings:
            distance = _compute_distance(current_embedding, stored_emb, metric)
            min_distance = min(min_distance, distance)

        # Determine verification result
        verified = min_distance <= threshold
        low_confidence = (
            not verified and min_distance <= threshold + LOW_CONFIDENCE_MARGIN
        )

        # Convert distance to confidence (0-1, higher = better)
        confidence = max(0.0, min(1.0, 1.0 - (min_distance / (threshold * 2))))

        if verified:
            message = "Face verified successfully."
        elif low_confidence:
            message = "Verification uncertain — low confidence match."
        else:
            message = "Face verification failed — identity mismatch."

        return {
            "verified": verified,
            "confidence": round(confidence, 4),
            "distance": round(min_distance, 4),
            "threshold": threshold,
            "model_used": use_model,
            "low_confidence": low_confidence,
            "message": message,
        }

    except Exception as e:
        logger.error(f"Face verification error for {person_id}: {e}", exc_info=True)
        return {
            "verified": False,
            "confidence": 0.0,
            "distance": 1.0,
            "threshold": threshold,
            "model_used": use_model,
            "low_confidence": False,
            "message": f"Verification error: {str(e)}",
        }


def verify_face_realtime(
    person_id: str,
    image: np.ndarray,
    model: Optional[str] = None,
) -> Dict:
    """
    Optimized real-time verification using SFace.
    Accepts a raw numpy image (no base64 decode needed).

    Args:
        person_id: Registered person to verify against.
        image: OpenCV BGR numpy array.

    Returns:
        Verification result dict.
    """
    DeepFace = _get_deepface()
    use_model, threshold, detector, metric = _resolve_model_profile(model or MONITORING_MODEL)

    try:
        stored_embeddings = get_registered_embeddings(person_id, model=use_model)

        if not stored_embeddings and use_model != REGISTRATION_MODEL:
            stored_embeddings = get_registered_embeddings(person_id, model=REGISTRATION_MODEL)
            if stored_embeddings:
                use_model = REGISTRATION_MODEL
                threshold = REGISTRATION_THRESHOLD
                detector = REGISTRATION_DETECTOR
                metric = REGISTRATION_DISTANCE_METRIC

        if not stored_embeddings:
            return {
                "verified": False,
                "confidence": 0.0,
                "distance": 1.0,
                "threshold": threshold,
                "model_used": use_model,
                "low_confidence": False,
                "message": "No registered embeddings.",
            }

        # Enhance image for better recognition in low-light / varied conditions
        image_enhanced = enhance_for_recognition(image)

        current_embeddings = DeepFace.represent(
            img_path=image_enhanced,
            model_name=use_model,
            detector_backend=detector,
            enforce_detection=False,
        )

        if not current_embeddings:
            # Fallback for dark/angled webcam frames where detector backend misses.
            # 'skip' uses the provided frame directly for embedding extraction.
            current_embeddings = DeepFace.represent(
                img_path=image_enhanced,
                model_name=use_model,
                detector_backend="skip",
                enforce_detection=False,
            )

        if not current_embeddings:
            return {
                "verified": False,
                "confidence": 0.0,
                "distance": 1.0,
                "threshold": threshold,
                "model_used": use_model,
                "low_confidence": False,
                "message": "No face detected.",
            }

        current_embedding = np.array(current_embeddings[0]["embedding"])

        min_distance = float("inf")
        for stored_emb in stored_embeddings:
            distance = _compute_distance(current_embedding, stored_emb, metric)
            min_distance = min(min_distance, distance)

        verified = min_distance <= threshold
        low_confidence = (
            not verified
            and min_distance <= threshold + LOW_CONFIDENCE_MARGIN
        )
        confidence = max(0.0, min(1.0, 1.0 - (min_distance / (threshold * 2))))

        return {
            "verified": verified,
            "confidence": round(confidence, 4),
            "distance": round(min_distance, 4),
            "threshold": threshold,
            "model_used": use_model,
            "low_confidence": low_confidence,
            "message": "",
        }

    except Exception as e:
        logger.error(f"Real-time verification error: {e}")
        return {
            "verified": False,
            "confidence": 0.0,
            "distance": 1.0,
            "threshold": threshold,
            "model_used": use_model,
            "low_confidence": False,
            "message": str(e),
        }


class PeriodicVerifier:
    """
    Manages periodic re-verification schedules.

    - Quick check (SFace) every REVERIFY_SFACE_INTERVAL seconds
    - Full check (ArcFace) every REVERIFY_INTERVAL_SECONDS seconds
    """

    def __init__(self, person_id: str):
        self.person_id = person_id
        self.last_sface_check = 0.0
        self.last_arcface_check = 0.0

    def should_run_sface(self) -> bool:
        """Check if a quick SFace verification is due."""
        return (time.time() - self.last_sface_check) >= REVERIFY_SFACE_INTERVAL

    def should_run_arcface(self) -> bool:
        """Check if a full ArcFace re-verification is due."""
        return (time.time() - self.last_arcface_check) >= REVERIFY_INTERVAL_SECONDS

    def mark_sface_done(self):
        self.last_sface_check = time.time()

    def mark_arcface_done(self):
        self.last_arcface_check = time.time()

    def get_model_for_check(self) -> Optional[str]:
        """Determine which model to use for the next verification check."""
        if self.should_run_arcface():
            return "ArcFace"
        elif self.should_run_sface():
            return "SFace"
        return None

    def mark_done(self, model: str):
        if model == "ArcFace":
            self.mark_arcface_done()
        else:
            self.mark_sface_done()


def _compute_distance(
    embedding1: np.ndarray,
    embedding2: np.ndarray,
    metric: str = "cosine",
) -> float:
    """
    Compute distance between two embeddings.

    Supports: cosine, euclidean, euclidean_l2
    """
    a = np.array(embedding1, dtype=np.float64)
    b = np.array(embedding2, dtype=np.float64)

    if metric == "cosine":
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 1.0
        return 1.0 - (dot / (norm_a * norm_b))

    elif metric == "euclidean":
        return float(np.linalg.norm(a - b))

    elif metric == "euclidean_l2":
        norm_a = a / (np.linalg.norm(a) + 1e-10)
        norm_b = b / (np.linalg.norm(b) + 1e-10)
        return float(np.linalg.norm(norm_a - norm_b))

    else:
        raise ValueError(f"Unsupported distance metric: {metric}")
