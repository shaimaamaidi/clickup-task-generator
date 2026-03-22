"""Exception for missing prompt templates."""

from src.domain.exceptions.app_exception import AppException


class PromptTemplateNotFoundException(AppException):
    """.prompty file not found."""
    def __init__(self, message: str = "Prompt template not found.", http_status=500):
        super().__init__(message=message, code="PROMPT_NOT_FOUND", http_status=http_status)
