"""
Features 7 & 8: Head Pose Estimation (Yaw & Pitch)

Estimates head rotation from MediaPipe FaceLandmarker (478 landmarks).
- Yaw: Left/right head turn — from nose horizontal offset (ratio-based)
- Pitch: Up/down head tilt — from vertical landmark ratio (nose vs forehead/chin)
Flags if angles exceed configurable thresholds.
"""

import logging
from pathlib import Path
import mediapipe as mp
import numpy as np

from app.config import HEAD_PITCH_LIMIT, HEAD_YAW_LIMIT

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent.parent / "models_data" / "face_landmarker.task"

# Key landmark indices
NOSE_TIP = 1
FOREHEAD = 10
CHIN = 152
LEFT_CHEEK = 234
RIGHT_CHEEK = 454
LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263
LEFT_MOUTH = 61
RIGHT_MOUTH = 291



class HeadPoseService:
    """Estimates head yaw and pitch using hybrid approach."""

    def __init__(self):
        self._landmarker = None
        self._yaw_history = []
        self._pitch_history = []
        self._smoothing_window = 3
        self._pitch_baseline = None  # Calibrated on first few frames
        self._calibration_pitches = []
        self._calibration_frames = 15  # Collect N frames to establish baseline
        self._init_landmarker()

    def _init_landmarker(self):
        """Initialize FaceLandmarker with the Tasks API."""
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
            logger.info("FaceLandmarker (Tasks API) initialized for head pose.")
        except Exception as e:
            logger.error(f"Failed to initialize FaceLandmarker: {e}")
            self._landmarker = None

    def estimate(self, frame: np.ndarray) -> dict:
        """
        Estimate head pose from a frame.

        Returns:
            dict with yaw, pitch, yaw_exceeded, pitch_exceeded.
        """
        if self._landmarker is None:
            return {"yaw": 0.0, "pitch": 0.0, "yaw_exceeded": False, "pitch_exceeded": False}

        try:
            rgb_frame = frame[:, :, ::-1].copy()
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            result = self._landmarker.detect(mp_image)

            if not result.face_landmarks:
                return {"yaw": 0.0, "pitch": 0.0, "yaw_exceeded": False, "pitch_exceeded": False}

            landmarks = result.face_landmarks[0]
            h, w = frame.shape[:2]

            # ── YAW: Ratio-based (works well for left/right) ──
            nose = landmarks[NOSE_TIP]
            left_cheek = landmarks[LEFT_CHEEK]
            right_cheek = landmarks[RIGHT_CHEEK]

            face_width = abs(right_cheek.x - left_cheek.x)
            if face_width < 0.01:
                face_width = 0.01

            face_center_x = (left_cheek.x + right_cheek.x) / 2
            nose_offset_x = (nose.x - face_center_x) / face_width
            yaw = nose_offset_x * 90.0

            # ── PITCH: Ratio-based (robust vertical estimation) ──
            forehead = landmarks[FOREHEAD]
            chin = landmarks[CHIN]

            face_height = abs(chin.y - forehead.y)
            if face_height < 0.01:
                face_height = 0.01

            raw_pitch_ratio = (nose.y - forehead.y) / face_height

            # Auto-calibrate: the first N frames establish the "looking straight" baseline ratio.
            if len(self._calibration_pitches) < self._calibration_frames:
                self._calibration_pitches.append(raw_pitch_ratio)
                if len(self._calibration_pitches) == self._calibration_frames:
                    # Use median to avoid outlier contamination
                    self._pitch_baseline = float(np.median(self._calibration_pitches))
                    logger.info(f"Head pose pitch baseline calibrated: {self._pitch_baseline:.3f}")

            if self._pitch_baseline is not None:
                # Calculate deviation from baseline.
                # If you look DOWN, nose moves closer to chin -> ratio increases -> deviation is positive.
                # If you look UP, nose moves closer to forehead -> ratio decreases -> deviation is negative.
                pitch_deviation = raw_pitch_ratio - self._pitch_baseline
                # Scale ratio to rough degrees (empirical multiplier: ~150 degrees per full scale)
                pitch = pitch_deviation * 150.0
            else:
                # During calibration, assume looking straight
                pitch = 0.0

            # Clamp for stability
            yaw = max(-90, min(90, yaw))
            pitch = max(-90, min(90, pitch))

            # Smooth with moving average
            yaw = self._smooth(yaw, self._yaw_history)
            pitch = self._smooth(pitch, self._pitch_history)

            return {
                "yaw": round(yaw, 1),
                "pitch": round(pitch, 1),
                "yaw_exceeded": abs(yaw) > HEAD_YAW_LIMIT,
                "pitch_exceeded": abs(pitch) > HEAD_PITCH_LIMIT,
            }

        except Exception as e:
            logger.error(f"Head pose estimation error: {e}")
            return {"yaw": 0.0, "pitch": 0.0, "yaw_exceeded": False, "pitch_exceeded": False}

    def _smooth(self, value: float, history: list) -> float:
        """Apply simple moving average smoothing."""
        history.append(value)
        if len(history) > self._smoothing_window:
            history.pop(0)
        return sum(history) / len(history)

    def close(self):
        """Release resources."""
        if self._landmarker:
            self._landmarker.close()
            self._landmarker = None
