"""Exception for missing or invalid LLM configuration."""

from src.domain.exceptions.app_exception import AppException


class LLMConfigurationException(AppException):
    """Missing Azure OpenAI environment variables."""
    def __init__(self, message: str = "Incomplete Azure OpenAI configuration.", http_status=500):
        super().__init__(message=message, code="LLM_CONFIGURATION_ERROR", http_status=http_status)
