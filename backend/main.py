from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from routers import inventory, recs

UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="twinventory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(UPLOADS_DIR)), name="static")
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(recs.router, prefix="/recs", tags=["recs"])


@app.get("/")
def read_root():
    return {"status": "ok", "message": "twinventory API running"}
