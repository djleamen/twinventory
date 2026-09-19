import os
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from pymongo import DESCENDING, MongoClient


PRODUCTS_INDEX = "products"
load_dotenv(Path(__file__).parents[2] / ".env")


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    if "<" in value or ">" in value:
        raise RuntimeError(f"Replace the placeholder in {name}")
    return value


def product_mappings(dimensions: int) -> dict:
    return {
        "properties": {
            "product_id": {"type": "keyword"},
            "title": {"type": "text"},
            "description": {"type": "text"},
            "image_url": {"type": "keyword", "index": False},
            "category": {"type": "keyword"},
            "color": {"type": "keyword"},
            "style": {"type": "keyword"},
            "tags": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": dimensions,
                "index": True,
                "similarity": "cosine",
            },
            "shop_url": {"type": "keyword", "index": False},
            "price": {"type": "scaled_float", "scaling_factor": 100},
            "currency": {"type": "keyword"},
        }
    }


def bootstrap_mongodb() -> None:
    client = MongoClient(required_env("MONGODB_URI"), serverSelectionTimeoutMS=10_000)
    client.admin.command("ping")
    database = client[required_env("MONGODB_DB")]

    if "items" not in database.list_collection_names():
        database.create_collection("items")

    database.items.create_index([("user_id", 1), ("created_at", DESCENDING)])
    client.close()
    print(f"MongoDB ready: {database.name}.items")


def bootstrap_elasticsearch() -> None:
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
    client = Elasticsearch(
        required_env("ELASTICSEARCH_URL"),
        api_key=required_env("ELASTICSEARCH_API_KEY"),
        request_timeout=30,
    )
    client.info()

    if client.indices.exists(index=PRODUCTS_INDEX):
        mapping = client.indices.get_mapping(index=PRODUCTS_INDEX)
        actual = mapping[PRODUCTS_INDEX]["mappings"]["properties"]["embedding"]["dims"]
        if actual != dimensions:
            raise RuntimeError(
                f"Existing {PRODUCTS_INDEX} index uses {actual} dimensions; expected {dimensions}"
            )
    else:
        client.indices.create(
            index=PRODUCTS_INDEX,
            mappings=product_mappings(dimensions),
        )

    print(f"Elasticsearch ready: {PRODUCTS_INDEX} ({dimensions} dimensions, cosine)")


if __name__ == "__main__":
    bootstrap_mongodb()
    bootstrap_elasticsearch()