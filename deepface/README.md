# DeepFace Proctoring Microservice

A production-grade, standalone face recognition and proctoring API built with FastAPI. Designed for integration with hiring assessment platforms.

## Features (19 total)

| # | Feature | Status |
|---|---------|--------|
| 1 | Face Registration | ✅ |
| 2 | Face Verification (Hybrid ArcFace + SFace) | ✅ |
| 3 | Liveness Detection | ✅ |
| 4 | Face Presence Detection | ✅ |
| 5 | Face Count Detection | ✅ |
| 6 | Periodic Re-verification | ✅ |
| 7 | Head Pose Estimation (Yaw) | ✅ |
| 8 | Head Pose Estimation (Pitch) | ✅ |
| 9 | Gaze Direction Tracking | ✅ |
| 10 | Prolonged Look-Away Detection | ✅ |
| 11 | Emotion Analysis | ✅ |
| 12 | Emotion Anomaly Flagging | ✅ |
| 13 | Engagement Scoring | ✅ |
| 14 | Real-time Alert System | ✅ |
| 15 | Violation Event Logging | ✅ |
| 16 | Session Report Generation (PDF + JSON) | ✅ |
| 17 | Deepfake / Virtual Camera Detection | ✅ |
| 18 | Low Verification Confidence Flagging | ✅ |
| 19 | Repeated Micro-Violations Scoring | ✅ |

## Architecture

- **Framework:** FastAPI (async, WebSocket-native)
- **Face Recognition:** DeepFace (ArcFace for accuracy, SFace for speed)
- **Face Mesh:** MediaPipe (468+10 iris landmarks)
- **Database:** SQLite (via aiosqlite)
- **Reports:** ReportLab (PDF generation)

## Quick Start

### 1. Install Dependencies

```bash
cd deepface
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 2. Start the Service

```bash
python run.py
# OR with auto-reload for development:
python run.py --reload
```

The service starts at `http://localhost:8500`.

### 3. API Documentation

- Swagger UI: http://localhost:8500/api/v1/docs
- ReDoc: http://localhost:8500/api/v1/redoc

## API Endpoints

### Registration
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/registration/register` | Register a face |
| POST | `/api/v1/registration/verify` | One-shot verification |
| GET | `/api/v1/registration/registered/{id}` | Check registration |
| DELETE | `/api/v1/registration/registered/{id}` | Delete registration |

### Session Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/session/start` | Start monitoring session |
| GET | `/api/v1/session/{id}` | Get session status |
| POST | `/api/v1/session/{id}/end` | End session |
| GET | `/api/v1/session/{id}/violations` | Get violations |

### Real-time Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| WebSocket | `/api/v1/ws/monitor/{session_id}` | Stream frames for analysis |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reports/{id}` | Download PDF report |
| GET | `/api/v1/reports/{id}/json` | Get JSON report |

## WebSocket Protocol

### Client sends:
```json
{"frame": "<base64_encoded_image>"}
```

### Server responds:
```json
{
  "frame_number": 42,
  "face_present": true,
  "face_count": 1,
  "verification": {"verified": true, "confidence": 0.92, "model_used": "SFace"},
  "liveness": {"is_live": true, "texture_score": 156.3},
  "head_pose": {"yaw": -5.2, "pitch": 3.1},
  "gaze": {"direction": "center", "off_screen": false},
  "emotion": {"dominant": "neutral", "scores": {"neutral": 0.85}},
  "engagement_score": 82.5,
  "micro_violation_score": 3.2,
  "alerts": []
}
```

## Integration with VerifiHireAI

This service is designed to integrate with the main platform:

1. **React Frontend:** Send webcam frames via WebSocket to `/ws/monitor/{session_id}`
2. **Django Backend:** Call REST endpoints for registration, session management, and reports
3. All APIs use **base64 image encoding** (compatible with existing `webcamScreenshot` format)
4. Session IDs map directly to the existing `token` pattern

## Configuration

All thresholds and settings are in `app/config.py`. Key settings:

- `REGISTRATION_MODEL`: ArcFace (high accuracy)
- `MONITORING_MODEL`: SFace (high speed)
- `REVERIFY_INTERVAL_SECONDS`: Full re-verification interval
- `HEAD_YAW_LIMIT` / `HEAD_PITCH_LIMIT`: Head rotation limits
- `GAZE_LOOKAWAY_DURATION`: Look-away alert threshold
- `MICRO_VIOLATION_CRITICAL_THRESHOLD`: Accumulated violation limit
