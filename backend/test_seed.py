"""Regression tests for the demo seed and the evaluator's repo inspection.

These cover bugs that previously broke the deployed site:
  * seed.py referenced participants that don't exist (KeyError on startup)
  * seeding made live GitHub calls for every submission
  * fetch_repository_insights() raised a swallowed NameError on `has_tests`
"""
import pytest

from app.ai import evaluator
from app.database import SessionLocal
from app.models.challenge import Challenge
from app.models.portfolio import PortfolioEntry
from app.models.submission import Submission
from app.models.user import User
from app.seed import seed


def test_seed_runs_offline_and_selects_winners(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("seed() must not inspect GitHub repositories")

    monkeypatch.setattr(evaluator, "fetch_repository_insights", no_network)

    seed()

    db = SessionLocal()
    try:
        assert db.query(User).filter(User.role == "organization").count() >= 5
        assert db.query(User).filter(User.email == "ngo@skillbridge.test").first() is not None
        assert db.query(Challenge).count() == 10
        assert db.query(Submission).count() == 30
        assert db.query(Challenge).filter(Challenge.status == "selected").count() == 5
        assert db.query(PortfolioEntry).filter(PortfolioEntry.is_winner == 1).count() == 5
        counts = (
            db.query(User).count(),
            db.query(Challenge).count(),
            db.query(Submission).count(),
        )
    finally:
        db.close()

    # Running it again must be a harmless no-op.
    seed()
    db = SessionLocal()
    try:
        assert counts == (
            db.query(User).count(),
            db.query(Challenge).count(),
            db.query(Submission).count(),
        )
    finally:
        db.close()


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def _fake_github(tree_paths):
    def fake_get(url, headers=None, timeout=None):
        if url.endswith("/languages"):
            return _FakeResponse({"Python": 100})
        if "/git/trees/" in url:
            return _FakeResponse(
                {"tree": [{"path": p, "type": "blob", "size": 500} for p in tree_paths]}
            )
        return _FakeResponse({"default_branch": "main"})

    return fake_get


def test_repo_insights_detects_tests(monkeypatch):
    monkeypatch.setattr(
        evaluator.httpx, "get", _fake_github(["README.md", "app/main.py", "tests/test_api.py"])
    )
    insights = evaluator.fetch_repository_insights("https://github.com/someone/project")
    assert insights["has_tests"] is True
    assert insights["has_readme"] is True
    assert "could not be inspected" not in insights["repo_summary"]


def test_repo_insights_without_tests(monkeypatch):
    monkeypatch.setattr(evaluator.httpx, "get", _fake_github(["README.md", "main.py"]))
    insights = evaluator.fetch_repository_insights("https://github.com/someone/project")
    assert insights["has_tests"] is False
    assert "could not be inspected" not in insights["repo_summary"]


def test_evaluate_submission_can_skip_network(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("network must not be used when fetch_repo=False")

    monkeypatch.setattr(evaluator, "fetch_repository_insights", no_network)
    result = evaluator.evaluate_submission(
        "A web app with a database.", "https://github.com/a/b", category="web", fetch_repo=False
    )
    assert 0 < result.overall_score <= 100


def test_settings_normalise_database_url_and_secret_key():
    from app.config import Settings

    s = Settings(database_url="postgres://user:pw@host/db", secret_key="change-me-in-production")
    assert s.database_url.startswith("postgresql://")
    assert s.secret_key != "change-me-in-production"
    assert len(s.secret_key) >= 32

    explicit = Settings(secret_key="my-own-secret")
    assert explicit.secret_key == "my-own-secret"
