"""Recommendations: what to wear today, complete outfit, try-on (StableVITON stub)."""

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter()


def _require_user(x_user_id: str | None = Header(None, alias="X-User-Id")) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return x_user_id


@router.get("/today")
def today(x_user_id: str | None = Header(None, alias="X-User-Id")):
    """GET /recommendations/today – what to wear today. Returns 204 until we have logic."""
    _require_user(x_user_id)
    return Response(status_code=204)


@router.get("/complete")
def complete(item_id: str, x_user_id: str | None = Header(None, alias="X-User-Id")):
    """GET /recommendations/complete?item_id=... – complete the outfit. Returns 204 for now."""
    _require_user(x_user_id)
    return Response(status_code=204)


# Try-on: StableVITON – place garment(s) onto user avatar.
class TryOnIn(BaseModel):
    avatar_image_id: str
    item_ids: list[str]  # garment image ids (e.g. one top, one bottom)


class TryOnOut(BaseModel):
    try_on_id: str
    status: str  # "pending" | "processing" | "completed" | "failed"
    result_image_id: str | None = None
    message: str


@router.post("/try-on", response_model=TryOnOut)
def try_on(body: TryOnIn, x_user_id: str | None = Header(None, alias="X-User-Id")):
    """
    POST /recommendations/try-on – run virtual try-on (StableVITON).
    Body: avatar_image_id (user's avatar), item_ids (wardrobe image ids to drape on avatar).
    Stub: returns pending job; integrate StableVITON model later to produce result_image_id.
    """
    user_id = _require_user(x_user_id)
    if not body.avatar_image_id or not body.item_ids:
        raise HTTPException(status_code=400, detail="avatar_image_id and item_ids required")
    # Stub: in production, enqueue job (Celery/RQ), run StableVITON, save result to images, return id.
    try_on_id = f"tryon-{user_id[:8]}-{len(body.item_ids)}"
    return TryOnOut(
        try_on_id=try_on_id,
        status="pending",
        result_image_id=None,
        message="Try-on queued. Integrate StableVITON model to generate result_image_id.",
    )


@router.get("/try-on/{try_on_id}", response_model=TryOnOut)
def get_try_on(
    try_on_id: str,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    """GET /recommendations/try-on/{id} – poll try-on job status. Stub returns pending."""
    _require_user(x_user_id)
    return TryOnOut(
        try_on_id=try_on_id,
        status="pending",
        result_image_id=None,
        message="Stub: integrate StableVITON to update status and result_image_id.",
    )
