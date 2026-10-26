// ==============================================================================
// FILE   : frontend/src/pages/InternshipListPage.jsx
// STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Page at /internships.
//
// BEHAVIOUR
//   Keeps filters + page in the URL query string. Loads via listInternships; shows loading and error states via StatusMessage.
//   Empty with no filters -> 'No internships currently available.'; empty with filters -> 'No matching internships found' with a Reset filters button (use case alternate flows A1, A2).
//   Renders InternshipCard grid with pagination controls.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
