"""Domain model for ClickUp folders."""

from dataclasses import dataclass, field
from typing import List

from src.domain.models.clickup_list_model import ClickUpList


@dataclass
class Folder:
    """Represents a ClickUp folder containing lists.

    Attributes:
        id: ClickUp folder identifier.
        name: Folder name.
        lists: Lists contained in the folder.
    """
    id: str
    name: str
    lists: List[ClickUpList] = field(default_factory=list)