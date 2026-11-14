import client from "./client";

export async function adminListInternships(params = {}) {
    const { data } = await client.get("/admin/internships", { params });
    return data; // { items, total, page, page_size }
}

export async function adminCreateInternship(payload) {
    const { data } = await client.post("/admin/internships", payload);
    return data;
}

export async function adminUpdateInternship(id, payload) {
    const { data } = await client.put(`/admin/internships/${id}`, payload);
    return data;
}

export async function adminListApplications(params = {}) {
    const { data } = await client.get("/admin/applications", { params });
    return data; // { items, total, page, page_size }
}

export async function adminSetApplicationStatus(id, status) {
    const { data } = await client.patch(`/admin/applications/${id}/status`, { status });
    return data;
}