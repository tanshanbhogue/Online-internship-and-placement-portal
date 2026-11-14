import { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { adminListApplications, adminSetApplicationStatus } from "../../api/adminInternshipApi.js";
import ApplicationStatusBadge from "../../components/applications/ApplicationStatusBadge.jsx";
import StatusMessage from "../../components/common/StatusMessage.jsx";
import { formatDate } from "../../components/internships/InternshipCard.jsx";

const PAGE_SIZE = 20;
const STATUSES = ["Applied", "Shortlisted", "Rejected", "Selected"];

export default function AdminApplicationsPage() {
    const [params] = useSearchParams();
    const internshipId = params.get("internship");
    const [data, setData] = useState({ items: [], total: 0 });
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState({ kind: "", text: "" });

    const load = useCallback(async () => {
        const query = { page, page_size: PAGE_SIZE };
        if (internshipId) query.internship_id = internshipId;
        setData(await adminListApplications(query));
    }, [page, internshipId]);

    useEffect(() => {
        load()
            .catch((err) => setMessage({ kind: "error", text: err.message || "Something went wrong" }))
            .finally(() => setLoading(false));
    }, [load]);

    async function changeStatus(application, status) {
        try {
            const updated = await adminSetApplicationStatus(application.id, status);
            setData((d) => ({ ...d, items: d.items.map((a) => (a.id === updated.id ? updated : a)) }));
            setMessage({ kind: "success", text: `Status set to ${status}` });
        } catch (err) {
            setMessage({ kind: "error", text: err.message || "Something went wrong" });
        }
    }

    const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));
    return (
        <div>
            <div className="row" style={{ justifyContent: "space-between" }}>
                <h1>Student Applications</h1>
                <Link to="/admin/internships">Back to internships</Link>
            </div>
            {message.text && <StatusMessage kind={message.kind} message={message.text} />}
            {loading && <StatusMessage kind="loading" message="Loading applications..." />}
            {!loading && data.items.length === 0 && <StatusMessage kind="empty" message="No applications yet" />}
            {data.items.length > 0 && (
                <table className="table card">
                    <thead>
                        <tr><th>Student</th><th>Internship</th><th>Applied on</th><th>Resume</th><th>Status</th><th>Change status</th></tr>
                    </thead>
                    <tbody>
                        {data.items.map((a) => (
                            <tr key={a.id}>
                                <td data-label="Student">{a.student_name}<br /><small>{a.student_email}</small></td>
                                <td data-label="Internship">{a.internship_title}<br /><small>{a.company}</small></td>
                                <td data-label="Applied on">{formatDate(a.applied_at)}</td>
                                <td data-label="Resume">{a.resume_original_name}</td>
                                <td data-label="Status"><ApplicationStatusBadge status={a.status} /></td>
                                <td data-label="Change status">
                                    <select aria-label={`Status for ${a.student_name}`} value={a.status} onChange={(e) => changeStatus(a, e.target.value)}>
                                        {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                                    </select>
                                </td>
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