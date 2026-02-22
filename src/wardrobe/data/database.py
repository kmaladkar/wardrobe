"""SQLite database: schema (users, images, wardrobe_items), indexes, and migrations."""

import sqlite3
from pathlib import Path


def _sqlite_path_from_url(url: str) -> Path:
    if not url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported for local dev")
    return Path(url.removeprefix("sqlite:///")).resolve()


def get_sqlite_path() -> Path:
    """Path to the SQLite database file (for sqlite:/// URLs only)."""
    from wardrobe.config.settings import get_database_url
    return _sqlite_path_from_url(get_database_url())


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a connection to the SQLite database. Creates the file and parent dir if missing."""
    path = db_path or get_sqlite_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Schema: users (profile + avatar), images (BLOB + kind), wardrobe_items (collection)
# Categories: top, bottom, jacket, footwear
# ---------------------------------------------------------------------------

SCHEMA = """
-- Images: avatar or wardrobe item (BLOB). user_id nullable for backward compat.
CREATE TABLE IF NOT EXISTS images (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    data BLOB NOT NULL,
    filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'wardrobe' CHECK(kind IN ('avatar','wardrobe')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Users: profile and optional avatar (FK to images).
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    avatar_image_id TEXT REFERENCES images(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Wardrobe items: user's clothes by collection (top, bottom, jacket, footwear).
CREATE TABLE IF NOT EXISTS wardrobe_items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_id TEXT NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK(category IN ('top','bottom','jacket','footwear')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indexes: lookups by user, category, and composite for list/filter.
CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id);
CREATE INDEX IF NOT EXISTS idx_images_kind ON images(kind);
CREATE INDEX IF NOT EXISTS idx_images_user_kind ON images(user_id, kind);
CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_avatar ON users(avatar_image_id);

CREATE INDEX IF NOT EXISTS idx_wardrobe_items_user_id ON wardrobe_items(user_id);
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_category ON wardrobe_items(category);
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_user_category ON wardrobe_items(user_id, category);
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_image_id ON wardrobe_items(image_id);
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_created_at ON wardrobe_items(created_at);
"""


def _migrate_images(conn: sqlite3.Connection) -> None:
    """Add user_id and kind to images if missing (existing DBs)."""
    cursor = conn.execute("PRAGMA table_info(images)")
    columns = {row[1] for row in cursor.fetchall()}
    if "user_id" not in columns:
        conn.execute("ALTER TABLE images ADD COLUMN user_id TEXT")
    if "kind" not in columns:
        conn.execute("ALTER TABLE images ADD COLUMN kind TEXT DEFAULT 'wardrobe'")


def init_db(conn: sqlite3.Connection | None = None) -> None:
    """Create tables and indexes; migrate existing images table. Safe to call multiple times."""
    own_conn = False
    if conn is None:
        path = get_sqlite_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        own_conn = True
    try:
        _migrate_images(conn)
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        if own_conn:
            conn.close()
