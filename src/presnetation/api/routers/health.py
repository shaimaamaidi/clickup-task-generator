"""Health check endpoints."""

from fastapi import APIRouter


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Health check")
def health_check():
    """Return service health status.

    Returns:
        JSON payload with the service status.
    """
    return {"status": "ok"}