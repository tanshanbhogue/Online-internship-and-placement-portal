# ==============================================================================
# FILE   : backend/app/modules/internship/schemas.py
# STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Response and query models for listings.
#
# EXPOSES
#   InternshipSummary: id, title, company, short_description (first ~160 chars of description), location, domain, stipend_per_month, duration_months, deadline, is_open
#   InternshipDetail: all Summary fields + description, eligibility. (No application status here: the SPA asks GET /api/applications/check/{id} from story #18.)
#   InternshipListResponse: items, total, page, page_size
#   InternshipFilters (query params): q, location, domain, min_stipend, max_duration_months, open_only(bool, default False), page(>=1), page_size(1..50, default 20)
#
# RULE
#   is_open = status == ACTIVE and deadline >= today (UTC date). Computed on the server only.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
