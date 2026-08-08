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


def test_notifications_are_created_for_submission_and_winner_selection():
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
            "title": "Notification Challenge",
            "description": "Build a challenge portal.",
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
            "repo_url": "https://github.com/example/notify-app",
            "description": "A portal app with backend, tests, and a nice UI.",
            "docs_url": "https://example.com/docs",
            "demo_url": "https://example.com/demo",
        },
    )
    assert submission.status_code == 200, submission.text

    notifications = client.get("/api/notifications", headers=participant_headers)
    assert notifications.status_code == 200, notifications.text
    assert any("evaluated" in n["title"].lower() or "report" in n["body"].lower() for n in notifications.json())

    submission_id = submission.json()["id"]
    winner = client.post(
        f"/api/challenges/{challenge_id}/select-winner?submission_id={submission_id}&feedback=Strong%20work%20and%20good%20documentation.",
        headers=org_headers,
    )
    assert winner.status_code == 200, winner.text

    participant_notifications = client.get("/api/notifications", headers=participant_headers)
    assert participant_notifications.status_code == 200, participant_notifications.text
    assert any("winner" in n["title"].lower() or "selected" in n["title"].lower() for n in participant_notifications.json())
