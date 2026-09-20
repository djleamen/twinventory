import os
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from routers import inventory
from routers.products import router as products_router
from routers.users import router as users_router
from services.elastic_client import elasticsearch_is_ready
from services.mongo_client import mongo_is_ready

UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def frontend_origins() -> list[str]:
    return [
        origin.strip()
        for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]


app = FastAPI(title="twinventory API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(UPLOADS_DIR)), name="static")
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(products_router)
app.include_router(users_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "success", "message": "Twinventory API"}


@app.get("/health")
def health(response: Response) -> dict[str, str]:
    checks: dict[str, Callable[[], bool]] = {
        "mongodb": mongo_is_ready,
        "elasticsearch": elasticsearch_is_ready,
    }
    result: dict[str, str] = {}
    for name, check in checks.items():
        try:
            result[name] = "ok" if check() else "unavailable"
        except Exception:
            result[name] = "unavailable"

    if "unavailable" in result.values():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
