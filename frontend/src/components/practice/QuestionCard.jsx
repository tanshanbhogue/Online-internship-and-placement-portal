// ==============================================================================
// FILE   : frontend/src/components/practice/QuestionCard.jsx
// STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
// ==============================================================================
//
// PURPOSE
//   Renders one question and collects the answer.
//
// BEHAVIOUR
//   props { question, onSubmit(answer), disabled, feedback }. MCQ: radio options (plain text), coding: textarea editor prefilled with starter_code. 'Submit answer' button.
//   When feedback exists the card locks and shows AnswerFeedback.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useState } from "react";

import AnswerFeedback from "./AnswerFeedback.jsx";

// Everything from the server is rendered as plain text (SEC-10).
export default function QuestionCard({ question, onSubmit, disabled, feedback }) {
  const [selected, setSelected] = useState(null);
  const [code, setCode] = useState(question.starter_code || "");
  const locked = disabled || !!feedback;
  const isMcq = question.type === "mcq";
  const canSubmit = !locked && (isMcq ? selected !== null : code.trim().length > 0);

  function submit(event) {
    event.preventDefault();
    if (!canSubmit) return;
    onSubmit(isMcq ? { selectedOptionId: selected } : { code });
  }

  return (
    <form className="card" onSubmit={submit}>
      <p className="muted small">{question.difficulty}</p>
      <h2 style={{ whiteSpace: "pre-wrap" }}>{question.prompt}</h2>

      {isMcq ? (
        <fieldset style={{ border: "none", padding: 0 }} disabled={locked}>
          <legend className="sr-only">Choose one answer</legend>
          {question.options.map((o) => (
            <label key={o.id} className="option">
              <input type="radio" name={`q-${question.id}`} value={o.id} checked={selected === o.id} onChange={() => setSelected(o.id)} />
              <span>{o.text}</span>
            </label>
          ))}
        </fieldset>
      ) : (
        <div className="field">
          <label htmlFor={`code-${question.id}`}>Your code</label>
          <textarea id={`code-${question.id}`} className="code" rows={10} spellCheck={false} value={code}
            onChange={(e) => setCode(e.target.value)} disabled={locked} />
        </div>
      )}

      {!feedback && <button className="btn" type="submit" disabled={!canSubmit}>Submit answer</button>}
      <AnswerFeedback feedback={feedback} question={question} />
    </form>
  );
}
