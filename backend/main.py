import os
from collections.abc import Callable

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from routers.recs import router as recs_router
from services.elastic_client import elasticsearch_is_ready
from services.mongo_client import mongo_is_ready


def frontend_origins() -> list[str]:
    return [
        origin.strip()
        for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(recs_router)


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


