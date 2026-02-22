#!/usr/bin/env python3
"""Import image files from local/uploads into SQLite (images + wardrobe_items).
Run from project root. Requires at least one user (register via API or create seed user)."""

import argparse
import sqlite3
import sys
import uuid
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
src = root / "src"
if src.exists() and str(src) not in sys.path:
    sys.path.insert(0, str(src))

from wardrobe.config.settings import get_storage_local_path
from wardrobe.data.database import get_connection, get_sqlite_path, init_db

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
CONTENT_TYPE = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}
CATEGORIES = {"top", "bottom", "jacket", "footwear"}


def _get_or_create_seed_user(conn: sqlite3.Connection) -> str:
    """Return first user id, or create seed@local.dev and return its id."""
    row = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    if row:
        return row["id"]
    user_id = f"user-{uuid.uuid4().hex[:12]}"
    conn.execute(
        "INSERT INTO users (id, email, display_name) VALUES (?, ?, ?)",
        (user_id, "seed@local.dev", "Seed User"),
    )
    return user_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Import images from local/uploads into SQLite")
    parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Directory to scan (default: local/uploads)",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default=None,
        help="User to attach items to (default: first user or create seed@local.dev)",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="top",
        choices=list(CATEGORIES),
        help="Default category for items (default: top). Subfolders named top/bottom/jacket/footwear override.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subdirectories; folder name used as category when it is top/bottom/jacket/footwear",
    )
    args = parser.parse_args()

    uploads_dir = args.dir or get_storage_local_path()
    if not uploads_dir.exists():
        print(f"Directory does not exist: {uploads_dir}")
        sys.exit(1)

    init_db()
    conn = get_connection()
    try:
        user_id = args.user_id
        if not user_id:
            user_id = _get_or_create_seed_user(conn)
            print(f"Using user: {user_id}")

        if args.recursive:
            files_to_import = []
            for ext in ALLOWED_EXTENSIONS:
                files_to_import.extend(uploads_dir.rglob(f"*{ext}"))
        else:
            files_to_import = [
                f for f in uploads_dir.iterdir()
                if f.is_file() and f.suffix.lower() in ALLOWED_EXTENSIONS
            ]

        if not files_to_import:
            print(f"No image files found in {uploads_dir}")
            return

        inserted = 0
        for path in sorted(files_to_import):
            suffix = path.suffix.lower()
            content_type = CONTENT_TYPE.get(suffix, "image/jpeg")
            category = args.category
            if args.recursive and path.parent != uploads_dir:
                parent_name = path.parent.name.lower()
                if parent_name in CATEGORIES:
                    category = parent_name

            try:
                data = path.read_bytes()
            except OSError as e:
                print(f"  Skip (read error): {path.name} - {e}")
                continue

            image_id = f"img-{uuid.uuid4().hex[:12]}"
            item_id = f"wi-{uuid.uuid4().hex[:12]}"
            try:
                conn.execute(
                    """INSERT INTO images (id, user_id, data, filename, content_type, kind)
                       VALUES (?, ?, ?, ?, ?, 'wardrobe')""",
                    (image_id, user_id, data, path.name, content_type),
                )
                conn.execute(
                    """INSERT INTO wardrobe_items (id, user_id, image_id, category)
                       VALUES (?, ?, ?, ?)""",
                    (item_id, user_id, image_id, category),
                )
                inserted += 1
                print(f"  {path.name} -> {category} (image_id={image_id})")
            except sqlite3.IntegrityError as e:
                print(f"  Skip: {path.name} - {e}")

        conn.commit()
        print(f"Imported {inserted} file(s) into images + wardrobe_items.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
