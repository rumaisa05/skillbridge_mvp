import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _user_payload(role: str, prefix: str):
    return {
        "email": f"{prefix}_{uuid.uuid4().hex[:8]}@example.com",
        "password": "password123",
        "name": f"{role.title()} User",
        "role": role,
    }


def test_submission_creates_portfolio_and_org_feedback():
    participant = _user_payload("participant", "part")
    org = _user_payload("organization", "org")

    participant_login = client.post("/api/auth/register", json=participant)
    org_login = client.post("/api/auth/register", json=org)

    participant_token = participant_login.json()["access_token"]
    org_token = org_login.json()["access_token"]

    participant_headers = {"Authorization": f"Bearer {participant_token}"}
    org_headers = {"Authorization": f"Bearer {org_token}"}

    challenge = client.post(
        "/api/challenges",
        headers=org_headers,
        json={
            "title": "Part 2 Challenge",
            "description": "Build a donation portal with backend, tests, and docs.",
            "category": "web",
            "difficulty": "medium",
            "reward": "Certificate",
            "status": "open",
        },
    )
    challenge_id = challenge.json()["id"]

    submission = client.post(
        "/api/submissions",
        headers=participant_headers,
        json={
            "challenge_id": challenge_id,
            "repo_url": "https://github.com/example/part-two-app",
            "description": "A donation app with user auth, API, tests, and docs.",
            "docs_url": "https://example.com/docs",
            "demo_url": "https://example.com/demo",
        },
    )
    assert submission.status_code == 200, submission.text
    submission_id = submission.json()["id"]

    portfolio = client.get("/api/portfolio/mine", headers=participant_headers)
    assert portfolio.status_code == 200, portfolio.text
    assert len(portfolio.json()) >= 1, portfolio.text

    selected = client.post(
        f"/api/challenges/{challenge_id}/select-winner?submission_id={submission_id}&feedback=Strong%20product%20thinking%20and%20clear%20project%20documentation.",
        headers=org_headers,
    )
    assert selected.status_code == 200, selected.text
    assert selected.json()["portfolio_entry_id"] is not None

    detail = client.get(f"/api/portfolio/user/{participant_login.json()['user']['id']}", headers=org_headers)
    assert detail.status_code == 200, detail.text
    assert any(item["organization_feedback"] for item in detail.json())
