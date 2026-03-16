from typing import List

from src.domain.models.clickup_list_model import ClickUpList
from src.domain.models.folder_model import Folder
from src.domain.models.task_model import Task
from src.domain.ports.output.clickup_reader_port import ClickUpReaderPort
from src.infrastructure.adapters.clickup.clickup_http_client import ClickUpHttpClient

PRIORITIES = ["urgent", "high", "normal", "low"]

class ClickUpReader(ClickUpReaderPort):

    def __init__(self, http_client: ClickUpHttpClient):
        self._http = http_client
        self.space_id = None

    def set_space_id(self, space_id: str):
        self.space_id = space_id

    def get_space_structure(self, space_id: str) -> List[Folder]:
        """
        Récupère la structure complète d'un space :
        folders → lists → tasks, et inclut statuses et priorities.
        """

        folders_data = self._get_folders(space_id)
        folders: List[Folder] = []

        for folder_data in folders_data:

            lists_data = self._get_lists(folder_data["id"])
            lists: List[ClickUpList] = []

            for list_data in lists_data:

                # Récupérer les détails de la list pour statuts et priorités
                list_details = self._get_list_details(list_data["id"])

                # Récupérer les tasks
                tasks_data = self._get_tasks(list_data["id"])
                tasks: List[Task] = []

                for task in tasks_data:
                    tasks.append(
                        Task(
                            id=task["id"],
                            name=task["name"],
                            description=task.get("description", ""),
                            status=task["status"]["status"],
                            assignee=task["assignees"][0]["username"] if task["assignees"] else None,
                            priority=task["priority"]["priority"] if task.get("priority") else None
                        )
                    )

                # Récupérer les statuses de la list
                statuses = [s["status"] for s in list_details.get("statuses", []) if "status" in s]

                # Récupérer les priorities de la list
                priorities = [
                    p.get("priority") or p.get("name")
                    for p in list_details.get("priorities", [])
                    if p.get("priority") or p.get("name")
                ]

                lists.append(
                    ClickUpList(
                        id=list_data["id"],
                        name=list_data["name"],
                        tasks=tasks,
                        statuses=statuses,
                        priorities=PRIORITIES
                    )
                )

            folders.append(
                Folder(
                    id=folder_data["id"],
                    name=folder_data["name"],
                    lists=lists
                )
            )

        return folders

    def _get_folders(self, space_id: str):
        return self._http.get(f"/space/{space_id}/folder")

    def _get_lists(self, folder_id: str):
        return self._http.get(f"/folder/{folder_id}/list")

    def _get_tasks(self, list_id: str):
        return self._http.get(f"/list/{list_id}/task")

    def _get_list_details(self, list_id: str):
        """
        Récupère les détails complets d'une list, incluant statuses et priorities.
        """
        return self._http.get(f"/list/{list_id}")

    def get_workspace_members(self) -> List[dict]:
        """
        Retourne la liste des membres du workspace.
        Format retourné :
        [
            {"id": 123, "username": "xxxx", "email": "xxxx@example.com"},
            ...
        ]
        """
        teams = self._http.get(f"/team").get("teams", [])
        members = []

        for team in teams:
            if str(team["id"]) == str(self.space_id):
                for m in team.get("members", []):
                    members.append({
                        "id": m["user"]["id"],
                        "username": m["user"]["username"],
                        "email": m["user"]["email"]
                    })
                break

        return members
