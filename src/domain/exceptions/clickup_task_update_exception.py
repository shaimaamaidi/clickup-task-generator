"""Exception for failures when updating ClickUp tasks."""

from src.domain.exceptions.app_exception import AppException


class ClickUpTaskUpdateException(AppException):
    """Failed to update a task in ClickUp."""
    def __init__(self, message: str = "Failed to update task.", http_status=502):
        super().__init__(message=message, code="CLICKUP_TASK_UPDATE_ERROR", http_status=http_status)