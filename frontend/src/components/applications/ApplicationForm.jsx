// ==============================================================================
// FILE   : frontend/src/components/applications/ApplicationForm.jsx
// STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
// ==============================================================================
//
// PURPOSE
//   Application form (resume upload + cover note).
//
// BEHAVIOUR
//   props { internship, onSubmitted }. Fields: resume file input (accept .pdf,.docx, client checks size <= 5 MB and type for quick feedback only), cover note textarea with 2000-char counter.
//   On submit call submitApplication. Highlight missing fields and return without submitting (use case A2). Map server errors: already_applied -> show AlreadyAppliedNotice-style message,
//   application_window_closed -> message, invalid_file -> field error on the resume input. Success -> onSubmitted(application).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useState } from "react";

import { submitApplication } from "../../api/applicationApi.js";
import AlreadyAppliedNotice from "./AlreadyAppliedNotice.jsx";
import StatusMessage from "../common/StatusMessage.jsx";

const MAX_BYTES = 5 * 1024 * 1024;
const MAX_NOTE = 2000;

// Quick feedback only: the server re-checks size, type AND the file's real content (SEC-16).
function clientFileProblem(file) {
  if (!file) return "Please upload your resume";
  if (!/\.(pdf|docx)$/i.test(file.name)) return "Resume must be a PDF or DOCX file";
  if (file.size > MAX_BYTES) return "Resume must be 5 MB or smaller";
  if (file.size === 0) return "The resume file is empty";
  return "";
}

export default function ApplicationForm({ internship, onSubmitted }) {
  const [file, setFile] = useState(null);
  const [note, setNote] = useState("");
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [alreadyApplied, setAlreadyApplied] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError("");
    const found = {};
    const fileProblem = clientFileProblem(file);
    if (fileProblem) found.resume = fileProblem;
    if (note.length > MAX_NOTE) found.cover_note = `Cover note must be at most ${MAX_NOTE} characters`;
    setErrors(found);
    if (Object.keys(found).length) return; // highlight and stop (alternate flow A2)

    setSubmitting(true);
    try {
      const application = await submitApplication({ internshipId: internship.id, coverNote: note, resumeFile: file });
      onSubmitted?.(application);
    } catch (err) {
      if (err.code === "already_applied") {
        setAlreadyApplied(true);
      } else if (err.code === "application_window_closed") {
        setFormError("Application window closed");
      } else if (err.code === "invalid_file") {
        setErrors({ resume: err.message });
      } else if (err.status === 422 && err.fields && Object.keys(err.fields).length) {
        const mapped = {};
        for (const [field, messages] of Object.entries(err.fields)) mapped[field] = messages[0];
        setErrors(mapped);
      } else {
        setFormError(err.message || "Something went wrong");
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (alreadyApplied) return <AlreadyAppliedNotice />;

  return (
    <form onSubmit={handleSubmit} noValidate>
      {formError && <StatusMessage kind="error" message={formError} />}

      <div className="field">
        <label htmlFor="apply-resume">Resume (PDF or DOCX, up to 5 MB)</label>
        <input id="apply-resume" type="file" accept=".pdf,.docx" onChange={(e) => setFile(e.target.files?.[0] || null)}
          aria-invalid={!!errors.resume} aria-describedby={errors.resume ? "apply-resume-err" : undefined} />
        {errors.resume && <p id="apply-resume-err" className="field-error" role="alert">{errors.resume}</p>}
      </div>

      <div className="field">
        <label htmlFor="apply-note">Cover note (optional)</label>
        <textarea id="apply-note" value={note} onChange={(e) => setNote(e.target.value)}
          aria-invalid={!!errors.cover_note} aria-describedby="apply-note-count" />
        <span id="apply-note-count" className="hint" aria-live="polite">{note.length} / {MAX_NOTE}</span>
        {errors.cover_note && <p className="field-error" role="alert">{errors.cover_note}</p>}
      </div>

      <button className="btn" type="submit" disabled={submitting}>
        {submitting ? "Submitting..." : "Submit application"}
      </button>
    </form>
  );
}
