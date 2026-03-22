"""FastAPI application factory and configuration."""

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.domain.exceptions.app_exception import AppException
from src.infrastructure.di.container import Container
from src.infrastructure.handlers.exception_handler import FastAPIExceptionHandler
from src.infrastructure.logging.logger_config import setup_logger
from src.presentation.api.routers import health, meeting


setup_logger()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance with routes and exception handlers.
    """
    app = FastAPI(
        title="ClickUp Meeting Processor",
        description="Processes meeting summaries and synchronizes tasks in ClickUp.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    container = Container()


    app.state.container = container

    app.add_exception_handler(AppException, FastAPIExceptionHandler.handle_app_exception)
    app.add_exception_handler(RequestValidationError, FastAPIExceptionHandler.handle_validation_exception)
    app.add_exception_handler(Exception, FastAPIExceptionHandler.handle_generic_exception)

    app.include_router(health.router)
    app.include_router(meeting.router)

    logger.info("ClickUp Meeting Processor started successfully.")

    return app

app = create_app()