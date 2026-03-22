"""ClickUp task writer adapter for applying create/update actions."""

import logging
from typing import List

from src.domain.exceptions.clickup_task_create_exception import ClickUpTaskCreateException
from src.domain.exceptions.clickup_task_update_exception import ClickUpTaskUpdateException
from src.domain.models.folder_model import Folder
from src.domain.services.clickup_helper import priority_to_int, resolve_assignee_ids
from src.domain.models.verification_result_model import VerificationResult
from src.domain.ports.output.clickup_task_writer_port import ClickUpTaskWriterPort
from src.infrastructure.adapters.clickup.clickup_http_client import ClickUpHttpClient


logger = logging.getLogger(__name__)


class ClickUpTaskWriter(ClickUpTaskWriterPort):
    """Adapter that applies task changes to ClickUp."""

    def __init__(self, http_client: ClickUpHttpClient):
        """Initialize the writer with an HTTP client.

        Args:
            http_client: ClickUp HTTP client instance.
        """
        self._http = http_client

    def apply_results(self, results: List[VerificationResult], folders: List[Folder], members: List[dict], name_to_email: dict[str, str]) -> None:
        """Apply verification results to ClickUp.

        Args:
            results: Verification results to apply.
            folders: Folder structure for resolving list IDs.
            members: Workspace members for assignee resolution.
            name_to_email: Mapping of usernames to emails.

        Returns:
            None.
        """
        name_to_email = name_to_email
        email_to_id = {m["email"].lower(): m["id"] for m in members}

        folder_list_map = self._build_folder_list_map(folders)

        logger.info(
            "Applying %d result(s) to ClickUp...",
            len(results),
        )

        for result in results:
            if result.action == "create":
                list_id = folder_list_map.get(result.folder)
                if not list_id:
                    logger.warning(
                        "Folder '%s' not found in ClickUp — skipping task '%s'.",
                        result.folder,
                        result.task_name,
                    )
                    continue
                self._create_task(list_id, result, name_to_email, email_to_id)

            elif result.action == "update":
                if not result.task_id:
                    logger.warning(
                        "Update requested but no task_id provided for '%s' — skipping.",
                        result.task_name,
                    )
                    continue
                self._update_task(result, name_to_email, email_to_id)

    def _create_task(self, list_id: str, result: VerificationResult, name_to_email: dict[str, str], email_to_id: dict[str, int]) -> None:
        """Create a task in ClickUp.

        Args:
            list_id: ClickUp list identifier.
            result: Verification result describing the task.
            name_to_email: Mapping of usernames to emails.
            email_to_id: Mapping of email to ClickUp member ID.

        Raises:
            ClickUpTaskCreateException: If the API request fails.
        """
        endpoint = f"/list/{list_id}/task"

        payload = {
            "name": result.task_name,
            "description": result.task_description,
            "status": result.task_status,
            "priority": priority_to_int(result.task_priority),
        }

        assignee_names = [a.strip() for a in result.task_assigne.split(",")]
        assignee_ids = resolve_assignee_ids(name_to_email, email_to_id, assignee_names)
        if assignee_ids:
            payload["assignees"] = assignee_ids

        response = self._http.post_raw(endpoint, payload)

        if response.status_code == 200:
            logger.info(
                "Task created: '%s' in folder '%s'.",
                result.task_name,
                result.folder,
            )
        else:
            raise ClickUpTaskCreateException(
                f"Failed to create '{result.task_name}' "
                f"(status {response.status_code}) — {response.text}"
            )

    def _update_task(self, result: VerificationResult, name_to_email: dict[str, str], email_to_id: dict[str, int]) -> None:
        """Update an existing task in ClickUp.

        Args:
            result: Verification result describing updates.
            name_to_email: Mapping of usernames to emails.
            email_to_id: Mapping of email to ClickUp member ID.

        Raises:
            ClickUpTaskUpdateException: If the API request fails.
        """
        endpoint = f"/task/{result.task_id}"

        payload = {
            "status": result.task_status,
            "priority": priority_to_int(result.task_priority),
        }

        assignee_names = [a.strip() for a in result.task_assigne.split(",")]
        assignee_ids = resolve_assignee_ids(name_to_email, email_to_id, assignee_names)
        if assignee_ids:
            payload["assignees"] = {"add": assignee_ids}

        response = self._http.put_raw(endpoint, payload)

        if response.status_code == 200:
            logger.info(
                "Task updated: '%s' (id='%s').",
                result.task_name,
                result.task_id,
            )
        else:
            raise ClickUpTaskUpdateException(
                f"Failed to update '{result.task_name}' id='{result.task_id}' "
                f"(status {response.status_code}) — {response.text}"
            )

    @staticmethod
    def _build_folder_list_map(folders) -> dict:
        """Build a mapping of folder name to list ID.

        Args:
            folders: Folder objects with lists.

        Returns:
            Mapping of folder name to first list ID.
        """
        mapping = {}
        for folder in folders:
            if folder.lists:
                mapping[folder.name] = folder.lists[0].id
        return mapping