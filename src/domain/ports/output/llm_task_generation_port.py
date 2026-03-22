"""Output port for task generation via LLMs."""

from abc import ABC, abstractmethod
from typing import List, Dict
from src.domain.models.generated_task_model import GeneratedTask


class TaskGenerationPort(ABC):
    """Output port to generate tasks via an LLM or other external services."""

    @abstractmethod
    def generate_tasks(
        self,
        meeting_summary: str,
        folders_statuses: Dict[str, Dict[str, List[str]]]
    ) -> List[GeneratedTask]:
        """Generate tasks from a meeting summary.

        Args:
            meeting_summary: Meeting summary in Arabic or French.
            folders_statuses: Mapping of folder names to statuses and priorities.

        Returns:
            List of GeneratedTask instances.
        """
        pass