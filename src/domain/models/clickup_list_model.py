from dataclasses import dataclass, field
from typing import List

from src.task_model import Task


@dataclass
class ClickUpList:
    id: str
    name: str
    tasks: List[Task] = field(default_factory=list)
    statuses: List[str] = field(default_factory=list)
    priorities: List[str] = field(default_factory=list)
