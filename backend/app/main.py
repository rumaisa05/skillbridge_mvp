import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import auth, challenges, submissions, portfolio, notifications, admin
from .seed import seed

logger = logging.getLogger("skillbridge")
logging.basicConfig(level=logging.INFO)


def apply_migrations() -> None:
    project_root = Path(__file__).resolve().parent.parent
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "migrations"))
    # Alembic's config parser treats "%" specially, so escape it (a URL-encoded
    # database password can contain "%").
    config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
    command.upgrade(config, "head")


def _allowed_origins() -> list[str]:
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://skillbridge-mvp-zdwk.vercel.app",
    ]
    for origin in settings.cors_origins.split(","):
        origin = origin.strip().rstrip("/")
        if origin and origin not in origins:
            origins.append(origin)
    return origins


app = FastAPI(
    title="SkillBridge API",
    description="AI-powered community innovation platform backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    # Vercel preview deployments of this project.
    allow_origin_regex=r"https://skillbridge-mvp-zdwk.*\.vercel\.app",
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
    try:
        apply_migrations()
    except Exception:
        # Fall back to creating any missing tables so the API can still start.
        logger.exception("Alembic migration failed; falling back to create_all()")
        Base.metadata.create_all(bind=engine)

    # Demo data is a nice-to-have. A seed error must never stop the API, or
    # login/register/challenges would all be down.
    try:
        seed()
    except Exception:
        logger.exception("Seeding demo data failed; continuing without it")


@app.get("/api/health")
@app.get("/health")  # some hosts probe /health by default
def health():
    return {"status": "ok"}
