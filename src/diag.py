from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict

from .config import PlaygroundConfig
from .queue import list_items
from .templates import get_prompt_templates


def export_diagnostics_bundle(*, config: PlaygroundConfig | None = None) -> Path:
    cfg = config or PlaygroundConfig.load()
    cfg.ensure_directories()
    bundle_dir = Path(tempfile.mkdtemp(prefix="comfy_diag_"))
    info: Dict[str, object] = {
        "drive_root": str(cfg.drive_root),
        "queue": list_items(config=cfg),
        "templates": get_prompt_templates(config=cfg),
    }
    bundle_info = bundle_dir / "diagnostics.json"
    bundle_info.write_text(json.dumps(info, indent=2), encoding="utf-8")
    archive = shutil.make_archive(str(bundle_dir), "zip", bundle_dir)
    shutil.rmtree(bundle_dir, ignore_errors=True)
    return Path(archive)
