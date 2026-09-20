# Twinventory Project Story

## Inspiration

Shopping online gives us access to almost anything, but it still leaves one difficult question unanswered: *Will this actually work for me?* Product pages show clothes on models, search results are organized around store categories, and shoppers are left to imagine how separate pieces might look together.

We wanted to make online shopping feel more personal and playful. Twinventory turns a user's own photo into the center of the experience, lets them describe an occasion or style in natural language, and helps them build and preview an outfit before following the products back to their stores. It brings the useful parts of a personal closet, a stylist, and a product search engine into one visual workflow.

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

We split Twinventory into a Next.js 16 frontend using React 19, TypeScript, and Tailwind CSS, and a Python FastAPI backend managed with `uv`.

The product pipeline drives a headless Chromium session through Browserbase and Playwright to collect public data from real Shopify stores' `/products.json` endpoints. We normalize each listing into a shared product model and upsert it into Elasticsearch by a stable product ID, so rerunning ingestion refreshes products instead of creating duplicates. Elasticsearch's `semantic_text` field combines each product's title and description, giving us semantic product discovery while preserving exact category filters.

OpenAI powers the virtual try-on flow through the Responses API and its image-generation tool. The frontend sends the user's photo first, followed by the selected product images, and renders the returned base64 image directly in the closet view. OpenAI also supports the inventory pipeline: `gpt-4o-mini` returns structured category, color, style, and size tags, while `text-embedding-3-small` turns those tags into a searchable vector.

MongoDB Atlas stores user profiles, style preferences, and uploaded inventory metadata. Uploaded clothing images pass through rembg's `birefnet-general` model to create clean cutouts before being served by the backend. For voice search, the browser records audio with the MediaRecorder API and sends it to ElevenLabs' `scribe_v2` speech-to-text model; the transcript is placed into the same search field and follows the same Elasticsearch path as typed input. The 3D view requests a Meshy model URL through FastAPI and renders the resulting GLB with Google's `<model-viewer>` web component, including camera controls and auto-rotation.

We instrumented the FastAPI backend with Sentry logs, traces, database spans, ingestion spans, and OpenAI monitoring. The frontend is deployed on Vercel, the backend runs on Railway, and the custom `twinventory.fashion` domain connects the complete experience. GitHub Actions runs the backend tests, frontend lint, and production build on every push and pull request.

## Challenges we ran into

One of our most time-consuming problems appeared in the Browserbase product-ingestion pipeline. Some product records contained image fields that were missing or were not usable source URLs. Those records could reach the product listing but fail when the frontend tried to display them.

To isolate the issue, we piped the JSON returned from Browserbase into our debugging workflow and inspected the image fields across a representative group of store URLs. We independently checked that sample image URLs returned `200 OK` responses and could be downloaded. We then added a validation gate in the scraper that rejects products with missing image data or malformed non-HTTP URLs before they are inserted into Elasticsearch. That gave the search index a consistent product contract and kept broken image records out of the shopping experience.

Coordinating several external services also required careful boundaries. Each service has different credentials, response formats, latency, and failure modes. We kept one FastAPI application with domain routers, normalized responses at the API boundary, and exposed readable errors to the frontend. Sentry traces helped us follow requests across product ingestion, Elasticsearch, and OpenAI instead of debugging each integration in isolation.

## Accomplishments that we're proud of

We are proud that Twinventory became a complete, deployed shopping flow rather than a collection of disconnected demos. A user can move from a personal profile to real product discovery, assemble an outfit across several clothing slots, generate a visual try-on, compare it with the original photo, and continue to the original store without leaving the experience.

We also built one product around several technologies without making the interactions feel separate. Voice and typed input share one semantic-search path. Browsing and recommendations return the same product contract. User preferences and inventory live in MongoDB, products remain searchable in Elasticsearch, and observability spans the ingestion and AI workflows.

Finally, we built repeatable engineering foundations during a short hackathon: a normalized API contract, idempotent Elasticsearch upserts, infrastructure bootstrap scripts, automated tests, continuous integration, health checks, production deployment across Vercel and Railway, and custom-domain routing.

## What we learned

We learned that AI shopping experiences depend as much on data quality as they do on model quality. A powerful search or image model cannot compensate for products with broken images, inconsistent categories, or unstable identifiers. Validating and normalizing records before indexing made every downstream feature more dependable, while stable IDs made the ingestion process safely repeatable.

We also learned to design integrations around shared user actions instead of around vendors. Speech transcription becomes useful because it feeds the existing search box. Semantic search becomes useful because its results fit the same outfit slots as browsed products. Image generation becomes useful because it preserves the selected products and links users back to the stores.

Observability was most valuable at system boundaries: browser sessions, ingestion batches, database searches, and AI calls. Those traces gave us a much clearer picture of where time was spent and where failures originated. We also learned that a single shared API contract saves enormous integration time when several people are building the frontend, data layer, and AI services in parallel.

## What's next for Twinventory

Next, we want to expand Twinventory into a richer persistent wardrobe. Users will be able to organize uploaded clothing, combine owned items with store products, and save complete outfits for different occasions.

We also plan to enrich recommendations with saved preferences and inventory context, add more product sources, and improve ranking across style, color, occasion, and price. The 3D experience can grow into a spatial closet, while a larger catalog and additional automated end-to-end tests will help Twinventory scale to more styles, stores, and shoppers.
