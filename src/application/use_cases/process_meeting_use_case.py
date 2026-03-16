from typing import List

from src.domain.models.folder_model import Folder
from src.domain.models.generated_task_model import GeneratedTask
from src.domain.models.verification_result_model import VerificationResult
from src.domain.ports.input.meeting_processing_port import MeetingProcessingPort
from src.domain.ports.output.clickup_reader_port import ClickUpReaderPort
from src.domain.ports.output.clickup_task_writer_port import ClickUpTaskWriterPort
from src.domain.ports.output.llm_task_generation_port import TaskGenerationPort
from src.domain.ports.output.llm_task_verification_port import TaskVerificationPort
from src.domain.ports.output.user_email_repository_port import UserEmailRepositoryPort
from src.application.services.task_grouping_service import get_folders_statuses_and_priorities, get_generated_tasks_by_folder, \
    get_tasks_by_folder


class ClickUpTaskPipelineUseCase(MeetingProcessingPort):
    """
    Orchestrateur principal du pipeline.
    Ne connaît que des ports (interfaces abstraites) — jamais les adapters concrets.
    """

    def __init__(
        self,
        clickup_repository: ClickUpReaderPort,
        task_generator: TaskGenerationPort,
        task_verifier: TaskVerificationPort,
        task_writer: ClickUpTaskWriterPort,
        email_repository: UserEmailRepositoryPort,
    ):
        self._clickup_repository = clickup_repository
        self._task_generator = task_generator
        self._task_verifier = task_verifier
        self._task_writer = task_writer
        self._email_repository = email_repository

    def process_meeting(self, space_id: str, meeting_summary: str) -> List[VerificationResult]:
        # 1. Récupérer la structure de l'espace ClickUp
        self._clickup_repository.set_space_id(space_id)
        folders: List[Folder] = self._clickup_repository.get_space_structure(space_id)

        # 2. Extraire les statuses/priorités par folder (logique applicative, pas domaine)
        folders_statuses = get_folders_statuses_and_priorities(folders)

        # 3. Générer les tasks depuis le résumé de réunion
        generated_tasks: List[GeneratedTask] = self._task_generator.generate_tasks(
            meeting_summary=meeting_summary,
            folders_statuses=folders_statuses,
        )

        # 4. Grouper les tasks existantes et générées par folder
        existing_by_folder = get_tasks_by_folder(folders)
        generated_by_folder = get_generated_tasks_by_folder(generated_tasks)

        # 5. Vérifier folder par folder (doublon ? créer ? mettre à jour ?)
        all_results = []
        for folder_name, gen_tasks in generated_by_folder.items():
            existing_tasks = existing_by_folder.get(folder_name, [])
            results = self._task_verifier.verify_tasks(
                existing_tasks=existing_tasks,
                generated_tasks=gen_tasks,
            )
            all_results.extend(results)

        name_to_email = self._email_repository.get_username_to_email()
        memebers = self._clickup_repository.get_workspace_members()


        # 6. Appliquer les résultats dans ClickUp (create / update / skip)
        self._task_writer.apply_results(all_results, folders, memebers, name_to_email)

        return all_results