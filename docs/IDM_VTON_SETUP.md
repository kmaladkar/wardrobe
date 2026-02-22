# IDM-VTON local setup

Use [IDM-VTON](https://github.com/yisol/IDM-VTON) (ECCV 2024) for diffusion-based virtual try-on by running it locally and pointing the Wardrobe app at it.

## 1. Clone and create environment

From the [official repo](https://github.com/yisol/IDM-VTON):

```bash
git clone https://github.com/yisol/IDM-VTON.git
cd IDM-VTON

conda env create -f environment.yaml
conda activate idm
```

## 2. Download checkpoints

You need human parsing and related checkpoints for the Gradio demo.

1. Download from the links in the repo:
   - **Human parsing**: [ckpt/humanparsing](https://huggingface.co/spaces/yisol/IDM-VTON/tree/main/ckpt) – place `parsing_atr.onnx` and `parsing_lip.onnx` in `ckpt/humanparsing/`
   - **DensePose**: [ckpt/densepose](https://huggingface.co/spaces/yisol/IDM-VTON/tree/main/ckpt) – place `model_final_162be9.pkl` in `ckpt/densepose/`
   - **OpenPose**: [ckpt/openpose](https://huggingface.co/spaces/yisol/IDM-VTON/tree/main/ckpt) – place `body_pose_model.pth` in `ckpt/openpose/ckpts/`

2. Target layout:

```
IDM-VTON/
ckpt/
  densepose/
    model_final_162be9.pkl
  humanparsing/
    parsing_atr.onnx
    parsing_lip.onnx
  openpose/
    ckpts/
      body_pose_model.pth
```

The main model weights (UNet, VAE, etc.) are loaded from Hugging Face (`yisol/IDM-VTON`) when you run the app.

## 3. Run the Gradio demo

From inside the IDM-VTON repo:

```bash
conda activate idm
python gradio_demo/app.py
```

By default the app runs at **http://127.0.0.1:7860**. Leave this running.

## 4. Point Wardrobe at your local IDM-VTON

Set the try-on URL to your local server and use the diffusion script:

**Option A – env var (recommended)**

In your Wardrobe `.env` (or shell):

```bash
# Use local IDM-VTON Gradio server
DIFFUSION_TRYON_URL=http://127.0.0.1:7860
TRY_ON_SCRIPT=/path/to/wardrobe/scripts/run_diffusion_tryon.py
```

Use an absolute path for `TRY_ON_SCRIPT` if you start the backend from another directory.

**Option B – TRY_ON_COMMAND**

```bash
TRY_ON_COMMAND="python /path/to/wardrobe/scripts/run_diffusion_tryon.py --human {human} --garment {garment} --output {output} --category {category}"
```

Ensure `DIFFUSION_TRYON_URL=http://127.0.0.1:7860` is set so the script talks to your local app.

## 5. Run the Wardrobe backend

From the Wardrobe project root:

```bash
uv sync --extra tryon --extra diffusion-tryon
uv run wardrobe
```

When you use the Today tab (or any try-on), the backend will call `run_diffusion_tryon.py`, which will use your local IDM-VTON at port 7860.

## Summary

| Step | Action |
|------|--------|
| 1 | Clone [yisol/IDM-VTON](https://github.com/yisol/IDM-VTON), `conda env create -f environment.yaml`, `conda activate idm` |
| 2 | Download ckpt files into `ckpt/densepose`, `ckpt/humanparsing`, `ckpt/openpose/ckpts` |
| 3 | Run `python gradio_demo/app.py` (server on port 7860) |
| 4 | Set `DIFFUSION_TRYON_URL=http://127.0.0.1:7860` and `TRY_ON_SCRIPT=.../run_diffusion_tryon.py` for Wardrobe |
| 5 | Start Wardrobe backend with `uv run wardrobe` |

If `DIFFUSION_TRYON_URL` is not set, the script falls back to the public Hugging Face Space (or Pillow composite if that fails).
