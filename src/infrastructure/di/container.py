import logging

from src.infrastructure.adapters.clickup.clickup_http_client import ClickUpHttpClient
from src.infrastructure.adapters.clickup.clickup_reader import ClickUpReader
from src.infrastructure.adapters.clickup.clickup_task_writer import ClickUpTaskWriter
from src.infrastructure.adapters.excel.excel_mail_reader import ExcelMailReader
from src.infrastructure.adapters.openai.AzureLLMClient import AzureLLMClient
from src.infrastructure.adapters.openai.clickup_task_generator import ClickUpTaskGenerator
from src.infrastructure.adapters.openai.clickup_task_verifier import ClickUpTaskVerifier
from src.infrastructure.prompts.loader.prompt_loader import PromptyLoader
from src.application.use_cases.process_meeting_use_case import ProcessMeetingUseCase


logger = logging.getLogger(__name__)


class Container:
    """
    Conteneur d'injection de dépendances amélioré.
    Instancie et connecte tous les composants de l'application.
    """

    def __init__(self):
        logger.info("Initializing application container...")

        # --- Clients externes ---
        self._http_client = self._create_http_client()
        self._llm_client = self._create_llm_client()
        self._email_repository = self._create_email_repository()
        self._prompt_provider = self._create_prompt_provider()

        # --- Adaptateurs ClickUp ---
        self._clickup_reader = self._create_clickup_reader()
        self._clickup_writer = self._create_clickup_writer()

        # --- Adaptateurs LLM ---
        self._task_generator = self._create_task_generator()
        self._task_verifier = self._create_task_verifier()

        # --- Use case ---
        self._process_meeting_use_case = self._create_process_meeting_use_case()

        logger.info("Application container initialized successfully.")

    # ---------------------- Création des clients ----------------------
    @staticmethod
    def _create_http_client() -> ClickUpHttpClient:
        logger.info("Creating ClickUpHttpClient...")
        return ClickUpHttpClient()

    @staticmethod
    def _create_llm_client() -> AzureLLMClient:
        logger.info("Creating AzureLLMClient...")
        return AzureLLMClient()

    @staticmethod
    def _create_email_repository() -> ExcelMailReader:
        logger.info("Creating ExcelMailReader...")
        return ExcelMailReader()

    @staticmethod
    def _create_prompt_provider() -> PromptyLoader:
        logger.info("Creating PromptyLoader...")
        return PromptyLoader()

    # ---------------------- Création des adaptateurs ----------------------
    def _create_clickup_reader(self) -> ClickUpReader:
        logger.info("Creating ClickUpReader...")
        return ClickUpReader(self._http_client)

    def _create_clickup_writer(self) -> ClickUpTaskWriter:
        logger.info("Creating ClickUpTaskWriter...")
        return ClickUpTaskWriter(self._http_client)

    def _create_task_generator(self) -> ClickUpTaskGenerator:
        logger.info("Creating ClickUpTaskGenerator...")
        return ClickUpTaskGenerator(self._llm_client, self._prompt_provider)

    def _create_task_verifier(self) -> ClickUpTaskVerifier:
        logger.info("Creating ClickUpTaskVerifier...")
        return ClickUpTaskVerifier(self._llm_client, self._prompt_provider)

    # ---------------------- Création du use case ----------------------
    def _create_process_meeting_use_case(self) -> ProcessMeetingUseCase:
        logger.info("Creating ProcessMeetingUseCase...")
        return ProcessMeetingUseCase(
            clickup_reader=self._clickup_reader,
            task_generator=self._task_generator,
            task_verifier=self._task_verifier,
            clickup_writer=self._clickup_writer,
            email_repository=self._email_repository
        )

    # ---------------------- Accès aux use cases ----------------------
    def get_process_meeting_use_case(self) -> ProcessMeetingUseCase:
        return self._process_meeting_use_case