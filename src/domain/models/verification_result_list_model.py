"""Models for verification result collections."""

from typing import List
from pydantic import BaseModel
from src.domain.models.verification_result_model import VerificationResult


class VerificationResultList(BaseModel):
    """Container for verification results returned by the LLM.

    Attributes:
        results: List of verification results.
    """
    results: List[VerificationResult]