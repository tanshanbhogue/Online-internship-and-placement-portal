// ==============================================================================
// FILE   : frontend/src/pages/InternshipDetailPage.jsx
// STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Page at /internships/:id.
//
// BEHAVIOUR
//   Loads getInternship(id). Shows full description, eligibility, deadline, stipend, duration and a back link to the list (state preserved). 404 -> friendly not-found message.
//   Phase 4 (this story): render an Apply area as a TODO placeholder only.
//   Phase 6 (story #17 PR, same owner, one sanctioned edit): add the 'Apply' button linking to /internships/:id/apply, disabled with 'Application window closed' when !is_open,
//   and use hooks/useApplicationStatus (story #18) to show 'Already applied' with the status badge instead of the button.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

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
