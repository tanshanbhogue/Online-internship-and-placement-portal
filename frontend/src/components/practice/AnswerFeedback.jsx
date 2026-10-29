export default function AnswerFeedback({ feedback, question }) {
  if (!feedback) return null;
  if (feedback.evaluation_status === "pending" || feedback.is_correct === null) {
    return (
      <div className="feedback feedback-pending" role="status">
        <strong>Saved.</strong> Your code was saved; evaluation is pending.
      </div>
    );
  }
  const correctOption = question?.options?.find((o) => o.id === feedback.correct_option_id);
  return (
    <div className={`feedback ${feedback.is_correct ? "feedback-correct" : "feedback-incorrect"}`} role="status">
      <strong>{feedback.is_correct ? "✔ Correct" : "✘ Incorrect"}</strong>
      {!feedback.is_correct && correctOption && <p>Correct answer: {correctOption.text}</p>}
      {feedback.explanation && <p>{feedback.explanation}</p>}
    </div>
  );
}
