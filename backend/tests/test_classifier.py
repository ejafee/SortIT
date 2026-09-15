"""Unit tests for the classifier JSON validation/parsing logic."""
import pytest

from classifier import _get_model_name, _validate_and_normalize, _clean_response_text
from exceptions import ClassificationParseError, GeminiAPIError


def test_default_model_is_gemini_35_flash(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert _get_model_name() == "gemini-3.5-flash"


def test_clean_response_strips_json_fence():
    raw = '```json\n{"waste_type": "plastic"}\n```'
    cleaned = _clean_response_text(raw)
    assert cleaned == '{"waste_type": "plastic"}'


def test_clean_response_plain_text():
    raw = '{"waste_type": "glass"}'
    assert _clean_response_text(raw) == raw


def test_validate_normalize_valid_response():
    raw = {
        "waste_type": "Plastic",
        "waste_name": "PET Bottle",
        "waste_detail": "Type 1",
        "confidence": 92,
        "instructions": ["rinse", "recycle"],
        "tip": "crush it",
    }
    out = _validate_and_normalize(raw)
    assert out["waste_type"] == "plastic"
    assert out["confidence"] == 92
    assert out["below_threshold"] is False


def test_validate_normalize_clamps_confidence():
    raw = {
        "waste_type": "paper",
        "waste_name": "Newspaper",
        "confidence": 250,
        "instructions": ["recycle"],
    }
    out = _validate_and_normalize(raw)
    assert out["confidence"] == 100


def test_validate_normalize_marks_below_threshold():
    raw = {
        "waste_type": "glass",
        "waste_name": "Jar",
        "confidence": 40,
        "instructions": ["x"],
    }
    out = _validate_and_normalize(raw)
    assert out["below_threshold"] is True


def test_validate_normalize_unknown_type_falls_back():
    raw = {
        "waste_type": "spaceship",
        "waste_name": "X",
        "confidence": 80,
        "instructions": [],
    }
    out = _validate_and_normalize(raw)
    assert out["waste_type"] == "unknown"


def test_validate_normalize_missing_required_raises():
    with pytest.raises(ClassificationParseError):
        _validate_and_normalize({"waste_type": "plastic"})


def test_validate_normalize_non_numeric_confidence_raises():
    with pytest.raises(ClassificationParseError):
        _validate_and_normalize({
            "waste_type": "plastic",
            "waste_name": "x",
            "confidence": "high",
            "instructions": [],
        })


def test_validate_normalize_instructions_must_be_list():
    with pytest.raises(ClassificationParseError):
        _validate_and_normalize({
            "waste_type": "plastic",
            "waste_name": "x",
            "confidence": 80,
            "instructions": "not a list",
        })


def test_gemini_api_error_is_typed():
    err = GeminiAPIError("network")
    assert err.status_code == 502
    assert isinstance(err, Exception)
