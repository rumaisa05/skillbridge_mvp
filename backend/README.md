# SkillBridge Backend (FastAPI)

AI-powered community innovation platform backend API.

## Setup

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

- API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## Database migrations
This backend now uses Alembic for schema migrations instead of automatically creating tables.

```bash
cd backend
python -m alembic upgrade head
```

If you add or change models, create a new migration revision:

```bash
python -m alembic revision --autogenerate -m "describe change"
python -m alembic upgrade head
```

## Demo Seeds
After running migrations, seed the demo organization manually by importing and calling the seed function or by running the app once with the seed helper enabled.

## Test isolation (important)

- The test suite uses a throwaway SQLite database at `backend/test.db` created by `backend/conftest.py`.
- Tests will not touch your developer `skillbridge.db`. The fixture sets `DATABASE_URL` to the test DB and recreates tables between test modules.
- If a test needs privileged accounts (admin), the admin user `test_admin@example.com` with password `password123` is seeded into the test DB by the fixture.
- Run the backend tests with:

```bash
cd backend
python -m pytest -q
```

## AI Evaluation
- Default mode is `mock` (heuristic scoring, no external API).
- To use an LLM, copy `.env.example` to `.env`, set `AI_MODE=llm` and
  `OPENAI_API_KEY`.

## Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login → token |
| GET | /api/challenges | List challenges |
| POST | /api/challenges | Create challenge (org) |
| POST | /api/submissions | Submit solution + triggers AI eval |
| GET | /api/submissions/{id}/report | Get AI skill report |
| POST | /api/submissions/{id}/portfolio | Create portfolio entry |
| GET | /api/portfolio/mine | My portfolio entries |
| GET | /api/talent/search | Search organization-verified winners (is_winner == 1) |

## Organization-verified projects

A portfolio entry only becomes an **organization-verified** project when an
organization selects its submission as the challenge winner via
`POST /api/challenges/{challenge_id}/select-winner`. That action sets
`is_winner = 1` on the corresponding portfolio entry (and resets it to `0` for
any other portfolio entries in the same challenge).

- Plain AI-evaluated submissions create portfolio entries with `is_winner = 0`.
- The employer-facing `/api/talent/search` endpoint **only** surfaces
  organization-verified winners (`is_winner == 1`). Non-winning AI-evaluated
  submissions are excluded from talent search.
