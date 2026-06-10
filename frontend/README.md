# HealthHub — Next.js frontend

A Next.js (App Router) frontend that consumes the HealthHub Django API at
`/api/v1`, demonstrating the **hybrid architecture**: the same backend serves
both the server-rendered Django app and this React SPA.

This is a **starter slice** — it implements auth + dashboard + AI coach as
working examples of the pattern. Extend it screen by screen against the existing
API (browse the contract at `http://localhost:8000/api/docs/`).

## What's here

- `lib/auth.ts` — JWT login/refresh against SimpleJWT (`/auth/token/`)
- `lib/api.ts` — typed fetch wrapper that attaches the token and refreshes on 401
- `app/login` — email/password login
- `app/dashboard` — pulls `/accounts/me/` and the weekly workout summary
- `app/coach` — chat against `/coach/conversations/…/send/`, including the
  guardrail badge when a reply is blocked

## Run it

Requires Node 18.18+ (Node 20 LTS recommended).

```bash
cd frontend
cp .env.local.example .env.local          # points at http://localhost:8000/api/v1
npm install
npm run dev                                # http://localhost:3000
```

The Django API must be running (`python manage.py runserver` in the repo root),
with `corsheaders` allowing `http://localhost:3000` (already configured in dev).

## Notes / next steps

- Tokens are stored in `localStorage` for simplicity. For production, move to
  httpOnly cookies to mitigate XSS token theft.
- Add the remaining screens (fitness logging, doctor directory, booking) — the
  API endpoints already exist.
- Generate a fully-typed client from the OpenAPI schema
  (`http://localhost:8000/api/schema/`) instead of hand-writing types.
