import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getMockHistory } from "../api/mockResultApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";
import { formatDuration } from "../components/mocktest/ResultSummaryCard.jsx";

const when = (v) => (v ? new Date(v).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" }) : "");

export default function MockTestHistoryPage() {
  const [state, setState] = useState({ loading: true, error: "", items: [] });

  useEffect(() => {
    let cancelled = false;
    getMockHistory()
      .then((data) => !cancelled && setState({ loading: false, error: "", items: data.items }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", items: [] }));
    return () => {
      cancelled = true;
    };
  }, []);

  const { loading, error, items } = state;
  return (
    <div>
      <h1>Mock Test History</h1>
      {loading && <StatusMessage kind="loading" message="Loading history..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {!loading && !error && items.length === 0 && (
        <StatusMessage kind="empty" message="No mock tests taken yet"><Link to="/mock-tests">Take a mock test</Link></StatusMessage>
      )}
      {items.length > 0 && (
        <table className="table card">
          <thead>
            <tr><th>Date</th><th>Test</th><th>Score</th><th>Time</th><th>Submitted</th><th><span className="sr-only">Details</span></th></tr>
          </thead>
          <tbody>
            {items.map((h) => (
              <tr key={h.attempt_id}>
                <td data-label="Date">{when(h.submitted_at)}</td>
                <td data-label="Test">{h.test_title}</td>
                <td data-label="Score">{h.correct_count} / {h.total_questions}{h.score_percent !== null ? ` (${h.score_percent}%)` : ""}</td>
                <td data-label="Time">{formatDuration(h.time_taken_seconds)}</td>
                <td data-label="Submitted">{h.status === "auto_submitted" ? "Automatically" : "By you"}</td>
                <td><Link to={`/mock-tests/result/${h.attempt_id}`}>View analysis</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
