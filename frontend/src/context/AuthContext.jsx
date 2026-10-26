// ==============================================================================
// FILE   : frontend/src/context/AuthContext.jsx
// STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
// OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
// ==============================================================================
//
// PURPOSE
//   Global session state for the SPA.
//
// EXPOSES
//   <AuthProvider> and hook useAuth() -> { user, loading, login(email, password), logout(), isAdmin, isStudent }
//   On mount call fetchMe(); 401 means 'not logged in' (user = null, loading false) and is not an error message.
//   Listens for the window "auth:expired" event (from api/client.js): clear user and navigate to /login with a 'session expired' notice.
//
// RULES
//   Hold the user object only in React state (never localStorage/sessionStorage); the cookie is the credential.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
