"""
Feature 1: Face Registration Service

Registers face embeddings for a person using ArcFace for maximum accuracy.
Supports multiple reference images per person for robust matching.
"""

import hashlib
import json
import logging
import os
import pickle
import cv2
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.config import (
    REGISTERED_FACES_DIR,
    REGISTRATION_DETECTOR,
    REGISTRATION_MODEL,
)
from app.utils.image_utils import (
    compute_laplacian_variance,
    decode_base64_image,
    resize_image,
)

logger = logging.getLogger(__name__)

# Lazy-load deepface to avoid import-time model downloads
_deepface = None


def _get_deepface():
    """Lazy import of deepface to defer model loading."""
    global _deepface
    if _deepface is None:
        from deepface import DeepFace
        _deepface = DeepFace
    return _deepface


def _get_person_dir(person_id: str) -> Path:
    """Get or create the directory for a person's face data."""
    person_dir = REGISTERED_FACES_DIR / person_id
    person_dir.mkdir(parents=True, exist_ok=True)
    return person_dir


def _save_embedding(person_dir: Path, model_name: str, label_str: str, embedding) -> None:
    """Persist a single embedding under the model-specific directory."""
    model_dir = person_dir / model_name.lower()
    model_dir.mkdir(exist_ok=True)

    with open(model_dir / f"{label_str}.pkl", "wb") as f:
        pickle.dump({
            "embedding": embedding,
            "model": model_name,
            "label": label_str,
        }, f)


def _extract_embedding(DeepFace, img: np.ndarray, model_name: str, detector_backend: str):
    """Extract the first embedding for a given model."""
    embedding_objs = DeepFace.represent(
        img_path=img,
        model_name=model_name,
        detector_backend=detector_backend,
        enforce_detection=False,
    )

    if not embedding_objs:
        return None

    return embedding_objs[0]["embedding"]


def register_face(
    person_id: str,
    image_base64: str,
    label: Optional[str] = None,
    overwrite: bool = False,
) -> Dict:
    """
    Register a face for a person.

    Extracts the face embedding using ArcFace and stores it.
    By default, it will NOT replace an existing registration unless overwrite=True.

    Args:
        person_id: Unique identifier for the person.
        image_base64: Base64-encoded face image.
        label: Optional label for this particular image.
        overwrite: If True, existing data for this person_id will be wiped.

    Returns:
        Dict with success status, quality score, and embedding count.
    """
    person_id = person_id.strip().lower()
    DeepFace = _get_deepface()

    try:
        # 1. SECURITY CHECK: Prevent accidental overwriting of an existing identity
        if is_registered(person_id) and not overwrite:
            logger.warning(f"Registration Blocked: Identity {person_id} already exists. Use overwrite=True to replace.")
            return {
                "success": False,
                "person_id": person_id,
                "message": "This candidate is already registered. Re-registration is not allowed for security reasons.",
                "embedding_count": _count_embeddings(person_id),
            }

        # Decode and preprocess image
        img = decode_base64_image(image_base64)
        img = resize_image(img, max_width=640, max_height=480)

        # Assess face quality
        quality_score = _assess_face_quality(img)

        if quality_score < 15.0:
            return {
                "success": False,
                "person_id": person_id,
                "message": "Image quality too low. Please provide a clearer face image.",
                "face_quality_score": quality_score,
                "embedding_count": _count_embeddings(person_id),
            }

        # Extract and store the registration embedding using ArcFace.
        embedding = _extract_embedding(
            DeepFace,
            img,
            REGISTRATION_MODEL,
            REGISTRATION_DETECTOR,
        )

        if embedding is None:
            return {
                "success": False,
                "person_id": person_id,
                "message": "No face detected in the image.",
                "face_quality_score": quality_score,
                "embedding_count": _count_embeddings(person_id),
            }

        # Wipe existing face embeddings ONLY if overwrite is explicitly requested.
        person_dir = _get_person_dir(person_id)
        if overwrite and person_dir.exists():
            for item in person_dir.glob("**/*"):
                if item.is_file():
                    try:
                        item.unlink()
                    except Exception as clean_err:
                        logger.warning(f"Could not unlink {item}: {clean_err}")

        # Re-create directory and start fresh
        person_dir = _get_person_dir(person_id)
        label_str = label or "face_0"
        embedding_path = person_dir / f"{label_str}.pkl"

        with open(embedding_path, "wb") as f:
            pickle.dump({
                "embedding": embedding,
                "model": REGISTRATION_MODEL,
                "label": label_str,
            }, f)

        # Save the actual image for report generation
        image_path = person_dir / f"{label_str}.jpg"
        cv2.imwrite(str(image_path), img)

        # Also store model-specific copies for later verification.
        _save_embedding(person_dir, REGISTRATION_MODEL, label_str, embedding)

        try:
            sface_embedding = _extract_embedding(
                DeepFace,
                img,
                "SFace",
                REGISTRATION_DETECTOR,
            )
            if sface_embedding is not None:
                _save_embedding(person_dir, "SFace", label_str, sface_embedding)
        except Exception as e:
            logger.warning(f"SFace embedding extraction failed for {person_id}: {e}")

        new_count = _count_embeddings(person_id)

        # Compute SHA-256 hash of the embedding for duplicate detection
        embedding_hash = hashlib.sha256(np.array(embedding).tobytes()).hexdigest()
        logger.info(f"Registered face for {person_id} ({label_str}). Total embeddings: {new_count}. Hash: {embedding_hash[:16]}...")

        return {
            "success": True,
            "person_id": person_id,
            "message": f"Face registered successfully. Total reference images: {new_count}",
            "face_quality_score": quality_score,
            "embedding_count": new_count,
            "embedding_hash": embedding_hash,
        }

    except Exception as e:
        logger.error(f"Face registration error for {person_id}: {e}", exc_info=True)
        return {
            "success": False,
            "person_id": person_id,
            "message": f"Registration failed: {str(e)}",
            "face_quality_score": 0.0,
            "embedding_count": _count_embeddings(person_id),
        }


