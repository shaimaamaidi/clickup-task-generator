from abc import ABC, abstractmethod
from typing import List
from src.domain.models.folder_model import Folder

class ClickUpReaderPort(ABC):

    """Output port : abstraction pour récupérer folders et members depuis ClickUp"""
    @abstractmethod
    def set_space_id(self, space_id: str) -> None:
        pass

    @abstractmethod
    def get_space_structure(self, space_id: str) -> List[Folder]:
        pass

    @abstractmethod
    def get_workspace_members(self) -> List[dict]:
        pass