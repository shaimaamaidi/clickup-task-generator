from typing import Dict

class UserEmailRepositoryPort:
    """
    Port de sortie : le domaine demande la correspondance username -> email
    """
    def get_username_to_email(self) -> Dict[str, str]:
        pass