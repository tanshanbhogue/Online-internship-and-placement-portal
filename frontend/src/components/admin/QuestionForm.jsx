// ==============================================================================
// FILE   : frontend/src/components/admin/QuestionForm.jsx
// STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
// ==============================================================================
//
// PURPOSE
//   Create/edit form for a question (admin).
//
// BEHAVIOUR
//   Fields: category, type (mcq/coding), prompt, difficulty, explanation; for mcq a dynamic list of 2..6 options with one 'correct' radio; for coding starter code + test cases (JSON textarea).
//   Client validation mirrors the server rules (exactly one correct option, required fields) and highlights errors (use case A1). Server 422 fields map to inputs.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useState } from "react";

const blankOption = () => ({ text: "" });

function initialState(initial, categories, defaultCategoryId) {
  if (!initial) {
    return {
      categoryId: defaultCategoryId ?? categories[0]?.id ?? "",
      type: "mcq", prompt: "", difficulty: "easy", explanation: "",
      options: [blankOption(), blankOption()], correctIndex: null, starterCode: "", testCases: "",
    };
  }
  return {
    categoryId: initial.category_id, type: initial.type, prompt: initial.prompt, difficulty: initial.difficulty,
    explanation: initial.explanation || "",
    options: initial.options.length ? initial.options.map((o) => ({ text: o.text })) : [blankOption(), blankOption()],
    correctIndex: initial.options.findIndex((o) => o.is_correct) >= 0 ? initial.options.findIndex((o) => o.is_correct) : null,
    starterCode: initial.starter_code || "", testCases: initial.test_cases || "",
  };
}

function Err({ message }) {
  return message ? <p className="field-error" role="alert">{message}</p> : null;
}

