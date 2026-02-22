"""User profile: get/update me, upload avatar."""

import uuid

from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from pydantic import BaseModel

from wardrobe.data.database import get_connection

router = APIRouter()

BASE_URL = "http://localhost:8000"


class UserOut(BaseModel):
    id: str
    email: str
    display_name: str | None
    avatar_image_id: str | None
    avatar_url: str | None
    created_at: str
    updated_at: str


class UpdateProfileIn(BaseModel):
    display_name: str | None = None


def _user_row_to_out(row: dict) -> UserOut:
    aid = row.get("avatar_image_id")
    return UserOut(
        id=row["id"],
        email=row["email"],
        display_name=row.get("display_name"),
        avatar_image_id=aid,
        avatar_url=f"{BASE_URL}/images/{aid}" if aid else None,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _require_user(x_user_id: str | None = Header(None, alias="X-User-Id")) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return x_user_id


@router.get("/me", response_model=UserOut)
def get_me(x_user_id: str | None = Header(None, alias="X-User-Id")):
    """Get current user profile (send X-User-Id header after login)."""
    user_id = _require_user(x_user_id)
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, email, display_name, avatar_image_id, created_at, updated_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return _user_row_to_out(dict(row))
    finally:
        conn.close()


@router.patch("/me", response_model=UserOut)
def update_me(
    body: UpdateProfileIn,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    """Update display name."""
    user_id = _require_user(x_user_id)
    conn = get_connection()
    try:
        if body.display_name is not None:
            conn.execute(
                "UPDATE users SET display_name = ?, updated_at = datetime('now') WHERE id = ?",
                (body.display_name, user_id),
            )
        conn.commit()
        row = conn.execute(
            "SELECT id, email, display_name, avatar_image_id, created_at, updated_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return _user_row_to_out(dict(row))
    finally:
        conn.close()


@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    """Upload avatar image; set as user's avatar. Replaces previous avatar."""
    user_id = _require_user(x_user_id)
    data = await file.read()
    filename = file.filename or "avatar.jpg"
    content_type = file.content_type or "image/jpeg"
    image_id = f"img-{uuid.uuid4().hex[:12]}"
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO images (id, user_id, data, filename, content_type, kind)
               VALUES (?, ?, ?, ?, ?, 'avatar')""",
            (image_id, user_id, data, filename, content_type),
        )
        conn.execute(
            "UPDATE users SET avatar_image_id = ?, updated_at = datetime('now') WHERE id = ?",
            (image_id, user_id),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, email, display_name, avatar_image_id, created_at, updated_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Update failed")
        return _user_row_to_out(dict(row))
    finally:
        conn.close()
