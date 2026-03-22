"""Unit tests for FastAPI exception handlers."""

import pytest
from starlette.requests import Request

from src.domain.exceptions.app_exception import AppException
from src.infrastructure.handlers.exception_handler import FastAPIExceptionHandler


@pytest.mark.asyncio
async def test_handle_app_exception_returns_json_response():
    """Return a JSON error payload for AppException errors."""
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
    }
    request = Request(scope)
    exc = AppException("Something went wrong", code="CLICKUP_API_ERROR", http_status=502)

    response = await FastAPIExceptionHandler.handle_app_exception(request, exc)

    assert response.status_code == 502
    assert response.body
