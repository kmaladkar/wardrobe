#!/usr/bin/env python3
"""Insert mock image rows into wardrobe.db for local development. Run from project root."""

import sqlite3
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
src = root / "src"
if src.exists() and str(src) not in sys.path:
    sys.path.insert(0, str(src))

from wardrobe.config.settings import get_storage_local_path
from wardrobe.data.database import get_connection, get_sqlite_path, init_db
from wardrobe.data.mock_images import MOCK_IMAGES

# Fallback when no file on disk (NOT NULL).
PLACEHOLDER_BLOB = b"\x00" * 64


def _image_blob(filename: str) -> bytes:
    """Use downloaded file from local/uploads/mock if present, else placeholder."""
    mock_dir = get_storage_local_path() / "mock"
    path = mock_dir / filename
    if path.is_file():
        return path.read_bytes()
    return PLACEHOLDER_BLOB


def main() -> None:
    path = get_sqlite_path()
    print(f"Seeding mock data into {path}")
    init_db()

    conn = get_connection()
    try:
        inserted = 0
        for id_, filename, content_type, _seed in MOCK_IMAGES:
            blob = _image_blob(filename)
            try:
                conn.execute(
                    "INSERT INTO images (id, data, filename, content_type) VALUES (?, ?, ?, ?)",
                    (id_, blob, filename, content_type),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                print(f"  Skip (exists): {id_} {filename}")
        conn.commit()
        print(f"Inserted {inserted} mock image(s).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
