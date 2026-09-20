import logging
from dataclasses import asdict, dataclass

import sentry_sdk
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from utils import _get_required_env

logger = logging.getLogger(__name__)

PRODUCTS_INDEX = "products"

client = Elasticsearch(
    _get_required_env("ELASTICSEARCH_URL"),
    api_key=_get_required_env("ELASTICSEARCH_API_KEY"),
    request_timeout=30,
)


@dataclass
class Product:
    id: str
    title: str
    description: str
    image: str
    price: float
    category: str
    url: str


def elasticsearch_is_ready() -> bool:
    return client.ping()


def insert_products(products: list[Product]) -> None:
    if not products:
        return

    actions = [
        {
            "_index": PRODUCTS_INDEX,
            "_id": product.id,
            "_source": {
                **asdict(product),
                "semantic_text": f"{product.title}\n\n{product.description}",
            },
        }
        for product in products
    ]

    with sentry_sdk.start_span(op="db.bulk_index", name="elasticsearch.bulk") as span:
        span.set_data("elasticsearch.index", PRODUCTS_INDEX)
        span.set_data("elasticsearch.actions_count", len(actions))
        bulk(client, actions)


def query_products(
    query: str,
    category: str | None = None,
    limit: int = 20,
) -> list[Product]:
    filters = [{"term": {"category": category}}] if category else []

    with sentry_sdk.start_span(op="db.search", name="elasticsearch.search") as span:
        span.set_data("elasticsearch.index", PRODUCTS_INDEX)
        span.set_data("query.category", category)
        span.set_data("query.limit", limit)

        response = client.search(
            index=PRODUCTS_INDEX,
            query={
                "bool": {
                    "must": [{"match": {"semantic_text": query}}],
                    "filter": filters,
                }
            },
            size=limit,
            source_excludes=["semantic_text"],
        )

        results = [Product(**hit["_source"]) for hit in response["hits"]["hits"]]
        span.set_data("results.count", len(results))
        return results


def list_products(
    category: str | None = None,
    limit: int = 20,
) -> list[Product]:
    query = (
        {"term": {"category": category}}
        if category
        else {"match_all": {}}
    )

    with sentry_sdk.start_span(op="db.search", name="elasticsearch.search") as span:
        span.set_data("elasticsearch.index", PRODUCTS_INDEX)
        span.set_data("query.category", category)
        span.set_data("query.limit", limit)

        response = client.search(
            index=PRODUCTS_INDEX,
            query=query,
            size=limit,
            source_excludes=["semantic_text"],
        )

        results = [Product(**hit["_source"]) for hit in response["hits"]["hits"]]
        span.set_data("results.count", len(results))
        return results
