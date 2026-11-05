// Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
// File: frontend/src/components/mocktest/AutoSubmitNotice.jsx
//
// Contract
//   <AutoSubmitNotice status="auto_submitted" />   the on-screen notice of UC-6 step 8; renders nothing for any other status.
import "../../styles/mock-timer.css";

export default function AutoSubmitNotice({ status }) {
  if (status !== "auto_submitted") return null;
  return (
    <div className="status status-warning auto-submit-notice" role="status" data-testid="auto-submit-notice">
      <strong>Time was up.</strong> This test was submitted automatically. Every answer saved before the time limit
      was scored; questions left blank count as not answered.
    </div>
  );
}
