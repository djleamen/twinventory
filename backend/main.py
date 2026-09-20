import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration

from collections.abc import Callable

from pathlib import Path

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from routers import inventory
from routers.models import router as models_router
from routers.products import router as products_router
from routers.speech import router as speech_router
from routers.users import router as users_router
from services.elastic_client import elasticsearch_is_ready
from services.mongo_client import mongo_is_ready

load_dotenv(Path(__file__).parent / ".env")

def _init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        logging.getLogger(__name__).warning(
            "SENTRY_DSN not set; Sentry tracing/logging/AI monitoring disabled."
        )
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        send_default_pii=True,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
        enable_logs=True,
        integrations=[
            LoggingIntegration(sentry_logs_level=logging.INFO),
            OpenAIIntegration(include_prompts=False),
        ],
    )


_init_sentry()

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
app.include_router(speech_router)
app.include_router(users_router)
app.include_router(models_router)


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

# test sentry
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
