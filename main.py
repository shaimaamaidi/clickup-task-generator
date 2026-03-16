from src.clickup_connector import ClickUpConnector
from src.clickup_task_generator import ClickUpTaskGenerator
from src.excel_reader import ExcelMailReader

SPACE_ID="90126596055"
connector = ClickUpConnector()

connector.set_space_id(SPACE_ID)

folders = connector.get_space_structure(SPACE_ID)
for folder in folders:
    print(f"Folder: {folder.name} (id: {folder.id})")
    for lst in folder.lists:
        print(f"  List: {lst.name} (id: {lst.id})")
        print(f"    Statuses: {lst.statuses}")
        print(f"    Priorities: {lst.priorities}")
        print(f"    Tasks:")
        if lst.tasks:
            for task in lst.tasks:
                print(f"      - {task.name} | Status: {task.status} | Assignee: {task.assignee} | Priority: {task.priority}")
        else:
            print("      (No tasks)")

dic = ClickUpConnector.get_folders_statuses_and_priorities(folders)

print("\nFolders and their statuses & priorities:")
for folder_name, info in dic.items():
    print(f"Folder: {folder_name}")
    print(f"  Statuses: {info['statuses']}")
    print(f"  Priorities: {info['priorities']}")

generator = ClickUpTaskGenerator()

MEETING_SUMMARY = """
عُقد اجتماع لمناقشة تحسين منصة العمل الرقمية.

تم تكليف علاء شرباجي بتحليل مشكلة بطء تحميل الصفحات الرئيسية واقتراح حلول لتحسين الأداء.

تم تكليف شوش فادي بتصميم واجهة جديدة لنظام الإشعارات داخل المنصة.

كما تم تكليف واجدي بن سلامة بدراسة إمكانية دمج المنصة مع خدمات البريد الإلكتروني وتطبيقات المراسلة.

وفي نهاية الاجتماع تم الاتفاق على أن يقوم كل مسؤول بمتابعة المهمة الخاصة به وتقديم تقرير بالتقدم خلال الاجتماع القادم.
"""

tasks = generator.create_tasks(meeting_summary=MEETING_SUMMARY, folders_statuses=dic)


print("\nGenerated tasks:")

for t in tasks:
    print("---------------")
    print("Name:", t.task_name)
    print("Description:", t.task_description)
    print("Assignee:", t.task_assigne)
    print("Status:", t.task_status)
    print("Priority: ", t.task_priority)
    print("Folder:", t.folder)


from src.clickup_helper import get_tasks_by_folder, get_generated_tasks_by_folder, print_tasks_by_folder, \
    print_generated_tasks_by_folder
from src.task_verifier import ClickUpTaskVerifier

# Grouper les tasks existantes par folder
existing_by_folder = get_tasks_by_folder(folders)

# Grouper les tasks générées par folder
generated_by_folder = get_generated_tasks_by_folder(tasks)

print("\nExisting tasks by folder:")
print_tasks_by_folder(existing_by_folder)

print("\nGenerated tasks by folder:")
print_generated_tasks_by_folder(generated_by_folder)
# Vérification folder par folder
verifier = ClickUpTaskVerifier()
all_results = []

for folder_name, gen_tasks in generated_by_folder.items():
    existing_tasks = existing_by_folder.get(folder_name, [])

    results = verifier.verify(
        existing_tasks=existing_tasks,
        generated_tasks=gen_tasks
    )
    all_results.extend(results)

# Affichage des résultats
print("\nVerification results:")
for r in all_results:
    print("---------------")
    print("Action:", r.action)
    print("Name:", r.task_name)
    print("Status:", r.task_status)
    print("Priority:", r.task_priority)
    print("Assignee:", r.task_assigne)
    print("Folder:", r.folder)
    if r.task_id:
        print("Task ID (to update):", r.task_id)

from src.clickup_task_manager import ClickUpTaskManager

excel_reader = ExcelMailReader()
name_to_email = excel_reader.read_to_dict()

print("\nExcel members:")
for username, email in name_to_email.items():
    print(f"  - {username} → {email}")

members = connector.get_workspace_members()
manager = ClickUpTaskManager(members, name_to_email)
manager.apply_results(all_results, folders)

