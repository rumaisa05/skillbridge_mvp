from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_expired_challenges_are_auto_closed_and_filtered():
    org_payload = {
        "email": f"org_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}@example.com",
        "password": "password123",
        "name": "Deadline Org",
        "role": "organization",
    }
    org_token = client.post("/api/auth/register", json=org_payload).json()["access_token"]
    headers = {"Authorization": f"Bearer {org_token}"}

    deadline = datetime.utcnow() - timedelta(days=1)
    challenge = client.post(
        "/api/challenges",
        headers=headers,
        json={
            "title": "Expired Challenge",
            "description": "Should auto-close.",
            "category": "web",
            "difficulty": "medium",
            "reward": "Certificate",
            "status": "open",
            "deadline": deadline.isoformat(),
        },
    )
    assert challenge.status_code == 200, challenge.text
    challenge_id = challenge.json()["id"]

    refreshed = client.get(f"/api/challenges/{challenge_id}")
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["status"] == "closed"

    filtered = client.get("/api/challenges", params={"status": "open"})
    assert filtered.status_code == 200, filtered.text
    assert all(item["id"] != challenge_id for item in filtered.json())
