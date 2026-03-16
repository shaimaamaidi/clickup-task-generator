from typing import List

from src.domain.models.folder_model import Folder
from src.domain.models.verification_result_model import VerificationResult

class ClickUpTaskWriterPort:
    """
    Output port : le domaine demande à ClickUp de créer ou mettre à jour des tâches.
    """

    def apply_results(self, results: List[VerificationResult], folders: List[Folder], members: List[dict], name_to_email: dict[str, str]) -> None:
        pass
