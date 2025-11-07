"""Command line interface for the ComfyUI playground."""

import argparse
import json
from pathlib import Path

from src import DownloadManager, compose_flow
from src.diag import export_diagnostics_bundle
from src.queue import list_items


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="comfyui-playground")
    sub = parser.add_subparsers(dest="command", required=True)

    compose = sub.add_parser("compose-run", help="Compose a flow JSON and persist to Drive")
    compose.add_argument("--prompt", "-p", default="A test prompt")
    compose.add_argument("--model", "-m", default=None)
    compose.add_argument("--steps", type=int, default=20)

    queue = sub.add_parser("queue-status", help="Print a summary of the queue state")
    queue.add_argument("--status", choices=["pending", "processing", "failed", "done"], default=None)

    manifest = sub.add_parser("manifest-check", help="Validate a manifest JSON file")
    manifest.add_argument("path", type=Path)

    download = sub.add_parser("download-manifest", help="Download all items in a manifest")
    download.add_argument("path", type=Path)

    diag = sub.add_parser("diag", help="Generate a diagnostics bundle")
    diag.add_argument("--output", type=Path, default=None)

    return parser


def _cmd_compose(args: argparse.Namespace) -> None:
    path, _ = compose_flow(args.prompt, model_key=args.model, steps=args.steps)
    print("Composed flow at", path)


def _cmd_queue(args: argparse.Namespace) -> None:
    rows = list_items(status=args.status)
    print(json.dumps(rows, indent=2))


def _cmd_manifest(args: argparse.Namespace) -> None:
    data = json.loads(args.path.read_text(encoding="utf-8"))
    keys = {"url", "destination"}
    missing = [idx for idx, item in enumerate(data.get("items", [])) if not keys.issubset(item)]
    if missing:
        raise SystemExit(f"Manifest validation failed; missing keys in rows: {missing}")
    print(f"Manifest {args.path} OK ({len(data.get('items', []))} items)")


def _cmd_download(args: argparse.Namespace) -> None:
    manifest_data = json.loads(args.path.read_text(encoding="utf-8"))
    items = manifest_data.get("items", [])
    manager = DownloadManager()
    manager.progress_callback = lambda state: print(
        f"downloaded {state['downloaded_bytes']} / {state.get('total_bytes', 'unknown')}"
    )
    for item in items:
        manager.add_item(item)
    manager.run()


def _cmd_diag(args: argparse.Namespace) -> None:
    bundle = export_diagnostics_bundle()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(bundle.read_bytes())
        print("Diagnostics bundle written to", args.output)
    else:
        print(bundle)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    command = args.command.replace("-", "_")
    handler = globals().get(f"_cmd_{command}")
    if handler is None:
        parser.error(f"Unknown command {args.command}")
    handler(args)


if __name__ == "__main__":
    main()
