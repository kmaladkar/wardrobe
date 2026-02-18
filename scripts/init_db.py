#!/usr/bin/env python3
"""Create or reset the local SQLite database (tables and indexes). Run from project root."""

import sys
from pathlib import Path

# Allow importing wardrobe when run as script (project root or via uv run)
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Ensure we can import from src
src = root / "src"
if src.exists() and str(src) not in sys.path:
    sys.path.insert(0, str(src))

from wardrobe.data.database import get_sqlite_path, init_db


def main() -> None:
    path = get_sqlite_path()
    print(f"Initializing SQLite database at {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    init_db()
    print("Done. Table: images.")


if __name__ == "__main__":
    main()
