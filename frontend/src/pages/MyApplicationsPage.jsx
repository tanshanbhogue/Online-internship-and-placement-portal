// ==============================================================================
// FILE   : frontend/src/pages/MyApplicationsPage.jsx
// STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
// ==============================================================================
//
// PURPOSE
//   Page at /applications ('My Applications').
//
// BEHAVIOUR
//   Loads listMyApplications; table/cards with internship title, company, applied date and ApplicationStatusBadge, each linking to the listing. Empty state: 'You have not applied to any internships yet' with a link to /internships.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { listMyApplications } from "../api/applicationApi.js";
import ApplicationStatusBadge from "../components/applications/ApplicationStatusBadge.jsx";
import StatusMessage from "../components/common/StatusMessage.jsx";
import { formatDate } from "../components/internships/InternshipCard.jsx";

export default function MyApplicationsPage() {
  const location = useLocation();
  const [state, setState] = useState({ loading: true, error: "", items: [] });

  useEffect(() => {
    let cancelled = false;
    listMyApplications()
      .then((data) => !cancelled && setState({ loading: false, error: "", items: data.items }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", items: [] }));
    return () => {
      cancelled = true;
    };
  }, []);

  const { loading, error, items } = state;
  return (
    <div>
      <h1>My Applications</h1>
      {location.state?.submitted && <StatusMessage kind="success" message="Application submitted" />}
      {loading && <StatusMessage kind="loading" message="Loading your applications..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {!loading && !error && items.length === 0 && (
        <StatusMessage kind="empty" message="You have not applied to any internships yet">
          <Link to="/internships">Browse internships</Link>
        </StatusMessage>
      )}
      {items.length > 0 && (
        <table className="table card">
          <thead>
            <tr><th>Internship</th><th>Company</th><th>Applied on</th><th>Status</th></tr>
          </thead>
          <tbody>
            {items.map((a) => (
              <tr key={a.id}>
                <td data-label="Internship"><Link to={`/internships/${a.internship.id}`}>{a.internship.title}</Link></td>
                <td data-label="Company">{a.internship.company}</td>
                <td data-label="Applied on">{formatDate(a.applied_at)}</td>
                <td data-label="Status"><ApplicationStatusBadge status={a.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
