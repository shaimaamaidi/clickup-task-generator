"""Output port for reading ClickUp structures and members."""

from abc import ABC, abstractmethod
from typing import List
from src.domain.models.folder_model import Folder


class ClickUpReaderPort(ABC):
    """Output port to retrieve folders and members from ClickUp."""
    @abstractmethod
    def set_space_id(self, space_id: str) -> None:
        """Set the current ClickUp space identifier.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            None.
        """
        pass

    @abstractmethod
    def get_space_structure(self, space_id: str) -> List[Folder]:
        """Fetch the full space structure including folders and lists.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List of Folder instances for the space.
        """
        pass

    @abstractmethod
    def get_workspace_members(self) -> List[dict]:
        """Fetch workspace members for the current space.

        Returns:
            List of member dictionaries with id, username, and email.
        """
        pass