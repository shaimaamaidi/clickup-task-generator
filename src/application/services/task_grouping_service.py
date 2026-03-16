from typing import List, Dict
from src.domain.models.task_model import Task
from src.domain.models.generated_task_model import GeneratedTask

def get_tasks_by_folder(folders) -> Dict[str, List[Task]]:
    result: Dict[str, List[Task]] = {}

    for folder in folders:
        tasks: List[Task] = []
        for lst in folder.lists:
            tasks.extend(lst.tasks)
        result[folder.name] = tasks

    return result


def get_generated_tasks_by_folder(generated_tasks: List[GeneratedTask]) -> Dict[str, List[GeneratedTask]]:
    result: Dict[str, List[GeneratedTask]] = {}

    for task in generated_tasks:
        folder = task.folder
        if folder not in result:
            result[folder] = []
        result[folder].append(task)

    return result

def print_tasks_by_folder(tasks_by_folder: Dict[str, List[Task]]) -> None:
    for folder_name, tasks in tasks_by_folder.items():
        print(f"Folder: {folder_name}")
        if tasks:
            for task in tasks:
                print(f"  - Name: {task.name}")
                print(f"    Description: {task.description}")
        else:
            print("  (No tasks)")


def print_generated_tasks_by_folder(generated_by_folder: Dict[str, List[GeneratedTask]]) -> None:
    for folder_name, tasks in generated_by_folder.items():
        print(f"Folder: {folder_name}")
        if tasks:
            for task in tasks:
                print(f"  - Name: {task.task_name}")
                print(f"    Description: {task.task_description}")
        else:
            print("  (No tasks)")




def get_folders_statuses_and_priorities(folders) -> Dict[str, Dict[str, List[str]]]:
    """
    Retourne les statuts et priorités disponibles pour chaque folder
    même si aucune task n'existe.

    Format renvoyé :
    {
        "folder_name": {
            "statuses": ["to do", "in progress", "done"],
            "priorities": ["low", "medium", "high"]
        }
    }
    """

    folders_info: Dict[str, Dict[str, set]] = {}

    for folder in folders:

        if folder.name not in folders_info:
            folders_info[folder.name] = {"statuses": set(), "priorities": set()}

        for lst in folder.lists:
            # Ajouter les statuts définis dans la list
            for status in lst.statuses:
                folders_info[folder.name]["statuses"].add(status)

            # Ajouter les priorités définies dans la list
            for priority in lst.priorities:
                folders_info[folder.name]["priorities"].add(priority)

    # conversion set -> list
    return {
        folder: {
            "statuses": list(info["statuses"]),
            "priorities": list(info["priorities"])
        }
        for folder, info in folders_info.items()
    }
