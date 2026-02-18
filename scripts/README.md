# Scripts

One-off or recurring scripts: migrations, seed data, model training, exports.

- **init_db.py** – Create the local SQLite database and tables: `uv run scripts/init_db.py`
- **download_mock_images.py** – Download mock wardrobe images into `local/uploads/mock/`: `uv run scripts/download_mock_images.py`
- **seed_mock_data.py** – Insert mock image rows into wardrobe.db (uses downloaded images if present): `uv run scripts/seed_mock_data.py`
