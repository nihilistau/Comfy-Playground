from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional dependency in notebooks
    yaml = None

DEFAULT_CONFIG_NAME = "config.yaml"


@dataclass
class PlaygroundConfig:
    """Runtime configuration loaded from Drive-backed YAML."""

    drive_root: Path = field(default_factory=lambda: Path(os.environ.get("DRIVE_ROOT", "/content/drive/MyDrive/ComfyUI")))
    models_dir: Path = field(init=False)
    loras_dir: Path = field(init=False)
    gguf_dir: Path = field(init=False)
    artifacts_dir: Path = field(init=False)
    config_dir: Path = field(init=False)
    manifests_dir: Path = field(init=False)
    queue_db_path: Path = field(init=False)
    tunnel_preference: str = "cloudflared"
    env_vars: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.drive_root = Path(self.drive_root).expanduser()
        self.models_dir = self.drive_root / "models"
        self.loras_dir = self.models_dir / "loras"
        self.gguf_dir = self.models_dir / "gguf"
        self.artifacts_dir = self.drive_root / "artifacts"
        self.config_dir = self.drive_root / "config"
        self.manifests_dir = self.drive_root / "manifests"
        self.queue_db_path = self.drive_root / "state" / "queue.sqlite3"

    @property
    def yaml_path(self) -> Path:
        return self.config_dir / DEFAULT_CONFIG_NAME

    def ensure_directories(self) -> None:
        for folder in (
            self.drive_root,
            self.models_dir,
            self.loras_dir,
            self.gguf_dir,
            self.artifacts_dir,
            self.config_dir,
            self.manifests_dir,
            self.queue_db_path.parent,
        ):
            folder.mkdir(parents=True, exist_ok=True)

    def save(self) -> None:
        if yaml is None:
            raise RuntimeError("PyYAML is required to persist configuration")
        self.ensure_directories()
        data = {
            "drive_root": str(self.drive_root),
            "tunnel_preference": self.tunnel_preference,
            "env_vars": self.env_vars,
        }
        with self.yaml_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, sort_keys=True)

    @classmethod
    def load(cls, path: Path | None = None) -> "PlaygroundConfig":
        candidate = Path(path) if path else Path(os.environ.get("PLAYGROUND_CONFIG", ""))
        if candidate and candidate.exists():
            return cls.from_yaml(candidate)
        fallback = cls().yaml_path
        if fallback.exists():
            return cls.from_yaml(fallback)
        instance = cls()
        instance.ensure_directories()
        return instance

    @classmethod
    def from_yaml(cls, path: Path) -> "PlaygroundConfig":
        if yaml is None:
            raise RuntimeError("PyYAML is required to read configuration")
        with path.open("r", encoding="utf-8") as fh:
            data: Dict[str, Any] = yaml.safe_load(fh) or {}
        cfg = cls(**{k: v for k, v in data.items() if k in {"drive_root", "tunnel_preference", "env_vars"}})
        cfg.ensure_directories()
        return cfg


def resolve_env(config: PlaygroundConfig) -> Dict[str, str]:
    """Return merged environment variables combining OS and config overrides."""
    merged = dict(os.environ)
    merged.update(config.env_vars)
    return merged
