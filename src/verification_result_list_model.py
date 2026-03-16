from typing import List
from pydantic import BaseModel
from src.verification_result_model import VerificationResult

class VerificationResultList(BaseModel):
    results: List[VerificationResult]