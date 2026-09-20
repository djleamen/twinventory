# Twinventory

Twinventory combines a user's photo with clothing discovered through semantic product search.

The current backend supports:

- browsing products, optionally by category
- semantic product search, optionally by category
- generating a try-on image from a user photo and selected product images
- MongoDB and Elasticsearch health checks

See [backend/README.md](backend/README.md) for setup and the API contract. The original hackathon architecture and ownership plan is in [docs/planning.md](docs/planning.md).

Current integration status and ownership are tracked in [docs/status.md](docs/status.md).

## Deployment

Production uses Vercel for the Next.js frontend and Railway for the FastAPI backend. GitHub Actions validates every pull request and push to `main`; the Vercel and Railway GitHub integrations deploy `main` automatically.

### Vercel

1. Import this repository and set **Root Directory** to `frontend`.
2. Set `NEXT_PUBLIC_API_URL=https://api.twinventory.fashion` for Production.
3. Set the Production Branch to `main`.
4. Add `twinventory.fashion` and `www.twinventory.fashion` under Domains.

### Railway

1. Create a service from this GitHub repository and set **Root Directory** to `/backend`.
2. Railway will build [backend/Dockerfile](backend/Dockerfile) and use its `PORT`-aware start command.
3. Set the Production Branch to `main` and the healthcheck path to `/health`.
4. Add the backend variables listed in [backend/README.md](backend/README.md#environment), with `FRONTEND_ORIGINS=https://twinventory.fashion,https://www.twinventory.fashion`.
5. Add `api.twinventory.fashion` as the custom domain.
6. If inventory uploads are part of the demo, attach a volume at `/app/uploads`.

At GoDaddy, add the exact apex and `www` records shown by Vercel. Add the `api` CNAME and verification TXT record shown by Railway. Provider-generated DNS targets should be copied from their dashboards rather than hard-coded here.

