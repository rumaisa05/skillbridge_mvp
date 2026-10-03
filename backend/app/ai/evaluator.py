"""AI Evaluation Engine for SkillBridge.

Evaluates a submission across 7 weighted dimensions and produces a skill report.

Two modes:
  - mock: deterministic heuristic scoring (great for demos / testing, no API needed)
  - llm: uses an LLM (OpenAI) for qualitative assessment (requires API key)
"""

import json
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from ..config import settings

# 7 dimensions with weights (sum = 1.0)
DIMENSIONS = {
    "code_quality": 0.25,
    "creativity": 0.10,
    "documentation": 0.15,
    "technical_complexity": 0.15,
    "security": 0.10,
    "ui_ux": 0.15,
    "completeness": 0.10,
}


@dataclass
class EvaluationResult:
    overall_score: int
    dimension_scores: dict
    strengths: list
    weaknesses: list
    recommendations: list
    summary: str
    model_used: str


def _normalise_repo_url(repo_url: str) -> str:
    """Normalise common GitHub URLs into a canonical HTTPS form."""
    cleaned = (repo_url or "").strip()
    if not cleaned:
        return ""

    if cleaned.startswith("git@"):
        cleaned = cleaned.replace("git@github.com:", "https://github.com/")
        cleaned = cleaned.replace("git@gitlab.com:", "https://gitlab.com/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    if not cleaned.startswith("http"):
        cleaned = f"https://{cleaned}"
    return cleaned.rstrip("/")


def _empty_insights(summary: str) -> dict:
    """Repository signals used when a repo can't (or shouldn't) be inspected."""
    return {
        "file_count": 0,
        "readme_length": 0,
        "has_tests": False,
        "has_security_config": False,
        "has_frontend": False,
        "has_backend": False,
        "has_lockfile": False,
        "has_readme": False,
        "languages": [],
        "file_names": [],
        "repo_summary": summary,
    }


def fetch_repository_insights(repo_url: str) -> dict:
    """Collect lightweight repository metadata for scoring without fetching full source files."""
    normalized = _normalise_repo_url(repo_url)
    if not normalized:
        return _empty_insights("No repository URL provided.")

    parsed = urlparse(normalized)
    host = parsed.netloc.lower()
    if not parsed.path or host not in {"github.com", "www.github.com", "gitlab.com", "www.gitlab.com"}:
        return _empty_insights(
            "Repository URL is not a supported public Git host."
        )

    path_parts = [segment for segment in parsed.path.split("/") if segment]
    if len(path_parts) < 2:
        return _empty_insights(
            "Repository URL does not include an owner and project name."
        )

    owner, repo_name = path_parts[:2]
    api_root = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "SkillBridgeEvaluator/1.0"}

    try:
        response = httpx.get(api_root, headers=headers, timeout=20)
        response.raise_for_status()
        metadata = response.json()
        default_branch = metadata.get("default_branch", "main")
        languages_response = httpx.get(f"{api_root}/languages", headers=headers, timeout=20)
        languages = list(languages_response.json().keys()) if languages_response.status_code == 200 else []

        tree_response = httpx.get(
            f"{api_root}/git/trees/{default_branch}?recursive=1",
            headers=headers,
            timeout=20,
        )
        tree_data = tree_response.json() if tree_response.status_code == 200 else {}
        files = [item["path"] for item in tree_data.get("tree", []) if item.get("type") == "blob"]
        file_count = min(len(files), 200)

        readme_candidates = [
            path for path in files if path.lower().startswith("readme") or path.lower().endswith("readme.md")
        ]
        readme_length = 0
        if readme_candidates:
            for path in readme_candidates:
                for item in tree_data.get("tree", []):
                    if item.get("path") == path and isinstance(item.get("size"), int):
                        readme_length = max(readme_length, item["size"])
                        break

        lowercase_files = [path.lower() for path in files]
        has_tests = any(
            "test" in path or ".spec." in path or "_spec." in path
            for path in lowercase_files
        )
        has_security_config = any(
            token in path for path in lowercase_files for token in ["security", "auth", "jwt", "oauth", ".env", "dockerfile"]
        )
        has_frontend = any(
            token in path for path in lowercase_files for token in ["app/", "src/", "components/", "public/", "frontend", "next.config", "vite.config"]
        ) or any(token in " ".join(lowercase_files) for token in ["package.json", "tailwind.config", "app/page", "src/app"])
        has_backend = any(
            token in path for path in lowercase_files for token in ["backend/", "api/", "server/", "routes/", "models/", "requirements.txt", "main.py", "app.py"]
        ) or any(token in " ".join(lowercase_files) for token in ["fastapi", "flask", "django", "express"])
        has_lockfile = any(path.lower() in {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "requirements.txt"} or path.lower().endswith("lock") for path in lowercase_files)
        has_readme = bool(readme_candidates)

        file_names = files[:12]
        repo_summary = (
            f"Repository includes {file_count} tracked files, "
            + f"{len(languages)} detected language(s), "
            + ("a README, " if has_readme else "no README, ")
            + ("tests, " if has_tests else "no test suite, ")
            + ("security-related config, " if has_security_config else "no explicit security config, ")
            + ("front-end assets, " if has_frontend else "no frontend structure, ")
            + ("and backend code." if has_backend else "and no obvious backend structure.")
        )

        return {
            "file_count": file_count,
            "readme_length": max(readme_length, 0),
            "has_tests": has_tests,
            "has_security_config": has_security_config,
            "has_frontend": has_frontend,
            "has_backend": has_backend,
            "has_lockfile": has_lockfile,
            "has_readme": has_readme,
            "languages": languages[:6],
            "file_names": file_names,
            "repo_summary": repo_summary,
        }
    except Exception:
        return _empty_insights(
            "Repository could not be inspected, so scoring relies on the submission description only."
        )


