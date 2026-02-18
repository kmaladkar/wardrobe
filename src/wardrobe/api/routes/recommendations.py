"""Recommendation routes: what to wear today, complete outfit (mock for now)."""

from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()


@router.get("/today")
def today():
    """GET /recommendations/today – what to wear today. Returns 204 until we have logic."""
    return Response(status_code=204)


@router.get("/complete")
def complete(item_id: str):
    """GET /recommendations/complete?item_id=... – complete the outfit. Returns 204 for now."""
    return Response(status_code=204)
