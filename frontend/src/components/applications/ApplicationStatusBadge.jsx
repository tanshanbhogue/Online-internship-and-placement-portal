// ==============================================================================
// FILE   : frontend/src/components/applications/ApplicationStatusBadge.jsx
// STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
// OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
// ==============================================================================
//
// PURPOSE
//   Small coloured badge for Applied / Shortlisted / Rejected / Selected.
//
// BEHAVIOUR
//   props { status }. Colour plus text (never colour alone, accessibility). Unknown status falls back to a neutral badge.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

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
