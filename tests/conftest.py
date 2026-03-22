"""Shared pytest fixtures for unit and integration tests."""

from dataclasses import dataclass

from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient

from src.domain.models.clickup_list_model import ClickUpList
from src.domain.models.folder_model import Folder
from src.domain.models.task_model import Task
from src.domain.models.verification_result_model import VerificationResult
from src.presnetation.api.routers import health, meeting


@dataclass
class GeneratedTaskStub:
    """Stub model for generated task data used in tests."""

    task_name: str
    task_description: str
    task_assigne: str
    task_status: str
    task_priority: str
    folder: str


@pytest.fixture()
def sample_tasks() -> list[Task]:
    """Return sample tasks for grouping tests."""
    return [
        Task(id="1", name="Task A", description="Desc A", status="todo", assignee=None, priority=None),
        Task(id="2", name="Task B", description="Desc B", status="done", assignee="alice", priority="high"),
    ]


@pytest.fixture()
def sample_list(sample_tasks: list[Task]) -> ClickUpList:
    """Return a sample ClickUp list with tasks."""
    return ClickUpList(id="list-1", name="List A", tasks=sample_tasks, statuses=[], priorities=[])


@pytest.fixture()
def sample_folder(sample_list: ClickUpList) -> Folder:
    """Return a sample folder with one list."""
    return Folder(id="folder-1", name="Engineering", lists=[sample_list])


@pytest.fixture()
def sample_generated_tasks() -> list[GeneratedTaskStub]:
    """Return sample generated tasks for grouping tests."""
    return [
        GeneratedTaskStub(
            task_name="Task A",
            task_description="Desc A",
            task_assigne="alice",
            task_status="todo",
            task_priority="high",
            folder="Engineering",
        ),
        GeneratedTaskStub(
            task_name="Task B",
            task_description="Desc B",
            task_assigne="bob",
            task_status="in progress",
            task_priority="low",
            folder="Marketing",
        ),
    ]


@pytest.fixture()
def stub_verification_results() -> list[VerificationResult]:
    """Return a deterministic verification result list for API tests."""
    return [
        VerificationResult(
            action="create",
            task_name="Task A",
            task_description="Desc A",
            task_assigne="alice",
            task_status="todo",
            task_priority="high",
            folder="Engineering",
            task_id=None,
        )
    ]


@pytest.fixture()
def test_client(stub_verification_results: list[VerificationResult]) -> TestClient:
    """Return a FastAPI test client wired with stubbed dependencies."""
    class _StubUseCase:
        """Stub use case for meeting processing."""

        def process_meeting(self, space_id: str, meeting_summary: str):
            """Return a deterministic verification result list."""
            return stub_verification_results

    class _StubContainer:
        """Stub container returning a meeting use case."""

        def get_process_meeting_use_case(self):
            """Return the stubbed meeting use case."""
            return _StubUseCase()

    app = FastAPI()
    app.include_router(health.router)
    app.include_router(meeting.router)
    app.state.container = _StubContainer()
    return TestClient(app)
