// Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
// File: frontend/src/api/autoSubmitApi.js
//
// Contract
//   requestAutoSubmit(attemptId) -> { attempt_id, status, auto_submitted, already_final, submitted_at, message }
//   Rejects with ApiError code "not_expired" (409) while the SERVER clock says time remains.
import client from "./client";

export async function requestAutoSubmit(attemptId) {
  const { data } = await client.post(`/mock-attempts/${attemptId}/auto-submit`);
  return data;
}
