import "../../styles/analytics-insights.css";

export const STATUS = {
  strong: { text: "Strong", cls: "badge-selected" },
  improved: { text: "Improved", cls: "badge-open" },
  average: { text: "Average", cls: "badge-applied" },
  weak: { text: "Needs work", cls: "badge-rejected" },
  not_enough_data: { text: "Not enough data", cls: "badge-neutral" },
};

export default function StrengthsWeaknesses({ data }) {
  return (
    <div>
      <p data-testid="strengths-line">
        <strong>Strengths:</strong> {data.strengths.length ? data.strengths.join(", ") : "none yet"}
        {" - "}
        <strong>Needs work:</strong> {data.weaknesses.length ? data.weaknesses.join(", ") : "none"}
      </p>
      <ul className="insight-list">
        {data.categories.map((c) => {
          const s = STATUS[c.status];
          return (
            <li key={c.category} className="card insight-row" data-testid={`insight-${c.category}`} data-status={c.status}>
              <div className="row spread">
                <strong>{c.category}</strong>
                <span className={`badge ${s.cls}`}>{s.text}</span>
              </div>
              <div className="insight-bar" role="img" aria-label={`Recent average ${c.recent_average} percent`}>
                <div style={{ width: `${Math.max(0, Math.min(100, c.recent_average))}%` }} />
              </div>
              <p className="muted small">
                Recent average {c.recent_average}% - overall {c.average}% - {c.attempts} attempt{c.attempts === 1 ? "" : "s"}
              </p>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
