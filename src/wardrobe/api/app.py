"""FastAPI app: CORS for iOS, routes for items and images."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wardrobe.api.routes import auth, images, items, recommendations, users, wardrobe

app = FastAPI(title="Wardrobe API", version="0.1.0")

# Allow iOS app (simulator and device) to call this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(wardrobe.router, prefix="/wardrobe", tags=["wardrobe"])
app.include_router(images.router, prefix="/images", tags=["images"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
# Legacy: flat list of images (no user/collection)
app.include_router(items.router, prefix="/items", tags=["items"])


@app.get("/health")
def health():
    return {"status": "ok"}
