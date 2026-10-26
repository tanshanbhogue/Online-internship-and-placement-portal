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

import io
import re
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from fastapi import UploadFile

from app.core.config import settings
from app.core.errors import InvalidFile

CHUNK_SIZE = 64 * 1024
MAX_ORIGINAL_NAME = 255

# Detected-by-content type -> (extension, content type we record). The client's Content-Type is never trusted.
_PDF = (".pdf", "application/pdf")
_DOCX = (".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@dataclass(frozen=True)
class StoredResume:
    stored_name: str
    original_name: str
    content_type: str
    size_bytes: int


def _storage_dir() -> Path:
    path = Path(settings.RESUME_STORAGE_DIR).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _clean_original_name(raw: str | None) -> str:
    """Display text only: strip any path parts and control characters, limit the length."""
    name = PurePosixPath((raw or "").replace("\\", "/")).name
    name = re.sub(r"[\x00-\x1f\x7f]", "", name).strip()
    return (name or "resume")[:MAX_ORIGINAL_NAME]


def _read_limited(upload: UploadFile) -> bytes:
    """Read in chunks and stop as soon as the file is too big (no unbounded memory use)."""
    limit = settings.RESUME_MAX_BYTES
    buffer = io.BytesIO()
    total = 0
    while True:
        chunk = upload.file.read(CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise InvalidFile(f"Resume must be {limit // (1024 * 1024)} MB or smaller" if limit >= 1024 * 1024 else "Resume is too large")
        buffer.write(chunk)
    return buffer.getvalue()


def _detect(data: bytes) -> tuple[str, str] | None:
    """Identify PDF/DOCX from the file's own bytes (magic number), not its name or declared type."""
    if data.startswith(b"%PDF-"):
        return _PDF
    if data.startswith(b"PK"):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                names = archive.namelist()
        except zipfile.BadZipFile:
            return None
        if "[Content_Types].xml" in names and any(n.startswith("word/") for n in names):
            return _DOCX
    return None


def save_resume(upload: UploadFile) -> StoredResume:
    if upload is None or not (upload.filename or "").strip():
        raise InvalidFile("Please choose a resume file")
    original_name = _clean_original_name(upload.filename)

    data = _read_limited(upload)
    if not data:
        raise InvalidFile("The resume file is empty")

    detected = _detect(data)
    if detected is None:
        raise InvalidFile("Resume must be a PDF or DOCX file")
    extension, content_type = detected
    # A name that claims another type (e.g. "cv.exe" holding PDF bytes) is refused as well.
    if Path(original_name).suffix.lower() != extension:
        raise InvalidFile("The file extension does not match its content")

    stored_name = f"{uuid.uuid4().hex}{extension}"  # random; the client's name never reaches the filesystem
    (_storage_dir() / stored_name).write_bytes(data)
    return StoredResume(stored_name=stored_name, original_name=original_name, content_type=content_type, size_bytes=len(data))


def open_resume_path(stored_name: str) -> Path:
    """Resolve a stored file for a future admin download, refusing anything outside the storage directory."""
    if not re.fullmatch(r"[0-9a-f]{32}\.(pdf|docx)", stored_name or ""):
        raise InvalidFile("Invalid file reference")
    base = _storage_dir()
    path = (base / stored_name).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise InvalidFile("Invalid file reference")
    return path


def delete_resume(stored_name: str) -> None:
    """Roll back a stored file (e.g. when the DB insert fails). Silent if it is already gone or the name is odd."""
    if not re.fullmatch(r"[0-9a-f]{32}\.(pdf|docx)", stored_name or ""):
        return
    try:
        (_storage_dir() / stored_name).unlink(missing_ok=True)
    except OSError:
        pass
