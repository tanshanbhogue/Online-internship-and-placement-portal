// Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
// File: frontend/src/components/mocktest/QuestionNavigator.jsx
//
// Contract
//   <QuestionNavigator questions answers marked current onSelect(index) disabled />
//   A numbered grid to jump between questions (UC-5 step 5). Each button says, in words and colour,
//   whether the question is answered, marked for review or still empty.
export default function QuestionNavigator({ questions, answers, marked, current, onSelect, disabled }) {
  return (
    <nav aria-label="Questions" className="question-nav">
      {questions.map((q, i) => {
        const answered = answers[q.id] !== undefined;
        const isMarked = marked.has(q.id);
        const state = isMarked ? "marked for review" : answered ? "answered" : "not answered";
        return (
          <button
            key={q.id}
            type="button"
            className={`qnav-btn${answered ? " qnav-answered" : ""}${isMarked ? " qnav-marked" : ""}${i === current ? " qnav-current" : ""}`}
            aria-current={i === current ? "true" : undefined}
            aria-label={`Question ${i + 1}, ${state}`}
            onClick={() => onSelect(i)}
            disabled={disabled}
          >
            {i + 1}
          </button>
        );
      })}
    </nav>
  );
}
