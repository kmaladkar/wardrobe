# Connecting the backend to the iOS app

## 1. Run the backend

From the **project root**:

```bash
uv sync
uv run wardrobe
```

The API runs at **http://localhost:8000** (and on your Mac’s IP on port 8000 for other devices).

- **Health:** http://localhost:8000/health  
- **Docs:** http://localhost:8000/docs  

## 2. Point the iOS app at the backend

### Simulator

- The simulator uses your Mac’s network, so **localhost** works.
- In the app, open the **Settings** tab and set **API base URL** to:  
  `http://localhost:8000`  
- Or leave the default in `APIClient.swift`: `http://localhost:8000`.

### Physical iPhone

- The phone cannot use “localhost” (that’s the phone itself).
- Use your **Mac’s IP** on the same Wi‑Fi, e.g. `http://192.168.1.5:8000`.
- Find the IP: **System Settings → Network → Wi‑Fi → Details** (or run `ipconfig getifaddr en0` in Terminal).
- In the app, open **Settings** and set **API base URL** to that address (e.g. `http://192.168.1.5:8000`), then tap **Save URL**.

## 3. Allow HTTP in the iOS app (local dev)

iOS blocks plain **HTTP** by default (App Transport Security). For local development you need to allow it:

1. In Xcode, select the **Wardrobe** project in the sidebar.
2. Select the **Wardrobe** target → **Info** tab.
3. Under **Custom iOS Target Properties**, add:
   - **Key:** `App Transport Security Settings` (dict).
   - Under it, add:
     - **Allow Arbitrary Loads in Web Content**: `NO` (or leave default).
     - **Exception Domains** (dict), or add at the top level:
   - **Key:** `NSAppTransportSecurity` (dict).
   - Under it add: **Allow Arbitrary Loads** = `YES` (for local HTTP only),  
     **or** **Exception Domains** with your host (e.g. `localhost`, or your Mac’s IP).

**Minimal for local HTTP:** add `NSAppTransportSecurity` → `Allow Arbitrary Loads` = `YES`.  
(Only for development; remove or tighten for production.)

Alternatively add to **Info.plist** (if you use one):

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

## 4. Check the connection

1. Backend: `uv run wardrobe` → you should see Uvicorn listening.
2. iOS app: run in Simulator or on device.
3. Open the **Closet** tab: it calls `GET /items`. If the backend has seed data, you’ll see items.
4. Open **Settings** and confirm the base URL; change it if you’re on a real device.

## API endpoints the app uses

| Method | Path | Purpose |
|--------|------|--------|
| GET | /items | List wardrobe items |
| POST | /items | Upload image (multipart: file + category) |
| GET | /images/{id} | Image bytes for item’s image_url |
| GET | /recommendations/today | What to wear today (204 until implemented) |
| GET | /recommendations/complete?item_id=... | Complete outfit (204 until implemented) |
