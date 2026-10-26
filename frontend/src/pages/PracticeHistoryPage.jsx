// ==============================================================================
// FILE   : frontend/src/pages/PracticeHistoryPage.jsx
// STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   Page at /practice/history.
//
// BEHAVIOUR
//   Loads getPracticeHistory; table with date, category, score; each row links to its result. Empty: 'No practice attempts yet'.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getPracticeHistory } from "../api/practiceApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";

function formatDateTime(value) {
  return value ? new Date(value).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" }) : "";
}

export default function PracticeHistoryPage() {
  const [state, setState] = useState({ loading: true, error: "", items: [] });

  useEffect(() => {
    let cancelled = false;
    getPracticeHistory()
      .then((data) => !cancelled && setState({ loading: false, error: "", items: data.items }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", items: [] }));
    return () => {
      cancelled = true;
    };
  }, []);

  const { loading, error, items } = state;
  return (
    <div>
      <h1>Practice History</h1>
      {loading && <StatusMessage kind="loading" message="Loading history..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {!loading && !error && items.length === 0 && (
        <StatusMessage kind="empty" message="No practice attempts yet">
          <Link to="/practice">Start practising</Link>
        </StatusMessage>
      )}
      {items.length > 0 && (
        <table className="table card">
          <thead>
            <tr><th>Date</th><th>Category</th><th>Score</th><th><span className="sr-only">Details</span></th></tr>
          </thead>
          <tbody>
            {items.map((h) => (
              <tr key={h.session_id}>
                <td data-label="Date">{formatDateTime(h.completed_at)}</td>
                <td data-label="Category">{h.category_name}</td>
                <td data-label="Score">
                  {h.correct_count} / {h.total_questions}
                  {h.score_percent !== null ? ` (${h.score_percent}%)` : " (pending)"}
                </td>
                <td><Link to={`/practice/result/${h.session_id}`}>View result</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
