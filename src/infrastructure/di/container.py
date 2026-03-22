"""Dependency injection container for wiring application components."""

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
    Enhanced dependency injection container.
    Instantiates and wires all application components.
    """

    def __init__(self):
        """Initialize and wire all application components."""
        logger.info("Initializing application container...")

        # --- External clients ---
        self._http_client = self._create_http_client()
        self._llm_client = self._create_llm_client()
        self._email_repository = self._create_email_repository()
        self._prompt_provider = self._create_prompt_provider()

        # --- ClickUp adapters ---
        self._clickup_reader = self._create_clickup_reader()
        self._clickup_writer = self._create_clickup_writer()

        # --- LLM adapters ---
        self._task_generator = self._create_task_generator()
        self._task_verifier = self._create_task_verifier()

        # --- Use case ---
        self._process_meeting_use_case = self._create_process_meeting_use_case()

        logger.info("Application container initialized successfully.")

    # ---------------------- Client creation ----------------------
    @staticmethod
    def _create_http_client() -> ClickUpHttpClient:
        """Create the ClickUp HTTP client.

        Returns:
            ClickUpHttpClient instance.
        """
        logger.info("Creating ClickUpHttpClient...")
        return ClickUpHttpClient()

    @staticmethod
    def _create_llm_client() -> AzureLLMClient:
        """Create the Azure OpenAI client.

        Returns:
            AzureLLMClient instance.
        """
        logger.info("Creating AzureLLMClient...")
        return AzureLLMClient()

    @staticmethod
    def _create_email_repository() -> ExcelMailReader:
        """Create the email repository adapter.

        Returns:
            ExcelMailReader instance.
        """
        logger.info("Creating ExcelMailReader...")
        return ExcelMailReader()

    @staticmethod
    def _create_prompt_provider() -> PromptyLoader:
        """Create the prompt provider.

        Returns:
            PromptyLoader instance.
        """
        logger.info("Creating PromptyLoader...")
        return PromptyLoader()

    # ---------------------- Adapter creation ----------------------
    def _create_clickup_reader(self) -> ClickUpReader:
        """Create the ClickUp reader adapter.

        Returns:
            ClickUpReader instance.
        """
        logger.info("Creating ClickUpReader...")
        return ClickUpReader(self._http_client)

    def _create_clickup_writer(self) -> ClickUpTaskWriter:
        """Create the ClickUp task writer adapter.

        Returns:
            ClickUpTaskWriter instance.
        """
        logger.info("Creating ClickUpTaskWriter...")
        return ClickUpTaskWriter(self._http_client)

    def _create_task_generator(self) -> ClickUpTaskGenerator:
        """Create the task generator adapter.

        Returns:
            ClickUpTaskGenerator instance.
        """
        logger.info("Creating ClickUpTaskGenerator...")
        return ClickUpTaskGenerator(self._llm_client, self._prompt_provider)

    def _create_task_verifier(self) -> ClickUpTaskVerifier:
        """Create the task verifier adapter.

        Returns:
            ClickUpTaskVerifier instance.
        """
        logger.info("Creating ClickUpTaskVerifier...")
        return ClickUpTaskVerifier(self._llm_client, self._prompt_provider)

    # ---------------------- Use case creation ----------------------
    def _create_process_meeting_use_case(self) -> ProcessMeetingUseCase:
        """Create the meeting processing use case.

        Returns:
            ProcessMeetingUseCase instance.
        """
        logger.info("Creating ProcessMeetingUseCase...")
        return ProcessMeetingUseCase(
            clickup_reader=self._clickup_reader,
            task_generator=self._task_generator,
            task_verifier=self._task_verifier,
            clickup_writer=self._clickup_writer,
            email_repository=self._email_repository
        )

    # ---------------------- Use case access ----------------------
    def get_process_meeting_use_case(self) -> ProcessMeetingUseCase:
        """Return the meeting processing use case.

        Returns:
            ProcessMeetingUseCase instance.
        """
        return self._process_meeting_use_case