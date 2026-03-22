"""Excel adapter for loading username-to-email mappings."""

import logging
import os

import pandas as pd
from pathlib import Path

from dotenv import load_dotenv

from src.domain.exceptions.excel_file_not_found_exception import ExcelFileNotFoundException
from src.domain.exceptions.excel_missing_columns_exception import ExcelMissingColumnsException
from src.domain.exceptions.excel_read_exception import ExcelReadException
from src.domain.ports.output.user_email_repository_port import UserEmailRepositoryPort


logger = logging.getLogger(__name__)


class ExcelMailReader(UserEmailRepositoryPort):
    """
    Class to read an Excel file containing USERNAME and MAIL columns
    and return a {username: mail} dictionary.
    """

    def __init__(self):
        """Initialize the Excel reader.

        Raises:
            ExcelFileNotFoundException: If the Excel path is missing or invalid.
        """
        load_dotenv()
        excel_path = os.getenv("EXCEL_MAIL_PATH")

        if not excel_path:
            raise ExcelFileNotFoundException(
                "EXCEL_MAIL_PATH environment variable is missing."
            )

        self.file_path = Path(excel_path)

        if not self.file_path.exists():
            raise ExcelFileNotFoundException(
                f"File '{excel_path}' does not exist."
            )

        logger.info("ExcelMailReader initialized with file '%s'.", self.file_path)

    def get_username_to_email(self) -> dict:
        """Read the Excel file and return a {USERNAME: MAIL} dictionary.

        Returns:
            Mapping of USERNAME to MAIL values.

        Raises:
            ExcelReadException: If reading the file fails.
            ExcelMissingColumnsException: If required columns are absent.
        """
        logger.info("Reading username-to-email mapping from '%s'...", self.file_path.name)
        try:
            df = pd.read_excel(self.file_path)
        except Exception as e:
            raise ExcelReadException(
                f"Unable to read Excel file '{self.file_path}': {e}"
            )
        # Normalize columns to ensure they exist
        if 'USERNAME' not in df.columns or 'MAIL' not in df.columns:
            raise ExcelMissingColumnsException(
                f"File '{self.file_path.name}' must contain 'USERNAME' and 'MAIL' columns."
            )

        # Convert to dictionary
        result = dict(zip(df['USERNAME'], df['MAIL']))

        logger.info(
            "Username-to-email mapping loaded: %d entry(ies) from '%s'.",
            len(result),
            self.file_path.name,
        )

        return result