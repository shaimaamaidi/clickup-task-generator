"""Response DTOs for the meeting processing API."""

from pydantic import BaseModel, Field
from typing import List

from src.domain.models.verification_result_model import VerificationResult


class ProcessMeetingResponse(BaseModel):
    """Response payload for POST /meeting/process.

    Attributes:
        total: Total number of actions applied.
        created: Number of tasks created.
        updated: Number of tasks updated.
        results: Detailed list of applied actions.
    """

    total: int = Field(..., description="Total number of actions applied")
    created: int = Field(..., description="Number of tasks created")
    updated: int = Field(..., description="Number of tasks updated")
    results: List[VerificationResult] = Field(..., description="Detailed list of applied actions")