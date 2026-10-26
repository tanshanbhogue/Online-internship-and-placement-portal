# ==============================================================================
# FILE   : backend/app/modules/application/models.py
# STORY  : #18 Prevent Duplicate Internship Applications  [FR-002; SEC-15]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   SQLAlchemy model for internship applications, including the database-level uniqueness that makes duplicate prevention race-proof.
#   Owned by #18 and merged BEFORE story #17 (which only uses it).
#
# EXPOSES
#   class ApplicationStatus(str, enum.Enum): APPLIED="Applied", SHORTLISTED="Shortlisted", REJECTED="Rejected", SELECTED="Selected"
#   class Application(Base) __tablename__ = "applications":
#     id int PK ; student_id FK users.id (indexed, ondelete restrict) ; internship_id FK internships.id (indexed, ondelete restrict)
#     cover_note text null (<= 2000) ; resume_stored_name str(80) ; resume_original_name str(255) ; resume_content_type str(100) ; resume_size_bytes int
#     status ApplicationStatus default APPLIED ; applied_at datetime(UTC) ; updated_at datetime(UTC)
#     UniqueConstraint("student_id", "internship_id", name="uq_application_student_internship")   <- the backstop for SEC-15
#
# RULES
#   Do not store the resume path or any absolute filesystem path, only the generated stored name. Imports: auth.models.User and internship.models.Internship (already merged).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
