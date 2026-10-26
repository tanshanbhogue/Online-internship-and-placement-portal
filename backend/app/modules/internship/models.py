# ==============================================================================
# FILE   : backend/app/modules/internship/models.py
# STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   SQLAlchemy model for internship listings (data posted by admin, read by students). Corresponds to the Internship Service component.
#
# EXPOSES
#   class ListingStatus(str, enum.Enum): DRAFT="draft", ACTIVE="active", INACTIVE="inactive"   ("expired" is NOT stored; it is derived from deadline)
#   class Internship(Base) __tablename__ = "internships":
#     id int PK ; title str(150) ; company str(100) ; description text ; eligibility text null ; location str(100) null ; domain str(60) null (indexed)
#     stipend_per_month int null ; duration_months int null ; deadline date not null ; status ListingStatus default ACTIVE
#     created_at, updated_at datetime(UTC)
#
# USED BY
#   application/models.py (#18) has a FK to internships.id; application/service.py (#17) reads listings through internship/service.py.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
