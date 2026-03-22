from src.domain.exceptions.app_exception import AppException


class ClickUpWorkspaceMembersException(AppException):
    """Workspace not found or no members returned."""
    def __init__(self, message: str = "Unable to retrieve workspace members.", http_status=404):
        super().__init__(message=message, code="CLICKUP_MEMBERS_ERROR", http_status=http_status)