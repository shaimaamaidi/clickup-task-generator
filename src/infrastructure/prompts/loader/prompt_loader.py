"""Prompt loader for .prompty templates."""
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import re
from jinja2 import Environment

from src.domain.ports.output.prompt_provider_port import PromptProviderPort


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
            raise ValueError(f"Templates directory not found: {self.templates_dir}")

    @staticmethod
    def _parse_prompty_file(file_path: Path) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split('---')
        if len(parts) < 3:
            raise ValueError(f"Invalid .prompty file format: {file_path}")

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
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        prompty_data = PromptyLoader._parse_prompty_file(file_path)
        prompt_content = prompty_data['content']

        metadata = prompty_data['metadata']
        if 'inputs' in metadata:
            required_inputs = set(metadata['inputs'].keys())
            provided_inputs = set(kwargs.keys())
            missing_inputs = required_inputs - provided_inputs
            if missing_inputs:
                raise ValueError(
                    f"Missing required inputs for {prompt_name}: {missing_inputs}"
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
        return template.render(**kwargs)

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

