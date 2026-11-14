import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { adminCreateInternship, adminListInternships, adminUpdateInternship } from "../../api/adminInternshipApi.js";
import InternshipForm from "../../components/admin/InternshipForm.jsx";
import StatusMessage from "../../components/common/StatusMessage.jsx";
import { formatDate } from "../../components/internships/InternshipCard.jsx";

const PAGE_SIZE = 20;

export default function AdminInternshipsPage() {
    const [data, setData] = useState({ items: [], total: 0 });
    const [page, setPage] = useState(1);
    const [editing, setEditing] = useState(null); // null = closed, {} = new, listing = edit
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState({ kind: "", text: "" });

    const load = useCallback(async () => {
        setData(await adminListInternships({ page, page_size: PAGE_SIZE }));
    }, [page]);

    useEffect(() => {
        load()
            .catch((err) => setMessage({ kind: "error", text: err.message || "Something went wrong" }))
            .finally(() => setLoading(false));
    }, [load]);

    // Throws on failure so InternshipForm can map the server's field errors onto its inputs.
    async function save(payload) {
        if (editing && editing.id) await adminUpdateInternship(editing.id, payload);
        else await adminCreateInternship(payload);
        setEditing(null);
        setMessage({ kind: "success", text: "Internship saved" });
        await load();
    }

    const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));
    return (
        <div>
            <div className="row" style={{ justifyContent: "space-between" }}>
                <h1>Manage Internships</h1>
                <span className="row">
                    <Link to="/admin/applications">View applications</Link>
                    <button type="button" className="btn" onClick={() => setEditing({})}>Add internship</button>
                </span>
            </div>
            {message.text && <StatusMessage kind={message.kind} message={message.text} />}
            {editing && <InternshipForm initial={editing.id ? editing : null} onSubmit={save} onCancel={() => setEditing(null)} />}
            {loading && <StatusMessage kind="loading" message="Loading internships..." />}
            {!loading && data.items.length === 0 && <StatusMessage kind="empty" message="No internships yet. Add the first one." />}
            {data.items.length > 0 && (
                <table className="table card">
                    <thead>
                        <tr><th>Title</th><th>Company</th><th>Deadline</th><th>Status</th><th>Applications</th><th /></tr>
                    </thead>
                    <tbody>
                        {data.items.map((l) => (
                            <tr key={l.id}>
                                <td data-label="Title">{l.title}</td>
                                <td data-label="Company">{l.company}</td>
                                <td data-label="Deadline">{formatDate(l.deadline)}</td>
                                <td data-label="Status">{l.status}</td>
                                <td data-label="Applications"><Link to={`/admin/applications?internship=${l.id}`}>{l.application_count}</Link></td>
                                <td><button type="button" className="btn btn-secondary btn-small" onClick={() => setEditing(l)}>Edit</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
            {totalPages > 1 && (
                <div className="row">
                    <button type="button" className="btn btn-secondary btn-small" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</button>
                    <span>Page {page} of {totalPages}</span>
                    <button type="button" className="btn btn-secondary btn-small" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next</button>
                </div>
            )}
        </div>
    );
}
