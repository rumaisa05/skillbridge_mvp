"""Seed interconnected demo data for SkillBridge.

Builds a realistic end-to-end dataset so the prototype is usable immediately:
multiple organizations (varied org_type), participants, challenges, AI-evaluated
submissions, portfolio entries, and a mix of winning + non-winning outcomes.

IDEMPOTENCY / PRODUCTION SAFETY
------------------------------
The OLD seed only created `ngo@skillbridge.test` (one org + three challenges).
That org may already exist in production alongside real user rows. This new
seed therefore:

  * Uses a VERSION-SPECIFIC sentinel guard: it only runs its new dataset if
    `brightvale@skillbridge.test` (a sentinel org unique to THIS seed set) is
    ABSENT. Checking for `ngo@skillbridge.test` would always skip on production
    because the old seed already created it.
  * Is ADDITIVE/get-or-create for every entity: it reuses an existing org /
    participant / challenge / submission instead of re-inserting. This means it
    never duplicates the existing `ngo@skillbridge.test` org or its challenges,
    and never touches real user rows (real users have non-*.skillbridge.test
    emails, so they are never matched).
  * Only creates an AIReport / PortfolioEntry / Notification when missing.

DRY-RUN MODE
------------
Call ``seed(dry_run=True)`` to print, for every entity that would be created,
an INSERT statement with the actual values WITHOUT writing anything. Foreign
keys reference the user/challenge/submission by their unique natural key
(email / org+title / challenge+participant) so the output is reviewable even
though the real numeric ids are generated at runtime.

All seeded accounts use the *.skillbridge.test email convention and a shared
demo password so visitors can tell they are sample accounts.

Reuses the existing models and the existing evaluate_submission() / winner
selection logic — no parallel evaluation or winner logic is created here.
"""
import json

from .database import SessionLocal
from .models.user import User
from .models.challenge import Challenge
from .models.submission import Submission
from .models.report import AIReport
from .models.portfolio import PortfolioEntry
from .models.notification import Notification
from .ai.evaluator import evaluate_submission
from .security import hash_password

# Shared demo password so every seeded account is easy to log into.
DEMO_PASSWORD = "password123"

# Version-specific sentinel: an org email unique to THIS new seed set. If this
# exists, the new seed data has already been loaded.
SEED_VERSION_SENTINEL = "brightvale@skillbridge.test"

# Module-level dry-run flag.
_DRY_RUN = False


