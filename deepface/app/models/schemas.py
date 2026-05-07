"""
Pydantic v2 schemas for all request/response models in the DeepFace proctoring microservice.

These schemas define the API contract — integration with VerifiHireAI will use these exact shapes.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# FACE REGISTRATION
# ──────────────────────────────────────────────

class FaceRegisterRequest(BaseModel):
    """Register a new face for a person."""
    person_id: str = Field(..., description="Unique identifier for the person (e.g., candidate token)")
    image_base64: str = Field(..., description="Base64-encoded face image")
    label: Optional[str] = Field(None, description="Optional label (e.g., 'profile_photo')")
    overwrite: bool = Field(False, description="If True, existing face data for this ID will be overwritten")


class FaceRegisterResponse(BaseModel):
    """Response after face registration."""
    success: bool
    person_id: str
    message: str
    face_quality_score: Optional[float] = Field(None, description="Face quality: sharpness, alignment, etc.")
    embedding_count: int = Field(0, description="Total embeddings stored for this person")
    embedding_hash: Optional[str] = Field(None, description="SHA-256 hash of the face embedding for duplicate detection")


# ──────────────────────────────────────────────
# FACE VERIFICATION
# ──────────────────────────────────────────────

class FaceVerifyRequest(BaseModel):
    """Verify a face against a registered person."""
    person_id: str = Field(..., description="Person ID to verify against")
    image_base64: str = Field(..., description="Base64-encoded face image to verify")
    model: Optional[str] = Field(None, description="Override model: 'ArcFace' or 'SFace'. Defaults to config.")


class FaceVerifyResponse(BaseModel):
    """Verification result."""
    verified: bool
    confidence: float = Field(..., description="Confidence score (0-1, higher = more confident match)")
    distance: float = Field(..., description="Raw distance metric")
    threshold: float = Field(..., description="Threshold used for this verification")
    model_used: str = Field(..., description="Model backend used")
    low_confidence: bool = Field(False, description="True if in uncertain zone")
    message: str = ""


# ──────────────────────────────────────────────
# SESSION MANAGEMENT
# ──────────────────────────────────────────────

class SessionConfig(BaseModel):
    """Configuration for a monitoring session."""
    reverify_interval: Optional[int] = Field(None, description="Override re-verification interval (seconds)")
    enable_deepfake: bool = Field(True, description="Enable deepfake detection")
    enable_liveness: bool = Field(True, description="Enable liveness checks")


class SessionStartRequest(BaseModel):
    """Start a new monitoring session."""
    person_id: str = Field(..., description="Registered person to monitor")
    session_id: Optional[str] = Field(None, description="Custom session ID. Auto-generated if not provided.")
    config: Optional[SessionConfig] = Field(default_factory=SessionConfig)
    camera_device_name: Optional[str] = Field(None, description="Client's camera device name for virtual cam check")


class SessionStartResponse(BaseModel):
    """Response after starting a session."""
    session_id: str
    person_id: str
    status: str
    started_at: datetime
    message: str
    initial_verification: Optional[FaceVerifyResponse] = None
    virtual_camera_warning: bool = False


class SessionStatusResponse(BaseModel):
    """Current session status and metrics."""
    session_id: str
    person_id: str
    status: str  # active, paused, completed
    started_at: datetime
    duration_seconds: float
    total_frames_analyzed: int
    total_violations: int
    current_engagement_score: float
    micro_violation_score: float
    verification_success_rate: float


# ──────────────────────────────────────────────
# MONITORING (WebSocket frame analysis)
# ──────────────────────────────────────────────

class HeadPoseData(BaseModel):
    """Head pose estimation output."""
    yaw: float = Field(0.0, description="Left/right rotation in degrees")
    pitch: float = Field(0.0, description="Up/down tilt in degrees")
    yaw_exceeded: bool = False
    pitch_exceeded: bool = False





class LivenessData(BaseModel):
    """Liveness detection output."""
    is_live: bool = True
    texture_score: float = Field(0.0, description="Laplacian variance score")
    blink_detected: bool = False
    motion_score: float = Field(0.0, description="Inter-frame motion score")


class VerificationData(BaseModel):
    """Real-time verification output."""
    verified: bool = True
    confidence: float = 1.0
    model_used: str = "SFace"
    low_confidence: bool = False


class AlertMessage(BaseModel):
    """Real-time alert pushed via WebSocket."""
    type: str = Field(..., description="Violation type constant")
    severity: str = Field(..., description="INFO, WARNING, or CRITICAL")
    message: str = Field(..., description="Human-readable alert message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None


class MonitoringResult(BaseModel):
    """Complete analysis result for a single frame — sent back via WebSocket."""
    frame_number: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    face_present: bool = False
    face_count: int = 0
    verification: Optional[VerificationData] = None
    liveness: Optional[LivenessData] = None
    head_pose: Optional[HeadPoseData] = None

    engagement_score: float = 0.0
    micro_violation_score: float = 0.0
    alerts: List[AlertMessage] = Field(default_factory=list)


# ──────────────────────────────────────────────
# VIOLATIONS
# ──────────────────────────────────────────────

class ViolationEvent(BaseModel):
    """A single logged violation event."""
    id: Optional[int] = None
    session_id: str
    type: str
    severity: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None
    frame_snapshot_b64: Optional[str] = Field(None, description="Thumbnail of the violation frame")


class ViolationListResponse(BaseModel):
    """List of violations for a session."""
    session_id: str
    total: int
    violations: List[ViolationEvent]


# ──────────────────────────────────────────────
# REPORTS
# ──────────────────────────────────────────────

class SessionReportData(BaseModel):
    """JSON report data for a session."""
    session_id: str
    person_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    total_frames: int = 0
    total_violations: int = 0
    violation_breakdown: Dict[str, int] = Field(default_factory=dict)
    avg_engagement_score: float = 0.0
    min_engagement_score: float = 0.0
    max_engagement_score: float = 0.0
    final_micro_violation_score: float = 0.0
    verification_success_rate: float = 0.0
    overall_integrity_score: float = Field(0.0, description="0-100 composite integrity score")
    violations: List[ViolationEvent] = Field(default_factory=list)
