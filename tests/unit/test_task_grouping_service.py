"""Unit tests for task grouping services."""

from src.application.services import task_grouping_service
from src.domain.models.clickup_list_model import ClickUpList
from src.domain.models.folder_model import Folder


def test_get_tasks_by_folder_groups_tasks(sample_folder: Folder):
    """Group existing tasks by folder name."""
    result = task_grouping_service.get_tasks_by_folder([sample_folder])

    assert list(result.keys()) == ["Engineering"]
    assert len(result["Engineering"]) == 2
    assert result["Engineering"][0].id == "1"


def test_get_generated_tasks_by_folder_groups_tasks(sample_generated_tasks: list[object]):
    """Group generated tasks by folder name."""
    result = task_grouping_service.get_generated_tasks_by_folder(sample_generated_tasks)

    assert set(result.keys()) == {"Engineering", "Marketing"}
    assert result["Engineering"][0].task_name == "Task A"


def test_get_folders_statuses_and_priorities_returns_unique_values(sample_folder: Folder, sample_list: ClickUpList):
    """Collect statuses and priorities from lists per folder."""
    sample_list.statuses = ["todo", "in progress", "done", "done"]
    sample_list.priorities = ["low", "high", "low"]
    sample_folder.lists = [sample_list]

    result = task_grouping_service.get_folders_statuses_and_priorities([sample_folder])

    assert set(result["Engineering"]["statuses"]) == {"todo", "in progress", "done"}
    assert set(result["Engineering"]["priorities"]) == {"low", "high"}
