import "../../styles/analytics-insights.css";

export default function FocusAreas({ areas }) {
  if (!areas.length) return <p className="muted">Nothing to work on right now. Keep it up!</p>;
  return (
    <ol className="focus-list" data-testid="focus-areas">
      {areas.map((a) => (
        <li key={a.category}>{a.message}</li>
      ))}
    </ol>
  );
}