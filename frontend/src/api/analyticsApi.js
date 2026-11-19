// Contract
//   filters = { source: "all" | "practice" | "mock", dateFrom: "YYYY-MM-DD" | "", dateTo: "YYYY-MM-DD" | "" }
//   getAnalyticsSummary(filters)        -> { has_data, total_attempts, practice_attempts, mock_attempts, average_score, best_score, latest_score, last_attempt_at }
//   getAnalyticsAttempts(filters, limit)-> { items: [{ kind, id, title, category, score_percent, completed_at }], total }
//   toParams(filters)                   shared with story #27's api file
import client from "./client";

export function toParams(filters = {}) {
  const params = {};
  if (filters.source && filters.source !== "all") params.source = filters.source;
  if (filters.dateFrom) params.date_from = filters.dateFrom;
  if (filters.dateTo) params.date_to = filters.dateTo;
  return params;
}

export async function getAnalyticsSummary(filters) {
  const { data } = await client.get("/analytics/summary", { params: toParams(filters) });
  return data;
}

export async function getAnalyticsAttempts(filters, limit = 20) {
  const { data } = await client.get("/analytics/attempts", { params: { ...toParams(filters), limit } });
  return data;
}
