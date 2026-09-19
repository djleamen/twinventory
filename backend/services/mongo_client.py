import os
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from services.stub_store import save_item as _stub_save, get_items as _stub_get

try:
    _client = MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=3000)
    _db = _client[os.environ["MONGODB_DB"]]
    _db.command("ping")
    _items = _db["items"]
    _use_stub = False
    print("[mongo] connected to Atlas")
except PyMongoError as e:
    _use_stub = True
    print(f"[mongo] Atlas unreachable ({e}), falling back to in-memory stub")


def save_item(item: dict) -> str:
    if _use_stub:
        return _stub_save(item)
    item["created_at"] = datetime.now(timezone.utc)
    result = _items.insert_one(item)
    return str(result.inserted_id)


def get_items(user_id: str) -> list[dict]:
    if _use_stub:
        return _stub_get(user_id)
    docs = _items.find({"user_id": user_id}, {"_id": 0})
    return list(docs)
