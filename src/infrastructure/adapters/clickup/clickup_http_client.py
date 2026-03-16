import os
import requests
from typing import Any
from dotenv import load_dotenv


class ClickUpHttpClient:
    """
    Couche transport : exécute tous les appels HTTP vers l'API ClickUp v2.
    Aucune logique métier ici — uniquement GET / POST / PUT.
    """

    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(self):
        load_dotenv()
        api_token = os.getenv("CLICKUP_API_TOKEN")
        if not api_token:
            raise EnvironmentError("CLICKUP_API_TOKEN manquant dans les variables d'environnement.")
        self._headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
        }

    def get(self, endpoint: str) -> Any:
        response = requests.get(f"{self.BASE_URL}{endpoint}", headers=self._headers)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, payload: dict) -> Any:
        response = requests.post(f"{self.BASE_URL}{endpoint}", json=payload, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def post_raw(self, endpoint: str, payload: dict) -> requests.Response:
        response = requests.post(f"{self.BASE_URL}{endpoint}", json=payload, headers=self._headers)
        return response

    def put(self, endpoint: str, payload: dict) -> Any:
        response = requests.put(f"{self.BASE_URL}{endpoint}", json=payload, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def put_raw(self, endpoint: str, payload: dict) -> Any:
        response = requests.put(f"{self.BASE_URL}{endpoint}", json=payload, headers=self._headers)
        return response