// ==============================================================================
// FILE   : frontend/src/pages/ApplyPage.jsx
// STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
// ==============================================================================
//
// PURPOSE
//   Page at /internships/:id/apply.
//
// BEHAVIOUR
//   Loads the listing (getInternship) and the status (useApplicationStatus from story #18). If already applied show AlreadyAppliedNotice instead of the form (use case A1).
//   If !is_open show 'Application window closed'. Otherwise render ApplicationForm. On success show the confirmation message ('Application submitted') and navigate to /applications.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
