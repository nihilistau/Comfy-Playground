from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from queue import Queue
from typing import Callable, Dict, Iterable, Optional

from ..config import PlaygroundConfig
from .stream import ProgressCallback, compute_sha256, preview_url, stream_file


@dataclass
class DownloadItem:
    url: str
    destination: str
    sha256: Optional[str] = None
    headers: Optional[Dict[str, str]] = None


@dataclass
class DownloadManifest:
    items: Iterable[DownloadItem]

    @classmethod
    def from_json(cls, path: Path) -> "DownloadManifest":
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        entries = [DownloadItem(**item) for item in payload.get("items", [])]
        return cls(entries)


@dataclass
class DownloadManager:
    config: PlaygroundConfig = field(default_factory=PlaygroundConfig.load)
    progress_callback: Optional[ProgressCallback] = None
    _queue: Queue = field(default_factory=Queue, init=False)

    def add_item(self, item: DownloadItem | Dict[str, str]) -> None:
        if isinstance(item, dict):
            payload = {k: item.get(k) for k in ["url", "destination", "sha256", "headers"] if k in item}
            item = DownloadItem(**payload)
        self._queue.put(item)

    def add_manifest(self, manifest: DownloadManifest) -> None:
        for item in manifest.items:
            self.add_item(item)

    def run(self) -> None:
        while not self._queue.empty():
            item: DownloadItem = self._queue.get()
            dest = self.config.drive_root / item.destination
            stream_file(
                item.url,
                dest,
                headers=item.headers,
                expected_sha256=item.sha256,
                progress_cb=self.progress_callback,
            )
            self._queue.task_done()

    def run_async(self) -> threading.Thread:
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread

    def preview(self, url: str) -> Dict[str, str]:
        return preview_url(url)

    def verify(self, path: Path) -> Dict[str, str]:
        return {"path": str(path), "sha256": compute_sha256(path)}
