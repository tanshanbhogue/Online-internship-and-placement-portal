// Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
// File: frontend/src/api/mockTestApi.js
//
// Contract (thin wrappers; every call is student-only and uses the HttpOnly session cookie)
//   listMockTests()                                  -> { items: [{ id, title, description, category, duration_minutes, question_count, open_attempt_id }] }
//   startAttempt(testId)                             -> attempt state + { resumed }   (starts, or resumes the open attempt)
//   getAttempt(attemptId)                            -> attempt state (remaining_seconds is SERVER time; closed attempts have status != "in_progress")
//   saveAnswer(attemptId, { questionId, selectedOptionId })   selectedOptionId null clears the answer
//   submitAttempt(attemptId, answers?)               -> { attempt_id, status, auto_submitted, submitted_at }
import client from "./client";

export async function listMockTests() {
  const { data } = await client.get("/mock-tests");
  return data;
}

export async function startAttempt(testId) {
  const { data } = await client.post(`/mock-tests/${testId}/attempts`);
  return data;
}

export async function getAttempt(attemptId) {
  const { data } = await client.get(`/mock-attempts/${attemptId}`);
  return data;
}

export async function saveAnswer(attemptId, { questionId, selectedOptionId }) {
  const { data } = await client.put(`/mock-attempts/${attemptId}/answers`, {
    question_id: questionId,
    selected_option_id: selectedOptionId ?? null,
  });
  return data;
}

export async function submitAttempt(attemptId, answers) {
  const body = answers ? { answers: answers.map((a) => ({ question_id: a.questionId, selected_option_id: a.selectedOptionId })) } : {};
  const { data } = await client.post(`/mock-attempts/${attemptId}/submit`, body);
  return data;
}
