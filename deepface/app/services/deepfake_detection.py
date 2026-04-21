"""
Feature 17: Deepfake / Virtual Camera Detection

Detects:
1. Virtual camera software (OBS, ManyCam, etc.) via device name matching
2. Deepfake artifacts via frequency domain analysis (DCT)
3. Unnatural temporal smoothness between consecutive frames
"""

import logging
from collections import deque
from typing import Dict, Optional

import cv2
import numpy as np

from app.config import (
    DEEPFAKE_FREQUENCY_THRESHOLD,
    DEEPFAKE_TEMPORAL_SMOOTHNESS_THRESHOLD,
    VIRTUAL_CAMERA_SIGNATURES,
)

logger = logging.getLogger(__name__)


def check_virtual_camera(device_name: Optional[str] = None) -> Dict:
    """
    Check if the camera device name matches known virtual camera software.

    Args:
        device_name: Camera device name from the client.

    Returns:
        Dict with detection result.
    """
    if not device_name:
        return {
            "virtual_camera_detected": False,
            "device_name": None,
            "message": "No device name provided for check.",
        }

    device_lower = device_name.lower().strip()

    for signature in VIRTUAL_CAMERA_SIGNATURES:
        if signature in device_lower:
            return {
                "virtual_camera_detected": True,
                "device_name": device_name,
                "matched_signature": signature,
                "message": f"Virtual camera detected: {device_name}",
            }

    return {
        "virtual_camera_detected": False,
        "device_name": device_name,
        "message": "Camera appears genuine.",
    }


class DeepfakeDetector:
    """
    Stateful deepfake detector analyzing frame sequences.
    """

    def __init__(self, history_size: int = 30):
        self.frame_history: deque = deque(maxlen=history_size)
        self.frequency_scores: deque = deque(maxlen=history_size)
        self.diff_scores: deque = deque(maxlen=history_size)

    def analyze(self, frame: np.ndarray) -> Dict:
        """
        Analyze a frame for deepfake indicators.

        Args:
            frame: OpenCV BGR image.

        Returns:
            Dict with deepfake detection results.
        """
        results = {
            "deepfake_suspected": False,
            "frequency_score": 0.0,
            "temporal_smoothness": 0.0,
            "reasons": [],
        }

        # 1. Frequency domain analysis (DCT)
        freq_score = self._analyze_frequency(frame)
        results["frequency_score"] = round(freq_score, 4)

        if freq_score > DEEPFAKE_FREQUENCY_THRESHOLD:
            results["reasons"].append(
                f"Abnormal frequency pattern (score: {freq_score:.4f})"
            )

        # 2. Temporal smoothness (needs frame history)
        if len(self.frame_history) >= 2:
            smoothness = self._analyze_temporal_smoothness(frame)
            results["temporal_smoothness"] = round(smoothness, 4)

            if smoothness < DEEPFAKE_TEMPORAL_SMOOTHNESS_THRESHOLD:
                results["reasons"].append(
                    f"Unnaturally smooth transitions (score: {smoothness:.4f})"
                )

        # Store frame for history
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (160, 120))
        self.frame_history.append(small)

        # Final decision
        results["deepfake_suspected"] = len(results["reasons"]) > 0

        return results

    def _analyze_frequency(self, frame: np.ndarray) -> float:
        """
        Analyze frequency domain characteristics using DCT.

        GAN-generated faces often have unusual high-frequency patterns.
        Returns a score where higher values indicate more suspicious patterns.
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (256, 256))
            gray_float = np.float32(gray)

            # Apply DCT
            dct = cv2.dct(gray_float)

            # Analyze high-frequency energy ratio
            h, w = dct.shape
            # High-frequency region (bottom-right quadrant)
            high_freq = dct[h // 2:, w // 2:]
            # Low-frequency region (top-left quadrant)
            low_freq = dct[:h // 4, :w // 4]

            high_energy = np.sum(np.abs(high_freq))
            low_energy = np.sum(np.abs(low_freq)) + 1e-10

            ratio = high_energy / low_energy
            self.frequency_scores.append(ratio)

            return ratio

        except Exception as e:
            logger.debug(f"Frequency analysis error: {e}")
            return 0.0

    def _analyze_temporal_smoothness(self, frame: np.ndarray) -> float:
        """
        Analyze temporal smoothness between consecutive frames.

        Real faces have natural micro-movements. Deepfakes may be unnaturally
        smooth or have inconsistent motion patterns.

        Returns the mean absolute difference (lower = smoother/more suspicious).
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            small = cv2.resize(gray, (160, 120))

            prev = self.frame_history[-1]
            diff = cv2.absdiff(small, prev).astype(np.float32)
            mean_diff = float(np.mean(diff))

            self.diff_scores.append(mean_diff)

            return mean_diff

        except Exception as e:
            logger.debug(f"Temporal analysis error: {e}")
            return 10.0  # Default to "normal" level

    def get_summary(self) -> Dict:
        """Get summary of deepfake analysis for the session."""
        return {
            "avg_frequency_score": round(
                np.mean(self.frequency_scores), 4
            ) if self.frequency_scores else 0.0,
            "avg_temporal_smoothness": round(
                np.mean(self.diff_scores), 4
            ) if self.diff_scores else 0.0,
            "frames_analyzed": len(self.frame_history),
        }
