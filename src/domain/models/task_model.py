"""Domain model for existing ClickUp tasks."""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents an existing task in ClickUp.

    Attributes:
        id: Task identifier.
        name: Task name/title.
        description: Task description.
        status: Current task status.
        assignee: Assignee username or None.
        priority: Priority label or None.
    """
    id: str
    name: str
    description: str
    status: str
    assignee: str | None
    priority: str | None
