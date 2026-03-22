"""Prompt loader for .prompty templates."""
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import re
from jinja2 import Environment

from src.domain.exceptions.prompt_invalid_format_exception import PromptInvalidFormatException
from src.domain.exceptions.prompt_missing_inputs_exception import PromptMissingInputsException
from src.domain.exceptions.prompt_template_not_found_exception import PromptTemplateNotFoundException
from src.domain.ports.output.prompt_provider_port import PromptProviderPort


logger = logging.getLogger(__name__)


class PromptyLoader(PromptProviderPort):
    """Load and render .prompty templates."""

    def __init__(self, templates_dir: Optional[str] = None):
        """Initialize the loader.

        :param templates_dir: Optional path to templates directory.
        :raises ValueError: If the templates directory does not exist.
        """
        if templates_dir is None:
            current_dir = Path(__file__).parent.parent
            self.templates_dir = current_dir / "templates"
        else:
            self.templates_dir = Path(templates_dir)

        if not self.templates_dir.exists():
            raise PromptTemplateNotFoundException(
                f"Répertoire de templates introuvable : {self.templates_dir}"
            )
        logger.info("PromptyLoader initialized with templates_dir='%s'.", self.templates_dir)

    @staticmethod
    def _parse_prompty_file(file_path: Path) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split('---')
        if len(parts) < 3:
            raise PromptInvalidFormatException(
                f"Format invalide dans '{file_path.name}' — séparateurs '---' manquants."
            )
        metadata = yaml.safe_load(parts[1])
        prompt_content = '---'.join(parts[2:]).strip()

        role_pattern = re.compile(r'^(system|user|assistant)\s*:\s*\n', re.IGNORECASE)
        prompt_content = role_pattern.sub('', prompt_content).strip()

        return {
            'metadata': metadata,
            'content': prompt_content
        }

    def _load_prompt(self, prompt_name: str, **kwargs: Any) -> str:
        """Load and render a prompt template.

        :param prompt_name: Template name without extension.
        :param kwargs: Template variables for rendering.
        :return: Rendered prompt content.
        :raises FileNotFoundError: If the template does not exist.
        :raises ValueError: If required inputs are missing.
        """
        file_path = self.templates_dir / f"{prompt_name}.prompty"

        if not file_path.exists():
            raise PromptTemplateNotFoundException(
                f"Template '{prompt_name}.prompty' introuvable dans {self.templates_dir}"
            )

        logger.info("Loading prompt template '%s.prompty'.", prompt_name)

        prompty_data = PromptyLoader._parse_prompty_file(file_path)
        prompt_content = prompty_data['content']

        metadata = prompty_data['metadata']
        if 'inputs' in metadata:
            required_inputs = set(metadata['inputs'].keys())
            provided_inputs = set(kwargs.keys())
            missing_inputs = required_inputs - provided_inputs
            if missing_inputs:
                raise PromptMissingInputsException(
                    f"Variables manquantes pour '{prompt_name}' : {missing_inputs}"
                )
        env = Environment(
            variable_start_string="[[",
            variable_end_string="]]",
            block_start_string="[%",
            block_end_string="%]",
            comment_start_string="[#",
            comment_end_string="#]",
        )
        prompt_content = re.sub(
            r"\{\{\s*(\w+)\s*\}\}",
            r"[[ \1 ]]",
            prompt_content,
        )

        template = env.from_string(prompt_content)
        rendered = template.render(**kwargs)

        logger.info("Prompt template '%s.prompty' loaded and rendered successfully.", prompt_name)

        return rendered

    def get_system_prompt(self, name: str) -> str:
        """Return a system prompt by type.

        :return: System prompt content.
        """
        prompt_name = f"system_prompt_{name}"
        return self._load_prompt(prompt_name)

    def get_user_prompt(self, name: str, **kwargs: Any) -> str:
        """Return a user prompt by type.

        :return: User prompt content.
        """
        prompt_name = f"user_prompt_{name}"
        return self._load_prompt(prompt_name, **kwargs)

