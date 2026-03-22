"""Application services for grouping tasks and folder metadata."""

import logging
from typing import List, Dict
from src.domain.models.task_model import Task
from src.domain.models.generated_task_model import GeneratedTask


logger = logging.getLogger(__name__)


def get_tasks_by_folder(folders) -> Dict[str, List[Task]]:
    """Group existing tasks by folder name.

    Args:
        folders: Iterable of Folder objects containing lists and tasks.

    Returns:
        Mapping of folder name to a list of Task instances.
    """
    result: Dict[str, List[Task]] = {}

    for folder in folders:
        tasks: List[Task] = []
        for lst in folder.lists:
            tasks.extend(lst.tasks)
        result[folder.name] = tasks

    logger.info(
        "Existing tasks grouped by folder: %s",
        {name: len(tasks) for name, tasks in result.items()},
    )

    return result


def get_generated_tasks_by_folder(generated_tasks: List[GeneratedTask]) -> Dict[str, List[GeneratedTask]]:
    """Group generated tasks by folder name.

    Args:
        generated_tasks: List of GeneratedTask instances.

    Returns:
        Mapping of folder name to a list of GeneratedTask instances.
    """
    result: Dict[str, List[GeneratedTask]] = {}

    for task in generated_tasks:
        folder = task.folder
        if folder not in result:
            result[folder] = []
        result[folder].append(task)

    logger.info(
        "Generated tasks grouped by folder: %s",
        {name: len(tasks) for name, tasks in result.items()},
    )

    return result

def print_tasks_by_folder(tasks_by_folder: Dict[str, List[Task]]) -> None:
    """Print grouped tasks to stdout.

    Args:
        tasks_by_folder: Mapping of folder name to existing tasks.

    Returns:
        None.
    """
    for folder_name, tasks in tasks_by_folder.items():
        print(f"Folder: {folder_name}")
        if tasks:
            for task in tasks:
                print(f"  - Name: {task.name}")
                print(f"    Description: {task.description}")
        else:
            print("  (No tasks)")


def print_generated_tasks_by_folder(generated_by_folder: Dict[str, List[GeneratedTask]]) -> None:
    """Print grouped generated tasks to stdout.

    Args:
        generated_by_folder: Mapping of folder name to generated tasks.

    Returns:
        None.
    """
    for folder_name, tasks in generated_by_folder.items():
        print(f"Folder: {folder_name}")
        if tasks:
            for task in tasks:
                print(f"  - Name: {task.task_name}")
                print(f"    Description: {task.task_description}")
        else:
            print("  (No tasks)")




def get_folders_statuses_and_priorities(folders) -> Dict[str, Dict[str, List[str]]]:
    """Collect statuses and priorities available per folder.

    Args:
        folders: Iterable of Folder objects containing lists and metadata.

    Returns:
        Mapping of folder name to available statuses and priorities.
        Example:
            {
                "folder_name": {
                    "statuses": ["to do", "in progress", "done"],
                    "priorities": ["low", "medium", "high"],
                }
            }
    """

    folders_info: Dict[str, Dict[str, set]] = {}

    for folder in folders:

        if folder.name not in folders_info:
            folders_info[folder.name] = {"statuses": set(), "priorities": set()}

        for lst in folder.lists:
            # Add statuses defined on the list
            for status in lst.statuses:
                folders_info[folder.name]["statuses"].add(status)

            # Add priorities defined on the list
            for priority in lst.priorities:
                folders_info[folder.name]["priorities"].add(priority)

    result = {
        folder: {
            "statuses": list(info["statuses"]),
            "priorities": list(info["priorities"]),
        }
        for folder, info in folders_info.items()
    }

    logger.info(
        "Folders statuses and priorities extracted: %s",
        {name: {"statuses": data["statuses"], "priorities": data["priorities"]}
         for name, data in result.items()},
    )

    return result
