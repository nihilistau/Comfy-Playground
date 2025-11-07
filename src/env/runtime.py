from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Dict

from ..config import PlaygroundConfig


def ensure_drive_mounted(config: PlaygroundConfig) -> Path:
    """Ensure the Drive layout exists (mounting in Colab handled externally)."""
    config.ensure_directories()
    sentinel = config.drive_root / ".copilot_sentinel"
    if not sentinel.exists():
        sentinel.write_text("created by comfyui_playground", encoding="utf-8")
    return sentinel


def detect_gpu() -> Dict[str, str]:
    """Return a summary of GPU availability."""
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,nounits,noheader"],
                                check=True, capture_output=True, text=True)
        name, memory = result.stdout.strip().split(",")
        return {"available": "true", "name": name.strip(), "memory_gb": str(round(int(memory.strip()) / 1024, 2))}
    except Exception:
        return {"available": "false"}


def get_env_summary(config: PlaygroundConfig) -> Dict[str, str]:
    """Produce a JSON-serialisable summary used by the notebook control board."""
    summary = {
        "drive_root": str(config.drive_root),
        "models_dir": str(config.models_dir),
        "tunnel_preference": config.tunnel_preference,
        "env_vars": list(config.env_vars.keys()),
    }
    summary.update({"gpu": detect_gpu()})
    return summary
