// ==============================================================================
// FILE   : frontend/src/routes/register.routes.jsx
// STORY  : #14 Student Registration  [FR-001; SEC-02, SEC-08, SEC-09]
// OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 2
// ==============================================================================
//
// PURPOSE
//   Route registration for the registration page (auto-discovered by App.jsx).
//
// EXPORT
//   export default [{ path: "/register", element: <RegisterPage />, access: "public" }]
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import RegisterPage from "../pages/RegisterPage.jsx";

export default [{ path: "/register", element: <RegisterPage />, access: "public" }];