def get_registered_embeddings(person_id: str, model: Optional[str] = None) -> List[np.ndarray]:
    """
    Load all stored embeddings for a person.

    Args:
        person_id: Person identifier.
        model: If specified, load from model-specific subdirectory.

    Returns:
        List of embedding vectors.
    """
    person_dir = _get_person_dir(person_id)

    if model:
        search_dir = person_dir / model.lower()
        if not search_dir.exists():
            search_dir = person_dir
    else:
        search_dir = person_dir

    embeddings = []
    for pkl_file in search_dir.glob("*.pkl"):
        try:
            with open(pkl_file, "rb") as f:
                data = pickle.load(f)

            if isinstance(data, dict):
                embeddings.append(np.array(data["embedding"]))
            elif isinstance(data, (list, np.ndarray)):
                embeddings.append(np.array(data))
        except Exception as e:
            logger.warning(f"Failed to load embedding {pkl_file}: {e}")

    return embeddings


def is_registered(person_id: str) -> bool:
    """Check if a person has any registered face embeddings."""
    person_id = person_id.strip().lower()
    return _count_embeddings(person_id) > 0


def delete_registration(person_id: str) -> bool:
    """Delete all registered face data for a person."""
    import shutil
    person_id = person_id.strip().lower()
    person_dir = REGISTERED_FACES_DIR / person_id
    if person_dir.exists():
        shutil.rmtree(person_dir)
        logger.info(f"Deleted all face data for {person_id}")
        return True
    return False


def _count_embeddings(person_id: str) -> int:
    """Count stored embeddings for a person."""
    person_dir = REGISTERED_FACES_DIR / person_id
    if not person_dir.exists():
        return 0
    return len(list(person_dir.glob("*.pkl")))


def _assess_face_quality(img: np.ndarray) -> float:
    """
    Assess the quality of a face image.
    Returns a score from 0-100 based on sharpness.
    """
    laplacian_var = compute_laplacian_variance(img)
    # Normalize: typical values range from 0 to ~500+
    # Score: 0-100 where 100 is very sharp
    score = min(100.0, (laplacian_var / 5.0))
    return round(score, 1)
