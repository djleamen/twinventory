# twinventory

<img width="2000" height="1000" alt="twinventory (2000x1000px)" src="https://github.com/user-attachments/assets/c9fd872e-4723-47cf-9de4-0c4269a67711" />

Ever stood at your closet with nothing to wear, or bought something online that looked nothing like you expected? Twinventory fixes both- digitize your wardrobe, try clothes on yourself with AI, in 3D.

Submitted to Hack the North 2026 for:

- OpenAI: API Prizes
- Shopify: Hack Shopping with AI
- Elastic: Find the Signal - Best Use of Elasticsearch
- Sentry: Best Use of Sentry
- MLH: Best Use of ElevenLabs
- MLH: Best Use of MongoDB Atlas
- MLH: Best Domain Name from GoDaddy Registry

## Check it out:
- [twinventory.fashion](https://www.twinventory.fashion)
- [Devpost](https://devpost.com/software/project-name-s0vg5w)

## MVP

The core flow is:

1. Choose a profile.
2. Browse by category or search with text or voice.
3. Add products to outfit slots.
4. Generate a try-on image from the profile photo and selected products.
5. Follow product links to the source store.

The backend also supports profile preferences, inventory upload and retrieval, speech transcription, and 3D model previews.

See [backend/README.md](backend/README.md) for setup and the API contract. The original hackathon architecture and ownership plan is in [docs/planning.md](docs/planning.md).

Current integration status and ownership are tracked in [docs/status.md](docs/status.md).

## Deployment

Production uses Vercel for the Next.js frontend and Railway for the FastAPI backend. GitHub Actions validates every pull request and push; Vercel and Railway deploy `main` through their GitHub integrations.

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
6. Attach a volume at `/app/uploads` to persist inventory uploads across deployments.

At GoDaddy, add the exact apex and `www` records shown by Vercel. Add the `api` CNAME and verification TXT record shown by Railway. Provider-generated DNS targets should be copied from their dashboards rather than hard-coded here.
