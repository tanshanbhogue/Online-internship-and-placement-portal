# ==============================================================================
# FILE   : backend/scripts/seed_internships.py
# STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Development seed data for listings, standing in for the admin 'Manage Listings' feature that is not in this sprint.
#
# BEHAVIOUR
#   Run: python -m scripts.seed_internships. Idempotent (skip titles that already exist). Insert about 8 realistic listings: mixed domains
#   (Backend, Data Analytics, QA, Frontend), locations (Remote, Bengaluru, Pune), stipends, durations, and deadlines relative to today:
#   at least one expiring in 30 days, one tomorrow and ONE ALREADY EXPIRED (needed for test ST_04). Test-plan examples: "Backend Intern - Acme Corp",
#   "Data Analyst Intern - Beta Inc", "QA Intern - Gamma Ltd", "Frontend Intern - Delta Co".
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import SessionLocal, init_db
from app.modules.internship.models import Internship, ListingStatus


def _listings(today):
    def d(days):
        return today + timedelta(days=days)

    return [
        dict(title="Backend Intern - Acme Corp", company="Acme Corp", domain="Backend", location="Bengaluru",
             stipend_per_month=25000, duration_months=6, deadline=d(30),
             description="Build and maintain REST APIs in Python and FastAPI, write unit tests and work with a PostgreSQL database alongside the platform team. You will ship real features in your first month.",
             eligibility="Final-year B.E./B.Tech students in CS/IS. Good Python fundamentals."),
        dict(title="Data Analyst Intern - Beta Inc", company="Beta Inc", domain="Data Analytics", location="Pune",
             stipend_per_month=18000, duration_months=3, deadline=d(14),
             description="Clean datasets, build dashboards and present weekly insights to product managers. Tools: SQL, Excel and Python (pandas).",
             eligibility="Any stream with a statistics or programming background."),
        dict(title="QA Intern - Gamma Ltd", company="Gamma Ltd", domain="QA", location="Remote",
             stipend_per_month=12000, duration_months=3, deadline=d(1),
             description="Design test cases, run manual and automated regression suites and report defects clearly. Exposure to Selenium and pytest.",
             eligibility="Pre-final or final-year students. Attention to detail."),
        dict(title="Frontend Intern - Delta Co", company="Delta Co", domain="Frontend", location="Bengaluru",
             stipend_per_month=20000, duration_months=4, deadline=d(45),
             description="Create responsive React interfaces from design mockups, focusing on accessibility and performance.",
             eligibility="Comfortable with HTML, CSS, JavaScript and basic React."),
        dict(title="Full Stack Intern - Epsilon Labs", company="Epsilon Labs", domain="Backend", location="Remote",
             stipend_per_month=15000, duration_months=6, deadline=d(21),
             description="Work across a React frontend and Node/Python services on an internal tooling product used by 500+ employees.",
             eligibility="Strong problem-solving skills; one personal or academic project required."),
        dict(title="Machine Learning Intern - Zeta AI", company="Zeta AI", domain="Data Analytics", location="Pune",
             stipend_per_month=30000, duration_months=6, deadline=d(60),
             description="Experiment with classification models, evaluate them rigorously and help deploy a model behind an API.",
             eligibility="Coursework in ML or statistics; Python, NumPy, scikit-learn."),
        dict(title="DevOps Intern - Eta Systems", company="Eta Systems", domain="DevOps", location="Bengaluru",
             stipend_per_month=22000, duration_months=3, deadline=d(7),
             description="Automate CI/CD pipelines, containerise services with Docker and monitor deployments.",
             eligibility="Linux fundamentals and basic scripting."),
        # ONE ALREADY EXPIRED: required by test ST_04 (application window closed).
        dict(title="Mobile App Intern - Theta Apps", company="Theta Apps", domain="Frontend", location="Remote",
             stipend_per_month=10000, duration_months=2, deadline=d(-10),
             description="Help build a cross-platform mobile app. Applications for this listing have closed.",
             eligibility="Basic knowledge of React Native or Flutter."),
    ]


def main() -> int:
    init_db()
    today = datetime.now(timezone.utc).date()
    created = skipped = 0
    with SessionLocal() as db:
        for row in _listings(today):
            if db.scalar(select(Internship.id).where(Internship.title == row["title"])) is not None:
                skipped += 1
                continue
            db.add(Internship(status=ListingStatus.ACTIVE, **row))
            created += 1
        db.commit()
    print(f"Internships: {created} created, {skipped} already present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
