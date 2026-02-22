"""Wardrobe collections: CRUD by category (top, bottom, jacket, footwear)."""

import uuid

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile
from pydantic import BaseModel

from wardrobe.data.database import get_connection

router = APIRouter()

BASE_URL = "http://localhost:8000"
COLLECTION_CATEGORIES = ("top", "bottom", "jacket", "footwear")


class WardrobeItemOut(BaseModel):
    id: str
    user_id: str
    image_id: str
    image_url: str
    category: str
    created_at: str


def _require_user(x_user_id: str | None = Header(None, alias="X-User-Id")) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return x_user_id


def _item_row_to_out(row: dict) -> WardrobeItemOut:
    return WardrobeItemOut(
        id=row["id"],
        user_id=row["user_id"],
        image_id=row["image_id"],
        image_url=f"{BASE_URL}/images/{row['image_id']}",
        category=row["category"],
        created_at=row["created_at"],
    )


@router.get("", response_model=list[WardrobeItemOut])
def list_items(
    category: str | None = None,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    """List wardrobe items for the user. Optional ?category=top|bottom|jacket|footwear."""
    user_id = _require_user(x_user_id)
    conn = get_connection()
    try:
        if category and category in COLLECTION_CATEGORIES:
            rows = conn.execute(
                """SELECT w.id, w.user_id, w.image_id, w.category, w.created_at
                   FROM wardrobe_items w
                   WHERE w.user_id = ? AND w.category = ?
                   ORDER BY w.created_at DESC""",
                (user_id, category),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT w.id, w.user_id, w.image_id, w.category, w.created_at
                   FROM wardrobe_items w
                   WHERE w.user_id = ?
                   ORDER BY w.category, w.created_at DESC""",
                (user_id,),
            ).fetchall()
        return [_item_row_to_out(dict(r)) for r in rows]
    finally:
        conn.close()


@router.post("", status_code=201, response_model=WardrobeItemOut)
async def add_item(
    file: UploadFile = File(...),
    category: str = Form(..., description="top | bottom | jacket | footwear"),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    """Upload a wardrobe item into a collection (top, bottom, jacket, footwear)."""
    user_id = _require_user(x_user_id)
    if category not in COLLECTION_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"category must be one of: {', '.join(COLLECTION_CATEGORIES)}",
        )
    data = await file.read()
    filename = file.filename or "upload.jpg"
    content_type = file.content_type or "image/jpeg"
    image_id = f"img-{uuid.uuid4().hex[:12]}"
    item_id = f"wi-{uuid.uuid4().hex[:12]}"
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO images (id, user_id, data, filename, content_type, kind)
               VALUES (?, ?, ?, ?, ?, 'wardrobe')""",
            (image_id, user_id, data, filename, content_type),
        )
        conn.execute(
            """INSERT INTO wardrobe_items (id, user_id, image_id, category)
               VALUES (?, ?, ?, ?)""",
            (item_id, user_id, image_id, category),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, user_id, image_id, category, created_at FROM wardrobe_items WHERE id = ?",
            (item_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Insert failed")
        return _item_row_to_out(dict(row))
    finally:
        conn.close()


@router.get("/{item_id}", response_model=WardrobeItemOut)
def get_item(
    item_id: str,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    """Get one wardrobe item by id."""
    user_id = _require_user(x_user_id)
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, user_id, image_id, category, created_at FROM wardrobe_items WHERE id = ? AND user_id = ?",
            (item_id, user_id),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        return _item_row_to_out(dict(row))
    finally:
        conn.close()


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: str,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    """Delete a wardrobe item (and its image)."""
    user_id = _require_user(x_user_id)
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM wardrobe_items WHERE id = ? AND user_id = ?",
            (item_id, user_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
    finally:
        conn.close()
