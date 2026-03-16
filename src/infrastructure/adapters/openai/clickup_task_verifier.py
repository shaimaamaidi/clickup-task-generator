import os
import json
from typing import List
from dotenv import load_dotenv
from openai import AzureOpenAI

from src.domain.models.task_model import Task
from src.domain.models.generated_task_model import GeneratedTask
from src.domain.models.verification_result_model import VerificationResult
from src.domain.models.verification_result_list_model import VerificationResultList
from src.domain.ports.output.llm_task_verification_port import TaskVerificationPort


class ClickUpTaskVerifier(TaskVerificationPort):
    SYSTEM_PROMPT = """
You are a project management assistant responsible for verifying tasks before they are created or updated in ClickUp.

You will receive:

1) A list of existing ClickUp tasks
Each task contains:
- id
- name
- description
- status
- priority
- assignee

2) A list of newly generated tasks extracted from a meeting summary.


------------------------------------------------
STEP 1 — Determine if the task already exists
------------------------------------------------

Compare each generated task against the existing tasks.

IMPORTANT:
You must compare tasks using ONLY the task_description.

Ignore:
- task_name
- status
- priority
- assignee

Task names can change between runs and must NOT be used for matching.

Two tasks are the SAME task if their descriptions describe the SAME technical feature or bug.

Examples of SAME task:

"Implement password reset using email verification" = "Develop password reset functionality using email verification"

"Fix incorrect calendar event display" = "Resolve issue where calendar shows incorrect event times"

"Integrate with WhatsApp messaging" = "Develop WhatsApp integration to manage messages"

If the technical goal and implementation are the same → it is the SAME task.


------------------------------------------------
STEP 2 — Decide the required action
------------------------------------------------

For each generated task:

If NO matching existing task is found:
→ action = "create"

If a matching existing task IS found:
→ compare the following fields:

- status
- priority
- assignee


Rules:

Status change → action = "update"

Priority change → action = "update"

Assignee change → action = "update"


------------------------------------------------
ASSIGNEE MERGE RULE (IMPORTANT)
------------------------------------------------

Assignees may contain multiple people separated by commas.

Example:
existing assignee: "X"
generated assignee: "Y,Z"

This means a NEW assignee was added.

In this case:
→ action = "update"
→ return the merged assignee list.

Example output:

task_assigne: "X,Y,Z"


Another example:

existing: "X,Y"
generated: "Y"

This is NOT a change because Y already exists.

Do NOT remove existing assignees unless explicitly requested.

Example output:

task_assigne: "X,Y"

------------------------------------------------
NO CHANGE RULE
------------------------------------------------

If the task already exists AND:

- status is the same
- priority is the same
- assignee contains no new names

→ DO NOT return this task at all.


------------------------------------------------
CRITICAL RULES
------------------------------------------------

- NEVER invent task_ids
- ONLY use ids from the existing tasks list
- NEVER create duplicate tasks
- NEVER return tasks where nothing changed
- ALWAYS return the existing task_id when action = "update"


------------------------------------------------
OUTPUT FORMAT
------------------------------------------------

Return JSON only.

{
  "results": [
    {
      "action": "create",
      "task_name": "Task title",
      "task_description": "Description",
      "task_status": "to do",
      "task_priority": "normal",
      "task_assigne": "X",
      "folder": "dev"
    },
    {
      "action": "update",
      "task_id": "existing_task_id",
      "task_name": "Task title",
      "task_description": "Description",
      "task_status": "in progress",
      "task_priority": "high",
      "task_assigne": "X,Y",
      "folder": "dev"
    }
  ]
}
    """

    def __init__(self):
        load_dotenv()
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    def verify(
        self,
        existing_tasks: List[Task],
        generated_tasks: List[GeneratedTask]
    ) -> List[VerificationResult]:
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

        user_message = f"""
Existing ClickUp tasks:
{existing_serialized}

Generated tasks:
{generated_serialized}

Apply the verification rules and return the result.
"""
        response = self.client.chat.completions.parse(
            model=self.deployment,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0,
            response_format=VerificationResultList
        )

        results = response.choices[0].message.parsed.results

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