import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { getInternship } from "../api/internshipApi.js";
import ApplicationStatusBadge from "../components/applications/ApplicationStatusBadge.jsx";
import StatusMessage from "../components/common/StatusMessage.jsx";
import { formatDate, formatDuration, formatStipend } from "../components/internships/InternshipCard.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useApplicationStatus } from "../hooks/useApplicationStatus.js";

function ApplyArea({ internship }) {
  const { loading, applied, status, appliedAt, error } = useApplicationStatus(internship.id);
  if (loading) return <StatusMessage kind="loading" message="Checking your application..." />;
  if (error) return <StatusMessage kind="error" message={error} />;
  if (applied) {
    return (
      <div className="status status-success" aria-live="polite">
        <strong>Already applied</strong> <ApplicationStatusBadge status={status} />
        {appliedAt && <span className="small"> on {formatDate(appliedAt)}</span>}{" "}
        <Link to="/applications">View My Applications</Link>
      </div>
    );
  }
  if (!internship.is_open) {
    return <button type="button" className="btn" disabled>Application window closed</button>;
  }
  return <Link className="btn" to={`/internships/${internship.id}/apply`}>Apply</Link>;
}

export default function InternshipDetailPage() {
  const { id } = useParams();
  const location = useLocation();
  const { isStudent } = useAuth();
  const [state, setState] = useState({ loading: true, error: "", notFound: false, data: null });

  useEffect(() => {
    let cancelled = false;
    setState({ loading: true, error: "", notFound: false, data: null });
    getInternship(id)
      .then((data) => !cancelled && setState({ loading: false, error: "", notFound: false, data }))
      .catch((err) => {
        if (cancelled) return;
        if (err.status === 404) setState({ loading: false, error: "", notFound: true, data: null });
        else setState({ loading: false, error: err.message || "Something went wrong", notFound: false, data: null });
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  const back = <Link to={`/internships${location.state?.fromSearch || ""}`}>&larr; Back to internships</Link>;
  const { loading, error, notFound, data } = state;

  return (
    <div className="page-medium">
      <p>{back}</p>
      {loading && <StatusMessage kind="loading" message="Loading internship..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {notFound && <StatusMessage kind="empty" message="Sorry, we could not find that internship." />}
      {data && (
        <article className="card">
          <div className="row spread">
            <h1>{data.title}</h1>
            <span className={`badge ${data.is_open ? "badge-open" : "badge-closed"}`}>{data.is_open ? "Open" : "Closed"}</span>
          </div>
          <p className="muted">{data.company}</p>
          <div className="card-meta">
            {data.location && <span>{data.location}</span>}
            {data.domain && <span>{data.domain}</span>}
            <span>{formatStipend(data.stipend_per_month)}</span>
            <span>{formatDuration(data.duration_months)}</span>
            <span>Deadline: {formatDate(data.deadline)}</span>
          </div>
          <h2>About the role</h2>
          <p style={{ whiteSpace: "pre-wrap" }}>{data.description}</p>
          {data.eligibility && (
            <>
              <h2>Eligibility</h2>
              <p style={{ whiteSpace: "pre-wrap" }}>{data.eligibility}</p>
            </>
          )}
          {isStudent && <div style={{ marginTop: "1rem" }}><ApplyArea internship={data} /></div>}
        </article>
      )}
    </div>
  );
}
