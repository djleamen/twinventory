# Integration Status

## Current state

| Area | State | Owner | Next action |
| --- | --- | --- | --- |
| Product ingestion | Complete | Fiona + DJ | Run on demand; monitor failed shops and malformed products |
| Elasticsearch schema/search | Complete | DJ | Preserve the normalized product contract and semantic mapping |
| Product list/search API | Complete | Ifeanyi + DJ | Frontend uses `/products`, `/products/search?q=`, and `/products/try` |
| Image try-on API | Complete | Ifeanyi + DJ | Returns readable 422/502 errors; white-background prompt in place |
| MongoDB infrastructure | Complete | DJ | Keep `twinventory.items` and shared accessors stable |
| Inventory upload/tagging | Not merged | Devyansh | Port only inventory modules from `origin/personb`, then add tests |
| User image/preferences | Not started on `main` | Ifeanyi + DJ | Agree on schema first; Ifeanyi owns feature, DJ owns persistence contract |
| Frontend | First version merged | Ifeanyi | Iterate on feedback; search now sends `q=`; lingerie and baby categories hidden |
| Sentry | In progress, branch not visible remotely | Fiona | Instrument scraper and try-on, then open a focused PR |
| Voice input | Optional | Fiona | Start only after the typed product flow works end to end |
| 3D experience | Cut/stretch | Unassigned | Do not start before the 2D demo is stable |

## Required next steps

1. **Devyansh:** rebase from `main`; port `inventory.py`, rembg, tagging, and embedding services only. Replace `MONGO_URI` with `MONGODB_URI`, reuse the shared collection accessor, avoid import-time model/client initialization, and add tests.
2. **Ifeanyi:** iterate on frontend feedback. Coordinate any user schema with DJ before writing persistence code.
3. **Fiona:** keep Sentry changes isolated to observability. Instrument scraper and try-on latency/errors without changing endpoint contracts or product fields.
4. **DJ:** review incoming PRs for contract drift, run the live smoke sequence, and keep docs/tests synchronized.

## Demo gate

The backend is not demo-complete until one browser flow succeeds with real services:

1. List or search real products.
2. Select a product and submit it with a user image.
3. Render the returned image.
4. Upload and retrieve one inventory item after Person B integration.
5. Confirm `/health` and one Sentry trace without exposing credentials.