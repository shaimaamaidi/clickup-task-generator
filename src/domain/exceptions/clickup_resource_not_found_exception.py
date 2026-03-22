from src.domain.exceptions.app_exception import AppException


class ClickUpResourceNotFoundException(AppException):
    """Resource not found in ClickUp (404)."""
    def __init__(self, message: str = "ClickUp resource not found.", http_status=404):
        super().__init__(message=message, code="CLICKUP_NOT_FOUND", http_status=http_status)

