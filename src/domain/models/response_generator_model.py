from typing import List

from pydantic import BaseModel

from src.domain.models.generated_task_model import GeneratedTask


class TaskList(BaseModel):
    tasks: List[GeneratedTask]