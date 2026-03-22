"""Input port for meeting processing use cases."""

from abc import ABC, abstractmethod


class MeetingProcessingPort(ABC):
    """
    Main input port of the application.
    Defines the contract for processing a meeting summary
    and syncing tasks in ClickUp.
    """

    @abstractmethod
    def process_meeting(self, space_id: str, meeting_summary: str) -> None:
        """Process a meeting summary and sync tasks in ClickUp.

        Args:
            space_id: ClickUp space identifier.
            meeting_summary: Meeting summary in Arabic or French.

        Returns:
            None.
        """
        pass