import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

load_dotenv(Path(__file__).parents[2] / ".env")


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient[dict[str, Any]]:
    return MongoClient(_required_env("MONGODB_URI"), serverSelectionTimeoutMS=3000)


def get_database() -> Database[dict[str, Any]]:
    return get_mongo_client()[_required_env("MONGODB_DB")]


def get_items_collection() -> Collection[dict[str, Any]]:
    return get_database()["items"]


def mongo_is_ready() -> bool:
    get_mongo_client().admin.command("ping")
    return True


try:
    get_mongo_client().admin.command("ping")
    _use_stub = False
except PyMongoError:
    _use_stub = True


def save_item(item: dict) -> str:
    if _use_stub:
        from services.stub_store import save_item as _stub_save
        return _stub_save(item)
    item["created_at"] = datetime.now(timezone.utc)
    result = get_items_collection().insert_one(item)
    return str(result.inserted_id)


def get_items(user_id: str) -> list[dict]:
    if _use_stub:
        from services.stub_store import get_items as _stub_get
        return _stub_get(user_id)
    docs = get_items_collection().find({"user_id": user_id}, {"_id": 0})
    return list(docs)
