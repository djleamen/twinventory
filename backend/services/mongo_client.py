from dataclasses import dataclass

from pymongo import MongoClient, ReturnDocument

from utils import _get_required_env

USERS_COLLECTION = "users"

client = MongoClient(
    _get_required_env("MONGODB_URI"),
    serverSelectionTimeoutMS=10_000,
)
database = client[_get_required_env("MONGODB_DB")]

users = database[USERS_COLLECTION]


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
