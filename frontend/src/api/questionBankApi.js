// ==============================================================================
// FILE   : frontend/src/api/questionBankApi.js
// STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   API calls for categories and questions (student and admin).
//
// EXPOSES
//   listCategories() ; listQuestions(categoryId, { count, difficulty })
//   admin: adminListCategories, adminCreateCategory, adminListQuestions(params), adminGetQuestion(id), adminCreateQuestion(payload), adminUpdateQuestion(id, payload), adminDeleteQuestion(id)
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import client from "./client";

export async function listCategories() {
  const { data } = await client.get("/question-bank/categories");
  return data;
}

export async function listQuestions(categoryId, { count, difficulty } = {}) {
  const params = {};
  if (count) params.count = count;
  if (difficulty) params.difficulty = difficulty;
  const { data } = await client.get(`/question-bank/categories/${categoryId}/questions`, { params });
  return data; // { items, total }
}

// ---- admin ----
export async function adminListCategories() {
  const { data } = await client.get("/admin/question-bank/categories");
  return data;
}

export async function adminCreateCategory(name) {
  const { data } = await client.post("/admin/question-bank/categories", { name });
  return data;
}

export async function adminListQuestions(params = {}) {
  const { data } = await client.get("/admin/question-bank/questions", { params });
  return data; // { items, total, page, page_size }
}

export async function adminGetQuestion(id) {
  const { data } = await client.get(`/admin/question-bank/questions/${id}`);
  return data;
}

export async function adminCreateQuestion(payload) {
  const { data } = await client.post("/admin/question-bank/questions", payload);
  return data;
}

export async function adminUpdateQuestion(id, payload) {
  const { data } = await client.put(`/admin/question-bank/questions/${id}`, payload);
  return data;
}

export async function adminDeleteQuestion(id) {
  await client.delete(`/admin/question-bank/questions/${id}`);
}
