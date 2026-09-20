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
| `BROWSERBASE_API_KEY` | Browserbase key used by the product scraper |
| `BROWSERBASE_PROJECT_ID` | Browserbase project used by the product scraper |
| `FRONTEND_ORIGINS` | Comma-separated browser origins allowed by CORS; defaults to `http://localhost:5173` |
| `SENTRY_DSN` | Sentry project DSN; when unset, Sentry is fully disabled and the app runs normally |
| `SENTRY_ENVIRONMENT` | Sentry environment tag (e.g. `development`, `production`); defaults to `development` |
| `SENTRY_TRACES_SAMPLE_RATE` | Fraction of requests traced (0.0-1.0); defaults to `1.0` |

OpenAI credentials are loaded only when try-on is called. Browserbase credentials are loaded only when the scraper runs.
Sentry is optional: the app boots normally when `SENTRY_DSN` is unset.

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

### `GET /products`

Lists products. `category` is an optional exact-match filter; `limit` accepts 1 through 100 and defaults to 20.

```text
GET /products?category=Shoes&limit=100
```

`GET /products/list` remains available as a temporary compatibility alias but is omitted from OpenAPI.

### `GET /products/search`

Searches the `semantic_text` field. `q` is required; `category` and `limit` are optional.

```text
GET /products/search?q=winter%20clothing&category=coat&limit=20
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

At least two image URLs are required: the user's image and one selected product.

## Product ingestion

Configure shops in `backend/config.json`, then run the scraper from the repository root:

```bash
PYTHONPATH=backend .venv-local/bin/python backend/scripts/scrape_products.py
```

The scraper normalizes Shopify products and upserts them into Elasticsearch by stable product ID. It is intentionally not exposed as a public HTTP endpoint.

To create or verify MongoDB and Elasticsearch infrastructure:

```bash
.venv-local/bin/python backend/scripts/bootstrap_data_infra.py
```

See [../docs/api-contract.md](../docs/api-contract.md) for the complete integration contract.

## Tests

The tests use inert credentials and mock all external calls.

```bash
PYTHONPATH=backend .venv-local/bin/python -m unittest discover -s backend/tests -v
```
