import os

import requests
from difflib import SequenceMatcher
from typing import List, Optional

from dotenv import load_dotenv

from src.verification_result_model import VerificationResult


class ClickUpTaskManager:

    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(self, members: List[dict], name_to_email: dict):
        load_dotenv()
        api_token = os.getenv("CLICKUP_API_TOKEN")
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        self.name_to_email = name_to_email
        self.email_to_id = {m["email"].lower(): m["id"] for m in members}

    def apply_results(self, results: List[VerificationResult], folders) -> None:
        folder_list_map = ClickUpTaskManager._build_folder_list_map(folders)

        for result in results:
            if result.action == "create":
                list_id = folder_list_map.get(result.folder)
                if not list_id:
                    print(f"[SKIP] Folder '{result.folder}' not found in ClickUp.")
                    continue
                self._create_task(list_id, result)

            elif result.action == "update":
                if not result.task_id:
                    print(f"[SKIP] Update requested but no task_id for '{result.task_name}'.")
                    continue
                self._update_task(result)

    def _resolve_assignee_ids(self, assignee_names: List[str]) -> List[int]:
        """
        Prend une liste de noms (arabes ou autres) et retourne
        la liste des user IDs correspondants via matching par email/username.
        """
        resolved = []
        for name in assignee_names:
            if not name or name == "غير محدد":
                continue
            member_id = self._find_member_id(name)
            if member_id:
                resolved.append(member_id)
            else:
                print(f"[WARN] Member '{name}' not found in workspace.")
        return resolved

    def _find_member_id(self, name: str) -> Optional[int]:
        """
        1. Cherche l'email dans le dictionnaire Excel via le nom
        2. Utilise l'email pour trouver l'ID ClickUp
        """
        # Étape 1 — trouver l'email via Excel (matching par similarité sur le nom)
        best_email = None
        best_score = 0.0

        for username, email in self.name_to_email.items():
            score = SequenceMatcher(None, name.lower(), username.lower()).ratio()
            if score > best_score:
                best_score = score
                best_email = email

        if best_score < 0.5 or not best_email:
            print(f"[WARN] No Excel match for '{name}' (best score: {best_score:.2f})")
            return None

        print(f"[EXCEL] '{name}' → email: {best_email} (score: {best_score:.2f})")

        # Étape 2 — trouver l'ID ClickUp via l'email
        member_id = self.email_to_id.get(best_email.lower())
        if not member_id:
            print(f"[WARN] Email '{best_email}' not found in ClickUp workspace.")
            return None

        print(f"[RESOLVE] '{name}' → ID {member_id}")
        return member_id

    def _create_task(self, list_id: str, result: VerificationResult) -> None:
        url = f"{self.BASE_URL}/list/{list_id}/task"

        payload = {
            "name": result.task_name,
            "description": result.task_description,
            "status": result.task_status,
            "priority": self._priority_to_int(result.task_priority),
        }

        assignee_names = [a.strip() for a in result.task_assigne.split(",")]
        assignee_ids = self._resolve_assignee_ids(assignee_names)
        if assignee_ids:
            payload["assignees"] = assignee_ids

        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 200:
            print(f"[CREATED] '{result.task_name}' in folder '{result.folder}'")
        else:
            print(f"[ERROR] Create failed for '{result.task_name}': {response.text}")

    def _update_task(self, result: VerificationResult) -> None:
        url = f"{self.BASE_URL}/task/{result.task_id}"

        payload = {
            "status": result.task_status,
            "priority": self._priority_to_int(result.task_priority),
        }

        assignee_names = [a.strip() for a in result.task_assigne.split(",")]
        assignee_ids = self._resolve_assignee_ids(assignee_names)
        if assignee_ids:
            payload["assignees"] = {"add": assignee_ids}

        response = requests.put(url, json=payload, headers=self.headers)

        if response.status_code == 200:
            print(f"[UPDATED] '{result.task_name}' (id: {result.task_id})")
        else:
            print(f"[ERROR] Update failed for '{result.task_name}': {response.text}")

    @staticmethod
    def _priority_to_int(priority: str) -> int:
        mapping = {
            "urgent": 1,
            "high": 2,
            "normal": 3,
            "low": 4
        }
        return mapping.get(priority.lower(), 3)

    @staticmethod
    def _build_folder_list_map(folders) -> dict:
        mapping = {}
        for folder in folders:
            if folder.lists:
                mapping[folder.name] = folder.lists[0].id
        return mapping