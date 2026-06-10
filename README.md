# HealthHub

> An AI fitness & wellness coach with a doctor-connection layer — built with the
> safety guardrails real health software needs.

HealthHub is a Django platform where users track their fitness, nutrition and
health readings, get **personalised, data-grounded coaching from an LLM**, and
**book consultations** with health professionals. The headline engineering idea
is a **guardrail-first AI pipeline**: every message is screened *before* it
reaches the model, so the coach stays firmly in the fitness/wellness lane and
refuses to give medical advice — redirecting users to a real doctor instead.

It is built as a **hybrid backend**: a complete server-rendered Django app *and*
a versioned REST API (`/api/v1/`) over the same service layer, so a Next.js
frontend can be added later without rewriting any business logic.

---

## Why this project

Most "AI health app" demos pipe user text straight into an LLM — which is
exactly the dangerous thing real health software cannot do. HealthHub is built
to show the *responsible* version:

- **Guardrail before the model.** A transparent, auditable safety classifier
  blocks medical, emergency and mental-health-crisis messages and never lets
  them reach the LLM. Every blocked turn is recorded for audit.
- **Grounded, not hallucinated.** The prompt builder injects the user's real
  profile and recent activity so advice is based on their data.
- **Provider-agnostic.** Anthropic, OpenAI or a local stub behind one interface.

---

## Architecture

```
 Clients          Django + HTMX        Next.js (phase 2)      Django admin
                        │                      │                    │
 Gateway        Template views ───┐    DRF REST API /api/v1     (built-in)
                                  └──────────┬──── JWT / session
                                             │
 Feature apps   ┌─────────────────────────── service layer ───────────────────────────┐
                │ accounts │ fitness │ nutrition │ coach │ consultations │ billing      │
                └──────────────────────────────────┬───────────────────────────────────┘
                                                    │
 AI pipeline    safety guardrail ─▶ prompt builder ─▶ LLM provider (Claude / GPT / stub)
                                                    │
 Data & infra        PostgreSQL  ·  Redis  ·  Celery workers  ·  email / Stripe
```

### Apps

| App | Responsibility |
|-----|----------------|
| `accounts` | Custom email-based `User`, patient/doctor roles, profile, health history |
| `fitness` | Exercise/routine library, workout logs, health readings (weight, BP, …) |
| `nutrition` | Food library, meal logging, diet plans |
| `coach` | AI coach: conversations + the guardrail → prompt → provider pipeline |
| `consultations` | Doctor directory, availability, bookings, per-booking messaging |
| `billing` | Plans, subscriptions, payments (Stripe-ready) |
| `notifications` | Async transactional email (Celery) |
| `common` | Shared abstract models and the `seed_demo` command |

### Design decisions

- **Custom user model from migration 0001.** Swapping `AUTH_USER_MODEL` later is
  painful; email is the login identifier and `role` drives the patient/doctor split.
- **Service layer.** Business logic lives in `services.py`, not in views. Both the
  template views and the API call the same functions — written once, no drift.
- **Guardrail as a pluggable function.** `guardrail.classify()` is a transparent
  rule set today and can be swapped for an ML classifier without touching callers.
- **Booking race safety.** `book_slot()` locks the slot row with
  `select_for_update()` inside a transaction so two patients can't grab the same slot.
- **Settings split.** `config/settings/{base,dev,prod,test}.py`; secrets come from
  the environment (12-factor) via `django-environ`.

---

## Tech stack

Python 3.12+ · Django 5.2 · Django REST Framework · SimpleJWT · drf-spectacular
· Celery + Redis · PostgreSQL · pytest · ruff · Docker.

---

## Getting started

### Quick start (SQLite, no services)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env                      # defaults work out of the box
python manage.py migrate
python manage.py seed_demo                # demo exercises, foods, a doctor + slots
python manage.py createsuperuser
python manage.py runserver
```

- App: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- API docs (Swagger): http://localhost:8000/api/docs/

### Full stack (Postgres + Redis + Celery)

```bash
docker compose up --build
```

### Tests & lint

```bash
pytest                 # behavioural test suite
ruff check apps config # lint
```

---

## Using the AI coach

By default `LLM_PROVIDER=stub` returns deterministic responses (no API key needed).
To use a real model, set in `.env`:

```bash
LLM_PROVIDER=anthropic       # or openai
LLM_API_KEY=sk-...
LLM_MODEL=claude-fable-5
```

The guardrail runs regardless of provider — try asking the coach a medical
question and watch it refuse and redirect to a consultation.

---

## Roadmap (future phases)

Phase 1 (this repo) ships the full core. Planned next:

- [ ] Real-time consultation chat (Django Channels / WebSockets)
- [ ] Stripe payments live (subscriptions + per-consultation fees)
- [ ] Video consultations
- [ ] Wearable / device sync for automatic health readings
- [ ] Next.js frontend consuming the existing API
- [ ] ML-based guardrail classifier alongside the rule set

---

## License

MIT
