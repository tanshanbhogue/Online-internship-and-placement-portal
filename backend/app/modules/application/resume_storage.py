# ==============================================================================
# FILE   : backend/app/modules/application/resume_storage.py
# STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
# ==============================================================================
#
# PURPOSE
#   Validates and stores uploaded resumes safely (SEC-16). Isolated here so file handling can be reviewed and tested on its own.
#
# EXPOSES
#   @dataclass StoredResume: stored_name, original_name, content_type, size_bytes
#   save_resume(upload: UploadFile) -> StoredResume     # raises InvalidFile (422) with a clear message
#   delete_resume(stored_name) -> None                  # used to roll back when the DB insert fails
#   open_resume_path(stored_name) -> Path               # for a future admin download; verifies the path stays inside the storage dir
#
# RULES (SEC-16, SEC-18)
#   - allowed: PDF and DOCX only; max settings.RESUME_MAX_BYTES (5 MB); read in chunks and stop early when too big.
#   - do NOT trust the filename or the client Content-Type: check magic bytes (%PDF- for PDF; ZIP header 'PK' plus word/ entries for DOCX).
#   - store under settings.RESUME_STORAGE_DIR (outside any web-served path, created on demand) using a random uuid name + the verified extension; never reuse the original name for the path.
#   - keep original_name only as display text (strip path parts, limit length).
#   - never log file content or the original filename together with user ids.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
