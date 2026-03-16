from difflib import SequenceMatcher
from typing import List, Dict, Optional

def resolve_assignee_ids(name_to_email: dict, email_to_id: Dict[str, int], assignee_names: List[str]) -> List[int]:
    """
    Prend une liste de noms (arabes ou autres) et retourne
    la liste des user IDs correspondants via matching par email/username.
    """
    resolved = []
    for name in assignee_names:
        if not name or name == "غير محدد":
            continue
        member_id = find_member_id(name, name_to_email, email_to_id)
        if member_id:
            resolved.append(member_id)
        else:
            print(f"[WARN] Member '{name}' not found in workspace.")
    return resolved


def find_member_id(name: str, name_to_email: dict, email_to_id: Dict[str, int]) -> Optional[int]:
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
        print(f"[WARN] No Excel match for '{name}' (best score: {best_score:.2f})")
        return None

    print(f"[EXCEL] '{name}' → email: {best_email} (score: {best_score:.2f})")

    # Étape 2 — trouver l'ID ClickUp via l'email
    member_id = email_to_id.get(best_email.lower())
    if not member_id:
        print(f"[WARN] Email '{best_email}' not found in ClickUp workspace.")
        return None

    print(f"[RESOLVE] '{name}' → ID {member_id}")
    return member_id

def priority_to_int(priority: str) -> int:
    mapping = {
        "urgent": 1,
        "high": 2,
        "normal": 3,
        "low": 4
    }
    return mapping.get(priority.lower(), 3)
