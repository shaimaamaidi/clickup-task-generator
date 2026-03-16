from dataclasses import dataclass, field
from typing import List

from src.clickup_list_model import ClickUpList


@dataclass
class Folder:
    id: str
    name: str
    lists: List[ClickUpList] = field(default_factory=list)