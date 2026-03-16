from dataclasses import dataclass


@dataclass
class Task:
    id: str
    name: str
    description: str
    status: str
    assignee: str | None
    priority: str | None
