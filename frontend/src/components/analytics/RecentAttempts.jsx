// Contract: <RecentAttempts filters refreshKey />   newest attempts with a link to the full result.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getAnalyticsAttempts } from "../../api/analyticsApi.js";
import StatusMessage from "../common/StatusMessage.jsx";

const when = (v) => new Date(v).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
const detailPath = (row) => (row.kind === "mock" ? `/mock-tests/result/${row.id}` : `/practice/result/${row.id}`);

export default function RecentAttempts({ filters, refreshKey }) {
  const [state, setState] = useState({ loading: true, error: "", data: null });

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true }));
    getAnalyticsAttempts(filters, 10)
      .then((data) => !cancelled && setState({ loading: false, error: "", data }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", data: null }));
    return () => {
      cancelled = true;
    };
  }, [filters, refreshKey]);

  const { loading, error, data } = state;
  return (
    <section aria-labelledby="recent-heading">
      <h2 id="recent-heading">Recent attempts</h2>
      {loading && !data && <StatusMessage kind="loading" message="Loading attempts..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {data && (
        <table className="table card">
          <thead><tr><th>Date</th><th>Attempt</th><th>Category</th><th>Score</th><th><span className="sr-only">Details</span></th></tr></thead>
          <tbody>
            {data.items.map((row) => (
              <tr key={`${row.kind}-${row.id}`}>
                <td data-label="Date">{when(row.completed_at)}</td>
                <td data-label="Attempt">{row.title}</td>
                <td data-label="Category">{row.category}</td>
                <td data-label="Score">{row.score_percent}%</td>
                <td><Link to={detailPath(row)}>View details</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
