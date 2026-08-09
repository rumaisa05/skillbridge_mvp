"""Thorough API endpoint tests for MVP improvements.

Tests: winner selection, talent search, profile editing,
challenge management, and backend search.
"""
import json
import sys
import httpx

BASE = "http://127.0.0.1:8000"
passed = 0
failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name} {detail}")


def main():
    client = httpx.Client(base_url=BASE, timeout=30)

    # 1. Health
    r = client.get("/api/health")
    check("Health check", r.status_code == 200 and r.json().get("status") == "ok", r.text)

    # 2. Register a participant
    email = "mvptest@example.com"
    r = client.post("/api/auth/register", json={
        "email": email, "password": "password123", "name": "MVP Test User", "role": "participant"
    })
    if r.status_code != 200:
        # Try login in case already registered
        r = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    check("Register/login participant", r.status_code == 200, r.text)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = r.json()["user"]["id"]

    # 3. Register an organization
    org_email = "mvporg@example.com"
    r = client.post("/api/auth/register", json={
        "email": org_email, "password": "password123", "name": "MVP Org", "role": "organization"
    })
    if r.status_code != 200:
        r = client.post("/api/auth/login", json={"email": org_email, "password": "password123"})
    check("Register/login org", r.status_code == 200, r.text)
    org_token = r.json()["access_token"]
    org_headers = {"Authorization": f"Bearer {org_token}"}
    org_id = r.json()["user"]["id"]

    # 4. Profile editing (GET /users/me)
    r = client.get("/api/users/me", headers=headers)
    check("GET /users/me", r.status_code == 200 and r.json()["email"] == email, r.text)

    # 5. Profile editing (PUT /users/me)
    r = client.put("/api/users/me", headers=headers, json={
        "name": "MVP Updated Name",
        "bio": "I am a full-stack developer.",
        "skills": json.dumps(["python", "react"]),
        "github_url": "https://github.com/mvptest",
    })
    check("PUT /users/me", r.status_code == 200 and r.json()["name"] == "MVP Updated Name", r.text)
    r = client.get("/api/users/me", headers=headers)
    check("GET /users/me after update", r.status_code == 200 and r.json().get("bio") == "I am a full-stack developer.", r.text)

    # 6. Create a challenge as org (for management tests)
    r = client.post("/api/challenges", headers=org_headers, json={
        "title": "MVP Test Challenge",
        "description": "Build a donation website with documentation and testing. Include security features.",
        "category": "web",
        "difficulty": "medium",
        "reward": "Certificate",
        "status": "open",
    })
    check("Create challenge as org", r.status_code == 200, r.text)
    challenge_id = r.json()["id"]

    # 7. Participant cannot create challenge
    r = client.post("/api/challenges", headers=headers, json={
        "title": "Should Fail", "description": "test", "category": "web"
    })
    check("Participant cannot create challenge (403)", r.status_code == 403, r.text)

    # 8. Challenge search/filter - search by title keyword
    r = client.get("/api/challenges", params={"search": "MVP Test"})
    check("Search challenges by keyword", r.status_code == 200 and any("MVP Test" in c["title"] for c in r.json()), r.text)

    # 9. Challenge filter by category
    r = client.get("/api/challenges", params={"category": "web"})
    check("Filter challenges by category", r.status_code == 200 and all(c["category"] == "web" for c in r.json()), r.text)

    # 10. Challenge filter by difficulty
    r = client.get("/api/challenges", params={"difficulty": "medium"})
    check("Filter challenges by difficulty", r.status_code == 200 and all(c["difficulty"] == "medium" for c in r.json()), r.text)

    # 11. Pagination
    r = client.get("/api/challenges", params={"page": 1, "limit": 2})
    check("Pagination limit=2", r.status_code == 200 and len(r.json()) <= 2, r.text)

    # 12. Update challenge (PUT)
    r = client.put(f"/api/challenges/{challenge_id}", headers=org_headers, json={
        "title": "MVP Test Challenge Updated",
        "description": "Updated description with auth, database, and real-time features plus documentation and testing.",
        "category": "web",
        "difficulty": "hard",
        "reward": "Certificate & stipend",
        "status": "open",
    })
    check("Update challenge (PUT)", r.status_code == 200 and r.json()["title"] == "MVP Test Challenge Updated", r.text)

    # 13. Wrong user cannot update challenge
    r = client.put(f"/api/challenges/{challenge_id}", headers=headers, json={
        "title": "Hacked", "description": "test", "category": "web"
    })
    check("Non-owner cannot update challenge (denied)", r.status_code in (403, 404), r.text)

    # 14. Participant submits solution
    r = client.post("/api/submissions", headers=headers, json={
        "challenge_id": challenge_id,
        "repo_url": "https://github.com/mvptest/donation-site",
        "description": "A responsive donation website with authentication, database integration, documentation, and testing. Includes UI/UX design and security features like HTTPS and input sanitization.",
        "docs_url": "https://github.com/mvptest/donation-site/blob/main/README.md",
        "demo_url": "https://mvptest-demo.vercel.app",
    })
    check("Submit solution", r.status_code == 200, r.text)
    submission_id = r.json()["id"]

    # 15. Get report for submission
    r = client.get(f"/api/submissions/{submission_id}/report", headers=headers)
    check("Get AI report", r.status_code == 200 and r.json().get("overall_score") is not None, r.text)

    # 16. Add to portfolio
    r = client.post(f"/api/submissions/{submission_id}/portfolio", headers=headers)
    check("Add portfolio entry", r.status_code == 200, r.text)

    # 17. Get own portfolio
    r = client.get("/api/portfolio/mine", headers=headers)
    check("Get own portfolio", r.status_code == 200 and len(r.json()) >= 1, r.text)

    # 18. Talent search - before winner selection, the AI-evaluated (non-verified)
    # submission must NOT appear as verified talent for employers.
    r = client.get("/api/talent/search", params={"q": "MVP"})
    check("Talent search excludes non-verified entries", r.status_code == 200 and len(r.json()) == 0, r.text)

    r = client.get("/api/talent/search", params={"skill": "python"})
    check("Talent search by skill returns none", r.status_code == 200 and len(r.json()) == 0, r.text)

    # 19. Get org challenge submissions list (org can see all)
    r = client.get("/api/submissions", params={"challenge_id": challenge_id}, headers=org_headers)
    check("Org sees all submissions", r.status_code == 200 and len(r.json()) >= 1, r.text)

    # 20. Select winner (submission_id is a query parameter, matching frontend)
    r = client.post(f"/api/challenges/{challenge_id}/select-winner", headers=org_headers, params={
        "submission_id": submission_id
    })
    check("Select winner", r.status_code == 200, r.text)

    # 20b. After winner selection, the verified winner NOW appears in talent search.
    r = client.get("/api/talent/search", params={"q": "MVP"})
    check("Verified winner appears in talent search", r.status_code == 200 and len(r.json()) >= 1, r.text)

    # 21. Close challenge
    r = client.put(f"/api/challenges/{challenge_id}", headers=org_headers, json={
        "title": "MVP Test Challenge Updated",
        "description": "Updated description",
        "category": "web",
        "difficulty": "hard",
        "reward": "Certificate & stipend",
        "status": "closed",
    })
    check("Close challenge", r.status_code == 200 and r.json()["status"] == "closed", r.text)

    # 22. Delete challenge
    r = client.delete(f"/api/challenges/{challenge_id}", headers=org_headers)
    check("Delete challenge", r.status_code == 200, r.text)

    # 23. Non-org cannot delete
    r = client.delete(f"/api/challenges/{challenge_id}", headers=headers)
    check("Non-owner cannot delete (denied)", r.status_code in (403, 404), r.text)

    print(f"\n=== RESULTS: {passed} passed, {failed} failed ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
