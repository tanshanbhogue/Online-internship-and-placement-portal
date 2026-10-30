import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getMockResult } from "../api/mockResultApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";
import AutoSubmitNotice from "../components/mocktest/AutoSubmitNotice.jsx";
import BreakdownList from "../components/mocktest/BreakdownList.jsx";
import ResultSummaryCard from "../components/mocktest/ResultSummaryCard.jsx";
import "../styles/mock-result.css";

export default function MockTestResultPage() {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const [filters, setFilters] = useState({ difficulty: "", outcome: "" });
  const [state, setState] = useState({ loading: true, error: "", result: null });

  useEffect(() => {
    let cancelled = false;
    getMockResult(attemptId, filters)
      .then((result) => !cancelled && setState({ loading: false, error: "", result }))
      .catch((err) => {
        if (cancelled) return;
        if (err.code === "attempt_in_progress") navigate(`/mock-tests/attempt/${attemptId}`, { replace: true });
        else setState({ loading: false, error: err.status === 404 ? "Result not found." : err.message || "Something went wrong", result: null });
      });
    return () => {
      cancelled = true;
    };
  }, [attemptId, filters, navigate]);

  const { loading, error, result } = state;
  const set = (key) => (e) => setFilters((f) => ({ ...f, [key]: e.target.value }));

  return (
    <div className="page-medium">
      {loading && !result && <StatusMessage kind="loading" message="Loading your result..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {result && (
        <>
          <AutoSubmitNotice status={result.status} />
          <ResultSummaryCard result={result} />

          <h2 style={{ marginTop: "1.25rem" }}>Detailed analysis</h2>
          <div className="filters result-filters">
            <div className="field">
              <label htmlFor="f-outcome">Show</label>
              <select id="f-outcome" value={filters.outcome} onChange={set("outcome")}>
                <option value="">All questions</option>
                <option value="correct">Correct</option>
                <option value="incorrect">Incorrect</option>
                <option value="skipped">Not answered</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="f-difficulty">Difficulty</label>
              <select id="f-difficulty" value={filters.difficulty} onChange={set("difficulty")}>
                <option value="">Any</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          </div>
          {result.breakdown.length === 0 ? (
            <StatusMessage kind="empty" message="No questions match these filters" />
          ) : (
            <div className="card"><BreakdownList items={result.breakdown} /></div>
          )}
          <div className="row" style={{ marginTop: "1rem" }}>
            <Link className="btn btn-secondary" to="/mock-tests/history">Test history</Link>
            <Link className="btn btn-secondary" to="/mock-tests">Take another test</Link>
            <Link className="btn btn-secondary" to="/analytics">My analytics</Link>
          </div>
        </>
      )}
    </div>
  );
}
