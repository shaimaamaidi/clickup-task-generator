"""Output port interface for prompt loading and formatting."""

from abc import ABC, abstractmethod
from typing import Any


class PromptProviderPort(ABC):
    """Interface for loading and formatting prompts."""

    @abstractmethod
    def get_system_prompt(self, name: str) -> str:
        """Return a system prompt by type.

        Args:
            name: Prompt name or type identifier.

        Returns:
            System prompt text.
        """
        pass

    @abstractmethod
    def get_user_prompt(self, name: str, **kwargs: Any) -> str:
        """Return a user prompt for workflow conversion.

        Args:
            name: Prompt name or type identifier.
            **kwargs: Template variables used for formatting.

        Returns:
            Formatted user prompt.
        """
        pass

