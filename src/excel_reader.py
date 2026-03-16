import os

import pandas as pd
from pathlib import Path

from dotenv import load_dotenv


class ExcelMailReader:
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
        self.file_path = Path(excel_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Le fichier {excel_path} n'existe pas.")

    def read_to_dict(self) -> dict:
        """
        Lit le fichier Excel et retourne un dictionnaire {USERNAME: MAIL}.

        :return: dict
        """
        try:
            df = pd.read_excel(self.file_path)
            # Nettoyage des colonnes pour s'assurer qu'elles existent
            if 'USERNAME' not in df.columns or 'MAIL' not in df.columns:
                raise ValueError("Le fichier Excel doit contenir les colonnes 'USERNAME' et 'MAIL'.")

            # Conversion en dictionnaire
            result = dict(zip(df['USERNAME'], df['MAIL']))
            return result

        except Exception as e:
            print(f"[ERROR] Impossible de lire le fichier Excel : {e}")
            return {}