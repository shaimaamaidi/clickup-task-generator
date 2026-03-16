import os
from dotenv import load_dotenv
from openai import AzureOpenAI


class AzureLLMClient:
    """
    Wrapper partagé pour Azure OpenAI.
    Centralise la configuration et l'instanciation du client.
    """

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        missing = [
            name for name, val in {
                "AZURE_OPENAI_API_KEY": api_key,
                "AZURE_OPENAI_API_VERSION": api_version,
                "AZURE_OPENAI_ENDPOINT": endpoint,
                "AZURE_OPENAI_DEPLOYMENT_NAME": self.deployment,
            }.items() if not val
        ]
        if missing:
            raise EnvironmentError(
                f"Variables d'environnement manquantes : {', '.join(missing)}"
            )

        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )

    def parse(self, messages: list, response_format, temperature: float = 0):
        """
        Appel structuré avec response_format Pydantic.
        Retourne l'objet parsé directement.
        """
        response = self.client.chat.completions.parse(
            model=self.deployment,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )
        return response.choices[0].message.parsed