"""SQLite database for local development: connection, schema, and init."""

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


SCHEMA = """
CREATE TABLE IF NOT EXISTS images (
    id TEXT PRIMARY KEY,
    data BLOB NOT NULL,
    filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at);
"""


def init_db(conn: sqlite3.Connection | None = None) -> None:
    """Create tables and indexes if they do not exist. Safe to call multiple times."""
    own_conn = False
    if conn is None:
        path = get_sqlite_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        own_conn = True
    conn.executescript(SCHEMA)
    conn.commit()
    if own_conn:
        conn.close()
