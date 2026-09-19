import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


load_dotenv(Path(__file__).parents[2] / ".env")


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient[dict[str, Any]]:
    return MongoClient(_required_env("MONGODB_URI"), serverSelectionTimeoutMS=10_000)


def get_database() -> Database[dict[str, Any]]:
    return get_mongo_client()[_required_env("MONGODB_DB")]


def get_items_collection() -> Collection[dict[str, Any]]:
    return get_database()["items"]


def mongo_is_ready() -> bool:
    get_mongo_client().admin.command("ping")
    return True