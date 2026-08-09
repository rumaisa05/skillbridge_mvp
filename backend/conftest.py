import os
from pathlib import Path

import pytest

# Force tests to use a throwaway SQLite file in the backend folder.
# This must be set before importing application modules so their DB engines
# bind to the test database instead of the developer `skillbridge.db`.
HERE = Path(__file__).resolve().parent
TEST_DB_PATH = HERE / "test.db"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")

# Remove any stale test DB file to ensure a fresh start for the test session.
try:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
except Exception:
    pass

# Import the app database after setting DATABASE_URL so the engine binds to test.db
from app import database

# Create tables for the session.
database.Base.metadata.create_all(bind=database.engine)

# Seed a privileged admin user directly in the test database so tests that
# require an admin can authenticate without using the public registration API.
try:
    from app.models.user import User
    from app.security import hash_password
    Session = database.SessionLocal

    db = Session()
    try:
        admin_email = "test_admin@example.com"
        if not db.query(User).filter(User.email == admin_email).first():
            adm = User(
                email=admin_email,
                password_hash=hash_password("password123"),
                name="Test Admin",
                role="admin",
            )
            db.add(adm)
            db.commit()
    finally:
        db.close()
except Exception:
    # If app internals cannot be imported yet, tests will handle admin creation
    # via fixtures that import SessionLocal when needed.
    pass

# Prevent alembic migrations from running during TestClient startup; we already
# created tables via metadata and want tests to be fast and deterministic.
try:
    from app import main as app_main

    def _noop_apply_migrations():
        return None

    app_main.apply_migrations = _noop_apply_migrations
except Exception:
    # If app.main cannot be imported for any reason, tests will import it later.
    pass


@pytest.fixture(autouse=True, scope="module")
def reset_db_between_modules():
    """Drop and recreate all tables between test modules to avoid state leakage."""
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    # Ensure seeded admin exists for each module after tables are recreated.
    try:
        from app.models.user import User
        from app.security import hash_password
        Session = database.SessionLocal
        db = Session()
        try:
            admin_email = "test_admin@example.com"
            if not db.query(User).filter(User.email == admin_email).first():
                adm = User(
                    email=admin_email,
                    password_hash=hash_password("password123"),
                    name="Test Admin",
                    role="admin",
                )
                db.add(adm)
                db.commit()
        finally:
            db.close()
    except Exception:
        pass
    yield
    # After module tests finish, clean up for the next module.
    database.Base.metadata.drop_all(bind=database.engine)
