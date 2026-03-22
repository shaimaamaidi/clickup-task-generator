"""Output port for retrieving username-to-email mappings."""

from typing import Dict


class UserEmailRepositoryPort:
    """
    Output port: the domain requests the username -> email mapping.
    """
    def get_username_to_email(self) -> Dict[str, str]:
        """Return the username to email mapping.

        Returns:
            Mapping of usernames to email addresses.
        """
        pass