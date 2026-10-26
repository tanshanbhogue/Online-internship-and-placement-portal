// ==============================================================================
// FILE   : frontend/src/api/applicationCheckApi.js
// STORY  : #18 Prevent Duplicate Internship Applications  [FR-002; SEC-15]
// OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   API call for the duplicate check.
//
// EXPOSES
//   checkApplication(internshipId) -> Promise<{ internship_id, applied, status, applied_at }> via client.get(`/applications/check/${internshipId}`).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import client from "./client";

export async function checkApplication(internshipId) {
  const { data } = await client.get(`/applications/check/${internshipId}`);
  return data; // { internship_id, applied, status, applied_at }
}
