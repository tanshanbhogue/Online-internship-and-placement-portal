
import client from "./client";

export async function registerStudent({ name, email, password, college, batch }) {
    const payload = { name, email, password };
    if (college && college.trim()) payload.college = college.trim();
    if (batch && batch.trim()) payload.batch = batch.trim();
    const { data } = await client.post("/auth/register", payload);
    return data;
}
