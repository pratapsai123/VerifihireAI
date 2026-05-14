"""
DeepFace Proctoring Microservice — Central Configuration

All tunable thresholds, paths, and settings are defined here.
Modify these values to calibrate the system for your environment.
"""

import os
import re
from pathlib import Path
from decouple import AutoConfig

# ──────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REGISTERED_FACES_DIR = DATA_DIR / "registered_faces"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
DB_PATH = DATA_DIR / "proctoring.db"  # Legacy — kept for reference only

# ──────────────────────────────────────────────
# POSTGRESQL — reads from VerifiHireAI settings.py
# ──────────────────────────────────────────────
def _read_django_db_config() -> dict:
    """
    Parse the Django settings.py to extract DATABASES default values.
    This ensures deepface always uses the same DB credentials as the
    main backend — a single source of truth.
    """
    settings_path = BASE_DIR.parent / "backend" / "VerifiHireAI_backend" / "settings.py"

    defaults = {
        "DB_NAME": "",
        "DB_USER": "",
        "DB_PASSWORD": "",
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "5432",
    }

    try:
        text = settings_path.read_text(encoding="utf-8")
        # Extract defaults from: os.environ.get
        for key in defaults:
            # Pattern 1: os.environ.get('KEY', 'DEFAULT')
            pattern1 = rf"os\.environ\.get\(\s*['\"]({key})['\"].*?['\"](.+?)['\"]\s*\)"
            match1 = re.search(pattern1, text)
            if match1:
                defaults[key] = match1.group(2)
            else:
                # Pattern 2: config('KEY', default='DEFAULT') or config('KEY')
                pattern2 = rf"config\(\s*['\"]({key})['\"](?:,\s*default=['\"](.+?)['\"])?\s*\)"
                match2 = re.search(pattern2, text)
                if match2 and match2.group(2):
                    defaults[key] = match2.group(2)
    except Exception:
        pass  # Fall back to hardcoded defaults if settings.py can't be read

    # Return defaults (which may have been updated by parsing settings.py)
    return defaults

# Load backend .env file
env_path = BASE_DIR.parent / "backend"
backend_config = AutoConfig(search_path=str(env_path)) if env_path.exists() else AutoConfig()

_pg = _read_django_db_config()
PG_HOST = backend_config('DB_HOST', default=_pg["DB_HOST"])
PG_PORT = backend_config('DB_PORT', default=_pg["DB_PORT"], cast=int)
PG_NAME = backend_config('DB_NAME', default=_pg["DB_NAME"])
PG_USER = backend_config('DB_USER', default=_pg["DB_USER"])
PG_PASSWORD = backend_config('DB_PASSWORD', default=_pg["DB_PASSWORD"])

