import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { listCategories } from "../api/questionBankApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";
import CategorySelector from "../components/practice/CategorySelector.jsx";

export default function PracticeHomePage() {
  const navigate = useNavigate();
  const [state, setState] = useState({ loading: true, error: "", categories: [] });
  const [selectedId, setSelectedId] = useState(null);
  const [count, setCount] = useState(10);

  useEffect(() => {
    let cancelled = false;
    listCategories()
      .then((categories) => !cancelled && setState({ loading: false, error: "", categories }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", categories: [] }));
    return () => {
      cancelled = true;
    };
  }, []);

  function start() {
    // A URL, not an import: PracticeSessionPage (story #22) creates the session.
    const safeCount = Math.min(50, Math.max(1, Number(count) || 10));
    navigate(`/practice/session/new?category=${selectedId}&count=${safeCount}`);
  }

  const { loading, error, categories } = state;
  return (
    <div className="page-medium">
      <h1>Practice</h1>
      <p className="muted">Choose a category and test yourself. You get instant feedback on every answer.</p>
      {loading && <StatusMessage kind="loading" message="Loading categories..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {!loading && !error && categories.length === 0 && <StatusMessage kind="empty" message="No categories available yet." />}
      {categories.length > 0 && (
        <>
          <CategorySelector categories={categories} selectedId={selectedId} onSelect={setSelectedId} />
          <div className="field" style={{ maxWidth: "14rem" }}>
            <label htmlFor="practice-count">Number of questions</label>
            <input id="practice-count" type="number" min="1" max="50" value={count} onChange={(e) => setCount(e.target.value)} />
          </div>
          <div className="row">
            <button type="button" className="btn" disabled={selectedId === null} onClick={start}>Start practice</button>
            <Link to="/practice/history">View practice history</Link>
          </div>
        </>
      )}
    </div>
  );
}
