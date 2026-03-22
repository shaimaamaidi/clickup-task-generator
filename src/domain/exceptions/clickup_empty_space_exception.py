from src.domain.exceptions.app_exception import AppException


class ClickUpEmptySpaceException(AppException):
    """Space without folders (valid space_id but empty)."""
    def __init__(self, message: str = "No folder found in the ClickUp space.", http_status=404):
        super().__init__(message=message, code="CLICKUP_EMPTY_SPACE", http_status=http_status)
