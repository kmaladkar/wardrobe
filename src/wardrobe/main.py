"""Run the Wardrobe API server. Usage: uv run wardrobe"""

import uvicorn

from wardrobe.api.app import app


def main() -> None:
    uvicorn.run(
        app,
        host="0.0.0.0",  # listen on all interfaces so iOS device can reach Mac
        port=8000,
    )


if __name__ == "__main__":
    main()
