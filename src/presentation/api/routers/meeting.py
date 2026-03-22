"""Meeting processing endpoints."""

import logging

from fastapi import APIRouter, Request

from src.application.dtos.meeting_request import ProcessMeetingRequest
from src.application.dtos.meeting_response import ProcessMeetingResponse


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/meeting", tags=["meeting"])


@router.post(
    "/process",
    response_model=ProcessMeetingResponse,
    summary="Process a meeting summary and sync ClickUp tasks",
)
def process_meeting(body: ProcessMeetingRequest, request: Request):
    """Process a meeting summary and synchronize tasks in ClickUp.

    Args:
        body: Request payload with space ID and meeting summary.
        request: FastAPI request object with application state.

    Returns:
        ProcessMeetingResponse with action counts and details.

    Raises:
        Exception: Propagated domain errors from the use case.
    """
    logger.info(
        "POST /meeting/process — space_id='%s'.",
        body.space_id,
    )

    use_case = request.app.state.container.get_process_meeting_use_case()
    results = use_case.process_meeting(
        space_id=body.space_id,
        meeting_summary=body.meeting_summary,
    )
    response = ProcessMeetingResponse(
        total=len(results),
        created=sum(1 for r in results if r.action == "create"),
        updated=sum(1 for r in results if r.action == "update"),
        results=results,
    )

    logger.info(
        "POST /meeting/process completed — total=%d, created=%d, updated=%d.",
        response.total,
        response.created,
        response.updated,
    )

    return response
