"""End-to-end integration test of the SkillBridge core flow using httpx."""
import json
import random
import string

import httpx
import pytest
from httpx import ASGITransport

from app.main import app


def pretty(label, obj):
    print(f"\n--- {label} ---")
    if isinstance(obj, dict):
        print(json.dumps(obj, indent=2))
    else:
        print(obj)


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    with httpx.Client(transport=transport, base_url="http://testserver", timeout=30) as c:
        yield c


@pytest.mark.integration
def test_end_to_end_flow(client):
    # 1) Health
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health endpoint failed: {r.text}"
    pretty("1. Health", r.json())

    # 2) List challenges (public)
    r = client.get("/api/challenges")
    assert r.status_code == 200, f"Challenges endpoint failed: {r.text}"
    challenges = r.json()
    pretty("2. Challenges listed", f"{len(challenges)} open challenges")
    assert challenges, "No challenges available — something is wrong."
    challenge = challenges[1] if len(challenges) > 1 else challenges[0]

    # 3) Register participant
    suffix = "".join(random.choices(string.ascii_lowercase, k=6))
    payload = {
        "email": f"participant_{suffix}@example.com",
        "password": "password123",
        "name": "Test Participant",
 "role": "participant",
    }
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 200, f"Register failed: {r.text}"
    pretty("3. Register", r.json())
    token = r.json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}

    # 4) Submit a solution to a challenge
    submission = {
        "challenge_id": challenge["id"],
        "repo_url": "https://github.com/example/donation-site",
        "demo_url": "https://demo.example.com",
        "description": (
            "A responsive donation management website built with React and a secure backend. "
            "Includes user authentication, a PostgreSQL database, real-time donation tracking, "
            "responsive UI/UX design, and thorough documentation with a detailed README. "
            "We added automated tests with jest and implemented security best practices "
            "including input sanitization and password hashing. The dashboard offers a "
            "custom, innovative and unique data visualization experience for the NGO team."
        ),
    }
    r = client.post("/api/submissions", json=submission, headers=auth)
    assert r.status_code == 200, f"Submission failed: {r.text}"
    pretty("4. Submit solution", r.json())
    sub_id = r.json()["id"]

    # 5) Get the AI report
    r = client.get(f"/api/submissions/{sub_id}/report", headers=auth)
    assert r.status_code == 200, f"AI report request failed: {r.text}"
    report = r.json()
    pretty("5. AI Skill Report", report)

    # 6) Add to portfolio
    r = client.post(f"/api/submissions/{sub_id}/portfolio", headers=auth)
    assert r.status_code in (200, 201), f"Add to portfolio failed: {r.text}"
    pretty("6. Add to portfolio", r.json())

    # 7) View my portfolio
    r = client.get("/api/portfolio/mine", headers=auth)
    assert r.status_code == 200, f"Portfolio fetch failed: {r.text}"
    pretty("7. My portfolio", r.json())

    print("\nEnd-to-end flow completed successfully!")
