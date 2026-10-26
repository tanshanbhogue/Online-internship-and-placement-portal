// ==============================================================================
// FILE   : frontend/src/api/sessionApi.js
// STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
// OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
// ==============================================================================
//
// PURPOSE
//   API calls for login, logout and session restore.
//
// EXPOSES
//   login({ email, password }) -> Promise<{ user }> ; logout() -> Promise<void> ; fetchMe() -> Promise<UserOut> (client.get('/auth/me')).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import client from "./client";

export async function login({ email, password }) {
  const { data } = await client.post("/auth/login", { email, password });
  return data; // { user }
}

export async function logout() {
  await client.post("/auth/logout");
}

export async function fetchMe() {
  const { data } = await client.get("/auth/me");
  return data;
}
