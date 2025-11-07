"""Bootstrap the ComfyUI Playground into a Drive-backed workspace.

This script prepares the directory layout expected by the notebooks, copies the
project sources into the target location, and optionally installs Python
dependencies. It is safe to re-run with ``--overwrite`` to refresh a staging
area while keeping the Drive folders intact.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Paths relative to the repository root that should be copied for a playground install
CORE_PATHS: Tuple[str, ...] = (
    "src",
    "cli.py",
    "composer.py",
    "downloader.py",
    "manifest_resolver.py",
    "queue.py",
    "templates.py",
    "security.py",
    "__init__.py",
    "requirements.txt",
    "README.md",
    "comfyui_playground.ipynb",
    "dashboard.ipynb",
    "docs",
)

IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc", ".ipynb_checkpoints")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the ComfyUI Playground into a Drive workspace")
    parser.add_argument(
        "--drive-root",
        default="/content/drive/MyDrive/ComfyUI",
        help="Drive root to provision (defaults to the standard Colab path)",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Optional target directory for project files (defaults to <drive-root>/playground)",
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install the Python dependencies using pip after copying files",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test_*.py files and notebooks for local validation",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the existing target contents instead of aborting",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return REPO_ROOT


def ensure_drive_layout(drive_root: Path) -> None:
    from src.config import PlaygroundConfig

    cfg = PlaygroundConfig(drive_root=drive_root)
    cfg.ensure_directories()
    try:
        cfg.save()
    except RuntimeError:
        # PyYAML is optional; saving the config is nice-to-have but not required
        pass


def copy_paths(paths: Iterable[str], destination: Path, include_tests: bool, overwrite: bool) -> None:
    root = repo_root()
    destination.mkdir(parents=True, exist_ok=True)
    for relative in paths:
        src = root / relative
        dest = destination / relative
        if src.is_dir():
            if dest.exists() and overwrite:
                shutil.rmtree(dest)
            shutil.copytree(src, dest, dirs_exist_ok=True, ignore=IGNORE_PATTERNS)
        else:
            if dest.exists() and overwrite:
                dest.unlink()
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    if include_tests:
        for test_file in root.glob("test_*.py"):
            dest = destination / test_file.name
            if dest.exists() and overwrite:
                dest.unlink()
            shutil.copy2(test_file, dest)


def install_dependencies(requirements_path: Path) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])


def main() -> None:
    args = parse_args()
    drive_root = Path(args.drive_root).expanduser().resolve()
    target = Path(args.target).expanduser().resolve() if args.target else (drive_root / "playground")

    print(f"Drive root: {drive_root}")
    print(f"Project target: {target}")

    ensure_drive_layout(drive_root)

    if target.exists() and not args.overwrite:
        raise SystemExit(
            f"Target {target} already exists. Re-run with --overwrite to refresh the playground contents."
        )

    copy_paths(CORE_PATHS, target, include_tests=args.include_tests, overwrite=args.overwrite)

    if args.install_deps:
        print("Installing Python dependencies via pip...")
        install_dependencies(target / "requirements.txt")

    notebooks_dir = target / "notebooks"
    notebooks_dir.mkdir(parents=True, exist_ok=True)
    for notebook_name in ("comfyui_playground.ipynb", "dashboard.ipynb"):
        src = target / notebook_name
        dst = notebooks_dir / notebook_name
        shutil.copy2(src, dst)

    print("\nPlayground ready.")
    print("Next steps:")
    print("  1. Mount Google Drive in Colab (if running remotely).")
    print(f"  2. Set the DRIVE_ROOT env var to {drive_root} before launching notebooks.")
    print(f"  3. Open {notebooks_dir / 'comfyui_playground.ipynb'} in Colab and follow the Control Board.")


if __name__ == "__main__":
    main()
