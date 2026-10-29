import client from "./client";

export async function checkApplication(internshipId) {
    const { data } = await client.get(`/applications/check/${internshipId}`);
    return data; // { internship_id, applied, status, applied_at }
}
