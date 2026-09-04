"""Unit tests for the custom exception hierarchy."""
import pytest

from exceptions import (
    ClassificationParseError,
    GeminiAPIError,
    InvalidImageError,
    SortItError,
)


def test_sortit_error_base_status_500():
    err = SortItError("oops")
    assert err.message == "oops"
    assert err.status_code == 500
    assert isinstance(err, Exception)


def test_gemini_api_error_status_502():
    err = GeminiAPIError("quota exceeded")
    assert err.status_code == 502
    assert isinstance(err, SortItError)


def test_invalid_image_error_status_400():
    err = InvalidImageError("empty file")
    assert err.status_code == 400
    assert isinstance(err, SortItError)


def test_classification_parse_error_status_500():
    err = ClassificationParseError("malformed")
    assert err.status_code == 500
    assert isinstance(err, SortItError)


def test_can_be_raised_and_caught_as_base():
    with pytest.raises(SortItError):
        raise GeminiAPIError("boom")
    with pytest.raises(SortItError):
        raise ClassificationParseError("nope")
    with pytest.raises(SortItError):
        raise InvalidImageError("nope")
