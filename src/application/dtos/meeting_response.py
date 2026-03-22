from pydantic import BaseModel, Field
from typing import List

from src.domain.models.verification_result_model import VerificationResult


class ProcessMeetingResponse(BaseModel):
    """Response DTO for POST /meeting/process."""

    total: int = Field(..., description="Total number of actions applied")
    created: int = Field(..., description="Number of tasks created")
    updated: int = Field(..., description="Number of tasks updated")
    results: List[VerificationResult] = Field(..., description="Detailed list of applied actions")