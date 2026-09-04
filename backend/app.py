# ============================================================
#  SortIt — Flask Application Entrypoint (app.py)
# ============================================================

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from classifier import CONFIDENCE_THRESHOLD, classify_waste
from exceptions import (
    ClassificationParseError,
    GeminiAPIError,
    InvalidImageError,
    SortItError,
)
from logging_config import setup_logger
from storage_interface import StorageBackend

load_dotenv()
logger = setup_logger("sortit")

app = Flask(__name__)
CORS(app)


class LocalJsonStorage(StorageBackend):
    """File-backed storage implementation for audit corrections."""

    def __init__(self, filepath: str | None = None) -> None:
        if filepath is None:
            log_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(log_dir, exist_ok=True)
            self.filepath = os.path.join(log_dir, "corrections.json")
        else:
            self.filepath = filepath

    def save_correction(self, record: Dict[str, Any]) -> None:
        data: List[Dict[str, Any]] = self.get_corrections()
        data.append(record)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_corrections(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []


storage: StorageBackend = LocalJsonStorage()


@app.route("/", methods=["GET"])
def home() -> Tuple[Response, int]:
    """Health check endpoint."""
    return jsonify({
        "message": "SortIt Backend is running! ♻️",
        "version": "2.1",
        "confidence_threshold": CONFIDENCE_THRESHOLD,
    }), 200


@app.route("/analyze", methods=["POST"])
def analyze() -> Tuple[Response, int]:
    """Accept photo, classify using Gemini, return structured JSON."""
    try:
        if "image" not in request.files:
            raise InvalidImageError("No image file provided in request.")

        image_file = request.files["image"]
        if not image_file.filename:
            raise InvalidImageError("Empty image file provided.")

        image_bytes: bytes = image_file.read()
        if not image_bytes:
            raise InvalidImageError("Image file contains 0 bytes.")

        mime_type: str = image_file.content_type or "image/jpeg"
        logger.info(f"Analyzing waste image ({len(image_bytes)} bytes, {mime_type})")

        result: Dict[str, Any] = classify_waste(image_bytes, mime_type=mime_type)

        if result.get("below_threshold"):
            logger.warning(
                f"Low confidence ({result.get('confidence')}%) for {result.get('waste_name')}"
            )
        else:
            logger.info(
                f"Classified: {result.get('waste_name')} -> {result.get('waste_type')} ({result.get('confidence')}%)"
            )

        return jsonify(result), 200

    except SortItError as e:
        logger.error(f"Handled error [{e.__class__.__name__}]: {e.message}")
        return jsonify({
            "error_type": e.__class__.__name__,
            "message": e.message,
        }), e.status_code

    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        return jsonify({
            "error_type": "InternalServerError",
            "message": "An unexpected error occurred while processing the image.",
        }), 500


@app.route("/correct", methods=["POST"])
def correct() -> Tuple[Response, int]:
    """Log a user correction / override for auditing & quality feedback."""
    try:
        data: Dict[str, Any] | None = request.get_json()
        if not data:
            return jsonify({
                "error_type": "InvalidRequestError",
                "message": "Missing JSON body in correction request.",
            }), 400

        corrected_type: str = str(data.get("corrected_waste_type", "")).strip().lower()
        if not corrected_type:
            return jsonify({
                "error_type": "InvalidRequestError",
                "message": "Field 'corrected_waste_type' is required.",
            }), 400

        record: Dict[str, Any] = {
            "timestamp": data.get("timestamp") or datetime.utcnow().isoformat() + "Z",
            "original_result": data.get("original_result") or {},
            "corrected_waste_type": corrected_type,
            "note": str(data.get("note", "")).strip(),
        }

        storage.save_correction(record)
        logger.info(
            f"AUDIT CORRECTION: AI='{record['original_result'].get('waste_type')}' -> USER='{corrected_type}' | note: '{record['note']}'"
        )

        return jsonify({"status": "logged", "message": "Correction recorded for audit."}), 200

    except Exception as e:
        logger.exception(f"Error logging correction: {e}")
        return jsonify({
            "error_type": "InternalServerError",
            "message": "Could not record correction.",
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
