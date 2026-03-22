"""ClickUp reader adapter for folders, lists, and tasks."""

import logging
from typing import List

from src.domain.exceptions.clickup_empty_space_exception import ClickUpEmptySpaceException
from src.domain.exceptions.clickup_workspace_members_exception import ClickUpWorkspaceMembersException
from src.domain.models.clickup_list_model import ClickUpList
from src.domain.models.folder_model import Folder
from src.domain.models.task_model import Task
from src.domain.ports.output.clickup_reader_port import ClickUpReaderPort
from src.infrastructure.adapters.clickup.clickup_http_client import ClickUpHttpClient


logger = logging.getLogger(__name__)


PRIORITIES = ["urgent", "high", "normal", "low"]

class ClickUpReader(ClickUpReaderPort):
    """Adapter to fetch ClickUp space structure and members."""

    def __init__(self, http_client: ClickUpHttpClient):
        """Initialize the reader with an HTTP client.

        Args:
            http_client: ClickUp HTTP client instance.
        """
        self._http = http_client
        self.space_id = None

    def set_space_id(self, space_id: str):
        """Set the current space identifier.

        Args:
            space_id: ClickUp space identifier.
        """
        self.space_id = space_id
        logger.info("Space ID set to '%s'.", space_id)

    def get_space_structure(self, space_id: str) -> List[Folder]:
        """Fetch the full structure of a space.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            List of Folder objects containing lists, tasks, statuses, and priorities.

        Raises:
            ClickUpEmptySpaceException: If the space has no folders.
        """
        logger.info("Fetching space structure for space_id='%s'...", space_id)
        folders_data = self._get_folders(space_id)
        if not folders_data:
            raise ClickUpEmptySpaceException(
                f"No folder found in space '{space_id}'."
            )
        folders: List[Folder] = []

        for folder_data in folders_data:
            logger.info("Processing folder '%s' (id=%s).", folder_data["name"], folder_data["id"])
            lists_data = self._get_lists(folder_data["id"])
            lists: List[ClickUpList] = []

            for list_data in lists_data:
                # Fetch list details for statuses and priorities
                list_details = self._get_list_details(list_data["id"])

                # Fetch tasks
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

                # Fetch list statuses
                statuses = [s["status"] for s in list_details.get("statuses", []) if "status" in s]

                # Fetch list priorities
                priorities = [
                    p.get("priority") or p.get("name")
                    for p in list_details.get("priorities", [])
                    if p.get("priority") or p.get("name")
                ]

                logger.info(
                    "List '%s': %d task(s), %d status(es).",
                    list_data["name"],
                    len(tasks),
                    len(statuses),
                )

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
        logger.info(
            "Space structure fetched: %d folder(s) for space_id='%s'.",
            len(folders),
            space_id,
        )
        return folders

    def get_workspace_members(self) -> List[dict]:
        """Return the list of workspace members.

        Returns:
            List of member dictionaries with id, username, and email.

        Raises:
            ClickUpWorkspaceMembersException: If the workspace has no members.
        """
        logger.info("Fetching workspace members for space_id='%s'...", self.space_id)
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
        if not members:
            raise ClickUpWorkspaceMembersException(
                f"Workspace '{self.space_id}' not found or has no members."
            )

        logger.info(
            "%d member(s) retrieved for workspace '%s'.",
            len(members),
            self.space_id,
        )
        return members

    def _get_folders(self, space_id: str):
        """Fetch folders for a space.

        Args:
            space_id: ClickUp space identifier.

        Returns:
            Parsed JSON response of folders.
        """
        return self._http.get(f"/space/{space_id}/folder")

    def _get_lists(self, folder_id: str):
        """Fetch lists for a folder.

        Args:
            folder_id: ClickUp folder identifier.

        Returns:
            Parsed JSON response of lists.
        """
        return self._http.get(f"/folder/{folder_id}/list")

    def _get_tasks(self, list_id: str):
        """Fetch tasks for a list.

        Args:
            list_id: ClickUp list identifier.

        Returns:
            Parsed JSON response of tasks.
        """
        return self._http.get(f"/list/{list_id}/task")

    def _get_list_details(self, list_id: str):
        """Fetch full list details, including statuses and priorities.

        Args:
            list_id: ClickUp list identifier.

        Returns:
            Parsed JSON response of list details.
        """
        return self._http.get(f"/list/{list_id}")
