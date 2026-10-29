

const KNOWN = {
  Applied: "badge-applied",
  Shortlisted: "badge-shortlisted",
  Rejected: "badge-rejected",
  Selected: "badge-selected",
};

// Colour plus text, never colour alone. Unknown values fall back to a neutral badge.
export default function ApplicationStatusBadge({ status }) {
  const cls = KNOWN[status] || "badge-neutral";
  return <span className={`badge ${cls}`}>{status || "Unknown"}</span>;
}
