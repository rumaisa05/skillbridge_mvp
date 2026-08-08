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


def test_admin_dashboard_and_user_listing_are_protected_and_sanitized():
    admin = _user_payload("admin", "adm")
    participant = _user_payload("participant", "part")

    admin_token = client.post("/api/auth/register", json=admin).json()["access_token"]
    participant_token = client.post("/api/auth/register", json=participant).json()["access_token"]

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    participant_headers = {"Authorization": f"Bearer {participant_token}"}

    summary = client.get("/api/admin/summary", headers=admin_headers)
    assert summary.status_code == 200, summary.text
    assert "users" in summary.json()

    forbidden = client.get("/api/admin/summary", headers=participant_headers)
    assert forbidden.status_code == 403, forbidden.text

    users = client.get("/api/admin/users", headers=admin_headers)
    assert users.status_code == 200, users.text
    assert all("password_hash" not in user for user in users.json())
