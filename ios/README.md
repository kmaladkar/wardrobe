# Wardrobe – iPhone App

Basic iOS app that talks to the Python backend. Implements the flows described in [IDEAS.md](../IDEAS.md): **catalog (closet)**, **what to wear today**, **add item (camera)**, and **settings**.

## Requirements

- Xcode 15+ (Swift 5.9, iOS 17)
- Backend running (e.g. `uv run main.py` with FastAPI later) and reachable from device/simulator

## Setup

1. **Create a new Xcode project**
   - File → New → Project → **App**
   - Product Name: **Wardrobe**
   - Team: your team
   - Organization Identifier: e.g. `com.yourname`
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Save inside this repo under `ios/` (e.g. `ios/Wardrobe.xcodeproj`).

2. **Add the app source**
   - Delete the default `ContentView.swift` and `WardrobeApp.swift` (or keep and replace contents).
   - Drag the `WardrobeApp` folder into the Xcode project (Copy items if needed, Create groups).

3. **Configure base URL**
   - In **SettingsView** or **APIClient**, set `baseURL` to your backend (e.g. `http://localhost:8000` for simulator, or your machine’s IP for a real device).

4. **Run**
   - Select a simulator or device and run (⌘R).

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
