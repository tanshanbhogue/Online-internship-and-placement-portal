// ==============================================================================
// FILE   : frontend/src/components/NavBar.jsx
// STORY  : Foundation - shared scaffold (chore, no backlog issue)
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
// ==============================================================================
//
// PURPOSE
//   Top navigation bar shown on every authenticated page.
//
// CODE TO WRITE
//   Static links (plain strings, no imports from feature modules): Internships (/internships), My Applications (/applications),
//   Practice (/practice), Practice History (/practice/history), Admin Question Bank (/admin/question-bank, shown only to admins).
//   Reads the current user through an optional `useAuth` found via import.meta.glob("../context/AuthContext.jsx"); if auth is not available yet show only the brand and Login/Register links.
//   Logout button calls logout() from the auth context when available. Responsive: collapses to a menu button under 640px (NFR003).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