def _mock_evaluate(description: str, repo_url: str = "", category: str = "web",
                   fetch_repo: bool = True) -> EvaluationResult:
    """Heuristic scoring based on submission content and repo signals."""
    text = f"{description or ''}".lower()
    repo = (
        fetch_repository_insights(repo_url)
        if fetch_repo
        else _empty_insights("Repository was not inspected.")
    )
    has_repo = bool(repo_url and "http" in repo_url)
    has_explicit_docs = any(k in text for k in ["documentation", "readme", "docs"])
    has_design = any(k in text for k in ["ui", "ux", "frontend", "design", "responsive"])
    has_security = any(k in text for k in ["auth", "security", "sanitize", "password", "https"]) or repo.get("has_security_config")
    has_ai = any(k in text for k in ["ai", "model", "machine learning", "ml"])
    has_testing = any(k in text for k in ["test", "testing", "pytest", "jest", "unit"]) or repo.get("has_tests")
    has_db = any(k in text for k in ["database", "sql", "postgres", "backend", "api"]) or repo.get("has_backend")
    has_creativity = any(k in text for k in ["real-time", "live", "custom", "innovative", "unique"])
    has_readme = repo.get("has_readme") or has_explicit_docs
    has_frontend = repo.get("has_frontend") or has_design
    has_backend = repo.get("has_backend") or has_db
    has_lockfile = repo.get("has_lockfile")
    large_repo = repo.get("file_count", 0) >= 12
    readme_strength = repo.get("readme_length", 0) >= 200

    length_bonus = min(2, len(description or "") // 200)

    def clamp_score(base, signals):
        return max(3, min(10, base + sum(bool(s) for s in signals) + length_bonus))

    code_quality = clamp_score(4, [has_repo, has_testing, has_backend, large_repo])
    creativity = clamp_score(4, [has_creativity, has_ai, has_frontend])
    documentation = clamp_score(4, [has_explicit_docs, has_readme, readme_strength])
    technical_complexity = clamp_score(4, [has_db, has_ai, has_backend, large_repo])
    security = clamp_score(4, [has_security, has_lockfile, repo.get("has_security_config")])
    ui_ux = clamp_score(4, [has_design, has_frontend, has_repo])
    completeness = clamp_score(4, [has_repo, has_testing, has_readme, has_backend or has_frontend, length_bonus > 0])

    scores = {
        "code_quality": code_quality,
        "creativity": creativity,
        "documentation": documentation,
        "technical_complexity": technical_complexity,
        "security": security,
        "ui_ux": ui_ux,
        "completeness": completeness,
    }

    overall = round(sum(scores[k] * w for k, w in DIMENSIONS.items()) * 10)

    strengths = []
    weaknesses = []
    recommendations = []

    if has_repo:
        strengths.append(f"Submission includes a repository link, and the repo appears to be {repo.get('repo_summary', 'a real project').lower()}.")
    if has_testing:
        strengths.append("Evidence of testing suggests attention to code reliability.")
    if has_design:
        strengths.append("Clear focus on user interface and experience design.")
    if has_ai:
        strengths.append("Incorporation of AI/ML concepts demonstrates technical ambition.")
    if has_backend:
        strengths.append("The codebase shows backend or full-stack implementation depth.")
    if repo.get("has_frontend"):
        strengths.append("The repository includes frontend assets or UI structure, indicating a user-facing product.")

    if code_quality < 7:
        weaknesses.append("Code organization and maintainability can be improved further.")
    if documentation < 6:
        weaknesses.append("Documentation is limited; a detailed README and inline comments would help.")
    if security < 6:
        weaknesses.append("Security considerations need more attention (auth, input validation, dependencies).")
    if ui_ux < 6:
        weaknesses.append("The UI/UX could be refined to improve clarity and responsiveness.")
    if completeness < 6:
        weaknesses.append("Project could be more complete; consider implementing all core requirements.")

    if documentation < 6:
        recommendations.append("Write a comprehensive README with setup, architecture, and usage instructions.")
    if security < 6:
        recommendations.append("Review OWASP Top 10 and add input sanitization plus secure dependency management.")
    if not has_testing:
        recommendations.append("Add automated tests to increase reliability and confidence.")
    if code_quality < 7:
        recommendations.append("Refactor code into modular, well-named components with consistent style.")
    if not repo.get("has_readme") and not has_explicit_docs:
        recommendations.append("Add a clear project README and implementation notes so reviewers can understand the build quickly.")

    summary = (
        f"Overall, this solution scores {overall}/100. "
        + (f"It includes a public repository at {repo_url}. " if has_repo else "A repository link would strengthen verification. ")
        + (repo.get("repo_summary", "Repo metadata was not available.") + " ")
        + "It meets the challenge with reasonable completeness "
        + ("and shows strong technical depth." if overall >= 75 else "and is a solid foundation to build upon.")
    )

    return EvaluationResult(
        overall_score=overall,
        dimension_scores=scores,
        strengths=strengths or ["Visible effort and engagement with the challenge."],
        weaknesses=weaknesses or ["Little external context to deeply evaluate."],
        recommendations=recommendations or ["Expand documentation and add a live demo."],
        summary=summary,
        model_used="mock",
    )


def _llm_evaluate(description: str, repo_url: str = "", category: str = "web",
                  fetch_repo: bool = True) -> EvaluationResult:
    """Use an LLM to evaluate a submission qualitatively. Requires openai_api_key."""
    try:
        repo = (
            fetch_repository_insights(repo_url)
            if fetch_repo
            else _empty_insights("Repository was not inspected.")
        )
        prompt = f"""
You are SkillBridge's AI evaluator. Evaluate the following project submission against 7 weighted dimensions.
Return a JSON object with keys: dimension_scores, strengths (list), weaknesses (list), recommendations (list), summary.

Dimensions & weights:
- code_quality (0.25)
- creativity (0.10)
- documentation (0.15)
- technical_complexity (0.15)
- security (0.10)
- ui_ux (0.15)
- completeness (0.10)

Submission description:
{description}

Repo: {repo_url}
Repo signals:
{json.dumps(repo, ensure_ascii=True, sort_keys=True)}
Category: {category}

Score each dimension 1-10, compute overall_score as the weighted average scored 1-100.
Only return valid JSON.
"""
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.openai_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        return EvaluationResult(
            overall_score=int(data.get("overall_score", 0)),
            dimension_scores=data.get("dimension_scores", {}),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            recommendations=data.get("recommendations", []),
            summary=data.get("summary", ""),
            model_used=settings.openai_model,
        )
    except Exception:
        # Fall back to mock on any LLM error so the flow never breaks.
        return _mock_evaluate(description, repo_url, category, fetch_repo)


def evaluate_submission(description: str, repo_url: str = "", category: str = "web",
                        fetch_repo: bool = True) -> EvaluationResult:
    """Score a submission. Pass fetch_repo=False to skip all GitHub network calls."""
    if settings.ai_mode == "llm":
        return _llm_evaluate(description, repo_url, category, fetch_repo)
    return _mock_evaluate(description, repo_url, category, fetch_repo)