# Ensure directories exist
for d in [DATA_DIR, REGISTERED_FACES_DIR, LOGS_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# SERVER
# ──────────────────────────────────────────────
HOST = os.getenv("DEEPFACE_HOST", "0.0.0.0")
PORT = int(os.getenv("DEEPFACE_PORT", "8500"))
CORS_ORIGINS = os.getenv("DEEPFACE_CORS_ORIGINS", "*").split(",")
API_PREFIX = "/api/v1"

# ──────────────────────────────────────────────
# FACE RECOGNITION MODELS (Hybrid Strategy)
# ──────────────────────────────────────────────
# ArcFace: High accuracy — used for registration & initial session verification
REGISTRATION_MODEL = "ArcFace"
REGISTRATION_DETECTOR = "opencv"
REGISTRATION_DISTANCE_METRIC = "cosine"
REGISTRATION_THRESHOLD = 0.60  # Cosine distance threshold for ArcFace (relaxed for webcam/lighting variance)

# SFace: High speed — used for continuous real-time monitoring
MONITORING_MODEL = "SFace"
MONITORING_DETECTOR = "opencv"
MONITORING_DISTANCE_METRIC = "cosine"
MONITORING_THRESHOLD = 0.50  # Balanced SFace threshold for live webcam variance (more relaxed)

# Low-confidence zone: between threshold and this value triggers a warning instead of hard fail
LOW_CONFIDENCE_MARGIN = 0.12  # e.g., 0.50 - 0.62 is "uncertain"

# ──────────────────────────────────────────────
# FACE DETECTION
# ──────────────────────────────────────────────
FACE_DETECTION_CONFIDENCE = 0.4  # MediaPipe min detection confidence (lowered for dim lighting)
EXPECTED_FACE_COUNT = 1  # Flag if face count != this value

# ──────────────────────────────────────────────
# LIVENESS DETECTION
# ──────────────────────────────────────────────
LIVENESS_LAPLACIAN_THRESHOLD = 80.0  # Below this = flat/printed image
LIVENESS_EAR_THRESHOLD = 0.21  # Eye Aspect Ratio below this = blink
LIVENESS_BLINK_CONSEC_FRAMES = 2  # Min consecutive frames for a blink
LIVENESS_MOTION_THRESHOLD = 5.0  # Pixel-level diff threshold between frames

# ──────────────────────────────────────────────
# HEAD POSE ESTIMATION
# ──────────────────────────────────────────────
HEAD_YAW_LIMIT = 30.0  # Degrees — beyond this triggers alert
HEAD_PITCH_LIMIT = 25.0  # Degrees — beyond this triggers alert



# ──────────────────────────────────────────────
# ENGAGEMENT SCORING (weights must sum to 1.0)
# ──────────────────────────────────────────────
ENGAGEMENT_WEIGHTS = {
    "face_presence": 0.30,
    "head_pose_attentive": 0.30,
    "liveness": 0.20,
    "verification": 0.20,
}

# ──────────────────────────────────────────────
# PERIODIC RE-VERIFICATION
# ──────────────────────────────────────────────
REVERIFY_INTERVAL_SECONDS = 120  # Full ArcFace re-verification every 2 minutes
REVERIFY_SFACE_INTERVAL = 2  # SFace quick-check every 2 seconds

# ──────────────────────────────────────────────
# DEEPFAKE / VIRTUAL CAMERA DETECTION
# ──────────────────────────────────────────────
VIRTUAL_CAMERA_SIGNATURES = [
    "obs virtual camera", "obs-camera", "manycam",
    "snap camera", "xsplit", "droidcam",
    "iriun", "epoccam", "iv cam", "ndi",
    "virtual", "fake", "camtwist",
]
DEEPFAKE_FREQUENCY_THRESHOLD = 0.15  # DCT high-freq energy ratio anomaly threshold
DEEPFAKE_TEMPORAL_SMOOTHNESS_THRESHOLD = 2.0  # Unnaturally smooth frame transitions

# ──────────────────────────────────────────────
# ALERT SYSTEM
# ──────────────────────────────────────────────
ALERT_COOLDOWN_SECONDS = 5.0  # Min interval between repeated alerts of the same type
ALERT_SEVERITY_LEVELS = ["INFO", "WARNING", "CRITICAL"]

# ──────────────────────────────────────────────
# VIOLATION SCORING
# ──────────────────────────────────────────────
VIOLATION_WEIGHTS = {
    "no_face": 3.0,
    "multiple_faces": 5.0,
    "verification_failed": 5.0,
    "low_confidence": 2.0,
    "liveness_failed": 5.0,
    "head_yaw_exceeded": 1.5,
    "head_pitch_exceeded": 1.5,
    "deepfake_suspected": 10.0,
    "virtual_camera": 10.0,
}
MICRO_VIOLATION_DECAY_SECONDS = 300  # Violations older than this decay in score
MICRO_VIOLATION_CRITICAL_THRESHOLD = 25.0  # Accumulated score that triggers critical alert

# ──────────────────────────────────────────────
# SESSION & REPORTING
# ──────────────────────────────────────────────
SESSION_MAX_DURATION_HOURS = 4  # Auto-close sessions after this
REPORT_INCLUDE_FRAME_SNAPSHOTS = True  # Include violation frame thumbnails in PDF
REPORT_MAX_SNAPSHOTS = 20  # Limit snapshots in report to control file size
