"""LLM adapter for generating ClickUp tasks."""

import json
import logging
from typing import List, Dict

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from src.domain.exceptions.llm_response_exception import LLMResponseException
from src.domain.models.generated_task_model import GeneratedTask
from src.domain.models.response_generator_model import TaskList
from src.domain.ports.output.llm_task_generation_port import TaskGenerationPort
from src.domain.ports.output.prompt_provider_port import PromptProviderPort
from src.infrastructure.adapters.openai.AzureLLMClient import AzureLLMClient


logger = logging.getLogger(__name__)


class ClickUpTaskGenerator(TaskGenerationPort):
    """
    Generate ClickUp tasks from a meeting summary
    using Azure OpenAI.
    """

    def __init__(self, llm_client: AzureLLMClient, prompt_provider: PromptProviderPort):
        """Initialize the generator.

        Args:
            llm_client: Azure OpenAI client wrapper.
            prompt_provider: Prompt provider for system/user prompts.
        """
        self._llm = llm_client
        self._prompt_provider = prompt_provider

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

        Raises:
            LLMResponseException: If the LLM response is malformed.
        """
        logger.info("Starting task generation from meeting summary...")

        # Convert the dictionary to JSON text to provide to the LLM
        folders_text = json.dumps(folders_statuses, ensure_ascii=False, indent=2)


        messages = [
            ChatCompletionSystemMessageParam(role="system", content=self._prompt_provider.get_system_prompt("generation")),
            ChatCompletionUserMessageParam(role="user", content=self._prompt_provider.get_user_prompt("generation", meeting_summary=meeting_summary, folders_text=folders_text))
        ]
        result = self._llm.parse(messages, response_format=TaskList)

        if result.tasks is None:
            raise LLMResponseException(
                "The model returned a malformed response — 'tasks' field is null."
            )

        if not result.tasks:
            logger.warning("No tasks extracted from meeting summary.")
            return []

        logger.info("%d task(s) generated from meeting summary.", len(result.tasks))

        return result.task
