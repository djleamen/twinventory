from dataclasses import dataclass
from datetime import UTC, datetime

from pymongo import DESCENDING, MongoClient, ReturnDocument

from utils import _get_required_env

USERS_COLLECTION = "users"
ITEMS_COLLECTION = "items"

client = MongoClient(
    _get_required_env("MONGODB_URI"),
    serverSelectionTimeoutMS=10_000,
)
database = client[_get_required_env("MONGODB_DB")]

users = database[USERS_COLLECTION]
items = database[ITEMS_COLLECTION]


@dataclass
class User:
    username: str
    image_url: str
    preferences: str


def mongo_is_ready() -> bool:
    client.admin.command("ping")
    return True


def get_user(username: str) -> User | None:
    document = users.find_one({"username": username}, {"_id": 0})
    return User(**document) if document else None


def update_user(username: str, preferences: str) -> User | None:
    document = users.find_one_and_update(
        {"username": username},
        {"$set": {"preferences": preferences}},
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER,
    )
    return User(**document) if document else None


def save_item(item: dict) -> str:
    document = {**item, "created_at": datetime.now(UTC)}
    return str(items.insert_one(document).inserted_id)


def get_items(user_id: str) -> list[dict]:
    documents = items.find({"user_id": user_id}).sort("created_at", DESCENDING)
    result = []
    for document in documents:
        item_id = str(document.pop("_id"))
        result.append({**document, "item_id": item_id})
    return result
