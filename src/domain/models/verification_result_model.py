"""Domain model for task verification outcomes."""

from typing import Optional, Literal
from pydantic import BaseModel


class VerificationResult(BaseModel):
    """Represents a create/update action decided by verification.

    Attributes:
        action: Action type, either "create" or "update".
        task_name: Task name/title.
        task_description: Task description.
        task_assigne: Assignee name(s).
        task_status: Task status.
        task_priority: Task priority.
        folder: Folder name.
        task_id: Existing task ID when action is "update".
    """
    action: Literal["create", "update"]
    task_name: str
    task_description: str
    task_assigne: str
    task_status: str
    task_priority: str
    folder: str
    task_id: Optional[str] = None  # Only set when action == "update"