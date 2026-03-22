import os
from dotenv import load_dotenv
from openai import AzureOpenAI

from src.domain.exceptions.llm_configuration_exception import LLMConfigurationException
from src.domain.exceptions.llm_response_exception import LLMResponseException


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
            raise LLMConfigurationException(
                f"Missing environment variables: {', '.join(missing)}"
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
        try:
            response = self.client.chat.completions.parse(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                response_format=response_format,
            )
            parsed = response.choices[0].message.parsed
            if parsed is None:
                raise LLMResponseException(
                    "The model returned an empty or non-parseable response."
                )
            return parsed
        except LLMResponseException:
            raise
        except Exception as e:
            raise LLMResponseException(
                f"Error while calling model '{self.deployment}': {e}"
            )