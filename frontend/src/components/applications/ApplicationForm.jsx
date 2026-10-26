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
