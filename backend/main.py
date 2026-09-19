from collections.abc import Callable

from fastapi import FastAPI, Response, status

from routers.products import router as products_router
from routers.recs import router as recs_router
from services.elastic_client import elasticsearch_is_ready
from services.mongo_client import mongo_is_ready

app = FastAPI()
app.include_router(recs_router)
app.include_router(products_router)


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


