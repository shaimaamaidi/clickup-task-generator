import logging
from difflib import SequenceMatcher
from typing import List, Dict, Optional


logger = logging.getLogger(__name__)


def resolve_assignee_ids(name_to_email: dict, email_to_id: Dict[str, int], assignee_names: List[str]) -> List[int]:
    """
    Prend une liste de noms (arabes ou autres) et retourne
    la liste des user IDs correspondants via matching par email/username.
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
    """
    1. Cherche l'email dans le dictionnaire Excel via le nom
    2. Utilise l'email pour trouver l'ID ClickUp
    """
    # Étape 1 — trouver l'email via Excel (matching par similarité sur le nom)
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

    # Étape 2 — trouver l'ID ClickUp via l'email
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
    mapping = {
        "urgent": 1,
        "high": 2,
        "normal": 3,
        "low": 4
    }
    return mapping.get(priority.lower(), 3)
