ComfyUI Colab Playground

This repository contains a Colab-ready notebook that mounts Google Drive, installs ComfyUI directly into the active runtime (while keeping assets on Drive), and provides a set of cells to safely resolve and download models from Civitai/HuggingFace with Drive persistence.

Quick run order

1. Mount Google Drive in Colab.
2. Run the secure token cell and provide CIVITAI_API_TOKEN.
3. Ensure the manifest file `manifests/civitai_model_manifests.json` exists under `DRIVE_ROOT` (default: `/content/drive/MyDrive/ComfyUI`). Use the Manifest locator helper if needed.
4. Run the Batch manifest resolver to populate final filenames and metadata.
5. Use the Downloader Panel UI to select one or more model entries and Start Queue.
6. After download, run the Post-download integrity checker and inspect `manifests/download_summary.json`.

Notes & safety

- The notebook includes guarded download templates and requires explicit preview/confirm steps for downloads.
- Tokens are read from environment variables in-memory. Do not paste tokens into long-lived cells.
- Colab sessions can time out; background scheduler and long-running downloads may be interrupted.

Advanced features

- HTML-based Downloader Panel with Start/Stop callbacks.
- Background queue worker with retries and server-hash heuristics.
- Nightly manifest resolver scheduler (runs periodically while the session is active).
- Optional upload helpers for S3/GCS to record artifact locations.

