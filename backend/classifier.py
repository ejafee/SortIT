# ============================================================
#  SortIt — Gemini Classification Logic (classifier.py)
# ============================================================

import json
import os
from typing import Any, Dict

from google import genai
from google.genai import types

from exceptions import ClassificationParseError, GeminiAPIError


CONFIDENCE_THRESHOLD: int = 60

VALID_WASTE_TYPES: set[str] = {
    "plastic", "paper", "glass", "organic", "ewaste", "hazardous", "unknown"
}

_CLASSIFICATION_PROMPT: str = """
You are a waste classification assistant for Malaysia and Indonesia.

Look at this image and identify the waste item.

Reply ONLY in this exact JSON format (no extra text):
{
    "waste_type": "plastic" or "paper" or "glass" or "organic" or "ewaste" or "hazardous" or "unknown",
    "waste_name": "specific name of the item (e.g. Plastic Bottle, Newspaper)",
    "waste_detail": "more specific detail (e.g. Type 2 HDPE Plastic)",
    "confidence": a number from 0 to 100,
    "instructions": ["step 1", "step 2", "step 3"],
    "tip": "one helpful tip about this waste type"
}

If the image is not a waste item, set waste_type to "unknown".
""".strip()


def _get_genai_client() -> genai.Client:
    """Create a Gemini client using the API key from environment."""
    api_key: str | None = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiAPIError("GEMINI_API_KEY not set. Check .env configuration.")
    return genai.Client(api_key=api_key)


def _get_model_name() -> str:
    """Return GEMINI_MODEL from env, falling back to a sensible default."""
    return os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


def _clean_response_text(text: str) -> str:
    """Strip markdown fences (```json ... ```) if present."""
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        inner = parts[1] if len(parts) > 1 else text
        if inner.lstrip().startswith("json"):
            inner = inner.lstrip()[4:]
        return inner.strip()
    return text


def _validate_and_normalize(result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that the parsed result matches the expected schema."""
    required_keys: list[str] = ["waste_type", "waste_name", "confidence", "instructions"]
    for k in required_keys:
        if k not in result:
            raise ClassificationParseError(f"Missing required field: {k}")

    wt: str = str(result["waste_type"]).strip().lower()
    if wt not in VALID_WASTE_TYPES:
        wt = "unknown"
    result["waste_type"] = wt

    try:
        result["confidence"] = max(0, min(100, int(result["confidence"])))
    except (ValueError, TypeError):
        raise ClassificationParseError("Invalid 'confidence' value; must be a number 0-100.")

    if not isinstance(result["instructions"], list):
        raise ClassificationParseError("'instructions' must be a list of strings.")

    if "tip" not in result:
        result["tip"] = ""
    if "waste_detail" not in result:
        result["waste_detail"] = ""

    result["below_threshold"] = result["confidence"] < CONFIDENCE_THRESHOLD
    return result


def classify_waste(image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
    """
    Send image to Gemini and return structured classification dict.
    Raises: GeminiAPIError, ClassificationParseError
    """
    client: genai.Client = _get_genai_client()
    model_name: str = _get_model_name()

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                _CLASSIFICATION_PROMPT,
            ],
        )
        raw_text: str | None = getattr(response, "text", None)
        if not raw_text or not str(raw_text).strip():
            raise ClassificationParseError("Gemini returned an empty response.")
        cleaned: str = _clean_response_text(str(raw_text))
    except ClassificationParseError:
        raise
    except Exception as e:
        raise GeminiAPIError(f"Gemini API call failed: {e}") from e

    try:
        parsed: Dict[str, Any] = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as e:
        raise ClassificationParseError(f"Response was not valid JSON: {e}") from e

    return _validate_and_normalize(parsed)
