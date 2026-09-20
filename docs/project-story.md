# Twinventory Project Story

## Inspiration

Shopping online gives us access to almost anything, but it still leaves one difficult question unanswered: *Will this actually work for me?* Product pages show clothes on models, search results are organized around store categories, and shoppers are left to imagine how separate pieces might look together.

We wanted to make online shopping feel more personal and playful. Twinventory turns a user's photo into the center of the experience, lets them describe an occasion or style in natural language, and helps them build and preview an outfit before following the products back to their stores.

## What it does

Twinventory is an AI-powered virtual closet and shopping experience. A user can:

- choose a profile with a photo and saved style preferences;
- browse products by clothing category;
- search semantically with prompts such as "winter layers" or "something for a summer wedding";
- hold the microphone button to turn speech into the same product search flow;
- add products to outfit slots such as tops, bottoms, outerwear, shoes, and accessories;
- generate a try-on image that combines the user's photo with the selected outfit;
- open product links and continue shopping from the original store;
- upload wardrobe items for background removal, AI tagging, embedding, and storage; and
- preview supported images as interactive 3D models.

## How we built it

We built Twinventory as a Next.js and TypeScript frontend backed by a Python FastAPI service.

The product pipeline uses Browserbase and Playwright to collect public Shopify product data from configured stores. We normalize each record into a shared product model and ingest it into Elasticsearch. Elasticsearch stores searchable semantic text built from each product's title and description, which lets the API rank products from natural-language searches while still supporting exact category filters.

OpenAI powers the image-generation try-on flow. The frontend sends the user's photo first, followed by the selected product images, and renders the returned image directly in the closet view. OpenAI also supports the inventory pipeline by generating structured clothing tags and embeddings.

MongoDB Atlas stores user profiles, style preferences, and uploaded inventory metadata. Uploaded clothing images pass through rembg to create clean cutouts before being served by the backend. ElevenLabs converts recorded speech into text, feeding the transcript into the same search path as typed queries. Meshy model URLs are rendered with Google's `<model-viewer>` component for an interactive 3D view.

We instrumented the FastAPI backend with Sentry logs, traces, database spans, ingestion spans, and OpenAI monitoring. The frontend is deployed on Vercel, the backend runs on Railway, and the custom `twinventory.fashion` domain connects the complete experience. GitHub Actions runs the backend tests, frontend lint, and production build on every push and pull request.

## Challenges we ran into

One of our most time-consuming problems appeared in the Browserbase product-ingestion pipeline. Some product records contained image fields that were missing or were not usable source URLs. Those records could reach the product listing but fail when the frontend tried to display them.

To isolate the issue, we piped the JSON returned from Browserbase into our debugging workflow and inspected the image fields across a representative group of store URLs. We independently checked that sample image URLs returned `200 OK` responses and could be downloaded. We then added a validation gate in the scraper that rejects products with missing image data or malformed non-HTTP URLs before they are inserted into Elasticsearch. That gave the search index a consistent product contract and kept broken image records out of the shopping experience.

Coordinating several external services also required careful boundaries. Each service has different credentials, response formats, latency, and failure modes. We kept one FastAPI application with domain routers, normalized responses at the API boundary, loaded operation-specific clients only when needed, and exposed readable errors to the frontend. Sentry traces helped us follow requests across product ingestion, Elasticsearch, and OpenAI instead of debugging each integration in isolation.

## Accomplishments that we're proud of

We are proud that Twinventory became a complete, deployed shopping flow rather than a collection of disconnected demos. A user can move from a personal profile to real product discovery, assemble an outfit, generate a visual try-on, and continue to the original store without leaving the experience.

We also built one product around several technologies without making the interactions feel separate. Voice and typed input share one semantic-search path. Browsing and recommendations return the same product contract. User preferences and inventory live in MongoDB, products remain searchable in Elasticsearch, and observability spans the ingestion and AI workflows.

Finally, we built repeatable engineering foundations during a short hackathon: a normalized API contract, idempotent Elasticsearch upserts, infrastructure bootstrap scripts, automated tests, continuous integration, health checks, production deployment, and custom-domain routing.

## What we learned

We learned that AI shopping experiences depend as much on data quality as they do on model quality. A powerful search or image model cannot compensate for products with broken images, inconsistent categories, or unstable identifiers. Validating and normalizing records before indexing made every downstream feature more dependable.

We also learned to design integrations around shared user actions instead of around vendors. Speech transcription becomes useful because it feeds the existing search box. Semantic search becomes useful because its results fit the same outfit slots as browsed products. Image generation becomes useful because it preserves the selected products and links users back to the stores.

Observability was most valuable when we added it around boundaries: browser sessions, ingestion batches, database searches, and AI calls. Those traces gave us a much clearer picture of where time was spent and where failures originated.

## What's next for Twinventory

Next, we want to expand Twinventory into a persistent personal wardrobe. Users will be able to add more profile photos, organize uploaded clothing, combine owned items with store products, and save complete outfits for different occasions.

We also plan to enrich recommendations with saved preferences and inventory context, add more product sources, and improve ranking across style, color, occasion, and price. The 3D experience can grow into a richer spatial closet, while stronger ingestion validation and additional automated end-to-end tests will support a larger catalog and more users.
