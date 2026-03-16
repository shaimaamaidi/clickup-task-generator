"""Output port interface for prompt loading and formatting."""

from abc import ABC, abstractmethod
from typing import Any


class PromptProviderPort(ABC):
    """Interface for loading and formatting prompts."""

    @abstractmethod
    def get_system_prompt(self, name: str) -> str:
        """Return a system prompt by type.

        :return: System prompt text.
        """
        pass

    @abstractmethod
    def get_user_prompt(self, name: str, **kwargs: Any) -> str:
        """Return a user prompt for workflow conversion.

        :return: Formatted user prompt.
        """
        pass

