import os

import pandas as pd
from pathlib import Path

from dotenv import load_dotenv

from src.domain.exceptions.excel_file_not_found_exception import ExcelFileNotFoundException
from src.domain.exceptions.excel_missing_columns_exception import ExcelMissingColumnsException
from src.domain.exceptions.excel_read_exception import ExcelReadException
from src.domain.ports.output.user_email_repository_port import UserEmailRepositoryPort


class ExcelMailReader(UserEmailRepositoryPort):
    """
    Classe pour lire un fichier Excel contenant des colonnes USERNAME et MAIL
    et retourner un dictionnaire {username: mail}.
    """

    def __init__(self):
        """
        Initialise le lecteur Excel.

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

    def get_username_to_email(self) -> dict:
        """
        Lit le fichier Excel et retourne un dictionnaire {USERNAME: MAIL}.

        :return: dict
        """
        try:
            df = pd.read_excel(self.file_path)
        except Exception as e:
            raise ExcelReadException(
                f"Unable to read Excel file '{self.file_path}': {e}"
            )
        # Nettoyage des colonnes pour s'assurer qu'elles existent
        if 'USERNAME' not in df.columns or 'MAIL' not in df.columns:
            raise ExcelMissingColumnsException(
                f"File '{self.file_path.name}' must contain 'USERNAME' and 'MAIL' columns."
            )

        # Conversion en dictionnaire
        return dict(zip(df['USERNAME'], df['MAIL']))
