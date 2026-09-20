# Integration Status

## Current state

| Area | State | Owner | Next action |
| --- | --- | --- | --- |
| Product ingestion | Complete | Fiona | Invalid image records are rejected; run scraper on demand |
| Elasticsearch schema/search | Complete | DJ | Preserve the normalized product contract and semantic mapping |
| Product list/search API | Complete | Ifeanyi | Frontend uses `/products`, `/products/search?q=`, and `/products/try` |
| Image try-on API | Complete | Ifeanyi | Returns readable 422/502 errors; white-background prompt in place |
| MongoDB infrastructure | Complete | DJ | Keep `twinventory.items` and shared accessors stable |
| Inventory upload/tagging | Available | Devyansh | Removes backgrounds, tags and embeds items, and stores them in MongoDB |
| User image/preferences | Available | Ifeanyi + DJ | Reads profiles and updates preferences in MongoDB |
| Frontend | Live | Ifeanyi | Supports product discovery, outfit selection, try-on, preferences, voice search, and 3D preview |
| Sentry | Integrated | Fiona | Captures backend logs, traces, and OpenAI instrumentation |
| Voice input | Integrated | Fiona | Transcribes microphone recordings into product search text |
| 3D preview | Integrated | Ifeanyi + Devyansh | Displays the model URL returned by `/models/convert` |
| Deployment | Live | DJ | Frontend and backend health verified 2026-09-20 |

## Demo gate

The MVP is demo-complete when one browser flow succeeds with real services:

1. Load the seeded profile and real products.
2. Search by text and select at least one product.
3. Generate and render a try-on image.
4. Open the selected product's source-store link.
5. Confirm `/health` and one Sentry trace without exposing credentials.