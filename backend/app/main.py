from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth, challenges, submissions, portfolio, notifications, admin
from .seed import seed


def apply_migrations() -> None:
    project_root = Path(__file__).resolve().parent.parent
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "migrations"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(config, "head")


app = FastAPI(
    title="SkillBridge API",
    description="AI-powered community innovation platform backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(challenges.router)
app.include_router(submissions.router)
app.include_router(portfolio.router)
app.include_router(notifications.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup() -> None:
    apply_migrations()
    seed()


@app.get("/api/health")
def health():
    return {"status": "ok"}

