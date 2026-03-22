from src.domain.exceptions.app_exception import AppException


class ExcelFileNotFoundException(AppException):
    """Excel file not found at the configured path."""
    def __init__(self, message: str = "Excel file not found.", http_status=500):
        super().__init__(message=message, code="EXCEL_FILE_NOT_FOUND", http_status=http_status)
