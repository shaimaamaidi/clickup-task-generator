import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.exceptions.app_exception import AppException

logger = logging.getLogger(__name__)

_CONFIG_CODES = {
    "CLICKUP_AUTH_ERROR",
    "LLM_CONFIGURATION_ERROR",
    "PROMPT_NOT_FOUND",
    "PROMPT_INVALID_FORMAT",
    "EXCEL_FILE_NOT_FOUND",
    "EXCEL_MISSING_COLUMNS",
}

_RUNTIME_CODES = {
    "CLICKUP_NOT_FOUND",
    "CLICKUP_API_ERROR",
    "CLICKUP_EMPTY_SPACE",
    "CLICKUP_MEMBERS_ERROR",
    "CLICKUP_TASK_CREATE_ERROR",
    "CLICKUP_TASK_UPDATE_ERROR",
    "EXCEL_READ_ERROR",
    "LLM_RESPONSE_ERROR",
    "PROMPT_MISSING_INPUTS",
}


class FastAPIExceptionHandler:
    """Centralized exception handling for FastAPI."""

    @staticmethod
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        """Handle :class:`AppException` errors.

        :param request: Incoming FastAPI request.
        :param exc: Application exception instance.
        :return: JSON error response.
        """
        if exc.code in _CONFIG_CODES:
            logger.error(
                "Configuration/Infrastructure Error [%s]: %s",
                exc.code,
                exc.message,
                exc_info=exc,
            )
        elif exc.code in _RUNTIME_CODES:
            logger.warning(
                "Runtime Error [%s]: %s",
                exc.code,
                exc.message,
            )
        else:
            logger.error(
                "Unknown Application Error [%s]: %s",
                exc.code,
                exc.message,
                exc_info=exc,
            )

        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    @staticmethod
    async def handle_validation_exception(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle FastAPI request validation errors.

        :param request: Incoming FastAPI request.
        :param exc: Validation exception instance.
        :return: JSON error response.
        """
        logger.info(
            "Validation Error on request %s: %s",
            request.url.path,
            exc.errors(),
        )

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                }
            },
        )

    @staticmethod
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions.

        :param request: Incoming FastAPI request.
        :param exc: Unhandled exception instance.
        :return: JSON error response.
        """
        logger.error(
            "Unhandled exception on request %s: %s",
            request.url.path,
            str(exc),
            exc_info=exc,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc),
                }
            },
        )