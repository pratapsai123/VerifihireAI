"""
Image utility functions for the DeepFace proctoring microservice.

Handles base64 decoding, format conversion, resizing, and preprocessing.
All functions are designed to work with both base64 strings and raw numpy arrays.
"""

import base64
import io
import logging
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def decode_base64_image(base64_string: str) -> np.ndarray:
    """
    Decode a base64-encoded image string into an OpenCV BGR numpy array.

    Handles both raw base64 and data URI formats (e.g., "data:image/jpeg;base64,...").

    Args:
        base64_string: Base64-encoded image string.

    Returns:
        OpenCV BGR image as numpy array.

    Raises:
        ValueError: If the image cannot be decoded.
    """
    try:
        # Strip data URI prefix if present
        if "," in base64_string:
            base64_string = base64_string.split(",", 1)[1]

        image_bytes = base64.b64decode(base64_string)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("cv2.imdecode returned None — invalid image data")

        return img
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {e}")
        raise ValueError(f"Invalid base64 image: {e}")


def encode_image_to_base64(image: np.ndarray, fmt: str = ".jpg", quality: int = 80) -> str:
    """
    Encode an OpenCV BGR numpy array to a base64 string.

    Args:
        image: OpenCV BGR image.
        fmt: Image format extension (e.g., ".jpg", ".png").
        quality: JPEG quality (1-100). Ignored for PNG.

    Returns:
        Base64-encoded string (without data URI prefix).
    """
    encode_params = []
    if fmt.lower() in (".jpg", ".jpeg"):
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]

    _, buffer = cv2.imencode(fmt, image, encode_params)
    return base64.b64encode(buffer).decode("utf-8")


def resize_image(image: np.ndarray, max_width: int = 640, max_height: int = 480) -> np.ndarray:
    """
    Resize an image to fit within max dimensions while preserving aspect ratio.

    Args:
        image: OpenCV BGR image.
        max_width: Maximum width.
        max_height: Maximum height.

    Returns:
        Resized image.
    """
    h, w = image.shape[:2]

    if w <= max_width and h <= max_height:
        return image

    scale = min(max_width / w, max_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def convert_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convert OpenCV BGR image to RGB."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert an image to grayscale."""
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def compute_laplacian_variance(image: np.ndarray) -> float:
    """
    Compute the Laplacian variance of an image.
    Higher values indicate sharper (less blurry) images.

    Args:
        image: OpenCV BGR or grayscale image.

    Returns:
        Laplacian variance (float).
    """
    gray = convert_to_grayscale(image)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return float(laplacian.var())


def compute_frame_diff(frame1: np.ndarray, frame2: np.ndarray) -> float:
    """
    Compute the mean absolute pixel difference between two frames.

    Used for motion detection and temporal consistency analysis.

    Args:
        frame1: First frame (BGR).
        frame2: Second frame (BGR).

    Returns:
        Mean pixel difference.
    """
    gray1 = convert_to_grayscale(frame1)
    gray2 = convert_to_grayscale(frame2)

    # Ensure same dimensions
    if gray1.shape != gray2.shape:
        gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))

    diff = cv2.absdiff(gray1, gray2)
    return float(np.mean(diff))


def crop_face_region(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    padding: float = 0.2,
) -> Optional[np.ndarray]:
    """
    Crop a face region from an image with optional padding.

    Args:
        image: OpenCV BGR image.
        bbox: (x, y, w, h) bounding box.
        padding: Fractional padding around the face (0.2 = 20%).

    Returns:
        Cropped face image, or None if bbox is invalid.
    """
    h, w = image.shape[:2]
    x, y, bw, bh = bbox

    pad_x = int(bw * padding)
    pad_y = int(bh * padding)

    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(w, x + bw + pad_x)
    y2 = min(h, y + bh + pad_y)

    if x2 <= x1 or y2 <= y1:
        return None

    return image[y1:y2, x1:x2]


def numpy_to_pil(image: np.ndarray) -> Image.Image:
    """Convert an OpenCV BGR numpy array to a PIL Image (RGB)."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def pil_to_numpy(image: Image.Image) -> np.ndarray:
    """Convert a PIL Image (RGB) to an OpenCV BGR numpy array."""
    rgb = np.array(image)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def create_thumbnail(image: np.ndarray, size: Tuple[int, int] = (160, 120)) -> np.ndarray:
    """Create a small thumbnail of an image for report embedding."""
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def enhance_for_recognition(image: np.ndarray) -> np.ndarray:
    """
    Enhance an image for better face recognition accuracy.

    Applies adaptive histogram equalization (CLAHE) to handle:
    - Low-light / dim webcam conditions
    - Uneven lighting / shadows on face
    - Distance-related loss of contrast

    The enhancement is applied per-channel in LAB color space so that
    colors are preserved while luminance is normalized.

    Args:
        image: OpenCV BGR image.

    Returns:
        Enhanced BGR image with normalized brightness/contrast.
    """
    if image is None or image.size == 0:
        return image

    try:
        # Convert to LAB color space (L = lightness, A/B = color channels)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # clipLimit controls contrast amplification — 2.5 is a good balance
        # tileGridSize controls the local region size for adaptation
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l_channel)

        # Merge back and convert to BGR
        lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
        enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

        # Light Gaussian blur to reduce webcam noise (helps embedding stability)
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)

        return enhanced
    except Exception as e:
        logger.warning(f"Image enhancement failed, using original: {e}")
        return image
