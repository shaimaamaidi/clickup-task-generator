"""LLM adapter for verifying generated ClickUp tasks."""

import json
import logging
from typing import List

from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam

from src.domain.exceptions.llm_response_exception import LLMResponseException
from src.domain.models.task_model import Task
from src.domain.models.generated_task_model import GeneratedTask
from src.domain.models.verification_result_model import VerificationResult
from src.domain.models.verification_result_list_model import VerificationResultList
from src.domain.ports.output.llm_task_verification_port import TaskVerificationPort
from src.domain.ports.output.prompt_provider_port import PromptProviderPort
from src.infrastructure.adapters.openai.AzureLLMClient import AzureLLMClient


logger = logging.getLogger(__name__)


class ClickUpTaskVerifier(TaskVerificationPort):
    """Adapter that verifies generated tasks against existing tasks."""

    def __init__(self, llm_client: AzureLLMClient, prompt_provider: PromptProviderPort):
        """Initialize the verifier.

        Args:
            llm_client: Azure OpenAI client wrapper.
            prompt_provider: Prompt provider for system/user prompts.
        """
        self._llm = llm_client
        self._prompt_provider = prompt_provider

    def verify_tasks(
        self,
        existing_tasks: List[Task],
        generated_tasks: List[GeneratedTask]
    ) -> List[VerificationResult]:
        """Verify generated tasks against existing tasks.

        Args:
            existing_tasks: Tasks already present in ClickUp.
            generated_tasks: Tasks produced by the LLM.

        Returns:
            Filtered verification results describing create/update actions.

        Raises:
            LLMResponseException: If the LLM response is invalid.
        """

        if not generated_tasks:
            logger.warning("No generated tasks to verify — skipping verification.")
            return []

        logger.info(
            "Starting verification: %d generated task(s) against %d existing task(s).",
            len(generated_tasks),
            len(existing_tasks),
        )

        existing_serialized = json.dumps(
            [{"id": t.id, "name": t.name, "description": t.description,
              "status": t.status, "priority": t.priority, "assignee": t.assignee}
             for t in existing_tasks],
            ensure_ascii=False, indent=2
        )

        generated_serialized = json.dumps(
            [{"task_name": t.task_name, "task_description": t.task_description,
              "task_status": t.task_status, "task_priority": t.task_priority,
              "task_assigne": t.task_assigne, "folder": t.folder}
             for t in generated_tasks],
            ensure_ascii=False, indent=2
        )

        messages = [
            ChatCompletionSystemMessageParam(role="system", content=self._prompt_provider.get_system_prompt("verification")),
            ChatCompletionUserMessageParam(role="user", content=self._prompt_provider.get_user_prompt("verification", existing_tasks=existing_serialized, generated_tasks=generated_serialized))
        ]
        results = self._llm.parse(messages, response_format=VerificationResultList).results

        if results is None:
            raise LLMResponseException(
                "The model returned an invalid verification response."
            )

        logger.info(
            "Verification response received: %d result(s) from LLM.",
            len(results),
        )

        existing_map = {t.id: t for t in existing_tasks}
        filtered = []

        for result in results:
            if result.action == "update" and result.task_id:
                existing = existing_map.get(result.task_id)
                if existing:
                    status_changed = result.task_status != existing.status
                    priority_changed = result.task_priority != existing.priority

                    # Handle multiple assignees separated by commas
                    new_assignees = {
                        a.strip() for a in result.task_assigne.split(",")
                        if a.strip() and a.strip() != "غير محدد"
                    }
                    existing_assignee = existing.assignee or ""
                    existing_assignees = {
                        a.strip() for a in existing_assignee.split(",")
                        if a.strip()
                    }
                    assignee_changed = bool(new_assignees - existing_assignees)

                    if not any([status_changed, priority_changed, assignee_changed]):
                        logger.warning(
                            "No real change detected for task '%s' (id='%s') — skipping.",
                            result.task_name,
                            result.task_id,
                        )
                        continue

            filtered.append(result)

        logger.info(
            "Verification complete: %d action(s) to apply (%d create, %d update).",
            len(filtered),
            sum(1 for r in filtered if r.action == "create"),
            sum(1 for r in filtered if r.action == "update"),
        )
        return filtered