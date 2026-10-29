// ==============================================================================
// FILE   : frontend/src/pages/PracticeSessionPage.jsx
// STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   Page at /practice/session/:sessionId (also handles /practice/session/new).
//
// BEHAVIOUR
//   When sessionId == 'new' read ?category and ?count, call startSession, then replace the URL with the real session id (keep the response in state).
//   If the server says no_questions show 'No questions found' with a link back to /practice (IT_07).
//   Shows one question at a time with progress (n of total), submits each answer immediately, shows AnswerFeedback, then Next. 'Finish' and 'Exit' both call finishSession (partial progress is kept, A2) and go to the result.
//   Refresh keeps working only for the starting call; do not re-create sessions on every render (guard against React StrictMode double effects).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom";

import { finishSession, getSessionResult, startSession, submitAnswer } from "../api/practiceApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";
import QuestionCard from "../components/practice/QuestionCard.jsx";

export default function PracticeSessionPage() {
  const { sessionId } = useParams();
  const [params] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();

  // location.state survives a browser refresh, so the questions can be shown again after one.
  const [session, setSession] = useState(location.state?.session || null);
  const [error, setError] = useState({ message: "", code: "" });
  const [index, setIndex] = useState(0);
  const [feedbacks, setFeedbacks] = useState({}); // question id -> feedback
  const [busy, setBusy] = useState(false);
  const started = useRef(false); // StrictMode runs effects twice in dev: never create two sessions

  useEffect(() => {
    if (session) return;
    if (sessionId === "new") {
      if (started.current) return;
      started.current = true;
      startSession({ categoryId: params.get("category"), count: params.get("count") })
        .then((data) => {
          setSession(data);
          navigate(`/practice/session/${data.session_id}`, { replace: true, state: { session: data } });
        })
        .catch((err) => setError({ message: err.message || "Something went wrong", code: err.code }));
      return;
    }
    // A real id but nothing in memory: a finished session goes to its result, an open one cannot be resumed.
    getSessionResult(sessionId)
      .then(() => navigate(`/practice/result/${sessionId}`, { replace: true }))
      .catch(() => setError({ message: "This practice session can no longer be resumed.", code: "not_resumable" }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSubmit(answer) {
    const question = session.questions[index];
    setBusy(true);
    setError({ message: "", code: "" });
    try {
      const feedback = await submitAnswer(session.session_id, { questionId: question.id, ...answer });
      setFeedbacks((f) => ({ ...f, [question.id]: feedback })); // server saved it already (progress is kept)
    } catch (err) {
      setError({ message: err.message || "Something went wrong", code: err.code });
    } finally {
      setBusy(false);
    }
  }

  async function finish() {
    setBusy(true);
    try {
      await finishSession(session.session_id); // partial progress is kept; unanswered count as wrong
      navigate(`/practice/result/${session.session_id}`);
    } catch (err) {
      setError({ message: err.message || "Something went wrong", code: err.code });
      setBusy(false);
    }
  }

  if (error.code === "no_questions") {
    return (
      <div className="page-medium">
        <StatusMessage kind="empty" message="No questions found">
          <Link to="/practice">Back to practice</Link>
        </StatusMessage>
      </div>
    );
  }
  if (!session) {
    return error.message ? (
      <div className="page-medium">
        <StatusMessage kind="error" message={error.message} />
        <Link to="/practice">Back to practice</Link>
      </div>
    ) : (
      <StatusMessage kind="loading" message="Preparing your questions..." />
    );
  }

  const total = session.questions.length;
  const question = session.questions[index];
  const feedback = feedbacks[question.id];
  const isLast = index === total - 1;

  return (
    <div className="page-medium">
      <div className="row spread">
        <h1>{session.category.name}</h1>
        <button type="button" className="btn btn-secondary btn-small" onClick={finish} disabled={busy}>Exit</button>
      </div>
      <p aria-live="polite">Question {index + 1} of {total}</p>
      <div className="progress" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={index + (feedback ? 1 : 0)}>
        <div style={{ width: `${((index + (feedback ? 1 : 0)) / total) * 100}%` }} />
      </div>

      {error.message && <StatusMessage kind="error" message={error.message} />}
      {/* key resets the card (selection, code) for every question */}
      <QuestionCard key={question.id} question={question} onSubmit={handleSubmit} disabled={busy} feedback={feedback} />

      {feedback && (
        <div className="row" style={{ marginTop: "1rem" }}>
          {isLast ? (
            <button type="button" className="btn" onClick={finish} disabled={busy}>Finish</button>
          ) : (
            <button type="button" className="btn" onClick={() => setIndex((i) => i + 1)}>Next question</button>
          )}
        </div>
      )}
    </div>
  );
}
