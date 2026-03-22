import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import List

from src.domain.models.verification_result_model import VerificationResult


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/meeting", tags=["meeting"])


class ProcessMeetingRequest(BaseModel):
    space_id: str = Field(..., description="ClickUp space ID to sync tasks into")
    meeting_summary: str = Field(..., description="Meeting summary in Arabic or French")


class ProcessMeetingResponse(BaseModel):
    total: int
    created: int
    updated: int
    results: List[VerificationResult]


@router.post(
    "/process",
    response_model=ProcessMeetingResponse,
    summary="Process a meeting summary and sync ClickUp tasks",
)
def process_meeting(body: ProcessMeetingRequest, request: Request):
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
