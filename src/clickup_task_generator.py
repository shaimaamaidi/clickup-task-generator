import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from openai import AzureOpenAI

from src.generated_task_model import GeneratedTask
from src.response_generator_model import TaskList


class ClickUpTaskGenerator:
    """
    Génère des tâches ClickUp à partir d'un résumé de réunion
    en utilisant Azure OpenAI.
    """

    SYSTEM_PROMPT = """
You are an assistant specialized in project management and meeting analysis.

Your task is to extract actionable software development tasks from a meeting summary
and convert them into structured ClickUp tasks.

The meeting summary may contain information about:
- new tasks
- updates to existing tasks
- completed tasks
- discussions
- organizational decisions

You must extract ONLY concrete technical tasks.

Return the CANONICAL representation of each task, not the management action.

For example:
If the meeting says “change tracker settings status to in progress”
you must return the original task with updated status,
NOT a task named “Update tracker settings status”.

------------------------------------------------
FIELD RULES
------------------------------------------------

### task_name

- Must be concise and written in English.
- Must describe a concrete technical action that produces a deliverable.
- Prefer verbs such as:
  Implement, Integrate, Configure, Add, Fix, Create, Develop.

- Do NOT use managerial or meta verbs such as:
  Prioritize, Discuss, Plan, Consider, Evaluate, Organize.

- The task name must describe WHAT will be built or fixed,
  not the process of managing the task.

Examples:

Correct:
Implement in-app notifications system
Fix incorrect calendar event display
Integrate with WhatsApp

Incorrect:
Prioritize tracker settings
Discuss UI improvements
Update tracker settings task status

------------------------------------------------

### task_description

- Must be precise, technical, and actionable.
- Clearly describe what must be implemented or fixed.
- Include technical context if available.

Avoid vague descriptions such as:
“Improve system”
“Handle notifications”

Examples:

Good:
Implement password reset using an email verification link and add two-step confirmation.

Bad:
Work on security improvements.

If the task is already in progress,
describe the FULL functionality of the task,
not just the remaining work.

Never start the description with:
"Continue", "Finish", or "Update".

------------------------------------------------

### task_assigne

- Copy the name EXACTLY as written in the meeting summary.
- If multiple people are assigned → separate with commas.
- If a new person joins an existing task → include ALL assignees.
- If no person is mentioned → write "غير محدد".

Examples:

<name_1>
<name_1>,<name_2>

------------------------------------------------

### task_status

Use ONLY statuses available for the chosen folder.

Rules:
- If the meeting states the task is finished → "complete"
- If work has started → "in progress"
- Otherwise → "to do"

------------------------------------------------

### task_priority

Use ONLY priorities available for the chosen folder.

Rules:

urgent:
- bugs affecting users
- critical system failures
- immediate deadlines

high:
- security features
- authentication
- important platform capabilities

normal:
- default for all other tasks

------------------------------------------------

### folder

You will receive a list of available folders.

IMPORTANT:
- Use ONLY the provided folder names.
- NEVER invent new folder names.
- Choose the most appropriate folder for the task.

------------------------------------------------

TASK EXTRACTION RULES
------------------------------------------------

The meeting summary may describe THREE situations:

1. New task
2. Update to an existing task
3. Completed task

You must ALWAYS return the canonical task.

Examples:

Meeting text:
"Change tracker settings task status to in progress."

Correct output:
task_name: Implement keyword and phrase tracking settings
task_status: in progress

Incorrect output:
task_name: Update tracker settings status


Meeting text:
"Add X to WhatsApp integration."

Correct output:
task_name: Integrate with WhatsApp
task_assigne: X

Incorrect output:
task_name: Integrate WhatsApp testing


Meeting text:
"Increase priority of custom tab task."

Correct output:
task_name: Add custom tab feature
task_priority: high

Incorrect output:
task_name: Prioritize custom tab feature

------------------------------------------------

WHAT NOT TO EXTRACT
------------------------------------------------

Do NOT create tasks for:

Meta work:
- create timeline
- organize next steps
- plan tasks
- schedule meeting

Organizational decisions:
- organize workspace in Teams
- restructure team channels
- divide work by departments

Testing assistance:
If someone helps test or review an existing task,
add them as assignee instead of creating a new task.

Example:

Meeting text:
"X will help test WhatsApp integration"

Correct:
task_name: Integrate with WhatsApp
task_assigne: X

Incorrect:
task_name: Test WhatsApp integration

------------------------------------------------

TASK GRANULARITY
------------------------------------------------

Each task must represent ONE technical deliverable.

If the meeting mentions multiple independent systems,
create separate tasks.

Example:

Meeting text:
"Integrate WhatsApp and Facebook"

Correct:
Integrate with WhatsApp
Integrate with Facebook

------------------------------------------------

OUTPUT FORMAT

Return JSON only.

{
  "tasks": [
    {
      "task_name": "Task title",
      "task_description": "Detailed explanation",
      "task_assigne": "اسم الشخص",
      "task_status": "to do",
      "task_priority": "normal",
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

    def create_tasks(
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

        user_message = f"""
Below is the meeting summary.

{meeting_summary}

Available folders and their statuses:

{folders_text}

Extract all actionable tasks from the meeting summary.
"""

        response = self.client.chat.completions.parse(
            model=self.deployment,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0,
            response_format=TaskList
        )

        return response.choices[0].message.parsed.tasks