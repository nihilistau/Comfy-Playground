# Comfy-Playground

Example diffusion AI controller for Colab, now expanded into a Drive-backed ComfyUI playground.

Local Colab-first toolkit for installing, monitoring, and extending ComfyUI via Drive-backed state. The refresh introduces a modular `src/` package, richer notebooks (`comfyui_playground.ipynb`, `dashboard.ipynb`), and CLI helpers for manifests, queue status, diagnostics, and flow regression.

## Highlights

- **Control Board & Dashboard**: Real-time Drive/queue/voice summaries, auto-refresh toggles, ComfyUI health probe, and queue controls.
- **Modular src/**: Packages for config, env, downloads, flows (with regression harness), voice benchmarking, templates, queue orchestration, maintenance, and diagnostics.
- **Audio Benchmark Suite**: Measure STT/TTS latency with pandas-backed reports.
- **Maintenance Utilities**: Prune stale artifacts, rotate manifest backups, and validate critical env vars before heavy runs.
- **Stretch Integrations**: Hooks for future Hugging Face inference, GPU estimation, and session persistence (see TODO list).

## Quick local test run

Install dependencies and execute the pseudo-test suite:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

The notebooks rely on Google Drive paths; when running locally ensure `DRIVE_ROOT` points to a writable directory (e.g. `set DRIVE_ROOT=d:\tmp\comfyui`).

## Guided install script

For a repeatable Drive bootstrap, run the installer from the repository root:

```powershell
python scripts/install_playground.py --install-deps --overwrite
```

Flags worth knowing:
- `--drive-root` sets the Drive destination (defaults to `/content/drive/MyDrive/ComfyUI`).
- `--target` controls where the project files are copied (defaults to `<drive-root>/playground`).
- `--include-tests` copies the regression test suite for local smoke checks.

After the script completes, open `notebooks/comfyui_playground.ipynb` inside the copied workspace and follow the Control Board.

## Launching from GitHub / Colab

Once this project lives on GitHub, add a Colab badge to the README so collaborators can spin it up instantly:

```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<your-org>/<your-repo>/blob/main/notebooks/comfyui_playground.ipynb)
```

Replace `<your-org>/<your-repo>` with the repository slug. The badge will clone the repo inside Colab, and the included install script can finish provisioning the Drive-backed environment.