def _sql(v):
    """Render a Python value as a SQL literal for dry-run output."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def _log(table, columns, values):
    """Print an INSERT statement for dry-run / review."""
    if not _DRY_RUN:
        return
    cols = ", ".join(f'"{c}"' for c in columns)
    vals = ", ".join(_sql(v) for v in values)
    print(f'INSERT INTO "{table}" ({cols}) VALUES ({vals});')


def _get_or_create_user(db, email, name, role, bio, **extra):
    """Return an existing user by email, else create (flush) a new demo user."""
    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        return user
    user = User(
        email=email,
        password_hash=hash_password(DEMO_PASSWORD),
        name=name,
        role=role,
        bio=f"[Demo account] {bio}",
        **extra,
    )
    _log("users", ["email", "name", "role", "bio", *extra.keys()],
         [email, name, role, f"[Demo account] {bio}", *extra.values()])
    if not _DRY_RUN:
        db.add(user)
        db.flush()
    return user


def _get_or_create_challenge(db, org, title, description, category, difficulty, reward):
    """Return an existing challenge for (org, title), else create (flush) a new one."""
    ch = db.query(Challenge).filter(
        Challenge.org_id == org.id,
        Challenge.title == title,
    ).first()
    if ch is not None:
        return ch
    ch = Challenge(
        org_id=org.id,
        title=title,
        description=description,
        category=category,
        difficulty=difficulty,
        reward=reward,
    )
    _log("challenges", ["org_email", "title", "description", "category", "difficulty", "reward"],
         [org.email, title, description, category, difficulty, reward])
    if not _DRY_RUN:
        db.add(ch)
        db.flush()
    return ch


def _get_or_create_submission(db, challenge, participant, repo_url, description):
    """Return an existing submission for (challenge, participant), else create (flush)."""
    sub = db.query(Submission).filter(
        Submission.challenge_id == challenge.id,
        Submission.participant_id == participant.id,
    ).first()
    if sub is not None:
        return sub
    sub = Submission(
        challenge_id=challenge.id,
        participant_id=participant.id,
        repo_url=repo_url,
        description=description,
        docs_url="https://example.com/docs",
        demo_url="https://example.com/demo",
        status="analyzing",
    )
    _log("submissions", ["challenge", "participant_email", "repo_url", "description",
                         "docs_url", "demo_url", "status"],
         [challenge.title, participant.email, repo_url, description, "https://example.com/docs",
          "https://example.com/demo", "analyzing"])
    if not _DRY_RUN:
        db.add(sub)
        db.flush()
    return sub


def _evaluate_and_portfolio(db, sub, challenge, feedback=""):
    """Run the real AI evaluator for a submission and create/update its portfolio entry.

    Mirrors the behavior in submissions._ensure_portfolio_entry using the same
    evaluate_submission() call and PortfolioEntry fields. Skips if a report or
    portfolio entry already exists for this submission (idempotent).
    """
    existing_report = db.query(AIReport).filter(AIReport.submission_id == sub.id).first()
    if existing_report is not None:
        return

    result = evaluate_submission(
        description=sub.description,
        repo_url=sub.repo_url,
        category=challenge.category,
    )
    report = AIReport(
        submission_id=sub.id,
        overall_score=result.overall_score,
        dimension_scores=json.dumps(result.dimension_scores),
        strengths=json.dumps(result.strengths),
        weaknesses=json.dumps(result.weaknesses),
        recommendations=json.dumps(result.recommendations),
        model_used=result.model_used,
        summary=result.summary,
    )
    _log("ai_reports", ["submission", "overall_score", "dimension_scores", "strengths",
                        "weaknesses", "recommendations", "model_used", "summary"],
         [f"challenge='{challenge.title}' participant='{sub.participant.email if sub.participant else ''}'",
          result.overall_score, json.dumps(result.dimension_scores),
          json.dumps(result.strengths), json.dumps(result.weaknesses),
          json.dumps(result.recommendations), result.model_used, result.summary])
    if not _DRY_RUN:
        db.add(report)
        sub.status = "analyzed"

    # Build the skills_proven list from report top dimensions + participant skills.
    top_skills = sorted(result.dimension_scores, key=result.dimension_scores.get, reverse=True)[:3]
    combined_skills = [str(s).strip().lower() for s in top_skills]
    if sub.participant and sub.participant.skills:
        try:
            for s in json.loads(sub.participant.skills or "[]"):
                clean = str(s).strip().lower().replace("_", " ")
                if clean and clean not in combined_skills:
                    combined_skills.append(clean)
        except Exception:
            pass

    entry = PortfolioEntry(
        participant_id=sub.participant_id,
        challenge_id=sub.challenge_id,
        submission_id=sub.id,
        title=challenge.title,
        description=sub.description,
        skills_proven=json.dumps(combined_skills),
        score=result.overall_score,
        organization_feedback=feedback,
        is_winner=0,
    )
    _log("portfolio_entries", ["submission", "participant_email", "title",
                               "skills_proven", "score", "organization_feedback", "is_winner"],
         [f"challenge='{challenge.title}'",
          sub.participant.email if sub.participant else "", challenge.title,
          json.dumps(combined_skills), result.overall_score, feedback, 0])
    if not _DRY_RUN:
        db.add(entry)


def _select_winner(db, sub):
    """Replicate the exact behavior of challenges.select_winner() for a submission.

    Sets is_winner on the submission + its portfolio entry, resets other submissions
    for the challenge, marks the challenge selected, and creates a success notification.
    Only acts if the submission is not already a winner (idempotent).
    """
    if _DRY_RUN:
        print(f"-- [select_winner] challenge='{sub.challenge.title if sub.challenge else ''}' "
              f"participant='{sub.participant.email if sub.participant else ''}'")
        return
    if sub.is_winner:
        return
    challenge = sub.challenge
    feedback = "We were impressed by the completeness and the attention to documentation. Congratulations!"

    # Reset any previous winner for this challenge before setting the new one.
    db.query(Submission).filter(Submission.challenge_id == challenge.id).update({"is_winner": 0})
    db.query(PortfolioEntry).filter(PortfolioEntry.challenge_id == challenge.id).update({"is_winner": 0})

    # Update the existing portfolio entry for this submission.
    entry = db.query(PortfolioEntry).filter(PortfolioEntry.submission_id == sub.id).first()
    if entry is not None:
        entry.organization_feedback = feedback
        entry.is_winner = 1

    sub.is_winner = 1
    challenge.status = "selected"
    db.add(Notification(
        user_id=sub.participant_id,
        title="Challenge winner selected",
        body=f"Congratulations! Your submission for '{challenge.title}' was selected as the winner. {feedback}",
        type="success",
    ))


def seed(dry_run: bool = False):
    """Seed demo data. Pass dry_run=True to print (not execute) the statements."""
    global _DRY_RUN
    _DRY_RUN = dry_run
    db = SessionLocal()
    try:
        # Version-specific guard: only load the new dataset if the sentinel org
        # (brightvale@skillbridge.test) is absent. This correctly detects the
        # "old seed present (ngo only), new seed missing" state on production.
        if db.query(User).filter(User.email == SEED_VERSION_SENTINEL).first():
            if dry_run:
                print("-- Sentinel brightvale@skillbridge.test already present; seed is a no-op.")
            return

        if dry_run:
            print("-- DRY RUN: statements below are what would execute against the DB. Nothing was written.")

        # ---------------------------------------------------------------- ORGS
        org_specs = [
            # (email, name, bio, org_type, website)
            ("ngo@skillbridge.test", "GreenFuture Foundation",
             "A local community NGO focused on sustainability, digital access, and transparent impact.",
             "ngo", "https://greenfuture.example.org"),
            ("brightvale@skillbridge.test", "Brightvale Academy",
             "A secondary school modernizing its classrooms and administrative tools for students and teachers.",
             "school", "https://brightvale.example.edu"),
            ("hospital@skillbridge.test", "St. Mary's Health Center",
             "A community hospital improving patient intake, scheduling, and care coordination.",
             "hospital", "https://stmaryshealth.example.org"),
            ("startup@skillbridge.test", "CloudNest",
             "An early-stage startup building tools to help small teams collaborate and ship faster.",
             "startup", "https://cloudnest.example.io"),
            ("company@skillbridge.test", "BluePeak Logistics",
             "A mid-size logistics company optimizing route planning and delivery operations.",
             "company", "https://bluepeak.example.com"),
        ]
        orgs = {}
        for email, name, bio, org_type, website in org_specs:
            org = _get_or_create_user(
                db, email, name, "organization", bio,
                org_type=org_type, website=website,
            )
            orgs[name] = org

        # -------------------------------------------------------- PARTICIPANTS
        participant_specs = [
            # (email, name, bio, skills, github_url)
            ("riley@skillbridge.test", "Riley Dawn",
             "Full-stack developer who loves building polished, testable web apps with React and FastAPI.",
             '["python", "react", "fastapi", "postgresql"]',
             "https://github.com/skillbridge-demo/riley"),
            ("aria@skillbridge.test", "Aria Moon",
             "Frontend engineer focused on accessible, responsive interfaces and design systems.",
             '["react", "ui/ux", "html", "css"]',
             "https://github.com/skillbridge-demo/aria"),
            ("nina@skillbridge.test", "Nina Chen",
             "Data analyst turning messy datasets into clear, actionable dashboards in Python and SQL.",
             '["python", "sql", "data analysis", "visualization"]',
             "https://github.com/skillbridge-demo/nina"),
            ("kai@skillbridge.test", "Kai Reyes",
             "Mobile developer building native-feeling apps with React Native and offline-first design.",
             '["react native", "javascript", "mobile"]',
             "https://github.com/skillbridge-demo/kai"),
            ("talia@skillbridge.test", "Talia Reed",
             "Backend engineer comfortable with APIs, databases, auth, and security best practices.",
             '["python", "django", "api", "security"]',
             "https://github.com/skillbridge-demo/talia"),
            ("samira@skillbridge.test", "Samira Patel",
             "Creative developer who loves building custom automation and AI-powered tools.",
             '["python", "ai", "automation", "typescript"]',
             "https://github.com/skillbridge-demo/samira"),
            ("cole@skillbridge.test", "Cole Hart",
             "Design-minded developer who cares about clean UI/UX and responsive web experiences.",
             '["javascript", "ui/ux", "design", "react"]',
             "https://github.com/skillbridge-demo/cole"),
            ("juno@skillbridge.test", "Juno Brooks",
             "Data scientist and engineer who enjoys building dashboards and ML prototypes.",
             '["python", "machine learning", "data", "viz"]',
             "https://github.com/skillbridge-demo/juno"),
        ]
        participants = {}
        for email, name, bio, skills, github_url in participant_specs:
            p = _get_or_create_user(
                db, email, name, "participant", bio,
                skills=skills, github_url=github_url,
            )
            participants[name] = p

        # ------------------------------------------------------- CHALLENGES
        # Each org posts 2 challenges. Each challenge will get 2-3 submissions.
        # GreenFuture's two challenges already exist from the OLD seed, so the
        # get-or-create guard reuses them (no duplicates).
        challenge_specs = [
            ("GreenFuture Foundation", "Donation Management Website",
             "Build a responsive donation management website for our NGO. It should let supporters donate, view impact stories, and see transparency reports. Include a clean UI/UX, donor data collection, and an admin dashboard. Strong documentation and tests are a plus.",
             "web", "medium", "Certification & recommendation letter"),
            ("GreenFuture Foundation", "Volunteer Scheduling Mobile App",
             "Create a mobile app for scheduling volunteers, tracking hours, and notifying members of events. Focus on a friendly UI/UX and offline support. Provide a demo or design mockups.",
             "mobile", "hard", "Paid internship offer (3 months)"),
            ("Brightvale Academy", "Student Grading Dashboard",
             "Build a dashboard for teachers to record and visualize student grades. Include charts, class averages, and per-student breakdowns. It should be easy to use and handle data securely. Provide documentation and tests.",
             "data", "medium", "Featured portfolio entry & prize"),
            ("Brightvale Academy", "Classroom Assignment Portal",
             "Design a web portal where teachers post assignments and students submit work. Focus on a clean UI/UX, notifications, and a simple backend with a database. Include tests and documentation.",
             "web", "medium", "Recommendation letter"),
            ("St. Mary's Health Center", "Patient Intake & Scheduling Tool",
             "Build a tool to streamline patient intake forms and appointment scheduling. It must handle sensitive data securely, offer a clean UI/UX, and connect to a backend database. Include thorough documentation and tests.",
             "web", "hard", "Honorarium & verified portfolio badge"),
            ("St. Mary's Health Center", "Care Coordination Dashboard",
             "Create a dashboard that helps nurses coordinate patient care across departments. Emphasize a clear UI/UX, real-time updates, and secure access controls. Provide docs and automated tests.",
             "data", "medium", "Featured portfolio entry"),
            ("CloudNest", "Team Task Collaboration App",
             "Build a lightweight team task manager with real-time updates, labels, and project boards. Focus on a modern UI/UX, a REST API, and a database. Include tests and documentation.",
             "web", "medium", "Equity opportunity & recommendation"),
            ("CloudNest", "Automated Onboarding Workflows",
             "Design automation that onboards new team members: create accounts, assign repos, and send welcome notes. Emphasize security, reliability, and custom workflows. Include tests and docs.",
             "automation", "hard", "$1,000 prize"),
            ("BluePeak Logistics", "Route Optimization Dashboard",
             "Build a dashboard that visualizes delivery routes and suggests optimizations. Use data analysis, charts, and filtering. Include a backend API, secure access, and documentation with tests.",
             "data", "hard", "$2,000 prize & interview"),
            ("BluePeak Logistics", "Fleet Tracking Portal",
             "Build a portal to track delivery vehicles in real time with a clean UI/UX. Include status updates, notifications, and a backend database. Provide docs and tests.",
             "web", "medium", "Certification & career opportunity"),
        ]
        challenges = []
        for org_name, title, desc, category, difficulty, reward in challenge_specs:
            ch = _get_or_create_challenge(
                db, orgs[org_name], title, desc, category, difficulty, reward,
            )
            challenges.append(ch)

        # --------------------------------------------------- SUBMISSIONS + EVAL
        # Each tuple: (org_name, challenge_title, participant_name, repo_url, description)
        submission_specs = [
            ("GreenFuture Foundation", "Donation Management Website", "Riley Dawn",
             "https://github.com/skillbridge-demo/donation-platform",
             "A full-stack donation platform with React frontend, FastAPI backend, PostgreSQL storage, unit tests, and a detailed README. Includes a clean, responsive UI/UX, secure donor forms with input sanitization, and an admin dashboard for campaigns."),
            ("GreenFuture Foundation", "Donation Management Website", "Aria Moon",
             "https://github.com/skillbridge-demo/donation-site",
             "A responsive donation website focused on accessibility and a beautiful UI/UX. Uses React with reusable components, a simple backend API with a database, and documentation covering setup and usage. Includes a small test suite."),
            ("GreenFuture Foundation", "Donation Management Website", "Cole Hart",
             "https://github.com/skillbridge-demo/greenfuture-donations",
             "A design-led donation experience with a focus on clean UI/UX and storytelling. Frontend built with React, a backend API, and a SQL database. Includes a README and basic tests."),
            ("GreenFuture Foundation", "Volunteer Scheduling Mobile App", "Kai Reyes",
             "https://github.com/skillbridge-demo/volunteer-mobile",
             "A React Native mobile app for volunteer scheduling with offline-first design, friendly UI/UX, and push notifications for events. Includes automated tests and documentation."),
            ("GreenFuture Foundation", "Volunteer Scheduling Mobile App", "Nina Chen",
             "https://github.com/skillbridge-demo/volunteer-scheduler",
             "A mobile-friendly volunteer scheduler with a clean UI/UX and a backend API. Focuses on tracking hours and event notifications, with a database and documentation. Includes tests."),
            ("GreenFuture Foundation", "Volunteer Scheduling Mobile App", "Samira Patel",
             "https://github.com/skillbridge-demo/volunteer-app",
             "A cross-platform volunteer app with real-time scheduling, custom workflows, and a friendly UI/UX. Built with React Native and a secure backend API. Includes tests and a README."),
            ("Brightvale Academy", "Student Grading Dashboard", "Nina Chen",
             "https://github.com/skillbridge-demo/grading-dashboard",
             "An interactive grading dashboard with charts, class averages, and per-student breakdowns. Built with Python, SQL, and visualization libraries. Includes a backend API, thorough documentation, and automated tests."),
            ("Brightvale Academy", "Student Grading Dashboard", "Juno Brooks",
             "https://github.com/skillbridge-demo/grade-dashboard",
             "A data-driven grading dashboard with clear visualizations and filtering. Uses Python and SQL, with a user-friendly UI/UX, documentation, and a test suite."),
            ("Brightvale Academy", "Student Grading Dashboard", "Riley Dawn",
             "https://github.com/skillbridge-demo/progress-tracker",
             "A full-stack grading dashboard with a React frontend and FastAPI backend. Features charts, secure role-based access, robust tests, and detailed documentation."),
            ("Brightvale Academy", "Classroom Assignment Portal", "Aria Moon",
             "https://github.com/skillbridge-demo/assignment-portal",
             "A clean classroom assignment portal with a friendly UI/UX. Teachers post assignments and students submit work. Built with React, a backend API, and a database. Includes tests and documentation."),
            ("Brightvale Academy", "Classroom Assignment Portal", "Talia Reed",
             "https://github.com/skillbridge-demo/assignment-portal-2",
             "A secure assignment portal with a Django backend, a database, and role-based access. Emphasizes input validation and security. Includes automated tests and documentation."),
            ("Brightvale Academy", "Classroom Assignment Portal", "Cole Hart",
             "https://github.com/skillbridge-demo/classroom-portal",
             "A design-focused classroom portal with a modern UI/UX. Covers assignment posting, student submissions, and notifications. Built with React and a backend API. Includes a README."),
            ("St. Mary's Health Center", "Patient Intake & Scheduling Tool", "Talia Reed",
             "https://github.com/skillbridge-demo/patient-intake",
             "A HIPAA-conscious patient intake and scheduling tool with secure authentication, input sanitization, and a robust backend. Built with Django and PostgreSQL. Includes thorough tests and documentation."),
            ("St. Mary's Health Center", "Patient Intake & Scheduling Tool", "Riley Dawn",
             "https://github.com/skillbridge-demo/patient-scheduler",
             "A full-stack patient intake and scheduling app with a React frontend and FastAPI backend. Features secure data handling, a clean UI/UX, comprehensive tests, and detailed docs."),
            ("St. Mary's Health Center", "Patient Intake & Scheduling Tool", "Samira Patel",
             "https://github.com/skillbridge-demo/patient-tool",
             "A patient intake and scheduling tool with a friendly UI/UX, secure forms, and a backend database. Includes custom automation for reminders, tests, and documentation."),
            ("St. Mary's Health Center", "Care Coordination Dashboard", "Nina Chen",
             "https://github.com/skillbridge-demo/care-coordination",
             "A care coordination dashboard with real-time updates and secure access controls. Uses Python, SQL, and visualization, with a clear UI/UX, documentation, and tests."),
            ("St. Mary's Health Center", "Care Coordination Dashboard", "Kai Reyes",
             "https://github.com/skillbridge-demo/care-dashboard",
             "A mobile-friendly care coordination dashboard with a clean UI/UX and secure role-based access. Built with React and a backend API. Includes documentation and tests."),
            ("St. Mary's Health Center", "Care Coordination Dashboard", "Juno Brooks",
             "https://github.com/skillbridge-demo/care-dashboard-2",
             "A data-driven care coordination dashboard with charts and filtering. Built with Python and SQL, emphasizing secure access and a clear UI/UX. Includes tests and documentation."),
            ("CloudNest", "Team Task Collaboration App", "Riley Dawn",
             "https://github.com/skillbridge-demo/task-collab",
             "A real-time team task manager with project boards, labels, and live updates. Built with React, FastAPI, and PostgreSQL. Includes a polished UI/UX, comprehensive tests, and detailed documentation."),
            ("CloudNest", "Team Task Collaboration App", "Aria Moon",
             "https://github.com/skillbridge-demo/task-collab-2",
             "A clean team task collaboration app with a modern UI/UX and real-time sync. Uses React and a backend API with a database. Includes a README and a solid test suite."),
            ("CloudNest", "Team Task Collaboration App", "Cole Hart",
             "https://github.com/skillbridge-demo/task-collab-3",
             "A design-focused task collaboration tool with boards, labels, and a friendly UI/UX. Built with React and a backend API. Includes documentation and basic tests."),
            ("CloudNest", "Automated Onboarding Workflows", "Samira Patel",
             "https://github.com/skillbridge-demo/onboarding-automation",
             "An automation system that onboards new team members: creates accounts, assigns repos, and sends welcome notes. Built with Python and custom workflows, emphasizing security and reliability. Includes tests and documentation."),
            ("CloudNest", "Automated Onboarding Workflows", "Talia Reed",
             "https://github.com/skillbridge-demo/onboarding-automation-2",
             "A secure onboarding automation pipeline with Django, role-based access, and custom workflows. Handles account creation and notifications reliably. Includes tests and docs."),
            ("CloudNest", "Automated Onboarding Workflows", "Kai Reyes",
             "https://github.com/skillbridge-demo/onboarding-flow",
             "A mobile-friendly onboarding automation flow with a clean UI/UX and secure backend. Automates account setup and welcome messages. Includes tests and documentation."),
            ("BluePeak Logistics", "Route Optimization Dashboard", "Nina Chen",
             "https://github.com/skillbridge-demo/route-optimization",
             "A route optimization dashboard with charts, filtering, and optimization suggestions. Built with Python, SQL, and visualization. Includes a backend API, secure access, documentation, and tests."),
            ("BluePeak Logistics", "Route Optimization Dashboard", "Juno Brooks",
             "https://github.com/skillbridge-demo/route-dashboard",
             "A data-driven route optimization dashboard with clear visualizations and data analysis. Uses Python and SQL, with a user-friendly UI/UX, documentation, and a test suite."),
            ("BluePeak Logistics", "Route Optimization Dashboard", "Riley Dawn",
             "https://github.com/skillbridge-demo/route-optimizer",
             "A full-stack route optimization dashboard with a React frontend and FastAPI backend. Features interactive charts, secure access, robust tests, and detailed documentation."),
            ("BluePeak Logistics", "Fleet Tracking Portal", "Kai Reyes",
             "https://github.com/skillbridge-demo/fleet-tracker",
             "A real-time fleet tracking portal with a clean UI/UX and live status updates. Built with React and a backend database. Includes notifications, documentation, and tests."),
            ("BluePeak Logistics", "Fleet Tracking Portal", "Riley Dawn",
             "https://github.com/skillbridge-demo/fleet-portal",
             "A full-stack fleet tracking portal with a React frontend and FastAPI backend. Features live vehicle tracking, status updates, secure access, tests, and documentation."),
            ("BluePeak Logistics", "Fleet Tracking Portal", "Aria Moon",
             "https://github.com/skillbridge-demo/fleet-tracker-2",
             "A design-led fleet tracking portal with real-time updates and a friendly UI/UX. Built with React and a backend API. Includes a README and basic tests."),
        ]

        for org_name, ch_title, p_name, repo_url, desc in submission_specs:
            org = orgs[org_name]
            ch = next(c for c in challenges if c.org_id == org.id and c.title == ch_title)
            participant = participants[p_name]
            sub = _get_or_create_submission(db, ch, participant, repo_url, desc)
            _evaluate_and_portfolio(db, sub, ch)
            if not _DRY_RUN:
                db.commit()

        # -------------------------------------------------------- WINNERS
        # Select a winner for at least one challenge per organization, leaving
        # the other challenge's submissions as non-winning (AI-evaluated) entries.
        # Winner chosen per challenge by (org_name, challenge_title, participant_name).
        winners = [
            ("GreenFuture Foundation", "Donation Management Website", "Richard Mensah"),
            ("Brightvale Academy", "Student Grading Dashboard", "Mei Chen"),
            ("St. Mary's Health Center", "Patient Intake & Scheduling Tool", "Sofia Rossi"),
            ("CloudNest", "Team Task Collaboration App", "Richard Mensah"),
            ("BluePeak Logistics", "Route Optimization Dashboard", "Mei Chen"),
        ]
        for org_name, ch_title, p_name in winners:
            org = orgs[org_name]
            ch = next(c for c in challenges if c.org_id == org.id and c.title == ch_title)
            participant = participants[p_name]
            if _DRY_RUN:
                print(f"-- [winner] challenge='{ch_title}' participant='{p_name}'")
                continue
            sub = db.query(Submission).filter(
                Submission.challenge_id == ch.id,
                Submission.participant_id == participant.id,
            ).first()
            if sub is None:
                continue
            _select_winner(db, sub)
            db.commit()

        if dry_run:
            print("-- END DRY RUN: no database writes were made.")
        else:
            print("Seeded demo organizations, participants, challenges, submissions, AI reports, "
                  "portfolio entries, and winners.")
    finally:
        db.close()
