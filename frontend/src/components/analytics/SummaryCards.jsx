// Contract: <SummaryCards summary={SummaryResponse} />   headline numbers exactly as the server computed them.
import "../../styles/analytics.css";

const pct = (v) => (v === null || v === undefined ? "-" : `${v}%`);

export default function SummaryCards({ summary }) {
  const cards = [
    ["Attempts", summary.total_attempts, "total-attempts"],
    ["Average score", pct(summary.average_score), "average-score"],
    ["Best score", pct(summary.best_score), "best-score"],
    ["Latest score", pct(summary.latest_score), "latest-score"],
  ];
  return (
    <section aria-label="Summary" className="summary-cards">
      {cards.map(([label, value, id]) => (
        <div className="card summary-card" key={id}>
          <p className="muted small">{label}</p>
          <p className="summary-value" data-testid={id}>{value}</p>
        </div>
      ))}
      <p className="muted small summary-split">
        {summary.practice_attempts} practice session{summary.practice_attempts === 1 ? "" : "s"} and {summary.mock_attempts} mock test{summary.mock_attempts === 1 ? "" : "s"}.
      </p>
    </section>
  );
}
