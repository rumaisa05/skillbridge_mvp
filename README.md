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

- `DATABASE_URL` (default: `sqlite:///./skillbridge.db`)
- `SECRET_KEY`
- `AI_MODE` (`mock` or `llm`)
- `OPENAI_API_KEY`

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

