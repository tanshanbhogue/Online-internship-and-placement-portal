// ==============================================================================
// FILE   : frontend/src/components/internships/InternshipCard.jsx
// STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Card showing one listing summary.
//
// PROPS/BEHAVIOUR
//   props { internship }. Shows title, company, location/domain, stipend and duration (format 'Rs 15,000 / month', '3 months'), short description, deadline,
//   a 'Closed' badge when !is_open. Whole card links to /internships/:id. All text rendered as plain text (SEC-10).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { Link, useLocation } from "react-router-dom";

export function formatStipend(amount) {
  if (amount === null || amount === undefined) return "Stipend not specified";
  return `Rs ${Number(amount).toLocaleString("en-IN")} / month`;
}

export function formatDuration(months) {
  if (months === null || months === undefined) return "Duration not specified";
  return `${months} ${months === 1 ? "month" : "months"}`;
}

// Deadlines are plain YYYY-MM-DD; parse as a local date so no timezone shifts the day.
export function formatDate(value) {
  if (!value) return "";
  const [y, m, d] = String(value).slice(0, 10).split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

// All text is rendered as plain text by React (SEC-10).
export default function InternshipCard({ internship }) {
  const location = useLocation();
  const place = [internship.location, internship.domain].filter(Boolean).join(" · ");
  return (
    <Link to={`/internships/${internship.id}`} state={{ fromSearch: location.search }} className="card-link">
      <article className="card">
        <div className="row spread">
          <h2>{internship.title}</h2>
          {!internship.is_open && <span className="badge badge-closed">Closed</span>}
        </div>
        <p className="muted">{internship.company}</p>
        {place && <p className="small">{place}</p>}
        <div className="card-meta">
          <span>{formatStipend(internship.stipend_per_month)}</span>
          <span>{formatDuration(internship.duration_months)}</span>
          <span>Deadline: {formatDate(internship.deadline)}</span>
        </div>
        <p>{internship.short_description}</p>
      </article>
    </Link>
  );
}
