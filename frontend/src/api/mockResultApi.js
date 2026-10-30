import client from "./client";

export async function getMockHistory() {
  const { data } = await client.get("/mock-results");
  return data;
}

export async function getMockResult(attemptId, { difficulty, outcome } = {}) {
  const params = {};
  if (difficulty) params.difficulty = difficulty;
  if (outcome) params.outcome = outcome;
  const { data } = await client.get(`/mock-results/${attemptId}`, { params });
  return data;
}
