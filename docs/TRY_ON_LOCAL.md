# Local open-source virtual try-on

The app runs try-on **locally**—no Replicate or other paid APIs.

## Options

### 1. Built-in composite (default with script)

Uses a simple overlay: garment image is scaled and pasted onto the avatar’s upper body. Good for testing.

1. Install the tryon extra (Pillow):
   ```bash
   uv sync --extra tryon
   ```
2. Set the script in your env (e.g. `.env`):
   ```
   TRY_ON_SCRIPT=scripts/run_local_tryon.py
   ```
   Use an absolute path if you run the server from another directory, e.g.:
   ```
   TRY_ON_SCRIPT=/path/to/wardrobe/scripts/run_local_tryon.py
   ```
3. Restart the backend. Today tab try-on will use this script.

### 2. Diffusion try-on via Hugging Face (run_diffusion_tryon.py)

Uses a **diffusion model** (IDM-VTON) by calling the [Hugging Face Space](https://huggingface.co/spaces/yisol/IDM-VTON) via `gradio_client`. If the Space is unavailable or the call fails, the script falls back to the Pillow composite.

1. Install the diffusion-tryon extra:
   ```bash
   uv sync --extra tryon --extra diffusion-tryon
   ```
2. Optional: set `HF_TOKEN` in your env if the Space is gated (get a token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)).
3. Set the script in your env:
   ```
   TRY_ON_SCRIPT=scripts/run_diffusion_tryon.py
   ```
4. Optional: use a different Space: `DIFFUSION_TRYON_SPACE=other/user-space`

### 3. IDM-VTON (run locally)

Run [IDM-VTON](https://github.com/yisol/IDM-VTON) locally and use it with the same `run_diffusion_tryon.py` script.

1. Follow **[docs/IDM_VTON_SETUP.md](IDM_VTON_SETUP.md)** to clone the repo, create the conda env, download checkpoints, and run their Gradio demo (`python gradio_demo/app.py`).
2. Set in your env:
   ```
   DIFFUSION_TRYON_URL=http://127.0.0.1:7860
   TRY_ON_SCRIPT=/path/to/wardrobe/scripts/run_diffusion_tryon.py
   ```
3. Start the Wardrobe backend. Try-on will use your local IDM-VTON server.

### 4. No script/command

If neither `TRY_ON_SCRIPT` nor `TRY_ON_COMMAND` is set, try-on returns the **avatar image** as the “result” so the app still works; you just don’t see a real try-on.

## Env reference

| Variable                   | Description |
|---------------------------|-------------|
| `TRY_ON_SCRIPT`            | Path to a Python script. Backend runs: `python <script> --human <path> --garment <path> --output <path> [--category <cat>]`. Script must write the result to `--output`. |
| `TRY_ON_COMMAND`           | Shell command. Use placeholders `{human}`, `{garment}`, `{output}`, `{category}`; backend replaces them and runs the command. Result must be written to `{output}`. |
| `HF_TOKEN`                 | Optional. Hugging Face token for gated Spaces (used by `run_diffusion_tryon.py`). |
| `DIFFUSION_TRYON_SPACE`    | Optional. HF Gradio Space when not using a local server (default: `yisol/IDM-VTON`). |
| `DIFFUSION_TRYON_URL`     | Optional. **Local** IDM-VTON Gradio server URL (e.g. `http://127.0.0.1:7860`). When set, the script uses this instead of the HF Space. See [IDM_VTON_SETUP.md](IDM_VTON_SETUP.md). |

Script/command runs with a 5-minute timeout. On failure, the backend falls back to returning the avatar as the result.
