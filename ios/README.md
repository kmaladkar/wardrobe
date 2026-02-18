# Wardrobe – iPhone App

Basic iOS app that talks to the Python backend. Implements the flows described in [IDEAS.md](../IDEAS.md): **catalog (closet)**, **what to wear today**, **add item (camera)**, and **settings**.

## How to open in Xcode

There is no `.xcodeproj` in the repo yet—only the Swift source in **`ios/WardrobeApp/`**. Use one of these:

### Option A: One-time project creation (recommended)

1. Open **Xcode**.
2. **File → New → Project** → choose **App** → Next.
3. Set **Product Name:** `Wardrobe`, **Team:** your team, **Organization Identifier:** e.g. `com.yourname`, **Interface:** SwiftUI, **Language:** Swift → Next.
4. **Save** into the repo’s **`ios`** folder (e.g. `.../wardrobe/ios/`). This creates `ios/Wardrobe.xcodeproj`.
5. In the left sidebar (Project Navigator), **right‑click the blue “Wardrobe” project** (or the yellow Wardrobe group) → **Add Files to "Wardrobe"…**.
6. Select the **`WardrobeApp`** folder (inside `ios/`), leave **“Create groups”** selected, optionally **“Copy items if needed”** if you want a copy (usually leave unchecked so it uses the repo files).
7. Click **Add**. You should see `WardrobeApp`, `Models`, `Views`, `Services` and all `.swift` files.
8. If Xcode created its own `ContentView.swift` / `WardrobeApp.swift`, **delete those default files** (Move to Trash) so the ones from `WardrobeApp` are the only app entry and content view.
9. **File → Open** (or **Open Recent**) and choose **`ios/Wardrobe.xcodeproj`** anytime to open the app.

### Option B: Open the folder

- In Xcode: **File → Open** → select the **`ios`** folder (or the **`WardrobeApp`** folder). Xcode may not treat it as a runnable app until you have a project; use **Option A** to create the project once, then open **`ios/Wardrobe.xcodeproj`** from then on.

## Requirements

- Xcode 15+ (Swift 5.9, iOS 17)
- Backend running (`uv run wardrobe`) and reachable from device/simulator

## After opening

1. **Configure base URL** in the app: run the app, open the **Settings** tab, set the API URL (e.g. `http://localhost:8000` for simulator).
2. **Run:** pick a simulator or device and press **⌘R**.

## Structure (what’s required)

```
WardrobeApp/
├── WardrobeApp.swift      # App entry
├── ContentView.swift      # Tab bar: Closet | Today | Add | Settings
├── Views/
│   ├── ClosetView.swift       # Virtual closet – list/filter items
│   ├── TodayView.swift       # “What to wear today” – daily suggestion
│   ├── AddItemView.swift     # Camera + upload new item
│   └── SettingsView.swift    # Profile, API URL, logout
├── Services/
│   └── APIClient.swift       # REST client (auth, items, recommendations)
└── Models/
    ├── Item.swift            # Wardrobe item (id, image_url, category, …)
    └── Outfit.swift          # Outfit (item_ids, occasion, …)
```

## Backend contract (to implement)

The app expects these endpoints; implement them in the Python FastAPI backend:

| Method | Path | Purpose |
|--------|------|--------|
| POST | `/auth/login` | Login (e.g. email/password or token) |
| GET  | `/items` | List current user’s wardrobe items |
| POST | `/items` | Create item (multipart: image + metadata) |
| GET  | `/recommendations/today` | “What to wear today” |
| GET  | `/recommendations/complete?item_id=…` | “Complete the outfit” for one item |

See `APIClient.swift` for the exact request/response shapes.
