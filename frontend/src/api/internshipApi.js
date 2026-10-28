

import client from "./client";

export async function listInternships(filters = {}) {
  const { data } = await client.get("/internships", { params: filters });
  return data; // { items, total, page, page_size }
}

export async function getInternship(id) {
  const { data } = await client.get(`/internships/${id}`);
  return data;
}
