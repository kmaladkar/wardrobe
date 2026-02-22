"""Recommendations: what to wear today, try-on (local script/command or placeholder)."""

import threading
import uuid

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from wardrobe.data.database import get_connection
from wardrobe.services.try_on import run_try_on

router = APIRouter()

BASE_URL = "http://localhost:8000"

# In-memory try-on job store: try_on_id -> { status, result_image_id, message }
_try_on_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()

CATEGORIES_ORDER = ("top", "bottom", "jacket", "footwear")


def _require_user(x_user_id: str | None = Header(None, alias="X-User-Id")) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return x_user_id


# ----- Response models -----


class OutfitItemOut(BaseModel):
    id: str
    user_id: str
    image_id: str
    image_url: str
    category: str
    created_at: str


class TodayOutfitOut(BaseModel):
    items: list[OutfitItemOut]
    item_ids: list[str]


class TodayOut(BaseModel):
    outfit: TodayOutfitOut
    try_on_id: str


class TryOnIn(BaseModel):
    avatar_image_id: str
    item_ids: list[str]


class TryOnOut(BaseModel):
    try_on_id: str
    status: str
    result_image_id: str | None = None
    message: str


def _wardrobe_row_to_out(row: dict) -> OutfitItemOut:
    return OutfitItemOut(
        id=row["id"],
        user_id=row["user_id"],
        image_id=row["image_id"],
        image_url=f"{BASE_URL}/images/{row['image_id']}",
        category=row["category"],
        created_at=row["created_at"],
    )


def _get_one_item_per_category(conn, user_id: str) -> list[dict]:
    """Return one wardrobe item per category (top, bottom, jacket, footwear), by latest created."""
    rows = conn.execute(
        """SELECT w.id, w.user_id, w.image_id, w.category, w.created_at
           FROM wardrobe_items w
           WHERE w.user_id = ?
           ORDER BY w.category, w.created_at DESC""",
        (user_id,),
    ).fetchall()
    by_cat: dict[str, dict] = {}
    for r in rows:
        d = dict(r)
        if d["category"] not in by_cat:
            by_cat[d["category"]] = d
    result = []
    for cat in CATEGORIES_ORDER:
        if cat in by_cat:
            result.append(by_cat[cat])
    return result


def _pick_garment_for_tryon(items: list[dict]) -> tuple[str, str] | None:
    """Pick best garment for try-on: prefer top/jacket (torso), then bottom, then footwear. Returns (image_id, category)."""
    for cat in ("top", "jacket", "bottom", "footwear"):
        for r in items:
            if r.get("category") == cat:
                return (r["image_id"], cat)
    if items:
        r = items[0]
        return (r["image_id"], r.get("category", "top"))
    return None


def _start_try_on_job(
    try_on_id: str,
    user_id: str,
    avatar_image_id: str,
    items: list[dict],
) -> None:
    """Background: run try-on (avatar + one garment by category), save result, update job."""
    with _jobs_lock:
        _try_on_jobs[try_on_id] = {"status": "processing", "result_image_id": None, "message": "Running try-on…"}
    result_image_id = None
    message = "Completed."
    try:
        picked = _pick_garment_for_tryon(items)
        if not picked:
            message = "No garment selected."
        else:
            garment_image_id, category = picked
            result_image_id = run_try_on(avatar_image_id, garment_image_id, user_id, category=category)
            if not result_image_id:
                message = "Try-on failed (check avatar and garment images)."
    except Exception as e:
        message = f"Try-on error: {e!s}"
    with _jobs_lock:
        _try_on_jobs[try_on_id] = {
            "status": "completed" if result_image_id else "failed",
            "result_image_id": result_image_id,
            "message": message,
        }


@router.get("/today", response_model=TodayOut, status_code=200)
def today(x_user_id: str | None = Header(None, alias="X-User-Id")):
    """
    GET /recommendations/today – suggested outfit (one item per category) and a try-on job.
    Requires X-User-Id. Returns 404 if no wardrobe items. Uses local try-on script if set.
    """
    user_id = _require_user(x_user_id)
    conn = get_connection()
    try:
        user_row = conn.execute(
            "SELECT id, avatar_image_id FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        avatar_image_id = user_row["avatar_image_id"] if user_row["avatar_image_id"] else None
        items = _get_one_item_per_category(conn, user_id)
    finally:
        conn.close()

    if not items:
        raise HTTPException(status_code=404, detail="No wardrobe items. Add top, bottom, or footwear.")

    item_ids = [r["image_id"] for r in items]
    try_on_id = f"tryon-{uuid.uuid4().hex[:12]}"
    with _jobs_lock:
        _try_on_jobs[try_on_id] = {"status": "pending", "result_image_id": None, "message": "Queued."}

    if avatar_image_id:
        thread = threading.Thread(
            target=_start_try_on_job,
            args=(try_on_id, user_id, avatar_image_id, items),
        )
        thread.start()
    else:
        with _jobs_lock:
            _try_on_jobs[try_on_id] = {
                "status": "failed",
                "result_image_id": None,
                "message": "Set an avatar in Profile to see try-on.",
            }

    outfit = TodayOutfitOut(
        items=[_wardrobe_row_to_out(r) for r in items],
        item_ids=item_ids,
    )
    return TodayOut(outfit=outfit, try_on_id=try_on_id)


@router.get("/complete")
def complete(item_id: str, x_user_id: str | None = Header(None, alias="X-User-Id")):
    """GET /recommendations/complete?item_id=... – complete the outfit. Returns 204 for now."""
    _require_user(x_user_id)
    return Response(status_code=204)


@router.post("/try-on", response_model=TryOnOut)
def try_on(body: TryOnIn, x_user_id: str | None = Header(None, alias="X-User-Id")):
    """
    POST /recommendations/try-on – run virtual try-on (avatar + garments).
    Picks first garment and uses its category for placement. Poll GET /try-on/{id} for result.
    """
    user_id = _require_user(x_user_id)
    if not body.avatar_image_id or not body.item_ids:
        raise HTTPException(status_code=400, detail="avatar_image_id and item_ids required")
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT image_id, category FROM wardrobe_items WHERE user_id = ? AND image_id IN ("
            + ",".join("?" * len(body.item_ids)) + ")",
            (user_id, *body.item_ids),
        ).fetchall()
        cat_by_image = {r["image_id"]: r["category"] for r in rows}
    finally:
        conn.close()
    items = [{"image_id": iid, "category": cat_by_image.get(iid, "top")} for iid in body.item_ids]
    try_on_id = f"tryon-{uuid.uuid4().hex[:12]}"
    with _jobs_lock:
        _try_on_jobs[try_on_id] = {"status": "pending", "result_image_id": None, "message": "Queued."}
    thread = threading.Thread(
        target=_start_try_on_job,
        args=(try_on_id, user_id, body.avatar_image_id, items),
    )
    thread.start()
    return TryOnOut(
        try_on_id=try_on_id,
        status="pending",
        result_image_id=None,
        message="Try-on queued. Poll GET /recommendations/try-on/{try_on_id} for result.",
    )


@router.get("/try-on/{try_on_id}", response_model=TryOnOut)
def get_try_on(
    try_on_id: str,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
):
    """GET /recommendations/try-on/{id} – poll try-on job status and result_image_id."""
    _require_user(x_user_id)
    with _jobs_lock:
        job = _try_on_jobs.get(try_on_id)
    if not job:
        raise HTTPException(status_code=404, detail="Try-on job not found")
    return TryOnOut(
        try_on_id=try_on_id,
        status=job["status"],
        result_image_id=job.get("result_image_id"),
        message=job.get("message", ""),
    )
