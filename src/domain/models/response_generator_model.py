"""LLM response wrapper models."""

from typing import List

from pydantic import BaseModel

from src.domain.models.generated_task_model import GeneratedTask


class TaskList(BaseModel):
    """Container for a list of generated tasks.

    Attributes:
        tasks: Generated tasks returned by the LLM.
    """
    tasks: List[GeneratedTask]