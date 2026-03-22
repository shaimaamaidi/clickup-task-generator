"""Domain helpers for resolving ClickUp assignees and priorities."""

import logging
from difflib import SequenceMatcher
from typing import List, Dict, Optional


logger = logging.getLogger(__name__)


def resolve_assignee_ids(name_to_email: dict, email_to_id: Dict[str, int], assignee_names: List[str]) -> List[int]:
    """Resolve assignee names to ClickUp member IDs.

    Args:
        name_to_email: Mapping of usernames to emails from Excel.
        email_to_id: Mapping of email to ClickUp member ID.
        assignee_names: List of assignee display names.

    Returns:
        List of resolved ClickUp member IDs.
    """
    resolved = []
    for name in assignee_names:
        if not name or name == "غير محدد":
            continue
        member_id = _find_member_id(name, name_to_email, email_to_id)
        if member_id:
            resolved.append(member_id)
        else:
            logger.warning("Member '%s' not found in workspace.", name)

    logger.info(
        "Assignee resolution: %d/%d resolved.",
        len(resolved),
        len([n for n in assignee_names if n and n != "غير محدد"]),
    )
    return resolved


def _find_member_id(name: str, name_to_email: dict, email_to_id: Dict[str, int]) -> Optional[int]:
    """Resolve a single name to a ClickUp member ID.

    The resolution is performed by:
    1. Looking up the email in the Excel dictionary by name.
    2. Using the email to find the ClickUp ID.

    Args:
        name: Assignee display name.
        name_to_email: Mapping of usernames to emails from Excel.
        email_to_id: Mapping of email to ClickUp member ID.

    Returns:
        ClickUp member ID if found, otherwise None.
    """
    # Step 1 — find the email via Excel (similarity match on the name)
    best_email = None
    best_score = 0.0

    for username, email in name_to_email.items():
        score = SequenceMatcher(None, name.lower(), username.lower()).ratio()
        if score > best_score:
            best_score = score
            best_email = email

    if best_score < 0.5 or not best_email:
        logger.warning(
            "No Excel match for '%s' (best score: %.2f).",
            name,
            best_score,
        )
        return None

    logger.info(
        "Excel match: '%s' → email='%s' (score: %.2f).",
        name,
        best_email,
        best_score,
    )

    # Step 2 — find the ClickUp ID via the email
    member_id = email_to_id.get(best_email.lower())
    if not member_id:
        logger.warning(
            "Email '%s' matched for '%s' but not found in ClickUp workspace.",
            best_email,
            name,
        )
        return None

    logger.info("Resolved: '%s' → ClickUp ID %s.", name, member_id)
    return member_id

def priority_to_int(priority: str) -> int:
    """Convert a priority label to a numeric rank.

    Args:
        priority: Priority label (e.g., urgent, high, normal, low).

    Returns:
        Integer rank where lower means higher priority.
    """
    mapping = {
        "urgent": 1,
        "high": 2,
        "normal": 3,
        "low": 4
    }
    return mapping.get(priority.lower(), 3)
