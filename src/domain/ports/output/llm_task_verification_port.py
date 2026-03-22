"""Output port for verifying generated tasks."""

from typing import List
from src.domain.models.task_model import Task
from src.domain.models.generated_task_model import GeneratedTask
from src.domain.models.verification_result_model import VerificationResult


class TaskVerificationPort:
    """
    Input port: the domain can request verification of generated tasks
    against existing tasks.
    """

    def verify_tasks(
        self,
        existing_tasks: List[Task],
        generated_tasks: List[GeneratedTask]
    ) -> List[VerificationResult]:
        """Compare existing tasks with generated tasks.

        Args:
            existing_tasks: Tasks already present in ClickUp.
            generated_tasks: Tasks produced by the LLM.

        Returns:
            Only the tasks that require creation or update.
        """
        raise NotImplementedError