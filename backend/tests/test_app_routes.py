"""Integration tests for Flask routes — Gemini is mocked."""
import io
import os
from unittest.mock import patch

import pytest

# Set required env vars BEFORE importing app
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("GEMINI_MODEL", "gemini-2.5-flash")

from app import app  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_home_health_check(client):
    res = client.get("/")
    assert res.status_code == 200
    body = res.get_json()
    assert "running" in body["message"].lower()
    assert "confidence_threshold" in body


def test_analyze_missing_image_returns_400(client):
    res = client.post("/analyze", data={}, content_type="multipart/form-data")
    assert res.status_code == 400
    body = res.get_json()
    assert body["error_type"] == "InvalidImageError"


def test_analyze_empty_file_returns_400(client):
    res = client.post("/analyze", data={"image": (io.BytesIO(b""), "x.jpg")}, content_type="multipart/form-data")
    assert res.status_code == 400
    assert res.get_json()["error_type"] == "InvalidImageError"


@patch("app.classify_waste")
def test_analyze_success_returns_200_and_below_threshold_flag(mock_clf, client):
    mock_clf.return_value = {
        "waste_type": "plastic",
        "waste_name": "PET Bottle",
        "waste_detail": "Type 1",
        "confidence": 92,
        "instructions": ["rinse", "recycle"],
        "tip": "crush it",
        "below_threshold": False,
    }
    res = client.post(
        "/analyze",
        data={"image": (io.BytesIO(b"fake-jpeg-bytes"), "waste.jpg")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["waste_type"] == "plastic"
    assert body["confidence"] == 92
    assert body["below_threshold"] is False


@patch("app.classify_waste")
def test_analyze_low_confidence_marks_below_threshold(mock_clf, client):
    mock_clf.return_value = {
        "waste_type": "unknown",
        "waste_name": "Mystery item",
        "waste_detail": "",
        "confidence": 30,
        "instructions": [],
        "tip": "",
        "below_threshold": True,
    }
    res = client.post(
        "/analyze",
        data={"image": (io.BytesIO(b"x"), "x.jpg")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    assert res.get_json()["below_threshold"] is True


@patch("app.classify_waste", side_effect=Exception("boom"))
def test_analyze_unhandled_exception_returns_500(mock_clf, client):
    res = client.post(
        "/analyze",
        data={"image": (io.BytesIO(b"x"), "x.jpg")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 500
    body = res.get_json()
    assert body["error_type"] == "InternalServerError"


def test_correct_missing_body_returns_400(client):
    res = client.post("/correct", json={})
    assert res.status_code == 400


def test_correct_missing_waste_type_returns_400(client):
    res = client.post("/correct", json={"note": "should be plastic"})
    assert res.status_code == 400
    assert "corrected_waste_type" in res.get_json()["message"]


def test_correct_success_returns_200(client, tmp_path):
    # Re-route storage to tmp file to avoid polluting repo
    from storage_interface import StorageBackend

    class TmpStorage(StorageBackend):
        def __init__(self, p):
            self.filepath = str(p)

        def save_correction(self, record):
            import json
            data = self.get_corrections()
            data.append(record)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        def get_corrections(self):
            import json, os
            if not os.path.exists(self.filepath):
                return []
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)

    p = tmp_path / "corr.json"
    import app as app_module
    app_module.storage = TmpStorage(p)

    payload = {
        "original_result": {"waste_type": "plastic", "waste_name": "Bottle"},
        "corrected_waste_type": "glass",
        "note": "looks like glass to me",
        "timestamp": "2026-01-01T00:00:00Z",
    }
    res = client.post("/correct", json=payload)
    assert res.status_code == 200
    assert res.get_json()["status"] == "logged"
    assert p.exists()
