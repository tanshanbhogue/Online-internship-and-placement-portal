// ==============================================================================
// FILE   : frontend/src/routes/practice.routes.jsx
// STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   Route registration for the practice session pages.
//
// EXPORT
//   export default [
//     { path: "/practice/session/:sessionId", element: <PracticeSessionPage />, access: "student" },
//     { path: "/practice/result/:sessionId",  element: <PracticeResultPage />,  access: "student" },
//     { path: "/practice/history",           element: <PracticeHistoryPage />, access: "student" } ]
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import PracticeHistoryPage from "../pages/PracticeHistoryPage.jsx";
import PracticeResultPage from "../pages/PracticeResultPage.jsx";
import PracticeSessionPage from "../pages/PracticeSessionPage.jsx";

export default [
  { path: "/practice/session/:sessionId", element: <PracticeSessionPage />, access: "student" },
  { path: "/practice/result/:sessionId", element: <PracticeResultPage />, access: "student" },
  { path: "/practice/history", element: <PracticeHistoryPage />, access: "student" },
];
