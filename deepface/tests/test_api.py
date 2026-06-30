"""
Tests for the DeepFace Proctoring Microservice API endpoints.

Run with: pytest tests/ -v
"""

import base64
import json
import os

import numpy as np
import pytest
from fastapi.testclient import TestClient

# Generate a simple solid-color test image (no real face, just for API shape testing)
def _make_test_image_b64(width=640, height=480, color=(128, 128, 128)):
    """Create a base64-encoded test image."""
    img = np.full((height, width, 3), color, dtype=np.uint8)
    import cv2
    _, buffer = cv2.imencode(".jpg", img)
    return base64.b64encode(buffer).decode("utf-8")


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def test_image_b64():
    """Generate a test image."""
    return _make_test_image_b64()


class TestHealthCheck:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "DeepFace Proctoring Microservice"

    def test_health(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestRegistration:
    def test_register_face(self, client, test_image_b64):
        response = client.post("/api/v1/registration/register", json={
            "person_id": "test_person_001",
            "image_base64": test_image_b64,
            "label": "test_photo",
        })
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["person_id"] == "test_person_001"

    def test_check_registration(self, client):
        response = client.get("/api/v1/registration/registered/test_person_001")
        assert response.status_code == 200
        data = response.json()
        assert data["person_id"] == "test_person_001"

    def test_verify_face(self, client, test_image_b64):
        response = client.post("/api/v1/registration/verify", json={
            "person_id": "test_person_001",
            "image_base64": test_image_b64,
        })
        assert response.status_code == 200
        data = response.json()
        assert "verified" in data
        assert "confidence" in data
        assert "model_used" in data

    def test_delete_registration(self, client):
        response = client.delete("/api/v1/registration/registered/test_person_001")
        # May succeed or fail depending on whether reg worked with a dummy image
        assert response.status_code in (200, 404)


class TestSession:
    def test_start_session(self, client):
        response = client.post("/api/v1/session/start", json={
            "person_id": "test_person_002",
            "session_id": "test_session_001",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test_session_001"
        assert data["status"] == "active"

    def test_get_session(self, client):
        response = client.get("/api/v1/session/test_session_001")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test_session_001"

    def test_get_violations(self, client):
        response = client.get("/api/v1/session/test_session_001/violations")
        assert response.status_code == 200
        data = response.json()
        assert "violations" in data

    def test_end_session(self, client):
        response = client.post("/api/v1/session/test_session_001/end")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"


class TestReports:
    def test_json_report(self, client):
        response = client.get("/api/v1/reports/test_session_001/json")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test_session_001"
        assert "total_violations" in data
        assert "overall_integrity_score" in data

    def test_pdf_report(self, client):
        response = client.get("/api/v1/reports/test_session_001")
        # PDF generation should work
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"

    def test_nonexistent_report(self, client):
        response = client.get("/api/v1/reports/nonexistent_session/json")
        assert response.status_code == 404
