import logging
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


logger = logging.getLogger(__name__)


class ProcessMeetingUseCase(MeetingProcessingPort):
    """
    Orchestrateur principal du pipeline.
    Ne connaît que des ports (interfaces abstraites) — jamais les adapters concrets.
    """

    def __init__(
        self,
        clickup_reader: ClickUpReaderPort,
        task_generator: TaskGenerationPort,
        task_verifier: TaskVerificationPort,
        clickup_writer: ClickUpTaskWriterPort,
        email_repository: UserEmailRepositoryPort,
    ):
        self._clickup_reader = clickup_reader
        self._task_generator = task_generator
        self._task_verifier = task_verifier
        self._clickup_writer = clickup_writer
        self._email_repository = email_repository

    def process_meeting(self, space_id: str, meeting_summary: str) -> List[VerificationResult]:
        logger.info("Starting meeting processing for space_id='%s'", space_id)

        # 1. Récupérer la structure de l'espace ClickUp
        self._clickup_reader.set_space_id(space_id)
        folders: List[Folder] = self._clickup_reader.get_space_structure(space_id)
        logger.info(
            "Space structure retrieved: %d folder(s) found for space_id='%s'",
            len(folders),
            space_id,
        )

        # 2. Extraire les statuses/priorités par folder (logique applicative, pas domaine)
        folders_statuses = get_folders_statuses_and_priorities(folders)

        # 3. Générer les tasks depuis le résumé de réunion
        logger.info("Generating tasks from meeting summary...")
        generated_tasks: List[GeneratedTask] = self._task_generator.generate_tasks(
            meeting_summary=meeting_summary,
            folders_statuses=folders_statuses,
        )
        logger.info("%d task(s) generated from meeting summary.", len(generated_tasks))

        if not generated_tasks:
            logger.warning("No tasks extracted from meeting summary — pipeline stopped early.")
            return []

        # 4. Grouper les tasks existantes et générées par folder
        existing_by_folder = get_tasks_by_folder(folders)
        generated_by_folder = get_generated_tasks_by_folder(generated_tasks)

        # 5. Vérifier folder par folder (doublon ? créer ? mettre à jour ?)
        logger.info("Starting task verification across %d folder(s)...", len(generated_by_folder))
        all_results = []
        for folder_name, gen_tasks in generated_by_folder.items():
            existing_tasks = existing_by_folder.get(folder_name, [])
            logger.info(
                "Verifying folder '%s': %d generated vs %d existing task(s).",
                folder_name,
                len(gen_tasks),
                len(existing_tasks),
            )
            results = self._task_verifier.verify_tasks(
                existing_tasks=existing_tasks,
                generated_tasks=gen_tasks,
            )
            logger.info(
                "Folder '%s' verification result: %d action(s) to apply.",
                folder_name,
                len(results),
            )
            all_results.extend(results)

        if not all_results:
            logger.warning("No create/update actions to apply after verification.")
            return []

        # 6. Récupérer membres et emails
        name_to_email = self._email_repository.get_username_to_email()
        members = self._clickup_reader.get_workspace_members()
        logger.info("Workspace members retrieved: %d member(s).", len(members))

        # 7. Appliquer les résultats dans ClickUp (create / update / skip)
        logger.info("Applying results to ClickUp...")
        self._clickup_writer.apply_results(all_results, folders, members, name_to_email)

        logger.info(
            "Meeting processing completed for space_id='%s': %d action(s) applied.",
            space_id,
            len(all_results),
        )

        return all_results