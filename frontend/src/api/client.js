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

import axios from "axios";

export class ApiError extends Error {
  constructor({ status = 0, code = "error", message = "Something went wrong", fields = {} } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fields = fields || {};
  }
}

// The one axios instance. No tokens are stored anywhere: the HttpOnly cookie is the credential.
const client = axios.create({
  baseURL: "/api",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const response = error.response;
    if (!response) {
      return Promise.reject(new ApiError({ status: 0, code: "network_error", message: "Something went wrong" }));
    }
    const body = response.data && typeof response.data === "object" ? response.data : {};
    const apiError = new ApiError({
      status: response.status,
      code: body.code || "error",
      message: typeof body.detail === "string" ? body.detail : "Something went wrong",
      fields: body.fields || {},
    });

    // An expired/invalid session mid-use sends the user to /login. The login call itself and the
    // session probe (/auth/me, used on page load) are expected to 401 and are not "expiry".
    const url = error.config?.url || "";
    const isSessionProbe = url.includes("/auth/login") || url.includes("/auth/me");
    if (response.status === 401 && apiError.code === "not_authenticated" && !isSessionProbe) {
      window.dispatchEvent(new Event("auth:expired"));
    }
    return Promise.reject(apiError);
  }
);

export default client;
