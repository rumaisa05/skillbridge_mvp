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


def test_talent_search_only_returns_verified_winners():
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
    submission_id = submission.json()["id"]

    # A plain AI-evaluated submission (NOT selected as a winner) SHOULD appear
    # in the employer talent search as an AI-evaluated candidate (is_winner == 0).
    by_name = client.get("/api/talent/search", params={"q": "User"})
    assert by_name.status_code == 200, by_name.text
    non_winner = next(
        (item for item in by_name.json() if item["participant_name"] == participant["name"]), None
    )
    assert non_winner is not None, "AI-evaluated non-winner should appear in talent search"
    assert non_winner["is_winner"] == 0, "Non-winner should carry is_winner == 0"

    by_skill = client.get("/api/talent/search", params={"skill": "python"})
    assert by_skill.status_code == 200, by_skill.text
    assert any(
        "python" in [s.lower() for s in item["skills_proven"]] and item["participant_name"] == participant["name"]
        for item in by_skill.json()
    ), "AI-evaluated non-winner should appear in skill search"

    # Select the submission as the winner -> becomes organization-verified.
    selected = client.post(
        f"/api/challenges/{challenge_id}/select-winner",
        headers=org_headers,
        params={"submission_id": submission_id, "feedback": "Verified by the organization."},
    )
    assert selected.status_code == 200, selected.text
    assert selected.json()["portfolio_entry_id"] is not None

    # Now the verified winner SHOULD appear with is_winner == 1.
    by_name = client.get("/api/talent/search", params={"q": "User"})
    assert by_name.status_code == 200, by_name.text
    winner = next(
        (item for item in by_name.json() if item["participant_name"] == participant["name"]), None
    )
    assert winner is not None
    assert winner["is_winner"] == 1, "Winner should carry is_winner == 1"

    by_skill = client.get("/api/talent/search", params={"skill": "python"})
    assert by_skill.status_code == 200, by_skill.text
    assert any("python" in [s.lower() for s in item["skills_proven"]] for item in by_skill.json())
