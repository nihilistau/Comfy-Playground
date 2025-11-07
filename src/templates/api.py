from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List

from ..config import PlaygroundConfig

DEFAULT_TEMPLATES = [
    {"name": "Photorealistic", "template": "Photorealistic photo of {prompt}", "category": "General"},
    {"name": "Cinematic", "template": "Cinematic poster of {prompt}", "category": "General"},
    {"name": "Studio Portrait", "template": "Studio portrait of {prompt}", "category": "Portrait"},
    {"name": "Fantasy", "template": "Fantasy illustration of {prompt}", "category": "Art"},
    {"name": "Minimal", "template": "{prompt}", "category": "General"},
]


def _templates_path(config: PlaygroundConfig) -> str:
    config.ensure_directories()
    path = config.config_dir / "prompt_templates.json"
    if not path.exists():
        with path.open("w", encoding="utf-8") as fh:
            json.dump(DEFAULT_TEMPLATES, fh, indent=2)
    return str(path)


def get_prompt_templates(config: PlaygroundConfig | None = None) -> List[Dict[str, str]]:
    cfg = config or PlaygroundConfig.load()
    path = _templates_path(cfg)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_prompt_templates(templates: List[Dict[str, str]], *, config: PlaygroundConfig | None = None) -> bool:
    cfg = config or PlaygroundConfig.load()
    path = _templates_path(cfg)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(templates, fh, indent=2)
    return True


def list_categories(templates: List[Dict[str, str]] | None = None, *, config: PlaygroundConfig | None = None) -> List[str]:
    data = templates or get_prompt_templates(config=config)
    return sorted({item.get("category", "General") for item in data})


def add_template(template: Dict[str, str], *, config: PlaygroundConfig | None = None) -> None:
    data = get_prompt_templates(config=config)
    data.append(template)
    save_prompt_templates(data, config=config)


def delete_template(name: str, *, config: PlaygroundConfig | None = None) -> bool:
    data = get_prompt_templates(config=config)
    updated = [item for item in data if item.get("name") != name]
    if len(updated) == len(data):
        return False
    save_prompt_templates(updated, config=config)
    return True
