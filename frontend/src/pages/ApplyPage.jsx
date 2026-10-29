

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getInternship } from "../api/internshipApi.js";
import AlreadyAppliedNotice from "../components/applications/AlreadyAppliedNotice.jsx";
import ApplicationForm from "../components/applications/ApplicationForm.jsx";
import StatusMessage from "../components/common/StatusMessage.jsx";
import { useApplicationStatus } from "../hooks/useApplicationStatus.js";

export default function ApplyPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const status = useApplicationStatus(id);
  const [state, setState] = useState({ loading: true, error: "", data: null });

  useEffect(() => {
    let cancelled = false;
    getInternship(id)
      .then((data) => !cancelled && setState({ loading: false, error: "", data }))
      .catch((err) =>
        !cancelled &&
        setState({ loading: false, error: err.status === 404 ? "Sorry, we could not find that internship." : err.message || "Something went wrong", data: null })
      );
    return () => {
      cancelled = true;
    };
  }, [id]);

  function handleSubmitted() {
    status.refresh();
    navigate("/applications", { state: { submitted: true } }); // the next page shows "Application submitted"
  }

  const { loading, error, data } = state;
  let body;
  if (loading || status.loading) body = <StatusMessage kind="loading" message="Loading..." />;
  else if (error) body = <StatusMessage kind="error" message={error} />;
  else if (status.applied) body = <AlreadyAppliedNotice status={status.status} appliedAt={status.appliedAt} />;
  else if (!data.is_open) body = <StatusMessage kind="error" message="Application window closed" />;
  else body = <ApplicationForm internship={data} onSubmitted={handleSubmitted} />;

  return (
    <div className="page-medium card">
      <p><Link to={`/internships/${id}`}>&larr; Back to listing</Link></p>
      <h1>Apply{data ? `: ${data.title}` : ""}</h1>
      {data && <p className="muted">{data.company}</p>}
      {body}
    </div>
  );
}
