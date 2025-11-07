from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from typing import Callable, Dict, Optional

import requests

CHUNK_SIZE = 1024 * 1024
ProgressCallback = Callable[[Dict[str, float]], None]


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def preview_url(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> Dict[str, str]:
    headers = headers or {}
    try:
        response = requests.head(url, allow_redirects=True, headers=headers, timeout=timeout)
        if response.status_code >= 400 or "content-length" not in response.headers:
            response = requests.get(url, allow_redirects=True, headers=headers, stream=True, timeout=timeout)
        return {
            "status_code": str(response.status_code),
            "final_url": response.url,
            "content_length": response.headers.get("content-length", "unknown"),
            "content_type": response.headers.get("content-type", "unknown"),
        }
    except Exception as exc:  # pragma: no cover - network errors depend on runtime
        return {"status_code": "error", "error": str(exc)}


def normalize_server_hash(headers: Dict[str, str]) -> Optional[str]:
    if not headers:
        return None
    for key in ("ETag", "Etag", "etag"):
        if key in headers:
            return headers[key].strip('"')
    if "x-goog-hash" in headers:
        parts = [p.strip() for p in headers["x-goog-hash"].split(",")]
        for part in parts:
            if part.startswith("md5="):
                return part.split("=", 1)[1]
        return parts[0]
    return headers.get("content-md5")


def stream_file(
    url: str,
    dest: Path,
    *,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 60,
    expected_sha256: Optional[str] = None,
    progress_cb: Optional[ProgressCallback] = None,
) -> Dict[str, str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest.with_suffix(dest.suffix + ".part")
    resume_pos = temp_path.stat().st_size if temp_path.exists() else 0
    request_headers = headers.copy() if headers else {}
    if resume_pos:
        request_headers["Range"] = f"bytes={resume_pos}-"
    with requests.get(url, stream=True, headers=request_headers, timeout=timeout) as response:
        response.raise_for_status()
        total = response.headers.get("content-length")
        total_bytes = int(total) + resume_pos if total and total.isdigit() else None
        mode = "ab" if resume_pos else "wb"
        downloaded = resume_pos
        with temp_path.open(mode) as fh:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:
                    continue
                fh.write(chunk)
                downloaded += len(chunk)
                if progress_cb:
                    progress_cb({
                        "downloaded_bytes": downloaded,
                        "total_bytes": total_bytes or -1,
                        "progress": downloaded / total_bytes if total_bytes else -1,
                    })
    shutil.move(str(temp_path), str(dest))
    sha256 = compute_sha256(dest)
    if expected_sha256 and sha256 != expected_sha256:
        dest.unlink(missing_ok=True)
        raise ValueError(f"SHA256 mismatch: expected {expected_sha256}, got {sha256}")
    metadata = {
        "path": str(dest),
        "sha256": sha256,
           "server_hash": normalize_server_hash(response.headers),
    }
    return metadata
