import "../../styles/analytics-insights.css";

const W = 640;
const H = 280;
const PAD = { top: 16, right: 16, bottom: 28, left: 40 };
const GRID = [0, 25, 50, 75, 100];

const when = (v) => new Date(v).toLocaleDateString("en-IN", { dateStyle: "medium" });

export default function TrendChart({ points }) {
  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;
  const x = (i) => PAD.left + (points.length === 1 ? innerW / 2 : (i / (points.length - 1)) * innerW);
  const y = (v) => PAD.top + innerH - (Math.max(0, Math.min(100, v)) / 100) * innerH;
  const line = (key) => points.map((p, i) => `${x(i)},${y(p[key])}`).join(" ");
  const label = `Score trend: ${points.length} attempt${points.length === 1 ? "" : "s"}, latest ${points[points.length - 1].score} percent.`;

  return (
    <figure className="trend-figure">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label} className="trend-chart" data-testid="trend-chart">
        {GRID.map((g) => (
          <g key={g}>
            <line x1={PAD.left} x2={W - PAD.right} y1={y(g)} y2={y(g)} className="trend-grid" />
            <text x={PAD.left - 6} y={y(g) + 4} textAnchor="end" className="trend-axis">{g}%</text>
          </g>
        ))}
        {points.length > 1 && <polyline points={line("score")} className="trend-score-line" fill="none" />}
        {points.length > 1 && <polyline points={line("moving_average")} className="trend-avg-line" fill="none" />}
        {points.map((p, i) => (
          <circle key={`${p.kind}-${p.id}`} cx={x(i)} cy={y(p.score)} r="4.5" className="trend-dot">
            <title>{`${p.title}: ${p.score}% (${when(p.at)})`}</title>
          </circle>
        ))}
        <text x={PAD.left} y={H - 6} className="trend-axis">Oldest</text>
        <text x={W - PAD.right} y={H - 6} textAnchor="end" className="trend-axis">Latest</text>
      </svg>
      <figcaption className="trend-legend small">
        <span><svg width="26" height="8" aria-hidden="true"><line x1="0" y1="4" x2="26" y2="4" className="trend-score-line" /></svg> Score</span>
        <span><svg width="26" height="8" aria-hidden="true"><line x1="0" y1="4" x2="26" y2="4" className="trend-avg-line" /></svg> Moving average</span>
      </figcaption>
      <details className="trend-table">
        <summary>View the numbers as a table</summary>
        <table className="table">
          <thead><tr><th>#</th><th>Date</th><th>Attempt</th><th>Score</th><th>Moving average</th></tr></thead>
          <tbody>
            {points.map((p) => (
              <tr key={`${p.kind}-${p.id}`}>
                <td data-label="#">{p.index}</td>
                <td data-label="Date">{when(p.at)}</td>
                <td data-label="Attempt">{p.title}</td>
                <td data-label="Score">{p.score}%</td>
                <td data-label="Moving average">{p.moving_average}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  );
}
