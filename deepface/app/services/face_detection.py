"""
Features 4 & 5: Face Detection Service (Presence & Count)

- Face Presence Detection: Is at least one face in the frame?
- Face Count Detection: How many faces are in the frame? Flag if ≠ 1.

Uses MediaPipe FaceLandmarker (Tasks API) for detection — this is more
reliable than the separate FaceDetector for webcam streams.
"""

import logging
from pathlib import Path

import mediapipe as mp
import numpy as np

from app.config import EXPECTED_FACE_COUNT, FACE_DETECTION_CONFIDENCE

logger = logging.getLogger(__name__)

# Use the FaceLandmarker model (more reliable for webcam detection)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models_data" / "face_landmarker.task"


class FaceDetectionService:
    """Detects faces using MediaPipe FaceLandmarker Tasks API."""

    def __init__(self):
        self._landmarker = None
        self._init()

    def _init(self):
        """Initialize FaceLandmarker for face detection."""
        try:
            base_options = mp.tasks.BaseOptions(
                model_asset_path=str(MODEL_PATH)
            )
            options = mp.tasks.vision.FaceLandmarkerOptions(
                base_options=base_options,
                num_faces=5,  # detect up to 5 to count them
                min_face_detection_confidence=FACE_DETECTION_CONFIDENCE,
                min_face_presence_confidence=FACE_DETECTION_CONFIDENCE,
                min_tracking_confidence=0.4,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False,
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
            )
            self._landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)
            logger.info("FaceLandmarker initialized for face detection.")
        except Exception as e:
            logger.error(f"Failed to initialize FaceLandmarker for detection: {e}")
            self._landmarker = None

    def detect(self, frame: np.ndarray) -> dict:
        """
        Detect faces in a frame.

        Returns:
            dict with face_present (bool), face_count (int),
            bounding_boxes (list), violation (str or None).
        """
        if self._landmarker is None:
            return {
                "face_present": False,
                "face_count": 0,
                "bounding_boxes": [],
                "violation": "face_detector_unavailable",
            }

        try:
            # Convert BGR (OpenCV) to RGB for MediaPipe
            rgb_frame = frame[:, :, ::-1].copy()
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            result = self._landmarker.detect(mp_image)

            # Extract approximate bounding boxes from landmarks.
            bounding_boxes = []
            h, w = frame.shape[:2]
            for face_lms in result.face_landmarks:
                # Clamp normalized landmark coordinates to image bounds.
                # Some landmarks can briefly fall outside [0, 1], which creates
                # shifted/oversized boxes if used directly.
                xs = [max(0.0, min(1.0, lm.x)) * w for lm in face_lms]
                ys = [max(0.0, min(1.0, lm.y)) * h for lm in face_lms]
                x_min, x_max = int(min(xs)), int(max(xs))
                y_min, y_max = int(min(ys)), int(max(ys))
                box_w = max(0, x_max - x_min)
                box_h = max(0, y_max - y_min)

                # Filter tiny/unstable detections to avoid random false tracking boxes.
                area_ratio = (box_w * box_h) / float(max(1, w * h))
                if area_ratio < 0.015:
                    continue

                x_min = max(0, min(x_min, w - 1))
                y_min = max(0, min(y_min, h - 1))

                bounding_boxes.append({
                    "x": x_min,
                    "y": y_min,
                    "width": box_w,
                    "height": box_h,
                    "confidence": 0.95,
                })

            # Sort largest first so downstream tracking uses the primary face consistently.
            bounding_boxes.sort(key=lambda b: b["width"] * b["height"], reverse=True)

            face_count = len(bounding_boxes)
            face_present = face_count > 0

            # Determine violation
            violation = None
            if not face_present:
                violation = "no_face"
            elif face_count != EXPECTED_FACE_COUNT:
                violation = "multiple_faces"

            return {
                "face_present": face_present,
                "face_count": face_count,
                "bounding_boxes": bounding_boxes,
                "violation": violation,
            }

        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return {
                "face_present": False,
                "face_count": 0,
                "bounding_boxes": [],
                "violation": "detection_error",
            }

    def close(self):
        """Release resources."""
        if self._landmarker:
            self._landmarker.close()
            self._landmarker = None
