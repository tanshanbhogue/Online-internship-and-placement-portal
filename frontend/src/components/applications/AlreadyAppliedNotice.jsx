// ==============================================================================
// FILE   : frontend/src/components/applications/AlreadyAppliedNotice.jsx
// STORY  : #18 Prevent Duplicate Internship Applications  [FR-002; SEC-15]
// OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   Notice shown instead of the application form/button when the student already applied.
//
// BEHAVIOUR
//   props { status, appliedAt }. Text 'You have already applied to this internship' with the status and date, plus a link to /applications (My Applications). Use StatusMessage styling.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { Link } from "react-router-dom";

import { formatDate } from "../internships/InternshipCard.jsx";
import StatusMessage from "../common/StatusMessage.jsx";
import ApplicationStatusBadge from "./ApplicationStatusBadge.jsx";

export default function AlreadyAppliedNotice({ status, appliedAt }) {
  return (
    <StatusMessage kind="success" message="You have already applied to this internship">
      {status && <ApplicationStatusBadge status={status} />}
      {appliedAt && <span className="small"> (applied on {formatDate(appliedAt)})</span>}{" "}
      <Link to="/applications">View My Applications</Link>
    </StatusMessage>
  );
}
