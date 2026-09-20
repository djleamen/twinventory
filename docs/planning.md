## **Twinventory / miirror.tech Architecture**![][image1]

> **Current backend contract:** product browsing and search use `GET /products` and `GET /products/search?q=...`; image try-on uses `POST /products/try`. Products use `{id, title, description, image, price, category, url}`. See [`api-contract.md`](api-contract.md) and [`status.md`](status.md); they supersede stale implementation details in this original plan.

**Three flows, that's the whole app:**

1. **Avatar:** photo goes to a vision LLM with a strict JSON schema (skin tone, hair style/color, face shape, eye/brow/mouth type, glasses). Frontend applies that to one base GLB. Trick that saves your weekend: Mii faces are 2D decals on a head, not sculpted geometry. So eyes, brows, and mouth are texture swaps, hair is a mesh swap, skin is a material color. No blendshape authoring needed. The guided editor is just a UI over the same JSON.  
2. **Inventory:** item photo goes through rembg, the vision LLM tags it (category, color, style), you embed it and store it. Clothes stay as 2D cutouts layered over the avatar in the closet view. Furniture gets sent to an image-to-3D API as a background job and drops into the grid room when the GLB is ready.  
3. **Recs:** run semantic text search against products in Elasticsearch, show results as cutouts on the avatar, and include the product link on the card.

**Build order with cut lines:** avatar from photo (the wow moment, do it first), inventory grid, closet mix and match, recs with buy links, then the room. If you run out of time, the room is what gets cut. A half-working Sims room hurts the demo more than no room.

## **Tracks that apply**

**Strong fits, select these:**

* **Shopify: Hack Shopping with AI.** Your best sponsor shot. They want experiments where AI meets commerce and list customer experience enhancements as a theme. "Try it on your cartoon self before you buy" is exactly that. Pulling real products through the Shopify API is optional per their rules but obviously helps.  
* **Finalists (main award).** They explicitly say projects can be playful or wonderfully weird and don't need a business plan. A Mii of yourself in a Clueless closet is squarely that. Note that the judging pitch should be a live demo rather than slides, which is another reason to nail the avatar flow.  
* **MLH: MongoDB Atlas.** You're using it anyway. Free entry.  
* **MLH: GoDaddy domain.** Register a punny name, takes five minutes.  
* Elastic  
* Sentry  
* OpenAI

**Pick one LLM lane:**

* **MLH: Gemini API** if Gemini does your vision extraction and tagging. Low bar.  
* **OpenAI: API Prizes** if you use the OpenAI API instead, but they also judge how meaningfully Codex supported your build process, so you'd need to actually develop with Codex and show one concrete way it improved things in the demo. Higher bar, better prizes. You can technically enter both by splitting vision and recs across providers, but I wouldn't add integration work just for that.

**Worth it if you have spare hands:**

* **Baseten.** Host an open image-to-3D model (	) or your rembg/embedding step there instead of calling a closed API. The grand prize includes an SF trip and final round interviews, so it's the highest upside add-on, but also the one most likely to eat 6 hours.  
* **Sentry.** Requires at least two products beyond error monitoring, and they judge on how observability actually shaped the build. Your slow 3D generation job is a natural tracing story, and the prize is a guaranteed interview.  
* **MLH: Vultr** if you deploy the backend there. **MLH: ElevenLabs** if you give the closet a stylist voice, which is cheap and fun but pure garnish.  
* **Backboard.io** only if you route your LLM calls and style-profile memory through it from the start. Retrofitting is not worth it.

&nbsp;

&nbsp;

### **Task → Owner mapping**

