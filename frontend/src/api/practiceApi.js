// ==============================================================================
// FILE   : frontend/src/api/practiceApi.js
// STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   API calls for practice sessions.
//
// EXPOSES
//   startSession({ categoryId, count }) ; submitAnswer(sessionId, { questionId, selectedOptionId | code }) ; finishSession(sessionId) ; getSessionResult(sessionId) ; getPracticeHistory().
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import client from "./client";

export async function startSession({ categoryId, count }) {
  const body = { category_id: Number(categoryId) };
  if (count) body.count = Number(count);
  const { data } = await client.post("/practice/sessions", body);
  return data;
}

export async function submitAnswer(sessionId, { questionId, selectedOptionId, code }) {
  const body = { question_id: questionId };
  if (selectedOptionId !== undefined && selectedOptionId !== null) body.selected_option_id = selectedOptionId;
  if (code !== undefined && code !== null) body.code = code;
  const { data } = await client.post(`/practice/sessions/${sessionId}/answers`, body);
  return data;
}

export async function finishSession(sessionId) {
  const { data } = await client.post(`/practice/sessions/${sessionId}/finish`);
  return data;
}

export async function getSessionResult(sessionId) {
  const { data } = await client.get(`/practice/sessions/${sessionId}`);
  return data;
}

export async function getPracticeHistory() {
  const { data } = await client.get("/practice/history");
  return data; // { items }
}
