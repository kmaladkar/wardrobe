#!/usr/bin/env python3
"""Download mock wardrobe images from the web and save to local folder. Run from project root."""

import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
src = root / "src"
if src.exists() and str(src) not in sys.path:
    sys.path.insert(0, str(src))

from wardrobe.config.settings import get_storage_local_path
from wardrobe.data.mock_images import MOCK_IMAGES

# Picsum.photos: deterministic images by seed.
BASE = "https://picsum.photos/seed/{seed}/400/400"


def download(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "WardrobeMock/1.0"})
    with urlopen(req, timeout=15) as resp:
        return resp.read()


def main() -> None:
    dest_dir = get_storage_local_path() / "mock"
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading mock images to {dest_dir}")

    for _id, filename, _content_type, seed in MOCK_IMAGES:
        url = BASE.format(seed=seed)
        out_path = dest_dir / filename
        try:
            data = download(url)
            out_path.write_bytes(data)
            print(f"  OK {filename} ({len(data)} bytes)")
        except (URLError, HTTPError, OSError) as e:
            print(f"  Skip {filename}: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
