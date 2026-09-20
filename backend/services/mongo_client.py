from dataclasses import dataclass
from datetime import UTC, datetime

from pymongo import DESCENDING, MongoClient, ReturnDocument

from utils import _get_required_env

USERS_COLLECTION = "users"
ITEMS_COLLECTION = "items"
MODEL_TASKS_COLLECTION = "model_tasks"
TRY_ON_RESULTS_COLLECTION = "try_on_results"

client = MongoClient(
    _get_required_env("MONGODB_URI"),
    serverSelectionTimeoutMS=10_000,
)
database = client[_get_required_env("MONGODB_DB")]

users = database[USERS_COLLECTION]
items = database[ITEMS_COLLECTION]
model_tasks = database[MODEL_TASKS_COLLECTION]
try_on_results = database[TRY_ON_RESULTS_COLLECTION]


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


def list_users() -> list[User]:
    return [User(**document) for document in users.find({}, {"_id": 0})]


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


def get_model_task(image_url: str) -> str | None:
    document = model_tasks.find_one({"image_url": image_url})
    return document["task_id"] if document else None


def save_model_task(image_url: str, task_id: str) -> None:
    model_tasks.update_one(
        {"image_url": image_url},
        {"$set": {"task_id": task_id, "created_at": datetime.now(UTC)}},
        upsert=True,
    )


def get_try_on_result(cache_key: str) -> str | None:
    document = try_on_results.find_one({"cache_key": cache_key})
    return document["image"] if document else None


def try_on_result_exists(cache_key: str) -> bool:
    return try_on_results.find_one({"cache_key": cache_key}, {"_id": 1}) is not None


def save_try_on_result(cache_key: str, image: str) -> None:
    try_on_results.update_one(
        {"cache_key": cache_key},
        {"$set": {"image": image, "created_at": datetime.now(UTC)}},
        upsert=True,
    )