/** onSubmit(payload) must return a promise; an ApiError's `fields` are mapped back onto the inputs. */
export default function QuestionForm({ categories, initial, defaultCategoryId, onSubmit, onCancel }) {
  const [s, setS] = useState(() => initialState(initial, categories, defaultCategoryId));
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const set = (name) => (e) => setS((v) => ({ ...v, [name]: e.target.value }));

  function setOptionText(i, text) {
    setS((v) => ({ ...v, options: v.options.map((o, idx) => (idx === i ? { text } : o)) }));
  }
  function addOption() {
    setS((v) => (v.options.length < 6 ? { ...v, options: [...v.options, blankOption()] } : v));
  }
  function removeOption(i) {
    setS((v) => {
      if (v.options.length <= 2) return v;
      const correct = v.correctIndex === i ? null : v.correctIndex !== null && v.correctIndex > i ? v.correctIndex - 1 : v.correctIndex;
      return { ...v, options: v.options.filter((_, idx) => idx !== i), correctIndex: correct };
    });
  }

  function validate() {
    const found = {};
    if (!s.categoryId) found.category_id = "Choose a category";
    if (!s.prompt.trim()) found.prompt = "This field is required";
    if (s.type === "mcq") {
      if (s.options.some((o) => !o.text.trim())) found.options = "Every option needs text";
      else if (s.correctIndex === null) found.options = "Mark exactly one option as correct";
    } else if (s.testCases.trim()) {
      try { JSON.parse(s.testCases); } catch { found.test_cases = "Test cases must be valid JSON"; }
    }
    return found;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError("");
    const found = validate();
    setErrors(found);
    if (Object.keys(found).length) return;

    const payload = {
      category_id: Number(s.categoryId), type: s.type, prompt: s.prompt.trim(), difficulty: s.difficulty,
      explanation: s.explanation.trim() || null,
    };
    if (s.type === "mcq") {
      payload.options = s.options.map((o, i) => ({ text: o.text.trim(), is_correct: i === s.correctIndex }));
    } else {
      payload.options = [];
      payload.starter_code = s.starterCode || null;
      payload.test_cases = s.testCases.trim() || null;
    }

    setSubmitting(true);
    try {
      await onSubmit(payload);
    } catch (err) {
      if (err.status === 422 && err.fields && Object.keys(err.fields).length) {
        const mapped = {};
        for (const [field, messages] of Object.entries(err.fields)) mapped[field] = messages[0];
        setErrors(mapped);
      } else {
        setFormError(err.message || "Something went wrong");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit} noValidate aria-label={initial ? "Edit question" : "New question"}>
      <h2>{initial ? "Edit question" : "Add question"}</h2>
      {formError && <Err message={formError} />}

      <div className="field">
        <label htmlFor="qf-category">Category</label>
        <select id="qf-category" value={s.categoryId} onChange={set("categoryId")} aria-invalid={!!errors.category_id}>
          {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <Err message={errors.category_id} />
      </div>

      <div className="row">
        <div className="field" style={{ flex: 1 }}>
          <label htmlFor="qf-type">Type</label>
          <select id="qf-type" value={s.type} onChange={set("type")} aria-invalid={!!errors.type}>
            <option value="mcq">Multiple choice</option>
            <option value="coding">Coding</option>
          </select>
          <Err message={errors.type} />
        </div>
        <div className="field" style={{ flex: 1 }}>
          <label htmlFor="qf-difficulty">Difficulty</label>
          <select id="qf-difficulty" value={s.difficulty} onChange={set("difficulty")} aria-invalid={!!errors.difficulty}>
            <option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
          </select>
          <Err message={errors.difficulty} />
        </div>
      </div>

      <div className="field">
        <label htmlFor="qf-prompt">Question</label>
        <textarea id="qf-prompt" value={s.prompt} onChange={set("prompt")} maxLength={5000} aria-invalid={!!errors.prompt} />
        <Err message={errors.prompt} />
      </div>

      {s.type === "mcq" ? (
        <fieldset aria-invalid={!!errors.options}>
          <legend>Options (2 to 6, select the correct one)</legend>
          {s.options.map((o, i) => (
            <div key={i} className="row" style={{ marginBottom: "0.5rem", flexWrap: "nowrap" }}>
              <input type="radio" name="qf-correct" checked={s.correctIndex === i} onChange={() => setS((v) => ({ ...v, correctIndex: i }))}
                aria-label={`Option ${i + 1} is correct`} />
              <input type="text" value={o.text} maxLength={500} onChange={(e) => setOptionText(i, e.target.value)} aria-label={`Option ${i + 1} text`} />
              <button type="button" className="btn btn-secondary btn-small" onClick={() => removeOption(i)} disabled={s.options.length <= 2}
                aria-label={`Remove option ${i + 1}`}>×</button>
            </div>
          ))}
          <button type="button" className="btn btn-secondary btn-small" onClick={addOption} disabled={s.options.length >= 6}>Add option</button>
          <Err message={errors.options} />
        </fieldset>
      ) : (
        <>
          <div className="field">
            <label htmlFor="qf-starter">Starter code</label>
            <textarea id="qf-starter" className="code" value={s.starterCode} onChange={set("starterCode")} />
            <Err message={errors.starter_code} />
          </div>
          <div className="field">
            <label htmlFor="qf-tests">Test cases (JSON)</label>
            <textarea id="qf-tests" className="code" value={s.testCases} onChange={set("testCases")} aria-invalid={!!errors.test_cases} />
            <span className="hint">Never shown to students.</span>
            <Err message={errors.test_cases} />
          </div>
        </>
      )}

      <div className="field">
        <label htmlFor="qf-explanation">Explanation (shown after the student answers)</label>
        <textarea id="qf-explanation" value={s.explanation} onChange={set("explanation")} />
        <Err message={errors.explanation} />
      </div>

      <div className="row">
        <button className="btn" type="submit" disabled={submitting}>{submitting ? "Saving..." : "Save question"}</button>
        <button className="btn btn-secondary" type="button" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}
