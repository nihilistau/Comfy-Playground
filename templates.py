"""Compatibility wrappers for template helpers."""

from src.templates.api import (
    add_template,
    delete_template,
    get_prompt_templates,
    list_categories,
    save_prompt_templates,
)

__all__ = [
    "get_prompt_templates",
    "save_prompt_templates",
    "list_categories",
    "add_template",
    "delete_template",
]
