# SkillBridge MVP

A local prototype connecting organizations with verified participants through challenge-based portfolios.

## Tech stack

- Backend: FastAPI, SQLAlchemy, Alembic, Uvicorn
- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS
- Database: SQLite (default development database)
- Auth: JWT-based authentication
- API client: Axios
- Deployment tooling: npm, Python venv

## Run locally

### Backend

1. Open a terminal and go to the backend folder:
   ```powershell
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The backend is available at `http://localhost:8000`.

### Frontend

1. Open a second terminal and go to the frontend folder:
   ```powershell
   cd frontend
   ```
2. Install frontend dependencies:
   ```powershell
   npm install
   ```
3. Start the frontend app:
   ```powershell
   npm run dev
   ```

The frontend is available at `http://localhost:3000`.

## Configuration

The frontend defaults to `http://localhost:8000` for API requests. Set a custom backend URL with:

```powershell
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
npm run dev
```

The backend supports environment variables via `.env` or the system environment. Common settings include:

- `DATABASE_URL` (default: `sqlite:///./skillbridge.db`; `postgres://` URLs are accepted and converted)
- `SECRET_KEY` (**set this in production**; if empty a random one is generated on every start, which logs everyone out on restart)
- `CORS_ORIGINS` (comma-separated website origins allowed to call the API, no trailing slash)
- `AI_MODE` (`mock` or `llm`)
- `OPENAI_API_KEY`

## Deploying (Docker host + Vercel)

The repo root has a `Dockerfile` that builds the backend only.

1. Create a free Postgres database (e.g. Neon) and copy its connection string.
2. Deploy the repo as a Docker container on your host and set these environment variables:
   - `DATABASE_URL` = the Postgres connection string
   - `SECRET_KEY` = a long random string (`python -c "import secrets; print(secrets.token_urlsafe(48))"`)
   - `CORS_ORIGINS` = `https://skillbridge-mvp-zdwk.vercel.app`
   - `AI_MODE` = `mock`
   - `PORT` = `8000` (and set the container port to 8000)
3. Open `<backend-url>/api/health` (expect `{"status":"ok"}`) and `<backend-url>/api/challenges` (expect a list).
4. In Vercel: Project > Settings > Environment Variables, set `NEXT_PUBLIC_API_URL` to the backend URL
   (no trailing slash), then **redeploy** (the value is baked in at build time).
5. Free hosts sleep when idle; the first request after a sleep can take about a minute.
6. Free hosts have no persistent disk, so use Postgres, not SQLite, there.

Demo login after the first start seeds the database: `ngo@skillbridge.test` / `password123`.

## Tests

```powershell
cd backend
python -m pytest -q
```

## Useful commands

Backend:
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Frontend:
```powershell
cd frontend
npm run dev
```

Build frontend for production:
```powershell
cd frontend
npm run build
```

## Project structure

- `backend/` — FastAPI backend, database, auth, routes, and seed data
- `frontend/` — Next.js frontend with pages, components, and API client

## Key routes

- Frontend: `/login`, `/register`, `/profile`, `/talent`, `/challenges`
- Backend API: `/api/auth/*`, `/api/users/*`, `/api/portfolio/*`, `/api/talent/search`

## Cleanup and ignored files

The repo should keep local artifacts out of version control. Ignore:
- `venv/`
- `node_modules/`
- `.next/`
- `__pycache__/`
- `*.pyc`
- `skillbridge.db`

## Notes

This README focuses on local setup and running the app. For further development, use the backend and frontend source folders directly.

