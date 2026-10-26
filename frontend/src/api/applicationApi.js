// ==============================================================================
// FILE   : frontend/src/api/applicationApi.js
// STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
// ==============================================================================
//
// PURPOSE
//   API calls for applications.
//
// EXPOSES
//   submitApplication({ internshipId, coverNote, resumeFile }) -> Promise<ApplicationOut>   (FormData, multipart; let the browser set the boundary header)
//   listMyApplications() -> Promise<{ items }>
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import client from "./client";

export async function submitApplication({ internshipId, coverNote, resumeFile }) {
  const form = new FormData();
  form.append("internship_id", String(internshipId));
  if (coverNote && coverNote.trim()) form.append("cover_note", coverNote.trim());
  if (resumeFile) form.append("resume", resumeFile);
  // axios must not JSON-encode this body; the browser then adds the multipart boundary itself.
  const { data } = await client.post("/applications", form, { headers: { "Content-Type": "multipart/form-data" } });
  return data;
}

export async function listMyApplications() {
  const { data } = await client.get("/applications/mine");
  return data; // { items }
}
