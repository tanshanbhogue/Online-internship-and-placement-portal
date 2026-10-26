// ==============================================================================
// FILE   : frontend/src/components/auth/ProtectedRoute.jsx
// STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
// OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
// ==============================================================================
//
// PURPOSE
//   Route guard used by App.jsx for every route.
//
// BEHAVIOUR
//   default export ProtectedRoute({ access, children }):
//     public -> render children ; authenticated -> require user ; student/admin -> require that role.
//     While auth is loading render a spinner. No user -> <Navigate to="/login" replace state={{ from: location }} />. Wrong role -> a 'not allowed' page (403).
//   Guards are UX only; the server enforces the same rules (SEC-07).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
