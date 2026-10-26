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
