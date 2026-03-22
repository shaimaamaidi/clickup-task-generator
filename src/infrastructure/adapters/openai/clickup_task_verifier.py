import json
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


class ClickUpTaskVerifier(TaskVerificationPort):

    def __init__(self, llm_client: AzureLLMClient, prompt_provider: PromptProviderPort):
        self._llm = llm_client
        self._prompt_provider = prompt_provider

    def verify(
        self,
        existing_tasks: List[Task],
        generated_tasks: List[GeneratedTask]
    ) -> List[VerificationResult]:

        if not generated_tasks:
            return []

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
            ChatCompletionUserMessageParam(role="user", content=self._prompt_provider.get_user_prompt("verification", existing_serialized=existing_serialized, generated_serialized=generated_serialized))
        ]
        results = self._llm.parse(messages, response_format=VerificationResultList).results

        if results is None:
            raise LLMResponseException(
                "The model returned an invalid verification response."
            )
        existing_map = {t.id: t for t in existing_tasks}
        filtered = []

        for result in results:
            if result.action == "update" and result.task_id:
                existing = existing_map.get(result.task_id)
                if existing:
                    status_changed = result.task_status != existing.status
                    priority_changed = result.task_priority != existing.priority

                    # Gérer les assignees multiples séparés par virgule
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
                        print(f"[SKIP] No real change for '{result.task_name}'")
                        continue
            filtered.append(result)

        return filtered