import "../../styles/mock-result.css";

const VERDICT = {
  correct: { text: "Correct", cls: "badge-selected" },
  incorrect: { text: "Incorrect", cls: "badge-rejected" },
  skipped: { text: "Not answered", cls: "badge-neutral" },
};

export default function BreakdownList({ items }) {
  return (
    <ol className="breakdown" aria-label="Answer analysis">
      {items.map((item) => {
        const verdict = VERDICT[item.outcome];
        return (
          <li key={item.question_id} data-testid={`breakdown-${item.position}`} data-outcome={item.outcome}>
            <div className="row spread">
              <strong>Question {item.position}</strong>
              <span className={`badge ${verdict.cls}`}>{verdict.text}</span>
            </div>
            <p className="breakdown-prompt">{item.prompt}</p>
            <ul className="breakdown-options">
              {item.options.map((o) => {
                const isCorrect = o.id === item.correct_option_id;
                const isChosen = o.id === item.selected_option_id;
                return (
                  <li key={o.id} className={`${isCorrect ? "opt-correct" : ""}${isChosen && !isCorrect ? " opt-wrong" : ""}`}>
                    {o.text}
                    {isCorrect && <span className="opt-tag"> (correct answer)</span>}
                    {isChosen && <span className="opt-tag"> (your answer)</span>}
                  </li>
                );
              })}
            </ul>
            {item.explanation && <p className="small"><strong>Explanation:</strong> {item.explanation}</p>}
          </li>
        );
      })}
    </ol>
  );
}
