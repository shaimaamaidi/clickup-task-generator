"""Output port for applying task changes to ClickUp."""

from typing import List

from src.domain.models.folder_model import Folder
from src.domain.models.verification_result_model import VerificationResult


class ClickUpTaskWriterPort:
    """
    Output port: the domain asks ClickUp to create or update tasks.
    """

    def apply_results(self, results: List[VerificationResult], folders: List[Folder], members: List[dict], name_to_email: dict[str, str]) -> None:
        """Apply verification results to ClickUp.

        Args:
            results: Verification results describing actions to apply.
            folders: Space structure used to resolve folders and lists.
            members: Workspace members with ids and emails.
            name_to_email: Mapping of usernames to email addresses.

        Returns:
            None.
        """
        pass
