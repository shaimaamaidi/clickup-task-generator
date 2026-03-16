import json
from typing import List, Dict

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from src.domain.models.generated_task_model import GeneratedTask
from src.domain.models.response_generator_model import TaskList
from src.domain.ports.output.llm_task_generation_port import TaskGenerationPort
from src.domain.ports.output.prompt_provider_port import PromptProviderPort
from src.infrastructure.adapters.openai.AzureLLMClient import AzureLLMClient


class ClickUpTaskGenerator(TaskGenerationPort):
    """
    Génère des tâches ClickUp à partir d'un résumé de réunion
    en utilisant Azure OpenAI.
    """

    def __init__(self, llm_client: AzureLLMClient, prompt_provider: PromptProviderPort):
        self._llm = llm_client
        self._prompt_provider = prompt_provider

    def generate_tasks(
        self,
        meeting_summary: str,
        folders_statuses: Dict[str, Dict[str, List[str]]]
    ) -> List[GeneratedTask]:
        """
        Génère des tasks à partir d'un résumé de réunion.

        Args:
            meeting_summary: résumé de réunion en arabe
            folders_statuses: {
                "bug": {"statuses": ["todo","in progress","done"], "priorities": ["low","medium","high"]},
                "development": {"statuses": ["todo","in progress","done"], "priorities": ["low","medium","high"]}
            }

        Returns:
            Liste de GeneratedTask
        """

        # On convertit le dictionnaire en texte JSON pour fournir au LLM
        folders_text = json.dumps(folders_statuses, ensure_ascii=False, indent=2)


        messages = [
            ChatCompletionSystemMessageParam(role="system", content=self._prompt_provider.get_system_prompt("generation")),
            ChatCompletionUserMessageParam(role="user", content=self._prompt_provider.get_user_prompt("generation", meeting_summary=meeting_summary, folders_text=folders_text))
        ]
        return self._llm.parse(messages, response_format=TaskList).tasks
