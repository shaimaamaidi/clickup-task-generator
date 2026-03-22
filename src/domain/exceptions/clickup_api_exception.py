from src.domain.exceptions.app_exception import AppException


class ClickUpApiException(AppException):
    """Generic ClickUp API error (4xx / 5xx)."""
    def __init__(self, message: str = "Unexpected ClickUp API error.", http_status=502):
        super().__init__(message=message, code="CLICKUP_API_ERROR", http_status=http_status)