# Wardrobe

Generative AI mobile app: manage your closet, get daily outfit suggestions, and see virtual try-on (garments on your avatar). **Backend:** Python (FastAPI + SQLite). **Client:** iPhone app (SwiftUI).

---

## Table of contents

- [Quick start](#quick-start)
- [Data model (SQLite)](#data-model-sqlite)
- [Backend API](#backend-api)
- [ML & virtual try-on](#ml--virtual-try-on)
- [iOS app](#ios-app)
- [Scripts](#scripts)
- [Configuration](#configuration)
- [Docs](#docs)

---

## Quick start

**Prerequisites:** [uv](https://docs.astral.sh/uv/) (or Python 3.11+ with venv), Xcode 15+ for iOS.

### 1. Backend

```bash
# From repo root
uv sync
uv run scripts/init_db.py    # create SQLite DB and tables
uv run wardrobe              # start API at http://localhost:8000
```

- **Health:** http://localhost:8000/health  
- **OpenAPI:** http://localhost:8000/docs  

### 2. iOS app

- **Open in Xcode:** `ios/Wardrobe/Wardrobe.xcodeproj` (use this project so all sources and the correct scheme are included).
- **Run:** Select the **Wardrobe** scheme and a simulator or device → **⌘R**.
- **Backend URL:** Simulator can use `http://localhost:8000`. For a physical device, set **Settings → API base URL** to your Mac’s IP (e.g. `http://192.168.1.5:8000`). See [Connecting backend ↔ iOS](docs/BACKEND_IOS_CONNECTION.md).

### 3. First use

1. In the app: **Profile** → register or log in (email).
2. **Profile** → set avatar (optional; needed for try-on).
3. **Add** → upload items (Top, Bottom, Jacket, Footwear).
4. **Today** → get a suggested outfit and try-on result (if try-on is configured).

---

## Data model (SQLite)

Default DB path: **`./local/wardrobe.db`** (overridable via `DATABASE_URL`).

### Entity–relationship

- **users** – One per account. Optional **avatar** (FK → `images`).
- **images** – Binary image data (BLOB). Each row is either an **avatar** or a **wardrobe** image; `kind` is `'avatar'` or `'wardrobe'`.
- **wardrobe_items** – User’s clothing items. Each row links a **user**, an **image** (the garment photo), and a **category**.

```
┌─────────────┐       ┌─────────────┐       ┌──────────────────┐
│   users     │       │   images    │       │  wardrobe_items  │
├─────────────┤       ├─────────────┤       ├──────────────────┤
│ id (PK)     │──┐    │ id (PK)     │◄──┐   │ id (PK)          │
│ email       │  │    │ user_id     │   │   │ user_id (FK)     │──► users.id
│ display_name│  │    │ data (BLOB) │   │   │ image_id (FK)    │──► images.id
│ avatar_     │  └───►│ filename    │   └───│ category         │
│   image_id  │       │ content_type│       │ created_at       │
│ created_at  │       │ kind        │       └──────────────────┘
│ updated_at  │       │ created_at  │
└─────────────┘       └─────────────┘
```

### Tables

| Table | Description |
|-------|-------------|
| **users** | Profile: `id`, `email` (UNIQUE), `display_name`, `avatar_image_id` (FK → images), `created_at`, `updated_at`. |
| **images** | Stored images: `id`, `user_id`, `data` (BLOB), `filename`, `content_type`, `kind` (`'avatar'` \| `'wardrobe'`), `created_at`. |
| **wardrobe_items** | One garment per row: `id`, `user_id` (FK → users), `image_id` (FK → images), `category` (`top` \| `bottom` \| `jacket` \| `footwear`), `created_at`. |

### Indexes

- **users:** `idx_users_email` (UNIQUE), `idx_users_avatar`
- **images:** `idx_images_user_id`, `idx_images_kind`, `idx_images_user_kind`, `idx_images_created_at`
- **wardrobe_items:** `idx_wardrobe_items_user_id`, `idx_wardrobe_items_category`, `idx_wardrobe_items_user_category`, `idx_wardrobe_items_image_id`, `idx_wardrobe_items_created_at`

Create/migrate DB: `uv run scripts/init_db.py`. Import files from disk: `uv run scripts/import_uploads_to_db.py` (see [Scripts](#scripts)).

---

## Backend API

| Method | Path | Purpose |
|--------|------|---------|
| **Auth** | | |
| POST | `/auth/register` | Register (email, optional display_name) |
| POST | `/auth/login` | Login by email |
| **Profile** | | |
| GET | `/users/me` | Current user (header: `X-User-Id`) |
| PATCH | `/users/me` | Update display name |
| POST | `/users/me/avatar` | Upload avatar (multipart) |
| **Wardrobe** | | |
| GET | `/wardrobe` | List items (optional `?category=top|bottom|jacket|footwear`) |
| POST | `/wardrobe` | Upload item (multipart: file + category) |
| GET | `/wardrobe/{id}` | One item |
| DELETE | `/wardrobe/{id}` | Delete item |
| **Recommendations & try-on** | | |
| GET | `/recommendations/today` | Suggested outfit + try-on job (returns outfit + `try_on_id`) |
| POST | `/recommendations/try-on` | Start try-on (avatar + garment image ids) |
| GET | `/recommendations/try-on/{id}` | Poll try-on status and `result_image_id` |
| **Images** | | |
| GET | `/images/{id}` | Image bytes (avatar or garment) |
| **Legacy** | | |
| GET / POST | `/items` | Flat item list (no user) |

All user-scoped routes require the **`X-User-Id`** header (set by the app after login). See [API_PROFILE_WARDROBE.md](docs/API_PROFILE_WARDROBE.md) for request/response shapes.

---

## ML & virtual try-on

Try-on places garment images onto the user’s avatar. The backend runs a **configurable script or command**; on failure it can fall back to returning the avatar only.

### Options (pick one)

| Option | Description | Doc |
|--------|-------------|-----|
| **Pillow composite** | Simple overlay (garment pasted on avatar by category). No GPU, good for testing. | [TRY_ON_LOCAL.md](docs/TRY_ON_LOCAL.md) §1 |
| **Diffusion (HF Space)** | Call IDM-VTON via Hugging Face Gradio Space. Set `TRY_ON_SCRIPT=scripts/run_diffusion_tryon.py` and optional `HF_TOKEN`. | [TRY_ON_LOCAL.md](docs/TRY_ON_LOCAL.md) §2 |
| **IDM-VTON local** | Run [IDM-VTON](https://github.com/yisol/IDM-VTON) locally (clone, conda, ckpt, `python gradio_demo/app.py`). Set `DIFFUSION_TRYON_URL=http://127.0.0.1:7860` and `TRY_ON_SCRIPT=.../run_diffusion_tryon.py`. | [IDM_VTON_SETUP.md](docs/IDM_VTON_SETUP.md) |
| **Custom command** | Any script or shell command that accepts `{human}`, `{garment}`, `{output}`, `{category}`. | [TRY_ON_LOCAL.md](docs/TRY_ON_LOCAL.md) |

### Scripts

- **`scripts/run_local_tryon.py`** – Pillow-based composite; category-aware placement and soft edges. Use with `TRY_ON_SCRIPT`.
- **`scripts/run_diffusion_tryon.py`** – Calls a Gradio try-on app: local URL (`DIFFUSION_TRYON_URL`) or HF Space (`yisol/IDM-VTON`). Falls back to Pillow if the call fails.

### Optional dependencies

```bash
uv sync --extra tryon              # Pillow (for run_local_tryon / fallback)
uv sync --extra diffusion-tryon    # gradio_client (for run_diffusion_tryon)
```

---

## iOS app

- **Location:** `ios/Wardrobe/` – open **`Wardrobe.xcodeproj`** (not the nested project under `WardrobeApp/Wardrobe/`).
- **Tabs:** Profile | Closet | Today | Add | Settings.
- **Auth:** Register/login by email; `X-User-Id` is stored and sent on API requests.
- **Structure:**

```
WardrobeApp/
├── WardrobeApp.swift      # App entry
├── ContentView.swift      # Tab bar
├── Views/
│   ├── ProfileView.swift     # Register, login, avatar, display name
│   ├── ClosetView.swift      # List/filter wardrobe (All | Top | Bottom | Jacket | Footwear)
│   ├── TodayView.swift       # Suggested outfit + try-on result image
│   ├── AddItemView.swift     # Category + upload
│   └── SettingsView.swift   # API base URL, logout
├── Services/
│   └── APIClient.swift       # REST: auth, users, wardrobe, recommendations, try-on
└── Models/
    ├── User.swift
    ├── WardrobeItem.swift
    ├── Item.swift (legacy)
    └── Outfit.swift
```

- **Base URL:** Default `http://localhost:8000`. Change in **Settings** for simulator or device; physical device must use your Mac’s IP. See [BACKEND_IOS_CONNECTION.md](docs/BACKEND_IOS_CONNECTION.md) and ATS for HTTP.

---

## Scripts

Run from **project root** (e.g. `uv run python scripts/init_db.py` or `uv run scripts/init_db.py` if wired in pyproject).

| Script | Purpose |
|--------|---------|
| **init_db.py** | Create or migrate SQLite DB (tables + indexes). |
| **import_uploads_to_db.py** | Import image files from `local/uploads` (or `--dir`) into `images` and `wardrobe_items`. Creates a seed user if none exist. `--category`, `--recursive`, `--user-id`. |
| **seed_mock_data.py** | Insert mock image rows (uses `wardrobe.data.mock_images`). |
| **download_mock_images.py** | Download mock images into `local/uploads/mock`. |
| **run_local_tryon.py** | Pillow composite try-on (human + garment → output). Used as `TRY_ON_SCRIPT`. |
| **run_diffusion_tryon.py** | Diffusion try-on via local Gradio or HF Space; fallback Pillow. Used as `TRY_ON_SCRIPT` when using IDM-VTON. |

---

## Configuration

| Variable | Default | Description |
|----------|--------|-------------|
| `DATABASE_URL` | `sqlite:///./local/wardrobe.db` | DB connection (Postgres supported for production). |
| `STORAGE_TYPE` | `local` | `local` or future `s3`. |
| `STORAGE_LOCAL_PATH` | `./local/uploads` | Directory for uploaded files when `STORAGE_TYPE=local`. |
| `TRY_ON_SCRIPT` | – | Path to script: `--human`, `--garment`, `--output`, `--category`. |
| `TRY_ON_COMMAND` | – | Shell command with placeholders `{human}`, `{garment}`, `{output}`, `{category}`. |
| `DIFFUSION_TRYON_URL` | – | Local Gradio try-on server (e.g. `http://127.0.0.1:7860`). |
| `DIFFUSION_TRYON_SPACE` | `yisol/IDM-VTON` | HF Space when not using a local URL. |
| `HF_TOKEN` | – | Hugging Face token for gated Spaces. |

Copy `.env.example` to `.env` and adjust. See [LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) for more.

---

## Docs

| Doc | Contents |
|-----|----------|
| [BACKEND_IOS_CONNECTION.md](docs/BACKEND_IOS_CONNECTION.md) | Run backend, set base URL, allow HTTP (ATS). |
| [API_PROFILE_WARDROBE.md](docs/API_PROFILE_WARDROBE.md) | Profile, wardrobe, try-on APIs and DB schema. |
| [TRY_ON_LOCAL.md](docs/TRY_ON_LOCAL.md) | Local try-on options (Pillow, HF Space, IDM-VTON, env reference). |
| [IDM_VTON_SETUP.md](docs/IDM_VTON_SETUP.md) | Clone and run IDM-VTON locally, then use with Wardrobe. |
| [STRUCTURE.md](docs/STRUCTURE.md) | Repo layout (api, core, ml, data, services). |
| [LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) | Env and local dev notes. |

---

## Development

- **Add dependency:** `uv add <package>`
- **Optional extras:** `uv sync --extra tryon --extra diffusion-tryon`
- **Run backend:** `uv run wardrobe` (from project root)
- **Init DB:** `uv run scripts/init_db.py`

License and contribution policy are defined in the repo.
