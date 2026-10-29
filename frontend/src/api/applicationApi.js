

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
