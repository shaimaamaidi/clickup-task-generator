"""Exception for malformed .prompty templates."""

from src.domain.exceptions.app_exception import AppException


class PromptInvalidFormatException(AppException):
    """Malformed .prompty file (missing --- separators)."""
    def __init__(self, message: str = "Invalid .prompty file format.", http_status=500):
        super().__init__(message=message, code="PROMPT_INVALID_FORMAT", http_status=http_status)


