# DeepFace Proctoring Integration Guide

This document outlines how to integrate the DeepFace Proctoring microservice into external applications (such as a VerifiHire Django/Next.js frontend).

## Architecture Overview
DeepFace runs as a completely independent **FastAPI Microservice**. 
It should be run on its own port (default: `8500`) alongside your main web backend (e.g., port `8000`). 

**Do NOT merge DeepFace into your main monolithic backend.** Video processing requires heavy CPU resources; keeping it isolated ensures your main backend never freezes. 

The microservice has CORS configured to accept incoming requests from any frontend (`*`), so your web client can communicate with it directly through REST and WebSockets.

---

## The 4-Step Integration Flow

### 1. Register the Candidate (REST)
Before a test begins, you must register the candidate's canonical face image into the system so the AI knows who it is looking for. 

**Endpoint:** `POST http://localhost:8500/api/v1/registration/register`
**Content-Type:** `application/json`

```json
// Request Body
{
  "person_id": "candidate_001",
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
  "label": "profile_photo"
}
```

```json
// Response Body
{
  "success": true,
  "person_id": "candidate_001",
  "message": "Successfully registered face profile",
  "face_quality_score": 0.95
}
```

---

### 2. Start a Proctoring Session (REST)
Right before the user starts their actual interview/exam, command the microservice to open a monitoring session.

**Endpoint:** `POST http://localhost:8500/api/v1/sessions/start`
**Content-Type:** `application/json`

```json
// Request Body
{
  "person_id": "candidate_001",
  "config": {
    "enable_liveness": true,
    "enable_deepfake": true
  }
}
```

```json
// Response Body
{
  "session_id": "session_abc123xyz",
  "person_id": "candidate_001",
  "status": "active"
}
```

---

### 3. Stream Live Video & Receive Alerts (WebSocket)
This is the core of the integration. Your frontend must capture the user's webcam, compress the frames, and send them over a WebSocket connection to DeepFace. DeepFace will instantly reply with AI judgments.

**WebSocket URL:** `ws://localhost:8500/api/v1/monitoring/ws/{session_id}`

#### Frontend JavaScript Example:
```javascript
// 1. Open Connection
const sessionId = "session_abc123xyz";
const ws = new WebSocket(`ws://localhost:8500/api/v1/monitoring/ws/${sessionId}`);

const videoElement = document.getElementById("userWebcam");
const hiddenCanvas = document.createElement("canvas");
hiddenCanvas.width = 640;
hiddenCanvas.height = 480;
const ctx = hiddenCanvas.getContext("2d");

// 2. Transmit Frames (approx. 5 frames per second is optimal)
const streamInterval = setInterval(() => {
    if (ws.readyState !== WebSocket.OPEN) return;
    
    // Draw current video frame to canvas
    ctx.drawImage(videoElement, 0, 0, hiddenCanvas.width, hiddenCanvas.height);
    
    // Convert to highly-compressed jpeg (Quality 0.5 saves massive bandwidth)
    const base64Frame = hiddenCanvas.toDataURL("image/jpeg", 0.5);
    
    ws.send(JSON.stringify({
        type: "frame",
        image_base64: base64Frame
    }));
}, 200);

// 3. Receive AI Analytics & Alerts
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    console.log("Current Engagement Score:", data.engagement_score);
    
    // Check if the AI flagged a rule violation
    if (data.alerts && data.alerts.length > 0) {
        data.alerts.forEach(alert => {
            console.warn(`[${alert.severity}] ${alert.message}`);
            // e.g. Show a red warning toast to the screen: "Multiple Faces Detected!"
        });
    }
};

// Clean up
window.onbeforeunload = () => {
    clearInterval(streamInterval);
    ws.close();
};
```

---

### 4. Fetch the Final Integrity Report (REST)
Once the exam finishes, pull the official final report from the microservice. You can save this JSON payload directly into your main VerifiHire database to show recruiters.

**Endpoint:** `GET http://localhost:8500/api/v1/reports/{session_id}/json`

```json
// Response Body Snippet
{
  "session_id": "session_abc123xyz",
  "duration_seconds": 1205.5,
  "overall_integrity_score": 85.0,
  "verification_success_rate": 99.1,
  "total_violations": 2,
  "violations": [
    {
      "type": "multiple_faces",
      "severity": "CRITICAL",
      "message": "Multiple faces detected — possible proxy candidate",
      "timestamp": "2026-04-15T12:00:05Z"
    }
  ]
}
```

## Security Note
Because `CORS_ORIGINS` is set to `["*"]` centrally, your VerifiHire frontend code can run under any domain name or IP without getting blocked by the browser. 
