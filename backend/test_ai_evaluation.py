from unittest.mock import patch

from app.ai.evaluator import evaluate_submission


def test_same_description_different_repo_signal_changes_score():
    same_description = "Build a web app for donors. Includes login, dashboards, and reporting."

    weak_repo = {
        "file_count": 4,
        "readme_length": 120,
        "has_tests": False,
        "has_security_config": False,
        "has_frontend": False,
        "has_backend": True,
        "has_lockfile": False,
        "has_readme": True,
        "languages": ["python"],
        "file_names": ["main.py"],
        "repo_summary": "Small Python backend with a minimal README.",
    }

    strong_repo = {
        "file_count": 28,
        "readme_length": 900,
        "has_tests": True,
        "has_security_config": True,
        "has_frontend": True,
        "has_backend": True,
        "has_lockfile": True,
        "has_readme": True,
        "languages": ["python", "javascript"],
        "file_names": ["README.md", "package.json", "src/App.tsx", "tests/test_api.py"],
        "repo_summary": "Project includes frontend, backend, tests, lockfile, and detailed docs.",
    }

    with patch("app.ai.evaluator.fetch_repository_insights", side_effect=[weak_repo, strong_repo]):
        weak_result = evaluate_submission(same_description, "https://github.com/example/weak-repo", category="web")
        strong_result = evaluate_submission(same_description, "https://github.com/example/strong-repo", category="web")

    assert weak_result.overall_score < strong_result.overall_score
    assert weak_result.model_used == strong_result.model_used
