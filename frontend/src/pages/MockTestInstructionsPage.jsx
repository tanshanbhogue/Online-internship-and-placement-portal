// Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
// File: frontend/src/pages/MockTestInstructionsPage.jsx
//
// Contract: route /mock-tests/test/:testId (student). Shows the instructions and the time limit (UC-5 step 3);
// "Start test" calls POST /mock-tests/{id}/attempts and opens the attempt page. The clock starts on the SERVER
// at that moment, not when this page opened.
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { listMockTests, startAttempt } from "../api/mockTestApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";
import "../styles/mock-test.css";

export default function MockTestInstructionsPage() {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [state, setState] = useState({ loading: true, error: "", test: null });
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState("");
  const started = useRef(false); // double clicks must not start twice

  useEffect(() => {
    let cancelled = false;
    listMockTests()
      .then((data) => {
        if (cancelled) return;
        const test = data.items.find((t) => String(t.id) === String(testId));
        setState({ loading: false, error: test ? "" : "This mock test is not available.", test: test || null });
      })
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", test: null }));
    return () => {
      cancelled = true;
    };
  }, [testId]);

  async function start() {
    if (started.current) return;
    started.current = true;
    setStarting(true);
    setStartError("");
    try {
      const attempt = await startAttempt(testId);
      navigate(`/mock-tests/attempt/${attempt.attempt_id}`);
    } catch (err) {
      started.current = false;
      setStarting(false);
      setStartError(err.code === "no_questions" ? "No questions found" : err.message || "Something went wrong");
    }
  }

  const { loading, error, test } = state;
  return (
    <div className="page-medium">
      {loading && <StatusMessage kind="loading" message="Loading..." />}
      {error && (
        <>
          <StatusMessage kind="error" message={error} />
          <Link to="/mock-tests">Back to mock tests</Link>
        </>
      )}
      {test && (
        <div className="card">
          <h1>{test.title}</h1>
          <div className="card-meta">
            <span>{test.category.name}</span>
            <span><strong>{test.duration_minutes} minutes</strong></span>
            <span>{test.question_count} questions</span>
          </div>
          <h2>Before you start</h2>
          <ul>
            <li>The timer starts the moment you press <strong>Start test</strong> and runs on our server.</li>
            <li>Refreshing the page or losing your connection does not reset it: you can resume with the time that is left.</li>
            <li>You can move between questions, change answers and mark questions for review.</li>
            <li>When time is up the test is submitted automatically with the answers you have saved.</li>
            <li>Correct answers are shown only after you submit.</li>
          </ul>
          {startError && <StatusMessage kind="error" message={startError} />}
          <div className="row">
            <button type="button" className="btn" onClick={start} disabled={starting}>
              {starting ? "Starting..." : test.open_attempt_id ? "Resume test" : "Start test"}
            </button>
            <Link to="/mock-tests">Back</Link>
          </div>
        </div>
      )}
    </div>
  );
}
