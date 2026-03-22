"""Unit tests for ClickUp helper functions."""

from src.domain.services import clickup_helper


def test_resolve_assignee_ids_resolves_known_user():
    """Resolve assignee names to ClickUp member IDs when data matches."""
    name_to_email = {"alice": "alice@example.com"}
    email_to_id = {"alice@example.com": 123}

    result = clickup_helper.resolve_assignee_ids(name_to_email, email_to_id, ["alice"])

    assert result == [123]


def test_priority_to_int_maps_known_values():
    """Map priority labels to integer ranks."""
    assert clickup_helper.priority_to_int("urgent") == 1
    assert clickup_helper.priority_to_int("high") == 2
    assert clickup_helper.priority_to_int("normal") == 3
    assert clickup_helper.priority_to_int("low") == 4
    assert clickup_helper.priority_to_int("unknown") == 3
