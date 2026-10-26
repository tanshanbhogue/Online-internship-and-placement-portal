// ==============================================================================
// FILE   : frontend/src/api/internshipApi.js
// STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   API calls for internship listings.
//
// EXPOSES
//   listInternships(filters) -> {items,total,page,page_size} (client.get('/internships', { params })) ; getInternship(id) -> InternshipDetail.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import client from "./client";

export async function listInternships(filters = {}) {
  const { data } = await client.get("/internships", { params: filters });
  return data; // { items, total, page, page_size }
}

export async function getInternship(id) {
  const { data } = await client.get(`/internships/${id}`);
  return data;
}
