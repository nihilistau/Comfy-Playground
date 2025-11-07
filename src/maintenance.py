from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable

from .config import PlaygroundConfig

# Rare comment: include OS environment so validation mirrors runtime behaviour.


def prune_artifacts(*, older_than_hours: int = 24, config: PlaygroundConfig | None = None) -> int:
    cfg = config or PlaygroundConfig.load()
    cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
    removed = 0
    for path in cfg.artifacts_dir.glob("**/*"):
        if path.is_file() and datetime.utcfromtimestamp(path.stat().st_mtime) < cutoff:
            path.unlink()
            removed += 1
    return removed


def rotate_manifest_backups(max_backups: int = 5, *, config: PlaygroundConfig | None = None) -> Dict[str, int]:
    cfg = config or PlaygroundConfig.load()
    summary: Dict[str, int] = {"rotated": 0}
    for manifest in cfg.manifests_dir.glob("*.json"):
        backup_dir = manifest.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        target = backup_dir / f"{manifest.stem}_{timestamp}.json"
        shutil.copy2(manifest, target)
        summary["rotated"] += 1
        backups = sorted(backup_dir.glob(f"{manifest.stem}_*.json"))
        for stale in backups[:-max_backups]:
            stale.unlink()
    return summary


def validate_env_vars(required: Iterable[str], *, config: PlaygroundConfig | None = None) -> Dict[str, bool]:
    cfg = config or PlaygroundConfig.load()
    merged: Dict[str, str] = {}
    merged.update(cfg.env_vars)
    merged.update({key: value for key, value in os.environ.items() if key not in merged})
    return {name: bool(merged.get(name)) for name in required}
