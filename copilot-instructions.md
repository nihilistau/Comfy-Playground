# Copilot instructions — ComfyUI / Colab playground

This file tells an AI coding agent what matters in this workspace and how to be productive quickly.

Short contract
- Inputs: Google Drive mounted at `/content/drive/MyDrive`, secrets: `CIVITAI_API_TOKEN`, `GOOGLE_API_KEY`, optional `HUGGINGFACE_TOKEN`.
- Outputs: a master Colab notebook (`notebooks/comfyui_playground.ipynb`) that installs/loads ComfyUI into Drive and provides modular demo cells.
- Error modes: missing tokens, insufficient Drive space, GPU unavailable, HTTP download failures (403/429).

Drive layout (create these paths when mounting)
- `MyDrive/ComfyUI/`
- `MyDrive/ComfyUI/models/loras/`
- `MyDrive/ComfyUI/models/gguf/`
- `MyDrive/ComfyUI/models/stable-diffusion/`
- `MyDrive/ComfyUI/artifacts/`
- `MyDrive/ComfyUI/config/`

Env vars and conventions (use these exact names)
- `CIVITAI_API_TOKEN` — used with wget for Civitai downloads.
- `GOOGLE_API_KEY` — optional; used if programmatic Drive auth is required.
- `HUGGINGFACE_TOKEN` — optional; use for huggingface model downloads.

Example Civitai download pattern (use verbatim):
```
!wget "https://civitai.com/api/download/models/1624818?type=Model&format=SafeTensor&size=full&fp=fp16&CIVITAI_TOKEN=$CIVITAI_API_TOKEN" --content-disposition -P "./models/loras/"
```
Always download directly into Drive so models persist between Colab sessions.

Notebook structure an agent should produce (concise cell list)
1) Mount Drive — validate by creating and reading a sentinel file.
2) Options toggles (checkboxes): install_comfyui, update_comfyui, install_plugins, start_cloudflared, start_localtunnel, run_demo_workflows.
3) Install/update ComfyUI (idempotent) — clone/sync into Drive and install requirements into a venv under Drive.
4) Model manager — commented civitai/hf download examples and quick-download helpers.
5) Start ComfyUI — two cells: Cloudflared and Localtunnel. Each must print a public URL and PID and be safe to re-run.
6) T2I demo — ipywidgets GUI: prompt, negative prompt, steps, cfg, sampler, model dropdown (populated from Drive), batch size, width/height, upscale toggle. Save to `artifacts/` and show inline preview.
7) I2I demo — upload reference + prompt + strength; preview and save.
8) Multi-LORA pipeline — select multiple LORAs (checkboxes) and run chained nodes (base gen -> blend LORAs -> upscale -> facedetailer). All nodes optional.
9) T2V / I2V cell (Wan2.1) — model selection (gguf), frames, steps/frame, motion smoothing, encoder options, save mp4.
10) LORA training cell — dataset prep, kohya-style training (reference cell), checkpoint output into `models/loras/` on Drive.

Testing & debugging tips for automations
- After starting a tunnel, poll the URL for HTTP 200 before reporting success.
- Detect GPU with `!nvidia-smi` and annotate cells that will be slow on T4.
- Use a sentinel file to assert Drive persistence across sessions.

References to mirror/adapt
- ComfyUI manager notebook: https://colab.research.google.com/github/ltdrdata/ComfyUI-Manager/blob/main/notebooks/comfyui_colab_with_manager.ipynb
- kohya_ss colab for training flow: https://colab.research.google.com/github/camenduru/kohya_ss-colab/blob/main/kohya_ss_colab.ipynb
- Wan2.1 examples the user provided for T2V/I2V workflows.

Merging guidance (if this file already exists)
- Preserve unique examples and concrete commands. Replace outdated env names with the ones above. Add Drive layout and the exact Civitai wget example.

Next questions for the user (choose before I generate the Colab notebook)
1) Confirm Drive root (default `MyDrive/ComfyUI`).
2) Confirm env var names or change them now.
3) Provide 3 preferred model IDs (one HF, two Civitai) to include as commented download examples.

If you want the Colab notebook created now, reply "Create notebook" and I'll produce `notebooks/comfyui_playground.ipynb` next, with modular, commented cells and the toggle pattern requested.