1. **Photo capture \+ OpenAI vision→JSON, applied to avatar** — Person A  
2. **Three.js rendering of the avatar in-browser** — Person A (tightly coupled to \#1, same person owns the whole avatar pipeline)  
3. **MongoDB (system of record)** — Person C  
4. **Elasticsearch (vector search)** — Person C  
5. **Recs: preference/prompt-driven search \+ Shopify sourcing** — Person B \+ Person D  
6. **ElevenLabs voice input** — Person D (garnish, last priority)

### **Phases (24 hours)**

#### **Hour 0–1: Setup, all hands**

* Repo, env vars, API keys (OpenAI, Mongo Atlas, Elastic, Sentry, Shopify or Browserbase, ElevenLabs)  
* Person C: spin up Shopify dev store immediately (or confirm Browserbase scrape target) — longest lead time, blocks task 5  
* Domain registration, whoever's free

#### **Hour 1–7: Core pipelines in parallel**

**Person A — Avatar (task 1 \+ 2\) (Ifeanyi)**

* OpenAI API call to combine the image of a person with the images of some clothing items  
* OpenAI API call to retrieve queries/categories from a recommendation

&nbsp;

* User photo → OpenAI vision call → strict JSON schema (skin tone, hair, face shape, eyes/brows/mouth, glasses)  
* Load base GLB in Three.js, apply JSON as texture swaps (eyes/brows/mouth), mesh swap (hair), material color (skin)  
* Get one real end-to-end pass working on a test photo before anything else — this is the wow moment, top priority for the whole team if it's behind

**Stack:** FastAPI, OpenAI Vision (`gpt-4o` or similar structured output), React \+ Three.js/`@react-three/fiber`

**Backend files:**

* `backend/routers/avatar.py` — `POST /avatar/generate` (photo in, JSON schema out)  
* `backend/services/openai_client.py` (shared, but A owns the vision-schema prompt logic inside it, e.g. `extract_avatar_features()`)  
* `backend/models/avatar_schema.py` — Pydantic model enforcing the strict JSON schema (skin tone, hair, face shape, eyes/brows/mouth, glasses)

**Frontend files:**

* `frontend/src/avatar/AvatarViewer.jsx` — Three.js canvas, loads base GLB, applies JSON via texture/mesh/material swaps  
* `frontend/src/avatar/avatarSwaps.js` — mapping logic: JSON field → texture path / mesh name / material color  
* `frontend/src/avatar/PhotoUpload.jsx` — capture/upload UI  
* `frontend/src/avatar/GuidedEditor.jsx` — manual override UI over the same JSON

&nbsp;

**Devyansh — Item photo \+ product photo pipeline (feeds task 5\)**&nbsp;

* rembg on user item photos, OpenAI tagging (category, color, style)  
* Same tagging pipeline applied to Shopify/scraped product photos as they come in from C  
* OpenAI tagging for user items and products
* Writes items to Mongo (via C's schema) and normalized products to Elastic

&nbsp;

**Stack:** FastAPI, `rembg` (Python lib), OpenAI vision tagging, MongoDB Atlas (`pymongo`), React for closet UI

Person B is really running **two connected pipelines**: (1) turn photos into tagged, embedded, stored items, and (2) turn a user's free-text prompt into a query vector that Person C's Elastic endpoint can use. Breaking it down:

**Backend files:**

* `backend/routers/inventory.py`  
  * `POST /inventory/upload` — accepts item photo → calls `rembg` → calls OpenAI tagging → writes to Mongo
  * `GET /inventory/{user_id}` — returns user's items for closet UI  
* `backend/services/rembg_service.py` — wraps `rembg` background removal, returns cutout image (save to disk/S3/base64 for frontend)  
* `backend/services/tagging_service.py` — `tag_item(image) -> {category, color, style}` via OpenAI vision call, structured output (Pydantic model)  
* `backend/routers/recs.py` (shared file with D, B owns backend half)  
  * Replaced by `backend/routers/products.py`, which exposes product listing, semantic search, and image try-on

**Frontend files:**

* `frontend/src/closet/InventoryUpload.jsx` — item photo upload UI  
* `frontend/src/closet/InventoryGrid.jsx` — grid of tagged items  
* `frontend/src/closet/ClosetView.jsx` — 2D cutouts layered over avatar, mix-and-match

**Mongo collections B writes to:**

* `items` — `{user_id, image_url, category, color, style, created_at}`

&nbsp;

**Person C — Data infra (task 3 \+ 4 \+ product sourcing) (DJ/Fiona split)**

**DJ**

* Mongo Atlas schema: users, avatar JSON, inventory items  
* Elasticsearch index setup, product ingestion, and semantic text query endpoint

**Fiona**

* Shopify Storefront API pull (or Browserbase scrape as fallback/supplement) → normalize products for Elastic ingestion (Fiona)
* Sentry instrumented across this pipeline from the start (ingestion \+ tagging calls are your tracing story) (Fiona)

&nbsp;

**Stack:** FastAPI, MongoDB Atlas, Elasticsearch, Shopify Storefront API (or Browserbase), Sentry

**Backend files:**

* `backend/services/mongo_client.py` — connection setup, schema helpers, used by everyone  
* `backend/services/elastic_client.py` — `insert_products()`, `list_products()`, and `query_products()`
* `backend/routers/products.py`  
  * internal script/endpoint to pull Shopify products (Storefront API) or scrape via Browserbase  
  * hands product photos to B's `tagging_service` (import/reuse, don't duplicate)  
  * writes results into Elastic via `elastic_client.insert_products()`
* `backend/scripts/seed_products.py` — one-off script run at hour 0-1 to seed the store/index, rerunnable  
* `backend/main.py` — app wiring, router includes, Sentry init, CORS, deploy config

**Mongo collections C owns:**

* `users` — `{user_id, avatar_json, created_at}`

**Elastic index C owns:**

* `products` — `{id, title, description, image, price, category, url}` plus internal `semantic_text`

&nbsp;

**Person D — Frontend shell \+ recs UI scaffold \+ Voice Integration (Fiona)**

* Basic browser application, avatar viewer container for A to drop into  
* Prompt input UI for task 5 ("going to a wedding…") wired to a stub endpoint  
* Starts Sentry on frontend/error boundaries; floats to help A or C if either is blocked

**Stack:** React, ElevenLabs SDK/API, Sentry (frontend), deployment (Vultr/Vercel/whatever)

**Frontend files:**

* `frontend/src/recs/PromptInput.jsx` — text box for "going to a wedding…" style queries, calls `/products/search`  
* `frontend/src/recs/ResultsGrid.jsx` — result cards: cutout image, product link, price  
* `frontend/src/voice/VoiceInput.jsx` — ElevenLabs speech-to-text, feeds transcript into the **same** `PromptInput` handler (no separate backend path)  
* `frontend/src/App.jsx` — top-level routing/state tying avatar \+ closet \+ recs together  
* `frontend/sentry.js` — frontend error boundary \+ Sentry init  
* `deploy/` — Dockerfile, deployment config, whoever D coordinates with

&nbsp;

**Checkpoint @ Hour 7:** avatar renders from a real photo in Three.js. If not, everyone reprioritizes onto A until it works — nothing else matters for the demo without this.

#### **Hour 7–14: Connect pipelines, build recs**

**Person A:** polish avatar (edge cases, guided-editor manual override UI over the same JSON)

**Person B:** finish item tagging into Mongo and connect free-text prompts to product semantic search

**Person C:** expose the search endpoint properly: takes style vector or prompt-derived vector → Elastic hybrid search → ranked products with buy links; keep feeding C+B's ingest loop with more Shopify/scraped products

**Person D:** build the real recs UI — text prompt in, result cards out (cutout \+ buy link), hook to C's endpoint; start ElevenLabs integration (speech-to-text on the prompt box) once recs UI is functional, not before

**Checkpoint @ Hour 14:** user can type "wedding" or similar, get back real ranked product cards with links, sourced from Shopify data.

#### **Hour 14–19: Voice, hardening, polish**

* **D:** finish ElevenLabs (voice → text → same prompt pipeline as typed input — don't build a separate path)  
* **A/B/C:** error handling, loading states, empty states, better seed data/photos so the demo looks good  
* **C:** finalize Sentry — make sure you can point to a trace in the ingestion or tagging pipeline live, since that's your Sentry differentiator  
* Skip/cut the room entirely under this plan unless everyone finishes early — it's not one of the six tasks you listed, so treat it as a stretch only

#### **Hour 19–22: Demo integration**

* Full run-throughs: photo → avatar → item upload → prompt/voice → recs cards  
* Fix whatever breaks in the seam between people's pieces (this always takes longer than expected — don't skip this block)  
* Record a backup demo video of one clean successful run

#### **Hour 22–23.5: README \+ submission**

* Problem, how AI is used (vision extraction, tagging, embeddings, search), user journey, assumptions/limitations, future work  
* Submission forms for each track (Shopify, Elastic, Sentry, OpenAI, Atlas, MLH ElevenLabs if applicable)

#### **Hour 23.5–24: Buffer**

* Deploy check, rehearse the live pitch, sleep-deprived triage

&nbsp;

&nbsp;

### **Shared stack**

* **Frontend:** React (Vite), Three.js (via `@react-three/fiber` \+ `@react-three/drei` for easier GLB handling)  
* **Backend:** FastAPI (Python), one service or lightweight microservices per domain — for 24hrs, I'd do **one FastAPI app with routers per domain**, not separate services, to avoid deployment overhead  
* **DB:** MongoDB Atlas (via `pymongo` or `motor` for async)  
* **Search:** Elasticsearch (via `elasticsearch-py`)  
* **AI:** OpenAI Python SDK (vision and image generation)  
* **Observability:** Sentry SDK (Python \+ JS)  
* **Repo layout (suggested):**

```
/frontend

    /src

        /avatar        (Person A)

        /closet         (Person B)

        /recs           (Person B \+ D)

        /voice          (Person D)

        App.jsx, main.jsx

/backend

    /routers

        avatar.py       (Person A)

        inventory.py    (Person B)
    
        products.py     (Person C)

        recs.py         (Person B \+ D)

    /services

        openai_client.py
        
        mongo_client.py
        
        elastic\_client.py
        
    main.py           (Person C owns wiring/deploy)

```
