// Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
// File: frontend/src/pages/MockTestAttemptPage.jsx
//
// Contract: route /mock-tests/attempt/:attemptId (student).
//   * Loads the attempt from the server on every visit, so a refresh keeps the SAME deadline (IT_10).
//   * The countdown comes from story #24's useAttemptExpiry (server-anchored); at zero the server closes the test
//     and this page moves to the result page /mock-tests/result/:attemptId (story #25) with state.autoSubmitted.
//   * Each choice is saved immediately (PUT .../answers). Manual submit sends a final snapshot (UT_13).
//   * No answer keys exist in the data this page receives (SEC-12).
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { getAttempt, saveAnswer, submitAttempt } from "../api/mockTestApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";
import AttemptTimer from "../components/mocktest/AttemptTimer.jsx";
import QuestionNavigator from "../components/mocktest/QuestionNavigator.jsx";
import useAttemptExpiry from "../hooks/useAttemptExpiry.js";
import "../styles/mock-test.css";

const toNumberKeys = (map) => Object.fromEntries(Object.entries(map || {}).map(([k, v]) => [Number(k), v]));

export default function MockTestAttemptPage() {
  const { attemptId } = useParams();
  const navigate = useNavigate();

  // Always start from the server's answer: navigation state survives a browser refresh and would show a stale clock.
  const [attempt, setAttempt] = useState(null);
  const [answers, setAnswers] = useState({});
  const [marked, setMarked] = useState(() => new Set());
  const [index, setIndex] = useState(0);
  const [loadError, setLoadError] = useState("");
  const [error, setError] = useState("");
  const [confirming, setConfirming] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const closed = useRef(false);

  const goToResult = useCallback(
    (autoSubmitted) => {
      if (closed.current) return;
      closed.current = true;
      navigate(`/mock-tests/result/${attemptId}`, { replace: true, state: { autoSubmitted: Boolean(autoSubmitted) } });
    },
    [attemptId, navigate]
  );

  // Fetch the attempt. `initial` also adopts the saved answers; later syncs only refresh the clock.
  const sync = useCallback(
    async (initial) => {
      try {
        const state = await getAttempt(attemptId);
        if (state.status !== "in_progress") {
          goToResult(state.status === "auto_submitted");
          return;
        }
        setAttempt((prev) => ({ ...state, questions: prev?.questions?.length ? prev.questions : state.questions }));
        if (initial) setAnswers(toNumberKeys(state.answers));
      } catch (err) {
        if (initial) setLoadError(err.status === 404 ? "This attempt was not found." : err.message || "Something went wrong");
      }
    },
    [attemptId, goToResult]
  );

  useEffect(() => {
    sync(true);
  }, [sync]);

  const { secondsLeft, phase, error: expiryError, retry } = useAttemptExpiry({
    attemptId,
    remainingSeconds: attempt?.remaining_seconds,
    syncKey: attempt?.server_time,
    enabled: Boolean(attempt) && !submitting,
    onAutoSubmitted: () => goToResult(true),
    onResync: () => sync(false),
  });

  // Warn before leaving mid-test: the server clock keeps running.
  useEffect(() => {
    if (!attempt) return undefined;
    const handler = (e) => {
      if (closed.current) return;
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [attempt]);

  const locked = phase !== "running" || submitting;
  const total = attempt?.questions?.length || 0;
  const answeredCount = useMemo(() => Object.keys(answers).length, [answers]);

  async function choose(question, optionId) {
    const previous = answers[question.id];
    setError("");
    setAnswers((a) => ({ ...a, [question.id]: optionId }));
    try {
      await saveAnswer(attemptId, { questionId: question.id, selectedOptionId: optionId });
    } catch (err) {
      if (err.code === "time_expired" || err.code === "already_submitted") {
        await sync(false); // the server closed the test: this moves us to the result page
        return;
      }
      setAnswers((a) => {
        const next = { ...a };
        if (previous === undefined) delete next[question.id];
        else next[question.id] = previous;
        return next;
      });
      setError(err.message || "Your answer could not be saved. Please try again.");
    }
  }

  async function clearAnswer(question) {
    const previous = answers[question.id];
    setAnswers((a) => {
      const next = { ...a };
      delete next[question.id];
      return next;
    });
    try {
      await saveAnswer(attemptId, { questionId: question.id, selectedOptionId: null });
    } catch (err) {
      if (err.code === "time_expired" || err.code === "already_submitted") await sync(false);
      else if (previous !== undefined) setAnswers((a) => ({ ...a, [question.id]: previous }));
    }
  }

  function toggleMark(question) {
    setMarked((set) => {
      const next = new Set(set);
      if (next.has(question.id)) next.delete(question.id);
      else next.add(question.id);
      return next;
    });
  }

  async function submit() {
    setSubmitting(true);
    setError("");
    try {
      const snapshot = Object.entries(answers).map(([qid, oid]) => ({ questionId: Number(qid), selectedOptionId: oid }));
      const result = await submitAttempt(attemptId, snapshot);
      goToResult(result.auto_submitted);
    } catch (err) {
      setSubmitting(false);
      setConfirming(false);
      setError(err.message || "Something went wrong");
    }
  }

  if (loadError) {
    return (
      <div className="page-medium">
        <StatusMessage kind="error" message={loadError} />
      </div>
    );
  }
  if (!attempt) return <StatusMessage kind="loading" message="Loading your test..." />;

  const question = attempt.questions[index];
  if (!question) return <StatusMessage kind="loading" message="Loading your test..." />;
  const isMarked = marked.has(question.id);

  return (
    <div className="attempt-page">
      <header className="attempt-header">
        <div>
          <h1 className="attempt-title">{attempt.test.title}</h1>
          <p className="muted small">{attempt.test.category.name} - {answeredCount} of {total} answered</p>
        </div>
        <AttemptTimer secondsLeft={secondsLeft} />
      </header>

      {phase === "finalizing" && (
        <StatusMessage kind="loading" message="Time is up. Submitting your test..." />
      )}
      {phase === "error" && (
        <StatusMessage kind="error" message={expiryError || "Could not submit automatically."}>
          <button type="button" className="btn-link" onClick={retry}>Try again</button>
        </StatusMessage>
      )}
      {error && <StatusMessage kind="error" message={error} />}

      <div className="attempt-layout">
        <section className="card attempt-question" aria-labelledby="q-heading">
          <p className="muted small" id="q-heading">Question {index + 1} of {total}</p>
          <fieldset disabled={locked} className="attempt-fieldset">
            <legend className="attempt-prompt">{question.prompt}</legend>
            {question.options.map((o) => (
              <label key={o.id} className="option">
                <input
                  type="radio"
                  name={`q-${question.id}`}
                  value={o.id}
                  checked={answers[question.id] === o.id}
                  onChange={() => choose(question, o.id)}
                />
                <span>{o.text}</span>
              </label>
            ))}
          </fieldset>
          <div className="row" style={{ marginTop: "0.5rem" }}>
            <button type="button" className="btn btn-secondary btn-small" onClick={() => toggleMark(question)} aria-pressed={isMarked} disabled={locked}>
              {isMarked ? "Unmark review" : "Mark for review"}
            </button>
            <button type="button" className="btn btn-secondary btn-small" onClick={() => clearAnswer(question)} disabled={locked || answers[question.id] === undefined}>
              Clear answer
            </button>
          </div>
          <div className="row spread" style={{ marginTop: "1rem" }}>
            <button type="button" className="btn btn-secondary" onClick={() => setIndex((i) => Math.max(0, i - 1))} disabled={index === 0 || locked}>Previous</button>
            <button type="button" className="btn btn-secondary" onClick={() => setIndex((i) => Math.min(total - 1, i + 1))} disabled={index === total - 1 || locked}>Next</button>
          </div>
        </section>

        <aside className="card attempt-side">
          <h2>Questions</h2>
          <QuestionNavigator questions={attempt.questions} answers={answers} marked={marked} current={index} onSelect={setIndex} disabled={locked} />
          <p className="hint">Blue: answered. Yellow outline: marked for review.</p>
          {!confirming ? (
            <button type="button" className="btn" onClick={() => setConfirming(true)} disabled={locked}>Submit test</button>
          ) : (
            <div role="alertdialog" aria-label="Confirm submission" className="attempt-confirm">
              <p>
                {total - answeredCount > 0
                  ? `${total - answeredCount} question${total - answeredCount === 1 ? " is" : "s are"} still unanswered. Submit anyway?`
                  : "Submit your test now?"}
              </p>
              <div className="row">
                <button type="button" className="btn" onClick={submit} disabled={submitting}>{submitting ? "Submitting..." : "Yes, submit"}</button>
                <button type="button" className="btn btn-secondary" onClick={() => setConfirming(false)} disabled={submitting}>Keep working</button>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
