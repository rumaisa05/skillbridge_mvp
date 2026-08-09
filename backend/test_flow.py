"""End-to-end test of the SkillBridge core flow using httpx."""
import httpx
import pytest
import random
import string

BASE = "http://127.0.0.1:8000"


def pretty(label, obj):
    print(f"\n--- {label} ---")
    if isinstance(obj, dict):
        import json
        print(json.dumps(obj, indent=2))
    else:
        print(obj)


@pytest.fixture
def client():
    """Provide an httpx client for testing."""
    return httpx.Client(base_url=BASE, timeout=30)


@pytest.mark.integration
def test_end_to_end_flow(client):
    """Test the complete SkillBridge flow."""
    # 1) Health
    r = client.get("/api/health")
    pretty("1. Health", r.json())

    # 2) List challenges (public)
    r = client.get("/api/challenges")
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
    pretty("4. Submit solution", r.json())
    assert r.status_code == 200, f"Submission failed: {r.text}"
    sub_id = r.json()["id"]

    # 5) Get the AI report
    r = client.get(f"/api/submissions/{sub_id}/report", headers=auth)
    report = r.json()
    pretty("5. AI Skill Report", report)

    # 6) Add to portfolio
    r = client.post(f"/api/submissions/{sub_id}/portfolio", headers=auth)
    pretty("6. Add to portfolio", r.json())

    # 7) View my portfolio
    r = client.get("/api/portfolio/mine", headers=auth)
    pretty("7. My portfolio", r.json())

    print("\nEnd-to-end flow completed successfully!")
