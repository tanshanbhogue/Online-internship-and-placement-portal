// ==============================================================================
// FILE   : frontend/src/routes/internship.routes.jsx
// STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Route registration for listings.
//
// EXPORT
//   export default [{ path: "/internships", element: <InternshipListPage />, access: "authenticated" }, { path: "/internships/:id", element: <InternshipDetailPage />, access: "authenticated" }]
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import InternshipDetailPage from "../pages/InternshipDetailPage.jsx";
import InternshipListPage from "../pages/InternshipListPage.jsx";

export default [
  { path: "/internships", element: <InternshipListPage />, access: "authenticated" },
  { path: "/internships/:id", element: <InternshipDetailPage />, access: "authenticated" },
];
