from abc import ABC, abstractmethod


class MeetingProcessingPort(ABC):
    """
    Port d'entrée principal de l'application.
    Définit le contrat pour traiter un résumé de réunion
    et synchroniser les tâches dans ClickUp.
    """

    @abstractmethod
    def process_meeting(self, space_id: str, meeting_summary: str) -> None:
        """
        Traite un résumé de réunion et synchronise les tâches dans ClickUp.

        :param space_id
        :param meeting_summary: Résumé de la réunion en arabe ou en français.
        """
        pass