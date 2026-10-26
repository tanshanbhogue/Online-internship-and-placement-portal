// ==============================================================================
// FILE   : frontend/src/pages/InternshipDetailPage.jsx
// STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Page at /internships/:id.
//
// BEHAVIOUR
//   Loads getInternship(id). Shows full description, eligibility, deadline, stipend, duration and a back link to the list (state preserved). 404 -> friendly not-found message.
//   Phase 4 (this story): render an Apply area as a TODO placeholder only.
//   Phase 6 (story #17 PR, same owner, one sanctioned edit): add the 'Apply' button linking to /internships/:id/apply, disabled with 'Application window closed' when !is_open,
//   and use hooks/useApplicationStatus (story #18) to show 'Already applied' with the status badge instead of the button.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
