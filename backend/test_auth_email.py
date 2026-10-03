import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_ignores_email_case_and_surrounding_spaces():
    local = f"MixedCase_{uuid.uuid4().hex[:8]}"
    registered = client.post(
        "/api/auth/register",
        json={
            "email": f"  {local}@Example.com ",
            "password": "password123",
            "name": "Mixed Case",
            "role": "participant",
        },
    )
    assert registered.status_code == 200, registered.text
    assert registered.json()["user"]["email"] == f"{local}@example.com".lower()

    for attempt in (f"{local}@example.com", f"{local.upper()}@EXAMPLE.COM  ", f"  {local}@example.com"):
        r = client.post("/api/auth/login", json={"email": attempt, "password": "password123"})
        assert r.status_code == 200, (attempt, r.text)

    wrong = client.post("/api/auth/login", json={"email": f"{local}@example.com", "password": "nope"})
    assert wrong.status_code == 401


def test_register_rejects_same_email_in_different_case():
    local = f"dupe_{uuid.uuid4().hex[:8]}"
    body = {"password": "password123", "name": "Dupe", "role": "participant"}
    first = client.post("/api/auth/register", json={**body, "email": f"{local}@example.com"})
    assert first.status_code == 200, first.text
    second = client.post("/api/auth/register", json={**body, "email": f"{local.upper()}@example.com"})
    assert second.status_code == 400
