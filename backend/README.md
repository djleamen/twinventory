# Twinventory backend

FastAPI service for product discovery and image-based try-on.

## Setup

Python 3.13 or later is required. From the repository root:

```bash
python3.13 -m venv .venv-local
.venv-local/bin/pip install -e backend
cp .env.example .env
```

Fill in the required values in `.env`, then start the API:

```bash
PYTHONPATH=backend .venv-local/bin/uvicorn main:app --reload --env-file .env
```

The API is available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.

## Environment

| Variable | Purpose |
| --- | --- |
| `ELASTICSEARCH_URL` | Elastic Cloud endpoint containing the `products` index |
| `ELASTICSEARCH_API_KEY` | Elastic API key |
| `OPENAI_API_KEY` | OpenAI key used for try-on image generation |
| `MONGODB_URI` | MongoDB connection string used by the health check and inventory services |
| `MONGODB_DB` | MongoDB database name |
| `FRONTEND_ORIGINS` | Comma-separated browser origins allowed by CORS; defaults to `http://localhost:5173` |

An OpenAI key is currently required when the application starts, even when only product endpoints are used.

## Product schema

Every product response has the same shape:

```json
{
	"id": "product-123",
	"title": "Blue Formal Dress",
	"description": "Lightweight formal summer dress",
	"image": "https://example.com/dress.jpg",
	"price": 89.0,
	"category": "dress",
	"url": "https://example.com/products/dress"
}
```

Product ingestion uses `services.elastic_client.insert_products()`. It writes `title` and `description` into the internal `semantic_text` search field, which is excluded from API responses.

## Endpoints

### `GET /health`

Returns `200` when MongoDB and Elasticsearch are reachable. Returns `503` with the unavailable dependency identified otherwise.

### `GET /products/list`

Lists up to 20 products. The optional `category` query parameter applies an exact category filter.

```text
GET /products/list?category=dress
```

### `GET /products/search`

Searches the `semantic_text` field. `query` is required and `category` is optional.

```text
GET /products/search?query=winter%20clothing&category=coat
```

### `POST /products/try`

Combines the supplied image URLs and returns a base64-encoded generated image. Send the user's image first, followed by the selected product images.

```json
{
	"image_urls": [
		"https://example.com/person.jpg",
		"https://example.com/coat.jpg"
	]
}
```

Response:

```json
{
	"image": "base64-encoded-image"
}
```

## Tests

The tests use inert credentials and mock all external calls.

```bash
PYTHONPATH=backend .venv-local/bin/python -m unittest discover -s backend/tests -v
```
