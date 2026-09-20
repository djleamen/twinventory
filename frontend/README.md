# Twinventory frontend

Next.js (App Router) + TypeScript + shadcn/ui + TanStack Query.

## Run

```bash
npm install
cp .env.example .env.local
npm run dev          # http://localhost:5173 (matches the backend's default CORS origin)
```

The backend must be running at `NEXT_PUBLIC_API_URL` (default `http://127.0.0.1:8000`).

## API

Everything goes through `src/lib/api/`:

| Feature | Endpoint |
| --- | --- |
| Profile, preferences | `GET /users/{username}`, `PATCH /users/{username}/preferences` |
| Product list / search | `GET /products/list`, `GET /products/search` |
| Try on | `POST /products/try` (user image first, then product images) |

The "Who's shopping?" screen shows the usernames listed in `USERNAMES` in
`src/lib/api/users.ts`. Keep it in sync with the backend's `users.json`.

## Where things live

- `src/app/page.tsx` — pick a user
- `src/app/u/[username]/page.tsx` — main screen (`src/components/shop/shop-screen.tsx`)
- `src/lib/slots.ts` — outfit slots and which categories go in each
- `src/hooks/queries.ts` — all TanStack Query hooks
- `src/app/globals.css` — light green theme tokens

The backend filters by a single category, so browsing a slot fires one request per
category in parallel and merges the results (`useProducts`).
