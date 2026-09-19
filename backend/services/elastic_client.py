import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from elasticsearch import Elasticsearch


PRODUCTS_INDEX = "products"
FILTER_FIELDS = ("category", "color", "style")
load_dotenv(Path(__file__).parents[2] / ".env")


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def embedding_dimensions() -> int:
    return int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))


@lru_cache(maxsize=1)
def get_elasticsearch_client() -> Elasticsearch:
    return Elasticsearch(
        _required_env("ELASTICSEARCH_URL"),
        api_key=_required_env("ELASTICSEARCH_API_KEY"),
        request_timeout=30,
    )


def _validate_embedding(embedding: list[float]) -> None:
    expected = embedding_dimensions()
    if len(embedding) != expected:
        raise ValueError(f"Embedding has {len(embedding)} values; expected {expected}")


def index_product(product: dict[str, Any]) -> None:
    product_id = product.get("product_id")
    embedding = product.get("embedding")
    if not product_id:
        raise ValueError("Product requires product_id")
    if not isinstance(embedding, list):
        raise ValueError("Product requires an embedding list")

    _validate_embedding(embedding)
    get_elasticsearch_client().index(
        index=PRODUCTS_INDEX,
        id=str(product_id),
        document=product,
    )


def search_products(
    query_vector: list[float],
    *,
    query_text: str | None = None,
    filters: dict[str, str] | None = None,
    limit: int = 12,
) -> list[dict[str, Any]]:
    _validate_embedding(query_vector)
    filter_clauses = [
        {"term": {field: value}}
        for field, value in (filters or {}).items()
        if field in FILTER_FIELDS and value
    ]
    bool_query: dict[str, Any] = {"filter": filter_clauses}
    if query_text:
        bool_query["must"] = {
            "multi_match": {
                "query": query_text,
                "fields": ["title^3", "tags^2", "description"],
            }
        }

    knn: dict[str, Any] = {
        "field": "embedding",
        "query_vector": query_vector,
        "k": limit,
        "num_candidates": max(limit * 10, 100),
    }
    if filter_clauses:
        knn["filter"] = {"bool": {"filter": filter_clauses}}

    response = get_elasticsearch_client().search(
        index=PRODUCTS_INDEX,
        query={"bool": bool_query},
        knn=knn,
        size=limit,
        source_excludes=["embedding"],
    )
    return [
        {**hit["_source"], "score": hit["_score"]}
        for hit in response["hits"]["hits"]
    ]


def elasticsearch_is_ready() -> bool:
    get_elasticsearch_client().info()
    return True