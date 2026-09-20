# Twinventory frontend

Next.js (App Router) + TypeScript + shadcn/ui + TanStack Query.

## Run

```bash
npm install
printf 'NEXT_PUBLIC_API_URL=http://127.0.0.1:8000\n' > .env.local
npm run dev          # http://localhost:5173 (matches the backend's default CORS origin)
```

The backend must be running at `NEXT_PUBLIC_API_URL` (default `http://127.0.0.1:8000`).

## API

Everything goes through `src/lib/api/`:

| Feature | Endpoint |
| --- | --- |
| Profile, preferences | `GET /users/{username}`, `PATCH /users/{username}/preferences` |
| Product list / search | `GET /products`, `GET /products/search?q=...` |
| Try on | `POST /products/try` (user image first, then product images) |
| Voice search | `POST /speech/transcribe` |
| Demo 3D preview | `POST /models/convert` |

The "Who's shopping?" screen shows the usernames listed in `USERNAMES` in
`src/lib/api/users.ts`. Each username must have a matching document in MongoDB's
`users` collection with `username`, `image_url`, and `preferences` fields.

## Where things live

- `src/app/page.tsx` — pick a user
- `src/app/u/[username]/page.tsx` — main screen (`src/components/shop/shop-screen.tsx`)
- `src/lib/slots.ts` — outfit slots and which categories go in each
- `src/hooks/queries.ts` — all TanStack Query hooks
- `src/app/globals.css` — light green theme tokens

The backend filters by a single category, so browsing a slot fires one request per
category in parallel and merges the results (`useProducts`).
