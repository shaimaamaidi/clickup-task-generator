from src.domain.exceptions.app_exception import AppException


class LLMResponseException(AppException):
    """Azure OpenAI call failed or response is not parseable."""
    def __init__(self, message: str = "Error while calling the LLM model.", http_status=502):
        super().__init__(message=message, code="LLM_RESPONSE_ERROR", http_status=http_status)
