from src.domain.exceptions.app_exception import AppException


class ExcelReadException(AppException):
    """Generic error while reading the Excel file."""
    def __init__(self, message: str = "Unable to read the Excel file.", http_status=500):
        super().__init__(message=message, code="EXCEL_READ_ERROR", http_status=http_status)