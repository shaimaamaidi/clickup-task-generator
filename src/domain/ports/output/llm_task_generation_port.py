from abc import ABC, abstractmethod
from typing import List, Dict
from src.domain.models.generated_task_model import GeneratedTask

class TaskGenerationPort(ABC):
    """Output port pour générer des tasks via LLM ou autre services externe"""

    @abstractmethod
    def generate_tasks(
        self,
        meeting_summary: str,
        folders_statuses: Dict[str, Dict[str, List[str]]]
    ) -> List[GeneratedTask]:
        pass