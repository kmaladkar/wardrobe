#!/usr/bin/env python3
"""
Diffusion-based virtual try-on using IDM-VTON: local Gradio server or Hugging Face Space.

  python scripts/run_diffusion_tryon.py --human person.jpg --garment cloth.jpg --output result.jpg --category top

Setup (choose one):
  - Local: clone https://github.com/yisol/IDM-VTON, install, run gradio_demo/app.py, set DIFFUSION_TRYON_URL=http://127.0.0.1:7860
  - HF Space: set HF_TOKEN if gated; script uses yisol/IDM-VTON by default when DIFFUSION_TRYON_URL is not set.

Requires: gradio_client (uv sync --extra diffusion-tryon), pillow for fallback (uv sync --extra tryon).
See docs/IDM_VTON_SETUP.md for full local setup.
"""

import argparse
import os
import sys
from pathlib import Path

# Project root for imports when fallback runs
_ROOT = Path(__file__).resolve().parents[1]
if _ROOT not in sys.path:
    sys.path.insert(0, str(_ROOT))
_SRC = _ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Local IDM-VTON server (e.g. http://127.0.0.1:7860) or HF Space name
TRYON_URL = os.environ.get("DIFFUSION_TRYON_URL", "").strip()
TRYON_SPACE = os.environ.get("DIFFUSION_TRYON_SPACE", "yisol/IDM-VTON")


def _run_gradio_tryon(human_path: Path, garment_path: Path, output_path: Path, category: str) -> bool:
    """Run try-on via Gradio: local URL (IDM-VTON) or HF Space. Returns True if output was written."""
    try:
        from gradio_client import Client
    except ImportError:
        return False

    # Prefer local IDM-VTON server; otherwise use HF Space
    token = os.environ.get("HF_TOKEN", "").strip() or None
    if TRYON_URL:
        client = Client(TRYON_URL)
    else:
        client = Client(TRYON_SPACE, token=token)

    # Space API: tryon(imgs, garm_img, garment_des, is_checked, is_checked_crop, denoise_steps, seed)
    # imgs can be dict with "background" (person image path) and "layers" (mask or None for auto)
    try:
        result = client.predict(
            str(human_path),  # some Spaces accept path for ImageEditor background
            str(garment_path),
            "upper body garment",  # garment_des
            True,   # is_checked = use auto mask
            False,  # is_checked_crop
            30,     # denoise_steps
            42,     # seed
            api_name="/tryon",
        )
    except Exception:
        # Try with dict for ImageEditor (background = person image)
        try:
            result = client.predict(
                {"background": str(human_path), "layers": None, "composite": None},
                str(garment_path),
                "upper body garment",
                True,
                False,
                30,
                42,
                api_name="/tryon",
            )
        except Exception:
            return False

    # Result can be (output_image, mask_image) tuple or a single output
    if result is None:
        return False
    out_img = result[0] if isinstance(result, (list, tuple)) else result
    if out_img is None:
        return False
    # gradio_client may return a file path (str) or a URL
    if isinstance(out_img, str) and Path(out_img).is_file():
        Path(out_img).rename(output_path)
        return True
    if isinstance(out_img, str) and out_img.startswith("http"):
        import urllib.request
        urllib.request.urlretrieve(out_img, output_path)
        return True
    return False


def _run_pillow_fallback(human_path: Path, garment_path: Path, output_path: Path, category: str) -> None:
    """Pillow composite fallback (same logic as run_local_tryon.py)."""
    from PIL import Image, ImageFilter

    person = Image.open(human_path).convert("RGB")
    garment = Image.open(garment_path).convert("RGB")
    pw, ph = person.size
    gw, gh = garment.size

    scale_w = pw * 0.45
    scale = scale_w / max(1, gw)
    target_w = max(64, min(pw, int(gw * scale)))
    target_h = max(64, min(ph, int(gh * scale)))
    feather = max(8, min(40, target_w // 6))

    if category in ("top", "jacket"):
        x, y = (pw - target_w) // 2, max(0, int(ph * 0.12))
    elif category == "bottom":
        x = (pw - target_w) // 2
        y = max(int(ph * 0.35), ph - target_h - int(ph * 0.1))
    elif category == "footwear":
        target_w = max(64, int(pw * 0.5))
        target_h = max(32, int(ph * 0.15))
        x, y = (pw - target_w) // 2, ph - target_h - int(ph * 0.02)
        feather = max(6, target_w // 10)
    else:
        x, y = (pw - target_w) // 2, max(0, int(ph * 0.12))

    garment_scaled = garment.resize((target_w, target_h), Image.Resampling.LANCZOS)
    box = (x, y, x + target_w, y + target_h)

    mask = Image.new("L", (target_w, target_h), 0)
    inner = (feather, feather, target_w - feather, target_h - feather)
    for ty in range(target_h):
        for tx in range(target_w):
            if inner[0] <= tx < inner[2] and inner[1] <= ty < inner[3]:
                alpha = 255
            else:
                dx = min(tx, target_w - 1 - tx, ty, target_h - 1 - ty, feather)
                alpha = int(255 * min(1.0, dx / max(1, feather)))
            mask.putpixel((tx, ty), alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=feather // 2))
    person.paste(garment_scaled, box, mask)
    person.save(output_path, "JPEG", quality=92)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diffusion try-on via HF Space (IDM-VTON) or Pillow fallback"
    )
    parser.add_argument("--human", type=Path, required=True, help="Path to person/avatar image")
    parser.add_argument("--garment", type=Path, required=True, help="Path to garment image")
    parser.add_argument("--output", type=Path, required=True, help="Path to write result image")
    parser.add_argument(
        "--category",
        type=str,
        default="top",
        choices=("top", "bottom", "jacket", "footwear"),
    )
    args = parser.parse_args()

    if not args.human.is_file():
        print(f"Not found: {args.human}", file=sys.stderr)
        sys.exit(1)
    if not args.garment.is_file():
        print(f"Not found: {args.garment}", file=sys.stderr)
        sys.exit(1)

    ok = _run_gradio_tryon(args.human, args.garment, args.output, args.category)
    if not ok:
        print("Diffusion Space unavailable or failed; using Pillow composite.", file=sys.stderr)
        _run_pillow_fallback(args.human, args.garment, args.output, args.category)

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
