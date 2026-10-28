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
