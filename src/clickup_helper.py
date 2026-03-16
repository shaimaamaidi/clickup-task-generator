from typing import List, Dict
from src.task_model import Task
from src.generated_task_model import GeneratedTask


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