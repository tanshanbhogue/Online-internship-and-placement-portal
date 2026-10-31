// Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
// File: frontend/src/components/mocktest/MockTestCard.jsx
//
// Contract
//   <MockTestCard test={...} />   one test of the list: title, category, duration, question count and a
//   Start / Resume button that leads to the instructions page or straight back into the running attempt.
import { Link } from "react-router-dom";

export default function MockTestCard({ test }) {
  const resume = test.open_attempt_id !== null && test.open_attempt_id !== undefined;
  return (
    <article className="card mock-test-card">
      <h2>{test.title}</h2>
      {test.description && <p className="muted">{test.description}</p>}
      <div className="card-meta">
        <span>{test.category.name}</span>
        <span>{test.duration_minutes} min</span>
        <span>{test.question_count} questions</span>
      </div>
      {resume ? (
        <Link className="btn" to={`/mock-tests/attempt/${test.open_attempt_id}`}>Resume test</Link>
      ) : (
        <Link className="btn" to={`/mock-tests/test/${test.id}`}>View instructions</Link>
      )}
    </article>
  );
}
