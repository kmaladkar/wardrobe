# API: Profile, Wardrobe, Try-on

## Overview

- **Users** have a profile (email, display name) and an **avatar** image stored in SQLite.
- **Wardrobe** items are stored per user in **collections**: `top`, `bottom`, `jacket`, `footwear`.
- **Try-on** (StableVITON): place garment images onto the user’s avatar; API is stubbed until the model is integrated.

After login/register, the client sends **`X-User-Id: <user_id>`** on all requests that require a user.

---

## Auth

| Method | Path | Body | Response |
|--------|------|------|----------|
| POST | `/auth/register` | `{ "email": "...", "display_name": "..." }` | `User` (id, email, avatar_url, …) |
| POST | `/auth/login` | `{ "email": "..." }` | `User` |

---

## User profile & avatar

| Method | Path | Headers | Body | Response |
|--------|------|---------|------|----------|
| GET | `/users/me` | `X-User-Id` | – | `User` |
| PATCH | `/users/me` | `X-User-Id` | `{ "display_name": "..." }` | `User` |
| POST | `/users/me/avatar` | `X-User-Id` | multipart: `file` (image) | `User` (with new `avatar_url`) |

---

## Wardrobe (collections)

| Method | Path | Headers | Query / Body | Response |
|--------|------|---------|--------------|----------|
| GET | `/wardrobe` | `X-User-Id` | `?category=top\|bottom\|jacket\|footwear` | `[WardrobeItem]` |
| POST | `/wardrobe` | `X-User-Id` | multipart: `file`, `category` | `WardrobeItem` (201) |
| GET | `/wardrobe/{item_id}` | `X-User-Id` | – | `WardrobeItem` |
| DELETE | `/wardrobe/{item_id}` | `X-User-Id` | – | 204 |

---

## Try-on (StableVITON stub)

| Method | Path | Headers | Body | Response |
|--------|------|---------|------|----------|
| POST | `/recommendations/try-on` | `X-User-Id` | `{ "avatar_image_id": "...", "item_ids": ["img-1", "img-2"] }` | `{ "try_on_id", "status", "result_image_id", "message" }` |
| GET | `/recommendations/try-on/{try_on_id}` | `X-User-Id` | – | Same shape (poll until `status` is `completed` and `result_image_id` is set) |

Integrate StableVITON to generate the result image, save it to `images`, and return `result_image_id`.

---

## Images

| Method | Path | Response |
|--------|------|----------|
| GET | `/images/{image_id}` | Image bytes (e.g. avatar or wardrobe item) |

---

## SQLite schema & indexes

- **users**: `id`, `email` (UNIQUE), `display_name`, `avatar_image_id` (FK → images), `created_at`, `updated_at`.  
  Indexes: `idx_users_email`, `idx_users_avatar`.
- **images**: `id`, `user_id`, `data` (BLOB), `filename`, `content_type`, `kind` (`avatar` \| `wardrobe`), `created_at`.  
  Indexes: `idx_images_user_id`, `idx_images_kind`, `idx_images_user_kind`, `idx_images_created_at`.
- **wardrobe_items**: `id`, `user_id` (FK → users), `image_id` (FK → images), `category` (top \| bottom \| jacket \| footwear), `created_at`.  
  Indexes: `idx_wardrobe_items_user_id`, `idx_wardrobe_items_category`, `idx_wardrobe_items_user_category`, `idx_wardrobe_items_image_id`, `idx_wardrobe_items_created_at`.

Run `uv run scripts/init_db.py` to create or migrate tables.
