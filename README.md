# Wardrobe

Generative AI mobile app that recommends outfits based on your collection.

- **Backend:** Python (this repo, `uv run main.py`)
- **iPhone app:** SwiftUI app in [ios/](ios/) – see [ios/README.md](ios/README.md) to run it.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Run the app
uv run main.py
```

If `uv` is not available or fails on your system, use a standard venv:

```bash
python3 -m venv .venv
source .venv/bin/activate   # or `.venv\Scripts\activate` on Windows
pip install -e .
uv run main.py   # or: python main.py
```

## Local development and data storage

- **Run from project root** so the default paths work.
- **Database:** SQLite by default at `./data/wardrobe.db` (set `DATABASE_URL` to use Postgres).
- **Images:** stored under `./data/uploads/` by default (set `STORAGE_TYPE=s3` and credentials for production).
- The `data/` directory is gitignored; create it with `mkdir -p data/uploads` if you want it upfront.

See **[docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md)** for env vars and details.

## Development

- Add dependencies: `uv add <package>`
- Add dev dependencies: `uv add --dev <package>`
- Run scripts: `uv run python script.py`
