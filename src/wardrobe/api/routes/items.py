"""Wardrobe item routes: list (from DB), upload, and serve image bytes."""

import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from wardrobe.data.database import get_connection

router = APIRouter()

# Base URL for image_url in responses; override with request.base_url in production.
BASE_URL = "http://localhost:8000"


def _row_to_item(row: dict, base_url: str) -> dict:
    """Map DB row to JSON the iOS app expects (Item)."""
    id_ = row["id"]
    created = row.get("created_at", "")
    return {
        "id": id_,
        "image_url": f"{base_url}/images/{id_}",
        "category": _filename_to_category(row["filename"]),
        "subcategory": None,
        "colors": None,
        "formality": None,
        "season": None,
        "created_at": created,
        "updated_at": created,
    }


def _filename_to_category(filename: str) -> str:
    """Heuristic: map filename to category for display."""
    f = filename.lower()
    if "shirt" in f or "tshirt" in f or "blazer" in f or "sweater" in f:
        return "top"
    if "jeans" in f or "chinos" in f or "pants" in f:
        return "bottom"
    if "shoes" in f or "sneakers" in f or "loafers" in f or "boots" in f:
        return "shoes"
    return "other"


@router.get("")
def list_items():
    """GET /items – list all images as items (iOS ClosetView)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, filename, content_type, created_at FROM images WHERE kind = 'wardrobe' OR kind IS NULL ORDER BY created_at DESC"
        ).fetchall()
        return [_row_to_item(dict(r), BASE_URL) for r in rows]
    finally:
        conn.close()


@router.post("", status_code=201)
async def create_item(
    file: UploadFile = File(..., description="Image file"),
    category: str = Form("other"),
):
    """POST /items – multipart: file + category. Saves to DB and returns item."""
    data = await file.read()
    filename = file.filename or "upload.jpg"
    content_type = file.content_type or "image/jpeg"
    id_ = f"img-{uuid.uuid4().hex[:12]}"
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO images (id, user_id, data, filename, content_type, kind) VALUES (?, ?, ?, ?, ?, 'wardrobe')",
            (id_, None, data, filename, content_type),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, filename, content_type, created_at FROM images WHERE id = ?", (id_,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Insert failed")
        return _row_to_item(dict(row), BASE_URL)
    finally:
        conn.close()
