// ==============================================================================
// FILE   : frontend/src/api/registerApi.js
// STORY  : #14 Student Registration  [FR-001; SEC-02, SEC-08, SEC-09]
// OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 2
// ==============================================================================
//
// PURPOSE
//   API call for registration.
//
// EXPOSES
//   registerStudent({ name, email, password, college, batch }) -> Promise<RegisterResponse>  via client.post('/auth/register'). Rejects with ApiError (see api/client.js).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
import client from "./client";

export async function registerStudent({ name, email, password, college, batch }) {
    const payload = { name, email, password };
    if (college && college.trim()) payload.college = college.trim();
    if (batch && batch.trim()) payload.batch = batch.trim();
    const { data } = await client.post("/auth/register", payload);
    return data;
}
