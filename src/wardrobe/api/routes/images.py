"""Serve image bytes by id (GET /images/{id})."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from wardrobe.data.database import get_connection

router = APIRouter()


@router.get("/{image_id}")
def get_image(image_id: str):
    """GET /images/{id} – return image BLOB (for image_url in items)."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT data, content_type FROM images WHERE id = ?", (image_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=bytes(row["data"]), media_type=row["content_type"])
    finally:
        conn.close()
