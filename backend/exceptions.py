# ============================================================
#  SortIt — Custom Exception Hierarchy (exceptions.py)
# ============================================================

class SortItError(Exception):
    """Base exception for all SortIt application errors."""
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GeminiAPIError(SortItError):
    """Raised when the Gemini API call fails (network, quota, auth)."""
    def __init__(self, message: str = "Gemini API request failed.") -> None:
        super().__init__(message, status_code=502)


class InvalidImageError(SortItError):
    """Raised when the uploaded image is missing, corrupt, or empty."""
    def __init__(self, message: str = "Invalid or missing image file.") -> None:
        super().__init__(message, status_code=400)


class ClassificationParseError(SortItError):
    """Raised when Gemini response cannot be parsed as valid JSON or doesn't match schema."""
    def __init__(self, message: str = "Failed to parse classification response from AI.") -> None:
        super().__init__(message, status_code=500)
