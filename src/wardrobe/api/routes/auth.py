"""Auth: register (create profile), login. No JWT for now – use user id in header or query."""

import sqlite3
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from wardrobe.data.database import get_connection

router = APIRouter()
BASE_URL = "http://localhost:8000"


class RegisterIn(BaseModel):
    email: EmailStr
    display_name: str | None = None


class LoginIn(BaseModel):
    email: EmailStr


class UserOut(BaseModel):
    id: str
    email: str
    display_name: str | None
    avatar_image_id: str | None
    avatar_url: str | None = None
    created_at: str
    updated_at: str


@router.post("/register", response_model=UserOut)
def register(body: RegisterIn):
    """Create a user profile. Returns user (no password for now)."""
    user_id = f"user-{uuid.uuid4().hex[:12]}"
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO users (id, email, display_name)
               VALUES (?, ?, ?)""",
            (user_id, body.email, body.display_name or ""),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, email, display_name, avatar_image_id, created_at, updated_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Insert failed")
        d = dict(row)
        d["avatar_url"] = f"{BASE_URL}/images/{d['avatar_image_id']}" if d.get("avatar_image_id") else None
        return UserOut(**d)
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@router.post("/login", response_model=UserOut)
def login(body: LoginIn):
    """Login by email (no password for now). Returns user or 404."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, email, display_name, avatar_image_id, created_at, updated_at FROM users WHERE email = ?",
            (body.email,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        d = dict(row)
        d["avatar_url"] = f"{BASE_URL}/images/{d['avatar_image_id']}" if d.get("avatar_image_id") else None
        return UserOut(**d)
    finally:
        conn.close()
