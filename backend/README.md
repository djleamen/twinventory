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
| `OPENAI_API_KEY` | OpenAI key used for try-on, inventory tagging, and item embeddings |
| `MONGODB_URI` | MongoDB connection string used by the health check and inventory services |
| `MONGODB_DB` | MongoDB database name |
| `ELEVENLABS_API_KEY` | ElevenLabs key used by `POST /speech/transcribe` |
| `MESHY_API_KEY` | Meshy client credential |
| `BROWSERBASE_API_KEY` | Browserbase key used by the product scraper |
| `BROWSERBASE_PROJECT_ID` | Browserbase project used by the product scraper |
| `FRONTEND_ORIGINS` | Comma-separated browser origins allowed by CORS; defaults to `http://localhost:5173` |
| `SENTRY_DSN` | Sentry project DSN; when unset, Sentry is fully disabled and the app runs normally |
| `SENTRY_ENVIRONMENT` | Sentry environment tag (e.g. `development`, `production`); defaults to `development` |
| `SENTRY_TRACES_SAMPLE_RATE` | Fraction of requests traced (0.0-1.0); defaults to `1.0` |

MongoDB, Elasticsearch, and OpenAI credentials are required by the current application. ElevenLabs powers voice transcription, Browserbase powers product scraping, and Meshy credentials are loaded by Meshy API calls. Setting `SENTRY_DSN` enables Sentry monitoring.

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

### User profiles

- `GET /users/{username}` returns `username`, `image_url`, and `preferences`.
- `PATCH /users/{username}/preferences` accepts `{"preferences": "..."}`.

Profile records are stored in MongoDB's `users` collection.

### Inventory

- `POST /inventory/upload?user_id=...` accepts multipart field `file`, removes its background, tags and embeds it, stores metadata in MongoDB, and writes the cutout under `/static`.
- `GET /inventory/{user_id}` returns that user's stored items.

Attach persistent storage at `/app/uploads` to retain uploaded files across Railway deployments.

### Voice and 3D

- `POST /speech/transcribe` accepts multipart field `audio` and returns `{"text": "..."}`.
- `POST /models/convert` accepts `{"image_url": "..."}` and returns `{"model_url": "..."}`.

The 3D route returns a GLB model URL for the frontend model viewer.

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

After bootstrapping, add a MongoDB `users` document matching `frontend/src/lib/api/users.ts` and run the product scraper to populate Elasticsearch.

See [../docs/api-contract.md](../docs/api-contract.md) for the complete integration contract.

## Tests

The tests use inert credentials and mock external calls.

```bash
PYTHONPATH=backend .venv-local/bin/python -m unittest discover -s backend/tests -v
```
