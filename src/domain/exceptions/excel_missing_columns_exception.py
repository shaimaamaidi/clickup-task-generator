from src.domain.exceptions.app_exception import AppException


class ExcelMissingColumnsException(AppException):
    """USERNAME or MAIL columns are missing from the Excel file."""
    def __init__(self, message: str = "Missing USERNAME or MAIL columns.", http_status=500):
        super().__init__(message=message, code="EXCEL_MISSING_COLUMNS", http_status=http_status)

