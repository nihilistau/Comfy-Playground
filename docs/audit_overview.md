# Notebook Audit & Dependency Overview

## Cell-to-Feature Map (High Level)

| Section | Purpose | Notes |
| --- | --- | --- |
| README / Orientation | Explain purpose, env vars, general steps | Needs executive summary & TOC anchors |
| Configuration + Options | Define Drive paths and toggles | Duplicated printing logic in multiple later cells |
| Drive Mount | Mounts Google Drive and ensures directory structure | Good sentinel creation; lacks retry messaging |
| Endpoint Helper + Health Check | Configure API base, run status ping | Spread across two cells; mixed display/logic |
| Install / Update | Clone ComfyUI, create venv, install deps | Large cell mixing setup + logging; no progress UI |
| Model Manager | Commented wget blocks | Needs structured manifest + queue integration |
| Tunnel Starters | Cloudflared / LocalTunnel commands | Minimal validation; no auto-poll of URL |
| Demo Blocks (T2I/I2I/etc.) | Widget-based generation scaffolds | Many rely on global state, limited modular reuse |
| Advanced (LoRA, training) | Additional flows + training notes | Several sections partially stubbed |
| Utility Checks | Torch verify, GPU info, cleanup helpers | Spread out, inconsistent messaging |

## Environment Variables Referenced

- `DRIVE_ROOT`
- `CIVITAI_API_TOKEN`
- `HUGGINGFACE_TOKEN`
- `COMFYUI_PUBLIC_URL`
- `COMFYUI_API_KEY`
- `GOOGLE_API_KEY`

## User Stories Captured

1. **Install & Bootstrap**: Mount Drive, install ComfyUI, start tunnels, confirm health.
2. **Model Management**: Queue and download models/assets into Drive.
3. **Programmatic Generation**: Launch text/image/video pipelines via reusable flows.
4. **Queue Operations**: Monitor, pause/resume, retry ComfyUI jobs.
5. **Voice/Audio Workflows**: Configure STT/TTS models, route outputs to flows.
6. **Training & Advanced Ops**: Launch LoRA/Kohya routines against Drive datasets.
7. **Maintenance**: Clean caches, rotate manifests, capture diagnostics for debugging.

## Dependency Diagram (ASCII)

```
[Notebook UI]
     |-- calls --> [src/notebook_ui]
     |-- imports -> [src/env] -- reads --> [.env/.yaml]
     |-- uses ----> [src/download] <--> [Drive Storage]
     |-- delegates -> [src/flows] ---> [ComfyUI API]
     |-- delegates -> [src/voice] ---> [STT/TTS Providers]
     |-- delegates -> [src/queue] ---> [sqlite queue db]
     |-- delegates -> [src/templates] ---> [Drive templates dir]
     |-- delegates -> [src/security] ---> [Secrets handling]
                             |
                             `--> [src/diag] -> Support bundles
```

## Follow-Up

- Tag redundant sections for removal during notebook refactor.
- Align future cells with the user stories list to keep the flow linear.
- Ensure env var usage funnels through `src/env` before exposing in UI.
