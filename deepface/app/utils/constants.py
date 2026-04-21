"""
Violation types and severity constants used across the proctoring system.
"""


class ViolationType:
    """Enumeration of all violation event types."""
    NO_FACE = "no_face"
    MULTIPLE_FACES = "multiple_faces"
    VERIFICATION_FAILED = "verification_failed"
    LOW_CONFIDENCE = "low_confidence_verification"
    LIVENESS_FAILED = "liveness_failed"
    HEAD_YAW_EXCEEDED = "head_yaw_exceeded"
    HEAD_PITCH_EXCEEDED = "head_pitch_exceeded"

    DEEPFAKE_SUSPECTED = "deepfake_suspected"
    VIRTUAL_CAMERA = "virtual_camera_detected"
    LOW_ENGAGEMENT = "low_engagement"
    MICRO_VIOLATION_CRITICAL = "micro_violation_threshold_exceeded"


class Severity:
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# Map violation types to their default severity
VIOLATION_SEVERITY_MAP = {
    ViolationType.NO_FACE: Severity.WARNING,
    ViolationType.MULTIPLE_FACES: Severity.CRITICAL,
    ViolationType.VERIFICATION_FAILED: Severity.CRITICAL,
    ViolationType.LOW_CONFIDENCE: Severity.WARNING,
    ViolationType.LIVENESS_FAILED: Severity.CRITICAL,
    ViolationType.HEAD_YAW_EXCEEDED: Severity.INFO,
    ViolationType.HEAD_PITCH_EXCEEDED: Severity.INFO,

    ViolationType.DEEPFAKE_SUSPECTED: Severity.CRITICAL,
    ViolationType.VIRTUAL_CAMERA: Severity.CRITICAL,
    ViolationType.LOW_ENGAGEMENT: Severity.WARNING,
    ViolationType.MICRO_VIOLATION_CRITICAL: Severity.CRITICAL,
}

# Human-readable descriptions for reports
VIOLATION_DESCRIPTIONS = {
    ViolationType.NO_FACE: "No face detected in the frame",
    ViolationType.MULTIPLE_FACES: "Multiple faces detected — possible proxy candidate",
    ViolationType.VERIFICATION_FAILED: "Face does not match registered identity",
    ViolationType.LOW_CONFIDENCE: "Face verification confidence is below acceptable threshold",
    ViolationType.LIVENESS_FAILED: "Liveness check failed — possible photo/video replay attack",
    ViolationType.HEAD_YAW_EXCEEDED: "Head turned excessively to the side",
    ViolationType.HEAD_PITCH_EXCEEDED: "Head tilted excessively up or down",

    ViolationType.DEEPFAKE_SUSPECTED: "Possible deepfake or AI-generated video detected",
    ViolationType.VIRTUAL_CAMERA: "Virtual camera software detected",
    ViolationType.LOW_ENGAGEMENT: "Candidate engagement score dropped below threshold",
    ViolationType.MICRO_VIOLATION_CRITICAL: "Accumulated minor violations exceeded safety threshold",
}
