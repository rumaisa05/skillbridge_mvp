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


def test_talent_search_filters_by_name_and_skill():
    participant = _user_payload("participant", "part")
    org = _user_payload("organization", "org")

    participant_token = client.post("/api/auth/register", json=participant).json()["access_token"]
    org_token = client.post("/api/auth/register", json=org).json()["access_token"]

    participant_headers = {"Authorization": f"Bearer {participant_token}"}
    org_headers = {"Authorization": f"Bearer {org_token}"}

    challenge = client.post(
        "/api/challenges",
        headers=org_headers,
        json={
            "title": "Talent Search Challenge",
            "description": "Build a platform with Python and React features.",
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
            "repo_url": "https://github.com/example/talent-app",
            "description": "A Python and React app with tests and docs.",
            "docs_url": "https://example.com/docs",
            "demo_url": "https://example.com/demo",
        },
    )
    assert submission.status_code == 200, submission.text

    by_name = client.get("/api/talent/search", params={"q": "User"})
    assert by_name.status_code == 200, by_name.text
    assert any(item["participant_name"] == participant["name"] for item in by_name.json())

    by_skill = client.get("/api/talent/search", params={"skill": "python"})
    assert by_skill.status_code == 200, by_skill.text
    assert any("python" in [s.lower() for s in item["skills_proven"]] for item in by_skill.json())
