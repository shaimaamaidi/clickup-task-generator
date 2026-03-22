"""Unit tests for the .prompty prompt loader."""

from pathlib import Path

import pytest

from src.domain.exceptions.prompt_invalid_format_exception import PromptInvalidFormatException
from src.domain.exceptions.prompt_missing_inputs_exception import PromptMissingInputsException
from src.domain.exceptions.prompt_template_not_found_exception import PromptTemplateNotFoundException
from src.infrastructure.prompts.loader.prompt_loader import PromptyLoader


def _write_prompty_file(path: Path, content: str) -> None:
    """Write a .prompty file to disk for tests.

    Args:
        path: Full path to the file to write.
        content: File content.
    """
    path.write_text(content, encoding="utf-8")


def test_get_user_prompt_renders_template(tmp_path: Path):
    """Render a prompt with provided inputs."""
    content = """---
inputs:
    person: str
---
user:
Hello [[ person ]]
"""
    _write_prompty_file(tmp_path / "user_prompt_greet.prompty", content)

    loader = PromptyLoader(templates_dir=str(tmp_path))
    rendered = loader.get_user_prompt("greet", person="Alice")

    assert rendered == "Hello Alice"


def test_missing_inputs_raise_exception(tmp_path: Path):
    """Raise when required inputs are missing."""
    content = """---
inputs:
    person: str
---
user:
Hello [[ person ]]
"""
    _write_prompty_file(tmp_path / "user_prompt_greet.prompty", content)

    loader = PromptyLoader(templates_dir=str(tmp_path))

    with pytest.raises(PromptMissingInputsException):
        loader.get_user_prompt("greet")


def test_missing_template_raises_exception(tmp_path: Path):
    """Raise when the template file does not exist."""
    loader = PromptyLoader(templates_dir=str(tmp_path))

    with pytest.raises(PromptTemplateNotFoundException):
        loader.get_system_prompt("unknown")


def test_invalid_template_format_raises_exception(tmp_path: Path):
    """Raise when the prompty file format is invalid."""
    bad_content = "This file has no separators"
    file_path = tmp_path / "bad.prompty"
    _write_prompty_file(file_path, bad_content)

    with pytest.raises(PromptInvalidFormatException):
        PromptyLoader._parse_prompty_file(file_path)
