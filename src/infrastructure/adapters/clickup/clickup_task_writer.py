from typing import List

from src.domain.models.folder_model import Folder
from src.domain.services.clickup_helper import priority_to_int, resolve_assignee_ids
from src.domain.models.verification_result_model import VerificationResult
from src.domain.ports.output.clickup_task_writer_port import ClickUpTaskWriterPort
from src.infrastructure.adapters.clickup.clickup_http_client import ClickUpHttpClient


class ClickUpTaskWriter(ClickUpTaskWriterPort):


    def __init__(self, http_client: ClickUpHttpClient):
        self._http = http_client

    def apply_results(self, results: List[VerificationResult], folders: List[Folder], members: List[dict], name_to_email: dict[str, str]) -> None:
        name_to_email = name_to_email
        email_to_id = {m["email"].lower(): m["id"] for m in members}

        folder_list_map = self._build_folder_list_map(folders)

        for result in results:
            if result.action == "create":
                list_id = folder_list_map.get(result.folder)
                if not list_id:
                    print(f"[SKIP] Folder '{result.folder}' not found in ClickUp.")
                    continue
                self._create_task(list_id, result, name_to_email, email_to_id)

            elif result.action == "update":
                if not result.task_id:
                    print(f"[SKIP] Update requested but no task_id for '{result.task_name}'.")
                    continue
                self._update_task(result, name_to_email, email_to_id)

    def _create_task(self, list_id: str, result: VerificationResult, name_to_email: dict[str, str], email_to_id: dict[str, int]) -> None:
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
            print(f"[CREATED] '{result.task_name}' in folder '{result.folder}'")
        else:
            print(f"[ERROR] Create failed for '{result.task_name}': {response.text}")

    def _update_task(self, result: VerificationResult, name_to_email: dict[str, str], email_to_id: dict[str, int]) -> None:
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
            print(f"[UPDATED] '{result.task_name}' (id: {result.task_id})")
        else:
            print(f"[ERROR] Update failed for '{result.task_name}': {response.text}")

    @staticmethod
    def _build_folder_list_map(folders) -> dict:
        mapping = {}
        for folder in folders:
            if folder.lists:
                mapping[folder.name] = folder.lists[0].id
        return mapping