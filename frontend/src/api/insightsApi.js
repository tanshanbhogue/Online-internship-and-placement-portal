import client from "./client";
import { toParams } from "./analyticsApi.js";

export async function getTrends(filters, window = 3) {
  const { data } = await client.get("/analytics/trends", { params: { ...toParams(filters), window } });
  return data;
}

export async function getStrengthsWeaknesses(filters) {
  const { data } = await client.get("/analytics/strengths-weaknesses", { params: toParams(filters) });
  return data;
}