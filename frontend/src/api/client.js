// ==============================================================================
// FILE   : frontend/src/api/client.js
// STORY  : Foundation - shared scaffold (chore, no backlog issue)
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
// ==============================================================================
//
// PURPOSE
//   The single axios instance used by every api/*.js file.
//
// CODE TO WRITE
//   - axios.create({ baseURL: "/api", withCredentials: true, headers: {"Content-Type": "application/json"} }); multipart calls override the header per request.
//   - Response interceptor: convert failures to `ApiError { status, code, message, fields }` using the shared error body
//     (fallback message "Something went wrong" when the server is unreachable).
//   - On HTTP 401 with code "not_authenticated" (not on /auth/login) dispatch window.dispatchEvent(new Event("auth:expired")); AuthContext (story #19) listens and redirects to /login.
//   - Export `client` (default) and `ApiError`. Never store tokens; never log request bodies.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
