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

Failure modes return JSON `{"detail": "..."}` suitable for direct display:

| Status | Meaning |
| --- | --- |
| `422` | The model declined to generate an image for these items |
| `502` | The OpenAI call failed; the client may retry |

## Product ingestion

Fiona owns source acquisition. `backend/scripts/scrape_products.py` reads Shopify store URLs from `backend/config.json`, normalizes records into the product model, and calls `insert_products()`.

DJ owns the Elasticsearch boundary. `insert_products()` uses stable IDs for native Elasticsearch upserts. `backend/scripts/bootstrap_data_infra.py` creates or validates the `semantic_text` product mapping.

Product scraping is a one-off script, not a public API endpoint.

## User API

### `GET /users/{username}`

Returns an existing profile:

```json
{
  "username": "steve",
  "image_url": "https://example.com/steve.jpg",
  "preferences": "Jeans, muted clothing"
}
```

Returns `404` when the profile does not exist.

### `PATCH /users/{username}/preferences`

Accepts `{"preferences": "..."}`, updates the existing profile, and returns the updated profile. Returns `404` when the profile does not exist.

Profiles are provisioned in MongoDB's `users` collection.

## Inventory API

MongoDB uses the configured `MONGODB_DB` database and the `items` collection.

### `POST /inventory/upload`

Requires query parameter `user_id` and multipart field `file`. The service removes the background, generates tags and an embedding, stores the item in MongoDB, and writes a PNG cutout under `/static`.

Response:

```json
{
  "item_id": "mongo-object-id",
  "tags": {
    "category": "shirt",
    "color": "white",
    "style": "casual",
    "size": "M"
  },
  "image_url": "/static/generated-id.png"
}
```

### `GET /inventory/{user_id}`

Returns `{"user_id": "...", "items": [...]}`. Stored items use this shape:

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

Uploaded files are served from `/static`; production deployments persist that directory at `/app/uploads`.

## Speech API

### `POST /speech/transcribe`

Accepts multipart field `audio` and returns `{"text": "..."}`. An empty upload returns `400`.

## 3D model API

### `POST /models/convert`

Accepts `{"image_url": "..."}` and returns `{"model_url": "..."}` for the frontend model viewer.

## Health API

`GET /health` checks MongoDB and Elasticsearch. It returns HTTP 200 when both are reachable and HTTP 503 when either is unavailable.

`GET /` returns a basic API status message. `GET /sentry-debug` raises a test exception for Sentry verification.

## MVP boundary

The MVP flow is seeded profile → product browse/search → outfit selection → try-on → source-store link. Voice transcription supplies search text. Profile preferences, inventory upload and retrieval, and 3D model previews are also available through the API.