# ==============================================================================
# FILE   : backend/app/modules/internship/service.py
# STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Read-side logic for listings, plus the helpers the Application module uses to enforce deadlines on the server (SEC-15).
#
# EXPOSES (other stories import these names)
#   list_listings(db, filters: InternshipFilters) -> tuple[list[Internship], int]
#       Only status ACTIVE. Includes listings whose deadline has passed (they show as Closed, needed for test ST_04). Order: open first, then deadline ascending.
#       Filters: q matches title/company case-insensitively (escape % and _ in the term); location and domain exact case-insensitive; min_stipend; max_duration_months; open_only.
#       All via ORM/bound parameters (SEC-09).
#   get_listing(db, internship_id) -> Internship        # raises NotFound unless status ACTIVE
#   is_open(listing, today: date | None = None) -> bool
#   ensure_open(listing) -> None                          # raises ApplicationWindowClosed ("Application window closed") when deadline passed
#
# TESTS COVERED
#   UT_05, IT_05 and the filter cases in test_internship_listings.py.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
