"""FastAPI app: CORS for iOS, routes for items and images."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wardrobe.api.routes import images, items, recommendations

app = FastAPI(title="Wardrobe API", version="0.1.0")

# Allow iOS app (simulator and device) to call this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(images.router, prefix="/images", tags=["images"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])


@app.get("/health")
def health():
    return {"status": "ok"}
