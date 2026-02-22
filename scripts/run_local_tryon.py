#!/usr/bin/env python3
"""
Local virtual try-on: composite garment onto avatar by category (top/bottom/footwear)
with soft-edge blending. Use as TRY_ON_SCRIPT for the backend.

  python scripts/run_local_tryon.py --human person.jpg --garment cloth.jpg --output result.jpg --category top

Requires: pip install pillow (or uv sync --extra tryon)
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError:
    print("Install Pillow: pip install pillow (or uv sync --extra tryon)", file=sys.stderr)
    sys.exit(1)


def _placement_for_category(category: str, pw: int, ph: int, gw: int, gh: int) -> tuple[int, int, int, int, int]:
    """
    Return (x, y, target_w, target_h, feather) for where to place the garment.
    top/jacket: upper body (torso). bottom: lower body. footwear: feet strip.
    """
    scale_w = pw * 0.45
    scale = scale_w / max(1, gw)
    target_w = max(64, min(pw, int(gw * scale)))
    target_h = max(64, min(ph, int(gh * scale)))
    feather = max(8, min(40, target_w // 6))

    if category in ("top", "jacket"):
        x = (pw - target_w) // 2
        y = max(0, int(ph * 0.12))
        return (x, y, target_w, target_h, feather)
    if category == "bottom":
        x = (pw - target_w) // 2
        y = max(int(ph * 0.35), ph - target_h - int(ph * 0.1))
        return (x, y, target_w, target_h, feather)
    if category == "footwear":
        tw_foot = max(64, int(pw * 0.5))
        th_foot = max(32, int(ph * 0.15))
        x = (pw - tw_foot) // 2
        y = ph - th_foot - int(ph * 0.02)
        return (x, y, tw_foot, th_foot, max(6, tw_foot // 10))
    # default: upper body
    x = (pw - target_w) // 2
    y = max(0, int(ph * 0.12))
    return (x, y, target_w, target_h, feather)


def composite_tryon(human_path: Path, garment_path: Path, output_path: Path, category: str = "top") -> None:
    """
    Place garment onto avatar using category-based region and soft blending.
    """
    person = Image.open(human_path).convert("RGB")
    garment = Image.open(garment_path).convert("RGB")

    pw, ph = person.size
    gw, gh = garment.size

    x, y, target_w, target_h, feather = _placement_for_category(category, pw, ph, gw, gh)

    garment_scaled = garment.resize((target_w, target_h), Image.Resampling.LANCZOS)
    box = (x, y, x + target_w, y + target_h)

    # Soft mask (same size as garment): 255 in center, fade at edges so it blends
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
    parser = argparse.ArgumentParser(description="Local try-on: composite garment onto person by category")
    parser.add_argument("--human", type=Path, required=True, help="Path to person/avatar image")
    parser.add_argument("--garment", type=Path, required=True, help="Path to garment image")
    parser.add_argument("--output", type=Path, required=True, help="Path to write result image")
    parser.add_argument("--category", type=str, default="top", choices=("top", "bottom", "jacket", "footwear"))
    args = parser.parse_args()

    if not args.human.is_file():
        print(f"Not found: {args.human}", file=sys.stderr)
        sys.exit(1)
    if not args.garment.is_file():
        print(f"Not found: {args.garment}", file=sys.stderr)
        sys.exit(1)

    composite_tryon(args.human, args.garment, args.output, args.category)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
