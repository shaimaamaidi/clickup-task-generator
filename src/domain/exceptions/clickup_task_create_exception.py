"""Exception for failures when creating ClickUp tasks."""

from src.domain.exceptions.app_exception import AppException


class ClickUpTaskCreateException(AppException):
    """Failed to create a task in ClickUp."""
    def __init__(self, message: str = "Failed to create task.", http_status=502):
        super().__init__(message=message, code="CLICKUP_TASK_CREATE_ERROR", http_status=http_status)
