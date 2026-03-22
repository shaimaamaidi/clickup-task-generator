"""Integration tests for API routes."""

from fastapi.testclient import TestClient


def test_health_check_returns_ok(test_client: TestClient):
    """Return a healthy status payload."""
    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_meeting_process_returns_counts(test_client: TestClient):
    """Return action counts and results from the use case."""
    response = test_client.post(
        "/meeting/process",
        json={"space_id": "space-1", "meeting_summary": "Summary"},
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["total"] == 1
    assert payload["created"] == 1
    assert payload["updated"] == 0
    assert len(payload["results"]) == 1


def test_meeting_process_validation_error(test_client: TestClient):
    """Return 422 when request validation fails."""
    response = test_client.post("/meeting/process", json={"meeting_summary": "Summary"})

    assert response.status_code == 422
