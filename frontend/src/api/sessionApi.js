
import client from "./client";

export async function login({ email, password }) {
  const response = await client.post("/auth/login", { email, password });
  return response.data;
}

export async function logout() {
  await client.post("/auth/logout");
}

export async function fetchMe() {
  const response = await client.get("/auth/me");
  return response.data;
}
