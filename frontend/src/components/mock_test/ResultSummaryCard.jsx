import "../../styles/mock-result.css";

export function formatDuration(totalSeconds) {
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  return `${m}m ${String(s).padStart(2, "0")}s`;
}

export default function ResultSummaryCard({ result }) {
  return (
    <section className="card result-summary" aria-labelledby="result-title">
      <h1 id="result-title">{result.test.title}</h1>
      <p className="muted">{result.category_name}</p>
      <p className="score" data-testid="score">
        {result.score_percent === null ? "-" : `${result.score_percent}%`}
      </p>
      <dl className="result-stats">
        <div><dt>Correct</dt><dd data-testid="correct-count">{result.correct_count}</dd></div>
        <div><dt>Incorrect</dt><dd data-testid="incorrect-count">{result.incorrect_count}</dd></div>
        <div><dt>Skipped</dt><dd data-testid="skipped-count">{result.skipped_count}</dd></div>
        <div><dt>Accuracy</dt><dd>{result.accuracy_percent === null ? "-" : `${result.accuracy_percent}%`}</dd></div>
        <div><dt>Time taken</dt><dd>{formatDuration(result.time_taken_seconds)} of {formatDuration(result.time_limit_seconds)}</dd></div>
        {result.percentile !== null && <div><dt>Percentile</dt><dd>{result.percentile}</dd></div>}
      </dl>
      {result.by_difficulty.length > 0 && (
        <p className="small muted">
          By difficulty: {result.by_difficulty.map((d) => `${d.difficulty} ${d.correct}/${d.total}`).join(" - ")}
        </p>
      )}
    </section>
  );
}
