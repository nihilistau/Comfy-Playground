"""ComfyUI Playground core package."""

from .config import PlaygroundConfig
from . import download as download_module
from .flows import composer as composer_module
from .flows.composer import compose_flow
from .queue import api as queue_module
from .queue.api import dequeue, enqueue, init_db, list_items
from .templates import api as templates_module
from .templates.api import get_prompt_templates, save_prompt_templates
from .security.api import set_api_key
from .download.manager import DownloadManager
from .diag import export_diagnostics_bundle
from .maintenance import prune_artifacts, rotate_manifest_backups, validate_env_vars

composer = composer_module
queue = queue_module
templates = templates_module
downloader = download_module

__all__ = [
    "PlaygroundConfig",
    "compose_flow",
    "enqueue",
    "dequeue",
    "list_items",
    "init_db",
    "get_prompt_templates",
    "save_prompt_templates",
    "set_api_key",
    "DownloadManager",
    "export_diagnostics_bundle",
    "composer",
    "queue",
    "templates",
    "downloader",
    "prune_artifacts",
    "rotate_manifest_backups",
    "validate_env_vars",
]
