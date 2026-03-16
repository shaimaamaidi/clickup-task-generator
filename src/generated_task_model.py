from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class GeneratedTask(BaseModel):
    task_name: str
    task_description: str
    task_assigne: str
    task_status: str
    task_priority: str
    folder: str