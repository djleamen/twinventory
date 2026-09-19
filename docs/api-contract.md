# Twinventory Backend Contract

This document is the source of truth for interfaces implemented on `main`.

## Product model

All product reads return normalized records:

```json
{
  "id": "allbirds-123",
  "title": "Tree Runner",
  "description": "Everyday lightweight shoe",
  "image": "https://cdn.example.com/tree-runner.jpg",
  "price": 98.0,
  "category": "Shoes",
  "url": "https://example.com/products/tree-runner"
}
```

`id` is the Elasticsearch document ID. Re-ingestion upserts that document, so changed prices and product details are refreshed without creating duplicates.

Elasticsearch stores one additional internal field, `semantic_text`, generated from the title and description. Its mapping type is `semantic_text`, and it is excluded from API responses.

## Product API

### `GET /products`

Lists products and returns `{"products": [...]}`.

| Parameter | Required | Contract |
| --- | --- | --- |
| `category` | no | Exact category filter |
| `limit` | no | Integer from 1 through 100; defaults to 20 |

`GET /products/list` is a temporary compatibility alias with the same behavior. It is omitted from OpenAPI and should not be used by new frontend code.

### `GET /products/search`

Searches `semantic_text` and returns `{"products": [...]}`.

| Parameter | Required | Contract |
| --- | --- | --- |
| `q` | yes | Non-empty natural-language query |
| `category` | no | Exact category filter |
| `limit` | no | Integer from 1 through 100; defaults to 20 |

### `POST /products/try`

Request:

```json
{
  "image_urls": [
    "https://example.com/person.jpg",
    "https://example.com/product.jpg"
  ]
}
```

At least two URLs are required. The response is `{"image": "<base64>"}`.

## Product ingestion

Fiona owns source acquisition. `backend/scripts/scrape_products.py` reads Shopify store URLs from `backend/config.json`, normalizes records into the product model, and calls `insert_products()`.

DJ owns the Elasticsearch boundary. `insert_products()` uses stable IDs for native Elasticsearch upserts. `backend/scripts/bootstrap_data_infra.py` creates or validates the `semantic_text` product mapping.

Product scraping is a one-off script, not a public API endpoint.

## Inventory integration

MongoDB uses database `twinventory` and collection `items`. The inventory upload/read API is not yet on `main`; `origin/personb` contains a candidate implementation that must be adapted rather than merged wholesale.

The intended inventory shape is:

```json
{
  "user_id": "demo-user",
  "image_url": "/static/generated-id.png",
  "category": "shirt",
  "color": "white",
  "style": "casual",
  "size": "M",
  "embedding": [0.012, -0.031],
  "created_at": "2026-09-19T17:00:00Z"
}
```

Before integration, Person B must use `MONGODB_URI`, reuse `services.mongo_client.get_items_collection()`, remove the in-memory product recommendation stub, and add route/service tests.

## Health API

`GET /health` checks MongoDB and Elasticsearch. It returns HTTP 200 when both are reachable and HTTP 503 when either is unavailable. OpenAI and Browserbase are intentionally excluded because they are only needed by specific operations.