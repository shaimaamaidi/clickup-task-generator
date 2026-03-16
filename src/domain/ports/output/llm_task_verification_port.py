from typing import List
from src.domain.models.task_model import Task
from src.domain.models.generated_task_model import GeneratedTask
from src.domain.models.verification_result_model import VerificationResult

class TaskVerificationPort:
    """
    Input port : le domaine peut demander la vérification de tâches générées
    par rapport aux tâches existantes.
    """

    def verify_tasks(
        self,
        existing_tasks: List[Task],
        generated_tasks: List[GeneratedTask]
    ) -> List[VerificationResult]:
        """
        Compare les tâches existantes avec les tâches générées et retourne
        uniquement celles nécessitant une création ou une mise à jour.
        """
        raise NotImplementedError