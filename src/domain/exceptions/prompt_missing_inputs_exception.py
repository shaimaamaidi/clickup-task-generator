"""Exception for missing prompt template variables."""

from src.domain.exceptions.app_exception import AppException


class PromptMissingInputsException(AppException):
    """Template-required variables missing at call time."""
    def __init__(self, message: str = "Missing required template variables.", http_status=500):
        super().__init__(message=message, code="PROMPT_MISSING_INPUTS", http_status=http_status)