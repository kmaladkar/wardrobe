"""Item domain model: wardrobe piece with metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    """A single wardrobe item (top, bottom, shoes, etc.)."""

    id: str
    user_id: str
    image_url: str
    category: str
    subcategory: str | None
    colors: str | None
    pattern: str | None
    formality: str | None
    season: str | None
    brand: str | None
    purchase_date: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: object) -> "Item":
        """Build Item from a database row (e.g. sqlite3.Row)."""
        r = dict(row)
        return cls(
            id=r["id"],
            user_id=r["user_id"],
            image_url=r["image_url"],
            category=r["category"],
            subcategory=r.get("subcategory"),
            colors=r.get("colors"),
            pattern=r.get("pattern"),
            formality=r.get("formality"),
            season=r.get("season"),
            brand=r.get("brand"),
            purchase_date=r.get("purchase_date"),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
