// ==============================================================================
// FILE   : frontend/src/pages/PracticeResultPage.jsx
// STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   Page at /practice/result/:sessionId.
//
// BEHAVIOUR
//   Loads getSessionResult. Shows score (correct / total, percent), category, answered count and a per-question breakdown with explanations. Buttons: Practice again (/practice), View history. 409 'not finished' -> redirect to the session.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getSessionResult } from "../api/practiceApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";

function verdict(item) {
  if (item.is_correct === null) return { text: "Pending evaluation", cls: "badge-shortlisted" };
  if (item.is_correct) return { text: "Correct", cls: "badge-selected" };
  if (item.selected_option_id === null) return { text: "Not answered", cls: "badge-neutral" };
  return { text: "Incorrect", cls: "badge-rejected" };
}

export default function PracticeResultPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [state, setState] = useState({ loading: true, error: "", result: null });

  useEffect(() => {
    let cancelled = false;
    getSessionResult(sessionId)
      .then((result) => !cancelled && setState({ loading: false, error: "", result }))
      .catch((err) => {
        if (cancelled) return;
        if (err.status === 409) navigate(`/practice/session/${sessionId}`, { replace: true }); // not finished yet
        else setState({ loading: false, error: err.status === 404 ? "Result not found." : err.message || "Something went wrong", result: null });
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId, navigate]);

  const { loading, error, result } = state;
  return (
    <div className="page-medium">
      {loading && <StatusMessage kind="loading" message="Loading your result..." />}
      {error && <StatusMessage kind="error" message={error} />}
      {result && (
        <>
          <div className="card">
            <h1>Your result: {result.category.name}</h1>
            <p className="score">
              {result.correct_count} / {result.total_questions}
              {result.score_percent !== null && <span className="muted"> ({result.score_percent}%)</span>}
            </p>
            {result.score_percent === null && <p className="muted">Not scored yet: coding answers are awaiting evaluation.</p>}
            <p className="muted">Answered {result.answered_count} of {result.total_questions} questions.</p>
            <div className="row">
              <Link className="btn" to="/practice">Practice again</Link>
              <Link className="btn btn-secondary" to="/practice/history">View history</Link>
            </div>
          </div>

          <h2 style={{ marginTop: "1.5rem" }}>Question breakdown</h2>
          <ol className="breakdown card">
            {result.breakdown.map((item) => {
              const v = verdict(item);
              return (
                <li key={item.question_id}>
                  <p style={{ whiteSpace: "pre-wrap" }}>{item.prompt}</p>
                  <span className={`badge ${v.cls}`}>{v.text}</span>
                  {item.explanation && <p className="small muted" style={{ marginTop: "0.4rem" }}>{item.explanation}</p>}
                </li>
              );
            })}
          </ol>
        </>
      )}
    </div>
  );
}
