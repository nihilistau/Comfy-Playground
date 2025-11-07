from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import PlaygroundConfig


def _ensure_flow_dir(config: PlaygroundConfig) -> Path:
    flow_dir = config.drive_root / "flows"
    flow_dir.mkdir(parents=True, exist_ok=True)
    return flow_dir


def compose_flow(
    prompt: str,
    *,
    model_key: Optional[str] = None,
    sampler: str = "DDIM",
    steps: int = 20,
    seed: int = -1,
    lora: Optional[str] = None,
    upscaler: Optional[str] = None,
    fmt: str = "comfyui",
    config: Optional[PlaygroundConfig] = None,
) -> tuple[str, Dict[str, Any]]:
    """Compose a minimal ComfyUI flow JSON and persist it to Drive."""
    cfg = config or PlaygroundConfig.load()
    flow_dir = _ensure_flow_dir(cfg)
    timestamp = int(time.time())
    flow = {
        "meta": {
            "prompt": prompt,
            "created_at": timestamp,
            "format": fmt,
            "model": model_key,
        },
        "nodes": [
            {
                "id": "txt2img",
                "type": "StableDiffusion",
                "params": {
                    "prompt": prompt,
                    "sampler": sampler,
                    "steps": steps,
                    "seed": seed,
                    "model": model_key,
                    "lora": lora,
                    "upscaler": upscaler,
                },
            }
        ],
    }
    path = flow_dir / f"flow_{timestamp}.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump(flow, fh, indent=2)
    return str(path), flow


def load_flow_from_drive(identifier: str, *, config: Optional[PlaygroundConfig] = None) -> Dict[str, Any]:
    cfg = config or PlaygroundConfig.load()
    flow_dir = _ensure_flow_dir(cfg)
    target = flow_dir / identifier
    if not target.exists():
        raise FileNotFoundError(target)
    with target.open("r", encoding="utf-8") as fh:
        return json.load(fh)
