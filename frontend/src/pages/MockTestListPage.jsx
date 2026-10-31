// Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
// File: frontend/src/pages/MockTestListPage.jsx
//
// Contract: route /mock-tests (student). Lists the active mock tests (UC-5 steps 1-2); a test already running
// shows "Resume test". The "history" link is provided by story #25.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listMockTests } from "../api/mockTestApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";
import MockTestCard from "../components/mocktest/MockTestCard.jsx";
import "../styles/mock-test.css";

export default function MockTestListPage() {
  const [state, setState] = useState({ loading: true, error: "", items: [] });

  useEffect(() => {
    let cancelled = false;
    listMockTests()
      .then((data) => !cancelled && setState({ loading: false, error: "", items: data.items }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", items: [] }));
    return () => {
      cancelled = true;
    };
  }, []);

  const { loading, error, items } = state;
  return (
    <div>
      <div className="row spread">
        <h1>Mock Tests</h1>
        <Link to="/mock-tests/history">Test history</Link>
      </div>
      <p className="muted">Timed tests that behave like the real thing: the clock runs on our server and the test is submitted for you when time is up.</p>
      {loading && <StatusMessage kind="loading" message="Loading tests..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {!loading && !error && items.length === 0 && <StatusMessage kind="empty" message="No mock tests are available yet" />}
      {items.length > 0 && (
        <div className="grid">
          {items.map((t) => <MockTestCard key={t.id} test={t} />)}
        </div>
      )}
    </div>
  );
}
