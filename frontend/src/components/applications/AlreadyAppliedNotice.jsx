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
