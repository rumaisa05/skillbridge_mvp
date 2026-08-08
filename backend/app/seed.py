"""Seed a demo organization and a few challenges so the prototype is usable immediately."""
from .database import SessionLocal
from .models.user import User
from .models.challenge import Challenge
from .security import hash_password


def seed():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "ngo@skillbridge.test").first():
            return
        org = User(
            email="ngo@skillbridge.test",
            password_hash=hash_password("password123"),
            name="GreenFuture Foundation",
            role="organization",
            bio="A local community NGO focused on sustainability and digital access.",
        )
        db.add(org)
        db.commit()
        db.refresh(org)

        challenges = [
            Challenge(
                org_id=org.id,
                title="Build a Donation Management Website",
                description=(
                    "Create a responsive website for our NGO to manage donations, "
                    "show impact stories, and allow supporters to see transparency reports. "
                    "Include a clean UI/UX, a way to collect donor information, and admin "
                    "dashboard for managing campaigns. Strong documentation is a plus."
                ),
                category="web",
                difficulty="medium",
                reward="Certification & recommendation letter",
            ),
            Challenge(
                org_id=org.id,
                title="Community Volunteer Mobile App",
                description=(
                    "Design a mobile app that helps schedule volunteers, track hours, "
                    "and notify members of upcoming events. Focus on a friendly UI/UX and "
                    "offline support. Provide a demo or design mockups."
                ),
                category="mobile",
                difficulty="hard",
                reward="Paid internship offer (3 months)",
            ),
            Challenge(
                org_id=org.id,
                title="Data Analysis: Impact Reporting Dashboard",
                description=(
                    "Analyze our community survey data and build an interactive dashboard "
                    "that visualizes impact metrics. Provide insights and recommendations. "
                    "Include charts, filtering, and a short report summarizing findings."
                ),
                category="data",
                difficulty="medium",
                reward="Featured portfolio entry & prize",
            ),
        ]
        db.add_all(challenges)
        db.commit()
        print("Seeded demo organization and challenges.")
    finally:
        db.close()
