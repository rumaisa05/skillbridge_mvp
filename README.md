# SkillBridge

**AI-powered community innovation platform.**

SkillBridge is a monorepo prototype that connects participants with
organizations through real-world digital challenges. Participants submit
solutions, receive AI-generated evaluation reports, and get a portfolio
snapshot that organizations and employers can review.

## Developers
- Rumaisa Waseem
- Manahil Imran

## Repo structure

```
new-skillbridge/
├── backend/                  # FastAPI backend API and database layer
│   ├── app/
│   │   ├── ai/               # AI evaluation engine
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── routers/          # API route implementations
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── main.py           # FastAPI app setup and router registration
│   │   ├── database.py       # SQLAlchemy engine and session config
│   │   ├── security.py       # auth, JWT, hashing helpers
│   │   ├── seed.py           # demo seed data loader
│   │   └── config.py         # environment-backed settings
│   ├── alembic/              # migration configuration
│   ├── alembic.ini
│   ├── requirements.txt
│   └── README.md
├── frontend/                 # Next.js frontend application
│   ├── app/                  # App Router pages
│   ├── components/           # shared React UI components
│   ├── lib/api.ts            # Axios API client and auth helpers
│   ├── package.json
│   └── tsconfig.json
├── .github/                  # CI workflow definitions
│   └── workflows/
├── PLAN.md                   # development plan and milestones
└── README.md                 # this file
```

## Backend overview

The backend is a FastAPI application with:
- SQLAlchemy models for users, challenges, submissions, AI reports, portfolios,
  and notifications
- Role-based authentication using JWT tokens
- Admin-only protected endpoints for platform summary and user listing
- AI submission evaluation and portfolio generation hooks

### Backend setup

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
pip install -r requirements.txt
```

### Database migrations

This project uses Alembic for schema migrations.

To apply the current database schema:

```bash
cd backend
python -m alembic upgrade head
```

To add a new migration after changing models:

```bash
python -m alembic revision --autogenerate -m "describe change"
python -m alembic upgrade head
```

### Run backend

```bash
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### Environment variables

The backend configuration is loaded from `.env` via `backend/app/config.py`.
Default values are:
- `DATABASE_URL=sqlite:///./skillbridge.db`
- `SECRET_KEY=change-me-in-production`
- `ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- `AI_MODE=mock`
- `OPENAI_API_KEY=`
- `OPENAI_MODEL=gpt-4o-mini`

To enable LLM-based evaluation, set:

```bash
AI_MODE=llm
OPENAI_API_KEY=your_api_key
```

## Frontend overview

The frontend is built with Next.js 14, React 18, TypeScript, Tailwind CSS, and
Recharts.

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app expects backend APIs at `http://localhost:8000` by default. Override
this in development with:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Build frontend

```bash
npm run build
```

## Running tests

Backend tests are located in `backend/` and include end-to-end regression
scripts such as `test_mvp_endpoints.py` and `test_flow.py`.

Run them with:

```bash
cd backend
python -m pytest test_mvp_endpoints.py test_flow.py
```

## CI / repo hygiene

A GitHub Actions workflow has been added at
`.github/workflows/backend-ci.yml` to run backend tests on push and pull requests.

The repository also includes `.gitignore` rules for local artifacts such as:
- `venv/`
- `node_modules/`
- `.next/`
- `__pycache__/`
- `*.pyc`
- `skillbridge.db`
- `*.sqlite3`

## Prototype features

This project includes:
- participant authentication and registration
- organization challenge creation
- submission creation with repo/demo links and description
- automated AI evaluation and score report generation
- portfolio entry creation from evaluated submissions
- admin-protected platform summary and user listing
- talent search and portfolio discovery flow

## Notes

This README is intended to document the project for developers and reviewers.
Do not include credentials or secrets in the repo. Use `.env` for local
configuration and keep production secrets outside version control.

