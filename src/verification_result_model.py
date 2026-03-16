from typing import Optional, Literal
from pydantic import BaseModel

class VerificationResult(BaseModel):
    action: Literal["create", "update"]
    task_name: str
    task_description: str
    task_assigne: str
    task_status: str
    task_priority: str
    folder: str
    task_id: Optional[str] = None  # Rempli seulement si action == "update"