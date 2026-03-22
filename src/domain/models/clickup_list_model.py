"""Domain model for ClickUp lists."""

from dataclasses import dataclass, field
from typing import List

from src.domain.models.task_model import Task


@dataclass
class ClickUpList:
    """Represents a ClickUp list with tasks and metadata.

    Attributes:
        id: ClickUp list identifier.
        name: List name.
        tasks: Tasks contained in the list.
        statuses: Available statuses for the list.
        priorities: Available priorities for the list.
    """
    id: str
    name: str
    tasks: List[Task] = field(default_factory=list)
    statuses: List[str] = field(default_factory=list)
    priorities: List[str] = field(default_factory=list)
