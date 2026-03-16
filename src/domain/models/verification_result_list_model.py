from typing import List
from pydantic import BaseModel
from src.domain.models.verification_result_model import VerificationResult

class VerificationResultList(BaseModel):
    results: List[VerificationResult]