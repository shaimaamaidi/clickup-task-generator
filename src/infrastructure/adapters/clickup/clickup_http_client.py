"""HTTP client for ClickUp API interactions."""

import logging
import os
import requests
from typing import Any
from dotenv import load_dotenv

from src.domain.exceptions.clickup_api_exception import ClickUpApiException
from src.domain.exceptions.clickup_authentication_exception import ClickUpAuthenticationException
from src.domain.exceptions.clickup_resource_not_found_exception import ClickUpResourceNotFoundException


logger = logging.getLogger(__name__)


class ClickUpHttpClient:
    """
    Transport layer: executes all HTTP calls to the ClickUp v2 API.
    No business logic here — only GET / POST / PUT.
    """

    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(self):
        """Initialize the client using environment configuration.

        Raises:
            ClickUpAuthenticationException: If the API token is missing.
        """
        load_dotenv()
        api_token = os.getenv("CLICKUP_API_TOKEN")
        if not api_token:
            raise ClickUpAuthenticationException(
                "CLICKUP_API_TOKEN is missing from environment variables."
            )
        self._headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
        }
        logger.info("ClickUpHttpClient initialized successfully.")

    def get(self, endpoint: str) -> Any:
        """Send a GET request to the ClickUp API.

        Args:
            endpoint: API endpoint path starting with '/'.

        Returns:
            Parsed JSON response.
        """
        logger.info("GET %s", endpoint)
        response = requests.get(f"{self.BASE_URL}{endpoint}", headers=self._headers)
        self._handle_response(response)
        return response.json()

    def post(self, endpoint: str, payload: dict) -> Any:
        """Send a POST request to the ClickUp API.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Parsed JSON response.
        """
        logger.info("POST %s", endpoint)
        response = requests.post(f"{self.BASE_URL}{endpoint}", json=payload, headers=self._headers)
        self._handle_response(response)
        return response.json()

    def post_raw(self, endpoint: str, payload: dict) -> requests.Response:
        """Send a POST request and return the raw response.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Raw Response object.
        """
        logger.info("POST (raw) %s", endpoint)
        response = requests.post(f"{self.BASE_URL}{endpoint}", json=payload, headers=self._headers)
        return response

    def put(self, endpoint: str, payload: dict) -> Any:
        """Send a PUT request to the ClickUp API.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Parsed JSON response.
        """
        logger.info("PUT %s", endpoint)
        response = requests.put(f"{self.BASE_URL}{endpoint}", json=payload, headers=self._headers)
        self._handle_response(response)
        return response.json()

    def put_raw(self, endpoint: str, payload: dict) -> Any:
        """Send a PUT request and return the raw response.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Raw Response object.
        """
        logger.info("PUT (raw) %s", endpoint)
        response = requests.put(f"{self.BASE_URL}{endpoint}", json=payload, headers=self._headers)
        return response

    @staticmethod
    def _handle_response(response: requests.Response) -> None:
        """Raise domain exceptions based on HTTP status codes.

        Args:
            response: HTTP response from the ClickUp API.

        Raises:
            ClickUpAuthenticationException: On 401 responses.
            ClickUpResourceNotFoundException: On 404 responses.
            ClickUpApiException: On non-OK responses.
        """
        if response.status_code == 401:
            raise ClickUpAuthenticationException(
                f"Invalid or expired token — {response.text}"
            )
        if response.status_code == 404:
            raise ClickUpResourceNotFoundException(
                f"Resource not found: {response.url} — {response.text}"
            )
        if not response.ok:
            raise ClickUpApiException(
                f"ClickUp API error ({response.status_code}) — {response.text}"
            )