"""Settings from env: DB URL, storage, ML paths. Defaults are for local development."""

import os
from pathlib import Path


def _str(value: str | None, default: str) -> str:
    return (value or "").strip() or default


def _path(value: str | None, default: Path) -> Path:
    p = Path(_str(value, str(default))).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


# ----- Database (local dev: SQLite in local/ folder) -----
# For production set DATABASE_URL to Postgres, e.g. postgresql://user:pass@host/db
DATABASE_URL: str = _str(
    os.environ.get("DATABASE_URL"),
    "sqlite:///./local/wardrobe.db",
)

# ----- Storage (local dev: filesystem in project data dir) -----
# Options: "local" | "s3" (future). Local writes to STORAGE_LOCAL_PATH.
STORAGE_TYPE: str = _str(os.environ.get("STORAGE_TYPE"), "local")
# Default: ./local/uploads when running from project root
STORAGE_LOCAL_PATH: Path = _path(
    os.environ.get("STORAGE_LOCAL_PATH"),
    Path.cwd() / "local" / "uploads",
)
# For S3 (when STORAGE_TYPE=s3): bucket, region, keys via env
# S3_BUCKET, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# ----- App -----
DEBUG: bool = os.environ.get("DEBUG", "1").strip().lower() in ("1", "true", "yes")
SECRET_KEY: str = _str(os.environ.get("SECRET_KEY"), "dev-secret-change-in-production")

# ----- ML (optional; paths or model names) -----
# EMBEDDING_MODEL, COMPATIBILITY_MODEL_PATH, etc.
EMBEDDING_MODEL: str = _str(os.environ.get("EMBEDDING_MODEL"), "")


def get_database_url() -> str:
    """Database URL for the current environment (used by ORM/DB client)."""
    return DATABASE_URL


def get_storage_local_path() -> Path:
    """Directory for local file uploads (images). Only used when STORAGE_TYPE=local."""
    return STORAGE_LOCAL_PATH
