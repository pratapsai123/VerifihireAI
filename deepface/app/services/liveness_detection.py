"""
Feature 3: Liveness Detection Service

Detects whether a face is live (real person) or a spoof (photo, video, deepfake).
Uses multiple signals:
  - Texture analysis (Laplacian variance / frequency domain)
  - Blink detection (Eye Aspect Ratio via FaceLandmarker)
  - Inter-frame motion analysis

Uses the new MediaPipe Tasks API (FaceLandmarker).
"""

import logging
import time
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

from app.config import (
    LIVENESS_BLINK_CONSEC_FRAMES,
    LIVENESS_EAR_THRESHOLD,
    LIVENESS_LAPLACIAN_THRESHOLD,
    LIVENESS_MOTION_THRESHOLD,
)

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent.parent / "models_data" / "face_landmarker.task"

# Eye landmark indices for EAR (Eye Aspect Ratio)
# Left eye vertical: (159,145) top, (153,154) bottom; horizontal: 33, 133
# Right eye vertical: (386,374) top, (380,381) bottom; horizontal: 362, 263
LEFT_EYE = [33, 159, 145, 133, 153, 154]  # corners + top + bottom
RIGHT_EYE = [362, 386, 374, 263, 380, 381]


class LivenessDetectionService:
    """Multi-signal liveness detection using texture, blink, and motion analysis."""

    def __init__(self):
        self._landmarker = None
        self._prev_frame_gray = None
        self._blink_counter = 0
        self._blink_total = 0
        self._ear_below_threshold_frames = 0
        self._init_landmarker()

    def _init_landmarker(self):
        """Initialize FaceLandmarker for EAR-based blink detection."""
        try:
            base_options = mp.tasks.BaseOptions(
                model_asset_path=str(MODEL_PATH)
            )
            options = mp.tasks.vision.FaceLandmarkerOptions(
                base_options=base_options,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_face_presence_confidence=0.5,
                min_tracking_confidence=0.5,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False,
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
            )
            self._landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)
            logger.info("FaceLandmarker (Tasks API) initialized for liveness detection.")
        except Exception as e:
            logger.error(f"Failed to initialize FaceLandmarker for liveness: {e}")
            self._landmarker = None

    def check(self, frame: np.ndarray) -> dict:
        """
        Perform liveness check on a frame.

        Returns:
            dict with is_live (bool), texture_score (float),
            blink_detected (bool), motion_detected (bool), violation (str or None).
        """
        try:
            # 1. Texture analysis (Laplacian variance)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            texture_score = cv2.Laplacian(gray, cv2.CV_64F).var()

            # 2. Blink detection via EAR
            blink_detected = False
            ear_value = 0.0

            if self._landmarker is not None:
                try:
                    rgb_frame = frame[:, :, ::-1].copy()
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                    result = self._landmarker.detect(mp_image)

                    if result.face_landmarks:
                        landmarks = result.face_landmarks[0]
                        left_ear = self._compute_ear(landmarks, LEFT_EYE, frame.shape)
                        right_ear = self._compute_ear(landmarks, RIGHT_EYE, frame.shape)
                        ear_value = (left_ear + right_ear) / 2

                        if ear_value < LIVENESS_EAR_THRESHOLD:
                            self._ear_below_threshold_frames += 1
                        else:
                            if self._ear_below_threshold_frames >= LIVENESS_BLINK_CONSEC_FRAMES:
                                self._blink_total += 1
                                blink_detected = True
                            self._ear_below_threshold_frames = 0
                except Exception as e:
                    logger.debug(f"Blink detection error: {e}")

            # 3. Inter-frame motion analysis
            motion_detected = False
            if self._prev_frame_gray is not None:
                diff = cv2.absdiff(gray, self._prev_frame_gray)
                motion_score = np.mean(diff)
                motion_detected = motion_score > LIVENESS_MOTION_THRESHOLD
            self._prev_frame_gray = gray.copy()

            # Determine liveness
            # A live face should have good texture (not flat) and some motion
            texture_ok = texture_score > LIVENESS_LAPLACIAN_THRESHOLD
            is_live = texture_ok  # Base on texture, motion and blinks are supplementary

            violation = None if is_live else "liveness_failed"

            return {
                "is_live": is_live,
                "texture_score": round(texture_score, 1),
                "ear_value": round(ear_value, 3),
                "blink_detected": blink_detected,
                "total_blinks": self._blink_total,
                "motion_detected": motion_detected,
                "violation": violation,
            }

        except Exception as e:
            logger.error(f"Liveness detection error: {e}")
            return {
                "is_live": False,
                "texture_score": 0.0,
                "ear_value": 0.0,
                "blink_detected": False,
                "total_blinks": self._blink_total,
                "motion_detected": False,
                "violation": "liveness_error",
            }

    def _compute_ear(self, landmarks, eye_indices, frame_shape) -> float:
        """
        Compute Eye Aspect Ratio (EAR) from face landmarks.

        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        where p1,p4 = horizontal corners, p2,p3 = top, p5,p6 = bottom
        """
        h, w = frame_shape[:2]
        pts = []
        for idx in eye_indices:
            lm = landmarks[idx]
            pts.append(np.array([lm.x * w, lm.y * h]))

        # p1=corner_left, p2=top1, p3=top2, p4=corner_right, p5=bottom1, p6=bottom2
        p1, p2, p3, p4, p5, p6 = pts

        # Vertical distances
        v1 = np.linalg.norm(p2 - p6)
        v2 = np.linalg.norm(p3 - p5)

        # Horizontal distance
        h_dist = np.linalg.norm(p1 - p4)

        if h_dist < 1e-6:
            return 0.0

        ear = (v1 + v2) / (2.0 * h_dist)
        return ear

    def close(self):
        """Release resources."""
        if self._landmarker:
            self._landmarker.close()
            self._landmarker = None
