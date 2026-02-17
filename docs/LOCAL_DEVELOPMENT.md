# Local development

How to run the project on your machine and where data is stored.

## Quick start

1. **From the project root**, create the environment and run:

   ```bash
   uv sync
   uv run main.py
   ```

   Or with venv:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   python main.py
   ```

2. **Optional:** copy env defaults and edit if needed:

   ```bash
   cp .env.example .env
   ```

3. **Optional:** create the data directory so the DB and uploads live in one place:

   ```bash
   mkdir -p data/uploads
   ```

   If you skip this, the **database** file will be created when the app first uses it; the **uploads** directory will be created when the app first uses local storage.

---

## Where data is stored (local defaults)

| What            | Default location        | Configured by                |
|-----------------|-------------------------|------------------------------|
| **Database**    | `./data/wardrobe.db`    | `DATABASE_URL`               |
| **Uploaded images** | `./data/uploads/`  | `STORAGE_LOCAL_PATH`         |

- All of this lives under the **`data/`** directory, which is **gitignored** so you never commit DB or user uploads.
- Run commands from the **project root** so that `./data` is created there.

### Database (SQLite)

- **URL:** `sqlite:///./data/wardrobe.db` (relative to current working directory).
- No extra setup: SQLite is file-based. The file is created on first use.
- To use **PostgreSQL** instead (e.g. for production), set in `.env`:
  - `DATABASE_URL=postgresql://user:password@localhost:5432/wardrobe`

### File storage (images)

- **Type:** `local` (files written to disk).
- **Path:** `./data/uploads/` by default; overridable with `STORAGE_LOCAL_PATH`.
- For production you’d set `STORAGE_TYPE=s3` and configure S3 (bucket, region, keys).

---

## Environment variables

| Variable              | Default (local)           | Purpose                          |
|-----------------------|---------------------------|----------------------------------|
| `DATABASE_URL`        | `sqlite:///./data/wardrobe.db` | Database connection string   |
| `STORAGE_TYPE`        | `local`                   | `local` or `s3`                  |
| `STORAGE_LOCAL_PATH`  | `./data/uploads`           | Directory for local image files  |
| `DEBUG`               | `1`                       | Enable debug mode               |
| `SECRET_KEY`          | (dev default)              | App secret; set in production   |
| `EMBEDDING_MODEL`     | (empty)                   | Optional ML model name/path     |

Use `.env` for local overrides; see `.env.example`.

---

## Switching to production-style storage

- **Database:** set `DATABASE_URL` to your Postgres (or other) URL.
- **Images:** set `STORAGE_TYPE=s3` and configure AWS (or S3-compatible) credentials and bucket; the app will use `services/storage/images.py` to talk to S3 instead of the local path.

No code change is required for these; configuration is read from the same settings and env.
