from src.domain.exceptions.app_exception import AppException


class ClickUpAuthenticationException(AppException):
    """Missing or invalid API token (401)."""
    def __init__(self, message: str = "Missing or invalid ClickUp token.", http_status=401):
        super().__init__(message=message, code="CLICKUP_AUTH_ERROR", http_status=http_status)

